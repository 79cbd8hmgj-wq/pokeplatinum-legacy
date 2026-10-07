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
M = "opp:hgss/map_location_preview"
T = "opp:ranger2/effect_sequencing"
N = "opp:pmd_sky/battler_status_indicators"
A = "opp:trainer/tc_ace_trainer_male/enhancement"
expect("unknown class", lambda d: find(d, T).update(classification="whole_replace"), "unknown classification")
expect("technique with pixels", lambda d: find(d, T).update(pixel_use="derived"), "pixel_use none")
expect("technique not asset_use techniques", lambda d: find(d, T).update(asset_use="components"), "asset_use techniques")
expect("technique without target", lambda d: find(d, T).update(target={"kind": "none", "host_system": "x"}), "requires an intended Platinum target")
expect("novel without host", lambda d: find(d, N)["target"].pop("host_system"), "host_system")
expect("missing provenance", lambda d: find(d, N)["donor"].update(locator=""), "donor.locator")
expect("missing constraints", lambda d: find(d, N).update(constraints=[]), "missing required field constraints")
expect("stale catalog binding", lambda d: find(d, M)["evidence"].update(bound_digest="0" * 20), "stale")
expect("dangling system ref", lambda d: find(d, T)["target"].update(refs=["src/does_not_exist.c"]), "does not exist")
expect("bad asset hash", lambda d: find(d, A)["target"]["native_ref"].update(sha256="deadbeef"), "native_ref")
expect("enhancement without links", lambda d: find(d, A).pop("links"), "must link")
expect("enhancement link to other target", lambda d: find(d, A)["links"].update(use_records=[r["record_id"] for r in use["trainer_battle_sprites"]["records"] if "female" in r["record_id"]][:1]), "different target")
expect("replacement without donor pixels", lambda d: find(d, "opp:ranger2/effect_primitives").update(classification="replacement_candidate"), "donor_pixels")
expect("duplicate id", lambda d: d["findings"].append(copy.deepcopy(d["findings"][0])), "duplicate finding_id")
# phase scope (DS-only)
expect("GBA donor in active set", lambda d: find(d, N)["donor"].update(game="firered", source_id="firered"), "outside the active DS-only phase")
expect("deferred game named as donor", lambda d: find(d, N)["donor"].update(game="pmd_red (via pmd_sky)"), "outside the active DS-only phase")
expect("platinum as donor", lambda d: find(d, N)["donor"].update(source_id="platinum"), "outside the active DS-only phase")
expect("missing scores", lambda d: find(d, N).pop("scores"), "scores must carry")
expect("score out of range", lambda d: find(d, N)["scores"].update(novelty=9), "scores must carry")
expect("feasibility mismatch", lambda d: find(d, N).update(feasibility=1), "disagrees")
expect("reference_only ranked", lambda d: find(d, "opp:hgss/camera_viewfinder").update(scores=dict(find(d, N)["scores"])), "never ranked")
expect("bad asset_use", lambda d: find(d, N).update(asset_use="everything"), "asset_use must be")
expect("checkout verification without entries", lambda d: find(d, N)["donor"].pop("verification"), "needs donor.verification")
expect("verification bad commit", lambda d: find(d, N)["donor"]["verification"][0].update(commit="abc"), "40-hex")
# deferred preservation
dd = opp.load_deferred()
assert len(dd["findings"]) == 9 and all(f["phase"] == "deferred_gba_gbc" for f in dd["findings"])
assert not ({f["finding_id"] for f in dd["findings"]} & {f["finding_id"] for f in BASE["findings"]})
print("ok   9 GBA/GBC findings preserved in the deferred file, none active")
opp.load_findings = lambda: BASE
reg0 = opp.derive_register(ledgers, use)
assert reg0["deferred_non_ds_findings"] == 9
assert not any(r["source_id"] in ("firered", "emerald", "pmd_red", "crystal", "yellow") for r in reg0["rows"]), "non-DS row leaked into register"
print("ok   deferred findings absent from the register")
sc = [r["rank_score"] for r in reg0["rows"] if r["rank_score"] is not None]
assert sc == sorted(sc, reverse=True) and M in [r["id"] for r in reg0["rows"][:5]], [r["id"] for r in reg0["rows"][:5]]  # map preview stays a top-5 finding (evidence closure added higher-scored libraries)
assert all(r["rank_score"] is None for r in reg0["rows"] if r["classification"] in ("reference_only", "reject"))
print("ok   register ranked by weighted score; reference_only/reject unranked; map preview in the top 5")
q = jload(SEL / "IMPLEMENTATION_QUEUE.json")
assert q["phase"] == "ds_only" and all(i["source_id"].split(",")[0] in ("hgss", "pmd_sky", "ranger2") for i in q["ranked"])
print("ok   queue is DS-only and ranked")
opp.load_findings = lambda: BASE
reg = opp.derive_register(ledgers, use)
assert reg["counts_by_class"] == {"novel_capability": 2, "novel_detail": 2, "technique_donor": 1, "enhancement_candidate": 2, "component_donor": 7, "replacement_candidate": 32, "reference_only": 9, "reject": 3}, reg["counts_by_class"]
print("ok   register counts by class")
sys.exit(1 if fails else 0)
