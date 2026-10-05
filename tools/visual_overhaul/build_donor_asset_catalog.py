#!/usr/bin/env python3
"""Build the source-agnostic visual donor asset catalog.

Current importer: Pokémon Ranger: Shadows of Almia compatibility census.
Additional donor sources should be added as separate importer functions rather
than altering the normalized asset record contract.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


RANGER_SOURCE_ID = "ranger2"


def ranger_assets(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    assets = []
    for row in data.get("rows", []):
        species = row.get("species")
        if species in (None, 0):
            continue

        # Geometry alone never proves visual usability.
        status = "unreviewed"
        if row.get("status") == "blank":
            status = "reject"

        rel = row.get("file")
        asset_id = (
            f"{RANGER_SOURCE_ID}:pokemon:{int(species):03d}:"
            f"{int(row.get('variant') or 0):02d}:"
            f"{row.get('group') or 'unknown'}:"
            f"{Path(rel).stem if rel else 'unknown'}"
        )

        assets.append(
            {
                "asset_id": asset_id,
                "source_id": RANGER_SOURCE_ID,
                "asset_type": "pokemon_sprite_frame",
                "species_dex": int(species),
                "form": None,
                "variant": row.get("variant"),
                "group": row.get("group"),
                "frame": Path(rel).stem if rel else None,
                "source_path": rel or "",
                "render_path": rel,
                "native_width": row.get("canvas_width"),
                "native_height": row.get("canvas_height"),
                "bbox_width": row.get("bbox_width"),
                "bbox_height": row.get("bbox_height"),
                "opaque_pixels": row.get("opaque_pixels"),
                "geometry_class": row.get("status"),
                "review_status": status,
                "target_tags": [],
                "quality_notes": (
                    "Geometry metadata only; visual reconstruction and semantic "
                    "pose suitability are not yet approved."
                    if status == "unreviewed"
                    else "Blank rendered cell."
                ),
                "source_metadata": {
                    "measurement": data.get("measurement"),
                    "target_cell": data.get("target_cell"),
                    "bbox": row.get("bbox"),
                    "width_ratio": row.get("width_ratio"),
                    "height_ratio": row.get("height_ratio"),
                    "max_axis_ratio": row.get("max_axis_ratio"),
                },
            }
        )
    return assets


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ranger-compatibility", type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", type=Path)
    args = p.parse_args()

    sources = []
    assets = []

    if args.ranger_compatibility:
        sources.append(
            {
                "source_id": RANGER_SOURCE_ID,
                "source_game": "Pokémon Ranger: Shadows of Almia",
                "source_repo": "79cbd8hmgj-wq/pokeranger2",
                "source_commit": None,
                "notes": (
                    "Ranger frame catalog seeded from the NCER render compatibility "
                    "census. Entries remain unreviewed until visual decoder validation."
                ),
            }
        )
        assets.extend(ranger_assets(args.ranger_compatibility))

    assets.sort(
        key=lambda a: (
            a["source_id"],
            a["species_dex"] if a["species_dex"] is not None else 999999,
            str(a["variant"]),
            str(a["group"]),
            str(a["frame"]),
        )
    )

    payload = {
        "schema_version": 1,
        "sources": sources,
        "assets": assets,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    if args.write_md:
        by_status = {}
        by_source = {}
        for asset in assets:
            by_status[asset["review_status"]] = by_status.get(asset["review_status"], 0) + 1
            by_source[asset["source_id"]] = by_source.get(asset["source_id"], 0) + 1

        lines = [
            "# Donor Asset Catalog",
            "",
            "This catalog is an inventory/curation database only. It does not replace",
            "or modify Platinum graphics.",
            "",
            "## Summary",
            "",
            f"- Sources: **{len(sources)}**",
            f"- Assets: **{len(assets)}**",
            "",
            "### Assets by source",
            "",
            "| Source | Assets |",
            "|---|---:|",
        ]
        for source_id, count in sorted(by_source.items()):
            lines.append(f"| {source_id} | {count} |")

        lines += [
            "",
            "### Review status",
            "",
            "| Status | Assets |",
            "|---|---:|",
        ]
        for status, count in sorted(by_status.items()):
            lines.append(f"| {status} | {count} |")

        args.write_md.parent.mkdir(parents=True, exist_ok=True)
        args.write_md.write_text("\n".join(lines) + "\n")

    print(f"Cataloged {len(assets)} assets from {len(sources)} source(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
