#!/usr/bin/env python3
"""Regression/mutation tests for the D7 QA validators (incl. the Solar Petal contact-flag fix)."""
import contextlib
import copy
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import validate_created_moves as vcm  # noqa: E402
import validate_id_integrity as vid  # noqa: E402
import validate_species_c3 as vsc  # noqa: E402
import build_runtime_matrix as brm  # noqa: E402
import validate_runtime_matrix as vrm  # noqa: E402


def run(mod, fn):
    orig = mod.jl
    mod.jl = fn(orig)
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = mod.main()
    finally:
        mod.jl = orig
    return rc, out.getvalue()


class T(unittest.TestCase):
    def test_baselines_pass(self):
        for m in (vcm, vid, vsc):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(), 0, m.__name__)

    def test_solar_petal_contact_regression(self):
        def f(orig):
            def j(rel):
                d = copy.deepcopy(orig(rel))
                if rel == "res/moves/solar_petal/data.json":
                    d["flags"].remove("MOVE_FLAG_MAKES_CONTACT")
                return d
            return j
        rc, out = run(vcm, f)
        self.assertEqual(rc, 1)
        self.assertIn("MOVE_SOLAR_PETAL contact flag", out)

    def test_magnet_volley_escalation_caught(self):
        def f(orig):
            def j(rel):
                d = copy.deepcopy(orig(rel))
                if rel == "res/moves/magnet_volley/data.json":
                    d["effect"]["type"] = "BATTLE_EFFECT_TRIPLE_KICK"
                return d
            return j
        self.assertEqual(run(vcm, f)[0], 1)

    def test_invalid_trainer_move_caught(self):
        def f(orig):
            def j(rel):
                d = copy.deepcopy(orig(rel))
                if rel.endswith("res/trainers/data/leader_roark.json"):
                    d["party"][0]["moves"][0] = "MOVE_NOT_A_MOVE"
                return d
            return j
        rc, out = run(vid, f)
        self.assertEqual(rc, 1)
        self.assertIn("invalid move MOVE_NOT_A_MOVE", out)

    def test_c3_postcondition_violation_caught(self):
        orig = vsc.species_data
        op = next(c for l in vsc.rec.decode_ledgers(vsc.text("docs/overhaul/implementation/archive/c3h-apply-species-original.yml"))
                  for c in l["changes"] if c["operation"] == "set_base_stat")

        def bad():
            d = copy.deepcopy(orig())
            d[op["species"]]["base_stats"][op["stat"]] = 1
            return d
        vsc.species_data = bad
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(vsc.main(), 1)
        finally:
            vsc.species_data = orig


class Runtime(unittest.TestCase):
    def test_pass_without_evidence_rejected(self):
        orig = brm.load_ledger
        def bad():
            led = copy.deepcopy(orig())
            led["results"]["MV-01|US Rev 0"] = {"actual": "ok", "result": "PASS", "tester": "", "date": "", "evidence": ""}
            return led
        brm.load_ledger = bad
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(vrm.main(), 1)
        finally:
            brm.load_ledger = orig

    def test_baseline_not_run(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(vrm.main(), 0)
        self.assertIn("RUNTIME QA PENDING", out.getvalue())


if __name__ == "__main__":
    unittest.main()
