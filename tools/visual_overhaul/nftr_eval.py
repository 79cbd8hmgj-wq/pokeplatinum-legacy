"""Nitro Font Resource (NFTR/RTFN) glyph-sheet validation shared by the Lane B/C/D/E recoveries."""
from __future__ import annotations

import struct


def eval_nftr(data: bytes):
    """Return (state, detail).  Valid when the CGLP glyph bitmap block decodes with plausible geometry and real ink."""
    if data[:4] != b"RTFN":
        raise ValueError("not RTFN")
    nblocks = struct.unpack_from("<H", data, 0x0E)[0]
    o = struct.unpack_from("<H", data, 0x0C)[0]
    cglp = None
    for _ in range(nblocks):
        mg, sz = data[o:o + 4], struct.unpack_from("<I", data, o + 4)[0]
        if mg == b"PLGC":
            cglp = (o, sz)
        o += sz
    if cglp is None:
        raise ValueError("no CGLP block")
    o, sz = cglp
    cw, ch, cell, _base, _maxw, bpp, _rot = struct.unpack_from("<BBHBBBB", data, o + 8)
    if bpp not in (1, 2, 4, 8) or cw == 0 or ch == 0 or cell == 0:
        raise ValueError("implausible CGLP geometry")
    body = data[o + 16:o + sz]
    n = len(body) // cell
    if n == 0 or cw * ch * bpp > cell * 8:
        raise ValueError("glyph cell size does not hold cw*ch*bpp bits")
    ink = sum(1 for g in range(n) if any(body[g * cell:(g + 1) * cell]))
    if ink == 0:
        return "blank_render", f"{n} glyph cells all empty"
    return "valid_render", f"{n} glyph bitmaps ({cw}x{ch}, {bpp}bpp), {ink} with ink"
