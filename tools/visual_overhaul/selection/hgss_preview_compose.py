"""Compose an HGSS map-preview screen (NSCR tilemap over the NCGR sheet PNG + palette) into a 256x192 RGBA image.

The cataloged PNG next to each .NSCR is the NCGR character sheet (32 tiles/row), NOT the screen: viewing it directly is scrambled.
Deterministic; used only for evidence (read-only on the HGSS checkout).
"""
from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image

DECODER_VERSION = "hgss-preview-nscr-v1"


def compose(nscr: Path, sheet_png: Path) -> Image.Image:
    d = nscr.read_bytes()
    if d[:4] != b"RCSN" or d[0x10:0x14] != b"NRCS":
        raise ValueError(f"not an NSCR: {nscr}")
    w, h = struct.unpack("<HH", d[0x18:0x1C])
    n = struct.unpack("<I", d[0x20:0x24])[0] // 2
    ents = struct.unpack(f"<{n}H", d[0x24 : 0x24 + 2 * n])
    if (w // 8) * (h // 8) != n:
        raise ValueError(f"NSCR entry count {n} != {w // 8}x{h // 8}")
    sheet = Image.open(sheet_png)
    if sheet.mode != "P" or sheet.width % 8:
        raise ValueError(f"sheet must be indexed with width multiple of 8: {sheet_png}")
    per_row = sheet.width // 8
    out = Image.new("P", (w, h))
    out.putpalette(sheet.getpalette())
    for i, e in enumerate(ents):
        t, hf, vf = e & 0x3FF, bool(e & 0x400), bool(e & 0x800)
        sx, sy = (t % per_row) * 8, (t // per_row) * 8
        if sy + 8 > sheet.height:
            continue  # tile outside the sheet stays index 0
        tile = sheet.crop((sx, sy, sx + 8, sy + 8))
        if hf:
            tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
        if vf:
            tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
        out.paste(tile, ((i % (w // 8)) * 8, (i // (w // 8)) * 8))
    return out.convert("RGB")
