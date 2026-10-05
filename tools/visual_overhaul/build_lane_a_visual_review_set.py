#!/usr/bin/env python3
"""Build the Lane A visual-review candidate set from render-integrity evidence.

This is a deduplication/triage pass only. It does not change donor review_status
or choose a preferred donor asset. Exact pixel duplicates are collapsed to one
technical representative while every duplicate member remains recorded.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


SOURCE_ORDER = {"hgss": 0, "diamond": 1, "ranger2": 2, "pmd_sky": 3}


def representative_key(row: dict) -> tuple:
    # Representative choice is strictly deterministic bookkeeping.
    # It does not express preference or usability.
    return (
        SOURCE_ORDER.get(str(row.get("source_id")), 99),
        str(row.get("asset_type") or ""),
        str(row.get("asset_id") or ""),
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--integrity", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    p.add_argument("--write-decode-json", required=True, type=Path)
    p.add_argument("--write-blank-json", required=True, type=Path)
    args = p.parse_args()

    audit = json.loads(args.integrity.read_text())
    rows = audit.get("records", [])

    nonblank = [r for r in rows if r.get("technical_state") == "verified_nonblank"]
    decode = [r for r in rows if r.get("technical_state") == "decode_error"]
    blanks = [r for r in rows if r.get("technical_state") == "blank"]

    by_hash: dict[str, list[dict]] = defaultdict(list)
    for row in nonblank:
        h = row.get("pixel_sha256")
        if not h:
            raise RuntimeError(f"Nonblank row lacks pixel hash: {row.get('asset_id')}")
        by_hash[h].append(row)

    representatives = []
    duplicate_sets = []
    for h, members in sorted(by_hash.items()):
        members = sorted(members, key=representative_key)
        rep = members[0]
        representatives.append({
            "visual_key": h,
            "representative_asset_id": rep.get("asset_id"),
            "representative_source_id": rep.get("source_id"),
            "representative_asset_type": rep.get("asset_type"),
            "representative_species_dex": rep.get("species_dex"),
            "representative_group": rep.get("group"),
            "representative_materialized_path": rep.get("materialized_path"),
            "logical_group": rep.get("logical_group"),
            "width": rep.get("width"),
            "height": rep.get("height"),
            "alpha_bbox": rep.get("alpha_bbox"),
            "unique_rgba_colors": rep.get("unique_rgba_colors"),
            "duplicate_count": len(members),
            "member_asset_ids": [m.get("asset_id") for m in members],
            "member_source_ids": [m.get("source_id") for m in members],
            "review_status": rep.get("review_status"),
        })
        if len(members) > 1:
            duplicate_sets.append({
                "visual_key": h,
                "representative_asset_id": rep.get("asset_id"),
                "count": len(members),
                "member_asset_ids": [m.get("asset_id") for m in members],
                "member_source_ids": [m.get("source_id") for m in members],
            })

    representatives.sort(
        key=lambda r: (
            r.get("representative_species_dex") if r.get("representative_species_dex") is not None else 999999,
            str(r.get("logical_group") or ""),
            SOURCE_ORDER.get(str(r.get("representative_source_id")), 99),
            str(r.get("representative_asset_id") or ""),
        )
    )

    source_counts = Counter(r.get("representative_source_id") for r in representatives)
    species_counts = Counter(
        r.get("representative_species_dex")
        for r in representatives
        if r.get("representative_species_dex") is not None
    )
    payload = {
        "schema_version": 1,
        "source_integrity_report": str(args.integrity),
        "lane": "A_render_ready",
        "audited_assets": len(rows),
        "nonblank_assets": len(nonblank),
        "unique_visual_candidates": len(representatives),
        "redundant_exact_duplicate_assets": len(nonblank) - len(representatives),
        "exact_duplicate_sets": len(duplicate_sets),
        "decode_error_assets": len(decode),
        "blank_assets": len(blanks),
        "representative_source_counts": dict(sorted(source_counts.items())),
        "species_with_candidates": len(species_counts),
        "duplicate_sets": duplicate_sets,
        "candidates": representatives,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")
    args.write_decode_json.write_text(json.dumps({
        "schema_version": 1,
        "lane": "A_render_ready",
        "count": len(decode),
        "records": decode,
    }, indent=2) + "\n")
    args.write_blank_json.write_text(json.dumps({
        "schema_version": 1,
        "lane": "A_render_ready",
        "count": len(blanks),
        "records": blanks,
    }, indent=2) + "\n")

    lines = [
        "# Lane A Visual Review Candidate Set",
        "",
        "This pass collapses exact pixel duplicates after the full render-integrity audit.",
        "It does not change donor review status or select a preferred donor.",
        "",
        "## Summary",
        "",
        f"- Audited Lane A assets: **{len(rows)}**",
        f"- Verified nonblank assets: **{len(nonblank)}**",
        f"- Unique visual candidates after exact deduplication: **{len(representatives)}**",
        f"- Redundant exact-duplicate assets removed from direct visual review: **{len(nonblank) - len(representatives)}**",
        f"- Exact duplicate sets: **{len(duplicate_sets)}**",
        f"- Decode-error assets isolated: **{len(decode)}**",
        f"- Blank assets isolated: **{len(blanks)}**",
        f"- Species represented among candidate records: **{len(species_counts)}**",
        "",
        "## Candidate representatives by source",
        "",
        "| Source | Unique visual representatives |",
        "|---|---:|",
    ]
    for source, count in sorted(source_counts.items()):
        lines.append(f"| {source} | {count} |")

    lines += [
        "",
        "## Review boundary",
        "",
        "- A representative is only a bookkeeping stand-in for identical pixels.",
        "- Every duplicate member remains recorded in the JSON.",
        "- Exact duplicates are not automatically marked alternate or reject.",
        "- Decode errors remain separate until format-specific handling is added.",
        "- Blank renders remain separate evidence and are not promoted.",
        "- No Platinum resource is modified by this pass.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")

    print("Audited assets:", len(rows))
    print("Unique visual candidates:", len(representatives))
    print("Redundant exact duplicates:", len(nonblank) - len(representatives))
    print("Decode errors:", len(decode))
    print("Blanks:", len(blanks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
