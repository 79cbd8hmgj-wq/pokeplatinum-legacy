#!/usr/bin/env python3
"""Mutation tests: each mutated manifest copy MUST make the availability validator fail with the expected code.

  python3 tools/overhaul/availability/test_validators.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMPL = HERE.parents[2] / "docs" / "overhaul" / "implementation"
FILES = ["availability_families.json", "wild_encounters.json", "special_systems.json", "encounter_zones.json",
         "special_acquisitions.json"]
ROOT = HERE.parents[2]
FIXED_SRC = ["src/system_vars.c", "include/data/field/hidden_items.h", "src/underground/mining.c", "src/scrcmd_fossil.c",
             "src/overlay006/feebas_fishing.c", "res/field/encounters/encounters_mt_coronet_b1f.json"]


def _referenced_sources(docs):
    out = set(FIXED_SRC)

    def walk(o):
        if isinstance(o, str) and o.startswith(("res/", "src/", "include/")) and "." in o:
            out.add(o)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(docs["special_acquisitions.json"])
    return sorted(out)


def run(mutate, src_mutate=None):
    tmp = Path(tempfile.mkdtemp())
    try:
        docs = {f: json.load(open(IMPL / f)) for f in FILES}
        mutate(docs)
        for f, d in docs.items():
            json.dump(d, open(tmp / f, "w"))
        src = {rel: (ROOT / rel).read_text() for rel in _referenced_sources(docs)}
        if src_mutate:
            src_mutate(src)
        for rel, text in src.items():
            (tmp / "src" / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / "src" / rel).write_text(text)
        env = dict(os.environ, AVAIL_IMPL_DIR=str(tmp), AVAIL_SRC_ROOT=str(tmp / "src"))
        r = subprocess.run([sys.executable, str(HERE / "validate_availability.py"), "--state", "manifest"],
                           env=env, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp)


def entries(docs, **kw):
    return [e for e in docs["wild_encounters.json"]["entries"] if all(e.get(k) == v for k, v in kw.items())]


def m_remove_family(d):          # Aipom exists only in authored tables (+ the Honey bonus array) -> no stable path left
    for e in entries(d, species="SPECIES_AIPOM"):
        e["species"] = "SPECIES_STARLY"


def m_below_floor(d):            # dunsparce only reachable at 4%
    for e in entries(d, species="SPECIES_DUNSPARCE"):
        e["species"] = "SPECIES_ZUBAT"
    e = entries(d, map="oreburgh_gate_1f", method="land", slot=8)[0]
    e["species"] = "SPECIES_DUNSPARCE"


def m_dual_slot(d):
    d["special_systems.json"]["dual_slot"]["maps"]["route_201"]["after"] = ["SPECIES_PIKACHU", "SPECIES_PIKACHU"]


def m_marsh(d):
    arr = d["special_systems.json"]["great_marsh"]["arrays"]["before_national_dex"]
    arr["after"] = arr["before"]


def m_decision(d):               # Eevee is a USER_DECISION family: wild placement must be rejected
    entries(d, map="route_201", method="land", slot=4)[0]["species"] = "SPECIES_EEVEE"


def m_legendary(d):
    entries(d, map="route_201", method="land", slot=4)[0]["species"] = "SPECIES_ARTICUNO"


def m_density(d):                # push a connector above 5 families
    for slot, sp in ((0, "SPECIES_CATERPIE"), (1, "SPECIES_PIDGEY"), (4, "SPECIES_RATTATA")):
        entries(d, map="ravaged_path", method="land", slot=slot)[0]["species"] = sp


def m_night_only(d):             # hoothoot placed only in a night-only slot
    for e in entries(d, species="SPECIES_HOOTHOOT"):
        e["species"] = "SPECIES_STARLY"
    for e in d["wild_encounters.json"]["entries"]:
        if e["map"] == "route_201" and e["method"] == "land_night" and e["slot"] == 3:
            e["species"] = "SPECIES_HOOTHOOT"
    # note: land slot 3 (morning) stays starly, so hoothoot has no all-day path


def m_too_early(d):              # a matrix-M1 family (doduo) placed in an E0 map
    entries(d, map="route_201", method="land", slot=4)[0]["species"] = "SPECIES_DODUO"


def m_super_rod_only(d):         # a family whose only route is Super Rod is not PRE_E4
    for e in entries(d, species="SPECIES_STARYU"):
        e["species"] = "SPECIES_MAGIKARP"
    # staryu now absent from Good Rod; add via super rod only
    d["wild_encounters.json"]["entries"].append({
        "map": "canalave_city", "method": "super_rod", "slot": 0, "species": "SPECIES_STARYU", "family_id": "staryu",
        "level_min": 30, "level_max": 55, "rate_pct": 40, "time_condition": "any", "band": "P1", "zone": "COAST",
        "bonus_system": None, "before": {"species": "SPECIES_GYARADOS", "level_min": 30, "level_max": 55}})


def m_stale_fallback(d):
    d["special_systems.json"]["radar"]["maps"]["route_201"]["entries"][0]["fallback"] = {
        "map": "route_201", "method": "land", "species": "SPECIES_NIDORAN_M", "min_rate_pct": 20, "band": "E0"}


def m_safari_only(d):            # tangela left only in the (Safari-format) Great Marsh
    for e in entries(d, map="route_213", species="SPECIES_TANGELA"):
        e["species"] = "SPECIES_STARLY"


CASES = [("family with no path", m_remove_family, "V4"), ("rate below 5%", m_below_floor, "V4"),
         ("dual-slot not neutral", m_dual_slot, "V7"), ("marsh Dex arrays differ", m_marsh, "V7"),
         ("decision family placed", m_decision, "V6"), ("legendary placed", m_legendary, "V12"),
         ("connector density", m_density, "V8"), ("night-only family", m_night_only, "V4"),
         ("earlier than matrix band", m_too_early, "V4"), ("super-rod-only family", m_super_rod_only, "V4"),
         ("stale fallback pointer", m_stale_fallback, "V7"), ("Safari-only family", m_safari_only, "V4")]


def sub(src, rel, old, new, count=1):
    assert old in src[rel], f"mutation anchor not found in {rel}: {old!r}"
    src[rel] = src[rel].replace(old, new, count)


CAST = "res/field/scripts/scripts_veilstone_city.s"
TYRO = "res/field/scripts/scripts_celestic_town_southwest_house.s"
EEVEE = "res/field/scripts/scripts_hearthome_city_northwest_house.s"
PORY = "res/field/scripts/scripts_veilstone_city_northeast_house.s"
RIOLU = "res/field/scripts/scripts_iron_island_b2f_left_room.s"
ROTOM = "res/field/scripts/scripts_old_chateau_back_middle_west_room.s"
SPIRIT = "res/field/scripts/scripts_route_209.s"
LAB = "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"
MINING = "src/underground/mining.c"
FEEBAS = "src/overlay006/feebas_fishing.c"
noop = lambda d: None

SPECIAL_CASES = [
    ("gift: no party-full guard (Castform)", noop, lambda s: sub(s, CAST, "    GoToIfEq VAR_RESULT, MAX_PARTY_SIZE, VeilstoneCity_BattleGirl2_PartyFull\n", ""), "S2"),
    ("gift: flag set before give (Tyrogue)", noop, lambda s: sub(s, TYRO, "    GivePokemon SPECIES_TYROGUE, 15, ITEM_NONE, VAR_RESULT\n", "    SetFlag FLAG_RECEIVED_CELESTIC_TOWN_SOUTHWEST_HOUSE_TYROGUE\n    GivePokemon SPECIES_TYROGUE, 15, ITEM_NONE, VAR_RESULT\n"), "S2"),
    ("gift: external trade required (Eevee)", noop, lambda s: sub(s, EEVEE, "HearthomeCityNorthwestHouse_AcceptEevee:\n", "HearthomeCityNorthwestHouse_AcceptEevee:\n    StartNPCTrade 0\n"), "S4"),
    ("gift: link/multiplayer required (Eevee)", noop, lambda s: sub(s, EEVEE, "HearthomeCityNorthwestHouse_AcceptEevee:\n", "HearthomeCityNorthwestHouse_AcceptEevee:\n    StartBattleClient\n"), "S4"),
    ("gift: National Dex gate on the give path (Porygon)", noop, lambda s: sub(s, PORY, "VeilstoneCityNortheastHouse_AcceptPorygonYesNo:\n", "VeilstoneCityNortheastHouse_AcceptPorygonYesNo:\n    GetNationalDexEnabled VAR_RESULT\n"), "S4"),
    ("gift: Mystery Gift/WFC distribution check (Porygon)", noop, lambda s: sub(s, PORY, "VeilstoneCityNortheastHouse_AcceptPorygonYesNo:\n", "VeilstoneCityNortheastHouse_AcceptPorygonYesNo:\n    CheckDistributionEvent DISTRIBUTION_EVENT_ROTOM, VAR_RESULT\n"), "S4"),
    ("gift: post-E4 band (Castform)", lambda d: d["special_acquisitions.json"]["acquisitions"]["castform"].update(band="P1"), None, "S3"),
    ("gift: badge gate beyond 8 (starter)", lambda d: d["special_acquisitions.json"]["acquisitions"]["mudkip"]["gift"].update(min_badges=9), None, "S3"),
    ("Riolu: recovery flag removed", noop, lambda s: sub(s, RIOLU, "    SetFlag FLAG_COULD_NOT_RECEIVE_RIOLU_EGG\n    SetVar VAR_IRON_ISLAND_B2F_LEFT_ROOM_FOLLOWER_RILEY_STATE, 2\n    Message IronIslandB2FLeftRoom_Text_NoRoomToTakeEgg", "    SetVar VAR_IRON_ISLAND_B2F_LEFT_ROOM_FOLLOWER_RILEY_STATE, 2\n    Message IronIslandB2FLeftRoom_Text_NoRoomToTakeEgg"), "S2"),
    ("Riolu: egg given without party guard", noop, lambda s: sub(s, RIOLU, "    GoToIfEq VAR_RESULT, MAX_PARTY_SIZE, IronIslandB2FLeftRoom_NoRoomToTakeEgg\n", ""), "S2"),
    ("Rotom: daily cap restored", noop, lambda s: sub(s, ROTOM, "    GetTimeOfDay VAR_RESULT\n", "    GoToIfSet FLAG_DAILY_BATTLED_OLD_CHATEAU_ROTOM, OldChateauBackMiddleWestRoom_TVHasMalevolentFeel\n    GetTimeOfDay VAR_RESULT\n"), "S4"),
    ("Rotom: no Secret Key / form unlock", noop, lambda s: sub(s, ROTOM, "    SetVar VAR_0x8004, ITEM_SECRET_KEY\n", ""), "S1"),
    ("Rotom: form room regated on the distribution event", noop, lambda s: sub(s, "res/field/scripts/scripts_rotoms_room.s", "RotomsRoom_OnTransition:\n", "RotomsRoom_OnTransition:\n    CheckDistributionEvent DISTRIBUTION_EVENT_ROTOM, VAR_MAP_LOCAL_0x00\n"), "S1"),
    ("Rotom: uncaught Rotom not recoverable", noop, lambda s: sub(s, ROTOM, "    CheckDidNotCapture VAR_RESULT\n    GoToIfEq VAR_RESULT, TRUE, OldChateauBackMiddleWestRoom_RotomDisappearedIntoTV\n", ""), "S2"),
    ("fossil: Armor Fossil depends on Trainer ID", noop, lambda s: sub(s, MINING, "MINING_TREASURE_ARMOR_FOSSIL, .oddTIDWeight = 12, .evenTIDWeight = 12,", "MINING_TREASURE_ARMOR_FOSSIL, .oddTIDWeight = 0, .evenTIDWeight = 12,"), "S4"),
    ("fossil: Helix Fossil gated by National Dex", noop, lambda s: sub(s, MINING, "MINING_TREASURE_HELIX_FOSSIL, .oddTIDWeight = 3, .evenTIDWeight = 3, .oddTIDNatDexWeight = 3, .evenTIDNatDexWeight = 3,", "MINING_TREASURE_HELIX_FOSSIL, .oddTIDWeight = 0, .evenTIDWeight = 0, .oddTIDNatDexWeight = 3, .evenTIDNatDexWeight = 3,"), "S4"),
    ("fossil: Skull Fossil missing from mining table", noop, lambda s: src_rename(s, MINING, "MINING_TREASURE_SKULL_FOSSIL, .odd", "MINING_TREASURE_SKULL_FOSSIX, .odd"), "S1"),
    ("fossil: revival without party guard", noop, lambda s: sub(s, "res/field/scripts/scripts_mining_museum.s", "    GoToIfEq VAR_RESULT, MAX_PARTY_SIZE, MiningMuseum_PartyFull\n    BufferSpeciesNameFromVar 1", "    BufferSpeciesNameFromVar 1"), "S2"),
    ("Spiritomb: only the multiplayer counter source", noop, lambda s: sub(s, MINING, "        SystemVars_SetSpiritombCounter(varsFlags, counter + 1);\n", ""), "S4"),
    ("Spiritomb: uncaught Spiritomb ends the ritual", noop, lambda s: sub(s, SPIRIT, "    CheckDidNotCapture VAR_RESULT\n    GoToIfEq VAR_RESULT, TRUE, Route209_SpiritombGotAway\n", ""), "S2"),
    ("Feebas: random mixed-record tiles", noop, lambda s: sub(s, FEEBAS, "    rand = FEEBAS_FIXED_TILE_SEED;\n", "    rand = RecordMixedRNG_GetRand(SaveData_GetRecordMixedRNG(fieldSystem->saveData));\n"), "S4"),
    ("Feebas: documented tiles stale", noop, lambda s: sub(s, FEEBAS, "0x42424242", "0x01020304"), "S1"),
    ("starters: two share one flag (exclusive)", lambda d: d["special_acquisitions.json"]["acquisitions"]["bulbasaur"]["gift"].update(flag="FLAG_RECEIVED_STARTER_KANTO_CHARMANDER"), None, "S5"),
    ("starters: chosen Sinnoh starter offered back", noop, lambda s: sub(s, LAB, "    GoToIfEq VAR_0x8000, SPECIES_TURTWIG, SandgemTownLab_StarterGift_Sinnoh_SkipTurtwig\n", ""), "S5"),
    ("starters: a regional starter missing", lambda d: (d["special_acquisitions.json"]["acquisitions"].pop("mudkip"), d["availability_families.json"]["families"][[f["family_id"] for f in d["availability_families.json"]["families"]].index("mudkip")].update(availability_status="PLACE_WILD", special_acquisition=False)), None, "V4"),
    ("special family dropped from the manifest", lambda d: d["special_acquisitions.json"]["acquisitions"].pop("castform"), None, "S1"),
]


def src_rename(s, rel, old, new):
    sub(s, rel, old, new)


def vanilla_control():
    """The pre-special-acquisition source (main at f89dfc79) must be rejected for every deferred family it did not solve."""
    import subprocess
    docs = {f: json.load(open(IMPL / f)) for f in FILES}
    tmp = Path(tempfile.mkdtemp())
    try:
        for f, d in docs.items():
            json.dump(d, open(tmp / f, "w"))
        for rel in _referenced_sources(docs):
            text = subprocess.run(["git", "show", f"f89dfc79:{rel}"], cwd=ROOT, capture_output=True, text=True).stdout
            (tmp / "src" / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / "src" / rel).write_text(text)
        env = dict(os.environ, AVAIL_IMPL_DIR=str(tmp), AVAIL_SRC_ROOT=str(tmp / "src"))
        r = subprocess.run([sys.executable, str(HERE / "validate_availability.py")], env=env, capture_output=True, text=True)
        out = r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp)
    need = ["fossil", "spiritomb", "feebas", "rotom", "castform", "tyrogue", "happiny", "turtwig"]
    missing = [n for n in need if not any(n in l.lower() for l in out.splitlines() if l.startswith("FAIL"))]
    return r.returncode != 0 and not missing, missing


def main():
    ok_v, missing = vanilla_control()
    print(("ok   " if ok_v else "MISS ") + f"vanilla-source control rejected (missing: {missing})")
    code, out = run(lambda d: None)
    assert code == 0, "baseline manifests must validate cleanly:\n" + out
    bad = 0
    for name, mut, expect in CASES:
        code, out = run(mut)
        ok = code != 0 and f"FAIL [{expect}]" in out
        print(("ok   " if ok else "MISS ") + name + f"  (expect {expect})")
        if not ok:
            bad += 1
            print(out[-600:])
    ok_ordinary = len(CASES) - bad
    sbad = 0
    for name, mut, smut, expect in SPECIAL_CASES:
        code, out = run(mut, smut)
        ok = code != 0 and f"FAIL [{expect}]" in out
        print(("ok   " if ok else "MISS ") + name + f"  (expect {expect})")
        if not ok:
            sbad += 1
            print(out[-500:])
    print(f"{ok_ordinary}/{len(CASES)} ordinary-availability mutation cases detected")
    print(f"{len(SPECIAL_CASES) - sbad}/{len(SPECIAL_CASES)} special-acquisition mutation cases detected")
    return 1 if (bad or sbad or not ok_v) else 0


if __name__ == "__main__":
    sys.exit(main())
