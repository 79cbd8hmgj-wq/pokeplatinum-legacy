"""Selection decision engine. Implements SELECTION_RULES.json exactly (rules_version 1.0)."""
from __future__ import annotations

from common import *  # noqa: F401,F403
import json


def risk_bump(level: str, n: int, order) -> str:
    return order[min(order.index(level) + n, len(order) - 1)]


def score_group(g: dict, ev: dict | None, rules: dict, sub: dict) -> dict:
    relation = (ev or {}).get("native_relation", "unmeasured")
    gain = rules["native_relation_to_gain"].get(relation)
    conv = g["conversion_requirement"]
    needs_rt = relation in rules["runtime_validation_relations"]
    order = rules["risk_order"]
    risk = rules["base_risk_by_conversion"][conv]
    flags = (ev or {}).get("risk_flags", [])
    bumps = int(needs_rt) + int(g["unresolved_decode_issue_members"] > 0) + sum(rules["risk_flag_bumps"][f] for f in flags)
    risk = risk_bump(risk, bumps, order)
    share = g["independent_member_count"] / g["member_count"]
    return {
        "native_relation": relation,
        "visual_gain": gain,
        "compat": rules["compat_score_by_conversion"][conv],
        "risk": risk,
        "integration_cost": sub["integration_cost"] + rules["conversion_scale"][conv],
        "independent_share": round(share, 4),
        "needs_runtime_validation": needs_rt or bool(flags),
        "risk_flags": sorted(flags),
    }


def initial_role(g: dict, s: dict, rules: dict) -> tuple[str, str]:
    th = rules["thresholds"]
    order = rules["risk_order"]
    cls = g["donor_class"]
    rel = s["native_relation"]
    gain = s["visual_gain"]
    if g["independent_member_count"] < th["min_independent_members"]:
        return "not_selected", "no_independent_evidence"
    if cls == "none":
        return "not_selected", "source_not_relevant_to_subsystem"
    if cls in ("technique", "reference") or g["conversion_requirement"] == "not_portable":
        return "reference_only", "policy_reference_class"
    if rel == "missing_in_native":
        return "reference_only", "no_native_target"
    if cls == "control":
        if rel in ("identical", "content_match_native"):
            return "not_selected", "identical_to_native"
        if rel == "unmeasured":
            return "reference_only", "control_unmeasured"
        return "reference_only", "control_differs_from_native"
    # direct / convertible
    if gain == 0:
        return "not_selected", "identical_to_native"
    if gain is None:
        return "reference_only", "needs_evidence"
    if s["independent_share"] < th["selection_min_independent_share"]:
        return "reference_only", "weak_evidence_share"
    if (
        s["compat"] >= th["preferred_min_compat"]
        and order.index(s["risk"]) <= order.index(th["preferred_max_risk"])
        and gain >= th["preferred_min_gain"]
    ):
        return "eligible_preferred", "best_eligible_donor"
    if s["compat"] >= th["alternate_min_compat"] and gain >= th["alternate_min_gain"]:
        return "eligible_alternate", "eligible_not_best_for_target"
    return "reference_only", "below_integration_thresholds"


def rank_key(g: dict, s: dict, rules: dict):
    order = rules["risk_order"]
    pref = rules["source_preference"]
    return (
        -(s["visual_gain"] or 0),
        -s["compat"],
        order.index(s["risk"]),
        rules["class_rank"].get(g["donor_class"], 9),
        pref.index(g["source_id"]) if g["source_id"] in pref else 99,
        g["group_id"],
    )


def evidence_digest(entry) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()[:16]


def decide(groups: list[dict], evidence: dict, rules: dict, subs: dict, reviews: dict | None = None) -> tuple[list[dict], list[dict]]:
    """groups: all candidate groups of ONE subsystem. Returns (decisions, targets)."""
    entries = evidence.get("entries", {})
    reviews = reviews or {}
    gids = {g["group_id"]: g for g in groups}
    for gid, rv in reviews.items():  # human verdicts must bind to the exact group + evidence they reviewed
        if gid not in gids:
            raise ValueError(f"review for unknown group {gid}")
        if rv["member_digest"] != gids[gid]["member_digest"]:
            raise ValueError(f"stale review (member digest changed): {gid}")
        if rv["evidence_digest"] != evidence_digest(entries.get(gid)):
            raise ValueError(f"stale review (evidence changed): {gid}")
        if rv["verdict"] not in ("use_hgss", "keep_platinum"):
            raise ValueError(f"bad verdict for {gid}")
    work = []
    for g in groups:
        sub = subs[g["subsystem"]]
        ev = entries.get(g["group_id"])
        s = score_group(g, ev, rules, sub)
        role, reason = initial_role(g, s, rules)
        rv = reviews.get(g["group_id"])
        pending = False
        if rv:
            if rv["verdict"] == "keep_platinum":
                if role.startswith("eligible_"):
                    role, reason = "not_selected", "human_keep_platinum"
            else:  # use_hgss: approval can only confirm a group the automated gates already consider eligible
                if not role.startswith("eligible_"):
                    raise ValueError(f"use_hgss verdict conflicts with automated gates ({reason}): {g['group_id']}")
                role = "eligible_preferred"
        elif sub.get("human_review_required") and role == "eligible_preferred":
            role, pending = "eligible_alternate", True
        work.append({"g": g, "s": s, "role": role, "reason": reason, "ev": ev, "review": rv, "pending": pending})

    by_target: dict[str, list[dict]] = {}
    for w in work:
        by_target.setdefault(w["g"]["target_id"], []).append(w)
    targets = []
    for tid in sorted(by_target):
        ws = by_target[tid]
        elig = sorted(
            [w for w in ws if w["role"] in ("eligible_preferred", "eligible_alternate")],
            key=lambda w: rank_key(w["g"], w["s"], rules),
        )
        top = next((w for w in elig if w["role"] == "eligible_preferred"), None)
        for w in elig:
            if w is top:
                w["role"], w["reason"] = "preferred", ("human_approved" if w["review"] else "best_eligible_donor")
            else:
                w["role"], w["reason"] = "alternate", ("pending_human_review" if w["pending"] else "eligible_not_best_for_target")
        targets.append(
            {
                "target_id": tid,
                "resolution": ("donor:" + top["g"]["group_id"]) if top else "platinum_native",
                "preferred": top["g"]["group_id"] if top else None,
                "alternates": [w["g"]["group_id"] for w in elig if w is not top],
            }
        )

    decisions = []
    for w in sorted(work, key=lambda w: w["g"]["group_id"]):
        g, s = w["g"], w["s"]
        decisions.append(
            {
                "group_id": g["group_id"],
                "target_id": g["target_id"],
                "subsystem": g["subsystem"],
                "source_id": g["source_id"],
                "curation_trace": {"recovered_ledger_member_counts": g["ledger_member_counts"], "status": "usable"},
                "asset_identity": {"unit": g["unit"], "member_count": g["member_count"], "member_digest": g["member_digest"], "sample_paths": g["sample_paths"]},
                "donor_class": g["donor_class"],
                "format_family": g["format_family"],
                "conversion_requirement": g["conversion_requirement"],
                "role": w["role"],
                "reason_code": w["reason"],
                "human_review": w["review"],
                "needs_evidence": w["reason"] == "needs_evidence",
                "needs_runtime_validation": s["needs_runtime_validation"] and w["role"] in ("preferred", "alternate"),
                "scores": {k: s[k] for k in ("visual_gain", "compat", "risk", "integration_cost", "independent_share")},
                "visual_evidence": {"native_relation": s["native_relation"], "risk_flags": s["risk_flags"], "detail": (w["ev"] or {}).get("detail")},
            }
        )
    return decisions, targets
