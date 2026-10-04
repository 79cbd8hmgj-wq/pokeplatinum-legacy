#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ROUTE = ROOT / "res/field/scripts/scripts_route_201.s"
CHOOSER = ROOT / "src/choose_starter/choose_starter_app.c"
SCRCMD = ROOT / "src/scrcmd.c"
TABLE = ROOT / "include/data/scripts/scrcmd.h"
MACROS = ROOT / "asm/macros/scrcmd.inc"
SANDGEM = ROOT / "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"
VARS = ROOT / "generated/vars_flags.txt"

EXPECTED = [
    (3, "Bulbasaur", "SPECIES_BULBASAUR", "SPECIES_TURTWIG"),
    (6, "Charmander", "SPECIES_CHARMANDER", "SPECIES_CHIMCHAR"),
    (9, "Squirtle", "SPECIES_SQUIRTLE", "SPECIES_PIPLUP"),
    (10, "Pikachu", "SPECIES_PIKACHU", "SPECIES_PIPLUP"),
    (20, "Chikorita", "SPECIES_CHIKORITA", "SPECIES_TURTWIG"),
    (30, "Cyndaquil", "SPECIES_CYNDAQUIL", "SPECIES_CHIMCHAR"),
    (40, "Totodile", "SPECIES_TOTODILE", "SPECIES_PIPLUP"),
    (50, "Treecko", "SPECIES_TREECKO", "SPECIES_TURTWIG"),
    (60, "Torchic", "SPECIES_TORCHIC", "SPECIES_CHIMCHAR"),
    (70, "Mudkip", "SPECIES_MUDKIP", "SPECIES_PIPLUP"),
    (80, "Turtwig", "SPECIES_TURTWIG", "SPECIES_TURTWIG"),
    (90, "Chimchar", "SPECIES_CHIMCHAR", "SPECIES_CHIMCHAR"),
]
DEFAULT = ("Piplup", "SPECIES_PIPLUP", "SPECIES_PIPLUP")
EXPECTED_COUNTS = {
    "SPECIES_BULBASAUR": 3,
    "SPECIES_CHARMANDER": 3,
    "SPECIES_SQUIRTLE": 3,
    "SPECIES_PIKACHU": 1,
    "SPECIES_CHIKORITA": 10,
    "SPECIES_CYNDAQUIL": 10,
    "SPECIES_TOTODILE": 10,
    "SPECIES_TREECKO": 10,
    "SPECIES_TORCHIC": 10,
    "SPECIES_MUDKIP": 10,
    "SPECIES_TURTWIG": 10,
    "SPECIES_CHIMCHAR": 10,
    "SPECIES_PIPLUP": 10,
}

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)

def function_body(src: str, name: str) -> str:
    m = re.search(rf"static BOOL {re.escape(name)}\(ScriptContext \*ctx\)\s*\{{", src)
    if not m:
        fail(f"missing {name}")
    start = m.start()
    brace = src.find("{", m.start())
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start : i + 1]
    fail(f"unterminated {name}")
    return ""

def parse_route(route: str):
    m = re.search(r"Route201_ResolveMysteryStarter:\n(?P<body>.*?)\nRoute201_DawnLeave:", route, re.S)
    if not m:
        fail("missing Mystery starter resolver")
    body = m.group("body")

    thresholds = [
        (int(n), label)
        for n, label in re.findall(
            r"GoToIfLt VAR_0x8001, (\d+), Route201_MysteryStarter_(\w+)", body
        )
    ]
    expected_thresholds = [(n, label) for n, label, _, _ in EXPECTED]
    if thresholds != expected_thresholds:
        fail(f"threshold table mismatch: {thresholds!r}")

    if "GoTo Route201_MysteryStarter_Piplup" not in body:
        fail("missing Piplup default branch")

    assignments = {}
    for label, species, branch in [(x[1], x[2], x[3]) for x in EXPECTED] + [DEFAULT]:
        pat = (
            rf"Route201_MysteryStarter_{label}:\s*"
            rf"SetVar VAR_MYSTERY_STARTER_SPECIES, ({species})\s*"
            rf"SetVar VAR_PLAYER_STARTER, ({branch})\s*Return"
        )
        if not re.search(pat, body):
            fail(f"bad assignment block for {label}")
        assignments[label] = (species, branch)

    return thresholds, assignments

def simulate(thresholds, assignments):
    out = []
    for roll in range(100):
        label = DEFAULT[0]
        for upper, candidate in thresholds:
            if roll < upper:
                label = candidate
                break
        out.append((roll, *assignments[label]))
    return out

def main() -> int:
    route = read(ROUTE)
    chooser = read(CHOOSER)
    scrcmd = read(SCRCMD)
    table = read(TABLE)
    macros = read(MACROS)
    sandgem = read(SANDGEM)
    vars_txt = read(VARS)

    active_flow = """    StartChooseStarterScene
    SaveChosenStarter
    ReturnToField
    FadeScreenIn
    WaitFadeScreen
    GetRandom VAR_0x8001, 100
    Call Route201_ResolveMysteryStarter
    SetVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES
    GivePokemon VAR_0x8000, 5, ITEM_NONE, VAR_RESULT"""
    if active_flow not in route:
        fail("active Route 201 flow is not vanilla-return + script-native RNG")

    save = function_body(scrcmd, "ScrCmd_SaveChosenStarter")
    if "ChooseStarterData *chooseStarterData" not in save:
        fail("SaveChosenStarter no longer reads vanilla chooser output")
    if "SystemVars_SetPlayerStarter" not in save or "chooseStarterData->species" not in save:
        fail("SaveChosenStarter is not vanilla starter persistence")
    if "MysteryStarter" in save or "VAR_MYSTERY_STARTER_SPECIES" in save:
        fail("custom Mystery logic re-entered SaveChosenStarter")

    if "MakeMysteryEggSprite" not in chooser or "SPECIES_EGG" not in chooser:
        fail("Mystery Egg chooser visuals missing")
    if not re.search(r"for \(int i = 0; i < NUM_STARTER_OPTIONS; i\+\+\) \{\s*MakeMysteryEggSprite", chooser):
        fail("chooser is not building all three previews as Mystery Eggs")
    if "Sound_PlayPokemonCry" in chooser:
        fail("chooser reveals species via cry")

    forbidden = (
        "GETMYSTERYSTARTERSPECIES",
        "GIVEMYSTERYSTARTEREGG",
        "HATCHMYSTERYSTARTEREGG",
    )
    joined = table + "\n" + macros
    if any(token in joined.upper() for token in forbidden):
        fail("retired custom Mystery script command still registered")
    if "ScrCmd_GetMysteryStarterSpecies" in scrcmd or "ScrCmd_GiveMysteryStarterEgg" in scrcmd or "ScrCmd_HatchMysteryStarterEgg" in scrcmd:
        fail("retired custom Mystery script command implementation still active")

    if "SetVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES" not in sandgem:
        fail("Sandgem starter-gift logic is not using native variable copy")
    if "GetMysteryStarterSpecies" in sandgem:
        fail("Sandgem still calls retired custom getter")

    if "VAR_PLAYER_STARTER\nVAR_MYSTERY_STARTER_SPECIES\n" not in vars_txt:
        fail("Mystery species is no longer the existing slot immediately after VAR_PLAYER_STARTER")

    thresholds, assignments = parse_route(route)
    sim = simulate(thresholds, assignments)
    counts = Counter(species for _, species, _ in sim)
    if dict(counts) != EXPECTED_COUNTS:
        fail(f"0..99 weight coverage mismatch: {dict(counts)!r}")

    branch_expect = {
        "SPECIES_BULBASAUR": "SPECIES_TURTWIG",
        "SPECIES_CHIKORITA": "SPECIES_TURTWIG",
        "SPECIES_TREECKO": "SPECIES_TURTWIG",
        "SPECIES_TURTWIG": "SPECIES_TURTWIG",
        "SPECIES_CHARMANDER": "SPECIES_CHIMCHAR",
        "SPECIES_CYNDAQUIL": "SPECIES_CHIMCHAR",
        "SPECIES_TORCHIC": "SPECIES_CHIMCHAR",
        "SPECIES_CHIMCHAR": "SPECIES_CHIMCHAR",
        "SPECIES_SQUIRTLE": "SPECIES_PIPLUP",
        "SPECIES_TOTODILE": "SPECIES_PIPLUP",
        "SPECIES_MUDKIP": "SPECIES_PIPLUP",
        "SPECIES_PIPLUP": "SPECIES_PIPLUP",
        "SPECIES_PIKACHU": "SPECIES_PIPLUP",
    }
    for roll, species, branch in sim:
        if branch_expect[species] != branch:
            fail(f"roll {roll}: {species} mapped to wrong story branch {branch}")

    print("PASS: D8 script-native Mystery starter — Egg chooser retained, vanilla return boundary, 100/100 rolls covered, weights/branches exact, no custom script commands")
    return 0

if __name__ == "__main__":
    sys.exit(main())
