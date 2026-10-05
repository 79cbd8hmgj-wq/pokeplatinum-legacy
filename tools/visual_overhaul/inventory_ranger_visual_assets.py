#!/usr/bin/env python3
"""Inventory likely reusable visual assets in Pokémon Ranger: Shadows of Almia.

This tool inventories donor material only. It does not render or modify Platinum.
It scans Ranger's prebuilt data tree, classifies likely visual packages/resources,
records container signatures where possible, and emits a source-side inventory that
can be normalized into the project donor asset catalog.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


EXCLUDED_TOP = {
    "Script",
    "Sound",
    "message",
    "param",
    "poke",
}

VISUAL_TOP = {
    "battle",
    "effect",
    "encyclo",
    "ending",
    "event",
    "eventicon",
    "field",
    "font",
    "interface",
    "menu",
    "npc",
    "opening",
    "player",
    "pokeOBJ",
    "sendbin",
    "system",
    "target",
    "targetOBJ",
    "title",
    "uppict",
}

RAW_VISUAL_SUFFIXES = {
    ".ncgr",
    ".ncbr",
    ".nclr",
    ".ncer",
    ".nanr",
    ".nftr",
    ".ntft",
    ".ntfp",
}

ROOT_VISUAL_NAMES = {
    "battle_disk01_LZ.bin",
    "battle_line01.NCBR",
    "battle_line01.NCLR",
    "cursor_LZ.bin",
    "disk02_LZ.bin",
    "disk_break_LZ.bin",
    "shadow.NCBR",
    "shadow.NCLR",
}

CATEGORY_TAGS = {
    "battle": ["battle", "background", "ui"],
    "effect": ["effect"],
    "encyclo": ["ui", "encyclopedia"],
    "ending": ["presentation", "ui"],
    "event": ["event", "scene"],
    "eventicon": ["ui", "icon"],
    "field": ["overworld", "field"],
    "font": ["ui", "font"],
    "interface": ["ui"],
    "menu": ["ui", "menu"],
    "npc": ["overworld", "npc", "trainer_candidate"],
    "opening": ["presentation"],
    "player": ["overworld", "player"],
    "pokeOBJ": ["pokemon_object"],
    "sendbin": ["unknown"],
    "system": ["ui", "system"],
    "target": ["capture", "target"],
    "targetOBJ": ["capture", "target_object"],
    "title": ["presentation", "ui"],
    "uppict": ["portrait", "ui"],
    "_root": ["ui", "effect"],
}


def signature(path: Path) -> str:
    try:
        raw = path.read_bytes()[:16]
    except OSError:
        return "unreadable"
    if not raw:
        return "empty"
    if raw[0] == 0x10:
        return "lz10"
    magic = raw[:4]
    known = {
        b"NARC": "narc",
        b"CRAN": "narc",
        b"RGCN": "nitro_character",
        b"RLCN": "nitro_palette",
        b"RECN": "nitro_cell",
        b"RNAN": "nitro_animation",
        b"RTFN": "nitro_font",
    }
    return known.get(magic, magic.decode("ascii", "replace"))


def classify(path: Path, data_root: Path):
    rel = path.relative_to(data_root)
    parts = rel.parts
    if len(parts) == 1:
        if path.name not in ROOT_VISUAL_NAMES:
            return None
        return "_root", CATEGORY_TAGS["_root"]

    top = parts[0]
    if top in EXCLUDED_TOP or top not in VISUAL_TOP:
        return None
    if path.name == "meson.build":
        return None
    return top, CATEGORY_TAGS.get(top, ["unknown"])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ranger-root", required=True, type=Path)
    p.add_argument("--write-json", required=True, type=Path)
    p.add_argument("--write-md", required=True, type=Path)
    args = p.parse_args()

    root = args.ranger_root.expanduser().resolve()
    data_root = root / "res/prebuilt/data"
    if not data_root.is_dir():
        raise SystemExit(f"Missing Ranger prebuilt data root: {data_root}")

    records = []
    category_counts = Counter()
    signature_counts = Counter()
    suffix_counts = Counter()
    bytes_by_category = Counter()

    for path in sorted(p for p in data_root.rglob("*") if p.is_file()):
        info = classify(path, data_root)
        if info is None:
            continue
        category, tags = info
        rel = path.relative_to(root).as_posix()
        sig = signature(path)
        suffix = path.suffix.lower() or "<none>"
        size = path.stat().st_size

        if path.suffix.lower() in RAW_VISUAL_SUFFIXES:
            asset_type = "raw_visual_resource"
        elif sig == "lz10" or path.name.lower().endswith("_lz.bin"):
            asset_type = "compressed_visual_package"
        else:
            asset_type = "visual_candidate_file"

        records.append(
            {
                "source_path": rel,
                "category": category,
                "asset_type": asset_type,
                "size_bytes": size,
                "suffix": suffix,
                "signature": sig,
                "target_tags": tags,
                "review_status": "unreviewed",
            }
        )
        category_counts[category] += 1
        signature_counts[sig] += 1
        suffix_counts[suffix] += 1
        bytes_by_category[category] += size

    payload = {
        "schema_version": 1,
        "source_id": "ranger2",
        "source_game": "Pokémon Ranger: Shadows of Almia",
        "root": str(root),
        "candidate_files": len(records),
        "category_counts": dict(sorted(category_counts.items())),
        "signature_counts": dict(sorted(signature_counts.items())),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "bytes_by_category": dict(sorted(bytes_by_category.items())),
        "records": records,
    }

    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    total_bytes = sum(bytes_by_category.values())
    lines = [
        "# Ranger Visual Asset Inventory",
        "",
        "Source: Pokémon Ranger: Shadows of Almia",
        "",
        "This is a donor-source inventory only. Nothing here modifies Platinum.",
        "",
        "The dedicated poke/ Pokémon frame corpus is tracked separately and is not",
        "duplicated in this source-level inventory.",
        "",
        "## Summary",
        "",
        f"- Candidate visual files/packages: {len(records)}",
        f"- Candidate bytes: {total_bytes:,}",
        f"- Categories: {len(category_counts)}",
        "",
        "## Categories",
        "",
        "| Category | Files | Bytes |",
        "|---|---:|---:|",
    ]
    for cat in sorted(category_counts):
        lines.append(f"| {cat} | {category_counts[cat]} | {bytes_by_category[cat]:,} |")

    lines += [
        "",
        "## Container/resource signatures",
        "",
        "| Signature | Files |",
        "|---|---:|",
    ]
    for sig, count in sorted(signature_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {sig} | {count} |")

    lines += [
        "",
        "## Inventory policy",
        "",
        "- unreviewed means the source exists but has not yet been visually assessed.",
        "- compressed packages are preserved even if their internal members are not yet decoded.",
        "- raw Nitro resources are cataloged directly.",
        "- no file is marked usable from its filename or dimensions alone.",
        "- all plausible alternatives remain in the database for later cross-source comparison.",
    ]

    args.write_md.parent.mkdir(parents=True, exist_ok=True)
    args.write_md.write_text("\n".join(lines) + "\n")

    print(f"Inventoried {len(records)} Ranger visual candidate files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
