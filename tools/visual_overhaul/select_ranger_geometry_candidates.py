#!/usr/bin/env python3
"""Create a geometry-only Ranger candidate shortlist for visual QA.

This tool does not decide semantic pose suitability. It ranks rendered cells only
by 80x80 geometry and preserves group/variant identity so later visual review can
determine whether a candidate is an idle/front-facing/battle-appropriate pose.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


CLASS_ORDER = {
    "fits": 0,
    "geometry_close": 1,
    "fits_small": 2,
    "oversize": 3,
    "blank": 4,
}


def score(row: dict) -> tuple:
    status = row.get("status", "blank")
    ratio = float(row.get("max_axis_ratio", 0.0))
    # Geometry-only preference:
    # 1) direct fit; 2) small correction; 3) undersized; 4) major reduction.
    # Within a class, prefer fuller use of the 80x80 envelope without overflow.
    if status == "geometry_close":
        size_metric = abs(ratio - 1.0)
    elif status == "oversize":
        size_metric = ratio
    else:
        size_metric = -ratio
    return (
        CLASS_ORDER.get(status, 99),
        size_metric,
        row.get("variant", 0),
        row.get("group") or "",
        row.get("file") or "",
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--compatibility-json", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    p.add_argument("--per-species", type=int, default=12)
    p.add_argument("--per-group", type=int, default=2)
    args = p.parse_args()

    source = json.loads(args.compatibility_json.read_text())
    by_species: dict[int, list[dict]] = defaultdict(list)
    for row in source.get("rows", []):
        species = row.get("species")
        if species is None or species == 0 or row.get("status") == "blank":
            continue
        by_species[int(species)].append(row)

    selections = []
    class_totals = defaultdict(int)

    for species in sorted(by_species):
        grouped: dict[str, list[dict]] = defaultdict(list)
        for row in by_species[species]:
            key = f"{row.get('variant', 0):02d}:{row.get('group') or '<none>'}"
            grouped[key].append(row)

        pool = []
        for key in sorted(grouped):
            ranked = sorted(grouped[key], key=score)
            pool.extend(ranked[: args.per_group])

        chosen = sorted(pool, key=score)[: args.per_species]
        for rank, row in enumerate(chosen, 1):
            class_totals[row["status"]] += 1
            selections.append(
                {
                    "species": species,
                    "rank": rank,
                    "variant": row.get("variant"),
                    "group": row.get("group"),
                    "file": row.get("file"),
                    "bbox_width": row.get("bbox_width"),
                    "bbox_height": row.get("bbox_height"),
                    "opaque_pixels": row.get("opaque_pixels"),
                    "max_axis_ratio": row.get("max_axis_ratio"),
                    "status": row.get("status"),
                }
            )

    species_count = len(by_species)
    payload = {
        "schema_version": 1,
        "policy": (
            "Geometry-only shortlist. Rank is not a semantic pose decision and "
            "must not be used as an automatic Platinum import ledger."
        ),
        "source_schema_version": source.get("schema_version"),
        "species_with_candidates": species_count,
        "per_species_limit": args.per_species,
        "per_group_limit": args.per_group,
        "candidate_count": len(selections),
        "class_totals": dict(sorted(class_totals.items())),
        "candidates": selections,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Ranger Geometry Candidate Shortlist",
        "",
        "This is a geometry-only visual-QA shortlist. It does **not** select final",
        "battle poses and does not infer Ranger animation-group semantics.",
        "",
        "## Summary",
        "",
        f"- Species represented: **{species_count}**",
        f"- Candidate cells: **{len(selections)}**",
        f"- Maximum candidates per species: **{args.per_species}**",
        f"- Maximum candidates retained per package/group before species ranking: **{args.per_group}**",
        "",
        "### Candidate geometry classes",
        "",
        "| Class | Candidates |",
        "|---|---:|",
    ]
    for key in ("fits", "geometry_close", "fits_small", "oversize"):
        lines.append(f"| {key} | {class_totals.get(key, 0)} |")

    lines.extend(
        [
            "",
            "## Review rule",
            "",
            "A high geometry rank means only that a cell is spatially convenient for an",
            "80x80 target. Final selection still requires visual review of pose, direction,",
            "animation role, completeness, and consistency with Platinum battle presentation.",
        ]
    )
    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")

    print(
        f"Shortlisted {len(selections)} geometry candidates across "
        f"{species_count} Ranger species."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
