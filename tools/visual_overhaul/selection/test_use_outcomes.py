#!/usr/bin/env python3
"""Negative tests for the use-outcome layer (component/composite/technique records). In-memory only; no files are modified."""
from __future__ import annotations

import copy
import unittest

from common import *  # noqa: F401,F403
import build_candidate_groups
import outcomes
import rules as engine

SUB = "trainer_battle_sprites"
_fx = None


def fixture():
    global _fx
    if _fx is None:
        fresh = build_candidate_groups.build(want_membership=True)
        membership = fresh.pop("_membership")
        groups = {g["group_id"]: g for g in jload(GROUPS_JSON)["groups"]}
        ledgers = {p.stem: jload(p) for p in sorted((SEL / "ledgers").glob("*.json"))}
        evidence = {s: jload(ROOT / l["inputs"]["evidence_file"]) for s, l in ledgers.items() if l["inputs"]["evidence_file"]}
        _fx = (groups, membership, ledgers, evidence, jload(outcomes.comp_path(SUB)), load_recovered_records())
    return _fx


class UseRecords(unittest.TestCase):
    def check(self, mutate):
        groups, membership, ledgers, evidence, doc, rec = fixture()
        doc = copy.deepcopy(doc)
        mutate(doc)
        orig = outcomes.load_use_files
        outcomes.load_use_files = lambda: {SUB: doc}
        try:
            return outcomes.validate_use_records(groups, membership, ledgers, evidence, rec)
        finally:
            outcomes.load_use_files = orig

    def has(self, errs, frag):
        self.assertTrue(any(frag in e for e in errs), (frag, errs[:5]))

    def test_committed_records_clean(self):
        self.assertEqual(self.check(lambda d: None), [])

    def test_every_decision_maps_to_an_outcome(self):
        _, _, ledgers, _, _, _ = fixture()
        v = outcomes.vocab()
        for led in ledgers.values():
            for d in led["decisions"]:
                self.assertIn(outcomes.replacement_outcome(d, v), v["outcomes"])

    def test_trainer_verdicts_unchanged_by_outcome_layer(self):
        _, _, ledgers, _, _, _ = fixture()
        v = outcomes.vocab()
        o = {d["group_id"].rsplit("/", 1)[1]: outcomes.replacement_outcome(d, v) for d in ledgers[SUB]["decisions"] if d["group_id"].startswith(f"{SUB}/hgss/hgss_front_")}
        for k in ("002", "003", "006", "008", "036", "043"):
            self.assertEqual(o[f"hgss_front_{k}"], "direct_replacement")
        for k in ("024", "025", "101", "122"):
            self.assertEqual(o[f"hgss_front_{k}"], "native_keep")

    def test_ace_candidates_are_components_not_replacements(self):
        doc = fixture()[4]
        self.assertEqual({r["outcome"] for r in doc["records"]}, {"component_donor"})
        self.assertTrue(all(r["status"] == "proposed" for r in doc["records"]))

    def test_provenance_cannot_be_dropped(self):
        for f in ("assets", "member_digest", "group_id"):
            def m(d, f=f):
                d["records"][0]["source"].pop(f)
            self.has(self.check(m), "provenance cannot be lost")

    def test_required_fields(self):
        for f in ("constraints", "adaptation", "tags", "reason", "evidence", "confidence", "component"):
            def m(d, f=f):
                d["records"][0].pop(f)
            self.has(self.check(m), f"missing required field {f}")

    def test_unknown_tag_rejected(self):
        self.has(self.check(lambda d: d["records"][0].__setitem__("tags", ["vibes"])), "tags must be")

    def test_source_asset_must_be_group_member(self):
        def m(d):
            d["records"][0]["source"]["assets"][0]["asset_id"] = "hgss:narc:files:a:0:5:8:front_025"
        self.has(self.check(m), "is not a member of")

    def test_source_asset_must_be_curated_usable(self):
        def m(d):
            d["records"][0]["source"]["assets"][0]["asset_id"] = "hgss:does:not:exist"
        self.has(self.check(m), "is not a member of")

    def test_stale_member_digest(self):
        self.has(self.check(lambda d: d["records"][0]["source"].__setitem__("member_digest", "0" * 20)), "stale")

    def test_evidence_digest_binding(self):
        self.has(self.check(lambda d: d["records"][0]["evidence"].__setitem__("evidence_entry_digest", "0" * 16)), "evidence_entry_digest stale")

    def test_native_ref_hash_binding(self):
        self.has(self.check(lambda d: d["records"][0]["target"]["native_ref"].__setitem__("sha256", "0" * 16)), "native_ref hash")

    def test_replacement_outcomes_are_never_recorded(self):
        self.has(self.check(lambda d: d["records"][0].__setitem__("outcome", "direct_replacement")), "not a contribution outcome")

    def test_technique_reference_carries_no_pixels(self):
        def m(d):
            d["records"][0]["outcome"] = "technique_reference"
        self.has(self.check(m), "pixel_use none")

    def test_component_use_must_declare_pixel_use(self):
        self.has(self.check(lambda d: d["records"][0].__setitem__("pixel_use", "none")), "must declare how donor pixels")

    def test_component_on_preferred_group_rejected(self):
        groups, _, _, _, _, _ = fixture()
        g = groups[f"{SUB}/hgss/hgss_front_002"]
        def m(d):
            d["records"][0]["source"]["group_id"] = g["group_id"]
        errs = self.check(m)
        self.has(errs, "stay distinct")

    def test_human_confirmation_is_digest_bound(self):
        def confirm(d):
            r = d["records"][0]
            r["status"] = "human_confirmed"
            r["human_review"] = {"verdict": "confirm", "reviewer": "owner", "reviewed_at": "2026-10-07", "member_digest": r["source"]["member_digest"],
                                 "evidence_digest": r["evidence"]["evidence_entry_digest"], "record_digest": outcomes.record_digest(r)}
        self.assertEqual(self.check(confirm), [])
        def edited(d):
            confirm(d)
            d["records"][0]["reason"] += " (edited after confirmation)"
        self.has(self.check(edited), "record content changed")
        def stale_ev(d):
            confirm(d)
            d["records"][0]["human_review"]["evidence_digest"] = "0" * 16
        self.has(self.check(stale_ev), "evidence changed")
        def stale_grp(d):
            confirm(d)
            d["records"][0]["human_review"]["member_digest"] = "0" * 20
        self.has(self.check(stale_grp), "member digest changed")
        def bare(d):
            d["records"][0]["status"] = "human_confirmed"
        self.has(self.check(bare), "without a confirm verdict")

    def _plan(self, d, status="design_pending", inputs=None, target="ace_trainer_male"):
        for r in d["records"]:
            if r["target"]["target_id"].endswith(target):
                r["outcome"] = "composite_input"
        nat = d["records"][0]["target"]["native_ref"]
        ids = inputs if inputs is not None else [r["record_id"] for r in d["records"] if r["target"]["target_id"].endswith(target)]
        d["composites"] = [{"composite_id": "cp1", "target_id": f"{SUB}/tc_{target}", "status": status, "native_base": nat, "inputs": ids, "technique_refs": []}]

    def test_valid_composite_plan(self):
        def m(d):
            self._plan(d)
            d["records"] = [r for r in d["records"] if r["target"]["target_id"].endswith("ace_trainer_male")]
            d["component_reviews"] = [c for c in d["component_reviews"] if c["group_id"].endswith("024")]
        self.assertEqual(self.check(m), [])

    def test_composite_input_must_exist(self):
        def m(d):
            self._plan(d, inputs=["uc:nope"])
        self.has(self.check(m), "missing/uncurated")

    def test_composite_input_must_be_composite_input_outcome(self):
        def m(d):
            self._plan(d)
            d["records"][0]["outcome"] = "component_donor"
        self.has(self.check(m), "must be an active composite_input")

    def test_ready_composite_requires_confirmed_inputs(self):
        def m(d):
            self._plan(d, status="ready")
        self.has(self.check(m), "unconfirmed input")

    def test_orphan_composite_input(self):
        def m(d):
            d["records"][0]["outcome"] = "composite_input"
        self.has(self.check(m), "not referenced by any composite plan")

    def test_composite_cannot_target_a_replaced_asset(self):
        groups, _, ledgers, _, _, _ = fixture()
        def m(d):
            self._plan(d)
            d["composites"][0]["target_id"] = f"{SUB}/tc_youngster"
        self.has(self.check(m), "exclusive")

    def test_composite_native_base_hash(self):
        def m(d):
            self._plan(d)
            d["composites"][0]["native_base"] = {**d["composites"][0]["native_base"], "sha256": "0" * 16}
        self.has(self.check(m), "native_base missing or hash mismatch")

    def test_none_found_review_conflicts_with_active_records(self):
        def m(d):
            for c in d["component_reviews"]:
                if c["group_id"].endswith("024"):
                    c["finding"] = "none_found"
        self.has(self.check(m), "none_found but active component records")

    def test_review_digest_binding(self):
        def m(d):
            d["component_reviews"][0]["evidence_digest"] = "0" * 16
        self.has(self.check(m), "stale (evidence changed)")


class Derivation(unittest.TestCase):
    def test_role_map_is_total_and_exact(self):
        v = outcomes.vocab()
        base = {"needs_evidence": False}
        self.assertEqual(outcomes.replacement_outcome({**base, "role": "preferred", "reason_code": "human_approved"}, v), "direct_replacement")
        self.assertEqual(outcomes.replacement_outcome({**base, "role": "not_selected", "reason_code": "human_keep_platinum"}, v), "native_keep")
        self.assertEqual(outcomes.replacement_outcome({**base, "role": "reference_only", "reason_code": "policy_reference_class"}, v), "technique_reference")
        self.assertEqual(outcomes.replacement_outcome({"needs_evidence": True, "role": "reference_only", "reason_code": "needs_evidence"}, v), "needs_evidence")
        with self.assertRaises(KeyError):
            outcomes.replacement_outcome({**base, "role": "reference_only", "reason_code": "brand_new_reason"}, v)


if __name__ == "__main__":
    unittest.main()
