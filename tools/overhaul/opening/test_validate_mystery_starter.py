#!/usr/bin/env python3
"""Deterministic mutation tests for the D8 Mystery Egg starter validator. Each mutation edits one source file in memory; the validator must
report at least one FAIL for it, and the unmutated tree must be clean. Writes docs/overhaul/implementation/opening/mutation_results.json
(no timestamps; byte-stable on an unchanged tree)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import validate_mystery_starter as VM  # noqa: E402

OUT = os.path.join(VM.ROOT, "docs/overhaul/implementation/opening/mutation_results.json")
SRC = "src/mystery_egg_starter.c"
HDR = "include/mystery_egg_starter.h"
APP = "src/choose_starter/choose_starter_app.c"
SC = "src/scrcmd.c"
SV = "src/system_vars.c"
DC = "src/overlay005/daycare.c"
R201 = "res/field/scripts/scripts_route_201.s"
R203 = "res/field/scripts/scripts_route_203.s"
TXT = "res/text/unk_0360.json"
STR = "src/scrcmd_strings.c"

# name -> (path, old, new)
MUTATIONS = {
    # Pool / visual contract
    "Pikachu weight 1 -> 2": (SRC, "{ SPECIES_PIKACHU, 1 }", "{ SPECIES_PIKACHU, 2 }"),
    "Gen I weight 3 -> 4": (SRC, "{ SPECIES_BULBASAUR, 3 }", "{ SPECIES_BULBASAUR, 4 }"),
    "Gen II weight 10 -> 9": (SRC, "{ SPECIES_CHIKORITA, 10 }", "{ SPECIES_CHIKORITA, 9 }"),
    "extra species in pool": (SRC, "    { SPECIES_PIPLUP, 10 },\n};", "    { SPECIES_PIPLUP, 10 },\n    { SPECIES_EEVEE, 0 },\n};"),
    "missing species in pool": (SRC, "    { SPECIES_MUDKIP, 10 },\n", ""),
    "egg position becomes table input": (HDR, "u16 MysteryStarter_SpeciesFromRoll(u32 roll);", "u16 MysteryStarter_SpeciesFromRoll(u32 roll, u32 position);"),
    "draw takes egg position": (HDR, "u16 MysteryStarter_Draw(void);", "u16 MysteryStarter_Draw(u32 position);"),
    "species preview uses real species": (APP, "BuildPokemonSpriteTemplate(&spriteTemplate, SPECIES_EGG, 0,", "BuildPokemonSpriteTemplate(&spriteTemplate, SPECIES_PIPLUP, 0,"),
    "species cry before reveal": (APP, "            app->chooseStarterStep++;\n        }\n        break;\n    case CHOOSE_STARTER_STEP_UPDATE_CURSOR_POSITION:",
                                  "            Sound_PlayPokemonCry(SPECIES_PIPLUP, 0);\n            app->chooseStarterStep++;\n        }\n        break;\n    case CHOOSE_STARTER_STEP_UPDATE_CURSOR_POSITION:"),
    "per-position confirmation text": (APP, "SetMessageWindowText(app->messageWindow, heapID, 360, 1, TEXT_COLOR(1, 2, 15), TEXT_SPEED_NO_TRANSFER);",
                                       "SetMessageWindowText(app->messageWindow, heapID, 360, 1 + app->cursorPosition, TEXT_COLOR(1, 2, 15), TEXT_SPEED_NO_TRANSFER);"),
    "fourth egg sprite": (APP, "#define NUM_STARTER_OPTIONS 3", "#define NUM_STARTER_OPTIONS 4"),
    "ChooseStarterData field order swapped": ("include/struct_defs/choose_starter_data.h",
                                               "    int species;\n    const Options *options;",
                                               "    const Options *options;\n    int species;"),
    "ChooseStarter exit species assignment removed": (APP, "    data->species = GetSelectedSpecies(app->cursorPosition);\n\n", ""),

    # Vanilla application-exit boundary
    "SaveChosenStarter reintroduces custom RNG": (
        SC,
        "    SystemVars_SetPlayerStarter(SaveData_GetVarsFlags(ctx->fieldSystem->saveData), chooseStarterData->species);",
        "    (void)MysteryStarter_Draw();\n    SystemVars_SetPlayerStarter(SaveData_GetVarsFlags(ctx->fieldSystem->saveData), chooseStarterData->species);"),
    "SaveChosenStarter reintroduces Mystery persistence": (
        SC,
        "    SystemVars_SetPlayerStarter(SaveData_GetVarsFlags(ctx->fieldSystem->saveData), chooseStarterData->species);",
        "    SystemVars_SetMysteryStarterSpecies(SaveData_GetVarsFlags(ctx->fieldSystem->saveData), chooseStarterData->species);"),
    "SaveChosenStarter frees chooser data twice": (
        SC,
        "    Heap_Free(*fieldSysDataPtr);\n\n    return FALSE;\n}\n\nstatic BOOL ScrCmd_OpenBag",
        "    Heap_Free(*fieldSysDataPtr);\n    Heap_Free(*fieldSysDataPtr);\n\n    return FALSE;\n}\n\nstatic BOOL ScrCmd_OpenBag"),

    # Native Route 201 RNG and weighted mapping
    "native RNG removed": (R201, "    GetRandom VAR_0x8000, 100\n", ""),
    "second native RNG draw": (R201, "    GetRandom VAR_0x8000, 100\n", "    GetRandom VAR_0x8000, 100\n    GetRandom VAR_0x8000, 100\n"),
    "native RNG range 100 -> 99": (R201, "    GetRandom VAR_0x8000, 100", "    GetRandom VAR_0x8000, 99"),
    "Bulbasaur threshold 3 -> 4": (R201,
        "GoToIfLt VAR_0x8000, 3, Route201_MysteryStarter_Bulbasaur",
        "GoToIfLt VAR_0x8000, 4, Route201_MysteryStarter_Bulbasaur"),
    "Pikachu threshold 10 -> 11": (R201,
        "GoToIfLt VAR_0x8000, 10, Route201_MysteryStarter_Pikachu",
        "GoToIfLt VAR_0x8000, 11, Route201_MysteryStarter_Pikachu"),
    "Mudkip threshold 70 -> 69": (R201,
        "GoToIfLt VAR_0x8000, 70, Route201_MysteryStarter_Mudkip",
        "GoToIfLt VAR_0x8000, 69, Route201_MysteryStarter_Mudkip"),
    "Pikachu actual species corrupted": (R201,
        "    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_PIKACHU\n    SetVar VAR_PLAYER_STARTER, SPECIES_PIPLUP",
        "    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_RAICHU\n    SetVar VAR_PLAYER_STARTER, SPECIES_PIPLUP"),
    "Pikachu rival branch -> Chimchar": (R201,
        "    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_PIKACHU\n    SetVar VAR_PLAYER_STARTER, SPECIES_PIPLUP",
        "    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_PIKACHU\n    SetVar VAR_PLAYER_STARTER, SPECIES_CHIMCHAR"),
    "Treecko rival branch -> Piplup": (R201,
        "    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_TREECKO\n    SetVar VAR_PLAYER_STARTER, SPECIES_TURTWIG",
        "    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_TREECKO\n    SetVar VAR_PLAYER_STARTER, SPECIES_PIPLUP"),
    "award reads canonical branch": (R201,
        "GivePokemon VAR_MYSTERY_STARTER_SPECIES, 5, ITEM_NONE, VAR_RESULT",
        "GivePokemon VAR_PLAYER_STARTER, 5, ITEM_NONE, VAR_RESULT"),
    "award level changed": (R201,
        "GivePokemon VAR_MYSTERY_STARTER_SPECIES, 5, ITEM_NONE, VAR_RESULT",
        "GivePokemon VAR_MYSTERY_STARTER_SPECIES, 6, ITEM_NONE, VAR_RESULT"),
    "custom getter reintroduced to Route 201": (R201,
        "    GivePokemon VAR_MYSTERY_STARTER_SPECIES, 5, ITEM_NONE, VAR_RESULT",
        "    GetMysteryStarterSpecies VAR_0x8000\n    GivePokemon VAR_MYSTERY_STARTER_SPECIES, 5, ITEM_NONE, VAR_RESULT"),
    "RNG moved before field fade completes": (R201,
        "    WaitFadeScreen\n\n    // Keep the application-exit boundary vanilla.",
        "    GetRandom VAR_0x8000, 100\n    WaitFadeScreen\n\n    // Keep the application-exit boundary vanilla."),
    "hatch helper reactivated": (R201,
        "    GivePokemon VAR_MYSTERY_STARTER_SPECIES, 5, ITEM_NONE, VAR_RESULT",
        "    GiveMysteryStarterEgg\n    GivePokemon VAR_MYSTERY_STARTER_SPECIES, 5, ITEM_NONE, VAR_RESULT"),

    # Downstream story and persistence
    "Sandgem gift skip reads canonical branch": (
        "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s",
        "SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES",
        "SetVarFromVar VAR_0x8000, VAR_PLAYER_STARTER"),
    "Route 203 Rival branch reads actual Mystery species": (R203,
        "GetPlayerStarterSpecies VAR_RESULT", "GetMysteryStarterSpecies VAR_RESULT"),
    "Rival starter keyed on Mystery species": (SV,
        "u16 playerStarter = TryGetVarValue(varsFlags, VAR_PLAYER_STARTER);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        rivalStarter",
        "u16 playerStarter = TryGetVarValue(varsFlags, VAR_MYSTERY_STARTER_SPECIES);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        rivalStarter"),
    "Counterpart starter keyed on Mystery species": (SV,
        "u16 playerStarter = TryGetVarValue(varsFlags, VAR_PLAYER_STARTER);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        counterpartStarter",
        "u16 playerStarter = TryGetVarValue(varsFlags, VAR_MYSTERY_STARTER_SPECIES);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        counterpartStarter"),
    "non-Sinnoh Rival comparison": (R203,
        "GoToIfEq VAR_RESULT, SPECIES_TURTWIG, Route203_StartRivalBattleTurtwig",
        "GoToIfEq VAR_RESULT, SPECIES_BULBASAUR, Route203_StartRivalBattleTurtwig"),
    "renamed var reverted": ("generated/vars_flags.txt", "VAR_MYSTERY_STARTER_SPECIES\n", "VAR_UNUSED_0x4031\n"),
    "extra var changes save size": ("generated/vars_flags.txt",
        "VAR_MYSTERY_STARTER_SPECIES\n", "VAR_MYSTERY_STARTER_SPECIES\nVAR_EXTRA_NEW\n"),
    "player name buffer uses canonical branch": (STR,
        "u16 species = SystemVars_GetMysteryStarterSpecies(varsFlags);",
        "u16 species = SystemVars_GetPlayerStarter(varsFlags);"),
    "rival name buffer uses Mystery species": (STR,
        "u16 species = SystemVars_GetRivalStarter(SaveData_GetVarsFlags(ctx->fieldSystem->saveData));",
        "u16 species = SystemVars_GetMysteryStarterSpecies(SaveData_GetVarsFlags(ctx->fieldSystem->saveData));"),

    # Breeding / output isolation
    "output level 5 -> 1": (HDR, "#define MYSTERY_STARTER_LEVEL      5", "#define MYSTERY_STARTER_LEVEL      1"),
    "ordinary Egg_CreateEgg level changed": (DC,
        "Egg_CreateEggAtLevel(egg, species, param2, trainerInfo, param4, metLocation, 1);",
        "Egg_CreateEggAtLevel(egg, species, param2, trainerInfo, param4, metLocation, 5);"),
    "ordinary hatch level changed": (DC,
        "Egg_CreateHatchedMonAtLevel(egg, heapID, 1);",
        "Egg_CreateHatchedMonAtLevel(egg, heapID, 5);"),
    "Day Care hatch constants edited": ("include/constants/daycare.h", None, "\n#define MUTATED_HATCH_CONSTANT 1\n"),

    # Manifest drift
    "manifest/source drift": ("MANIFEST", None, None),
}


def make_reader(path, old, new):
    base = VM.file_reader

    def read(p):
        text = base(p)
        if p == path:
            if old is None:
                return text + new
            if old not in text:
                raise AssertionError(f"mutation anchor missing in {p}: {old[:60]!r}")
            return text.replace(old, new, 1)
        return text
    return read


def run(name, spec):
    if spec[0] == "MANIFEST":
        m = json.loads(VM.file_reader(VM.MANIFEST))
        m["pool"][3]["weight"] = 2
        return [r for r in VM.V(manifest=m).run() if r[1] == "FAIL"]
    path, old, new = spec
    return [r for r in VM.V(reader=make_reader(path, old, new)).run() if r[1] == "FAIL"]


def main():
    base = [r for r in VM.V().run() if r[1] == "FAIL"]
    cases, missed = [], 0
    for name, spec in MUTATIONS.items():
        fails = run(name, spec)
        cases.append({"name": name, "detected": bool(fails), "failing": len(fails)})
        missed += 0 if fails else 1
        print(("detected" if fails else "MISSED") + f": {name} ({len(fails)} failing checks)")
    print("baseline failures:", len(base))
    with open(OUT, "w") as f:
        json.dump({"total": len(cases), "detected": len(cases) - missed, "baseline_failures": len(base), "cases": cases}, f, indent=1)
        f.write("\n")
    return missed + len(base)


if __name__ == "__main__":
    sys.exit(main())
