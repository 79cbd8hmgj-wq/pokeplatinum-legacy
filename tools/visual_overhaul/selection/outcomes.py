"""Donor-use outcome layer (selection v2): derived replacement outcomes + explicit component/composite/technique records.

The ledgers (role/reason_code) are NOT modified by this layer. See SELECTION_SCHEMA.md "Use outcomes".
"""
from __future__ import annotations

import hashlib
import json

from common import *  # noqa: F401,F403
import rules as engine

USE_OUTCOMES_JSON = SEL / "USE_OUTCOMES.json"
COMP_DIR = SEL / "components"


def vocab() -> dict:
    return jload(USE_OUTCOMES_JSON)


def replacement_outcome(decision: dict, v: dict | None = None) -> str:
    """Derived replacement-axis outcome of one ledger decision (raises KeyError on an unmapped pair)."""
    v = v or vocab()
    if decision["needs_evidence"]:
        return "needs_evidence"
    m = v["legacy_role_map"]
    if decision["role"] in m["by_role"]:
        return m["by_role"][decision["role"]]
    return m["by_role_reason"][f'{decision["role"]}/{decision["reason_code"]}']


def record_digest(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k not in ("status", "human_review")}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]


def comp_path(subsystem: str) -> Path:
    return COMP_DIR / f"{subsystem}.json"


def load_use_files() -> dict[str, dict]:
    return {p.stem: jload(p) for p in sorted(COMP_DIR.glob("*.json"))} if COMP_DIR.is_dir() else {}


def active(rec: dict) -> bool:
    return rec["status"] != "withdrawn"


def catalog_index() -> dict[str, dict]:
    idx = {a["asset_id"]: a for a in jload(VO / "DONOR_ASSET_CATALOG.json")["assets"]}
    for e in extensions():
        for a in jload(EXT_DIR / e["catalog"])["assets"]:
            idx[a["asset_id"]] = a
    return idx


def validate_use_records(groups: dict, membership: dict, ledgers: dict, evidence: dict, recovered: dict | None = None) -> list[str]:
    """groups: group_id->group; membership: asset_id->group_id; ledgers: subsystem->ledger; evidence: subsystem->evidence doc."""
    errs: list[str] = []
    v = vocab()
    outcomes = set(v["outcomes"])
    contribution = {k for k, o in v["outcomes"].items() if o["axis"] == "contribution"}
    tags_ok = set(v["component_tags"])
    recovered = recovered if recovered is not None else load_recovered_records()
    cat = None

    # U0: every ledger decision maps to a replacement outcome; legacy map only targets known outcomes
    for k, o in list(v["legacy_role_map"]["by_role"].items()) + list(v["legacy_role_map"]["by_role_reason"].items()):
        if o not in outcomes or v["outcomes"][o]["axis"] != "replacement" and o != "technique_reference":
            errs.append(f"USE_OUTCOMES legacy map {k} -> {o} invalid")
    dec_of: dict[str, dict] = {}
    for sname, led in ledgers.items():
        for d in led["decisions"]:
            dec_of[d["group_id"]] = d
            try:
                replacement_outcome(d, v)
            except KeyError:
                errs.append(f"{sname}: {d['group_id']} role/reason {d['role']}/{d['reason_code']} has no outcome mapping")

    files = load_use_files()
    all_ids: dict[str, str] = {}
    recs_by_id: dict[str, dict] = {}
    for sname, doc in files.items():
        tag = f"components/{sname}.json"
        if doc.get("subsystem") != sname or sname not in ledgers:
            errs.append(f"{tag}: subsystem mismatch / no ledger")
            continue
        led = ledgers[sname]
        tmap = {t["target_id"]: t for t in led["targets"]}
        ev_entries = evidence.get(sname, {}).get("entries", {})
        for rec in doc.get("records", []):
            rid = rec.get("record_id", "?")
            rt = f"{tag}:{rid}"
            if rid in all_ids:
                errs.append(f"{rt}: duplicate record_id")
            all_ids[rid] = sname
            recs_by_id[rid] = rec
            for f in v["required_record_fields"]:
                if rec.get(f) in (None, "", [], {}):
                    errs.append(f"{rt}: missing required field {f}")
            if rec.get("outcome") not in contribution:
                errs.append(f"{rt}: outcome {rec.get('outcome')} is not a contribution outcome (replacement outcomes are derived, never recorded)")
                continue
            if rec.get("status") not in v["record_status"]:
                errs.append(f"{rt}: bad status")
                continue
            if rec.get("pixel_use") not in v["pixel_use"]:
                errs.append(f"{rt}: bad pixel_use")
            if rec.get("confidence") not in v["confidence_levels"] or rec.get("risk") not in v["risk_levels"]:
                errs.append(f"{rt}: bad confidence/risk")
            tg = rec.get("tags") or []
            if not tg or any(t not in tags_ok for t in tg) or len(set(tg)) != len(tg):
                errs.append(f"{rt}: tags must be a non-empty duplicate-free subset of component_tags")
            for f in ("constraints", "adaptation"):
                if not isinstance(rec.get(f), list) or not all(isinstance(s, str) and s.strip() for s in rec.get(f) or []):
                    errs.append(f"{rt}: {f} must be a non-empty list of non-empty strings")
            comp = rec.get("component") or {}
            if not (comp.get("property") or "").strip():
                errs.append(f"{rt}: component.property missing")
            if rec.get("outcome") == "technique_reference" and rec.get("pixel_use") != "none":
                errs.append(f"{rt}: technique_reference must have pixel_use none (technique use never carries donor pixels)")
            if rec.get("outcome") in ("component_donor", "composite_input") and rec.get("pixel_use") == "none":
                errs.append(f"{rt}: component use must declare how donor pixels are used (pixel_use none is technique-only)")
            # target
            tgt = rec.get("target") or {}
            if tgt.get("subsystem") != sname or tgt.get("target_id") not in tmap:
                errs.append(f"{rt}: target missing from the {sname} ledger")
            nr = tgt.get("native_ref")
            if rec.get("outcome") != "technique_reference" or nr:
                if not nr or not nr.get("path") or not nr.get("sha256"):
                    errs.append(f"{rt}: target.native_ref (path+sha256) required")
                elif not (ROOT / nr["path"]).is_file() or file_sha256(ROOT / nr["path"])[: len(nr["sha256"])] != nr["sha256"]:
                    errs.append(f"{rt}: target.native_ref hash does not match the Platinum file")
            # source provenance
            src = rec.get("source") or {}
            for f in v["required_source_fields"]:
                if not src.get(f):
                    errs.append(f"{rt}: source.{f} missing (provenance cannot be lost)")
            g = groups.get(src.get("group_id"))
            if g is None:
                errs.append(f"{rt}: source group {src.get('group_id')} is not a curated candidate group")
                continue
            if g["member_digest"] != src.get("member_digest") or g["source_id"] != src.get("source_id"):
                errs.append(f"{rt}: source member_digest/source_id stale vs group {g['group_id']}")
            if cat is None:
                cat = catalog_index()
            for a in src.get("assets") or []:
                for f in v["required_source_asset_fields"]:
                    if not a.get(f):
                        errs.append(f"{rt}: source asset missing {f}")
                aid = a.get("asset_id")
                if membership.get(aid) != g["group_id"]:
                    errs.append(f"{rt}: asset {aid} is not a member of {g['group_id']}")
                    continue
                r = recovered.get(aid)
                if r is None or r["review_status"] != "usable":
                    errs.append(f"{rt}: asset {aid} is not a curated usable record")
                ca = cat.get(aid)
                if ca is None:
                    errs.append(f"{rt}: asset {aid} not in donor catalog")
                    continue
                if ca["source_path"] != a.get("source_path") or ca.get("source_metadata", {}).get("source_commit", a.get("source_commit")) != a.get("source_commit"):
                    errs.append(f"{rt}: source path/commit differs from catalog for {aid}")
                if a.get("render_sha256") and ca.get("source_metadata", {}).get("render_sha256") != a["render_sha256"]:
                    errs.append(f"{rt}: render_sha256 differs from catalog for {aid}")
            # component use is distinct from whole-asset replacement
            gd = dec_of.get(g["group_id"])
            if gd and gd["role"] == "preferred" and rec.get("outcome") != "technique_reference" and active(rec):
                errs.append(f"{rt}: component use recorded on a direct_replacement (preferred) group; replacement and component use must stay distinct")
            # evidence binding
            evd = rec.get("evidence") or {}
            if evd.get("kind") not in v["evidence_kinds"] or not (evd.get("summary") or "").strip():
                errs.append(f"{rt}: evidence.kind/summary invalid")
            ent = ev_entries.get(g["group_id"]) if g["subsystem"] == sname else evidence.get(g["subsystem"], {}).get("entries", {}).get(g["group_id"])
            want = engine.evidence_digest(ent) if ent else None
            if evd.get("evidence_entry_digest") != want:
                errs.append(f"{rt}: evidence_entry_digest stale/mismatched vs current evidence for {g['group_id']}")
            for p in evd.get("refs") or []:
                if not (ROOT / p).is_file():
                    errs.append(f"{rt}: evidence ref {p} missing")
            # human review is digest-bound
            hr = rec.get("human_review")
            if rec["status"] == "human_confirmed":
                if not hr or hr.get("verdict") != "confirm":
                    errs.append(f"{rt}: human_confirmed without a confirm verdict")
                else:
                    if hr.get("member_digest") != g["member_digest"]:
                        errs.append(f"{rt}: stale human review (member digest changed)")
                    if hr.get("evidence_digest") != want:
                        errs.append(f"{rt}: stale human review (evidence changed)")
                    if hr.get("record_digest") != record_digest(rec):
                        errs.append(f"{rt}: stale human review (record content changed after confirmation)")
                    if not hr.get("reviewer") or not hr.get("reviewed_at"):
                        errs.append(f"{rt}: human review lacks reviewer/date")
            elif hr:
                errs.append(f"{rt}: human_review present but status is {rec['status']}")

        # composites
        in_plan: set[str] = set()
        cids = set()
        for cp in doc.get("composites", []):
            cid = cp.get("composite_id", "?")
            ct = f"{tag}:{cid}"
            if cid in cids:
                errs.append(f"{ct}: duplicate composite_id")
            cids.add(cid)
            if cp.get("status") not in v["composite_status"]:
                errs.append(f"{ct}: bad status")
            t = tmap.get(cp.get("target_id"))
            if t is None:
                errs.append(f"{ct}: unknown target")
            elif t["resolution"] != "platinum_native":
                errs.append(f"{ct}: composite target resolves to a donor replacement ({t['resolution']}); native enhancement and replacement are exclusive")
            nb = cp.get("native_base") or {}
            if not nb.get("path") or not (ROOT / nb["path"]).is_file() or file_sha256(ROOT / nb["path"])[: len(nb.get("sha256", "x"))] != nb.get("sha256"):
                errs.append(f"{ct}: native_base missing or hash mismatch")
            if not cp.get("inputs"):
                errs.append(f"{ct}: composite has no inputs")
            for rid in cp.get("inputs", []):
                r = doc_rec(doc, rid)
                if r is None:
                    errs.append(f"{ct}: input {rid} missing/uncurated (not a record of this subsystem)")
                    continue
                if r["outcome"] != "composite_input" or not active(r):
                    errs.append(f"{ct}: input {rid} must be an active composite_input record (is {r['outcome']}/{r['status']})")
                if (r.get("target") or {}).get("target_id") != cp.get("target_id"):
                    errs.append(f"{ct}: input {rid} targets a different target")
                in_plan.add(rid)
                if cp.get("status") in ("ready", "implemented") and r["status"] != "human_confirmed":
                    errs.append(f"{ct}: {cp['status']} composite has unconfirmed input {rid}")
            for rid in cp.get("technique_refs", []):
                r = doc_rec(doc, rid)
                if r is None or r["outcome"] != "technique_reference" or not active(r):
                    errs.append(f"{ct}: technique_ref {rid} must be an active technique_reference record")
        for rec in doc.get("records", []):
            if rec.get("outcome") == "composite_input" and active(rec) and rec["record_id"] not in in_plan:
                errs.append(f"components/{sname}.json:{rec['record_id']}: composite_input not referenced by any composite plan")
            if rec.get("outcome") == "component_donor" and rec["record_id"] in in_plan:
                errs.append(f"components/{sname}.json:{rec['record_id']}: component_donor used in a composite (promote it to composite_input)")

        # component reviews (evaluated-with-no-component findings are digest-bound too)
        seen_rv = set()
        for cr in doc.get("component_reviews", []):
            ct = f"{tag}:review:{cr.get('group_id')}"
            g = groups.get(cr.get("group_id"))
            if g is None:
                errs.append(f"{ct}: unknown group")
                continue
            if cr["group_id"] in seen_rv:
                errs.append(f"{ct}: duplicate review")
            seen_rv.add(cr["group_id"])
            if cr.get("member_digest") != g["member_digest"]:
                errs.append(f"{ct}: stale (member digest changed)")
            ent = evidence.get(g["subsystem"], {}).get("entries", {}).get(g["group_id"])
            if cr.get("evidence_digest") != (engine.evidence_digest(ent) if ent else None):
                errs.append(f"{ct}: stale (evidence changed)")
            if cr.get("finding") not in v["component_review_findings"] or not (cr.get("note") or "").strip() or not cr.get("reviewer"):
                errs.append(f"{ct}: finding/note/reviewer invalid")
            has = [r for r in doc.get("records", []) if (r.get("source") or {}).get("group_id") == g["group_id"] and active(r)]
            if cr.get("finding") == "none_found" and has:
                errs.append(f"{ct}: finding none_found but active component records exist")
            if cr.get("finding") == "records_proposed" and not has:
                errs.append(f"{ct}: finding records_proposed but no active records")
    return errs


def doc_rec(doc: dict, rid: str) -> dict | None:
    for r in doc.get("records", []):
        if r.get("record_id") == rid:
            return r
    return None


def derive_status(groups: list[dict], ledgers: dict) -> dict:
    """OUTCOME_STATUS: per-subsystem derived replacement outcomes + explicit use-record counts."""
    v = vocab()
    files = load_use_files()
    rows = []
    for sname in sorted(ledgers):
        led = ledgers[sname]
        c: dict[str, int] = {}
        for d in led["decisions"]:
            o = replacement_outcome(d, v)
            c[o] = c.get(o, 0) + 1
        doc = files.get(sname, {})
        recs = [r for r in doc.get("records", []) if active(r)]
        rc: dict[str, int] = {}
        for r in recs:
            rc[r["outcome"]] = rc.get(r["outcome"], 0) + 1
        rows.append({
            "subsystem": sname,
            "replacement_outcomes": dict(sorted(c.items())),
            "use_records": dict(sorted(rc.items())),
            "records_human_confirmed": sum(r["status"] == "human_confirmed" for r in recs),
            "composites": {s: sum(cp["status"] == s for cp in doc.get("composites", [])) for s in v["composite_status"] if any(cp["status"] == s for cp in doc.get("composites", []))},
            "component_reviews": len(doc.get("component_reviews", [])),
        })
    return {"schema_version": 1, "inputs": {"use_outcomes_sha256": file_sha256(USE_OUTCOMES_JSON), "use_files": {k: file_sha256(comp_path(k)) for k in sorted(files)}}, "subsystems": rows}
