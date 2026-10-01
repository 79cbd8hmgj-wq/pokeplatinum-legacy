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
FILES = ["availability_families.json", "wild_encounters.json", "special_systems.json", "encounter_zones.json"]


def run(mutate):
    tmp = Path(tempfile.mkdtemp())
    try:
        docs = {f: json.load(open(IMPL / f)) for f in FILES}
        mutate(docs)
        for f, d in docs.items():
            json.dump(d, open(tmp / f, "w"))
        env = dict(os.environ, AVAIL_IMPL_DIR=str(tmp))
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


def main():
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
    print(f"{len(CASES) - bad}/{len(CASES)} mutation cases detected")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
