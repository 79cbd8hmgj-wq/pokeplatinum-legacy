#!/usr/bin/env python3
"""Inventory high-value Pokémon Mystery Dungeon: Explorers of Sky visual donor assets.

This is an extraction/catalog pass only. It records source-backed visual files
from the PMD Sky decomp and does not modify Platinum or make usability decisions.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOTS = [
    ("effects", "files/EFFECT", ["effect", "battle_animation_frame", "field_effect"]),
    ("ground_sprites_effects", "files/GROUND", ["overworld", "effect", "transition"]),
    ("map_backgrounds", "files/MAP_BG", ["environment", "background", "tile", "palette"]),
    ("monster_graphics", "files/MONSTER", ["pokemon", "overworld", "animation"]),
    ("ui_font_resources", "files/FONT", ["ui", "cursor", "frame", "icon"]),
    ("static_backgrounds", "files/BACK", ["background", "ui", "scene"]),
    ("title_top_assets", "files/TOP", ["ui", "title", "background"]),
    ("dungeon_visuals", "files/DUNGEON", ["environment", "background", "effect"]),
    ("system_visual_candidates", "files/SYSTEM", ["ui", "icon", "effect"]),
]

VISUAL_SUFFIXES = {
    ".png",
    ".ncgr", ".nclr", ".ncer", ".nanr", ".nscr",
    ".wan", ".wte", ".wtu", ".wat", ".wba",
    ".bgp", ".bma", ".bpc", ".bpl", ".bpa",
    ".chr", ".pal", ".w16", ".kao",
    ".bin", ".dat",
}

IGNORE_SUFFIXES = {
    ".mk", ".h", ".s", ".c", ".cpp", ".txt", ".csv",
    ".md", ".json", ".yml", ".yaml",
    ".gitignore", ".gitattributes",
}


def asset_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "source_png"
    if suffix in {".ncgr", ".nclr", ".ncer", ".nanr", ".nscr"}:
        return "nitro_visual_resource"
    if suffix == ".wan":
        return "pmd_sprite_animation_container"
    if suffix in {".wte", ".wtu", ".wat", ".wba"}:
        return "pmd_effect_or_texture_resource"
    if suffix in {".bgp", ".bma", ".bpc", ".bpl", ".bpa"}:
        return "pmd_background_or_map_resource"
    if suffix in {".chr", ".pal", ".w16", ".kao"}:
        return "pmd_ui_or_palette_resource"
    if suffix in {".bin", ".dat"}:
        return "binary_visual_candidate"
    return "visual_candidate_file"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pmd-root", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    root = args.pmd_root.expanduser().resolve()
    records = []
    category_counts = Counter()
    type_counts = Counter()
    suffix_counts = Counter()
    bytes_by_category = Counter()
    missing_roots = []
    seen_paths = set()

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

            rel = path.relative_to(root).as_posix()
            if rel in seen_paths:
                raise RuntimeError(f"Duplicate PMD Sky source path: {rel}")
            seen_paths.add(rel)

            size = path.stat().st_size
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

    if sum(category_counts.values()) != len(records):
        raise RuntimeError("PMD Sky category totals do not match candidate file count")

    report = {
        "schema_version": 1,
        "source_id": "pmd_sky",
        "source_game": "Pokémon Mystery Dungeon: Explorers of Sky",
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
        "# PMD Sky Visual Asset Inventory",
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

    lines += [
        "",
        "## Suffixes",
        "",
        "| Suffix | Files |",
        "|---|---:|",
    ]
    for suffix, count in sorted(suffix_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {suffix} | {count} |")

    if missing_roots:
        lines += ["", "## Missing roots", ""]
        lines += [f"- {x}" for x in missing_roots]

    lines += [
        "",
        "## Policy",
        "",
        "- All entries remain unreviewed until the cross-source bulk review phase.",
        "- Binary/container presence does not imply a valid render or Platinum compatibility.",
        "- Source files and PMD-specific resources are preserved independently.",
        "- No species/Dex mapping is inferred from filenames in this pass.",
    ]

    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")

    print(f"Cataloged {len(records)} PMD Sky visual/source candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
