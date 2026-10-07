"""Decode HGSS trainer battle sprite sets (a/0/5/8 front, a/0/0/6 back) without Platinum edits.

Layout (HGSS src/pokemon.c sub_02070D3C): class i uses NARC members 5i+{0:NCGR,1:NCLR,2:NCER,3:NANR,4:NCBR}.
NCGR = tile-ordered 4bpp chars (0xFFFF geometry, 1D OBJ mapping); NCER = extended cell bank.
"""
from __future__ import annotations

import struct

NARC_FRONT = "files/a/0/5/8"
NARC_BACK = "files/a/0/0/6"
SHAPE_SIZE = {
    0: {0: (8, 8), 1: (16, 16), 2: (32, 32), 3: (64, 64)},
    1: {0: (16, 8), 1: (32, 8), 2: (32, 16), 3: (64, 32)},
    2: {0: (8, 16), 1: (8, 32), 2: (16, 32), 3: (32, 64)},
}


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def parse_ncgr_tiles(raw: bytes) -> list[list[int]]:
    """Tile list (8x8, 4bpp). Also see ncgr_unit_shift(): OBJ char names address 32<<shift byte units."""
    if raw[:4] != b"RGCN" or raw[0x10:0x14] != b"RAHC":
        raise ValueError("not NCGR")
    wt, ht, fmt = struct.unpack_from("<HHI", raw, 0x18)
    if fmt != 3:
        raise ValueError(f"unsupported char format {fmt}")
    size = struct.unpack_from("<I", raw, 0x28)[0]
    body = raw[0x30:0x30 + size]
    if len(body) != size or size % 32:
        raise ValueError("truncated NCGR")
    return [[(b >> (4 * k)) & 15 for b in body[p:p + 32] for k in (0, 1)] for p in range(0, size, 32)]


def ncgr_unit_shift(raw: bytes) -> int:
    """RAHC mapping mode bits 4-5: 0=1D_32K (32B char unit), 1=1D_64K (64B), 2=128K, 3=256K."""
    return (struct.unpack_from("<I", raw, 0x20)[0] >> 4) & 3


def parse_nclr(raw: bytes) -> list[tuple[int, int, int]]:
    if raw[:4] != b"RLCN" or raw[0x10:0x14] != b"TTLP":
        raise ValueError("not NCLR")
    size = struct.unpack_from("<I", raw, 0x20)[0]
    out = []
    for p in range(0x28, 0x28 + size, 2):
        v = u16(raw, p)
        out.append(((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31))
    return out


def parse_ncer_transfers(raw: bytes, count: int) -> list[tuple[int, int]] | None:
    """Per-cell VRAM transfer (source byte offset into NCGR data, byte size), or None if the bank has none.
    Layout (nitrogfx ReadNtrCell_CEBK): KBEC block at 0x10; u16 at block+0x14 = offset (from block+8) to
    [maxSize u32, offset u32] followed by one (srcOffset u32, size u32) pair per cell."""
    blk = 0x10
    off = struct.unpack_from("<H", raw, blk + 0x14)[0]
    if off == 0:
        return None
    p = blk + 8 + off + 8
    if p + 8 * count > len(raw):
        raise ValueError("VRAM transfer table exceeds NCER")
    return [struct.unpack_from("<II", raw, p + 8 * i) for i in range(count)]


def parse_ncer(raw: bytes) -> list[list[tuple[int, int, int]]]:
    if raw[:4] != b"RECN" or raw[0x10:0x14] != b"KBEC":
        raise ValueError("not NCER")
    count, attr = struct.unpack_from("<HH", raw, 0x18)
    ent = 16 if attr == 1 else 8
    base = 0x30 + count * ent
    cells = []
    for i in range(count):
        n, _a, off = struct.unpack_from("<HHI", raw, 0x30 + i * ent)
        s = base + off
        if s + 6 * n > len(raw):
            raise ValueError(f"cell {i} OAM exceeds file")
        cells.append([struct.unpack_from("<HHH", raw, s + 6 * j) for j in range(n)])
    return cells


def _sx(a1):
    v = a1 & 0x1FF
    return v - 512 if v >= 256 else v


def _sy(a0):
    v = a0 & 0xFF
    return v - 256 if v >= 128 else v


def render_cell_1d(oams, tiles, shift=0):
    objs = []
    for a0, a1, a2 in oams:
        shape = (a0 >> 14) & 3
        if shape not in SHAPE_SIZE:
            continue
        w, h = SHAPE_SIZE[shape][(a1 >> 14) & 3]
        objs.append((_sx(a1), _sy(a0), w, h, (a2 & 0x3FF) << shift, a2 >> 12, bool(a1 & 0x1000), bool(a1 & 0x2000)))
    if not objs:
        return 0, 0, [], 0
    min_x = min(o[0] for o in objs)
    min_y = min(o[1] for o in objs)
    width = max(o[0] + o[2] for o in objs) - min_x
    height = max(o[1] + o[3] for o in objs) - min_y
    canvas = [0] * (width * height)
    oob = 0
    for x0, y0, w, h, t0, prow, hf, vf in objs:
        wt = w // 8
        for py in range(h):
            sy = h - 1 - py if vf else py
            ty, iy = divmod(sy, 8)
            for px in range(w):
                sx = w - 1 - px if hf else px
                tx, ix = divmod(sx, 8)
                t = t0 + ty * wt + tx
                if t >= len(tiles):
                    oob += 1
                    continue
                c = tiles[t][iy * 8 + ix]
                if c:
                    canvas[(y0 - min_y + py) * width + x0 - min_x + px] = c + prow * 16
    return width, height, canvas, oob


def render_sheet(cells, tiles, gap=1, shift=0, transfers=None):
    """Stack all cells vertically (Platinum multi-frame layout: 1px gap). Returns (w,h,pixels,oob,cell_dims)."""
    rendered = []
    for i, c in enumerate(cells):
        pool = tiles
        if transfers:
            src, size = transfers[i]
            pool = tiles[src // 32:(src + size) // 32]
        rendered.append(render_cell_1d(c, pool, shift))
    w = max(r[0] for r in rendered)
    rows, dims, oob = [], [], 0
    for rw, rh, cv, o in rendered:
        oob += o
        dims.append((rw, rh))
        for y in range(rh):
            rows.append(cv[y * rw:(y + 1) * rw] + [0] * (w - rw))
        if gap:
            rows.append([0] * w)
    if gap and rows:
        rows.pop()  # no trailing gap
    flat = [p for r in rows for p in r]
    return w, len(rows), flat, oob, dims
