#!/usr/bin/env python3
"""Build deterministic cross-source review queues from DONOR_ASSET_CATALOG.json.

This tool does not modify catalog review statuses and does not choose replacement
winners. It only groups existing donor records into practical review batches.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


POKEMON_TAGS = {
    "battle_front", "battle_back", "battle_animation_frame",
    "party_icon", "summary_icon", "overworld", "portrait", "trainer", "pokemon",
}
EFFECT_TAGS = {
    "effect", "field_effect", "battle_animation_frame", "transition", "animation",
}
ENV_UI_TAGS = {
    "environment", "background", "tile", "palette", "ui", "cursor", "frame",
    "icon", "title", "scene",
}


def lane_for(asset: dict) -> str:
    tags = set(asset.get("target_tags") or [])
    asset_type = str(asset.get("asset_type") or "")
    group = str(asset.get("group") or "").lower()

    if asset.get("render_path") or asset_type == "source_png":
        return "A_render_ready"
    if tags & POKEMON_TAGS or any(k in group for k in ("pokemon", "trainer", "pokeobj", "npc", "player")):
        return "B_pokemon_facing"
    if tags & EFFECT_TAGS or "effect" in group or "animation" in group:
        return "C_effects_animation"
    if tags & ENV_UI_TAGS or any(k in group for k in ("map", "background", "ui", "font", "menu", "title", "field", "dungeon")):
        return "D_environment_ui"
    return "E_decode_or_context_needed"


def priority(asset: dict, lane: str) -> tuple:
    status_rank = {"valid_render": 0, "usable": 1, "alternate": 2, "unreviewed": 3, "decode_issue": 4, "reject": 5}
    source_rank = {"hgss": 0, "diamond": 1, "pmd_sky": 2, "ranger2": 3}
    type_rank = {
        "source_png": 0,
        "pokemon_sprite_frame": 1,
        "nitro_visual_resource": 2,
        "pmd_sprite_animation_container": 3,
        "pmd_effect_or_texture_resource": 4,
        "pmd_background_or_map_resource": 5,
        "embedded_visual_resource": 6,
    }
    return (
        status_rank.get(asset.get("review_status"), 9),
        source_rank.get(asset.get("source_id"), 9),
        type_rank.get(asset.get("asset_type"), 9),
        asset.get("species_dex") if asset.get("species_dex") is not None else 999999,
        str(asset.get("group") or ""),
        str(asset.get("asset_id") or ""),
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    p.add_argument("--batch-size", type=int, default=100)
    args = p.parse_args()

    if args.batch_size < 1:
        raise SystemExit("--batch-size must be >= 1")

    catalog = json.loads(args.catalog.read_text())
    assets = catalog.get("assets", [])
    lanes: dict[str, list[dict]] = defaultdict(list)

    for asset in assets:
        lane = lane_for(asset)
        lanes[lane].append(asset)

    records = []
    batches = []
    seen = set()

    for lane in sorted(lanes):
        rows = sorted(lanes[lane], key=lambda a: priority(a, lane))
        for index, asset in enumerate(rows):
            asset_id = asset["asset_id"]
            if asset_id in seen:
                raise RuntimeError(f"Duplicate catalog asset_id in review queue: {asset_id}")
            seen.add(asset_id)
            batch_no = index // args.batch_size + 1
            review_id = f"{lane}:{batch_no:04d}:{index % args.batch_size:03d}"
            record = {
                "review_id": review_id,
                "lane": lane,
                "batch": batch_no,
                "asset_id": asset_id,
                "source_id": asset.get("source_id"),
                "asset_type": asset.get("asset_type"),
                "species_dex": asset.get("species_dex"),
                "group": asset.get("group"),
                "source_path": asset.get("source_path"),
                "render_path": asset.get("render_path"),
                "review_status": asset.get("review_status"),
                "target_tags": asset.get("target_tags") or [],
            }
            records.append(record)

        for start in range(0, len(rows), args.batch_size):
            batch_rows = rows[start:start + args.batch_size]
            batch_no = start // args.batch_size + 1
            batches.append({
                "lane": lane,
                "batch": batch_no,
                "count": len(batch_rows),
                "sources": dict(sorted(Counter(a.get("source_id") for a in batch_rows).items())),
                "asset_types": dict(sorted(Counter(a.get("asset_type") for a in batch_rows).items())),
            })

    if len(records) != len(assets):
        raise RuntimeError(f"Queue coverage mismatch: {len(records)} != {len(assets)}")

    lane_counts = Counter(r["lane"] for r in records)
    source_counts = Counter(r["source_id"] for r in records)
    payload = {
        "schema_version": 1,
        "source_catalog": str(args.catalog),
        "batch_size": args.batch_size,
        "asset_count": len(records),
        "lane_counts": dict(sorted(lane_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "batches": batches,
        "records": records,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Donor Asset Cross-Source Review Queue",
        "",
        "This queue organizes the donor catalog for review. It does not change",
        "review statuses, select winners, or modify Platinum resources.",
        "",
        "## Summary",
        "",
        f"- Catalog assets covered: **{len(records)}**",
        f"- Review batch size: **{args.batch_size}**",
        f"- Review batches: **{len(batches)}**",
        "",
        "## Review lanes",
        "",
        "| Lane | Assets | Purpose |",
        "|---|---:|---|",
    ]
    purposes = {
        "A_render_ready": "Already has a render path/source PNG; inspect first.",
        "B_pokemon_facing": "Pokémon, trainer, icon, portrait, overworld and battle-facing candidates.",
        "C_effects_animation": "Effects, transitions and animation resources.",
        "D_environment_ui": "Environment, backgrounds, maps, palettes and UI resources.",
        "E_decode_or_context_needed": "Opaque/container/context-heavy candidates requiring more decoding or source interpretation.",
    }
    for lane in sorted(lane_counts):
        lines.append(f"| {lane} | {lane_counts[lane]} | {purposes[lane]} |")

    lines += [
        "",
        "## Assets by source",
        "",
        "| Source | Assets |",
        "|---|---:|",
    ]
    for source, count in sorted(source_counts.items()):
        lines.append(f"| {source} | {count} |")

    lines += [
        "",
        "## Batch counts",
        "",
        "| Lane | Batches |",
        "|---|---:|",
    ]
    by_lane_batches = Counter(b["lane"] for b in batches)
    for lane in sorted(by_lane_batches):
        lines.append(f"| {lane} | {by_lane_batches[lane]} |")

    lines += [
        "",
        "## Review rules",
        "",
        "- Review lane assignment is organizational only.",
        "- Existing catalog review status is preserved.",
        "- No donor asset is promoted to usable automatically.",
        "- Replacement/import decisions remain deferred until candidate review is complete.",
    ]

    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")

    print(f"Queued {len(records)} assets into {len(batches)} batches.")
    for lane in sorted(lane_counts):
        print(f"{lane}: {lane_counts[lane]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
