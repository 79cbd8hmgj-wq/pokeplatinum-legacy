"""Offline, deterministic renderer for SPL replays (orthographic front view, normal alpha blend, texture x vertex-colour modulate).

This is a *preview of the decoded state*, not a re-implementation of the Nitro 3D pipeline: no depth sort, no polygon-ID rules, no
polygon/directional draw types, fixed camera. It exists so a human can judge whether the reconstructed motion is plausible.
"""
from __future__ import annotations

import hashlib

from PIL import Image

from dau1 import spl as dspl

W, H = 256, 192
BG = (24, 26, 36)


def bgr555(c):
    return ((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31)


def extent(rp) -> float:
    m = 1.0
    for fr in rp.frames:
        for p in fr:
            m = max(m, abs(p["x"]) / 4096, abs(p["y"]) / 4096)
    return m


def pixel_scale(rp) -> float:
    """World-unit -> pixel factor: fit the replay's extent into ~80 px radius, capped so unit-sized quads stay visible."""
    return round(min(80.0 / extent(rp), 48.0), 3)


def render_frame(snap, textures, scale, ox=W // 2, oy=H * 3 // 5) -> Image.Image:
    canvas = Image.new("RGBA", (W, H), BG + (255,))
    for p in sorted(snap, key=lambda q: q["z"]):
        tex = textures[p["texture"]] if p["texture"] < len(textures) else None
        a = max(0, min(31, p["alpha31"])) / 31.0
        if a <= 0:
            continue
        w = max(1, int(2 * p["sx"] / 4096 * scale))
        h = max(1, int(2 * p["sy"] / 4096 * scale))
        if w > 400 or h > 400:
            continue
        if tex is None or tex.frame is None:
            continue
        im = tex.frame.image().resize((w, h), Image.NEAREST)
        r, g, b = bgr555(p["color"])
        px = im.load()
        out = Image.new("RGBA", im.size)
        op = out.load()
        for y in range(h):
            for x in range(w):
                cr, cg, cb, ca = px[x, y]
                op[x, y] = (cr * r // 255, cg * g // 255, cb * b // 255, int(ca * a))
        if p["rotation"]:
            out = out.rotate(-p["rotation"] * 360.0 / 65536.0, resample=Image.NEAREST, expand=True)
        cx = ox + int(p["x"] / 4096 * scale) - out.width // 2
        cy = oy - int(p["y"] / 4096 * scale) - out.height // 2
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(out, (cx, cy))
        canvas = Image.alpha_composite(canvas, layer)
    return canvas.convert("RGB")


def frames_hash(imgs) -> str:
    h = hashlib.sha256()
    for im in imgs:
        h.update(im.tobytes())
    return h.hexdigest()


def render_replay(data: bytes, rp, frames_to_render=None):
    arch = dspl.parse_spl(data)
    scale = pixel_scale(rp)
    idx = frames_to_render if frames_to_render is not None else list(range(len(rp.frames)))
    imgs = [render_frame(rp.frames[i], arch.textures, scale) for i in idx]
    undecoded = sorted({p["texture"] for fr in rp.frames for p in fr if p["texture"] >= len(arch.textures) or arch.textures[p["texture"]].frame is None})
    return imgs, scale, undecoded


def timeline_sheet(imgs, labels, cols=6) -> Image.Image:
    from PIL import ImageDraw
    rows = (len(imgs) + cols - 1) // cols
    cw, ch = W // 2, H // 2
    sheet = Image.new("RGB", (cols * (cw + 4) + 4, rows * (ch + 14) + 4), (12, 12, 18))
    d = ImageDraw.Draw(sheet)
    for n, (im, lb) in enumerate(zip(imgs, labels)):
        x, y = 4 + (n % cols) * (cw + 4), 4 + (n // cols) * (ch + 14)
        sheet.paste(im.resize((cw, ch), Image.NEAREST), (x, y))
        d.text((x, y + ch), lb, fill=(200, 200, 205))
    return sheet
