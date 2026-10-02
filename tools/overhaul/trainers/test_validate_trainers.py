#!/usr/bin/env python3
"""Mutation tests: the trainer validator must reject each corrupted in-memory copy (no source files are touched)."""
from __future__ import annotations

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import validate_trainers as vt
from trainer_lib import load_trainer, trainer_files

RULES = vt.load(vt.RULES)
MAN = vt.load(vt.MANIFEST)
BASE = {t: load_trainer(t) for t in trainer_files()}


def run(mutate) -> vt.Result:
    data = copy.deepcopy(BASE)
    mutate(data)
    vt.load_trainer = lambda t: copy.deepcopy(data[t])
    vt.trainer_files = lambda: sorted(data)
    res = vt.Result()
    d = vt.check_source(res, RULES)
    vt.check_manifest(res, MAN, d, False)
    vt.check_bosses(res, RULES, MAN, d)
    vt.rival_structure(res, MAN, d)
    vt.check_ordinary(res, d, vt.category_of(MAN))
    return res


def expect(name, mutate, needle):
    res = run(mutate)
    ok = any(needle in e for e in res.errors)
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        print("   errors:", res.errors[:3])
    return ok


def m_species(d):
    d["leader_roark"]["party"][0]["species"] = "SPECIES_NOT_A_MON"


def m_empty(d):
    d["ace_trainer_abel"]["party"] = []


def m_over(d):
    d["ace_trainer_abel"]["party"] = d["ace_trainer_abel"]["party"] * 4


def m_size(d):
    d["leader_roark"]["party"].append(copy.deepcopy(d["leader_roark"]["party"][0]))


def m_level(d):
    d["leader_gardenia"]["party"][2]["level"] = 40


def m_dup(d):
    d["elite_four_aaron"]["party"][1] = copy.deepcopy(d["elite_four_aaron"]["party"][0])


def m_ai(d):
    d["champion_cynthia"]["ai_flags"] = ["AI_FLAG_BASIC"]


def m_move(d):
    d["leader_candice"]["party"][0]["moves"][0] = "MOVE_DRAGON_SWIPE"


def m_badmove(d):
    d["leader_candice"]["party"][0]["moves"][0] = "MOVE_NOT_REAL"


def m_item(d):
    d["leader_roark"]["party"][0]["item"] = "ITEM_NOT_REAL"


def m_avail(d):
    d["youngster_logan"]["party"][0]["species"] = "SPECIES_GARCHOMP"


def m_evo(d):
    d["youngster_logan"]["party"][0]["species"] = "SPECIES_MAGNEMITE"
    d["youngster_logan"]["party"][0]["level"] = 40


def m_drift(d):
    d["leader_wake"]["party"][0]["level"] = 34


def m_encoding(d):
    d["ace_trainer_abel"]["party"][1]["moves"] = None


def m_gymteam(d):
    d["leader_fantina"]["party"][0]["moves"][0] = "MOVE_TACKLE"


def m_forbidden(d):
    d["leader_byron"]["party"][0]["item"] = "ITEM_LEFTOVERS"


def m_rival(d):
    d["rival_pokemon_league_chimchar"]["party"][0]["level"] = 40


def m_gym1_item(d):
    for m in d["leader_roark"]["party"]:
        m["item"] = "ITEM_NONE"
    d["leader_roark"]["party"][0]["item"] = "ITEM_SITRUS_BERRY"


def m_ace(d):
    d["leader_volkner"]["party"][4]["level"] = 49


TESTS = [
    ("invalid species", m_species, "invalid species"), ("empty party", m_empty, "empty party"),
    ("oversized party", m_over, "oversized"), ("wrong boss party size", m_size, "party size"),
    ("level outside band", m_level, "level outside"), ("duplicate on important team", m_dup, "duplicate"),
    ("missing boss AI", m_ai, "missing required boss AI"), ("unresolved move constant", m_move, "unresolved"),
    ("invalid move", m_badmove, "invalid move"), ("invalid item", m_item, "invalid item"),
    ("ordinary availability violation", m_avail, "family band"), ("evolution contradiction", m_evo, "evolution-stage"),
    ("manifest/source drift", m_drift, "drifted"), ("non-uniform encoding", m_encoding, "non-uniform"),
    ("gym team != locked spec", m_gymteam, "does not match the locked spec"),
    ("forbidden main-story held item", m_forbidden, "forbidden"), ("rival branch level mismatch", m_rival, "levels differ"),
    ("gym 1 held item", m_gym1_item, "Gym 1"), ("ace level != locked", m_ace, "ace level"),
]

if __name__ == "__main__":
    ok = all([expect(*t) for t in TESTS])
    clean = run(lambda d: None)
    print(("PASS " if not clean.errors else "FAIL ") + "unmutated tree has 0 errors")
    sys.exit(0 if ok and not clean.errors else 1)
