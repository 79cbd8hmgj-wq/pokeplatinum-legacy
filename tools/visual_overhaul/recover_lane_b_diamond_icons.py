#!/usr/bin/env python3
"""Recover Diamond party/summary icons from Lane B NCGR resources.

The Diamond donor keeps later icon members as raw NCGR while the shared source
palette remains a JASC .pal file. This pass decodes those NCGRs deterministically
using the same Nitro 4bpp layout already used by the Ranger preview tooling.

A recovered icon is promoted to usable only when:
- it is one of Lane B's Diamond pokemon_icons nitro_2d_decode records;
- the source file is a valid 4bpp RGCN/RAHC NCGR;
- decoded geometry is exactly 32x64, matching the Gen IV icon contract;
- at least one nonzero pixel is present; and
- every used palette index exists in the donor's shared palette.

No Platinum resource is written and no preferred donor is selected.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from pathlib import Path


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def read_rgcn(path: Path) -> tuple[int, int, list[int]]:
    raw = path.read_bytes()
    if raw[:4] != b"RGCN":
        raise ValueError("not RGCN")
    if raw[0x10:0x14] != b"RAHC":
        raise ValueError("missing RAHC")
    width_tiles = u16(raw, 0x18)
    height_tiles = u16(raw, 0x1A)
    pixel_format = u16(raw, 0x1C)
    data_size = struct.unpack_from("<I", raw, 0x28)[0]
    body = raw[0x30:0x30 + data_size]
    if pixel_format != 3:
        raise ValueError(f"unsupported pixel format {pixel_format}")

    # Diamond icon NCGRs use 0xFFFF/0xFFFF as "dimensions unspecified" in
    # RAHC even though the payload is valid. For this icon family the source
    # contract is independently known to be two stacked 32x32 frames, i.e.
    # 32x64 = 4x8 tiles = 1024 bytes at 4bpp.
    if width_tiles == 0xFFFF and height_tiles == 0xFFFF:
        if len(body) != 1024:
            raise ValueError(
                f"unspecified RAHC geometry with unexpected payload {len(body)} bytes"
            )
        width_tiles, height_tiles = 4, 8

    expected = width_tiles * height_tiles * 32
    if expected != len(body):
        raise ValueError(f"geometry expects {expected} bytes, got {len(body)}")

    width = width_tiles * 8
    height = height_tiles * 8
    pixels = [0] * (width * height)
    tile = 0
    for ty in range(height_tiles):
        for tx in range(width_tiles):
            chunk = body[tile * 32:(tile + 1) * 32]
            tile += 1
            pos = 0
            for y in range(8):
                for pair in range(4):
                    b = chunk[pos]
                    pos += 1
                    x = pair * 2
                    base = (ty * 8 + y) * width + tx * 8 + x
                    pixels[base] = b & 0x0F
                    pixels[base + 1] = b >> 4
    return width, height, pixels


def read_jasc_palette(path: Path) -> list[tuple[int, int, int]]:
    lines = [x.strip() for x in path.read_text().splitlines() if x.strip()]
    if len(lines) < 4 or lines[0] != "JASC-PAL":
        raise ValueError("not JASC-PAL")
    count = int(lines[2])
    colors = [tuple(map(int, row.split())) for row in lines[3:3 + count]]
    if len(colors) != count:
        raise ValueError("palette count mismatch")
    return colors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recovery", required=True, type=Path)
    ap.add_argument("--diamond-root", required=True, type=Path)
    ap.add_argument("--write-json", required=True, type=Path)
    ap.add_argument("--write-md", required=True, type=Path)
    args = ap.parse_args()

    recovery = json.loads(args.recovery.read_text())
    targets = [
        r for r in recovery.get("records", [])
        if r.get("recovery_route") == "nitro_2d_decode"
        and r.get("source_id") == "diamond"
        and r.get("group") == "pokemon_icons"
        and str(r.get("source_path") or "").lower().endswith(".ncgr")
    ]

    icon_dir = args.diamond_root / "files/poketool/icongra/poke_icon"
    palette_path = icon_dir / "narc_0000.pal"
    palette = read_jasc_palette(palette_path)

    decisions = []
    for r in targets:
        src = args.diamond_root / r["source_path"]
        status = "decode_issue"
        code = "diamond_icon_decode_failed"
        reason = "Diamond icon NCGR could not be validated against the native icon contract."
        evidence = {}
        try:
            width, height, pixels = read_rgcn(src)
            used = sorted(set(pixels))
            nonzero = sum(1 for p in pixels if p != 0)
            indices_ok = all(i < len(palette) for i in used)
            geometry_ok = (width, height) == (32, 64)
            evidence = {
                "width": width,
                "height": height,
                "nonzero_pixels": nonzero,
                "used_palette_indices": used,
                "palette_entries": len(palette),
                "indices_within_palette": indices_ok,
            }
            if geometry_ok and nonzero > 0 and indices_ok:
                status = "usable"
                code = "diamond_icon_ncgr_validated"
                reason = (
                    "Raw Diamond NCGR decodes as a nonblank 32x64 4bpp icon using "
                    "the donor's shared icon palette; plausible party/summary use is explicit."
                )
            elif nonzero == 0:
                code = "diamond_icon_blank"
                reason = "Decoded Diamond icon is blank."
            elif not geometry_ok:
                code = "diamond_icon_geometry_mismatch"
                reason = f"Decoded Diamond icon geometry is {width}x{height}, expected 32x64."
            elif not indices_ok:
                code = "diamond_icon_palette_index_mismatch"
                reason = "Decoded Diamond icon references palette indices outside the donor palette."
        except Exception as exc:
            evidence = {"error": str(exc)}

        decisions.append({
            "asset_id": r["asset_id"],
            "source_id": r["source_id"],
            "group": r["group"],
            "source_path": r["source_path"],
            "review_status": status,
            "reason_code": code,
            "reason": reason,
            "evidence": evidence,
        })

    if len(decisions) != 502:
        raise SystemExit(f"Diamond icon recovery coverage mismatch: {len(decisions)} != 502")
    ids = [d["asset_id"] for d in decisions]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate Diamond icon recovery asset_id")

    counts = Counter(d["review_status"] for d in decisions)
    payload = {
        "schema_version": 1,
        "lane": "B_pokemon_facing",
        "family": "diamond_pokemon_icons_ncgr",
        "asset_count": len(decisions),
        "status_counts": dict(sorted(counts.items())),
        "palette_path": str(palette_path.relative_to(args.diamond_root)),
        "decisions": decisions,
    }
    args.write_json.parent.mkdir(parents=True, exist_ok=True)
    args.write_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Lane B Diamond Icon NCGR Recovery",
        "",
        "Deterministic recovery of raw Diamond party/summary icon NCGR resources.",
        "No Platinum resources are modified.",
        "",
        f"- Assets checked: **{len(decisions)}**",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: **{count}**")
    lines += [
        "",
        "## Validation contract",
        "",
        "- Nitro RGCN/RAHC 4bpp decode succeeds.",
        "- Geometry is exactly 32x64.",
        "- At least one nontransparent pixel exists.",
        "- Every used palette index is covered by the donor shared palette.",
        "- Passing assets are usable donor candidates, not preferred selections.",
    ]
    args.write_md.write_text("\n".join(lines) + "\n")
    print("Diamond icon recovery:", len(decisions), dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
