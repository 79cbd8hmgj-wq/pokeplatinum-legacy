"""Deterministic shape/colour features of decoded frames - used ONLY to *propose* roles for anonymous art.

These numbers are search aids.  A hue/shape heuristic can rank where to look; it can never mark an asset visually approved
(``visual_review.status`` is always ``AWAITING_OWNER_REVIEW`` in the committed outputs).  Requires numpy (host-side only).
"""
from __future__ import annotations

import colorsys
import math

import numpy as np

MAX_FRAMES = 8
HUES = ["red", "orange", "yellow", "lime", "green", "teal", "cyan", "azure", "blue", "purple", "magenta", "pink"]


def _hue_bucket(h: float) -> int:
    # 12 buckets of 30 degrees, centred on the named hue (red = 345..15)
    return int(((h * 360 + 15) % 360) // 30)


def frame_array(f) -> np.ndarray:
    return np.frombuffer(f.rgba, dtype=np.uint8).reshape(f.height, f.width, 4)


def _components(mask: np.ndarray, cap: int = 64) -> int:
    """4-connected component count on a small boolean mask (iterative flood fill, capped)."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    n = 0
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if seen[y0, x0]:
            continue
        n += 1
        if n >= cap:
            return n
        stack = [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
    return n


def frame_features(f) -> dict | None:
    a = frame_array(f)
    alpha = a[:, :, 3] > 32
    if not alpha.any():
        return None
    ys, xs = np.nonzero(alpha)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    bw, bh = int(x1 - x0), int(y1 - y0)
    crop = alpha[y0:y1, x0:x1]
    fill = float(crop.mean())
    # principal-axis elongation of the opaque pixels
    pts = np.stack([xs - xs.mean(), ys - ys.mean()])
    cov = pts @ pts.T / max(len(xs), 1)
    ev = np.sort(np.linalg.eigvalsh(cov))
    elong = float(math.sqrt(max(ev[1], 1e-9) / max(ev[0], 1e-9))) if len(xs) > 3 else 1.0
    # hollow centre (ring/halo): centre 30% of the bbox mostly empty while the outer band is populated
    cy0, cy1 = int(bh * 0.35), max(int(bh * 0.65), int(bh * 0.35) + 1)
    cx0, cx1 = int(bw * 0.35), max(int(bw * 0.65), int(bw * 0.35) + 1)
    centre = float(crop[cy0:cy1, cx0:cx1].mean()) if crop.size else 0.0
    hollow = float(centre < 0.2 and fill > 0.08 and min(bw, bh) >= 8)
    # colour
    rgb = a[:, :, :3][alpha].astype(np.float64) / 255.0
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in rgb[:: max(1, len(rgb) // 400)]])
    sat, val = hsv[:, 1], hsv[:, 2]
    chroma = (sat > 0.28) & (val > 0.28)
    hist = np.zeros(12)
    for h_ in hsv[chroma, 0]:
        hist[_hue_bucket(h_)] += 1
    n = len(hsv)
    return {"bw": bw, "bh": bh, "fill": fill, "elong": elong, "hollow": hollow,
            "components": _components(alpha[:: max(1, bh // 48 or 1), :: max(1, bw // 48 or 1)]),
            "opaque": int(alpha.sum()), "chromatic": float(chroma.mean()),
            "white": float(((sat < 0.2) & (val > 0.75)).sum() / n), "dark": float((val < 0.3).sum() / n),
            "grey": float(((sat < 0.2) & (val >= 0.3) & (val <= 0.75)).sum() / n),
            "bright": float(val.mean()), "hue_hist": (hist / max(hist.sum(), 1)).tolist()}


def unit_features(frames) -> dict:
    """Aggregate over up to MAX_FRAMES evenly-spaced frames (largest opaque area wins ties) - JSON-serialisable."""
    if not frames:
        return {"usable": False}
    idx = sorted({round(i * (len(frames) - 1) / max(MAX_FRAMES - 1, 1)) for i in range(min(len(frames), MAX_FRAMES))})
    fs = [x for x in (frame_features(frames[i]) for i in idx) if x]
    if not fs:
        return {"usable": False}
    def mean(k):
        return round(float(np.mean([x[k] for x in fs])), 3)
    hist = np.mean([x["hue_hist"] for x in fs], axis=0)
    order = np.argsort(-hist)
    dom = [HUES[i] for i in order[:2] if hist[i] > 0.15]
    neutral = max(("white", mean("white")), ("dark", mean("dark")), ("grey", mean("grey")), key=lambda t: t[1])
    biggest = max(fs, key=lambda x: x["opaque"])
    return {"usable": True, "frames_sampled": len(fs), "bw": biggest["bw"], "bh": biggest["bh"], "fill": mean("fill"),
            "elong": mean("elong"), "hollow": mean("hollow"), "components": mean("components"),
            "chromatic": mean("chromatic"), "bright": mean("bright"), "dominant_hues": dom,
            "neutral": neutral[0] if neutral[1] > 0.45 else None, "hue_hist": [round(float(x), 3) for x in hist],
            "varies": len({fr.rgba for fr in (frames[i] for i in idx)}) > 1}
