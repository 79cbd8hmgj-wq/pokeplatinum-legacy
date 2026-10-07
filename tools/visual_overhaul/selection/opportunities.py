"""Opportunity layer (selection v3): canonical 8-class donor classification over the existing selection outputs.

Additive: ledgers, SELECTION_RULES, USE_OUTCOMES and components/*.json are not changed. This module
  * loads OPPORTUNITY_CLASSES.json (taxonomy) and opportunities/findings.json (explicit findings, incl. novel
    capability/detail records with NO existing Platinum target and findings for donors that are not cataloged),
  * derives a unified register (explicit findings + existing use records + ledger replacement verdicts + none_found reviews),
  * validates the findings file.
See SELECTION_SCHEMA.md "Opportunity classes".
"""
from __future__ import annotations

from common import *  # noqa: F401,F403
import outcomes
import rules as engine

CLASSES_JSON = SEL / "OPPORTUNITY_CLASSES.json"
FINDINGS_JSON = SEL / "opportunities" / "findings.json"
UNVERIFIED_BASIS = "prior_session_unrecorded"


def taxonomy() -> dict:
    return jload(CLASSES_JSON)


def load_findings() -> dict:
    return jload(FINDINGS_JSON) if FINDINGS_JSON.is_file() else {"schema_version": 1, "findings": []}


def active(f: dict) -> bool:
    return f["status"] != "withdrawn"


def bound_digest(group_ids, groups: dict, evidence: dict) -> str:
    """Digest binding a finding to the exact member sets (and evidence entries) of the groups it cites."""
    parts = []
    for gid in sorted(group_ids):
        g = groups[gid]
        ent = evidence.get(g["subsystem"], {}).get("entries", {}).get(gid)
        parts.append(f"{gid}|{g['member_digest']}|{engine.evidence_digest(ent) if ent else '-'}")
    return digest_ids(parts)


def needs_verification(f: dict) -> bool:
    return f["evidence"]["basis"] == UNVERIFIED_BASIS


def validate_findings(groups: dict, ledgers: dict, evidence: dict, use_files: dict) -> list[str]:
    errs: list[str] = []
    tx = taxonomy()
    classes = tx["classes"]
    doc = load_findings()
    seen: set[str] = set()
    for f in doc["findings"]:
        fid = f.get("finding_id", "?")
        t = f"opportunities/findings.json:{fid}"
        if fid in seen:
            errs.append(f"{t}: duplicate finding_id")
        seen.add(fid)
        for k in tx["required_finding_fields"]:
            if f.get(k) in (None, "", [], {}):
                errs.append(f"{t}: missing required field {k}")
        cl = f.get("classification")
        if cl not in classes:
            errs.append(f"{t}: unknown classification {cl}")
            continue
        if f.get("status") not in tx["status"]:
            errs.append(f"{t}: bad status")
            continue
        if f.get("pixel_use") not in tx["pixel_use"]:
            errs.append(f"{t}: bad pixel_use")
        if f.get("confidence") not in tx["confidence_levels"] or f.get("risk") not in tx["cost_levels"] or f.get("cost") not in tx["cost_levels"]:
            errs.append(f"{t}: bad confidence/risk/cost")
        if f.get("feasibility") not in (1, 2, 3):
            errs.append(f"{t}: feasibility must be 1..3")
        for k in ("constraints", "adaptation"):
            if not isinstance(f.get(k), list) or not all(isinstance(s, str) and s.strip() for s in f.get(k) or []):
                errs.append(f"{t}: {k} must be a non-empty list of non-empty strings")
        pol = classes[cl]
        if pol["pixel_policy"] == "none" and f.get("pixel_use") != "none":
            errs.append(f"{t}: {cl} must have pixel_use none (never carries donor pixels)")
        if cl == "replacement_candidate" and f.get("pixel_use") != "donor_pixels":
            errs.append(f"{t}: replacement_candidate must declare pixel_use donor_pixels")
        if cl in ("component_donor", "enhancement_candidate") and f.get("pixel_use") == "none":
            errs.append(f"{t}: {cl} must declare how donor pixels/components are used (none is technique-only)")
        # donor provenance
        d = f.get("donor") or {}
        for k in ("game", "source_id", "locator"):
            if not (d.get(k) or "").strip():
                errs.append(f"{t}: donor.{k} missing (provenance cannot be lost)")
        # target
        tg = f.get("target") or {}
        kind = tg.get("kind")
        if kind not in tx["target_kinds"]:
            errs.append(f"{t}: bad target.kind")
        elif kind == "none":
            if pol["target_policy"] != "none_allowed":
                errs.append(f"{t}: {cl} requires an intended Platinum target or system")
            if cl in ("novel_capability", "novel_detail") and not (tg.get("host_system") or "").strip():
                errs.append(f"{t}: target-less {cl} must name target.host_system")
        else:
            if not (tg.get("subsystem") and (tg.get("target_id") or tg.get("system"))):
                errs.append(f"{t}: target needs subsystem and target_id/system")
            for p in tg.get("refs") or []:
                if not (ROOT / p).exists():
                    errs.append(f"{t}: target ref {p} does not exist")
            if kind == "system" and not tg.get("refs"):
                errs.append(f"{t}: system target needs refs[] naming existing Platinum code/resources")
            if kind == "asset":
                nr = tg.get("native_ref") or {}
                if not nr.get("path") or not (ROOT / nr["path"]).is_file() or file_sha256(ROOT / nr["path"])[: len(nr.get("sha256", "x"))] != nr.get("sha256"):
                    errs.append(f"{t}: target.native_ref missing or hash mismatch")
                led = ledgers.get(tg.get("subsystem"))
                if led is None or tg.get("target_id") not in {x["target_id"] for x in led["targets"]}:
                    errs.append(f"{t}: asset target missing from the {tg.get('subsystem')} ledger")
        # evidence
        ev = f.get("evidence") or {}
        basis = ev.get("basis")
        if basis not in tx["evidence_basis"]:
            errs.append(f"{t}: bad evidence.basis")
            continue
        if not (ev.get("summary") or "").strip():
            errs.append(f"{t}: evidence.summary missing")
        for p in ev.get("refs") or []:
            if not (ROOT / p).exists():
                errs.append(f"{t}: evidence ref {p} missing")
        if basis in ("repo_document", "catalog_evidence") and not ev.get("refs"):
            errs.append(f"{t}: {basis} evidence needs refs[]")
        if basis == "catalog_evidence":
            gids = d.get("group_ids") or []
            if not gids or any(g not in groups for g in gids):
                errs.append(f"{t}: catalog_evidence needs donor.group_ids that are curated candidate groups")
            elif ev.get("bound_digest") != bound_digest(gids, groups, evidence):
                errs.append(f"{t}: stale (cited groups/evidence changed since this finding was written)")
            elif d.get("source_id") not in {groups[g]["source_id"] for g in gids}:
                errs.append(f"{t}: donor.source_id does not match the cited groups")
        if basis == UNVERIFIED_BASIS:
            if f.get("confidence") != "low" or f.get("feasibility") != 1:
                errs.append(f"{t}: unrecorded-evidence findings are capped at confidence low / feasibility 1")
            if f.get("status") == "human_confirmed":
                errs.append(f"{t}: cannot be human_confirmed without recorded evidence")
            if d.get("cataloged"):
                errs.append(f"{t}: donor marked cataloged but evidence basis is unrecorded")
        # links to existing explicit use records (enhancement aggregates)
        for rid in (f.get("links") or {}).get("use_records", []):
            hit = None
            for sname, ud in use_files.items():
                hit = hit or outcomes.doc_rec(ud, rid)
            if hit is None or not outcomes.active(hit):
                errs.append(f"{t}: linked use record {rid} missing/withdrawn")
            elif cl == "enhancement_candidate" and (hit.get("target") or {}).get("target_id") != tg.get("target_id"):
                errs.append(f"{t}: linked use record {rid} targets a different target")
        if cl == "enhancement_candidate" and not (f.get("links") or {}).get("use_records") and not f.get("component_refs"):
            errs.append(f"{t}: enhancement_candidate must link the component/technique records it aggregates")
        if cl == "enhancement_candidate" and kind != "none":
            led = ledgers.get(tg.get("subsystem"), {})
            res = {x["target_id"]: x["resolution"] for x in led.get("targets", [])}.get(tg.get("target_id"))
            if res is not None and res != "platinum_native":
                errs.append(f"{t}: enhancement target resolves to {res}; enhancement and donor replacement are exclusive")
    return errs


def replacement_rows(ledgers: dict) -> list[dict]:
    rows = []
    for sname, led in sorted(ledgers.items()):
        for d in led["decisions"]:
            if d["role"] == "preferred":
                rows.append({"id": f"ledger:{d['group_id']}", "classification": "replacement_candidate", "origin": "ledger", "status": "preferred" ,
                             "subsystem": sname, "target": d["target_id"], "source_id": d["source_id"], "feasibility": 3, "verified": True,
                             "needs_runtime_validation": bool(d["needs_runtime_validation"])})
    return rows


def derive_register(ledgers: dict, use_files: dict) -> dict:
    tx = taxonomy()
    tier = {k: v["tier"] for k, v in tx["classes"].items()}
    rows: list[dict] = []
    for f in load_findings()["findings"]:
        if not active(f):
            continue
        rows.append({"id": f["finding_id"], "classification": f["classification"], "origin": "finding", "status": f["status"],
                     "subsystem": f["target"].get("subsystem") or f["target"].get("host_system"), "target": f["target"].get("target_id") or f["target"].get("system"),
                     "source_id": f["donor"]["source_id"], "donor_game": f["donor"]["game"], "feasibility": f["feasibility"], "cost": f["cost"], "risk": f["risk"],
                     "confidence": f["confidence"], "verified": not needs_verification(f), "title": f.get("subject", "")})
    m = tx["map_existing"]["use_record_outcomes"]
    for sname, doc in sorted(use_files.items()):
        for r in doc.get("records", []):
            if outcomes.active(r) and r["outcome"] in m:
                rows.append({"id": r["record_id"], "classification": m[r["outcome"]], "origin": "use_record", "status": r["status"], "subsystem": sname,
                             "target": r["target"]["target_id"], "source_id": r["source"]["source_id"], "feasibility": 2, "cost": "medium", "risk": r["risk"],
                             "confidence": r["confidence"], "verified": True})
        for cr in doc.get("component_reviews", []):
            if cr["finding"] == "none_found":
                rows.append({"id": f"review:{cr['group_id']}", "classification": tx["map_existing"]["component_review_none_found"], "origin": "component_review", "status": "reviewed",
                             "subsystem": sname, "target": cr.get("target_id"), "source_id": cr["group_id"].split("/")[1], "verified": True, "feasibility": None})
    rows += replacement_rows(ledgers)
    rows.sort(key=lambda r: (tier[r["classification"]], -(r.get("feasibility") or 0), r["id"]))
    counts = {c: 0 for c in tx["classes"]}
    for r in rows:
        counts[r["classification"]] += 1
    pools = {"technique_donor_unscoped_groups": 0, "component_donor_unscoped_groups": 0, "replacement_candidate_alternate_groups": 0, "unreviewed_not_selected_groups": 0, "needs_evidence_groups": 0}
    v = outcomes.vocab()
    for led in ledgers.values():
        for d in led["decisions"]:
            o = outcomes.replacement_outcome(d, v)
            if o == "technique_reference":
                pools["technique_donor_unscoped_groups"] += 1
            elif d["role"] == "reference_only" and d["reason_code"] == "no_native_target":
                pools["component_donor_unscoped_groups"] += 1
            elif o == "alternate":
                pools["replacement_candidate_alternate_groups"] += 1
            elif o == "not_selected":
                pools["unreviewed_not_selected_groups"] += 1
            elif o == "needs_evidence":
                pools["needs_evidence_groups"] += 1
    return {"schema_version": 1,
            "inputs": {"classes_sha256": file_sha256(CLASSES_JSON), "findings_sha256": file_sha256(FINDINGS_JSON) if FINDINGS_JSON.is_file() else None,
                       "use_files": {k: file_sha256(outcomes.comp_path(k)) for k in sorted(use_files)}},
            "counts_by_class": counts, "unscoped_pools": pools,
            "needs_donor_verification": sorted(r["id"] for r in rows if not r["verified"]), "rows": rows}
