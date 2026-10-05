#!/usr/bin/env python3
"""Compact machine-readable structural diagnostic for Ranger Pokemon packages.

For each selected species/variant/group it emits NCER header fields, character
resource header fields (including the scan flag), OAM attribute histograms,
tile-reference coverage against the available character data, and a
"coherence" score of the rendered cells under both the legacy (tile-ordered)
and scan-aware character readers.  Diagnostic only; renders nothing to disk.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path

from inspect_ranger_assets import extract_narc_members
from nitro_narc import lz10_decompress
from render_ranger_ncer_preview import (
    SHAPE_SIZE,
    read_cells,
    read_chars,
    render_cell,
    signed_x,
    signed_y,
    u16,
    u32,
)


def coherence(width: int, height: int, pixels: list[int]) -> float | None:
    """Mean fraction of 4-neighbours sharing the same colour index, over opaque
    pixels with at least one opaque neighbour.  Coherent art scores high;
    tile-scrambled "soup" scores low."""
    num = den = 0
    for y in range(height):
        for x in range(width):
            c = pixels[y * width + x]
            if not c:
                continue
            same = opaque = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    n = pixels[ny * width + nx]
                    if n:
                        opaque += 1
                        same += n == c
            if opaque:
                num += same / opaque
                den += 1
    return round(num / den, 4) if den else None


def render_score(cells, sheet_w, tiles, stride=32):
    scores = []
    for oams in cells:
        w, h, px = render_cell(oams, sheet_w, tiles, stride)
        s = coherence(w, h, px)
        if s is not None:
            scores.append(s)
    return round(sum(scores) / len(scores), 4) if scores else None


def char_header(path: Path) -> dict:
    raw = path.read_bytes()
    return {
        "file": path.name,
        "kind": path.suffix[1:],
        "tiles_w": u16(raw, 0x18),
        "tiles_h": u16(raw, 0x1A),
        "depth": u32(raw, 0x1C),
        "scan_flag": u32(raw, 0x24),
        "data_bytes": u32(raw, 0x28),
    }


def group_report(extract_dir: Path, stem: str, cell_sample: int) -> dict:
    ncer = extract_dir / f"{stem}.NCER"
    raw = ncer.read_bytes()
    cells = read_cells(ncer)
    report: dict = {
        "group": stem,
        "ncer": {
            "cells": len(cells),
            "cell_type": u16(raw, 0x1A),
            "mapping_type": u32(raw, 0x20),
            "vram_transfer_off": u32(raw, 0x24),
        },
        "chars": [],
    }
    objs = [o for c in cells for o in c]
    report["ncer"]["oam_total"] = len(objs)
    report["ncer"]["oam_per_cell_max"] = max((len(c) for c in cells), default=0)
    report["oam_hist"] = {
        "shape_size": dict(Counter(f"{(a0 >> 14) & 3}/{(a1 >> 14) & 3}" for a0, a1, _ in objs)),
        "affine": sum(1 for a0, _, _ in objs if a0 & 0x100),
        "disable_or_double": sum(1 for a0, _, _ in objs if a0 & 0x200),
        "obj_mode": dict(Counter((a0 >> 10) & 3 for a0, _, _ in objs)),
        "mosaic": sum(1 for a0, _, _ in objs if a0 & 0x1000),
        "color256": sum(1 for a0, _, _ in objs if a0 & 0x2000),
        "hflip": sum(1 for _, a1, _ in objs if a1 & 0x1000),
        "vflip": sum(1 for _, a1, _ in objs if a1 & 0x2000),
        "palette_nums": dict(Counter(a2 >> 12 for _, _, a2 in objs)),
        "priority": dict(Counter((a2 >> 10) & 3 for _, _, a2 in objs)),
    }
    max_tile_end = 0
    for a0, a1, a2 in objs:
        w, h = SHAPE_SIZE[(a0 >> 14) & 3][(a1 >> 14) & 3]
        t = a2 & 0x3FF
        max_tile_end = max(max_tile_end, t + (h // 8 - 1) * 32 + w // 8)
    report["oam_hist"]["max_logical_tile_end_2d32"] = max_tile_end

    # Candidate character resources for this group, in both readers.
    for suffix in ("NCGR", "NCBR"):
        path = extract_dir / f"{stem}.{suffix}"
        if not path.exists():
            continue
        hdr = char_header(path)
        sw, sh, legacy = read_chars(path, honor_scanned=False)
        _, _, aware = read_chars(path, cells=cells)
        hdr["tiles_total"] = sw * sh
        hdr["coherence_legacy"] = render_score(cells, sw, legacy)
        aw, _, aware = read_chars(path, cells=cells)
        hdr["raster_width_tiles"] = aw
        hdr["coherence_scan_aware"] = render_score(cells, aw, aware)
        report["chars"].append(hdr)

    report["cells_sample"] = [
        [
            {
                "shape": f"{SHAPE_SIZE[(a0 >> 14) & 3][(a1 >> 14) & 3][0]}x{SHAPE_SIZE[(a0 >> 14) & 3][(a1 >> 14) & 3][1]}",
                "xy": [signed_x(a1), signed_y(a0)],
                "tile": a2 & 0x3FF,
                "pal": a2 >> 12,
                "flip": (a1 >> 12) & 3,
            }
            for a0, a1, a2 in oams
        ]
        for oams in cells[:cell_sample]
    ]
    return report


def corpus_checks(poke: Path) -> dict:
    """Whole-corpus structural invariants (cheap; no image output).

    Counts objects whose 2D-mapped tile footprint falls outside the character
    data, objects that read only blank tiles, and palette rows beyond the NCLR.
    """
    total = {"packages": 0, "group_count": 0, "cells": 0, "objects": 0,
             "oob_objects": 0, "blank_objects": 0, "palette_overflow_objects": 0,
             "groups_scanned_raster": 0, "groups_tiled": 0}
    raster_widths: Counter = Counter()
    flagged: list = []
    groups: dict = {}
    for pkg in sorted(poke.glob("p???_??_LZ.bin")):
        if pkg.name.startswith("p000"):
            continue
        total["packages"] += 1
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            extract_narc_members(lz10_decompress(pkg.read_bytes()), d)
            pal = sorted(d.glob("*.NCLR"))[0]
            pal_rows = (u32(pal.read_bytes(), 0x20)) // 32
            gfx = {p.stem: p for p in sorted(d.glob("*.NCBR"))}
            gfx.update({p.stem: p for p in sorted(d.glob("*.NCGR"))})
            for ncer in sorted(d.glob("*.NCER")):
                if ncer.stem not in gfx:
                    continue
                cells = read_cells(ncer)
                sw, sh, tiles = read_chars(gfx[ncer.stem], cells=cells)
                scanned = gfx[ncer.stem].suffix == ".NCBR"
                total["group_count"] += 1
                total["groups_scanned_raster" if scanned else "groups_tiled"] += 1
                if scanned:
                    raster_widths[sw] += 1
                total["cells"] += len(cells)
                g_oob = 0
                oob_cells: list = []
                for ci, oams in enumerate(cells):
                    cell_oob = False
                    for a0, a1, a2 in oams:
                        shape = (a0 >> 14) & 3
                        if shape not in SHAPE_SIZE:
                            continue
                        w, h = SHAPE_SIZE[shape][(a1 >> 14) & 3]
                        t = a2 & 0x3FF
                        total["objects"] += 1
                        if (a2 >> 12) >= pal_rows:
                            total["palette_overflow_objects"] += 1
                        oob = blank = True
                        refs = []
                        for ty in range(h // 8):
                            for tx in range(w // 8):
                                row, col = divmod(t + ty * 32 + tx, 32)
                                src = row * sw + col
                                ok = col < sw and 0 <= src < len(tiles)
                                refs.append(ok)
                                if ok and any(tiles[src]):
                                    blank = False
                        if not all(refs):
                            total["oob_objects"] += 1
                            g_oob += 1
                            cell_oob = True
                        if blank:
                            total["blank_objects"] += 1
                    if cell_oob:
                        oob_cells.append(ci)
                groups[ncer.stem] = {
                    "src": gfx[ncer.stem].suffix[1:],
                    "raster_w": sw,
                    "cells": len(cells),
                    "oob_cells": oob_cells,
                }
                if g_oob and len(flagged) < 40:
                    flagged.append({"pkg": pkg.name[:7], "group": ncer.stem, "oob_objects": g_oob})
    total["raster_width_tiles_hist"] = dict(sorted(raster_widths.items()))
    total["groups_with_oob_objects_sample"] = flagged
    total["group_ledger"] = groups  # per-group structural validity ledger
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranger-root", required=True, type=Path)
    ap.add_argument("--species", action="append", type=int, default=[])
    ap.add_argument("--corpus", action="store_true", help="whole-corpus invariant summary")
    ap.add_argument("--variant", action="append", type=int, default=[])
    ap.add_argument("--cell-sample", type=int, default=2)
    ap.add_argument("--write-json", type=Path)
    args = ap.parse_args()

    poke = args.ranger_root.expanduser().resolve() / "res/prebuilt/data/poke"
    if args.corpus:
        text = json.dumps(corpus_checks(poke), separators=(",", ":"))
        if args.write_json:
            args.write_json.parent.mkdir(parents=True, exist_ok=True)
            args.write_json.write_text(text + "\n")
        print(text)
        return 0
    out = []
    for sp in args.species:
        for pkg in sorted(poke.glob(f"p{sp:03d}_??_LZ.bin")):
            var = int(pkg.name[5:7])
            if args.variant and var not in args.variant:
                continue
            with tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                extract_narc_members(lz10_decompress(pkg.read_bytes()), d)
                pal = next(iter(sorted(d.glob("*.NCLR"))), None)
                out.append(
                    {
                        "species": sp,
                        "variant": var,
                        "nclr_bytes": pal.stat().st_size if pal else None,
                        "groups": [
                            group_report(d, p.stem, args.cell_sample)
                            for p in sorted(d.glob("*.NCER"))
                        ],
                    }
                )
    text = json.dumps(out, separators=(",", ":"))
    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
