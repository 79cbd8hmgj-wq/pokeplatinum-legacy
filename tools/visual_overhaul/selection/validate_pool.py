"""Validation of the mined opportunity pool (OPPORTUNITY_POOL.json, mining/passes, needs-evidence queue)."""
from __future__ import annotations

import collections
import json

from common import *  # noqa: F401,F403
import mine_pool
import mine_rules as MR
import opportunities as opp

USE_OK = {"replacement_candidate": {"whole_asset"}, "technique_donor": {"technique"}, "component_donor": {"component"}, "enhancement_candidate": {"composite_input"},
          "novel_capability": {"whole_asset", "component", "technique", "mixed"}, "novel_detail": {"whole_asset", "component", "technique", "mixed"}}


def validate_pool(groups: dict, membership: dict, pool: dict | None = None, check_reproducible: bool = True) -> list[str]:
    errs: list[str] = []
    if pool is None:
        if not mine_pool.POOL_JSON.is_file():
            return ["OPPORTUNITY_POOL.json missing (run mine_pool.py)"]
        pool = jload(mine_pool.POOL_JSON)
    tx = opp.taxonomy()
    sc = opp.scope()
    ds = set(sc["ds_sources"]) - {"platinum"}
    recs = pool["records"]
    ids = [r["opportunity_id"] for r in recs]
    for oid, n in collections.Counter(ids).items():
        if n > 1:
            errs.append(f"pool: duplicate opportunity_id {oid}")
    deferred = {f["finding_id"] for f in opp.load_deferred()["findings"]}
    if set(ids) & deferred:
        errs.append("pool: deferred GBA/GBC finding ids appear in the active pool")
    if pool["groups_processed"] != len(groups):
        errs.append(f"pool: groups_processed {pool['groups_processed']} != {len(groups)} candidate groups")
    # inputs freshness (ledgers/groups untouched since the pool was mined)
    inp = pool["inputs"]
    if inp["groups_sha256"] != file_sha256(GROUPS_JSON):
        errs.append("pool: stale vs CANDIDATE_GROUPS.json (rerun mine_pool.py)")
    for n, h in inp["ledgers"].items():
        if file_sha256(SEL / "ledgers" / f"{n}.json") != h:
            errs.append(f"pool: stale vs ledger {n}")
    mined_keys = collections.Counter()
    for r in recs:
        t = f"pool:{r['opportunity_id']}"
        cl = r.get("classification")
        if cl not in tx["classes"]:
            errs.append(f"{t}: unknown class {cl}")
            continue
        if cl in ("reference_only", "reject") and r["origin"] == "mined":
            errs.append(f"{t}: reference_only/reject are group dispositions, not promoted records")
        if r["source_id"] not in ds:
            errs.append(f"{t}: donor {r['source_id']} outside the DS phase scope / not a donor")
        if r["origin"] == "mined":
            g = groups.get(r["group_id"])
            if g is None:
                errs.append(f"{t}: candidate group {r['group_id']} does not exist")
                continue
            if g["member_digest"] != r["member_digest"] or g["source_id"] != r["source_id"] or g["subsystem"] != r["subsystem"]:
                errs.append(f"{t}: provenance differs from the group (digest/source/subsystem)")
            if r["source_id"] == "diamond" and not r.get("diamond_exception"):
                errs.append(f"{t}: Diamond is control/reference; promoted record needs a justified diamond_exception")
            for a in r["member_sample"]:
                if membership.get(a) != r["group_id"]:
                    errs.append(f"{t}: member {a} is not in the group")
                    break
            if r["use_mode"] not in USE_OK.get(cl, set()):
                errs.append(f"{t}: use_mode {r['use_mode']} inconsistent with class {cl}")
            if cl == "technique_donor" and (r["pixel_use"] != "none" or r["donor_pixels_intended"]):
                errs.append(f"{t}: technique_donor must not reuse donor pixels")
            if cl == "replacement_candidate" and (r["ledger"]["role"] != "preferred" or r["remains_platinum_native"] or not r["donor_pixels_intended"]):
                errs.append(f"{t}: replacement_candidate must come from a ledger-preferred group and use donor pixels")
            if cl in ("component_donor", "enhancement_candidate") and r["use_mode"] == "whole_asset":
                errs.append(f"{t}: component/enhancement use must be distinguishable from whole-asset use")
            if r["status"] not in ("promoted", "needs_evidence"):
                errs.append(f"{t}: bad status")
            mined_keys[(r["group_id"], cl, r["use_mode"])] += 1
            if not r["why_surfaced"] or not r["why_it_matters"] or not r["evidence_pointers"]:
                errs.append(f"{t}: missing why_surfaced / why_it_matters / evidence_pointers")
            d = r["dims"]
            if set(d) != set(MR.DIMS) or any(not isinstance(d[k], int) or not 1 <= d[k] <= 5 for k in MR.DIMS):
                errs.append(f"{t}: dims invalid")
            elif MR.composite(d) != r["composite"]:
                errs.append(f"{t}: composite does not match dims")
            if r["classification"] == "replacement_candidate" and r["dims"]["novelty"] != 1:
                errs.append(f"{t}: replacement must carry novelty 1")
        for p in r["evidence_pointers"]:
            if not (ROOT / p).exists():
                errs.append(f"{t}: evidence pointer {p} missing")
        for p in r["platinum_host"]["refs"]:
            if not (ROOT / p).exists():
                errs.append(f"{t}: platinum host ref {p} missing")
    for k, n in mined_keys.items():
        if n > 1:
            errs.append(f"pool: duplicate (group,class,use_mode) {k}")
    explicit_ids = {r["opportunity_id"] for r in recs if r["origin"] == "explicit"}
    if explicit_ids != {f["finding_id"] for f in opp.load_findings()["findings"] if opp.active(f)}:
        errs.append("pool: explicit findings not integrated (set differs from active findings)")
    for r in recs:
        if r.get("subsumed_by") and r["subsumed_by"] not in explicit_ids:
            errs.append(f"pool:{r['opportunity_id']}: subsumed_by unknown explicit finding")
    # libraries
    byid = set(ids)
    for l in pool["libraries"]:
        if any(x not in byid for x in l["top_records"]):
            errs.append(f"pool: library {l['library_id']} references a missing record")
    # passes: every group processed exactly once; dispositions consistent
    seen = collections.Counter()
    for p in sorted((SEL / "mining" / "passes").glob("*.json")):
        pd = jload(p)
        for x in pd["ranked"]:
            seen[x["g"]] += 1
            if x["g"] not in groups:
                errs.append(f"passes/{p.name}: unknown group {x['g']}")
            if x["disp"] in ("promoted", "needs_evidence") and not x["rec"]:
                errs.append(f"passes/{p.name}: {x['g']} {x['disp']} without records")
            for rid in x["rec"]:
                if rid not in byid:
                    errs.append(f"passes/{p.name}: record {rid} missing from pool")
    if set(seen) != set(groups) or any(v != 1 for v in seen.values()):
        errs.append(f"passes: not every candidate group processed exactly once ({len(seen)}/{len(groups)})")
    ne = jload(mine_pool.NE_JSON)
    ne_ids = {r["opportunity_id"] for r in recs if r["origin"] == "mined" and r["status"] == "needs_evidence"}
    if {x["opportunity_id"] for x in ne["items"]} != ne_ids:
        errs.append("needs-evidence queue differs from needs_evidence pool records")
    # evidence closure: resolutions are pinned to the frozen baseline scope, cite existing evidence, and every baseline needs-evidence record is accounted for
    if mine_pool.RES_JSON.is_file():
        res = jload(mine_pool.RES_JSON)
        scope_p = mine_pool.MINING / "EVIDENCE_CLOSURE_SCOPE.json"
        scope = jload(scope_p)
        if res["scope_sha256"] != file_sha256(scope_p):
            errs.append("evidence resolutions: stale vs EVIDENCE_CLOSURE_SCOPE.json (rerun resolve_evidence.py)")
        if set(res["scope_groups"]) != set(scope["group_ids"]):
            errs.append("evidence resolutions: scope_groups differ from the frozen closure scope")
        for gid in res["group_resolutions"]:
            if gid not in groups:
                errs.append(f"evidence resolutions: unknown group {gid}")
            elif gid not in set(scope["group_ids"]):
                errs.append(f"evidence resolutions: {gid} is outside the frozen closure scope")
        for x in list(res["family_resolutions"]) + list(res["group_resolutions"].values()):
            if x["verdict"] not in ("confirm", "reference_only"):
                errs.append(f"evidence resolutions: bad verdict {x['verdict']}")
            for rp in x.get("evidence_refs", []):
                if not (ROOT / rp).exists():
                    errs.append(f"evidence resolutions: evidence ref {rp} missing")
        closed = set()
        for p in sorted((SEL / "mining" / "passes").glob("*.json")):
            for x in jload(p)["ranked"]:
                if any(sg.startswith("evidence_closed") for sg in x["sig"]):
                    closed.add(x["g"])
        by_id = {r["opportunity_id"]: r for r in recs}
        for oid in scope["opportunity_ids"]:
            gid = oid[len("opp:mined/"):].rsplit("/", 2)[0]
            r = by_id.get(oid)
            if r is None and gid not in closed:
                errs.append(f"evidence closure: baseline record {oid} vanished without an evidence_closed disposition")
            if r is not None and r["status"] == "promoted" and not r.get("evidence_resolution") and gid in set(res["scope_groups"]):
                errs.append(f"evidence closure: {oid} promoted without an evidence_resolution block")
    if check_reproducible:
        try:
            res = mine_pool.derive()
            fresh = mine_pool.pool_doc(res)
        except Exception as e:  # ledgers/groups inconsistent: other validators report the root cause
            errs.append(f"pool: cannot be re-derived from current ledgers/groups ({type(e).__name__}: {e})")
        else:
            if json.loads(json.dumps(fresh, sort_keys=True)) != json.loads(json.dumps(pool, sort_keys=True)):
                errs.append("OPPORTUNITY_POOL.json is not reproducible from current catalog/ledgers/evidence (rerun mine_pool.py)")
    return errs
