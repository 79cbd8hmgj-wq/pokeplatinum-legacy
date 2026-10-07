#!/usr/bin/env python3
"""Negative tests for the opportunity layer: each mutation of a valid findings file must be rejected."""
from __future__ import annotations

import copy
import sys

from common import *  # noqa: F401,F403
import opportunities as opp
import outcomes

groups = {g["group_id"]: g for g in jload(GROUPS_JSON)["groups"]}
ledgers = {p.stem: jload(p) for p in sorted((SEL / "ledgers").glob("*.json"))}
evidence = {s: jload(ROOT / l["inputs"]["evidence_file"]) for s, l in ledgers.items() if l["inputs"]["evidence_file"] and (ROOT / l["inputs"]["evidence_file"]).is_file()}
use = outcomes.load_use_files()
BASE = copy.deepcopy(opp.load_findings())
fails = 0


def run(doc):
    opp.load_findings = lambda: doc
    return opp.validate_findings(groups, ledgers, evidence, use)


def find(doc, fid):
    return next(f for f in doc["findings"] if f["finding_id"] == fid)


def expect(name, mutate, needle):
    global fails
    doc = copy.deepcopy(BASE)
    mutate(doc)
    errs = run(doc)
    if not any(needle in e for e in errs):
        print(f"FAIL {name}: expected '{needle}', got {errs[:3]}")
        fails += 1
    else:
        print(f"ok   {name}")


assert run(copy.deepcopy(BASE)) == [], run(copy.deepcopy(BASE))
print("ok   baseline valid")
cl = opp.taxonomy()["classes"]
assert list(cl) == ["novel_capability", "novel_detail", "technique_donor", "component_donor", "enhancement_candidate", "replacement_candidate", "reference_only", "reject"] or set(cl) == {"novel_capability", "novel_detail", "technique_donor", "component_donor", "enhancement_candidate", "replacement_candidate", "reference_only", "reject"}
print("ok   eight canonical classes")
expect("unknown class", lambda d: find(d, "opp:emerald/field_action_choreography").update(classification="whole_replace"), "unknown classification")
expect("technique with pixels", lambda d: find(d, "opp:emerald/field_action_choreography").update(pixel_use="derived"), "pixel_use none")
expect("technique without target", lambda d: find(d, "opp:emerald/field_action_choreography").update(target={"kind": "none", "host_system": "x"}), "requires an intended Platinum target")
expect("novel without host", lambda d: find(d, "opp:pmd_red/battler_status_overlays")["target"].pop("host_system"), "host_system")
expect("missing provenance", lambda d: find(d, "opp:pmd_red/battler_status_overlays")["donor"].update(locator=""), "donor.locator")
expect("missing constraints", lambda d: find(d, "opp:pmd_red/battler_status_overlays").update(constraints=[]), "missing required field constraints")
expect("unrecorded evidence high confidence", lambda d: find(d, "opp:pmd_red/battler_status_overlays").update(confidence="high"), "capped at confidence low")
expect("unrecorded evidence confirmed", lambda d: find(d, "opp:pmd_red/battler_status_overlays").update(status="human_confirmed"), "cannot be human_confirmed")
expect("stale catalog binding", lambda d: find(d, "opp:firered/map_location_preview")["evidence"].update(bound_digest="0" * 20), "stale")
expect("dangling system ref", lambda d: find(d, "opp:emerald/field_action_choreography")["target"].update(refs=["src/does_not_exist.c"]), "does not exist")
expect("bad asset hash", lambda d: find(d, "opp:trainer/tc_ace_trainer_male/enhancement")["target"]["native_ref"].update(sha256="deadbeef"), "native_ref")
expect("enhancement without links", lambda d: find(d, "opp:trainer/tc_ace_trainer_male/enhancement").pop("links"), "must link")
expect("enhancement link to other target", lambda d: find(d, "opp:trainer/tc_ace_trainer_male/enhancement")["links"].update(use_records=[r["record_id"] for r in use["trainer_battle_sprites"]["records"] if "female" in r["record_id"]][:1]), "different target")
expect("replacement without donor pixels", lambda d: find(d, "opp:crystal/battle_anim_artwork").update(classification="replacement_candidate"), "donor_pixels")
expect("duplicate id", lambda d: d["findings"].append(copy.deepcopy(d["findings"][0])), "duplicate finding_id")
opp.load_findings = lambda: BASE
reg = opp.derive_register(ledgers, use)
assert reg["counts_by_class"]["reject"] == 2 and reg["counts_by_class"]["replacement_candidate"] == 32, reg["counts_by_class"]
print("ok   register counts (reject=2 none_found reviews, replacement=32 preferred)")
sys.exit(1 if fails else 0)
