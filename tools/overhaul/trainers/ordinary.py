"""T5 ordinary-trainer transformation rules (deterministic, archetype-driven; see trainer_archetypes.json).

R1 evolution-stage sync (level evolutions from the live evolution tables, both directions)
R2 availability fairness (family band must be <= the trainer's band)
R3 in-team duplicate removal (not for double battles)
R4 global usage caps (species / family) to reduce repetitive filler and showcase more families
R5 weak/illegal move replacement for teams with explicit movesets (<= 2 slots per Pokémon, natural STAB upgrades)
"""
from __future__ import annotations

import collections
import hashlib
from dataclasses import dataclass, field

from area_lib import BAND_ORDER, band_le, family_band, special_species, species_band, trainer_band
from moveset_lib import is_attack, score, usable
from trainer_lib import (bst, evo_edges, legal_moves, level_evo_threshold, move_data, pre_evolutions, species_data,
                         species_set)

CAP_SPECIES = 8
CAP_FAMILY = 20
MAX_SWAPS_PER_TRAINER = 2  # R4 only
BST_LOW, BST_HIGH = 0.80, 1.20
GRUNT_TYPES = {"TYPE_POISON", "TYPE_DARK", "TYPE_FLYING", "TYPE_NORMAL"}
UNUSABLE_SPECIES = {"SPECIES_NONE", "SPECIES_UNOWN", "SPECIES_DITTO", "SPECIES_SMEARGLE", "SPECIES_SHEDINJA", "SPECIES_WOBBUFFET",
                    "SPECIES_WYNAUT", "SPECIES_EGG", "SPECIES_BAD_EGG"}
# Records outside the ordinary pass (partner/story specials, unused, dummy, Frontier handled elsewhere).
SPECIAL_PREFIXES = ("dawn_", "lucas_", "cheryl_", "buck_", "marley_", "mira_", "riley_", "dummy_", "none")
BOSS_PREFIXES = ("leader_", "elite_four", "champion", "commander_", "galactic_boss", "rival_")
LEVEL_BAND = [(14, "E0"), (24, "E1"), (34, "M1"), (40, "M2"), (46, "L1"), (52, "L2"), (60, "P0"), (999, "P1")]
BAND_OVERRIDE = {"galactic_grunt_lake_verity": "M1"}  # story-gated event placed on an early-banded lake map


def h(*a) -> int:
    return int(hashlib.sha256("|".join(map(str, a)).encode()).hexdigest()[:8], 16)


def is_ordinary(tid: str) -> bool:
    return not (tid.startswith(SPECIAL_PREFIXES) or tid.startswith(BOSS_PREFIXES) or "_unused" in tid or "dummy" in tid
                or tid.endswith("_dummy"))


def is_grunt(tid: str) -> bool:
    return tid.startswith("galactic_grunt")


def effective_band(tid: str, party: list[dict]) -> str:
    for k, b in BAND_OVERRIDE.items():
        if tid.startswith(k):
            return b
    if "rematch" not in tid:
        b = trainer_band(tid)
        if b:
            return b
    top = max(m["level"] for m in party)
    return next(b for lim, b in LEVEL_BAND if top <= lim)


def family_of(const: str) -> str:
    cur = const
    while cur in pre_evolutions():
        cur = pre_evolutions()[cur]
    return cur


def level_edges(const: str) -> list[list]:
    out = []
    for e in evo_edges().get(const, []):
        if e[0] in ("EVO_LEVEL", "EVO_LEVEL_NIGHT", "EVO_LEVEL_DAY", "EVO_LEVEL_MALE", "EVO_LEVEL_FEMALE") and isinstance(e[1], int):
            out.append(e)
    return out


def next_stage(const: str, level: int) -> str | None:
    """Unique plain-level evolution reached at `level`, else None."""
    edges = [e for e in level_edges(const) if level >= e[1]]
    if len(evo_edges().get(const, [])) != len(level_edges(const)) and len(edges) != 1:
        return None
    return edges[0][-1] if len(edges) == 1 else None


def prev_stage(const: str, level: int) -> str | None:
    pre = pre_evolutions().get(const)
    if not pre:
        return None
    edge = [e for e in level_edges(pre) if e[-1] == const]
    if len(edge) == 1 and level < edge[0][1]:
        return pre
    return None


def sync_evolution(const: str, level: int) -> str:
    while True:
        n = next_stage(const, level)
        if n is None:
            break
        const = n
    while True:
        p_ = prev_stage(const, level)
        if p_ is None:
            break
        const = p_
    return const


def contradiction(const: str, level: int) -> str | None:
    """'under' = level >= own level-evolution threshold; 'over' = level < pre-evolution's threshold; else None."""
    if next_stage(const, level):
        return "under"
    if prev_stage(const, level):
        return "over"
    return None


def stage_ok(const: str, level: int) -> bool:
    return contradiction(const, level) is None


def natural_moves(const: str, level: int) -> list[str]:
    """Last four distinct level-up moves (own + pre-evolutions) at or below `level`; at least two usable attacks."""
    seq: list[tuple[int, str]] = []
    cur = const
    chain = []
    while cur:
        chain.append(cur)
        cur = pre_evolutions().get(cur)
    for sp in reversed(chain):
        d = species_data(sp)
        for lv, mv in (d.get("learnset", {}).get("by_level", []) if d else []):
            if lv <= level and usable(mv):
                seq.append((lv, mv))
    seen: list[str] = []
    for _, mv in seq:
        if mv in seen:
            seen.remove(mv)
        seen.append(mv)
    out = seen[-4:]
    if sum(1 for m in out if is_attack(m)) < 2:
        extra = [m for m in reversed(seen) if is_attack(m) and m not in out]
        while extra and sum(1 for m in out if is_attack(m)) < 2 and out:
            for i, m in enumerate(out):
                if not is_attack(m):
                    out[i] = extra.pop(0)
                    break
            else:
                break
    return out


@dataclass
class Usage:
    species: collections.Counter = field(default_factory=collections.Counter)
    family: collections.Counter = field(default_factory=collections.Counter)

    def add(self, s: str, d: int = 1) -> None:
        self.species[s] += d
        self.family[family_of(s)] += d


def candidates(orig: str, level: int, band: str, grunt: bool, exclude: set[str]) -> list[str]:
    b0 = bst(orig)
    otypes = set(species_data(orig)["types"])
    out = []
    for c in sorted(species_set()):
        if c in UNUSABLE_SPECIES or c in exclude or c == orig or (c in special_species() and orig not in special_species()):
            continue
        sb = species_band(c)
        if sb is None or not band_le(sb, band):
            continue
        cd = species_data(c)
        if not cd or not (BST_LOW * b0 <= bst(c) <= BST_HIGH * b0):
            continue
        ctypes = set(cd["types"])
        if grunt:
            if not ctypes & GRUNT_TYPES:
                continue
        elif not ctypes & otypes:
            continue
        if not stage_ok(c, level):
            continue
        out.append(c)
    return out


def pick(orig: str, level: int, band: str, grunt: bool, exclude: set[str], usage: Usage, seed: str) -> str | None:
    pool = candidates(orig, level, band, grunt, exclude)
    if not pool:
        return None
    b0 = bst(orig)
    otypes = species_data(orig)["types"]

    def key(c: str):
        aff = 0 if species_data(c)["types"][0] == otypes[0] else (1 if set(species_data(c)["types"]) & set(otypes) else 2)
        return (aff, usage.species[c] + 0.5 * usage.family[family_of(c)], round(abs(bst(c) - b0) / b0, 2), h(seed, c))
    return min(pool, key=key)


def weak_moves(const: str, level: int, moves: list[str]) -> list[str]:
    """R5: replace illegal / obviously useless moves (<= 2 slots) with natural STAB upgrades."""
    leg = legal_moves(const, level)
    types = species_data(const)["types"]
    bad = []
    for m in moves:
        d = move_data(m)
        useless = m == "MOVE_SPLASH" or (d and is_attack(m) and d["power"] <= 40 and level >= 28 and d["type"] not in types
                                         and d["effect"]["type"] == "BATTLE_EFFECT_HIT")
        if m not in leg or useless or not usable(m):
            bad.append(m)
    if not bad:
        return moves
    pool = sorted((m for m in leg if is_attack(m) and usable(m) and move_data(m)["accuracy"] >= 75
                   and move_data(m)["type"] in types and m not in moves), key=lambda m: (-score(const, m), m))
    out = list(moves)
    swaps = 0
    for i, m in enumerate(moves):
        if m in bad and swaps < 2 and pool:
            out[i] = pool.pop(0)
            swaps += 1
        elif m in bad and m not in leg:
            out[i] = None  # illegal and no upgrade left: drop
    return [m for m in out if m]
