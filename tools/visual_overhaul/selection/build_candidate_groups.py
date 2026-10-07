#!/usr/bin/env python3
"""Derive donor candidate groups from the authoritative recovered curation ledgers.

Reads only the three recovered ledgers (+ SUBSYSTEMS.json / SELECTION_RULES.json).
Groups = (subsystem, source, unit). Every `usable` record lands in exactly one group.
`decision_issue` records that map into a group are counted as blockers, never selected.
Output: docs/visual_overhaul/selection/CANDIDATE_GROUPS.json (+ .md summary).
"""
from __future__ import annotations

import argparse
import collections
import sys

from common import *  # noqa: F401,F403
import mapping


def build(want_membership: bool = False) -> dict:
    subs = jload(SUBSYSTEMS_JSON)["subsystems"]
    rules = jload(RULES_JSON)
    weak = set(rules["weak_reason_codes"])
    recs = load_recovered_records()
    status = jload(STATUS_JSON)

    groups: dict[str, dict] = {}
    unresolved_by_group: dict[str, int] = collections.Counter()
    usable_seen = 0
    membership: dict[str, str] = {}
    for aid, r in recs.items():
        st = r["review_status"]
        if st == "reject":
            continue
        try:
            c = mapping.classify(r)
        except KeyError:
            if st == "usable":
                raise  # usable records must always map
            unresolved_by_group["unmapped/" + r["source_id"]] += 1
            continue
        gid = f"{c['subsystem']}/{r['source_id']}/{c['unit']}"
        if st == "decode_issue":
            unresolved_by_group[gid] += 1
            continue
        usable_seen += 1
        g = groups.get(gid)
        if g is None:
            role = subs[c["subsystem"]]["source_roles"].get(r["source_id"])
            g = groups[gid] = {
                "group_id": gid,
                "subsystem": c["subsystem"],
                "target_id": c["target_id"],
                "source_id": r["source_id"],
                "unit": c["unit"],
                "unit_kind": c["unit_kind"],
                "_ids": [],
                "_atypes": collections.Counter(),
                "_reasons": collections.Counter(),
                "_weak": 0,
                "_ledgers": collections.Counter(),
                "_paths": [],
                "role_defined": role is not None,
            }
        g["_ids"].append(aid)
        g["_ledgers"][r["_ledger"]] += 1
        if want_membership:
            membership[aid] = gid
        g["_atypes"][r["asset_type"]] += 1
        g["_reasons"][r["reason_code"]] += 1
        if r["reason_code"] in weak:
            g["_weak"] += 1
        if len(g["_paths"]) < 3:
            g["_paths"].append(r["source_path"])

    out_groups = []
    missing_roles = collections.Counter()
    for gid in sorted(groups):
        g = groups[gid]
        ids = g.pop("_ids")
        n = len(ids)
        weak_n = g.pop("_weak")
        sub = subs[g["subsystem"]]
        role = sub["source_roles"].get(g["source_id"])
        if role is None:
            missing_roles[(g["subsystem"], g["source_id"])] += n
            role = {"class": "none", "format_family": "unknown", "conversion": "not_portable", "rationale": "no source role defined"}
        # conversion may be overridden per asset type; take the worst (highest) across members
        scale = rules["conversion_scale"]
        conv = max(
            (role.get("by_asset_type", {}).get(at, role["conversion"]) for at in g["_atypes"]),
            key=lambda c: scale[c],
        )
        g.update(
            {
                "member_count": n,
                "member_digest": digest_ids(ids),
                "independent_member_count": n - weak_n,
                "asset_type_counts": dict(sorted(g.pop("_atypes").items())),
                "reason_code_counts": dict(sorted(g.pop("_reasons").items())),
                "sample_paths": g.pop("_paths"),
                "donor_class": role["class"],
                "format_family": role["format_family"],
                "conversion_requirement": conv,
                "ledger_member_counts": dict(sorted(g.pop("_ledgers").items())),
                "unresolved_decode_issue_members": unresolved_by_group.get(gid, 0),
            }
        )
        del g["role_defined"]
        out_groups.append(g)

    targets: dict[str, dict] = {}
    for g in out_groups:
        t = targets.setdefault(g["target_id"], {"target_id": g["target_id"], "subsystem": g["subsystem"], "groups": []})
        t["groups"].append(g["group_id"])
    sub_counts = collections.Counter(g["subsystem"] for g in out_groups)
    # unresolved groups with no usable counterpart
    orphan_unresolved = {k: v for k, v in unresolved_by_group.items() if k not in groups}
    doc = {
        "schema_version": 1,
        "inputs": {
            "recovered_ledger_sha256": ledger_hashes(),
            "subsystems_sha256": file_sha256(SUBSYSTEMS_JSON),
            "alignment_sha256": file_sha256(SEL / "alignment" / "trainer_classes.json"),
            "rules_version": rules["rules_version"],
            "curation_status": {"usable": status["status_totals"]["usable"] if "status_totals" in status else None},
        },
        "totals": {
            "usable_records_grouped": usable_seen,
            "groups": len(out_groups),
            "targets": len(targets),
            "groups_by_subsystem": dict(sorted(sub_counts.items())),
            "members_by_subsystem": dict(
                sorted(collections.Counter({s: sum(g["member_count"] for g in out_groups if g["subsystem"] == s) for s in sub_counts}).items())
            ),
            "records_with_undefined_source_role": sum(missing_roles.values()),
            "unresolved_decode_issue_in_unit": sum(unresolved_by_group.values()),
            "unresolved_decode_issue_without_usable_unit": sum(orphan_unresolved.values()),
        },
        "undefined_source_roles": {f"{a}|{b}": n for (a, b), n in sorted(missing_roles.items())},
        "groups": out_groups,
    }
    if want_membership:
        doc["_membership"] = membership
    return doc


def write_md(doc: dict) -> None:
    t = doc["totals"]
    lines = [
        "# Donor Candidate Groups",
        "",
        "Generated by `tools/visual_overhaul/selection/build_candidate_groups.py` from the recovered curation ledgers.",
        "No Platinum resource is modified.",
        "",
        f"- usable records grouped: **{t['usable_records_grouped']}**",
        f"- candidate groups: **{t['groups']}**",
        f"- targets: **{t['targets']}**",
        f"- unresolved decode_issue records mapping into a unit: **{t['unresolved_decode_issue_in_unit']}** "
        f"(of which with no usable unit: {t['unresolved_decode_issue_without_usable_unit']})",
        f"- usable records with undefined source role: **{t['records_with_undefined_source_role']}**",
        "",
        "| Subsystem | Groups | Members |",
        "|---|---:|---:|",
    ]
    for s, n in t["groups_by_subsystem"].items():
        lines.append(f"| {s} | {n} | {t['members_by_subsystem'][s]} |")
    (SEL / "CANDIDATE_GROUPS.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if committed CANDIDATE_GROUPS.json differs from a fresh derivation")
    a = ap.parse_args()
    doc = build()
    if a.check:
        old = jload(GROUPS_JSON)
        if old != doc:
            print("CANDIDATE_GROUPS.json is stale", file=sys.stderr)
            return 1
        print("CANDIDATE_GROUPS.json up to date")
        return 0
    jdump(GROUPS_JSON, doc)
    write_md(doc)
    print(json.dumps(doc["totals"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
