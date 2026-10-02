"""Shared loaders/helpers for the locked D1 Trainer Overhaul tooling."""
from __future__ import annotations

import functools
import glob
import hashlib
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE_COMMIT = "77ff7a74ec0a46fcb594850db1d03d2768ddc775"  # main at trainer-overhaul start (PR #18 merged)
TRAINER_DIR = "res/trainers/data"
FRONTIER_DIR = "res/trainers/frontier"
OUT_DIR = "docs/overhaul/implementation/trainers"
MANIFEST = f"{OUT_DIR}/trainer_overhaul_manifest.json"
ARCHETYPES = f"{OUT_DIR}/trainer_archetypes.json"
RULES = f"{OUT_DIR}/trainer_validation_rules.json"
REPORT = f"{OUT_DIR}/TRAINER_VALIDATION_REPORT.md"

MAX_PARTY = 6
MAX_IV_SCALE = 255


def p(*parts: str) -> str:
    return os.path.join(ROOT, *parts)


def read_lines(rel: str) -> list[str]:
    with open(p(rel), encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


@functools.lru_cache(None)
def species_set() -> frozenset[str]:
    return frozenset(read_lines("generated/species.txt"))


@functools.lru_cache(None)
def move_set() -> frozenset[str]:
    return frozenset(read_lines("generated/moves.txt"))


@functools.lru_cache(None)
def item_set() -> frozenset[str]:
    return frozenset(read_lines("generated/items.txt"))


@functools.lru_cache(None)
def ai_flag_set() -> frozenset[str]:
    return frozenset(read_lines("generated/ai_flags.txt"))


def species_dir(const: str) -> str:
    return const[len("SPECIES_"):].lower()


@functools.lru_cache(None)
def species_data(const: str) -> dict | None:
    path = p("res/pokemon", species_dir(const), "data.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(None)
def move_data(const: str) -> dict | None:
    path = p("res/moves", const[len("MOVE_"):].lower(), "data.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@functools.lru_cache(None)
def tm_moves() -> dict[str, str]:
    out = {}
    for path in glob.glob(p("res/items/data/[th]m[0-9][0-9].json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        out[d["name"]] = d["teachesMove"]
    return out


def bst(const: str) -> int:
    d = species_data(const)
    return sum(d["base_stats"].values()) if d else 0


@functools.lru_cache(None)
def evo_edges() -> dict[str, list]:
    """{species const: [evolution edge, ...]} from live data."""
    out = {}
    for path in sorted(glob.glob(p("res/pokemon/*/data.json"))):
        d = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as f:
            ev = json.load(f).get("evolutions") or []
        if ev:
            out["SPECIES_" + d.upper()] = ev
    return out


@functools.lru_cache(None)
def pre_evolutions() -> dict[str, str]:
    out = {}
    for src, edges in evo_edges().items():
        for e in edges:
            out[e[-1]] = src
    return out


def level_evo_threshold(const: str) -> int | None:
    """Lowest plain level at which `const` evolves (EVO_LEVEL / stat / day-night level methods), else None."""
    best = None
    for e in evo_edges().get(const, []):
        m = e[0]
        if m.startswith("EVO_LEVEL") and len(e) >= 3 and isinstance(e[1], int) and m not in (
                "EVO_LEVEL_BEAUTY", "EVO_LEVEL_PID_LOW", "EVO_LEVEL_PID_HIGH", "EVO_LEVEL_SHEDINJA"):
            best = e[1] if best is None else min(best, e[1])
    return best


def stage(const: str) -> int:
    n, cur = 0, const
    while cur in pre_evolutions():
        cur = pre_evolutions()[cur]
        n += 1
    return n


def is_final(const: str) -> bool:
    return const not in evo_edges()


def legal_moves(const: str, level: int) -> set[str]:
    """Moves a trainer Pokémon may legally carry: level-up (incl. pre-evolutions) <= level, TM/HM, tutor, egg."""
    out: set[str] = set()
    cur = const
    while cur:
        d = species_data(cur)
        if d:
            ls = d.get("learnset") or {}
            for lv, mv in ls.get("by_level", []):
                if lv <= level:
                    out.add(mv)
            if cur == const:
                tms = tm_moves()
                out.update(tms[t] for t in ls.get("by_tm", []) if t in tms)
                out.update(ls.get("by_tutor", []))
                out.update(ls.get("egg_moves", []))
        cur = pre_evolutions().get(cur)
    return out


def trainer_files() -> list[str]:
    return sorted(os.path.basename(x)[:-5] for x in glob.glob(p(TRAINER_DIR, "*.json")))


def load_trainer(tid: str) -> dict:
    with open(p(TRAINER_DIR, tid + ".json"), encoding="utf-8") as f:
        return json.load(f)


def dump_trainer(tid: str, data: dict) -> None:
    """Write with the file's existing indentation style and trailing-newline convention (files differ)."""
    path = p(TRAINER_DIR, tid + ".json")
    with open(path, encoding="utf-8") as f:
        trailing = f.read().endswith("\n")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        if trailing:
            f.write("\n")


def file_sha(rel: str) -> str:
    with open(p(rel), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def party_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data["party"], sort_keys=True).encode()).hexdigest()[:16]


def frontier_fingerprint(overrides: dict | None = None) -> str:
    """Fingerprint of res/trainers/frontier.  `overrides` maps repo-relative paths to replacement bytes (used to
    compare against the D1 inventory while ignoring the D6-manifested Frontier set corrections)."""
    overrides = overrides or {}
    h = hashlib.sha256()
    for path in sorted(glob.glob(p(FRONTIER_DIR, "**", "*"), recursive=True)):
        if os.path.isfile(path):
            rel = os.path.relpath(path, ROOT)
            h.update(rel.encode())
            if rel in overrides:
                h.update(overrides[rel])
                continue
            with open(path, "rb") as f:
                h.update(f.read())
    return h.hexdigest()


def party_summary(data: dict) -> list[str]:
    return [f"{m['species'][8:]}:{m['level']}" for m in data["party"]]
