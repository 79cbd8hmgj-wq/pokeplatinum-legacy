#!/usr/bin/env python3
"""Minimal NSBMD/BMD0 (MDL0 + TEX0) previewer for evidence work. Not a converter, not a general renderer.

Decodes TEX0 textures (formats 1-7) and MDL0 shape display lists (positions/texcoords, no skinning, no node transforms),
then rasterises a flat-lit, textured 3/4 view with a z-buffer. Good enough to judge whether a model family is
architecture / props / terrain and how it relates to Platinum's own models. Reads files only; modifies nothing.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field

import numpy as np
from PIL import Image


def u16(d, o): return struct.unpack_from("<H", d, o)[0]
def u32(d, o): return struct.unpack_from("<I", d, o)[0]
def s16(d, o): return struct.unpack_from("<h", d, o)[0]
def s32(d, o): return struct.unpack_from("<i", d, o)[0]


def read_dict(d: bytes, p: int, unit_fmt=None):
    """Nitro 3D dictionary at p -> list of (name, data_bytes)."""
    n = d[p + 1]
    q = p + 8 + (n + 1) * 4
    unit, _size = u16(d, q), u16(d, q + 2)
    data0 = q + 4
    names0 = data0 + n * unit
    out = []
    for i in range(n):
        name = d[names0 + 16 * i: names0 + 16 * i + 16].split(b"\0")[0].decode("latin1")
        out.append((name, d[data0 + unit * i: data0 + unit * (i + 1)]))
    return out


def c555(v):
    return ((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31)


@dataclass
class Tex:
    name: str
    w: int
    h: int
    fmt: int
    rgba: np.ndarray | None = None
    pal_name: str | None = None


def parse_tex0(d: bytes, base: int):
    assert d[base:base + 4] == b"TEX0"
    tex_off = base + u32(d, base + 0x14)
    comp_data = base + u32(d, base + 0x24)
    comp_idx = base + u32(d, base + 0x28)
    pal_data = base + u32(d, base + 0x38)
    texd = read_dict(d, base + u16(d, base + 0x0E))
    pald = read_dict(d, base + u32(d, base + 0x34))
    pals = {}
    for i, (n, e) in enumerate(pald):
        pals[n] = (u16(e, 0) << 3, i)
    pal_order = [n for n, _ in pald]
    texs = {}
    for i, (n, e) in enumerate(texd):
        off = u16(e, 0) << 3
        prm = u16(e, 2)
        wl, hl, fmt, c0 = (prm >> 4) & 7, (prm >> 7) & 7, (prm >> 10) & 7, (prm >> 13) & 1
        w, h = 8 << wl, 8 << hl
        texs[n] = dict(name=n, w=w, h=h, fmt=fmt, c0=c0, off=off, idx=i)
    return dict(texs=texs, tex_off=tex_off, comp=comp_data, comp_idx=comp_idx, pal_data=pal_data, pals=pals, pal_order=pal_order, texd=[n for n, _ in texd])


def decode_tex(d: bytes, T, tex, pal_name: str | None):
    w, h, fmt = tex["w"], tex["h"], tex["fmt"]
    pals = T["pals"]
    if pal_name not in pals:
        nm = tex["name"]
        pick = next((c for c in (nm, nm + "_pl", nm + "_p", nm + "_pal", nm.rstrip("0123456789_") + "_pl") if c in pals), None)
        if pick is None and len(T["pal_order"]) == len(T["texd"]):
            pick = T["pal_order"][tex["idx"]]
        pal_name = pick or (T["pal_order"][0] if T["pal_order"] else None)
    pal = []
    if pal_name is not None:
        po = T["pal_data"] + pals[pal_name][0]
        n = {1: 32, 2: 4, 3: 16, 4: 256, 5: 0, 6: 8}.get(fmt, 0)
        if fmt == 5:
            n = 2048
        end = min(len(d), po + 2 * n)
        pal = [u16(d, o) for o in range(po, end - 1, 2)]
    out = np.zeros((h, w, 4), np.uint8)
    off = T["tex_off"] + tex["off"]
    if fmt == 7:
        for i in range(w * h):
            v = u16(d, off + 2 * i)
            r, g, b = c555(v)
            out[i // w, i % w] = (r, g, b, 255 if v & 0x8000 else 0)
        return out
    if fmt == 5:
        coff = T["comp"] + tex["off"]
        ioff = T["comp_idx"] + (tex["off"] >> 1)
        bw = w // 4
        for by in range(h // 4):
            for bx in range(bw):
                b = by * bw + bx
                blk = u32(d, coff + 4 * b)
                inf = u16(d, ioff + 2 * b)
                po = T["pal_data"] + (pals[pal_name][0] if pal_name in pals else 0) + (inf & 0x3FFF) * 4
                cc = [u16(d, po + 2 * k) if po + 2 * k + 2 <= len(d) else 0 for k in range(2)]
                c0, c1 = c555(cc[0]), c555(cc[1])
                mode = inf >> 14
                c2v = [u16(d, po + 2 * k) if po + 2 * k + 2 <= len(d) else 0 for k in range(4)]
                if mode == 0:
                    pl = [c0, c1, c555(c2v[2]), None]
                elif mode == 1:
                    pl = [c0, c1, tuple((a + b2) // 2 for a, b2 in zip(c0, c1)), None]
                elif mode == 2:
                    pl = [c0, c1, c555(c2v[2]), c555(c2v[3])]
                else:
                    pl = [c0, c1, tuple((5 * a + 3 * b2) // 8 for a, b2 in zip(c0, c1)), tuple((3 * a + 5 * b2) // 8 for a, b2 in zip(c0, c1))]
                for ty in range(4):
                    row = (blk >> (8 * ty)) & 0xFF
                    for tx in range(4):
                        c = pl[(row >> (2 * tx)) & 3]
                        out[by * 4 + ty, bx * 4 + tx] = (0, 0, 0, 0) if c is None else (*c, 255)
        return out
    bits = {1: 8, 2: 2, 3: 4, 4: 8, 6: 8}[fmt]
    n = w * h
    raw = np.frombuffer(d, np.uint8, count=max(0, min(len(d) - off, n * bits // 8)), offset=off)
    if fmt in (1, 6):
        mask, sh, amax = (31, 5, 7) if fmt == 1 else (7, 3, 31)
        idx, alpha = raw & mask, (raw >> sh).astype(np.int32) * 255 // amax
    else:
        per = 8 // bits
        idx = np.stack([(raw >> (bits * k)) & ((1 << bits) - 1) for k in range(per)], axis=1).reshape(-1)
        alpha = np.full(idx.shape, 255, np.int32)
        if tex["c0"]:
            alpha[idx == 0] = 0
    if len(idx) < n:
        idx = np.pad(idx, (0, n - len(idx)))
        alpha = np.pad(alpha, (0, n - len(alpha)))
    palrgb = np.array([c555(v) for v in pal] or [(255, 0, 255)], np.uint8)
    idx = np.minimum(idx[:n].astype(np.int32), len(palrgb) - 1)
    out[..., :3] = palrgb[idx].reshape(h, w, 3)
    out[..., 3] = alpha[:n].reshape(h, w)
    return out


def parse_dl(dl: bytes, scale: float):
    """Display list -> list of triangles [(pos(3), uv(2))*3] plus texture-param changes ignored."""
    tris = []
    p = 0
    PARAMS = {0x10: 1, 0x11: 0, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 0, 0x16: 16, 0x17: 12, 0x18: 16, 0x19: 12, 0x1A: 9, 0x1B: 3, 0x1C: 3, 0x20: 1, 0x21: 1, 0x22: 1,
              0x23: 2, 0x24: 1, 0x25: 1, 0x26: 1, 0x27: 1, 0x28: 1, 0x29: 1, 0x2A: 1, 0x2B: 1, 0x30: 1, 0x31: 1, 0x32: 1, 0x33: 1, 0x34: 32, 0x40: 1, 0x41: 0, 0x50: 1,
              0x60: 1, 0x70: 3, 0x71: 2, 0x72: 1}
    vt, verts, uv, cur = 0, [], (0.0, 0.0), [0.0, 0.0, 0.0]

    def flush():
        nonlocal verts
        v = verts
        if vt == 0:
            for i in range(0, len(v) - 2, 3):
                tris.append((v[i], v[i + 1], v[i + 2]))
        elif vt == 1:
            for i in range(0, len(v) - 3, 4):
                tris.append((v[i], v[i + 1], v[i + 2]))
                tris.append((v[i], v[i + 2], v[i + 3]))
        elif vt == 2:
            for i in range(len(v) - 2):
                tris.append((v[i], v[i + 1], v[i + 2]) if i % 2 == 0 else (v[i + 1], v[i], v[i + 2]))
        elif vt == 3:
            for i in range(0, len(v) - 3, 2):
                tris.append((v[i], v[i + 1], v[i + 3]))
                tris.append((v[i], v[i + 3], v[i + 2]))
        verts = []

    def emit():
        verts.append((tuple(c * scale for c in cur), uv))

    while p + 4 <= len(dl):
        cmds = dl[p:p + 4]
        p += 4
        for c in cmds:
            if c == 0:
                continue
            n = PARAMS.get(c)
            if n is None:
                return tris
            prm = dl[p:p + 4 * n]
            p += 4 * n
            if len(prm) < 4 * n:
                return tris
            if c == 0x40:
                vt = u32(prm, 0) & 3
                verts = []
            elif c == 0x41:
                flush()
            elif c == 0x22:
                v = u32(prm, 0)
                uv = (s16(prm, 0) / 16.0, s16(prm, 2) / 16.0)
            elif c == 0x23:
                cur = [s16(prm, 0) / 4096.0, s16(prm, 2) / 4096.0, s16(prm, 4) / 4096.0]
                emit()
            elif c == 0x24:
                v = u32(prm, 0)
                f = lambda sh: (((v >> sh) & 0x3FF) - (0x400 if (v >> sh) & 0x200 else 0)) / 64.0
                cur = [f(0), f(10), f(20)]
                emit()
            elif c in (0x25, 0x26, 0x27):
                x, y = s16(prm, 0) / 4096.0, s16(prm, 2) / 4096.0
                if c == 0x25:
                    cur[0], cur[1] = x, y
                elif c == 0x26:
                    cur[0], cur[2] = x, y
                else:
                    cur[1], cur[2] = x, y
                emit()
            elif c == 0x28:
                v = u32(prm, 0)
                g = lambda sh: (((v >> sh) & 0x3FF) - (0x400 if (v >> sh) & 0x200 else 0)) / 4096.0
                cur = [cur[0] + g(0), cur[1] + g(10), cur[2] + g(20)]
                emit()
    return tris


def parse_bmd(d: bytes):
    assert d[:4] == b"BMD0" or d[:4] == b"BTX0", d[:4]
    nblk = u16(d, 0x0E)
    offs = [u32(d, 0x10 + 4 * i) for i in range(nblk)]
    mdl, tex = None, None
    for o in offs:
        if d[o:o + 4] == b"MDL0":
            mdl = o
        elif d[o:o + 4] == b"TEX0":
            tex = o
    return mdl, tex


def parse_models(d: bytes, mdl: int):
    out = []
    for name, e in read_dict(d, mdl + 8):
        m = mdl + u32(e, 0)
        sbc, mat, shp = m + u32(d, m + 4), m + u32(d, m + 8), m + u32(d, m + 12)
        pos_scale = s32(d, m + 0x1C) / 4096.0
        nshp = d[m + 0x19]
        nmat = d[m + 0x18]
        # materials: texture-pair dict -> {texname: [material ids]}
        texmap, palmap = {}, {}
        for off_field, target in ((0, texmap), (2, palmap)):
            do = mat + u16(d, mat + off_field)
            try:
                for nm, ee in read_dict(d, do):
                    lo, cnt = u16(ee, 0), ee[2]
                    target[nm] = list(d[mat + lo: mat + lo + cnt])
            except Exception:  # noqa: BLE001
                pass
        shapes = []
        for sn, se in read_dict(d, shp + 0 if False else shp + 0):
            pass
        for sn, se in read_dict(d, shp):
            so = shp + u32(se, 0)
            dlo, dls = so + u32(d, so + 8), u32(d, so + 12)
            shapes.append((sn, d[dlo:dlo + dls]))
        shape_mat, cur, p = {}, None, sbc
        PAR = {0: 0, 2: 2, 3: 1, 4: 1, 5: 1, 7: 1, 8: 1, 0x0B: 0}
        while p < len(d):
            op = d[p]
            base = op & 0x1F
            p += 1
            if base == 1:
                break
            if base == 6:
                p += 3 + (1 if op & 0x20 else 0) + (1 if op & 0x40 else 0)
                continue
            if base not in PAR:
                break
            prm = d[p:p + PAR[base]]
            p += PAR[base]
            if base == 4:
                cur = prm[0]
            elif base == 5 and cur is not None:
                shape_mat.setdefault(prm[0], cur)
        out.append(dict(name=name, scale=pos_scale, shape_mat=shape_mat, nmat=nmat, shapes=shapes, texmap=texmap, palmap=palmap))
    return out


def render_model(d: bytes, size=160, yaw=35.0, pitch=28.0, max_tris=20000):
    mdl, tex = parse_bmd(d)
    models = parse_models(d, mdl)
    T = parse_tex0(d, tex) if tex else None
    m = models[0]
    # material -> texture
    mat_tex, mat_pal = {}, {}
    for tn, ids in m["texmap"].items():
        for i in ids:
            mat_tex[i] = tn
    for pn, ids in m["palmap"].items():
        for i in ids:
            mat_pal[i] = pn
    cache = {}

    def tex_for(i):
        if T is None:
            return None
        tn = mat_tex.get(i)
        if tn is None or tn not in T["texs"]:
            return None
        key = (tn, mat_pal.get(i))
        if key not in cache:
            cache[key] = decode_tex(d, T, T["texs"][tn], mat_pal.get(i))
        return cache[key]

    all_tris = []
    for si, (sn, dl) in enumerate(m["shapes"]):
        tr = parse_dl(dl, m["scale"])
        all_tris += [(t, si) for t in tr]
    stats = dict(shapes=len(m["shapes"]), tris=len(all_tris), textures=len(T["texs"]) if T else 0,
                 tex_sizes=sorted({(t["w"], t["h"], t["fmt"]) for t in T["texs"].values()}) if T else [], materials=m["nmat"])
    if not all_tris:
        return None, stats
    pts = np.array([v[0] for t, _ in all_tris for v in t])
    c = (pts.min(0) + pts.max(0)) / 2
    ext = float(np.abs(pts - c).max()) or 1.0
    ya, pa = math.radians(yaw), math.radians(pitch)
    Ry = np.array([[math.cos(ya), 0, math.sin(ya)], [0, 1, 0], [-math.sin(ya), 0, math.cos(ya)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(pa), -math.sin(pa)], [0, math.sin(pa), math.cos(pa)]])
    R = Rx @ Ry
    img = np.zeros((size, size, 4), np.uint8)
    img[..., :3] = (70, 80, 110)
    img[..., 3] = 255
    zb = np.full((size, size), -1e9)
    L = np.array([0.4, 0.8, 0.45])
    L /= np.linalg.norm(L)
    s = (size * 0.46) / ext
    for (tri, si) in all_tris[:max_tris]:
        P = [(R @ (np.array(v[0]) - c)) for v in tri]
        n = np.cross(np.array(tri[1][0]) - np.array(tri[0][0]), np.array(tri[2][0]) - np.array(tri[0][0]))
        ln = np.linalg.norm(n)
        shade = 0.55 + 0.45 * abs(float(n @ L) / ln) if ln > 0 else 0.8
        sp = np.array([[p[0] * s + size / 2, -p[1] * s + size / 2, p[2]] for p in P])
        x0, x1 = int(max(0, math.floor(sp[:, 0].min()))), int(min(size - 1, math.ceil(sp[:, 0].max())))
        y0, y1 = int(max(0, math.floor(sp[:, 1].min()))), int(min(size - 1, math.ceil(sp[:, 1].max())))
        if x1 < x0 or y1 < y0:
            continue
        a, b, cc = sp[0, :2], sp[1, :2], sp[2, :2]
        den = (b[1] - cc[1]) * (a[0] - cc[0]) + (cc[0] - b[0]) * (a[1] - cc[1])
        if abs(den) < 1e-9:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l0 = ((b[1] - cc[1]) * (xs - cc[0]) + (cc[0] - b[0]) * (ys - cc[1])) / den
        l1 = ((cc[1] - a[1]) * (xs - cc[0]) + (a[0] - cc[0]) * (ys - cc[1])) / den
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
        if not inside.any():
            continue
        z = l0 * sp[0, 2] + l1 * sp[1, 2] + l2 * sp[2, 2]
        tx = tex_for(m["shape_mat"].get(si, si))
        if tx is not None:
            u = l0 * tri[0][1][0] + l1 * tri[1][1][0] + l2 * tri[2][1][0]
            v = l0 * tri[0][1][1] + l1 * tri[1][1][1] + l2 * tri[2][1][1]
            th, tw = tx.shape[:2]
            col = tx[np.mod(np.floor(v).astype(int), th), np.mod(np.floor(u).astype(int), tw)]
        else:
            col = np.zeros(xs.shape + (4,), np.uint8)
            col[...] = (170, 170, 170, 255)
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        ok = inside & (z > sub) & (col[..., 3] > 127)
        sub[ok] = z[ok]
        reg = img[y0:y1 + 1, x0:x1 + 1]
        reg[ok, :3] = (col[..., :3][ok] * shade).astype(np.uint8)
    return Image.fromarray(img, "RGBA"), stats
