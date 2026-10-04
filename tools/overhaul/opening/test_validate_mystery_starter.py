#!/usr/bin/env python3
"""Deterministic mutation tests for the hardened D8 Mystery Egg starter validator.

Each mutation edits one source file in memory. The validator must report at least
one FAIL for every mutation, while the unmutated tree must have zero failures.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import validate_mystery_starter as VM  # noqa: E402

OUT = os.path.join(VM.ROOT, "docs/overhaul/implementation/opening/mutation_results.json")
SRC = "src/mystery_egg_starter.c"  # validator/reference-only; not linked into ROM
HDR = "include/mystery_egg_starter.h"
APP = "src/choose_starter/choose_starter_app.c"
SC = "src/scrcmd.c"
SV = "src/system_vars.c"
R201 = "res/field/scripts/scripts_route_201.s"
R203 = "res/field/scripts/scripts_route_203.s"
LAB = "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"
TXT = "res/text/unk_0360.json"
STR = "src/scrcmd_strings.c"
MESON = "src/meson.build"

# name -> (path, old, new)
MUTATIONS = {
    # Locked reference pool / position independence.
    "Pikachu weight 1 -> 2": (SRC, "{ SPECIES_PIKACHU, 1 }", "{ SPECIES_PIKACHU, 2 }"),
    "Bulbasaur weight 3 -> 4": (SRC, "{ SPECIES_BULBASAUR, 3 }", "{ SPECIES_BULBASAUR, 4 }"),
    "Piplup weight 10 -> 11": (SRC, "{ SPECIES_PIPLUP, 10 }", "{ SPECIES_PIPLUP, 11 }"),
    "extra species in reference pool": (SRC, "    { SPECIES_PIPLUP, 10 },\n};", "    { SPECIES_PIPLUP, 10 },\n    { SPECIES_EEVEE, 0 },\n};"),
    "missing species in reference pool": (SRC, "    { SPECIES_MUDKIP, 10 },\n", ""),
    "reference lookup takes egg position": (HDR, "u16 MysteryStarter_SpeciesFromRoll(u32 roll);", "u16 MysteryStarter_SpeciesFromRoll(u32 roll, u32 position);"),

    # Egg chooser presentation / vanilla exit contract.
    "chooser uses real species sprite": (APP, "BuildPokemonSpriteTemplate(&spriteTemplate, SPECIES_EGG, 0,", "BuildPokemonSpriteTemplate(&spriteTemplate, SPECIES_PIPLUP, 0,"),
    "chooser plays species cry": (APP, "            app->chooseStarterStep++;\n        }\n        break;\n    case CHOOSE_STARTER_STEP_UPDATE_CURSOR_POSITION:", "            Sound_PlayPokemonCry(SPECIES_PIPLUP, 0);\n            app->chooseStarterStep++;\n        }\n        break;\n    case CHOOSE_STARTER_STEP_UPDATE_CURSOR_POSITION:"),
    "per-position confirmation text": (APP, "SetMessageWindowText(app->messageWindow, heapID, 360, 1, TEXT_COLOR(1, 2, 15), TEXT_SPEED_NO_TRANSFER);", "SetMessageWindowText(app->messageWindow, heapID, 360, 1 + app->cursorPosition, TEXT_COLOR(1, 2, 15), TEXT_SPEED_NO_TRANSFER);"),
    "fourth egg option": (APP, "#define NUM_STARTER_OPTIONS 3", "#define NUM_STARTER_OPTIONS 4"),
    "ChooseStarterData species field removed": ("include/struct_defs/choose_starter_data.h", "    int species;\n", ""),
    "ChooseStarter_Exit species assignment removed": (APP, "    data->species = GetSelectedSpecies(app->cursorPosition);\n\n", ""),
    "chooser teardown reordered": (APP, "    DeleteDrawing();\n\n    VramTransfer_Free();", "    VramTransfer_Free();\n\n    DeleteDrawing();"),
    "chooser text differs per egg": (TXT, '"A Mystery Egg!\\n"', '"A Mystery Egg?!\\n"'),

    # Vanilla application-exit boundary.
    "SaveChosenStarter frees chooser data twice": (SC, "    Heap_Free(*fieldSysDataPtr);\n\n    return FALSE;\n}\n\nstatic BOOL ScrCmd_OpenBag", "    Heap_Free(*fieldSysDataPtr);\n    Heap_Free(*fieldSysDataPtr);\n\n    return FALSE;\n}\n\nstatic BOOL ScrCmd_OpenBag"),
    "SaveChosenStarter writes Mystery variable": (SC, "    SystemVars_SetPlayerStarter(SaveData_GetVarsFlags(ctx->fieldSystem->saveData), chooseStarterData->species);", "    SystemVars_SetPlayerStarter(SaveData_GetVarsFlags(ctx->fieldSystem->saveData), chooseStarterData->species);\n    VAR_MYSTERY_STARTER_SPECIES;"),

    # Native post-return RNG timing and weighted thresholds.
    "native RNG upper bound 100 -> 99": (R201, "    GetRandom VAR_0x8000, 100", "    GetRandom VAR_0x8000, 99"),
    "second starter RNG draw": (R201, "    GetRandom VAR_0x8000, 100", "    GetRandom VAR_0x8000, 100\n    GetRandom VAR_0x8001, 100"),
    "Bulbasaur threshold 3 -> 4": (R201, "GoToIfLt VAR_0x8000, 3, Route201_MysteryStarter_Bulbasaur", "GoToIfLt VAR_0x8000, 4, Route201_MysteryStarter_Bulbasaur"),
    "Pikachu threshold 10 -> 11": (R201, "GoToIfLt VAR_0x8000, 10, Route201_MysteryStarter_Pikachu", "GoToIfLt VAR_0x8000, 11, Route201_MysteryStarter_Pikachu"),
    "Chimchar threshold 90 -> 91": (R201, "GoToIfLt VAR_0x8000, 90, Route201_MysteryStarter_Chimchar", "GoToIfLt VAR_0x8000, 91, Route201_MysteryStarter_Chimchar"),
    "Piplup fallback removed": (R201, "    GoTo Route201_MysteryStarter_Piplup\n    End", "    End"),
    "RNG moved before field fade completion": (R201, "    FadeScreenIn\n    WaitFadeScreen\n\n    // D8 Mystery Starter hardening:", "    GetRandom VAR_0x8000, 100\n    FadeScreenIn\n    WaitFadeScreen\n\n    // D8 Mystery Starter hardening:"),

    # Actual species / canonical Rival branch persistence.
    "Pikachu actual store wrong": (R201, "Route201_MysteryStarter_Pikachu:\n    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_PIKACHU", "Route201_MysteryStarter_Pikachu:\n    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_PIPLUP"),
    "Pikachu canonical branch -> Chimchar": (R201, "Route201_MysteryStarter_Pikachu:\n    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_PIKACHU\n    SetVar VAR_PLAYER_STARTER, SPECIES_PIPLUP", "Route201_MysteryStarter_Pikachu:\n    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_PIKACHU\n    SetVar VAR_PLAYER_STARTER, SPECIES_CHIMCHAR"),
    "Treecko canonical branch -> Piplup": (R201, "Route201_MysteryStarter_Treecko:\n    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_TREECKO\n    SetVar VAR_PLAYER_STARTER, SPECIES_TURTWIG", "Route201_MysteryStarter_Treecko:\n    SetVar VAR_MYSTERY_STARTER_SPECIES, SPECIES_TREECKO\n    SetVar VAR_PLAYER_STARTER, SPECIES_PIPLUP"),
    "actual species copied from canonical var": (R201, "SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES", "SetVarFromVar VAR_0x8000, VAR_PLAYER_STARTER"),
    "starter award removed": (R201, "    GivePokemon VAR_0x8000, 5, ITEM_NONE, VAR_RESULT\n", ""),
    "starter award level 5 -> 6": (R201, "GivePokemon VAR_0x8000, 5,", "GivePokemon VAR_0x8000, 6,"),

    # Custom engine plumbing must stay gone.
    "custom getter macro reintroduced": ("asm/macros/scrcmd.inc", None, "\n    .macro GetMysteryStarterSpecies destVar\n    .short SCRCMD_GETMYSTERYSTARTERSPECIES\n    .short \\destVar\n    .endm\n"),
    "custom getter opcode reintroduced": ("include/data/scripts/scrcmd.h", None, "\nScriptCommand(SCRCMD_GETMYSTERYSTARTERSPECIES, ScrCmd_GetMysteryStarterSpecies)\n"),
    "reference C module linked into ROM": (MESON, None, "\n# mutation\n'mystery_egg_starter.c',\n"),

    # Downstream semantics.
    "Route 203 Rival reads actual Mystery species": (R203, "GetPlayerStarterSpecies VAR_RESULT", "SetVarFromVar VAR_RESULT, VAR_MYSTERY_STARTER_SPECIES"),
    "Rival helper keyed on actual Mystery species": (SV, "u16 playerStarter = TryGetVarValue(varsFlags, VAR_PLAYER_STARTER);\n\n    if (playerStarter == SPECIES_TURTWIG) {", "u16 playerStarter = TryGetVarValue(varsFlags, VAR_MYSTERY_STARTER_SPECIES);\n\n    if (playerStarter == SPECIES_TURTWIG) {"),
    "player name buffer uses canonical branch": (STR, "u16 species = SystemVars_GetMysteryStarterSpecies(varsFlags);", "u16 species = SystemVars_GetPlayerStarter(varsFlags);"),
    "Sandgem lab reads canonical branch": (LAB, "SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES", "SetVarFromVar VAR_0x8000, VAR_PLAYER_STARTER"),
    "Mystery variable renamed back to unused": ("generated/vars_flags.txt", "VAR_MYSTERY_STARTER_SPECIES\n", "VAR_UNUSED_0x4031\n"),

    # Breeding / hatch engine must remain byte-identical to pre-D8.
    "ordinary daycare source edited": ("src/overlay005/daycare.c", None, "\n/* D8 mutation */\n"),
    "egg hatch engine edited": ("src/egg_hatch.c", None, "\n/* D8 mutation */\n"),
    "field hatch engine edited": ("src/unk_0203D1B8.c", None, "\n/* D8 mutation */\n"),
    "daycare header edited": ("include/overlay005/daycare.h", None, "\n/* D8 mutation */\n"),
    "egg hatch args edited": ("include/egg_hatch.h", None, "\n/* D8 mutation */\n"),
    "daycare constants edited": ("include/constants/daycare.h", None, "\n#define MUTATED_HATCH_CONSTANT 1\n"),

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
