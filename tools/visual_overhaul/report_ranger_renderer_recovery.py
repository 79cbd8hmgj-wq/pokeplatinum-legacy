#!/usr/bin/env python3
"""Compare two Lane A P1 ledgers (before/after a Ranger renderer fix).

Outputs a compact JSON: how many previously-unresolved (decode_issue) P1
candidates are now valid_render, at candidate level and at asset level
(every exact-duplicate member counted).  Pure bookkeeping; changes no status.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def per_asset(ledger: dict) -> dict[str, str]:
    out = {}
    for rec in ledger["records"]:
        for member in rec["duplicate_member_asset_ids"]:
            out[member] = rec["review_status"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True, type=Path)
    ap.add_argument("--after", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    args = ap.parse_args()
    before = json.loads(args.before.read_text())
    after = json.loads(args.after.read_text())
    b_asset, a_asset = per_asset(before), per_asset(after)

    # Candidate level: each previous record's representative asset, looked up in the new ledger.
    cand = Counter()
    for rec in before["records"]:
        cand[(rec["review_status"], a_asset.get(rec["asset_id"], "no_longer_a_p1_asset"))] += 1
    # Asset level: every duplicate member.
    asset = Counter()
    for a, st in b_asset.items():
        asset[(st, a_asset.get(a, "no_longer_a_p1_asset"))] += 1
    newly = sorted(set(a_asset) - set(b_asset))

    def fmt(c):
        return {f"{k[0]} -> {k[1]}": v for k, v in sorted(c.items())}

    out = {
        "schema_version": 1,
        "before_status_counts": before["status_counts"],
        "after_status_counts": after["status_counts"],
        "candidate_level_transitions": fmt(cand),
        "asset_level_transitions": fmt(asset),
        "assets_new_to_p1_ledger": len(newly),
        "previous_decode_issue_candidates": before["status_counts"].get("decode_issue", 0),
        "previous_decode_issue_now_valid_render_candidates": cand[("decode_issue", "valid_render")],
        "previous_decode_issue_assets": sum(v for k, v in asset.items() if k[0] == "decode_issue"),
        "previous_decode_issue_now_valid_render_assets": asset[("decode_issue", "valid_render")],
    }
    args.write_json.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if "transitions" not in k}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
