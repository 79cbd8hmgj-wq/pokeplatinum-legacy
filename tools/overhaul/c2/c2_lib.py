"""Shared helpers for the locked-C2 TM/HM mechanics tooling."""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE_COMMIT = "e13b728fbe4f05ad137f143be11dd7eb71bf5d46"  # main at C2 implementation start (C1 merged)
MANIFEST = "docs/overhaul/implementation/c2_mechanics_manifest.json"

HM_DIRS = ("cut", "fly", "surf", "strength", "defog", "rock_smash", "waterfall", "rock_climb")
SRC = {
    "party_callbacks": "src/applications/party_menu/callbacks.c",
    "party_main": "src/applications/party_menu/main.c",
    "game_corner": "src/scrcmd_game_corner_prize.c",
    "shop_menu": "src/overlay007/shop_menu.c",
    "frontier_unused": "src/unk_020494DC.c",
    "scrcmd": "src/scrcmd.c",
    "defog": "res/battle/scripts/subscripts/subscript_defog.s",
    "prize_script": "res/field/scripts/scripts_veilstone_city_prize_exchange.s",
    "victory_road": "res/field/scripts/scripts_victory_road_1f.s",
    "moves_txt": "generated/moves.txt",
}
# Vendor script: its ITEM_TM01 threshold comparisons are vendor logic, not TM placement.
FINGERPRINT_EXCLUDE = {"res/field/scripts/scripts_veilstone_city_prize_exchange.s"}
FIELD_ITEM_RE = re.compile(r"\bITEM_(?:TM|HM)\d\d\b|\"(?:TM|HM)\d\d\"")


def git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True)


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def load_json(rel: str):
    return json.loads(read(rel))


def base_text(rel: str) -> str:
    return git("show", f"{BASE_COMMIT}:{rel}")


def tm_item_files() -> list[str]:
    return sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "res/items/data/[th]m[0-9][0-9].json")))


def parse_pairs(src: str, array_marker: str) -> list[tuple[str, int]]:
    """Parse `{ ITEM_X, n }` rows following the first occurrence of array_marker."""
    start = src.index(array_marker)
    end = src.index("};", start)
    return [(m.group(1), int(m.group(2))) for m in re.finditer(r"\{\s*(ITEM_\w+),\s*(\d+)\s*\}", src[start:end])]


def field_tm_fingerprint(read_fn=read, files=None) -> dict:
    """{relpath: {token: count}} for every field script/event mentioning TM/HM items."""
    out: dict[str, dict[str, int]] = {}
    paths = files if files is not None else sorted(
        os.path.relpath(p, ROOT)
        for pat in ("res/field/scripts/*.s", "res/field/events/*.json")
        for p in glob.glob(os.path.join(ROOT, pat))
    )
    for rel in paths:
        if rel in FINGERPRINT_EXCLUDE:
            continue
        c = Counter(FIELD_ITEM_RE.findall(read_fn(rel)))
        if c:
            out[rel] = dict(sorted(c.items()))
    return out


def tm_species_sets() -> dict:
    """Species data dirs whose by_tm list holds TM21 / TM78."""
    res = {"TM21": set(), "TM78": set()}
    for p in glob.glob(os.path.join(ROOT, "res/pokemon/**/data.json"), recursive=True):
        txt = open(p, encoding="utf-8").read()
        rel = os.path.relpath(os.path.dirname(p), os.path.join(ROOT, "res/pokemon"))
        for k in res:
            if f'"{k}"' in txt:
                res[k].add(rel)
    return res
