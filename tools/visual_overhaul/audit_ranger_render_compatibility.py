#!/usr/bin/env python3
"""Audit rendered Ranger Pokémon cells against Platinum 80x80 geometry.

Generated Ranger previews are indexed PNGs written by render_ranger_ncer_preview.py.
This audit parses those PNGs directly, measures the nontransparent pixel bounding
box (palette index 0 is transparent), and classifies geometry using occupied art
rather than the raw OAM canvas.
"""
from __future__ import annotations

import argparse
import json
import struct
import zlib
from collections import Counter, defaultdict
from pathlib import Path


PNG_SIG = b"\x89PNG\r\n\x1a\n"


def read_indexed_png(path: Path) -> tuple[int, int, bytes]:
    raw = path.read_bytes()
    if raw[:8] != PNG_SIG:
        raise ValueError(f"{path}: not PNG")

    pos = 8
    width = height = None
    idat = bytearray()
    while pos + 12 <= len(raw):
        size = struct.unpack(">I", raw[pos:pos + 4])[0]
        kind = raw[pos + 4:pos + 8]
        payload = raw[pos + 8:pos + 8 + size]
        pos += 12 + size
        if kind == b"IHDR":
            width, height, bit_depth, color_type, comp, filt, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if bit_depth != 8 or color_type != 3 or interlace != 0:
                raise ValueError(
                    f"{path}: expected non-interlaced indexed 8bpp PNG, "
                    f"got depth={bit_depth} color={color_type} interlace={interlace}"
                )
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            break

    if width is None or height is None:
        raise ValueError(f"{path}: missing IHDR")

    decoded = zlib.decompress(bytes(idat))
    stride = width + 1
    if len(decoded) != stride * height:
        raise ValueError(f"{path}: unexpected decompressed PNG size")

    pixels = bytearray(width * height)
    prev = bytearray(width)
    for y in range(height):
        row = decoded[y * stride:(y + 1) * stride]
        filter_type = row[0]
        src = bytearray(row[1:])
        out = bytearray(width)

        if filter_type == 0:
            out[:] = src
        elif filter_type == 1:
            for x, val in enumerate(src):
                left = out[x - 1] if x else 0
                out[x] = (val + left) & 0xFF
        elif filter_type == 2:
            for x, val in enumerate(src):
                out[x] = (val + prev[x]) & 0xFF
        else:
            raise ValueError(f"{path}: unsupported PNG filter {filter_type}")

        pixels[y * width:(y + 1) * width] = out
        prev = out

    return width, height, bytes(pixels)


def occupied_bbox(width: int, height: int, pixels: bytes):
    xs = []
    ys = []
    opaque = 0
    for i, index in enumerate(pixels):
        if index == 0:
            continue
        opaque += 1
        xs.append(i % width)
        ys.append(i // width)
    if not xs:
        return None, 0
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1), opaque


def classify(width: int, height: int, target: int) -> str:
    if width <= target // 2 and height <= target // 2:
        return "fits_small"
    if width <= target and height <= target:
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
    species_classes = defaultdict(Counter)
    group_counts = Counter()

    for png in sorted(root.rglob("cell_*.png")):
        canvas_w, canvas_h, pixels = read_indexed_png(png)
        bbox, opaque = occupied_bbox(canvas_w, canvas_h, pixels)
        if bbox is None:
            art_w = art_h = 0
            status = "blank"
        else:
            left, top, right, bottom = bbox
            art_w = right - left
            art_h = bottom - top
            status = classify(art_w, art_h, args.target_size)

        parts = png.relative_to(root).parts
        species = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else None
        variant = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        group = parts[2] if len(parts) > 2 else None
        counts[status] += 1
        if species is not None:
            species_classes[species][status] += 1
        if group:
            group_counts[group.rsplit("_", 1)[-1]] += 1

        rows.append(
            {
                "species": species,
                "variant": variant,
                "group": group,
                "file": str(png.relative_to(root)),
                "canvas_width": canvas_w,
                "canvas_height": canvas_h,
                "bbox": list(bbox) if bbox else None,
                "bbox_width": art_w,
                "bbox_height": art_h,
                "opaque_pixels": opaque,
                "width_ratio": round(art_w / args.target_size, 6),
                "height_ratio": round(art_h / args.target_size, 6),
                "max_axis_ratio": round(max(art_w, art_h) / args.target_size, 6),
                "status": status,
            }
        )

    species_summary = []
    for species in sorted(species_classes):
        sc = species_classes[species]
        total = sum(sc.values())
        species_summary.append(
            {
                "species": species,
                "cells": total,
                "status_counts": dict(sorted(sc.items())),
                "oversize_fraction": round(sc["oversize"] / total, 6),
            }
        )

    report = {
        "schema_version": 2,
        "measurement": "nontransparent_bbox",
        "target_cell": [args.target_size, args.target_size],
        "cells": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "group_suffix_counts": dict(sorted(group_counts.items())),
        "species_summary": species_summary,
        "rows": rows,
    }

    print(f"Audited {len(rows)} Ranger cells using opaque bounding boxes")
    print("Statuses:", report["status_counts"])

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(report, indent=2) + "\n")

    if args.write_md:
        total = max(1, len(rows))
        lines = [
            "# Ranger Pokémon Render Compatibility Audit",
            "",
            f"Target comparison cell: **{args.target_size}x{args.target_size}**",
            "",
            "Classification uses the nontransparent pixel bounding box, not the raw OAM canvas.",
            "Palette index 0 is treated as transparent.",
            "",
            "## Summary",
            "",
            "| Status | Cells | Share |",
            "|---|---:|---:|",
        ]
        for key in ("fits_small", "fits", "geometry_close", "oversize", "blank"):
            value = counts.get(key, 0)
            lines.append(f"| {key} | {value} | {value / total:.2%} |")

        oversize_species = sorted(
            (
                (s["status_counts"].get("oversize", 0), s["species"], s["cells"])
                for s in species_summary
                if s["status_counts"].get("oversize", 0)
            ),
            reverse=True,
        )
        lines.extend(
            [
                "",
                "## Species with oversize cells",
                "",
                "| Species | Oversize cells | Total cells |",
                "|---:|---:|---:|",
            ]
        )
        for n, species, cells in oversize_species:
            lines.append(f"| {species:03d} | {n} | {cells} |")
        if not oversize_species:
            lines.append("| — | 0 | — |")

        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                "- fits_small: occupied art is at most 40x40.",
                "- fits: occupied art fits inside 80x80.",
                "- geometry_close: occupied art exceeds 80x80 but is no larger than 96x96.",
                "- oversize: occupied art exceeds the 96x96 review envelope.",
                "- blank: no nontransparent pixels were rendered.",
                "",
                "These are census labels, not automatic import decisions.",
            ]
        )
        args.write_md.parent.mkdir(parents=True, exist_ok=True)
        args.write_md.write_text("\n".join(lines) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
