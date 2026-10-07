"""Helpers for Ranger .ntft/.ntfp DS 3D texture pairs (A3I5 / A5I3 + BGR555 palette)."""
from __future__ import annotations

import struct
from pathlib import Path


def read_ntfp(path: Path) -> list[int]:
    raw = path.read_bytes()
    return list(struct.unpack("<" + "H" * (len(raw) // 2), raw[: len(raw) // 2 * 2]))


def _score(vals: list[int], w: int) -> float:
    h = len(vals) // w
    if h < 2:
        return 1e9
    d = 0
    for y in range(h - 1):
        a, b = vals[y * w:(y + 1) * w], vals[(y + 1) * w:(y + 2) * w]
        d += sum(abs(x - z) for x, z in zip(a, b))
    return d / (w * (h - 1))


def decode_ntft(raw: bytes, pal: list[int]):
    """Return (mode, width, height, [(alpha8, colour555)]) or raise.  Format must be proven by palette coverage."""
    n = len(raw)
    for mode, ishift_mask, ashift, amax in (("A3I5", 31, 5, 7), ("A5I3", 7, 3, 31)):
        idx = [b & ishift_mask for b in raw]
        if max(idx) < len(pal):
            break
    else:
        raise ValueError("palette does not cover A3I5/A5I3 indices")
    alpha = [(b >> ashift) * 255 // amax for b in raw]
    if not any(alpha):
        raise ValueError("fully transparent texture")
    widths = [w for w in (8, 16, 32, 64, 128, 256, 512) if n % w == 0 and n // w >= 8]
    if not widths:
        raise ValueError("no plausible width")
    # row-continuity of alpha*index decides the width; ties prefer squares
    sig = [a + i for a, i in zip(alpha, idx)]
    scored = sorted((_score(sig, w), abs((n // w).bit_length() - w.bit_length()), w) for w in widths)
    w = scored[0][2]
    return mode, w, n // w, [(a, pal[i]) for a, i in zip(alpha, idx)], scored[:2]
