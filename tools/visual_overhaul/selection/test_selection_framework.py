#!/usr/bin/env python3
"""Negative tests: the validator must catch duplicate/conflicting/untraceable selections.

Runs the real validator against temporarily tampered ledger files (restored afterwards).
"""
from __future__ import annotations

import copy
import unittest

from common import *  # noqa: F401,F403
import rules as engine
import validate_selection

PILOT = SEL / "ledgers" / "pokemon_icons.json"


class Tamper(unittest.TestCase):
    def setUp(self):
        self.orig = PILOT.read_text()
        self.led = json.loads(self.orig)

    def tearDown(self):
        PILOT.write_text(self.orig)

    def write(self, led):
        PILOT.write_text(json.dumps(led, indent=1, sort_keys=True) + "\n")

    def errs(self):
        return validate_selection.validate()

    def test_clean(self):
        self.assertEqual(self.errs(), [])

    def test_duplicate_decision(self):
        led = copy.deepcopy(self.led)
        led["decisions"].append(copy.deepcopy(led["decisions"][0]))
        self.write(led)
        self.assertTrue(any("duplicate decisions" in e for e in self.errs()))

    def test_two_preferred_same_target(self):
        led = copy.deepcopy(self.led)
        tid = led["decisions"][0]["target_id"]
        for d in led["decisions"]:
            if d["target_id"] == tid:
                d["role"] = "preferred"
        self.write(led)
        self.assertTrue(any("preferred groups" in e for e in self.errs()))

    def test_selected_without_gain(self):
        led = copy.deepcopy(self.led)
        led["decisions"][0]["role"] = "alternate"
        self.write(led)
        e = self.errs()
        self.assertTrue(any("without measured visual gain" in x for x in e))
        self.assertTrue(any("not reproducible" in x for x in e))

    def test_drifted_digest(self):
        led = copy.deepcopy(self.led)
        led["decisions"][0]["asset_identity"]["member_digest"] = "0" * 20
        self.write(led)
        self.assertTrue(any("digest drifted" in e for e in self.errs()))

    def test_missing_group(self):
        led = copy.deepcopy(self.led)
        led["decisions"].pop()
        self.write(led)
        self.assertTrue(any("do not cover" in e for e in self.errs()))


class Rules(unittest.TestCase):
    def test_native_preference_when_no_gain(self):
        rules = jload(RULES_JSON)
        g = {"group_id": "x/hgss/a", "subsystem": "pokemon_icons", "target_id": "t", "source_id": "hgss", "unit": "a", "unit_kind": "species",
             "member_count": 1, "member_digest": "d", "independent_member_count": 1, "asset_type_counts": {}, "reason_code_counts": {},
             "sample_paths": [], "donor_class": "direct", "format_family": "f", "conversion_requirement": "none",
             "unresolved_decode_issue_members": 0, "ledger_member_counts": {"L": 1}}
        subs = jload(SUBSYSTEMS_JSON)["subsystems"]
        for rel, role in (("identical", "not_selected"), ("unmeasured", "reference_only"), ("art_diff_geometry_close", "preferred")):
            d, t = engine.decide([g], {"entries": {"x/hgss/a": {"native_relation": rel}}}, rules, subs)
            self.assertEqual(d[0]["role"], role, rel)
        d, t = engine.decide([g], {"entries": {"x/hgss/a": {"native_relation": "identical"}}}, rules, subs)
        self.assertEqual(t[0]["resolution"], "platinum_native")

    def test_better_source_wins_and_other_is_alternate(self):
        rules = jload(RULES_JSON)
        base = {"subsystem": "pokemon_icons", "target_id": "t", "unit": "a", "unit_kind": "species", "member_count": 1, "member_digest": "d",
                "independent_member_count": 1, "asset_type_counts": {}, "reason_code_counts": {}, "sample_paths": [], "format_family": "f",
                "unresolved_decode_issue_members": 0, "ledger_member_counts": {"L": 1}}
        a = {**base, "group_id": "x/hgss/a", "source_id": "hgss", "donor_class": "direct", "conversion_requirement": "none"}
        b = {**base, "group_id": "x/other/a", "source_id": "pmd_sky", "donor_class": "convertible", "conversion_requirement": "trivial"}
        ev = {"entries": {"x/hgss/a": {"native_relation": "art_diff_geometry_close"}, "x/other/a": {"native_relation": "art_diff_geometry_close"}}}
        d, t = engine.decide([b, a], ev, rules, jload(SUBSYSTEMS_JSON)["subsystems"])
        roles = {x["group_id"]: x["role"] for x in d}
        self.assertEqual(roles, {"x/hgss/a": "preferred", "x/other/a": "alternate"})


if __name__ == "__main__":
    unittest.main()
