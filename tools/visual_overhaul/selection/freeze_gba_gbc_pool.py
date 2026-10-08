#!/usr/bin/env python3
"""B7 freeze of the GBA/GBC donor layer (idempotent; edits only GBA_GBC_OPPORTUNITY_POOL.json and GBA_GBC_NEEDS_EVIDENCE.json).

* records the frozen donor status (Ruby skipped, Crystal angels deferred by project decision);
* normalises the two PMD Red records that used non-canonical target kinds / free-text cost fields so they obey
  OPPORTUNITY_CLASSES.json (target kind none|system, cost/risk low|medium|high);
* marks the cross-generation merge targets (no DS file is touched).
Run validate_gba_gbc_pool.py afterwards.
"""
from __future__ import annotations

from common import *  # noqa: F401,F403
import validate_gba_gbc_pool as V

PARENT = "opp:pmd_red/battler_status_overlays"
CYCLE = "opp:pmd_red/battler_status_overlays/multi_status_cycling"

DONOR_STATUS = {
    "emerald": {"status": "complete", "records": "3 reference_only", "needs_evidence": 0},
    "firered": {"status": "complete", "records": "4 reference_only", "needs_evidence": 0},
    "pmd_red": {"status": "complete", "records": "1 novel_detail, 1 technique_donor (conditional), 1 reference_only", "needs_evidence": 0},
    "crystal": {"status": "reviewed", "records": "3 reference_only, 1 reject, 1 needs_evidence", "needs_evidence": 1,
                "note": "angels motif (ne:crystal/angels_motif_vs_platinum) explicitly deferred, non-blocking, excluded from ranking"},
    "yellow": {"status": "complete", "records": "3 reference_only, 1 reject", "needs_evidence": 0},
    "ruby": {"status": "skipped", "records": "none (not mined)", "needs_evidence": 0,
             "note": "B5 Ruby semantic delta skipped by project decision; not an evidence gap"},
}


def main() -> int:
    pool = jload(V.POOL)
    ne = jload(V.NE)
    R = {r["finding_id"]: r for r in pool["records"]}

    pool["note"] = ("Frozen GBA/GBC pool (B7). Separate from the DS pool (selection/OPPORTUNITY_POOL.json is untouched). "
                    "Cross-generation ranking and merge decisions live in CROSS_GEN_OPPORTUNITY_RANKING.json; this file keeps per-donor provenance.")
    pool["frozen"] = True
    pool["frozen_in"] = "B7_cross_generation_merge"
    pool["donor_status"] = DONOR_STATUS
    pool["batches_skipped"] = [
        {"batch": "B4_5_crystal_angels_evidence_closure", "reason": "project decision: deferred, non-blocking", "item": "ne:crystal/angels_motif_vs_platinum"},
        {"batch": "B5_ruby_semantic_delta", "reason": "project decision: Ruby skipped/deferred", "item": None},
    ]

    p = R[PARENT]
    p["target"] = {"kind": "none", "host_system": p["target"]["host_system"]}
    p["cost"], p["feasibility"] = "medium", 2
    p.setdefault("risk_note", p["risk"])
    p["risk"] = "medium"
    p["merge"] = {"into": "opp:pmd_sky/battler_status_indicators", "role": "corroborates_and_strengthens",
                  "note": "Same concept as the DS PMD Sky status-icon record (battler-local, mask-driven status indicator). PMD Red adds traced behaviour and the Platinum comparison; it is not a second opportunity."}

    c = R[CYCLE]
    c["target"] = {"kind": "system", "system": "battle status-overlay layer (depends on the parent record)", "host_system": c["target"]["host_system"],
                   "refs": ["src/battle/healthbox.c", "src/battle/battle_lib.c"]}
    c["cost"], c["feasibility"] = "low", 2
    c.setdefault("risk_note", c["risk"])
    c["risk"] = "low"
    c["merge"] = {"into": "opp:pmd_sky/battler_status_indicators", "role": "conditional_sub_technique", "note": "Not ranked separately; rides the merged status-overlay opportunity."}

    f = R["opp:firered/map_location_preview"]
    f["merge"] = {"into": "opp:hgss/map_location_preview", "role": "corroborates", "note": f.get("subsumed_by", "subsumed by the HGSS area-preview concept")}

    pal = R["opp:firered/animated_palette_sequences"]
    pal["merge"] = {"into": "cross-gen IO palette-cycle service (DS libraries pmd_mapbg_*)", "role": "corroborates_timing_shape_only",
                    "note": "reference_only: Platinum has native equivalents; FireRed only adds timing shape to the PMD Sky technique."}

    a = R["opp:crystal/battle_anim_artwork/angels_motif"]
    a["deferral"] = {"state": "deferred_non_blocking", "decided": "B7 final synthesis (project decision)", "ranked": False,
                     "rule_when_reopened": "see GBA_GBC_NEEDS_EVIDENCE.json disposition_rule"}

    for it in ne["items"]:
        if it["item_id"] == "ne:crystal/angels_motif_vs_platinum":
            it["status"] = "deferred_non_blocking"
            it["decision"] = "Closure (B4.5) skipped by project decision at B7; not resolved, not blocking, excluded from ranking."
    ne["frozen"] = True
    ne["note"] = "GBA/GBC needs-evidence items (frozen at B7). Narrow: each names the single piece of missing evidence and the disposition rule once it is supplied."
    ids = {d["item_id"] for d in ne["deferred_not_blocking"]}
    if "defer:ruby/semantic_delta" not in ids:
        ne["deferred_not_blocking"].append({
            "item_id": "defer:ruby/semantic_delta", "raised_in": "B7_cross_generation_merge", "finding_id": None,
            "what": "Ruby semantic delta against Emerald (B5) was not run.",
            "why_not_blocking": "Project decision. Ruby is Emerald's predecessor on the same engine; Emerald is closed with 0 promoted records, so no ranked opportunity depends on it.",
            "disposition_rule": "If reopened, reuse evidence/B1_EMERALD_SYMBOL_EVIDENCE.json and evidence/B1_5_PLATINUM_FLDEFF_MEMBER_NAMES.json; any Ruby-only effect matching a Platinum member already named there is reference_only."})
    jdump_pretty(V.POOL, pool)
    jdump_pretty(V.NE, ne)
    return 0


def jdump_pretty(path, obj) -> None:
    import json
    path.write_text(json.dumps(obj, indent=1) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
