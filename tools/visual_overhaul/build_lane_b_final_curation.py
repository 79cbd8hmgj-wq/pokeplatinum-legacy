#!/usr/bin/env python3
"""Curate all Lane B Pokémon-facing donor records.

Lane B is intentionally non-render-ready. Final states therefore distinguish:
- reject: metadata, indices, offsets, scripts, manifests, or other context files
  that are not standalone donor art;
- decode_issue: a visual resource/container/package whose source exists and is
  plausibly relevant, but which still needs trustworthy decoding/rendering.

No Lane B record is promoted to usable without a validated visual render.
No preferred donor is selected and no Platinum resource is modified.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

VISUAL_RESOURCE_TYPES = {
    "compressed_visual_package",
    "embedded_visual_resource",
    "nitro_visual_resource",
    "pmd_effect_or_texture_resource",
    "pmd_sprite_animation_container",
    "raw_visual_resource",
    "visual_container",
}

ALWAYS_CONTEXT_TYPES = {
    "source_metadata",
    "visual_metadata",
}

CONTEXT_PATH_MARKERS = (
    "/height/", "/height_o/", "/poke_shadow/", "/poke_shadow_ofx/",
    "/poke_yofs/", "/mapmatrix/", "/maptable/", "/encountdata/",
    "/eventdata/", "/script/", "/wazaoshie/", ".gitignore",
)

VISUAL_FILE_SUFFIXES = (
    ".ncgr", ".nclr", ".ncer", ".nanr", ".nscr", ".nsbmd", ".nsbtx",
    ".nsbca", ".nsbta", ".nsbtp", ".nsbma", ".narc", ".wan", ".wte",
    ".wtu", ".wat", ".wba",
)


def classify(row: dict) -> tuple[str, str, str]:
    kind = str(row.get("asset_type") or "")
    path = str(row.get("source_path") or "").replace("\\", "/").lower()
    tags = set(row.get("target_tags") or [])

    if kind in ALWAYS_CONTEXT_TYPES:
        return (
            "reject",
            "context_not_standalone_visual",
            "Metadata/context record is not standalone donor artwork.",
        )

    if any(marker in path for marker in CONTEXT_PATH_MARKERS):
        return (
            "reject",
            "context_or_offset_table",
            "Path identifies gameplay/context/offset metadata rather than standalone visual art.",
        )

    if kind in VISUAL_RESOURCE_TYPES:
        return (
            "decode_issue",
            "visual_resource_requires_decode",
            "Source is a plausible Pokémon-facing visual resource/container but lacks a trustworthy rendered form.",
        )

    if kind == "binary_visual_candidate":
        if path.endswith(VISUAL_FILE_SUFFIXES):
            return (
                "decode_issue",
                "binary_visual_resource_requires_decode",
                "Binary candidate has a known visual-resource suffix but is not yet rendered/validated.",
            )
        return (
            "reject",
            "binary_context_not_standalone_visual",
            "Binary candidate is context/metadata rather than independently usable donor artwork.",
        )

    if kind == "visual_candidate_file":
        if path.endswith(VISUAL_FILE_SUFFIXES):
            return (
                "decode_issue",
                "candidate_visual_file_requires_decode",
                "Candidate file has a recognized visual/container format but is not yet rendered/validated.",
            )
        # Files explicitly tagged as Pokémon-facing but with no recognized image/resource
        # encoding are retained as unresolved rather than silently discarded, unless
        # caught by the context-path rules above.
        if tags:
            return (
                "decode_issue",
                "candidate_file_needs_format_context",
                "Pokémon-facing candidate exists but its visual format/context is not yet trustworthy.",
            )
        return (
            "reject",
            "candidate_file_not_visual",
            "Candidate file has no supported visual format or plausible target metadata.",
        )

    return (
        "decode_issue",
        "unknown_pokemon_facing_resource",
        "Pokémon-facing source exists but requires format/context resolution before visual validation.",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    queue = json.loads(args.queue.read_text())
    rows = [r for r in queue.get("records", []) if r.get("lane") == "B_pokemon_facing"]
    if len(rows) != 15157:
        raise SystemExit(f"Lane B count mismatch: {len(rows)} != 15157")

    decisions = []
    for row in rows:
        status, code, reason = classify(row)
        decisions.append({
            "asset_id": row.get("asset_id"),
            "source_id": row.get("source_id"),
            "asset_type": row.get("asset_type"),
            "species_dex": row.get("species_dex"),
            "group": row.get("group"),
            "source_path": row.get("source_path"),
            "target_tags": row.get("target_tags") or [],
            "review_status": status,
            "reason_code": code,
            "reason": reason,
        })

    ids = [d["asset_id"] for d in decisions]
    if len(ids) != len(set(ids)) != 15157:
        raise SystemExit("Lane B duplicate asset IDs")
    if len(set(ids)) != 15157:
        raise SystemExit(f"Lane B unique decision mismatch: {len(set(ids))}")

    counts = Counter(d["review_status"] for d in decisions)
    by_source = {}
    for source in sorted({d["source_id"] for d in decisions}):
        by_source[source] = dict(sorted(Counter(
            d["review_status"] for d in decisions if d["source_id"] == source
        ).items()))
    by_type = {}
    for kind in sorted({d["asset_type"] for d in decisions}):
        by_type[kind] = dict(sorted(Counter(
            d["review_status"] for d in decisions if d["asset_type"] == kind
        ).items()))

    payload = {
        "schema_version": 1,
        "lane": "B_pokemon_facing",
        "scope": (
            "Complete Lane B curation. Non-art metadata/context is rejected; "
            "plausible visual resources without trustworthy renders remain decode_issue. "
            "No usable promotion, preferred-donor choice, or Platinum writes."
        ),
        "asset_count": len(decisions),
        "status_counts": dict(sorted(counts.items())),
        "source_status_counts": by_source,
        "asset_type_status_counts": by_type,
        "records": sorted(decisions, key=lambda d: d["asset_id"]),
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane B Final Curation",
        "",
        "Complete per-asset curation for Pokémon-facing assets that are not render-ready.",
        "No Platinum resources are modified.",
        "",
        "## Summary",
        "",
        f"- Lane B assets curated: **{len(decisions)}**",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: **{count}**")

    lines += [
        "",
        "## By source",
        "",
        "| Source | usable | reject | decode_issue |",
        "|---|---:|---:|---:|",
    ]
    for source, c in by_source.items():
        lines.append(
            f"| {source} | {c.get('usable', 0)} | {c.get('reject', 0)} | {c.get('decode_issue', 0)} |"
        )

    lines += [
        "",
        "## Policy",
        "",
        "- Metadata, offset tables, scripts, map/event context, and manifests are reject as standalone donor art.",
        "- Recognized visual resources/containers without a validated render are decode_issue.",
        "- Ambiguous Pokémon-facing candidate files remain decode_issue unless clearly non-visual.",
        "- No Lane B asset becomes usable merely from tags or file extension.",
        "- Preferred/alternate selection remains deferred until the full database is curated.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")

    print("Lane B final:", len(decisions), dict(counts))
    print("By source:", by_source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
