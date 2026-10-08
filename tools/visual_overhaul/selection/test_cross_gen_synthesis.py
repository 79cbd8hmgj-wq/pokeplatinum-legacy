#!/usr/bin/env python3
"""Invariants of the frozen GBA/GBC pool and the cross-generation ranking (B7). Fails closed; reads committed artifacts only."""
from __future__ import annotations

import collections

from common import *  # noqa: F401,F403
import opportunities as opp
import validate_gba_gbc_pool as V

OUT = jload(SEL / "CROSS_GEN_OPPORTUNITY_RANKING.json")
fails = 0


def check(name: str, ok: bool) -> None:
    global fails
    print(("ok   " if ok else "FAIL ") + name)
    fails += 0 if ok else 1


check("GBA/GBC pool validates", V.validate() == [])
w = opp.taxonomy()["ranking"]["weights"]
check("ranking uses the canonical weights", OUT["method"]["weights"] == w)
R = OUT["ranked"]
check("ranks are 1..N by descending score", [x["rank"] for x in R] == list(range(1, len(R) + 1)) and all(a["canonical_score"] >= b["canonical_score"] for a, b in zip(R, R[1:])))
check("only rankable classes are ranked", all(x["class"] not in ("reference_only", "reject") for x in R))
ref_ids = {r["id"] for r in OUT["reference_only_register"]}
scored = {i["id"] for x in R for d in x["donors"] for i in d["items"]}
check("reference_only/reject never appear among scored members", not (ref_ids & scored))
check("corroboration never affects score", all(c["affects_score"] is False for x in R for c in x["corroboration"]))
ds = sum(x["ds_queue_items"] for x in R) + sum(len(g["ds_queue_items"]) for g in OUT["gated_excluded"])
check("all 94 DS queue items accounted for exactly once", ds == 94 == OUT["counts"]["ds_queue_items"])
check("every ranked item keeps donor identity", all(x["donors"] and all(d["source_id"] and d["items"] for d in x["donors"]) for x in R))
check("exec order is a permutation", sorted(x["execution_order"] for x in R) == list(range(1, len(R) + 1)))
check("GBA/GBC corroboration does not add a ranked record", OUT["counts"]["gba_gbc_new_ranked_opportunities"] == 0)
check("replacement_candidate is neither immediate nor in the top 10", all(x["bucket"] == "later" and x["rank"] > 10 for x in R if x["class"] == "replacement_candidate"))
check("first slice is an immediate candidate", next(x for x in R if x["io_id"] == OUT["first_slice"]["io_id"])["bucket"] == "immediate")
check("angels motif and Ruby stay deferred and unranked", {g["id"] for g in OUT["evidence_gaps"]} >= {"ne:crystal/angels_motif_vs_platinum", "defer:ruby/semantic_delta"} and "opp:crystal/battle_anim_artwork/angels_motif" not in scored | {c["id"] for x in R for c in x["corroboration"]})
raise SystemExit(1 if fails else 0)
