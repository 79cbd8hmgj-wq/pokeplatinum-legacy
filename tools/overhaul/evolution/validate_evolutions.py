#!/usr/bin/env python3
"""Static validator for the locked Pass A evolution overhaul.

validate(...) is pure (takes tables + texts) so the mutation tests can feed it corrupted copies.
Exit status: 0 when no hard failure.  --strict also fails while any UNRESOLVED_AUTHORITY edge remains.
"""
from __future__ import annotations

import itertools
import json
import os
import re
import sys

from evo_lib import (ALL_METHODS, BASE_COMMIT, EVOLUTION_STONES, FORBIDDEN_METHODS, ITEM_USE_METHODS, LOCKED_FINAL, MANIFEST,
                     NEW_METHODS, PARAM_KIND, ROOT, UNRESOLVED, VANILLA_METHODS, final_tables, load_base_tables,
                     load_live_tables, read_methods_file, species_const)

# Distinctive / retained mechanics that must exist in the final tables exactly as vanilla.
RETAINED = {
    "wurmple": [["EVO_LEVEL_PID_LOW", 7, "SPECIES_SILCOON"], ["EVO_LEVEL_PID_HIGH", 7, "SPECIES_CASCOON"]],
    "nincada": [["EVO_LEVEL_NINJASK", 20, "SPECIES_NINJASK"], ["EVO_LEVEL_SHEDINJA", 20, "SPECIES_SHEDINJA"]],
    "tyrogue": [["EVO_LEVEL_ATK_LT_DEF", 20, "SPECIES_HITMONCHAN"], ["EVO_LEVEL_ATK_GT_DEF", 20, "SPECIES_HITMONLEE"],
                ["EVO_LEVEL_ATK_EQ_DEF", 20, "SPECIES_HITMONTOP"]],
    "feebas": [["EVO_LEVEL_BEAUTY", 170, "SPECIES_MILOTIC"]],
    "nosepass": [["EVO_LEVEL_MAGNETIC_FIELD", "SPECIES_PROBOPASS"]],
    "magneton": [["EVO_LEVEL_MAGNETIC_FIELD", "SPECIES_MAGNEZONE"]],
    "snorunt": [["EVO_LEVEL", 42, "SPECIES_GLALIE"], ["EVO_USE_ITEM_FEMALE", "ITEM_DAWN_STONE", "SPECIES_FROSLASS"]],
    "kirlia": [["EVO_LEVEL", 30, "SPECIES_GARDEVOIR"], ["EVO_USE_ITEM_MALE", "ITEM_DAWN_STONE", "SPECIES_GALLADE"]],
    "roselia": [["EVO_USE_ITEM", "ITEM_SHINY_STONE", "SPECIES_ROSERADE"]],
    "eevee": [["EVO_LEVEL_MOSS_ROCK", "SPECIES_LEAFEON"], ["EVO_LEVEL_ICE_ROCK", "SPECIES_GLACEON"],
              ["EVO_USE_ITEM", "ITEM_THUNDERSTONE", "SPECIES_JOLTEON"], ["EVO_USE_ITEM", "ITEM_WATER_STONE", "SPECIES_VAPOREON"],
              ["EVO_USE_ITEM", "ITEM_FIRE_STONE", "SPECIES_FLAREON"], ["EVO_LEVEL_HAPPINESS_DAY", "SPECIES_ESPEON"],
              ["EVO_LEVEL_HAPPINESS_NIGHT", "SPECIES_UMBREON"]],
    "mantyke": [["EVO_LEVEL_SPECIES_IN_PARTY", "SPECIES_REMORAID", "SPECIES_MANTINE"]],
}

# Exact comparison source patterns required in src/pokemon.c (method -> (lhs, op, rhs)).
STAT_SEMANTICS = {
    "EVO_LEVEL_ATK_GT_DEF": ("MON_DATA_ATK", ">", "MON_DATA_DEF"),
    "EVO_LEVEL_ATK_EQ_DEF": ("MON_DATA_ATK", "==", "MON_DATA_DEF"),
    "EVO_LEVEL_ATK_LT_DEF": ("MON_DATA_ATK", "<", "MON_DATA_DEF"),
    "EVO_LEVEL_SPATK_GT_ATK": ("MON_DATA_SP_ATK", ">", "MON_DATA_ATK"),
    "EVO_LEVEL_SPATK_GE_ATK": ("MON_DATA_SP_ATK", ">=", "MON_DATA_ATK"),
    "EVO_LEVEL_ATK_GT_SPATK": ("MON_DATA_ATK", ">", "MON_DATA_SP_ATK"),
    "EVO_LEVEL_SPDEF_GT_DEF": ("MON_DATA_SP_DEF", ">", "MON_DATA_DEF"),
}


# --------------------------------------------------------------------------- engine model (mirrors src/pokemon.c)
def eligible(edge: list, level: int, atk: int, df: int, spa: int, spd: int, night: bool = False) -> bool:
    m = edge[0]
    p = edge[1] if PARAM_KIND[m] == "level" else None
    if m == "EVO_LEVEL":
        return p <= level
    if m == "EVO_LEVEL_NIGHT":
        return night and p <= level
    if m == "EVO_LEVEL_DAY":
        return (not night) and p <= level
    if m in STAT_SEMANTICS:
        a, op, b = STAT_SEMANTICS[m]
        v = {"MON_DATA_ATK": atk, "MON_DATA_DEF": df, "MON_DATA_SP_ATK": spa, "MON_DATA_SP_DEF": spd}
        l, r = v[a], v[b]
        ok = {">": l > r, ">=": l >= r, "<": l < r, "==": l == r}[op]
        return p <= level and ok
    return False  # methods outside the model (item/trade/held/etc.) never fire in the level-up branch model


def first_match(edges: list, **ctx) -> str | None:
    for e in edges:
        if e[0] in ITEM_USE_METHODS:
            continue  # item class is a separate evaluation pass in the engine
        if eligible(e, **ctx):
            return e[-1]
    return None


STATS = list(itertools.product(range(1, 5), repeat=4))  # atk, def, spa, spd -> covers every ordering/tie class


def check_branches(tables: dict, f: list) -> None:
    def need(sp):
        if sp not in tables:
            f.append(f"branch check: {sp} missing from tables")
            return False
        return True

    if need("clamperl"):
        eds = tables["clamperl"]
        for lvl in (34, 35, 36):
            for atk, df, spa, spd in STATS:
                hits = [e[-1] for e in eds if eligible(e, lvl, atk, df, spa, spd)]
                exp = [] if lvl < 35 else (["SPECIES_HUNTAIL"] if atk > spa else ["SPECIES_GOREBYSS"])
                if hits != exp:
                    f.append(f"clamperl lvl{lvl} atk{atk} spa{spa}: eligible {hits}, expected {exp}")
                    return
    if need("slowpoke"):
        eds = tables["slowpoke"]
        for lvl in (36, 37, 38):
            for atk, df, spa, spd in STATS:
                got = first_match(eds, level=lvl, atk=atk, df=df, spa=spa, spd=spd)
                exp = None if lvl < 37 else ("SPECIES_SLOWKING" if spd > df else "SPECIES_SLOWBRO")
                if got != exp:
                    f.append(f"slowpoke lvl{lvl} def{df} spd{spd}: got {got}, expected {exp}")
                    return
    if need("poliwhirl"):
        eds = tables["poliwhirl"]
        for lvl in (34, 35, 36):
            for atk, df, spa, spd in STATS:
                got = first_match(eds, level=lvl, atk=atk, df=df, spa=spa, spd=spd)
                exp = "SPECIES_POLITOED" if lvl >= 35 and spa > atk else None
                if got != exp:
                    f.append(f"poliwhirl lvl{lvl} atk{atk} spa{spa}: got {got}, expected {exp}")
                    return
        if ["EVO_USE_ITEM", "ITEM_WATER_STONE", "SPECIES_POLIWRATH"] not in eds:
            f.append("poliwhirl lost its Water Stone -> Poliwrath evolution")
    if need("tyrogue"):
        eds = tables["tyrogue"]
        for lvl in (19, 20, 21):
            for atk, df, spa, spd in STATS:
                hits = [e[-1] for e in eds if eligible(e, lvl, atk, df, spa, spd)]
                exp = [] if lvl < 20 else ["SPECIES_HITMONLEE" if atk > df else "SPECIES_HITMONCHAN" if atk < df else "SPECIES_HITMONTOP"]
                if hits != exp:
                    f.append(f"tyrogue lvl{lvl} atk{atk} def{df}: eligible {hits}, expected {exp}")
                    return
    if need("happiny"):
        for lvl in (19, 20, 21):
            for night in (False, True):
                got = first_match(tables["happiny"], level=lvl, atk=1, df=1, spa=1, spd=1, night=night)
                exp = "SPECIES_CHANSEY" if (not night and lvl >= 20) else None
                if got != exp:
                    f.append(f"happiny lvl{lvl} night={night}: got {got}, expected {exp}")
                    return
    for sp, target in (("gligar", "SPECIES_GLISCOR"), ("sneasel", "SPECIES_WEAVILE")):
        if not need(sp):
            continue
        eds = tables[sp]
        for lvl in (37, 38, 39):
            for night in (False, True):
                got = first_match(eds, level=lvl, atk=1, df=1, spa=1, spd=1, night=night)
                exp = target if (night and lvl >= 38) else None
                if got != exp:
                    f.append(f"{sp} lvl{lvl} night={night}: got {got}, expected {exp}")
                    return


# --------------------------------------------------------------------------- static source semantics
def check_engine_source(pokemon_c: str, methods: list[str], speciesproc_c: str, f: list) -> None:
    if methods[: len(VANILLA_METHODS)] != VANILLA_METHODS:
        f.append("vanilla evolution method IDs 0..26 changed or reordered")
    if methods[len(VANILLA_METHODS):] != NEW_METHODS:
        f.append(f"appended methods are {methods[len(VANILLA_METHODS):]}, expected exactly {NEW_METHODS}")
    for m, (a, op, b) in STAT_SEMANTICS.items():
        blk = re.search(rf"case {m}:(.*?)break;", pokemon_c, re.S)
        if not blk:
            f.append(f"src/pokemon.c has no case for {m}")
            continue
        pat = rf"Pokemon_GetValue\(mon, {a}, NULL\) {re.escape(op)} Pokemon_GetValue\(mon, {b}, NULL\)"
        if not re.search(pat, blk.group(1)):
            f.append(f"src/pokemon.c {m}: expected `{a} {op} {b}`")
        if "speciesEvolutions[i].param <= monLevel" not in blk.group(1):
            f.append(f"src/pokemon.c {m}: missing level gate")
    blk = re.search(r"case EVO_LEVEL_NIGHT:(.*?)break;", pokemon_c, re.S)
    if not blk or "IsNight() == TRUE" not in blk.group(1) or "param <= monLevel" not in blk.group(1) or "HELD" in blk.group(1).upper():
        f.append("src/pokemon.c EVO_LEVEL_NIGHT must be `IsNight() == TRUE && param <= monLevel` with no held-item test")
    blk = re.search(r"case EVO_LEVEL_DAY:(.*?)break;", pokemon_c, re.S)
    if not blk or "IsNight() == FALSE" not in blk.group(1) or "param <= monLevel" not in blk.group(1) or "HELD" in blk.group(1).upper():
        f.append("src/pokemon.c EVO_LEVEL_DAY must be `IsNight() == FALSE && param <= monLevel` with no held-item test")
    if "SPECIES_KADABRA" in pokemon_c.split("Pokemon_GetEvolutionTargetSpecies(", 1)[-1].split("switch (evoClass)", 1)[0]:
        f.append("Kadabra Everstone exemption is back (Kadabra no longer evolves by trade)")
    for m in NEW_METHODS:
        if f"case {m}:" not in speciesproc_c:
            f.append(f"tools/dataproc/src/speciesproc.c has no param handler for {m}")
    if not re.search(r"if \(targetSpecies\) \{\s*break;", pokemon_c):
        f.append("engine no longer stops at the first eligible evolution (precedence assumption broken)")


# --------------------------------------------------------------------------- main table validation
def validate(tables: dict, base: dict, manifest: dict, items: set, species: list, moves: set | None = None) -> tuple[list, list]:
    f: list[str] = []
    notes: list[str] = []
    final = {k: v for k, v in tables.items()}
    man_species = {s["dir"]: s for s in manifest["species"]}
    exc = {k: v["edge"] for k, v in UNRESOLVED.items()}
    dex = set(species[1:494])

    # manifest completeness / guards
    if set(final) != set(man_species):
        f.append(f"manifest species set differs from source: {sorted(set(final) ^ set(man_species))}")
    for sp, ent in man_species.items():
        if sp in LOCKED_FINAL and ent["after"] != LOCKED_FINAL[sp]:
            f.append(f"manifest after for {sp} differs from the locked table")
        if ent["changed"] and not ent.get("before"):
            f.append(f"manifest change for {sp} has no expected-before guard")
        if not ent["changed"] and base.get(sp) != final.get(sp):
            f.append(f"{sp}: manifest says unchanged but base differs from final")
        if ent["after"] != final.get(sp):
            f.append(f"{sp}: live {final.get(sp)} != manifest after {ent['after']}")
    if len(manifest["edges"]) != sum(len(v) for v in final.values()):
        f.append("manifest edge list size differs from source edge count")
    cls = {}
    for e in manifest["edges"]:
        cls[e["class"]] = cls.get(e["class"], 0) + 1
    if manifest["summary"]["changed_edges"] != cls.get("LOCKED_CHANGED", 0):
        f.append("manifest changed_edges summary inconsistent")

    # unchanged vanilla must not be modified without authority
    for sp in sorted(set(final) | set(base)):
        if sp in LOCKED_FINAL:
            continue
        if final.get(sp) != base.get(sp):
            f.append(f"{sp}: evolution table modified without manifest authority: {base.get(sp)} -> {final.get(sp)}")

    # locked tables exact
    for sp, want in LOCKED_FINAL.items():
        if final.get(sp) != want:
            f.append(f"{sp}: expected locked {want}, found {final.get(sp)}")

    # retained mechanics
    for sp, want in RETAINED.items():
        if final.get(sp) != want:
            f.append(f"{sp}: retained mechanic damaged: {final.get(sp)} != {want}")

    # global rules over the ENTIRE table
    for sp, edges in final.items():
        for e in edges:
            m = e[0]
            if m not in ALL_METHODS:
                f.append(f"{sp}: unknown method {m}")
                continue
            kind = PARAM_KIND[m]
            want_len = 2 if kind == "none" else 3
            if len(e) != want_len:
                f.append(f"{sp}: {e} malformed for {m}")
                continue
            if e[-1] not in dex:
                f.append(f"{sp}: target {e[-1]} outside #001-#493")
            if m in FORBIDDEN_METHODS and not (sp in exc and e == exc[sp]):
                f.append(f"{sp}: forbidden trade/held-item evolution {e}")
            if m in ITEM_USE_METHODS and e[1] not in EVOLUTION_STONES:
                f.append(f"{sp}: evolution consumes non-stone item {e[1]}")
            if kind == "item" and e[1] not in items:
                f.append(f"{sp}: unknown item {e[1]}")
            if kind == "level" and m != "EVO_LEVEL_BEAUTY" and not (1 <= e[1] <= 100):
                f.append(f"{sp}: level out of range in {e}")
            if kind == "move" and moves is not None and e[1] not in moves:
                f.append(f"{sp}: unknown move {e[1]}")
    for e in EVOLUTION_STONES:
        if e not in items:
            f.append(f"whitelisted stone {e} missing from item list")
    for sp, edge in exc.items():
        if edge in final.get(sp, []):
            notes.append(f"UNRESOLVED_AUTHORITY: {UNRESOLVED[sp]['key']} ({sp} {edge}) retained as vanilla")
    check_branches(final, f)
    return f, notes


def load_items() -> set:
    return {l.strip() for l in open(os.path.join(ROOT, "generated/items.txt")) if l.strip()}


def load_species() -> list:
    return [l.strip() for l in open(os.path.join(ROOT, "generated/species.txt")) if l.strip()]


def load_moves() -> set:
    return {l.strip() for l in open(os.path.join(ROOT, "generated/moves.txt")) if l.strip()}


def read(rel: str) -> str:
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def main() -> int:
    strict = "--strict" in sys.argv
    with open(os.path.join(ROOT, MANIFEST), encoding="utf-8") as fh:
        manifest = json.load(fh)
    fails, notes = validate(load_live_tables(), load_base_tables(), manifest, load_items(), load_species(), load_moves())
    check_engine_source(read("src/pokemon.c"), read_methods_file(), read("tools/dataproc/src/speciesproc.c"), fails)
    s = manifest["summary"]
    print(f"species={s['evolution_bearing_species']} edges={s['total_edges']} classes={s['edge_class_counts']}")
    for n in notes:
        print("NOTE:", n)
    for x in fails:
        print("FAIL:", x)
    unresolved = len(manifest["unresolved_authority"])
    if strict and unresolved:
        print(f"FAIL(strict): {unresolved} UNRESOLVED_AUTHORITY evolution(s) remain")
        return 1
    print("PASS" if not fails else f"{len(fails)} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
