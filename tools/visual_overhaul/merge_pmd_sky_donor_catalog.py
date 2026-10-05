#!/usr/bin/env python3
"""Merge a PMD Sky source inventory into the existing donor asset catalog.

This preserves all existing catalog sources/assets and replaces only the pmd_sky
slice so the operation is idempotent.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

SOURCE_ID = "pmd_sky"


def normalize(row: dict) -> dict:
    rel = row.get("source_path", "")
    return {
        "asset_id": f"{SOURCE_ID}:source:{rel.replace('/', ':')}",
        "source_id": SOURCE_ID,
        "asset_type": row.get("asset_type", "visual_candidate_file"),
        "species_dex": None,
        "form": None,
        "variant": None,
        "group": row.get("category"),
        "frame": None,
        "source_path": rel,
        "render_path": rel if row.get("asset_type") == "source_png" else None,
        "native_width": None,
        "native_height": None,
        "bbox_width": None,
        "bbox_height": None,
        "opaque_pixels": None,
        "geometry_class": None,
        "review_status": row.get("review_status", "unreviewed"),
        "target_tags": row.get("target_tags", []),
        "quality_notes": (
            "PMD Sky source-backed visual candidate. Deferred to cross-source bulk review."
        ),
        "source_metadata": {
            "category": row.get("category"),
            "size_bytes": row.get("size_bytes"),
            "suffix": row.get("suffix"),
        },
    }


def write_markdown(path: Path, sources: list[dict], assets: list[dict]) -> None:
    by_source = Counter(a["source_id"] for a in assets)
    by_type = Counter(a["asset_type"] for a in assets)
    by_status = Counter(a["review_status"] for a in assets)
    by_group = Counter((a.get("group") or "unknown") for a in assets if a.get("species_dex") is None)

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

    lines += ["", "### Asset types", "", "| Type | Assets |", "|---|---:|"]
    for kind, count in sorted(by_type.items()):
        lines.append(f"| {kind} | {count} |")

    lines += ["", "### Source categories", "", "| Category | Assets/files |", "|---|---:|"]
    for group, count in sorted(by_group.items()):
        lines.append(f"| {group} | {count} |")

    lines += ["", "### Review status", "", "| Status | Assets |", "|---|---:|"]
    for status, count in sorted(by_status.items()):
        lines.append(f"| {status} | {count} |")

    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog-json", required=True, type=Path)
    p.add_argument("--catalog-md", required=True, type=Path)
    p.add_argument("--pmd-sky-inventory", required=True, type=Path)
    args = p.parse_args()

    catalog = json.loads(args.catalog_json.read_text())
    inventory = json.loads(args.pmd_sky_inventory.read_text())

    sources = [s for s in catalog.get("sources", []) if s.get("source_id") != SOURCE_ID]
    assets = [a for a in catalog.get("assets", []) if a.get("source_id") != SOURCE_ID]

    sources.append({
        "source_id": SOURCE_ID,
        "source_game": "Pokémon Mystery Dungeon: Explorers of Sky",
        "source_repo": "79cbd8hmgj-wq/pmd-sky",
        "source_commit": None,
        "notes": "Effects/reference donor inventory. Bulk visual review deferred.",
    })
    assets.extend(normalize(row) for row in inventory.get("records", []))

    assets.sort(key=lambda a: (
        a["source_id"],
        a["species_dex"] if a["species_dex"] is not None else 999999,
        str(a["asset_type"]),
        str(a["variant"]),
        str(a["group"]),
        str(a["frame"]),
        str(a["source_path"]),
    ))

    ids = [a["asset_id"] for a in assets]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate asset_id after PMD Sky merge")
    if sum(1 for s in sources if s.get("source_id") == SOURCE_ID) != 1:
        raise RuntimeError("Expected exactly one PMD Sky source record")

    catalog["sources"] = sources
    catalog["assets"] = assets
    args.catalog_json.write_text(json.dumps(catalog, indent=2) + "\n")
    write_markdown(args.catalog_md, sources, assets)

    print(f"Merged {len(inventory.get('records', []))} PMD Sky assets; catalog now has {len(assets)} assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
