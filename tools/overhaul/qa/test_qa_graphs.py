#!/usr/bin/env python3
"""Mutation/regression tests for the D7 completion-graph checker (each mutation must be caught)."""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import build_qa_graphs as q  # noqa: E402


class Mut(unittest.TestCase):
    def run_with(self, live_fn=None, jl_fn=None):
        ol, oj = q.load_live, q.jl
        try:
            if live_fn:
                q.load_live = lambda names: live_fn(copy.deepcopy(ol(names)))
            if jl_fn:
                q.jl = lambda rel: jl_fn(rel, copy.deepcopy(oj(rel)))
            return q.build()
        finally:
            q.load_live, q.jl = ol, oj

    def test_baseline_clean(self):
        _, errors, _ = self.run_with()
        self.assertEqual(errors, [])

    def test_trade_evolution_rejected(self):
        def m(live):
            live["SPECIES_MACHOKE"]["evolutions"] = [["EVO_TRADE", "SPECIES_MACHAMP"]]
            return live
        _, errors, _ = self.run_with(live_fn=m)
        self.assertTrue(any("forbidden evolution method" in e for e in errors))

    def test_non_stone_item_rejected(self):
        def m(live):
            live["SPECIES_PIKACHU"]["evolutions"] = [["EVO_USE_ITEM", "ITEM_POTION", "SPECIES_RAICHU"]]
            return live
        _, errors, _ = self.run_with(live_fn=m)
        self.assertTrue(any("not a renewable pre-E4 stone" in e for e in errors))

    def test_unlearnable_move_evolution_rejected(self):
        def m(live):
            live["SPECIES_AIPOM"]["evolutions"] = [["EVO_LEVEL_KNOW_MOVE", "MOVE_SPLASH", "SPECIES_AMBIPOM"]]
            return live
        _, errors, _ = self.run_with(live_fn=m)
        self.assertTrue(any("move-known evolution" in e for e in errors))

    def test_unreachable_species_rejected(self):
        def m(live):  # cut Kadabra off from Abra
            live["SPECIES_ABRA"]["evolutions"] = []
            return live
        _, errors, _ = self.run_with(live_fn=m)
        self.assertTrue(any("SPECIES_KADABRA: unreachable" in e for e in errors))

    def test_postgame_only_family_rejected(self):
        def j(rel, d):
            if rel.endswith("availability_families.json"):
                for f in d["families"]:
                    if f["family_id"] == "bulbasaur":
                        f["availability_status"], f["special_acquisition_key"] = "PLACE_WILD", None
            if rel.endswith("wild_encounters.json"):
                for e in d["entries"]:
                    if e["family_id"] == "pidgey":
                        e["bonus_system"] = "radar"
            return d
        _, errors, _ = self.run_with(jl_fn=j)
        self.assertTrue(any("only postgame/bonus-system" in e or "no wild entry" in e for e in errors))

    def test_event_cycle_rejected(self):
        def j(rel, d):
            if rel.endswith("native_legendary_events.json"):
                for e in d["events"]:
                    if e["species"] == "SPECIES_REGIROCK":
                        e["internal_prerequisites"] = ["SPECIES_REGIGIGAS"]
            return d
        _, errors, _ = self.run_with(jl_fn=j)
        self.assertTrue(any("circular event dependency" in e for e in errors))

    def test_external_dependency_in_event_rejected(self):
        def j(rel, d):
            if rel.endswith("native_legendary_events.json"):
                d["events"][0]["target_gates"] = ["requires trade with another game"]
            return d
        _, errors, _ = self.run_with(jl_fn=j)
        self.assertTrue(any("external dependency" in e for e in errors))

    def test_something_depending_on_arceus_rejected(self):
        def j(rel, d):
            if rel.endswith("native_legendary_events.json"):
                for e in d["events"]:
                    if e["species"] == "SPECIES_MANAPHY":
                        e["internal_prerequisites"] = ["SPECIES_ARCEUS"]
            return d
        _, errors, _ = self.run_with(jl_fn=j)
        self.assertTrue(any("depends on Arceus" in e or "circular" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
