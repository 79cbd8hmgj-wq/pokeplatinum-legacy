#!/usr/bin/env python3
"""Build the source-agnostic visual donor asset catalog.

Current importers:
- Ranger Pokémon NCER frame census
- Ranger source-wide visual file/package inventory

Additional donor sources should be added as separate importer functions rather
than altering the normalized asset record contract.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


RANGER_SOURCE_ID = "ranger2"
HGSS_SOURCE_ID = "hgss"


def ranger_source_record(notes: str) -> dict:
    return {
        "source_id": RANGER_SOURCE_ID,
        "source_game": "Pokémon Ranger: Shadows of Almia",
        "source_repo": "79cbd8hmgj-wq/pokeranger2",
        "source_commit": None,
        "notes": notes,
    }


def ranger_frame_assets(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    assets = []
    for row in data.get("rows", []):
        species = row.get("species")
        if species in (None, 0):
            continue

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


def ranger_inventory_assets(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    assets = []
    for row in data.get("records", []):
        rel = row.get("source_path", "")
        category = row.get("category")
        safe = rel.replace("/", ":")
        assets.append(
            {
                "asset_id": f"{RANGER_SOURCE_ID}:source:{safe}",
                "source_id": RANGER_SOURCE_ID,
                "asset_type": row.get("asset_type", "visual_candidate_file"),
                "species_dex": None,
                "form": None,
                "variant": None,
                "group": category,
                "frame": None,
                "source_path": rel,
                "render_path": None,
                "native_width": None,
                "native_height": None,
                "bbox_width": None,
                "bbox_height": None,
                "opaque_pixels": None,
                "geometry_class": None,
                "review_status": row.get("review_status", "unreviewed"),
                "target_tags": row.get("target_tags", []),
                "quality_notes": (
                    "Source-level visual candidate. Internal resources may still "
                    "require extraction, decoding, or visual validation."
                ),
                "source_metadata": {
                    "category": category,
                    "size_bytes": row.get("size_bytes"),
                    "suffix": row.get("suffix"),
                    "signature": row.get("signature"),
                },
            }
        )
    return assets



def ranger_deep_assets(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    assets = []
    for row in data.get("embedded_resources", []):
        package_path = row.get("package_path", "")
        index = row.get("member_index")
        name = row.get("member_name")
        kind = row.get("member_kind")
        category = row.get("category")
        member_key = name or f"member_{int(index):04d}"
        safe_pkg = package_path.replace("/", ":")
        asset_id = f"{RANGER_SOURCE_ID}:embedded:{safe_pkg}:{member_key}"
        tags = list(row.get("package_target_tags", []))
        if kind in {"ncgr", "nclr", "ncer", "nanr", "nscr", "nsbmd", "nsbtx", "nsbca", "nsbta", "nsbtp", "nsbma"}:
            tags = sorted(set(tags + ["nitro_resource"]))
        assets.append(
            {
                "asset_id": asset_id,
                "source_id": RANGER_SOURCE_ID,
                "asset_type": "embedded_visual_resource",
                "species_dex": None,
                "form": None,
                "variant": None,
                "group": category,
                "frame": None,
                "source_path": package_path,
                "render_path": None,
                "native_width": None,
                "native_height": None,
                "bbox_width": None,
                "bbox_height": None,
                "opaque_pixels": None,
                "geometry_class": None,
                "review_status": row.get("review_status", "unreviewed"),
                "target_tags": tags,
                "quality_notes": (
                    "Embedded resource inventoried from a Ranger compressed visual package. "
                    "Not yet visually validated."
                ),
                "source_metadata": {
                    "member_index": index,
                    "member_name": name,
                    "member_kind": kind,
                    "member_size": row.get("member_size"),
                    "category": category,
                },
            }
        )
    return assets


def hgss_inventory_assets(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    assets = []
    for row in data.get("records", []):
        rel = row.get("source_path", "")
        category = row.get("category")
        safe = rel.replace("/", ":")
        assets.append(
            {
                "asset_id": f"{HGSS_SOURCE_ID}:source:{safe}",
                "source_id": HGSS_SOURCE_ID,
                "asset_type": row.get("asset_type", "visual_candidate_file"),
                "species_dex": None,
                "form": None,
                "variant": None,
                "group": category,
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
                    "HGSS source-backed visual asset. Deferred to cross-source bulk review."
                ),
                "source_metadata": {
                    "category": category,
                    "size_bytes": row.get("size_bytes"),
                    "suffix": row.get("suffix"),
                },
            }
        )
    return assets

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ranger-compatibility", type=Path)
    p.add_argument("--ranger-inventory", type=Path)
    p.add_argument("--ranger-deep-inventory", type=Path)
    p.add_argument("--hgss-inventory", type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", type=Path)
    args = p.parse_args()

    sources = []
    assets = []

    if args.hgss_inventory:
        sources.append(
            {
                "source_id": HGSS_SOURCE_ID,
                "source_game": "Pokemon HeartGold/SoulSilver",
                "source_repo": "79cbd8hmgj-wq/pokeheartgold",
                "source_commit": None,
                "notes": "Direct-donor extraction/catalog inventory. Bulk visual review deferred.",
            }
        )
        assets.extend(hgss_inventory_assets(args.hgss_inventory))

    if args.ranger_inventory:
        if not any(s.get("source_id") == RANGER_SOURCE_ID for s in sources):
            sources.append(
                ranger_source_record(
                    "Source-wide Ranger visual inventory plus Pokémon frame census where available."
                )
            )
        assets.extend(ranger_inventory_assets(args.ranger_inventory))

    if args.ranger_deep_inventory:
        if not any(s.get("source_id") == RANGER_SOURCE_ID for s in sources):
            sources.append(
                ranger_source_record(
                    "Ranger source-wide and embedded-resource inventory."
                )
            )
        assets.extend(ranger_deep_assets(args.ranger_deep_inventory))

    if args.ranger_compatibility:
        if not any(s.get("source_id") == RANGER_SOURCE_ID for s in sources):
            sources.append(
                ranger_source_record(
                    "Ranger frame catalog seeded from the NCER render compatibility census."
                )
            )
        assets.extend(ranger_frame_assets(args.ranger_compatibility))

    assets.sort(
        key=lambda a: (
            a["source_id"],
            a["species_dex"] if a["species_dex"] is not None else 999999,
            str(a["asset_type"]),
            str(a["variant"]),
            str(a["group"]),
            str(a["frame"]),
            str(a["source_path"]),
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
        by_type = {}
        by_group = {}
        for asset in assets:
            by_status[asset["review_status"]] = by_status.get(asset["review_status"], 0) + 1
            by_source[asset["source_id"]] = by_source.get(asset["source_id"], 0) + 1
            by_type[asset["asset_type"]] = by_type.get(asset["asset_type"], 0) + 1
            if asset.get("species_dex") is None:
                group = asset.get("group") or "unknown"
                by_group[group] = by_group.get(group, 0) + 1

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
            "### Asset types",
            "",
            "| Type | Assets |",
            "|---|---:|",
        ]
        for asset_type, count in sorted(by_type.items()):
            lines.append(f"| {asset_type} | {count} |")

        lines += [
            "",
            "### Ranger source categories",
            "",
            "| Category | Assets/files |",
            "|---|---:|",
        ]
        for group, count in sorted(by_group.items()):
            lines.append(f"| {group} | {count} |")

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
