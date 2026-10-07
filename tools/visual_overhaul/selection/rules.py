"""Selection decision engine. Implements SELECTION_RULES.json exactly (rules_version 1.0)."""
from __future__ import annotations

from common import *  # noqa: F401,F403


def risk_bump(level: str, n: int, order) -> str:
    return order[min(order.index(level) + n, len(order) - 1)]


def score_group(g: dict, ev: dict | None, rules: dict, sub: dict) -> dict:
    relation = (ev or {}).get("native_relation", "unmeasured")
    gain = rules["native_relation_to_gain"].get(relation)
    conv = g["conversion_requirement"]
    needs_rt = relation in rules["runtime_validation_relations"]
    order = rules["risk_order"]
    risk = rules["base_risk_by_conversion"][conv]
    bumps = int(needs_rt) + int(g["unresolved_decode_issue_members"] > 0)
    risk = risk_bump(risk, bumps, order)
    share = g["independent_member_count"] / g["member_count"]
    return {
        "native_relation": relation,
        "visual_gain": gain,
        "compat": rules["compat_score_by_conversion"][conv],
        "risk": risk,
        "integration_cost": sub["integration_cost"] + rules["conversion_scale"][conv],
        "independent_share": round(share, 4),
        "needs_runtime_validation": needs_rt,
    }


def initial_role(g: dict, s: dict, rules: dict) -> tuple[str, str]:
    th = rules["thresholds"]
    order = rules["risk_order"]
    cls = g["donor_class"]
    rel = s["native_relation"]
    gain = s["visual_gain"]
    if s["independent_share"] < th["min_independent_share"]:
        return "not_selected", "no_independent_evidence"
    if cls == "none":
        return "not_selected", "source_not_relevant_to_subsystem"
    if cls in ("technique", "reference") or g["conversion_requirement"] == "not_portable":
        return "reference_only", "policy_reference_class"
    if cls == "control":
        if rel in ("identical", "content_match_native"):
            return "not_selected", "identical_to_native"
        if rel == "unmeasured":
            return "reference_only", "needs_evidence"
        return "reference_only", "control_differs_from_native"
    # direct / convertible
    if gain == 0:
        return "not_selected", "identical_to_native"
    if gain is None:
        return "reference_only", "needs_evidence"
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


def decide(groups: list[dict], evidence: dict, rules: dict, subs: dict) -> tuple[list[dict], list[dict]]:
    """groups: all candidate groups of ONE subsystem. Returns (decisions, targets)."""
    entries = evidence.get("entries", {})
    work = []
    for g in groups:
        sub = subs[g["subsystem"]]
        ev = entries.get(g["group_id"])
        s = score_group(g, ev, rules, sub)
        role, reason = initial_role(g, s, rules)
        work.append({"g": g, "s": s, "role": role, "reason": reason, "ev": ev})

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
                w["role"], w["reason"] = "preferred", "best_eligible_donor"
            else:
                w["role"], w["reason"] = "alternate", "eligible_not_best_for_target"
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
                "needs_evidence": w["reason"] == "needs_evidence",
                "needs_runtime_validation": s["needs_runtime_validation"] and w["role"] in ("preferred", "alternate"),
                "scores": {k: s[k] for k in ("visual_gain", "compat", "risk", "integration_cost", "independent_share")},
                "visual_evidence": {"native_relation": s["native_relation"], "detail": (w["ev"] or {}).get("detail")},
            }
        )
    return decisions, targets
