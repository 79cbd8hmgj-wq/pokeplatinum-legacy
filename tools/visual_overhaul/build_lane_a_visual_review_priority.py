#!/usr/bin/env python3
"""Prioritize Lane A unique visual candidates for actual visual inspection.

This is an organizational/evidence pass only. It never changes review_status.
It uses source/type/species plus image geometry and color statistics to put the
highest-risk reconstruction candidates first and native source PNGs later.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def classify(candidate: dict) -> tuple[str, list[str]]:
    source = str(candidate.get("representative_source_id") or "")
    asset_type = str(candidate.get("representative_asset_type") or "")
    species = candidate.get("representative_species_dex")
    width = int(candidate.get("width") or 0)
    height = int(candidate.get("height") or 0)
    bbox = candidate.get("alpha_bbox")
    colors = candidate.get("unique_rgba_colors")
    reasons: list[str] = []

    if source == "ranger2" and asset_type == "pokemon_sprite_frame":
        reasons.append("Ranger frame reconstruction requires direct visual validation")
        if width > 96 or height > 96:
            reasons.append("canvas exceeds 96px review envelope")
        if bbox and len(bbox) == 4:
            bw = max(0, int(bbox[2]) - int(bbox[0]))
            bh = max(0, int(bbox[3]) - int(bbox[1]))
            if bw > 96 or bh > 96:
                reasons.append("occupied art exceeds 96px review envelope")
            if bw <= 8 or bh <= 8:
                reasons.append("very small occupied art")
        if colors is not None and int(colors) <= 2:
            reasons.append("very low color count")
        return "P1_ranger_species_render", reasons

    if species is not None:
        reasons.append("species-backed native/render-ready candidate")
        return "P2_other_species", reasons

    if asset_type == "source_png":
        reasons.append("native donor source PNG; reconstruction risk is low")
        return "P3_native_source_png", reasons

    reasons.append("render-ready non-species candidate")
    return "P4_other_render_ready", reasons


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--review-set", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    review = json.loads(args.review_set.read_text())
    records = []
    for c in review.get("candidates", []):
        priority, reasons = classify(c)
        records.append({
            "priority": priority,
            "visual_key": c.get("visual_key"),
            "asset_id": c.get("representative_asset_id"),
            "source_id": c.get("representative_source_id"),
            "asset_type": c.get("representative_asset_type"),
            "species_dex": c.get("representative_species_dex"),
            "group": c.get("representative_group"),
            "width": c.get("width"),
            "height": c.get("height"),
            "alpha_bbox": c.get("alpha_bbox"),
            "unique_rgba_colors": c.get("unique_rgba_colors"),
            "duplicate_count": c.get("duplicate_count"),
            "review_status": c.get("review_status"),
            "reasons": reasons,
        })

    order = {
        "P1_ranger_species_render": 0,
        "P2_other_species": 1,
        "P3_native_source_png": 2,
        "P4_other_render_ready": 3,
    }
    records.sort(key=lambda r: (
        order[r["priority"]],
        r["species_dex"] if r["species_dex"] is not None else 999999,
        str(r["source_id"]),
        str(r["group"]),
        str(r["asset_id"]),
    ))

    counts = Counter(r["priority"] for r in records)
    payload = {
        "schema_version": 1,
        "lane": "A_render_ready",
        "candidate_count": len(records),
        "priority_counts": dict(sorted(counts.items())),
        "rule": "Organizational priority only; no review_status changes.",
        "records": records,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane A Visual Review Priority",
        "",
        "Priority ordering for actual visual inspection of the unique Lane A candidates.",
        "This file does not change review status.",
        "",
        f"- Candidates prioritized: **{len(records)}**",
        "",
        "| Priority | Candidates | Meaning |",
        "|---|---:|---|",
        f"| P1_ranger_species_render | {counts.get('P1_ranger_species_render', 0)} | Ranger Pokémon frames; highest reconstruction-validation risk. |",
        f"| P2_other_species | {counts.get('P2_other_species', 0)} | Other species-backed candidates. |",
        f"| P3_native_source_png | {counts.get('P3_native_source_png', 0)} | Native donor PNGs; low reconstruction risk but still need visual/use review. |",
        f"| P4_other_render_ready | {counts.get('P4_other_render_ready', 0)} | Remaining render-ready non-species candidates. |",
        "",
        "## Boundary",
        "",
        "- Priority is not approval.",
        "- No candidate is marked valid_render, usable, alternate, or reject here.",
        "- Blank and decode-error decisions remain in LANE_A_REVIEW_DECISIONS.",
        "- Exact duplicates remain collapsed in the visual-review set.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")
    print("Priority counts:", dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
