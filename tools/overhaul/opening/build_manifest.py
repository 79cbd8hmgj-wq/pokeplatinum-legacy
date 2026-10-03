#!/usr/bin/env python3
"""Regenerates docs/overhaul/implementation/opening/mystery_egg_starter_manifest.json (D8). Before-guards are git blob ids at the
starting SHA, so drift against the pre-D8 source is machine-checkable. Re-run after any source edit that changes the guarded file set."""
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
START_SHA = "6fc1eedfec637041733b5e5d9626a49c7524daa9"
OUT = "docs/overhaul/implementation/opening/mystery_egg_starter_manifest.json"

POOL = [  # (species, weight, category, rival branch, roll range)
    ("BULBASAUR", 3, "GEN_I_RARE", "TURTWIG"), ("CHARMANDER", 3, "GEN_I_RARE", "CHIMCHAR"), ("SQUIRTLE", 3, "GEN_I_RARE", "PIPLUP"),
    ("PIKACHU", 1, "PIKACHU_RARE", "PIPLUP"),
    ("CHIKORITA", 10, "GEN_II", "TURTWIG"), ("CYNDAQUIL", 10, "GEN_II", "CHIMCHAR"), ("TOTODILE", 10, "GEN_II", "PIPLUP"),
    ("TREECKO", 10, "GEN_III", "TURTWIG"), ("TORCHIC", 10, "GEN_III", "CHIMCHAR"), ("MUDKIP", 10, "GEN_III", "PIPLUP"),
    ("TURTWIG", 10, "GEN_IV", "TURTWIG"), ("CHIMCHAR", 10, "GEN_IV", "CHIMCHAR"), ("PIPLUP", 10, "GEN_IV", "PIPLUP"),
]

# file -> what the D8 target must contain (validator greps these) / why the file is guarded
SOURCES = {
    "src/mystery_egg_starter.c": "NEW: weighted table, single draw, Rival-branch mapping",
    "include/mystery_egg_starter.h": "NEW: MYSTERY_STARTER_* constants + prototypes",
    "src/choose_starter/choose_starter_app.c": "three identical egg sprites; species preview/cry removed",
    "include/struct_defs/choose_starter_data.h": "species output replaced by eggPosition (never selects a species)",
    "src/scrcmd.c": "SaveChosenStarter draws once and persists; GetPlayerStarterBranch / GiveMysteryStarterEgg / HatchMysteryStarterEgg",
    "src/system_vars.c": "SystemVars_GetPlayerStarterBranch; Rival/counterpart starter derived from the branch",
    "src/overlay005/daycare.c": "level-parameterised internals; ordinary entry points keep level 1",
    "src/egg_hatch.c": "hatchLevel > 1 selects Egg_CreateHatchedMonAtLevel",
    "src/unk_0203D1B8.c": "FieldSystem_HatchMysteryStarterEgg (no TV segment); FieldSystem_HatchEgg hatchLevel = 0",
    "res/field/scripts/scripts_route_201.s": "Route201_Briefcase egg flow",
    "res/text/unk_0360.json": "neutral Mystery Egg chooser text",
    "res/text/route_201.json": "Egg wording + hatch lead-in",
}
RIVAL_SCRIPTS = [
    "scripts_route_201.s", "scripts_route_203.s", "scripts_route_209_gate_to_hearthome_city.s", "scripts_pastoria_city.s",
    "scripts_canalave_city.s", "scripts_pokemon_league_north_pokecenter_1f.s", "scripts_fight_area.s", "scripts_survival_area.s",
    "scripts_spear_pillar.s", "scripts_jubilife_city.s", "scripts_veilstone_city.s", "scripts_trainers_school.s",
    "scripts_jubilife_tv_2f.s", "scripts_veilstone_store_1f.s", "scripts_eterna_city_underground_man_house.s",
]


def blob(path):
    r = subprocess.run(["git", "rev-parse", f"{START_SHA}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    lo = 0
    pool = []
    for sp, w, cat, branch in POOL:
        pool.append({"species": f"SPECIES_{sp}", "weight": w, "category": cat, "rival_branch": f"SPECIES_{branch}", "roll_range": [lo, lo + w - 1]})
        lo += w
    guards = {p: {"before_blob": blob(p), "target": why} for p, why in SOURCES.items()}
    for f in RIVAL_SCRIPTS:
        p = f"res/field/scripts/{f}"
        guards[p] = {"before_blob": blob(p), "target": "GetPlayerStarterSpecies -> GetPlayerStarterBranch" if "route_201" not in f else "Route201_Briefcase egg flow + branch query"}
    m = {
        "schema": "pokeplatinum-overhaul/mystery-egg-starter/v1",
        "starting_sha": START_SHA,
        "authority": ["docs/overhaul/opening/MYSTERY_EGG_STARTER_SPEC.md", "docs/overhaul/opening/MYSTERY_EGG_STARTER_IMPLEMENTATION_PLAN.md"],
        "pool_size": 13, "weight_total": 100, "weight_unit": "integer units out of 100 (no floating point)",
        "pool": pool,
        "rival_branches": {"SPECIES_TURTWIG": "Grass", "SPECIES_CHIMCHAR": "Fire", "SPECIES_PIPLUP": "Water"},
        "rival_branch_count": 3,
        "visual_equivalence": {
            "positions": ["left", "center", "right"], "same_visual": "SPECIES_EGG sprite", "species_preview": False, "species_name_preview": False,
            "type_hint": False, "cry_before_hatch": False, "confirmation_text_identical": True, "table_depends_on_position": False,
            "pokeball_3d_models_visible": False,
        },
        "rng": {"function": "MysteryStarter_Draw", "source": "LCRNG_Next() % 100", "range": [0, 99], "draws": 1, "timing": "inside ScrCmd_SaveChosenStarter, after the chooser app exits with a confirmed egg",
                "position_is_input": False, "reroll_on_hatch": False, "reroll_on_field_return": False, "reroll_on_battle_start": False, "anti_save_scumming": False},
        "persistence": {"store": "VAR_PLAYER_STARTER (existing u16 var; actual species)", "written": "immediately in ScrCmd_SaveChosenStarter", "save_format_change": False,
                        "rival_branch_store": "none; derived by SystemVars_GetPlayerStarterBranch (pure function of the actual species)"},
        "reveal": {"timing": "after ReturnToField, before Rowan/counterpart departure and before Barry's first battle",
                   "mechanism": "GiveMysteryStarterEgg -> native egg hatch scene (HatchMysteryStarterEgg)", "tv_segment": False},
        "output": {"level": 5, "level_constant": "MYSTERY_STARTER_LEVEL", "owner": "player", "pikachu_hatches_as": "SPECIES_PIKACHU",
                   "generation": "Pokemon_InitWith(level 5, INIT_IVS_RANDOM, random personality); no guaranteed IV/nature/gender/shiny/item"},
        "ordinary_breeding_unchanged": {"Egg_CreateEgg_level": 1, "Egg_CreateHatchedMon_level": 1, "FieldSystem_HatchEgg_hatchLevel": 0,
                                        "untouched_files": ["include/constants/daycare.h", "src/daycare_save.c", "docs/overhaul/implementation/breeding/"]},
        "source_guards": guards,
        "validation": {"state": "IMPLEMENTED_PENDING_CI", "validator": "tools/overhaul/validate_mystery_starter.py", "runtime": "NOT RUN",
                       "verified": False},
    }
    with open(os.path.join(ROOT, OUT), "w") as f:
        json.dump(m, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
