#!/usr/bin/env python3
"""Audit rendered Ranger Pokémon PNG cells against Platinum-friendly geometry.

This is a curation aid, not an importer. It reads PNG dimensions directly and
classifies obvious fit/outlier cases for an 80x80 Platinum battle-sprite cell.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from pathlib import Path


def png_size(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise ValueError(f"{path}: not PNG")
    return struct.unpack(">II", raw[16:24])


def classify(width: int, height: int, target: int) -> str:
    if width <= target and height <= target:
        if width <= target // 2 and height <= target // 2:
            return "fits_small"
        return "fits"
    if width <= target + 16 and height <= target + 16:
        return "geometry_close"
    return "oversize"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--render-root", required=True, type=Path)
    p.add_argument("--target-size", type=int, default=80)
    p.add_argument("--write-json", type=Path)
    p.add_argument("--write-md", type=Path)
    args = p.parse_args()

    root = args.render_root.expanduser().resolve()
    rows = []
    counts = Counter()

    for png in sorted(root.rglob("cell_*.png")):
        width, height = png_size(png)
        status = classify(width, height, args.target_size)
        counts[status] += 1
        parts = png.relative_to(root).parts
        species = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else None
        variant = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        group = parts[2] if len(parts) > 2 else None
        rows.append(
            {
                "species": species,
                "variant": variant,
                "group": group,
                "file": str(png.relative_to(root)),
                "width": width,
                "height": height,
                "status": status,
            }
        )

    report = {
        "schema_version": 1,
        "target_cell": [args.target_size, args.target_size],
        "cells": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "rows": rows,
    }

    print(f"Audited {len(rows)} Ranger cells")
    print("Statuses:", report["status_counts"])

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(report, indent=2) + "\n")

    if args.write_md:
        lines = [
            "# Ranger Pokémon Render Compatibility Audit",
            "",
            f"Target comparison cell: **{args.target_size}x{args.target_size}**",
            "",
            "| Status | Cells |",
            "|---|---:|",
        ]
        for key, value in sorted(counts.items()):
            lines.append(f"| {key} | {value} |")
        lines.extend(
            [
                "",
                "## Cell inventory",
                "",
                "| Species | Variant | Group | Cell | Size | Status |",
                "|---:|---:|---|---|---:|---|",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['species']} | {row['variant']} | {row['group']} | "
                f"`{row['file']}` | {row['width']}x{row['height']} | "
                f"{row['status']} |"
            )
        args.write_md.parent.mkdir(parents=True, exist_ok=True)
        args.write_md.write_text("\n".join(lines) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
