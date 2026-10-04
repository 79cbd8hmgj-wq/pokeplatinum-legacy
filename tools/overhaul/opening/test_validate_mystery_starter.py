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
    "Pikachu weight 1 -> 2": (SRC, "{ SPECIES_PIKACHU, 1 }", "{ SPECIES_PIKACHU, 2 }"),
    "Gen I weight (Bulbasaur) 3 -> 4": (SRC, "{ SPECIES_BULBASAUR, 3 }", "{ SPECIES_BULBASAUR, 4 }"),
    "Gen II weight (Chikorita) 10 -> 9": (SRC, "{ SPECIES_CHIKORITA, 10 }", "{ SPECIES_CHIKORITA, 9 }"),
    "Gen III weight (Mudkip) 10 -> 11": (SRC, "{ SPECIES_MUDKIP, 10 }", "{ SPECIES_MUDKIP, 11 }"),
    "Gen IV weight (Piplup) 10 -> 11 (total 101)": (SRC, "{ SPECIES_PIPLUP, 10 }", "{ SPECIES_PIPLUP, 11 }"),
    "total weight 100 -> 99 via Torchic": (SRC, "{ SPECIES_TORCHIC, 10 }", "{ SPECIES_TORCHIC, 9 }"),
    "egg position becomes a table input": (HDR, "u16 MysteryStarter_SpeciesFromRoll(u32 roll);", "u16 MysteryStarter_SpeciesFromRoll(u32 roll, u32 position);"),
    "draw takes the egg position": (HDR, "u16 MysteryStarter_Draw(void);", "u16 MysteryStarter_Draw(u32 position);"),
    "second RNG call in the draw": (SRC, "u32 roll = LCRNG_Next() % MYSTERY_STARTER_ROLL_RANGE;", "LCRNG_Next();\n    u32 roll = LCRNG_Next() % MYSTERY_STARTER_ROLL_RANGE;"),
    "draw called a second time (hatch reroll)": (SC, "Egg_CreateMysteryStarterEgg(egg, species,", "species = MysteryStarter_Draw();\n    Egg_CreateMysteryStarterEgg(egg, species,"),
    "Pikachu Rival mapping -> Chimchar branch": (SRC, "    case SPECIES_PIPLUP:\n    case SPECIES_PIKACHU:\n    default:\n        return SPECIES_PIPLUP;", "    case SPECIES_PIPLUP:\n    default:\n        return SPECIES_PIPLUP;\n    case SPECIES_PIKACHU:\n        return SPECIES_CHIMCHAR;"),
    "Pikachu Rival mapping -> Turtwig branch": (SRC, "    case SPECIES_PIPLUP:\n    case SPECIES_PIKACHU:\n    default:\n        return SPECIES_PIPLUP;", "    case SPECIES_PIPLUP:\n    default:\n        return SPECIES_PIPLUP;\n    case SPECIES_PIKACHU:\n        return SPECIES_TURTWIG;"),
    "Grass category mapped to Water (Treecko)": (SRC, "    case SPECIES_TREECKO:\n", "    case SPECIES_TREECKO:\n        return SPECIES_PIPLUP;\n"),
    "Route 203 Rival branch reads the actual Mystery species": (R203, "GetPlayerStarterSpecies VAR_RESULT", "GetMysteryStarterSpecies VAR_RESULT"),
    "Rival starter keyed on the Mystery species": (SV, "u16 playerStarter = TryGetVarValue(varsFlags, VAR_PLAYER_STARTER);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        rivalStarter",
                                                      "u16 playerStarter = TryGetVarValue(varsFlags, VAR_MYSTERY_STARTER_SPECIES);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        rivalStarter"),
    "Rival branch compared against a non-Sinnoh species": (R203, "GoToIfEq VAR_RESULT, SPECIES_TURTWIG, Route203_StartRivalBattleTurtwig", "GoToIfEq VAR_RESULT, SPECIES_BULBASAUR, Route203_StartRivalBattleTurtwig"),
    "thirteen-way Rival duplication (extra Rival label)": (R203, "Route203_StartRivalBattlePiplup:", "Route203_StartRivalBattleBulbasaur:\n    GoTo Route203_StartRivalBattlePiplup\n\nRoute203_StartRivalBattlePiplup:"),
    "output level 5 -> 1": (HDR, "#define MYSTERY_STARTER_LEVEL      5", "#define MYSTERY_STARTER_LEVEL      1"),
    "starter hatch level reset to ordinary": ("src/unk_0203D1B8.c", "args.hatchLevel = MYSTERY_STARTER_LEVEL;", "args.hatchLevel = 0;"),
    "species preview: chooser sprite built from a real species": (APP, "BuildPokemonSpriteTemplate(&spriteTemplate, SPECIES_EGG, 0,", "BuildPokemonSpriteTemplate(&spriteTemplate, SPECIES_PIPLUP, 0,"),
    "species cry before hatch": (APP, "            app->chooseStarterStep++;\n        }\n        break;\n    case CHOOSE_STARTER_STEP_UPDATE_CURSOR_POSITION:", "            Sound_PlayPokemonCry(SPECIES_PIPLUP, 0);\n            app->chooseStarterStep++;\n        }\n        break;\n    case CHOOSE_STARTER_STEP_UPDATE_CURSOR_POSITION:"),
    "per-position confirmation text": (APP, "SetMessageWindowText(app->messageWindow, heapID, 360, 1, TEXT_COLOR(1, 2, 15), TEXT_SPEED_NO_TRANSFER);", "SetMessageWindowText(app->messageWindow, heapID, 360, 1 + app->cursorPosition, TEXT_COLOR(1, 2, 15), TEXT_SPEED_NO_TRANSFER);"),
    "Poke Ball models hidden again (non-vanilla visibility)": (APP, "            Set3DGraphicsIsVisible(&app->starter3DGraphics[4], TRUE);\n", ""),
    "custom resting-state plumbing reintroduced": (APP, "static BOOL IsSelectionMade(ChooseStarterApp *app, enum HeapID heapID);", "static void SetMysteryEggRestingState(ChooseStarterApp *app, int position);\nstatic BOOL IsSelectionMade(ChooseStarterApp *app, enum HeapID heapID);"),
    "preview movement offset changed": (APP, "[1] + 48) << FX32_SHIFT", "[1] + 40) << FX32_SHIFT"),
    "eggPosition output reintroduced": ("include/struct_defs/choose_starter_data.h", "const Options *options;", "int eggPosition;\n    const Options *options;"),
    "Route 201 calls GiveMysteryStarterEgg again": (R201, "    GetMysteryStarterSpecies VAR_0x8000\n    GivePokemon", "    GiveMysteryStarterEgg\n    GetMysteryStarterSpecies VAR_0x8000\n    GivePokemon"),
    "Route 201 calls HatchMysteryStarterEgg again": (R201, "    GetMysteryStarterSpecies VAR_0x8000\n    GivePokemon", "    HatchMysteryStarterEgg\n    GetMysteryStarterSpecies VAR_0x8000\n    GivePokemon"),
    "Route 201 award GivePokemon removed": (R201, "    GivePokemon VAR_0x8000, 5, ITEM_NONE, VAR_RESULT\n    ApplyMovement LOCALID_PROF_ROWAN", "    ApplyMovement LOCALID_PROF_ROWAN"),
    "Route 201 award level changed": (R201, "GivePokemon VAR_0x8000, 5,", "GivePokemon VAR_0x8000, 6,"),
    "Route 201 award before FadeScreenIn": (R201, "    FadeScreenIn\n    WaitFadeScreen\n    GetMysteryStarterSpecies VAR_0x8000\n", "    GetMysteryStarterSpecies VAR_0x8000\n    FadeScreenIn\n    WaitFadeScreen\n"),
    "chooser text differs per egg": (TXT, '"A Mystery Egg!\\n"', '"A Mystery Egg?!\\n"'),
    "missing persistence after roll": (SC, "SystemVars_SetMysteryStarterSpecies(varsFlags, species);", "SystemVars_SetPlayerStarter(varsFlags, 0);"),
    "extra species in the pool": (SRC, "    { SPECIES_PIPLUP, 10 },\n};", "    { SPECIES_PIPLUP, 10 },\n    { SPECIES_EEVEE, 0 },\n};"),
    "missing species in the pool": (SRC, "    { SPECIES_MUDKIP, 10 },\n", ""),
    "ordinary Egg_CreateEgg level changed": (DC, "Egg_CreateEggAtLevel(egg, species, param2, trainerInfo, param4, metLocation, 1);", "Egg_CreateEggAtLevel(egg, species, param2, trainerInfo, param4, metLocation, 5);"),
    "ordinary hatch level changed": (DC, "Egg_CreateHatchedMonAtLevel(egg, heapID, 1);", "Egg_CreateHatchedMonAtLevel(egg, heapID, 5);"),
    "breeding logic edited (hatch friendship)": (DC, "friendship = 120;", "friendship = 70;"),
    "Day Care hatch-cycle constants edited": ("include/constants/daycare.h", None, "\n#define MUTATED_HATCH_CONSTANT 1\n"),
    "Counterpart starter keyed on the Mystery species": (SV, "u16 playerStarter = TryGetVarValue(varsFlags, VAR_PLAYER_STARTER);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        counterpartStarter",
                                                            "u16 playerStarter = TryGetVarValue(varsFlags, VAR_MYSTERY_STARTER_SPECIES);\n\n    if (playerStarter == SPECIES_TURTWIG) {\n        counterpartStarter"),
    "VAR_PLAYER_STARTER receives the actual species": (SC, "SystemVars_SetPlayerStarter(varsFlags, branch);", "SystemVars_SetPlayerStarter(varsFlags, species);"),
    "actual species never stored": (SC, "SystemVars_SetMysteryStarterSpecies(varsFlags, species);", "(void)species;"),
    "branch computed with a second helper (not the single draw)": (SC, "u16 branch = MysteryStarter_GetRivalBranch(species);", "u16 branch = MysteryStarter_GetRivalBranch(MysteryStarter_Draw());"),
    "Pikachu branch store -> Chimchar via mapping": (SRC, "    case SPECIES_PIPLUP:\n    case SPECIES_PIKACHU:\n    default:\n        return SPECIES_PIPLUP;", "    case SPECIES_PIPLUP:\n    default:\n        return SPECIES_PIPLUP;\n    case SPECIES_PIKACHU:\n        return SPECIES_CHIMCHAR;"),
    "branch-remap layer reintroduced (SystemVars_GetPlayerStarterBranch)": (SV, "u16 SystemVars_GetRivalStarter(VarsFlags *varsFlags)\n{", "u16 SystemVars_GetPlayerStarterBranch(VarsFlags *varsFlags)\n{\n    return 0;\n}\n\nu16 SystemVars_GetRivalStarter(VarsFlags *varsFlags)\n{"),
    "renamed var reverted to VAR_UNUSED_0x4031": ("generated/vars_flags.txt", "VAR_MYSTERY_STARTER_SPECIES\n", "VAR_UNUSED_0x4031\n"),
    "extra var added to the table (save-size change)": ("generated/vars_flags.txt", "VAR_MYSTERY_STARTER_SPECIES\n", "VAR_MYSTERY_STARTER_SPECIES\nVAR_EXTRA_NEW\n"),
    "player name buffer uses the canonical branch": (STR, "u16 species = SystemVars_GetMysteryStarterSpecies(varsFlags);", "u16 species = SystemVars_GetPlayerStarter(varsFlags);"),
    "rival name buffer uses the Mystery species": (STR, "u16 species = SystemVars_GetRivalStarter(SaveData_GetVarsFlags(ctx->fieldSystem->saveData));", "u16 species = SystemVars_GetMysteryStarterSpecies(SaveData_GetVarsFlags(ctx->fieldSystem->saveData));"),
    "Route 201 award reads VAR_PLAYER_STARTER again": (R201, "    GetMysteryStarterSpecies VAR_0x8000\n    GivePokemon", "    GetPlayerStarterSpecies VAR_0x8000\n    GivePokemon"),
    "Sandgem lab gift skip reads the canonical branch": ("res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s", "GetMysteryStarterSpecies VAR_0x8000", "GetPlayerStarterSpecies VAR_0x8000"),
    "manifest/source drift (manifest weight)": ("MANIFEST", None, None),
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
