#!/usr/bin/env python3
"""Validate the donor selection pipeline end to end. Exit 1 on any violation.

Checks (see SELECTION_SCHEMA.md): recovered-ledger coverage, group reproducibility and exclusivity,
ledger reproducibility from rules+evidence, no duplicate/conflicting decisions, one preferred per
target, selected groups trace to usable recovered records, evidence binding, queue freshness.
"""
from __future__ import annotations

import argparse
import sys

from common import *  # noqa: F401,F403
import build_candidate_groups
import select_subsystem

def validate(sel_dir: Path | None = None, quiet: bool = False) -> list[str]:
    errs: list[str] = []
    rules = jload(RULES_JSON)
    roles = set(rules["roles"])
    reasons = set(rules["reason_codes"])
    subs = jload(SUBSYSTEMS_JSON)["subsystems"]
    status = jload(STATUS_JSON)

    # V1/V2: groups reproducible from the recovered ledgers, full coverage
    fresh = build_candidate_groups.build(want_membership=True)
    membership = fresh.pop("_membership")
    committed = jload(GROUPS_JSON)
    if committed != fresh:
        errs.append("CANDIDATE_GROUPS.json is not reproducible from the recovered ledgers")
    usable = status["status_totals"]["usable"]
    if fresh["totals"]["usable_records_grouped"] != usable or len(membership) != usable:
        errs.append(f"usable coverage mismatch: grouped {len(membership)} vs curation status {usable}")
    gid_seen = set()
    groups = {}
    for g in committed["groups"]:
        if g["group_id"] in gid_seen:
            errs.append(f"duplicate group id {g['group_id']}")
        gid_seen.add(g["group_id"])
        groups[g["group_id"]] = g
        if g["subsystem"] not in subs:
            errs.append(f"{g['group_id']}: unknown subsystem")
    if committed["totals"]["records_with_undefined_source_role"]:
        errs.append("usable records with undefined source role")

    # V4: per-subsystem ledgers
    ledgers_dir = SEL / "ledgers"
    for lp in sorted(ledgers_dir.glob("*.json")):
        led = jload(lp)
        sname = led.get("subsystem")
        tag = lp.name
        if sname != lp.stem or sname not in subs:
            errs.append(f"{tag}: subsystem name mismatch")
            continue
        if led.get("rules_version") != rules["rules_version"]:
            errs.append(f"{tag}: rules_version {led.get('rules_version')} != {rules['rules_version']}")
        sgroups = [g for g in committed["groups"] if g["subsystem"] == sname]
        if led["inputs"]["subsystem_groups_digest"] != subsystem_groups_digest(sgroups):
            errs.append(f"{tag}: stale vs candidate groups (digest)")
        if led["inputs"]["recovered_ledger_sha256"] != ledger_hashes():
            errs.append(f"{tag}: stale vs recovered curation ledgers")
        if led["inputs"]["rules_sha256"] != file_sha256(RULES_JSON) or led["inputs"]["subsystems_sha256"] != file_sha256(SUBSYSTEMS_JSON):
            errs.append(f"{tag}: stale vs rules/subsystems")
        # evidence binding
        ev = {"entries": {}}
        if led["inputs"]["evidence_file"]:
            ep = ROOT / led["inputs"]["evidence_file"]
            if not ep.is_file() or file_sha256(ep) != led["inputs"]["evidence_sha256"]:
                errs.append(f"{tag}: evidence file missing or hash mismatch")
            else:
                ev = jload(ep)
                for gid, e in ev["entries"].items():
                    g = groups.get(gid)
                    if g is None or g["member_digest"] != e.get("member_digest"):
                        errs.append(f"{tag}: evidence entry {gid} does not bind to current group digest")
        # completeness, duplicates, per-decision integrity
        dec_ids = [d["group_id"] for d in led["decisions"]]
        if len(dec_ids) != len(set(dec_ids)):
            errs.append(f"{tag}: duplicate decisions for a group")
        if set(dec_ids) != {g["group_id"] for g in sgroups}:
            errs.append(f"{tag}: decisions do not cover exactly the subsystem's groups")
        tmap = {t["target_id"]: t for t in led["targets"]}
        pref_per_target: dict[str, list[str]] = {}
        for d in led["decisions"]:
            g = groups.get(d["group_id"])
            if g is None:
                errs.append(f"{tag}: decision for unknown group {d['group_id']}")
                continue
            if d["role"] not in roles:
                errs.append(f"{tag}: bad role {d['role']}")
            if d["reason_code"] not in reasons:
                errs.append(f"{tag}: bad reason {d['reason_code']}")
            if d["target_id"] != g["target_id"] or d["source_id"] != g["source_id"]:
                errs.append(f"{tag}: {d['group_id']} identity mismatch")
            if d["asset_identity"]["member_digest"] != g["member_digest"]:
                errs.append(f"{tag}: {d['group_id']} member digest drifted")
            if d["role"] in ("preferred", "alternate"):
                sc = d["scores"]
                if g["donor_class"] not in ("direct", "convertible"):
                    errs.append(f"{tag}: {d['group_id']} selected with class {g['donor_class']}")
                if sc["visual_gain"] is None or sc["visual_gain"] < rules["thresholds"]["alternate_min_gain"]:
                    errs.append(f"{tag}: {d['group_id']} selected without measured visual gain")
                if sc["independent_share"] < rules["thresholds"]["selection_min_independent_share"]:
                    errs.append(f"{tag}: {d['group_id']} selected with weak independent evidence")
                if g["unresolved_decode_issue_members"] and d["role"] == "preferred":
                    errs.append(f"{tag}: {d['group_id']} preferred while unit has unresolved decode_issue members")
                if not d["curation_trace"]["recovered_ledger_member_counts"]:
                    errs.append(f"{tag}: {d['group_id']} lacks curation trace")
            if d["role"] == "preferred":
                pref_per_target.setdefault(d["target_id"], []).append(d["group_id"])
        for tid, lst in pref_per_target.items():
            if len(lst) > 1:
                errs.append(f"{tag}: target {tid} has {len(lst)} preferred groups")
        for t in led["targets"]:
            want = pref_per_target.get(t["target_id"], [])
            if (t["preferred"] or None) != (want[0] if want else None):
                errs.append(f"{tag}: target {t['target_id']} preferred pointer inconsistent")
            exp_res = ("donor:" + t["preferred"]) if t["preferred"] else "platinum_native"
            if t["resolution"] != exp_res:
                errs.append(f"{tag}: target {t['target_id']} resolution inconsistent")
        if set(tmap) != {g["target_id"] for g in sgroups}:
            errs.append(f"{tag}: targets do not cover subsystem targets")
        # reproducibility: re-derive from rules+evidence
        fresh_led = select_subsystem.derive(sname)
        if fresh_led != led:
            errs.append(f"{tag}: not reproducible from current rules/evidence/groups")
    # asset exclusivity across selected groups follows from group exclusivity; verify group membership is a function
    # (membership dict maps each asset to exactly one group by construction; compare counts)
    if sum(g["member_count"] for g in committed["groups"]) != len(membership):
        errs.append("group member counts do not sum to unique assets (an asset is in two groups)")

    # V7: queue/status freshness
    try:
        import build_queue
        qfresh = build_queue.derive()
        qp = SEL / "IMPLEMENTATION_QUEUE.json"
        if qp.is_file() and jload(qp) != qfresh:
            errs.append("IMPLEMENTATION_QUEUE.json is stale")
    except ImportError:
        pass
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    a = ap.parse_args()
    errs = validate()
    if errs:
        for e in errs[:50]:
            print("FAIL:", e, file=sys.stderr)
        print(f"{len(errs)} violation(s)", file=sys.stderr)
        return 1
    print("selection validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
