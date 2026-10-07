"""Compose a Ranger2 field map (map.dat.lz + map.tex.lz) from its quad layers.

Format (established from the overlay-0 loader + data; see recover_lane_b_ranger_maps.py):
  tex: 'TEX\\0' + NARC of texture banks; each bank is a NARC [RGCN scan=1 4bpp raster, RLCN 256 colours].
  dat: NARC [MPIF, TXIF, LYR(\\0)+NARC-of-NARC layers, CTA, PLA].
  layer entry types 5 / 13 (and the 0xd sub-block inside type 2) are quad layers:
     u32 type, u32 scale S, u32 nquads, s16 w0,h0, u32 thr, u16 gw,gh, u32 ngroups, then per group
     s16 x,y,w,h + u32 nbatch; per batch u32 bank, u32 nq; per quad 5 x s16 (x,y,w,h in S units, block
     index e) + 3 bytes (palette bank, palette row, flip flags: 1=H, 2=V).
  The quad copies the (w*S x h*S) rectangle at atlas block e ((e % bw)*S, (e // bw)*S) to (x*S, y*S).
"""
from __future__ import annotations

import struct
from pathlib import Path

from nitro_narc import lz10_decompress


def narc_members(b: bytes) -> list[bytes]:
    pos = struct.unpack_from("<H", b, 0xC)[0]
    fat = struct.unpack_from("<I", b, pos + 4)[0]
    cnt = struct.unpack_from("<I", b, pos + 8)[0]
    ent = [struct.unpack_from("<II", b, pos + 12 + i * 8) for i in range(cnt)]
    fnt = pos + fat
    base = fnt + struct.unpack_from("<I", b, fnt + 4)[0] + 8
    return [b[base + s:base + e] for s, e in ent]


def load_banks(tex_lz: Path):
    return banks_from_tex(lz10_decompress(tex_lz.read_bytes()))


def banks_from_tex(raw: bytes):
    import numpy as np
    banks = []
    for o in narc_members(raw[4:]):
        inner = narc_members(o)
        g = next(x for x in inner if x[:4] == b"RGCN")
        p = next(x for x in inner if x[:4] == b"RLCN")
        wt, ht, fmt = struct.unpack_from("<HHI", g, 0x18)
        size = struct.unpack_from("<I", g, 0x28)[0]
        body = np.frombuffer(g[0x30:0x30 + size], dtype=np.uint8)
        px = np.empty(size * 2, dtype=np.uint8)
        px[0::2], px[1::2] = body & 15, body >> 4
        w, h = wt * 8, ht * 8
        n = struct.unpack_from("<I", p, 0x20)[0] // 2
        pal = np.frombuffer(p[0x28:0x28 + 2 * n], dtype="<u2")
        rgba = np.zeros((n, 4), dtype=np.uint8)
        rgba[:, 0] = (pal & 31) * 8
        rgba[:, 1] = ((pal >> 5) & 31) * 8
        rgba[:, 2] = ((pal >> 10) & 31) * 8
        rgba[:, 3] = 255
        banks.append({"w": w, "h": h, "px": px.reshape(h, w), "rgba": rgba})
    return banks


def parse_quad_layer(b: bytes):
    o = 4
    S, _total = struct.unpack_from("<II", b, o); o += 8
    o += 4  # s16 w0,h0
    o += 4  # thr
    gw, gh = struct.unpack_from("<HH", b, o); o += 4
    ng, = struct.unpack_from("<I", b, o); o += 4
    quads = []
    for _ in range(ng):
        _x, _y, _w, _h, nb = struct.unpack_from("<hhhhI", b, o); o += 12
        for _ in range(nb):
            bank, nq = struct.unpack_from("<II", b, o); o += 8
            for _ in range(nq):
                x, y, w, h, e, pb, row, fl = struct.unpack_from("<5h3B", b, o); o += 13
                quads.append((bank, x, y, w, h, e, pb, row, fl))
    if o != len(b):
        raise ValueError(f"quad layer size mismatch: parsed {o} of {len(b)}")
    return S, gw, gh, quads


def layers_of(dat_lz: Path):
    return layers_from_members(narc_members(lz10_decompress(dat_lz.read_bytes())))


def layers_from_members(d: list[bytes]):
    mp = next(m for m in d if m[:4] == b"MPIF")
    mw, mh, cw, ch = struct.unpack_from("<4I", mp, 4)
    lyr = next(m for m in d if m[:4] == b"LYR\x00")
    entries = narc_members(narc_members(lyr[4:])[0])
    out = []
    for e in entries:
        t = struct.unpack_from("<I", e, 0)[0]
        if t in (5, 13):
            out.append(e)
        elif t == 2:
            a = struct.unpack_from("<I", e, 4)[0]
            sub = e[12:12 + a]
            if sub[:4] == struct.pack("<I", 13):
                out.append(sub)
    return (mw, mh, cw), out


def compose_single(map_lz: Path):
    """Single-archive form (e.g. test.map.lz): MPIF, TEX, TXIF, LYR, CTA, PLA in one NARC."""
    d = narc_members(lz10_decompress(map_lz.read_bytes()))
    tex = next(m for m in d if m[:4] == b"TEX\x00")
    return _compose(layers_from_members(d), banks_from_tex(tex))


def compose(dat_lz: Path, tex_lz: Path):
    """Return (width, height, RGBA ndarray, stats)."""
    return _compose(layers_of(dat_lz), load_banks(tex_lz))


def _compose(layers_info, banks):
    import numpy as np
    (mw, mh, _cell), layers = layers_info
    canvas = np.zeros((mh, mw, 4), dtype=np.uint8)
    stats = {"layers": len(layers), "quads": 0, "oob_src": 0, "wrapped": 0, "oob_bank": 0, "clipped": 0, "bad_pal": 0}
    for data in layers:
        S, _gw, _gh, quads = parse_quad_layer(data)
        for bank, x, y, w, h, e, pb, row, fl in quads:
            stats["quads"] += 1
            if bank >= len(banks):
                stats["oob_bank"] += 1
                continue
            bk = banks[bank]
            bw = bk["w"] // S
            u0, v0 = (e % bw) * S, (e // bw) * S
            if w <= 0 or h <= 0 or e < 0 or (e // bw) * S >= bk["h"] * 4 or e // max(bw, 1) >= bk["h"] // S * 4:
                stats["oob_src"] += 1
                continue
            if u0 + w * S > bk["w"] or v0 + h * S > bk["h"]:
                stats["wrapped"] += 1   # DS texture REPEAT: source wraps modulo the bank texture size
            pk = banks[pb] if pb < len(banks) else bk
            if (row + 1) * 16 > len(pk["rgba"]):
                stats["bad_pal"] += 1
                continue
            rows = (v0 + np.arange(h * S)) % bk["h"]
            cols = (u0 + np.arange(w * S)) % bk["w"]
            idx = bk["px"][np.ix_(rows, cols)]
            if fl & 1:
                idx = idx[:, ::-1]
            if fl & 2:
                idx = idx[::-1, :]
            rgba = pk["rgba"][row * 16:(row + 1) * 16][idx]
            x0, y0 = x * S, y * S
            x1, y1 = min(mw, x0 + w * S), min(mh, y0 + h * S)
            if x0 < 0 or y0 < 0 or x1 - x0 != w * S or y1 - y0 != h * S:
                stats["clipped"] += 1
                if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:
                    continue
            sub = rgba[:y1 - y0, :x1 - x0]
            mask = (idx[:y1 - y0, :x1 - x0] != 0)[..., None]
            canvas[y0:y1, x0:x1] = np.where(mask, sub, canvas[y0:y1, x0:x1])
    stats["painted"] = int((canvas[..., 3] > 0).sum())
    return mw, mh, canvas, stats
