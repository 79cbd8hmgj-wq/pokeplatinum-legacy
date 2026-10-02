#!/usr/bin/env python3
"""Mutation tests: every corruption below must be rejected by validate_evolutions."""
import copy
import json
import os
import re
import sys
import unittest

import validate_evolutions as V
from evo_lib import NEW_METHODS, ROOT, VANILLA_METHODS, MANIFEST, load_base_tables, load_live_tables, read_methods_file

MAN = json.load(open(os.path.join(ROOT, MANIFEST)))
BASE = load_base_tables()
LIVE = load_live_tables()
ITEMS, SPECIES, MOVES = V.load_items(), V.load_species(), V.load_moves()
PC, SP = V.read("src/pokemon.c"), V.read("tools/dataproc/src/speciesproc.c")


def run(tables):
    return V.validate(tables, BASE, MAN, ITEMS, SPECIES, MOVES)[0]


def mutate(sp, edges):
    t = copy.deepcopy(LIVE)
    t[sp] = edges
    return t


class Baseline(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(run(LIVE), [])
        f = []
        V.check_engine_source(PC, read_methods_file(), SP, f)
        self.assertEqual(f, [])


class Mutations(unittest.TestCase):
    def rejects(self, sp, edges):
        self.assertTrue(run(mutate(sp, edges)), f"{sp} -> {edges} was not rejected")

    def test_trade_restorations(self):
        for sp, tgt in (("kadabra", "ALAKAZAM"), ("machoke", "MACHAMP"), ("graveler", "GOLEM"), ("haunter", "GENGAR")):
            self.rejects(sp, [["EVO_TRADE", f"SPECIES_{tgt}"]])

    def test_item_trade_restorations(self):
        cases = [("onix", "ITEM_METAL_COAT", "STEELIX"), ("scyther", "ITEM_METAL_COAT", "SCIZOR"), ("seadra", "ITEM_DRAGON_SCALE", "KINGDRA"),
                 ("electabuzz", "ITEM_ELECTIRIZER", "ELECTIVIRE"), ("magmar", "ITEM_MAGMARIZER", "MAGMORTAR"), ("rhydon", "ITEM_PROTECTOR", "RHYPERIOR"),
                 ("porygon", "ITEM_UPGRADE", "PORYGON2"), ("porygon2", "ITEM_DUBIOUS_DISC", "PORYGON_Z"), ("dusclops", "ITEM_REAPER_CLOTH", "DUSKNOIR")]
        for sp, it, tgt in cases:
            self.rejects(sp, [["EVO_TRADE_WITH_HELD_ITEM", it, f"SPECIES_{tgt}"]])

    def test_held_night_restorations(self):
        self.rejects("gligar", [["EVO_LEVEL_WITH_HELD_ITEM_NIGHT", "ITEM_RAZOR_FANG", "SPECIES_GLISCOR"]])
        self.rejects("sneasel", [["EVO_LEVEL_WITH_HELD_ITEM_NIGHT", "ITEM_RAZOR_CLAW", "SPECIES_WEAVILE"]])

    def test_wrong_level_every_locked_level(self):
        n = 0
        for sp, edges in V.LOCKED_FINAL.items():
            for i, e in enumerate(edges):
                if V.PARAM_KIND[e[0]] == "level":
                    bad = copy.deepcopy(edges)
                    bad[i][1] += 1
                    self.rejects(sp, bad)
                    n += 1
        self.assertGreaterEqual(n, 20)

    def test_night_restriction_lost(self):
        self.rejects("gligar", [["EVO_LEVEL", 38, "SPECIES_GLISCOR"]])
        self.rejects("sneasel", [["EVO_LEVEL", 38, "SPECIES_WEAVILE"]])
        self.rejects("happiny", [["EVO_LEVEL", 20, "SPECIES_CHANSEY"]])
        self.rejects("happiny", [["EVO_LEVEL_WITH_HELD_ITEM_DAY", "ITEM_OVAL_STONE", "SPECIES_CHANSEY"]])

    def test_clamperl(self):
        self.rejects("clamperl", [["EVO_LEVEL_SPATK_GT_ATK", 35, "SPECIES_HUNTAIL"], ["EVO_LEVEL_ATK_GT_SPATK", 35, "SPECIES_GOREBYSS"]])  # reversed
        self.rejects("clamperl", [["EVO_LEVEL_ATK_GT_SPATK", 35, "SPECIES_HUNTAIL"], ["EVO_LEVEL_ATK_GT_SPATK", 35, "SPECIES_GOREBYSS"]])  # tie -> nothing
        self.rejects("clamperl", [["EVO_LEVEL_ATK_GT_SPATK", 35, "SPECIES_HUNTAIL"], ["EVO_LEVEL", 35, "SPECIES_GOREBYSS"]])  # overlap

    def test_slowpoke_and_poliwhirl(self):
        self.rejects("slowpoke", [["EVO_LEVEL", 37, "SPECIES_SLOWBRO"], ["EVO_LEVEL_SPDEF_GT_DEF", 37, "SPECIES_SLOWKING"]])  # Slowking shadowed
        self.rejects("poliwhirl", [["EVO_USE_ITEM", "ITEM_WATER_STONE", "SPECIES_POLIWRATH"], ["EVO_LEVEL_ATK_GT_SPATK", 35, "SPECIES_POLITOED"]])
        self.rejects("poliwhirl", [["EVO_LEVEL_SPATK_GT_ATK", 35, "SPECIES_POLITOED"]])  # Poliwrath stone lost

    def test_retained_mechanics(self):
        self.rejects("tyrogue", LIVE["tyrogue"][:2])
        self.rejects("tyrogue", [["EVO_LEVEL_ATK_GE_DEF" if False else "EVO_LEVEL", 20, "SPECIES_HITMONTOP"]] + LIVE["tyrogue"][:2])
        self.rejects("feebas", [["EVO_LEVEL", 30, "SPECIES_MILOTIC"]])
        self.rejects("nosepass", [["EVO_LEVEL", 30, "SPECIES_PROBOPASS"]])
        self.rejects("snorunt", [LIVE["snorunt"][0], ["EVO_USE_ITEM", "ITEM_DAWN_STONE", "SPECIES_FROSLASS"]])
        self.rejects("kirlia", [LIVE["kirlia"][0], ["EVO_USE_ITEM", "ITEM_DAWN_STONE", "SPECIES_GALLADE"]])
        self.rejects("wurmple", [["EVO_LEVEL", 7, "SPECIES_SILCOON"]])
        self.rejects("nincada", [["EVO_LEVEL_NINJASK", 20, "SPECIES_NINJASK"]])

    def test_stone_converted_to_level(self):
        self.rejects("roselia", [["EVO_LEVEL", 30, "SPECIES_ROSERADE"]])
        self.rejects("clefairy", [["EVO_LEVEL", 30, "SPECIES_CLEFABLE"]])
        self.rejects("growlithe", [["EVO_LEVEL", 30, "SPECIES_ARCANINE"]])

    def test_non_stone_item_use(self):
        self.rejects("onix", [["EVO_USE_ITEM", "ITEM_METAL_COAT", "SPECIES_STEELIX"]])

    def test_unauthorised_vanilla_edit(self):
        self.rejects("bulbasaur", [["EVO_LEVEL", 17, "SPECIES_IVYSAUR"]])
        self.rejects("charmander", [["EVO_LEVEL", 15, "SPECIES_CHARMELEON"]])
        t = copy.deepcopy(LIVE)
        del t["pikachu"]
        self.assertTrue(run(t))

    def test_unknown_method_and_target(self):
        self.rejects("abra", [["EVO_BOGUS", 16, "SPECIES_KADABRA"]])
        self.rejects("abra", [["EVO_LEVEL", 16, "SPECIES_NONE"]])


class EngineSource(unittest.TestCase):
    def fails(self, pc=PC, methods=None, sp=SP):
        f = []
        V.check_engine_source(pc, methods or read_methods_file(), sp, f)
        return f

    def test_comparison_semantics(self):
        for old, new in (("MON_DATA_SP_ATK, NULL) > Pokemon_GetValue(mon, MON_DATA_ATK", "MON_DATA_SP_ATK, NULL) >= Pokemon_GetValue(mon, MON_DATA_ATK"),):
            self.assertTrue(self.fails(PC.replace(old, new, 1)))
        # tie behaviour of each new method, evaluated through the engine model
        e = V.eligible
        self.assertFalse(e(["EVO_LEVEL_SPATK_GT_ATK", 35, "X"], 35, 5, 1, 5, 1))
        self.assertTrue(e(["EVO_LEVEL_SPATK_GE_ATK", 35, "X"], 35, 5, 1, 5, 1))
        self.assertFalse(e(["EVO_LEVEL_ATK_GT_SPATK", 35, "X"], 35, 5, 1, 5, 1))
        self.assertFalse(e(["EVO_LEVEL_SPDEF_GT_DEF", 37, "X"], 37, 1, 5, 1, 5))
        self.assertTrue(e(["EVO_LEVEL_SPDEF_GT_DEF", 37, "X"], 37, 1, 4, 1, 5))
        self.assertFalse(e(["EVO_LEVEL_NIGHT", 38, "X"], 38, 1, 1, 1, 1, night=False))
        self.assertFalse(e(["EVO_LEVEL_NIGHT", 38, "X"], 37, 1, 1, 1, 1, night=True))
        self.assertTrue(e(["EVO_LEVEL_DAY", 20, "X"], 20, 1, 1, 1, 1, night=False))
        self.assertFalse(e(["EVO_LEVEL_DAY", 20, "X"], 20, 1, 1, 1, 1, night=True))
        self.assertFalse(e(["EVO_LEVEL_DAY", 20, "X"], 19, 1, 1, 1, 1, night=False))

    def test_each_pokemon_c_operator_mutation_caught(self):
        for m, (a, op, b) in V.STAT_SEMANTICS.items():
            blk = re.search(rf"case {m}:(.*?)break;", PC, re.S)
            bad_op = {">": "<", ">=": "<", "<": ">", "==": ">"}[op]
            bad = blk.group(0).replace(f" {op} Pokemon_GetValue", f" {bad_op} Pokemon_GetValue", 1)
            self.assertTrue(self.fails(PC.replace(blk.group(0), bad)), m)

    def test_method_id_shift_caught(self):
        vm = list(VANILLA_METHODS)
        shifted = [vm[0]] + ["EVO_LEVEL_NIGHT"] + vm[1:] + [m for m in NEW_METHODS if m != "EVO_LEVEL_NIGHT"]
        self.assertTrue(self.fails(methods=shifted))
        self.assertTrue(self.fails(methods=VANILLA_METHODS + NEW_METHODS[:-1]))

    def test_new_ids(self):
        self.assertEqual({m: read_methods_file().index(m) for m in NEW_METHODS},
                         {"EVO_LEVEL_SPATK_GT_ATK": 27, "EVO_LEVEL_SPATK_GE_ATK": 28, "EVO_LEVEL_ATK_GT_SPATK": 29,
                          "EVO_LEVEL_SPDEF_GT_DEF": 30, "EVO_LEVEL_NIGHT": 31})

    def test_dataproc_handler_required(self):
        self.assertTrue(self.fails(sp=SP.replace("case EVO_LEVEL_NIGHT:", "case EVO_NONE_X:")))
        self.assertTrue(self.fails(sp=SP.replace("case EVO_LEVEL_DAY:", "case EVO_NONE_X:")))

    def test_kadabra_no_longer_bypasses_everstone(self):
        self.assertNotIn("monSpecies != SPECIES_KADABRA", PC)
        self.assertTrue(self.fails(pc=PC.replace("if (itemHoldEffect == HOLD_EFFECT_NO_EVOLVE", "if (monSpecies != SPECIES_KADABRA\n        && itemHoldEffect == HOLD_EFFECT_NO_EVOLVE", 1)))


if __name__ == "__main__":
    unittest.main(verbosity=1)
