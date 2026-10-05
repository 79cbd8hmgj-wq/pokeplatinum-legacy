#!/usr/bin/env python3
"""Inventory high-value HeartGold/SoulSilver visual donor assets.

This is an extraction/catalog pass only. It records source-backed visual files
from the HGSS decomp and does not modify Platinum or make usability decisions.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOTS = [
    ("pokemon_battle", "files/poketool/pokegra", ["pokemon", "battle_front", "battle_back"]),
    ("pokemon_icons", "files/poketool/icongra", ["pokemon", "party_icon", "summary_icon"]),
    ("graphics", "files/graphic", ["ui", "graphics"]),
    ("field", "files/fielddata", ["field", "overworld"]),
]

VISUAL_SUFFIXES = {
    ".png",
    ".nclr",
    ".ncgr",
    ".ncer",
    ".nanr",
    ".nscr",
    ".narc",
    ".pal",
    ".bin",
    ".dat",
    ".json",
    ".key",
}

IGNORE_SUFFIXES = {".mk", ".h", ".s", ".c", ".txt", ".csv", ".gitignore", ".narcignore", ".narcorder"}


def asset_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "source_png"
    if suffix in {".nclr", ".ncgr", ".ncer", ".nanr", ".nscr"}:
        return "nitro_visual_resource"
    if suffix == ".narc":
        return "visual_container"
    if suffix in {".pal", ".key"}:
        return "visual_metadata"
    if suffix in {".bin", ".dat"}:
        return "binary_visual_candidate"
    if suffix == ".json":
        return "source_metadata"
    return "visual_candidate_file"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--hgss-root", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    root = args.hgss_root.expanduser().resolve()
    records = []
    category_counts = Counter()
    type_counts = Counter()
    suffix_counts = Counter()
    bytes_by_category = Counter()
    missing_roots = []

    for category, relative, tags in ROOTS:
        scan_root = root / relative
        if not scan_root.exists():
            missing_roots.append(relative)
            continue

        for path in sorted(p for p in scan_root.rglob("*") if p.is_file()):
            suffix = path.suffix.lower()
            if suffix in IGNORE_SUFFIXES:
                continue
            if suffix and suffix not in VISUAL_SUFFIXES:
                continue

            size = path.stat().st_size
            rel = path.relative_to(root).as_posix()
            kind = asset_type(path)
            records.append(
                {
                    "source_path": rel,
                    "category": category,
                    "asset_type": kind,
                    "size_bytes": size,
                    "suffix": suffix or "<none>",
                    "target_tags": tags,
                    "review_status": "unreviewed",
                }
            )
            category_counts[category] += 1
            type_counts[kind] += 1
            suffix_counts[suffix or "<none>"] += 1
            bytes_by_category[category] += size

    report = {
        "schema_version": 1,
        "source_id": "hgss",
        "source_game": "Pokemon HeartGold/SoulSilver",
        "candidate_files": len(records),
        "missing_roots": missing_roots,
        "category_counts": dict(sorted(category_counts.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "bytes_by_category": dict(sorted(bytes_by_category.items())),
        "records": records,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# HeartGold/SoulSilver Visual Asset Inventory",
        "",
        "This is an extraction/catalog pass only. Nothing here modifies Platinum.",
        "",
        "## Summary",
        "",
        f"- Candidate visual/source files: **{len(records)}**",
        f"- Missing configured roots: **{len(missing_roots)}**",
        "",
        "## Categories",
        "",
        "| Category | Files | Bytes |",
        "|---|---:|---:|",
    ]
    for category in sorted(category_counts):
        lines.append(
            f"| {category} | {category_counts[category]} | {bytes_by_category[category]:,} |"
        )

    lines += [
        "",
        "## Asset types",
        "",
        "| Type | Files |",
        "|---|---:|",
    ]
    for kind, count in sorted(type_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {kind} | {count} |")

    if missing_roots:
        lines += ["", "## Missing roots", ""]
        lines += [f"- {x}" for x in missing_roots]

    lines += [
        "",
        "## Policy",
        "",
        "- All entries remain unreviewed until the cross-source bulk review phase.",
        "- Source PNGs and Nitro resources are preserved as separate catalog records.",
        "- Containers are inventoried now and can be structurally expanded later if useful.",
        "- No Platinum replacement/import decisions are made by this pass.",
    ]

    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")
    print(f"Inventoried {len(records)} HGSS visual/source files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
