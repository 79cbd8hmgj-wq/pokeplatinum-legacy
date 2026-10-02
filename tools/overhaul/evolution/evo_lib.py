"""Shared helpers + canonical locked data for the Pass A evolution overhaul tooling."""
from __future__ import annotations

import glob
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BASE_COMMIT = "3b7b843e78ae3afcbd64c475816bfd4f3e83dc79"  # main at evolution implementation start (C1 #13 + C2 #14 merged)
MANIFEST = "docs/overhaul/implementation/evolution_manifest.json"
METHODS_FILE = "generated/evolution_methods.txt"

# Vanilla enum EvolutionMethod (IDs 0..26).  Order is frozen: nothing may shift.
VANILLA_METHODS = [
    "EVO_NONE", "EVO_LEVEL_HAPPINESS", "EVO_LEVEL_HAPPINESS_DAY", "EVO_LEVEL_HAPPINESS_NIGHT", "EVO_LEVEL",
    "EVO_TRADE", "EVO_TRADE_WITH_HELD_ITEM", "EVO_USE_ITEM", "EVO_LEVEL_ATK_GT_DEF", "EVO_LEVEL_ATK_EQ_DEF",
    "EVO_LEVEL_ATK_LT_DEF", "EVO_LEVEL_PID_LOW", "EVO_LEVEL_PID_HIGH", "EVO_LEVEL_NINJASK", "EVO_LEVEL_SHEDINJA",
    "EVO_LEVEL_BEAUTY", "EVO_USE_ITEM_MALE", "EVO_USE_ITEM_FEMALE", "EVO_LEVEL_WITH_HELD_ITEM_DAY",
    "EVO_LEVEL_WITH_HELD_ITEM_NIGHT", "EVO_LEVEL_KNOW_MOVE", "EVO_LEVEL_SPECIES_IN_PARTY", "EVO_LEVEL_MALE",
    "EVO_LEVEL_FEMALE", "EVO_LEVEL_MAGNETIC_FIELD", "EVO_LEVEL_MOSS_ROCK", "EVO_LEVEL_ICE_ROCK",
]
# Methods appended by this pass (IDs 27..31).
NEW_METHODS = [
    "EVO_LEVEL_SPATK_GT_ATK",   # 27  Lv >= param and SpA >  Atk
    "EVO_LEVEL_SPATK_GE_ATK",   # 28  Lv >= param and SpA >= Atk
    "EVO_LEVEL_ATK_GT_SPATK",   # 29  Lv >= param and Atk >  SpA
    "EVO_LEVEL_SPDEF_GT_DEF",   # 30  Lv >= param and SpD >  Def
    "EVO_LEVEL_NIGHT",          # 31  Lv >= param and night (no item)
]
ALL_METHODS = VANILLA_METHODS + NEW_METHODS

PARAM_KIND = {m: "none" for m in ALL_METHODS}
for _m in ("EVO_LEVEL", "EVO_LEVEL_ATK_GT_DEF", "EVO_LEVEL_ATK_EQ_DEF", "EVO_LEVEL_ATK_LT_DEF", "EVO_LEVEL_PID_LOW",
           "EVO_LEVEL_PID_HIGH", "EVO_LEVEL_NINJASK", "EVO_LEVEL_SHEDINJA", "EVO_LEVEL_BEAUTY", "EVO_LEVEL_MALE",
           "EVO_LEVEL_FEMALE", *NEW_METHODS):
    PARAM_KIND[_m] = "level"
for _m in ("EVO_TRADE_WITH_HELD_ITEM", "EVO_USE_ITEM", "EVO_USE_ITEM_MALE", "EVO_USE_ITEM_FEMALE",
           "EVO_LEVEL_WITH_HELD_ITEM_DAY", "EVO_LEVEL_WITH_HELD_ITEM_NIGHT"):
    PARAM_KIND[_m] = "item"
PARAM_KIND["EVO_LEVEL_KNOW_MOVE"] = "move"
PARAM_KIND["EVO_LEVEL_SPECIES_IN_PARTY"] = "species"

FORBIDDEN_METHODS = {"EVO_TRADE", "EVO_TRADE_WITH_HELD_ITEM", "EVO_LEVEL_WITH_HELD_ITEM_DAY", "EVO_LEVEL_WITH_HELD_ITEM_NIGHT"}
ITEM_USE_METHODS = {"EVO_USE_ITEM", "EVO_USE_ITEM_MALE", "EVO_USE_ITEM_FEMALE"}

# Genuine Gen IV evolution stones (explicit whitelist; each must exist in generated/items.txt).
EVOLUTION_STONES = [
    "ITEM_FIRE_STONE", "ITEM_WATER_STONE", "ITEM_THUNDERSTONE", "ITEM_LEAF_STONE", "ITEM_MOON_STONE",
    "ITEM_SUN_STONE", "ITEM_SHINY_STONE", "ITEM_DUSK_STONE", "ITEM_DAWN_STONE",
]

# The single evolution whose final method was never recovered (see EVOLUTION_RECOVERY_AUDIT.md).
UNRESOLVED = {
    "happiny": {
        "key": "HAPPINY_CHANSEY_HELD_OVAL_STONE",
        "edge": ["EVO_LEVEL_WITH_HELD_ITEM_DAY", "ITEM_OVAL_STONE", "SPECIES_CHANSEY"],
    }
}


def E(method: str, *rest) -> list:
    return [method, *rest]


# Final locked evolution tables for every species whose table the overhaul changes (data dir -> final list).
# Order matters: the engine takes the FIRST eligible entry.
LOCKED_FINAL = {
    "kadabra":    [E("EVO_LEVEL", 36, "SPECIES_ALAKAZAM")],
    "machoke":    [E("EVO_LEVEL", 36, "SPECIES_MACHAMP")],
    "graveler":   [E("EVO_LEVEL", 36, "SPECIES_GOLEM")],
    "haunter":    [E("EVO_LEVEL", 36, "SPECIES_GENGAR")],
    "onix":       [E("EVO_LEVEL", 35, "SPECIES_STEELIX")],
    "scyther":    [E("EVO_LEVEL", 38, "SPECIES_SCIZOR")],
    "seadra":     [E("EVO_LEVEL", 42, "SPECIES_KINGDRA")],
    "electabuzz": [E("EVO_LEVEL", 42, "SPECIES_ELECTIVIRE")],
    "magmar":     [E("EVO_LEVEL", 42, "SPECIES_MAGMORTAR")],
    "rhydon":     [E("EVO_LEVEL", 52, "SPECIES_RHYPERIOR")],
    "porygon":    [E("EVO_LEVEL", 30, "SPECIES_PORYGON2")],
    "porygon2":   [E("EVO_LEVEL", 45, "SPECIES_PORYGON_Z")],
    "dusclops":   [E("EVO_LEVEL", 45, "SPECIES_DUSKNOIR")],
    "gligar":     [E("EVO_LEVEL_NIGHT", 38, "SPECIES_GLISCOR")],
    "sneasel":    [E("EVO_LEVEL_NIGHT", 38, "SPECIES_WEAVILE")],
    "pupitar":    [E("EVO_LEVEL", 50, "SPECIES_TYRANITAR")],
    "poliwhirl":  [E("EVO_USE_ITEM", "ITEM_WATER_STONE", "SPECIES_POLIWRATH"),
                   E("EVO_LEVEL_SPATK_GT_ATK", 35, "SPECIES_POLITOED")],
    # Slowking first: SpD > Def -> Slowking; everything else (SpD <= Def) falls through to the unchanged Lv37 Slowbro.
    "slowpoke":   [E("EVO_LEVEL_SPDEF_GT_DEF", 37, "SPECIES_SLOWKING"),
                   E("EVO_LEVEL", 37, "SPECIES_SLOWBRO")],
    "clamperl":   [E("EVO_LEVEL_ATK_GT_SPATK", 35, "SPECIES_HUNTAIL"),
                   E("EVO_LEVEL_SPATK_GE_ATK", 35, "SPECIES_GOREBYSS")],
}

# Authority key / provenance per changed species (edge-level classification).
CHANGE_AUTHORITY = {
    "kadabra": ("TRADE_REPLACEMENT_KANTO", "EVOLUTION_SPEC.md recovered rulings; C3 sync (Alakazam Lv36)"),
    "machoke": ("TRADE_REPLACEMENT_KANTO", "EVOLUTION_SPEC.md recovered rulings; C3 sync (Machamp Lv36)"),
    "graveler": ("TRADE_REPLACEMENT_KANTO", "EVOLUTION_SPEC.md recovered rulings; C3 sync (Golem Lv36)"),
    "haunter": ("TRADE_REPLACEMENT_KANTO", "EVOLUTION_SPEC.md recovered rulings; C3 sync (Gengar Lv36)"),
    "onix": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md; C3 sync (Steelix Lv35)"),
    "scyther": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md; C3 sync (Scizor Lv38)"),
    "seadra": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md; C3 sync (Kingdra Lv42)"),
    "electabuzz": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md; C3 sync (Electivire Lv42)"),
    "magmar": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md (Magmortar Lv42)"),
    "rhydon": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md (Rhyperior Lv52)"),
    "porygon": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md; C3 sync (Porygon2 Lv30)"),
    "porygon2": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md; C3 sync (Porygon-Z Lv45)"),
    "dusclops": ("ITEM_TRADE_REPLACEMENT", "EVOLUTION_SPEC.md (Dusknoir Lv45)"),
    "gligar": ("NIGHT_LEVEL", "EVOLUTION_SPEC.md (Gliscor Lv38 at night, no Razor Fang)"),
    "sneasel": ("NIGHT_LEVEL", "EVOLUTION_SPEC.md (Weavile Lv38 at night, no Razor Claw)"),
    "pupitar": ("LEVEL_RETUNE", "EVOLUTION_SPEC.md (Tyranitar Lv50; vanilla Lv55)"),
    "poliwhirl": ("STAT_BRANCH", "EVOLUTION_SPEC.md / EMERALD_PORT_PLAN.md (Politoed Lv35 SpA > Atk); Poliwrath Water Stone unchanged"),
    "slowpoke": ("STAT_BRANCH", "EVOLUTION_SPEC.md / EMERALD_PORT_PLAN.md (Slowking Lv37 SpD > Def); Slowbro Lv37 unchanged, now the fallback"),
    "clamperl": ("STAT_BRANCH", "EVOLUTION_SPEC.md / EMERALD_PORT_PLAN.md (Huntail Atk > SpA; Gorebyss SpA >= Atk, both Lv35)"),
}

# Locked rulings that the overhaul confirms as already matching vanilla (LOCKED_KEEP): species -> (edge, note).
LOCKED_KEEP = {
    "snorunt": "Glalie Lv42 and female Snorunt -> Froslass via Dawn Stone",
    "kirlia": "Gardevoir Lv30 and male Kirlia -> Gallade via Dawn Stone",
    "nosepass": "Probopass via the existing Mt. Coronet magnetic-field method",
    "roselia": "Roserade via Shiny Stone",
    "feebas": "Milotic via Beauty (retained)",
    "tyrogue": "vanilla three-way Attack/Defense split retained",
    "wurmple": "personality split retained",
    "nincada": "Ninjask/Shedinja special evolution retained",
    "magneton": "Magnezone via magnetic field retained",
    "eevee": "stone / friendship / location branches retained",
}

SPECIES_DIR_OVERRIDES: dict[str, str] = {}


def git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True)


def species_const(dirname: str) -> str:
    return "SPECIES_" + dirname.upper()


def species_dirs() -> list[str]:
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, "res/pokemon/*/data.json")))


def data_path(dirname: str) -> str:
    return f"res/pokemon/{dirname}/data.json"


def load_live_tables() -> dict[str, list]:
    out = {}
    for d in species_dirs():
        with open(os.path.join(ROOT, data_path(d)), encoding="utf-8") as f:
            ev = json.load(f).get("evolutions") or []
        if ev:
            out[d] = ev
    return out


def load_base_tables() -> dict[str, list]:
    out = {}
    for d in species_dirs():
        try:
            ev = json.loads(git("show", f"{BASE_COMMIT}:{data_path(d)}")).get("evolutions") or []
        except subprocess.CalledProcessError:
            continue
        if ev:
            out[d] = ev
    return out


def edge_target(edge: list) -> str:
    return edge[-1]


def edge_param(edge: list):
    return edge[1] if len(edge) == 3 else None


def final_tables(base: dict[str, list]) -> dict[str, list]:
    """Base tables with the locked overlay applied."""
    out = {k: [list(e) for e in v] for k, v in base.items()}
    for k, v in LOCKED_FINAL.items():
        out[k] = [list(e) for e in v]
    return out


def read_methods_file(text: str | None = None) -> list[str]:
    if text is None:
        with open(os.path.join(ROOT, METHODS_FILE), encoding="utf-8") as f:
            text = f.read()
    return [l.strip() for l in text.splitlines() if l.strip()]


def edge_to_str(species: str, edge: list) -> str:
    return f"{species}: {edge}"
