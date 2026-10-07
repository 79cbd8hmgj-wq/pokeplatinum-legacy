#!/usr/bin/env python3
"""Prioritized implementation queue from completed subsystem ledgers (plus open evidence work).

Only subsystems with a ledger participate. Queue items:
  implement  - a preferred donor group (one item per subsystem+source batch), ranked by value/cost
  evidence   - reference_only(needs_evidence) groups whose gain could flip them into selection
  runtime_qa - preferred/alternate groups flagged needs_runtime_validation
Every item carries a `work_lane` (USE_OUTCOMES.json work_lanes):
  A direct_replacement  - whole-asset donor replacement (implement, runtime_qa)
  B native_enhancement  - new Platinum-native asset from Platinum + donor components (component_review, composite_build, component_pool)
  C technique_only      - technique/timing/layout re-implemented with no donor pixels (technique_build, technique_pool)
  evidence              - open evidence work that could change a whole-asset verdict
Selection v3: every item also carries an `opportunity_class` (OPPORTUNITY_CLASSES.json), `tier` and `feasibility`;
items are ranked by opportunity type (novel capability/detail > technique > enhancement > component > replacement), then
feasibility, then score. Explicit opportunity findings (opportunities/findings.json) enter as `opportunity` items.
Pending subsystems (no ledger yet) are listed so the queue is visibly incomplete, not silently short.
"""
from __future__ import annotations

import argparse
import collections
import sys

from common import *  # noqa: F401,F403
import opportunities as opp
import outcomes


def derive() -> dict:
    subs = jload(SUBSYSTEMS_JSON)["subsystems"]
    gdoc = jload(GROUPS_JSON)
    done, pending = [], []
    implement: dict[tuple, dict] = {}
    evidence: dict[tuple, dict] = {}
    runtime: dict[tuple, dict] = {}
    for name in sorted(subs):
        lp = SEL / "ledgers" / f"{name}.json"
        if not lp.is_file():
            n = sum(1 for g in gdoc["groups"] if g["subsystem"] == name)
            pending.append({"subsystem": name, "groups": n})
            continue
        led = jload(lp)
        done.append(name)
        w = subs[name]["priority_weight"]
        for d in led["decisions"]:
            key = (name, d["source_id"])
            if d["role"] == "preferred":
                it = implement.setdefault(key, {"kind": "implement", "subsystem": name, "source_id": d["source_id"], "targets": [], "gain_sum": 0, "cost": d["scores"]["integration_cost"], "formats": set()})
                it["targets"].append(d["target_id"])
                it["gain_sum"] += d["scores"]["visual_gain"]
                it["formats"].add(d["format_family"])
            if d["role"] == "preferred" and d["needs_runtime_validation"]:
                it = runtime.setdefault(key, {"kind": "runtime_qa", "subsystem": name, "source_id": d["source_id"], "groups": 0})
                it["groups"] += 1
            if d["needs_evidence"]:
                it = evidence.setdefault(key, {"kind": "evidence", "subsystem": name, "source_id": d["source_id"], "groups": 0, "members": 0, "targets": []})
                it["groups"] += 1
                it["members"] += d["asset_identity"]["member_count"]
                it["targets"].append(d["target_id"])
    items = []
    for it in implement.values():
        w = subs[it["subsystem"]]["priority_weight"]
        items.append({
            "kind": "implement", "subsystem": it["subsystem"], "source_id": it["source_id"],
            "target_count": len(it["targets"]), "targets_sample": sorted(it["targets"])[:5],
            "format_families": sorted(it["formats"]), "integration_cost": it["cost"],
            "priority_score": round(it["gain_sum"] * w / max(it["cost"], 1), 3),
        })
    for it in evidence.values():
        items.append({**it, "targets": None, "target_count": len(it["targets"]), "targets_sample": sorted(it["targets"])[:5],
                      "priority_score": round(0.1 * subs[it["subsystem"]]["priority_weight"], 3)})
    for it in runtime.values():
        items.append({**it, "priority_score": 0.0})
    for it in items:
        it["work_lane"] = {"implement": "direct_replacement", "runtime_qa": "direct_replacement"}.get(it["kind"], "evidence")
    vocab = outcomes.vocab()
    use_files = outcomes.load_use_files()
    for sname, doc in sorted(use_files.items()):
        w = subs[sname]["priority_weight"]
        cost = max(subs[sname]["integration_cost"], 1)
        recs = [r for r in doc.get("records", []) if outcomes.active(r)]
        comp = [r for r in recs if r["outcome"] in ("component_donor", "composite_input")]
        if comp:
            pend = [r for r in comp if r["status"] != "human_confirmed"]
            items.append({"kind": "component_review", "work_lane": "native_enhancement", "subsystem": sname, "source_id": ",".join(sorted({r["source"]["source_id"] for r in comp})),
                          "target_count": len({r["target"]["target_id"] for r in comp}), "targets_sample": sorted({r["target"]["target_id"] for r in comp})[:5],
                          "records": len(comp), "awaiting_human_confirmation": len(pend), "tags": sorted({t for r in comp for t in r["tags"]}),
                          "priority_score": round(0.25 * len(comp) * w / cost, 3)})
        for cp in doc.get("composites", []):
            if cp["status"] == "ready":
                items.append({"kind": "composite_build", "work_lane": "native_enhancement", "subsystem": sname, "source_id": "composite", "target_count": 1,
                              "targets_sample": [cp["target_id"]], "composite_id": cp["composite_id"], "priority_score": round(1.0 * w / cost, 3)})
        tech = [r for r in recs if r["outcome"] == "technique_reference"]
        if tech:
            items.append({"kind": "technique_build", "work_lane": "technique_only", "subsystem": sname, "source_id": ",".join(sorted({r["source"]["source_id"] for r in tech})),
                          "target_count": len({r["target"]["target_id"] for r in tech}), "targets_sample": sorted({r["target"]["target_id"] for r in tech})[:5],
                          "records": len(tech), "priority_score": round(0.25 * len(tech) * w / cost, 3)})
    pool: dict[tuple, int] = collections.Counter()
    cpool: dict[tuple, int] = collections.Counter()
    for name in done:
        led = jload(SEL / "ledgers" / f"{name}.json")
        for d in led["decisions"]:
            if outcomes.replacement_outcome(d, vocab) == "technique_reference":
                pool[(name, d["source_id"])] += 1
            elif d["role"] == "reference_only" and d["reason_code"] == "no_native_target":
                cpool[(name, d["source_id"])] += 1
    cov = {c for f in opp.load_findings()["findings"] if opp.active(f) for c in f.get("covers_pools", [])}
    for (name, src), n in sorted(cpool.items()):
        if src == "diamond" or f"{name}/{src}" in cov:
            continue
        items.append({"kind": "component_pool", "work_lane": "native_enhancement", "subsystem": name, "source_id": src, "groups": n, "target_count": None,
                      "priority_score": round(0.05 * subs[name]["priority_weight"], 3),
                      "note": "donor groups with no Platinum counterpart (no whole-asset replacement possible); candidates for component/composite use once Platinum targets are scoped"})
    for (name, src), n in sorted(pool.items()):
        if src == "diamond" or f"{name}/{src}" in cov:
            continue
        items.append({"kind": "technique_pool", "work_lane": "technique_only", "subsystem": name, "source_id": src, "groups": n, "target_count": None,
                      "priority_score": round(0.05 * subs[name]["priority_weight"], 3),
                      "note": "technique-class groups without explicit technique_reference records; scope a target + technique before any implementation"})
    tx = opp.taxonomy()
    tier = {k: v["tier"] for k, v in tx["classes"].items()}
    ds = set(opp.scope()["ds_sources"])
    cls_of = {"implement": "replacement_candidate", "runtime_qa": "replacement_candidate", "component_review": "enhancement_candidate", "composite_build": "enhancement_candidate",
              "technique_build": "technique_donor", "component_pool": "component_donor", "technique_pool": "technique_donor", "evidence": None}
    reg = opp.derive_register({n: jload(SEL / "ledgers" / f"{n}.json") for n in done}, use_files)
    covered = {rid for f in opp.load_findings()["findings"] if opp.active(f) for rid in (f.get("links") or {}).get("use_records", [])}
    items = [i for i in items if not (i["kind"] == "component_review" and covered >= {r["record_id"] for r in use_files[i["subsystem"]]["records"] if r["outcome"] in ("component_donor", "composite_input") and outcomes.active(r)})]
    for it in items:
        it["opportunity_class"] = cls_of[it["kind"]]
        if it["kind"] == "runtime_qa":  # gate on the matching implement item, not a separate opportunity
            it["rank_score"], it["asset_use"] = None, "whole_assets"
        elif it["kind"] == "implement":  # grouped replacement work: documented derived profile
            it["scores"] = opp.PROFILES["replacement_candidate"]
            it["rank_score"] = opp.rank_score(it["scores"])
            it["asset_use"] = "whole_assets"
        elif it["kind"] in ("component_review", "technique_build"):
            cl = "component_donor" if it["kind"] == "component_review" else "technique_donor"
            it["scores"] = opp.PROFILES[cl]
            it["rank_score"] = opp.rank_score(it["scores"])
            it["asset_use"] = "components" if it["kind"] == "component_review" else "techniques"
        else:  # unscoped pools / open evidence: not ranked until a target + technique/component is scoped
            it["rank_score"] = None
            it["asset_use"] = {"component_pool": "components", "technique_pool": "techniques"}.get(it["kind"])
    for r in reg["rows"]:
        if r["origin"] != "finding" or r["rank_score"] is None:
            continue
        items.append({"kind": "opportunity", "work_lane": "opportunity", "opportunity_class": r["classification"], "subsystem": r["subsystem"], "source_id": r["source_id"],
                      "target_count": 1, "targets_sample": [r["target"]], "finding_id": r["id"], "title": r["title"], "scores": r["scores"], "rank_score": r["rank_score"],
                      "asset_use": r["asset_use"], "cost": r["cost"], "risk": r["risk"], "priority_score": r["rank_score"]})
    assert all(i["source_id"].split(",")[0] in ds or i["source_id"] == "composite" for i in items), "non-DS donor leaked into the queue"
    ranked = sorted([i for i in items if i["rank_score"] is not None], key=lambda i: (-i["rank_score"], tier[i["opportunity_class"]], i["kind"], i["subsystem"], i["source_id"], i.get("finding_id", "")))
    unranked = sorted([i for i in items if i["rank_score"] is None], key=lambda i: (i["kind"] != "evidence", i["kind"], -i["priority_score"], i["subsystem"], i["source_id"]))
    for n, it in enumerate(ranked, 1):
        it["rank"] = n
    for it in unranked:
        it["rank"] = None
    items = ranked + unranked
    return {
        "schema_version": 3,
        "phase": "ds_only", "inputs": {"scope_sha256": file_sha256(opp.SCOPE_JSON), "classes_sha256": file_sha256(opp.CLASSES_JSON), "findings_sha256": file_sha256(opp.FINDINGS_JSON) if opp.FINDINGS_JSON.is_file() else None, "ledger_files": {n: file_sha256(SEL / "ledgers" / f"{n}.json") for n in done}, "use_outcomes_sha256": file_sha256(outcomes.USE_OUTCOMES_JSON),
                   "use_files": {k: file_sha256(outcomes.comp_path(k)) for k in sorted(use_files)}},
        "completed_subsystems": done,
        "pending_subsystems": pending,
        "items": items,
    }


def write_md(q: dict) -> None:
    L = ["# Donor Implementation Queue", "", "Generated by `build_queue.py`. Phase: **DS-only** (PHASE_SCOPE.json; GBA/GBC findings are deferred and excluded). Ranked by opportunity score across all eight classes; reference_only/reject are never queued. No Platinum resource is modified.", ""]
    L.append(f"- completed subsystems: {', '.join(q['completed_subsystems']) or 'none'}")
    L.append(f"- pending subsystems: {len(q['pending_subsystems'])}")
    L.append("")
    ranked = [i for i in q["items"] if i["rank"] is not None]
    L += ["## Ranked opportunities (DS-only)", "", "Score = weighted mean of visual impact(7), novelty(6), feasibility(5), reuse(4), cost(3, inverted), risk(2, inverted), vertical-slice usefulness(1); 1-5 scale.", "",
          "| # | Class | Opportunity / work | Source | Asset use | Score |", "|---:|---|---|---|---|---:|"]
    for i in ranked:
        what = i.get("title") or f"{i['kind']}: {i['subsystem']} ({i.get('target_count') or i.get('groups')})"
        L.append(f"| {i['rank']} | {i['opportunity_class']} | {what} | {i['source_id']} | {i['asset_use']} | {i['rank_score']} |")
    L += ["", "## Unranked: open evidence and unscoped pools", "", "| Kind | Class | Subsystem | Source | Groups |", "|---|---|---|---|---:|"]
    for i in q["items"]:
        if i["rank"] is None:
            L.append(f"| {i['kind']} | {i['opportunity_class'] or '-'} | {i['subsystem']} | {i['source_id']} | {i.get('target_count') or i.get('groups')} |")
    (SEL / "IMPLEMENTATION_QUEUE.md").write_text("\n".join(L) + "\n")


def main() -> int:
    q = derive()
    jdump(SEL / "IMPLEMENTATION_QUEUE.json", q)
    write_md(q)
    print(f"queue items: {len(q['items'])}; completed: {q['completed_subsystems']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
