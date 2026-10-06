#!/usr/bin/env python3
"""Resolve Lane B decode issues with source-native PNG equivalents.

For recovery records classified as source_png_equivalent, require a matching
Lane A P3 native PNG decision from the same source/path. If that PNG is curated
usable, the raw sibling visual resource is recovered as usable donor material.

This does not choose preferred donors or modify Platinum resources.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recovery", required=True, type=Path)
    ap.add_argument("--p3-curation", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    recovery = json.loads(args.recovery.read_text())
    p3 = json.loads(args.p3_curation.read_text())

    png_by_path = {
        (d.get("source_id"), d.get("source_path")): d
        for d in p3.get("decisions", [])
    }

    targets = [
        r for r in recovery.get("records", [])
        if r.get("recovery_route") == "source_png_equivalent"
    ]
    decisions = []
    for r in targets:
        png_path = r.get("source_png_equivalent")
        match = png_by_path.get((r.get("source_id"), png_path))
        if match and match.get("review_status") == "usable":
            status = "usable"
            code = "source_native_png_equivalent"
            reason = (
                "Source resource has a same-source, same-stem native PNG sibling that "
                "was independently curated usable in Lane A P3."
            )
        else:
            status = "decode_issue"
            code = "source_png_equivalent_unresolved"
            reason = (
                "A same-stem PNG sibling was found, but no matching usable Lane A P3 "
                "decision could be proven."
            )
        decisions.append({
            "asset_id": r["asset_id"],
            "source_id": r.get("source_id"),
            "asset_type": r.get("asset_type"),
            "group": r.get("group"),
            "source_path": r.get("source_path"),
            "source_png_equivalent": png_path,
            "matched_p3_asset_id": match.get("asset_id") if match else None,
            "review_status": status,
            "reason_code": code,
            "reason": reason,
        })

    if len(decisions) != 76:
        raise SystemExit(f"source-PNG recovery coverage mismatch: {len(decisions)} != 76")
    ids = [d["asset_id"] for d in decisions]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate source-PNG recovery decision")

    counts = Counter(d["review_status"] for d in decisions)
    payload = {
        "schema_version": 1,
        "lane": "B_pokemon_facing",
        "recovery_route": "source_png_equivalent",
        "asset_count": len(decisions),
        "status_counts": dict(sorted(counts.items())),
        "decisions": decisions,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane B Source-PNG Recovery",
        "",
        "Recovery decisions for Lane B resources with source-native PNG equivalents.",
        "No Platinum resources are modified.",
        "",
        f"- Assets checked: **{len(decisions)}**",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: **{count}**")
    lines += [
        "",
        "## Evidence rule",
        "",
        "- Same source and same-stem native PNG sibling must exist.",
        "- The sibling PNG must already be curated usable in Lane A P3.",
        "- Recovered resource is usable donor material, but is not selected as preferred.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")
    print("Source-PNG recovery:", len(decisions), dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
