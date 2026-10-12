"""Pokemon Ranger 2 ``.ntft`` / ``.ntfp`` 3D-texture pairs (A3I5 / A5I3 + BGR555 palette)."""
from __future__ import annotations

import struct
from pathlib import Path

from .catalog import Unit
from .common import DECODED, STRUCTURAL_ONLY, UNSUPPORTED, sha256_bytes
from .render import Frame, frames_hash


def decode_ntft(raw: bytes, pal: list[int]):
    """Return (mode, width, height, Frame, ambiguous) or raise ValueError.  Width is inferred by row continuity."""
    n = len(raw)
    for mode, mask, ashift, amax in (("A3I5", 31, 5, 7), ("A5I3", 7, 3, 31)):
        if max(b & mask for b in raw) < len(pal):
            break
    else:
        raise ValueError("palette does not cover A3I5 or A5I3 indices")
    alpha = [(b >> ashift) * 255 // amax for b in raw]
    if not any(alpha):
        raise ValueError("fully transparent texture")
    widths = [w for w in (8, 16, 32, 64, 128, 256, 512) if n % w == 0 and n // w >= 8]
    if not widths:
        raise ValueError("no plausible texture width")
    sig = [a + (b & mask) for a, b in zip(alpha, raw)]

    def score(w):
        h = n // w
        d = 0
        for y in range(h - 1):
            d += sum(abs(x - z) for x, z in zip(sig[y * w:(y + 1) * w], sig[(y + 1) * w:(y + 2) * w]))
        return d / (w * (h - 1))
    ranked = sorted((score(w), w) for w in widths)
    w = ranked[0][1]
    ambiguous = len(ranked) > 1 and ranked[1][0] < ranked[0][0] * 1.5
    rgba = bytearray(n * 4)
    for i, b in enumerate(raw):
        c = pal[b & mask]
        a = alpha[i]
        rgba[4 * i:4 * i + 4] = bytes(((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31, a))
    return mode, w, n // w, Frame(w, n // w, bytes(rgba)), ambiguous


def texture_unit(library: str, rel_ntft: str, ntft: bytes, ntfp: bytes | None):
    uid = f"{library}:{rel_ntft}"
    sha = sha256_bytes(ntft)
    base = dict(id=uid, library=library, source=rel_ntft, sha256=sha, type="ds_ntft_texture",
                members=[{"name": rel_ntft, "sha256": sha, "size": len(ntft)}])
    if ntfp is None:
        return Unit(**base, status=STRUCTURAL_ONLY, error_reason=".ntfp palette file missing"), None
    base["members"].append({"name": rel_ntft[:-1] + "p", "sha256": sha256_bytes(ntfp), "size": len(ntfp)})
    pal = list(struct.unpack("<" + "H" * (len(ntfp) // 2), ntfp[: len(ntfp) // 2 * 2]))
    try:
        mode, w, h, frame, amb = decode_ntft(ntft, pal)
    except ValueError as e:
        return Unit(**base, status=UNSUPPORTED, error_reason=f"TEXTURE: {e}"), None
    if amb:
        return Unit(**base, status=STRUCTURAL_ONLY, palette_size=len(pal), dimensions={"min": [w, h], "max": [w, h]},
                    error_reason=f"{mode} indices fit the palette but the texture width is ambiguous (candidates differ by <50%)"), frame
    return Unit(**base, status=DECODED, frame_count=1, palette_size=len(pal), dimensions={"min": [w, h], "max": [w, h]},
                tile_budget=None, oam_budget=None, visual_sha256=frames_hash([frame]), extra={"mode": mode}), frame
