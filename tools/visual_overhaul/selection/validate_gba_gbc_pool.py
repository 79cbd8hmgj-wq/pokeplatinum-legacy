#!/usr/bin/env python3
"""Read-only validation of the frozen GBA/GBC pool (GBA_GBC_OPPORTUNITY_POOL.json + GBA_GBC_NEEDS_EVIDENCE.json).

Checks: duplicate ids, provenance (pinned commit, verification facts, existing evidence refs), canonical taxonomy
(class / target / pixel_use policy from OPPORTUNITY_CLASSES.json), replacement_candidate usage, reference_only/reject
isolation from ranking, needs-evidence bookkeeping. Returns a list of error strings (empty = valid).
"""
from __future__ import annotations

import collections

from common import *  # noqa: F401,F403
import opportunities as opp

GBA_DIR = SEL / "gba_gbc"
POOL = GBA_DIR / "GBA_GBC_OPPORTUNITY_POOL.json"
NE = GBA_DIR / "GBA_GBC_NEEDS_EVIDENCE.json"
TARGET_KINDS = {"asset", "none", "system"}  # OPPORTUNITY_CLASSES.json target_kinds
RANKABLE = {"novel_capability", "novel_detail", "technique_donor", "enhancement_candidate", "component_donor", "replacement_candidate"}


def validate() -> list[str]:
    errs: list[str] = []
    tx = opp.taxonomy()
    classes = tx["classes"]
    pool = jload(POOL)
    ne = jload(NE)
    ids = [r["finding_id"] for r in pool["records"]]
    for fid, n in collections.Counter(ids).items():
        if n > 1:
            errs.append(f"duplicate finding_id {fid}")
    ds_ids = {f["finding_id"] for f in opp.load_findings()["findings"]}
    for fid in set(ids) & ds_ids:
        errs.append(f"{fid}: id collides with a DS finding")
    pinned = pool["pinned_donors"]
    open_ne = {i["item_id"] for i in ne["items"]}
    for r in pool["records"]:
        t = r["finding_id"]
        cl = r["classification"]
        disp = r["disposition"]
        d = r["donor"]
        if d["source_id"] not in pinned or d["commit"] != pinned[d["source_id"]]:
            errs.append(f"{t}: donor commit is not the pinned commit for {d['source_id']}")
        if not d.get("verification"):
            errs.append(f"{t}: no donor verification facts")
        for ref in r["evidence"]["refs"]:
            if not (ROOT / ref).is_file():
                errs.append(f"{t}: evidence ref missing: {ref}")
        if cl is None:
            if disp != "needs_evidence" or r.get("needs_evidence_item") not in open_ne:
                errs.append(f"{t}: unclassified record must be disposition needs_evidence with an open needs-evidence item")
            continue
        if cl not in classes:
            errs.append(f"{t}: unknown class {cl}")
            continue
        if disp != cl:
            errs.append(f"{t}: disposition {disp} != classification {cl}")
        c = classes[cl]
        kind = r["target"]["kind"]
        if kind not in TARGET_KINDS:
            errs.append(f"{t}: non-canonical target kind {kind!r}")
        if c["target_policy"] == "none_allowed" and kind not in ("none",):
            if cl in ("reference_only", "reject", "novel_capability", "novel_detail"):
                errs.append(f"{t}: {cl} must not name an existing Platinum target (kind={kind})")
        if c["target_policy"] == "target_required" and kind == "none":
            errs.append(f"{t}: {cl} requires a Platinum target")
        if kind == "none" and cl in ("novel_capability", "novel_detail") and not r["target"].get("host_system"):
            errs.append(f"{t}: {cl} with target none must name host_system")
        if c["pixel_policy"] == "none" and r["pixel_use"] != "none":
            errs.append(f"{t}: {cl} must have pixel_use none")
        if cl == "replacement_candidate":
            errs.append(f"{t}: replacement_candidate in the GBA/GBC pool (not expected)")
        if cl in RANKABLE:
            for k in ("cost", "risk", "confidence", "feasibility", "adaptation", "constraints"):
                if r.get(k) in (None, [], ""):
                    errs.append(f"{t}: rankable record missing {k}")
    for it in ne["items"]:
        if it["finding_id"] not in ids:
            errs.append(f"{it['item_id']}: finding {it['finding_id']} not in pool")
    return errs


def counts() -> dict:
    pool = jload(POOL)
    c = collections.Counter((r["classification"] or "needs_evidence") for r in pool["records"])
    return dict(sorted(c.items()))


if __name__ == "__main__":
    e = validate()
    print(counts())
    for x in e:
        print("ERR", x)
    raise SystemExit(1 if e else 0)
