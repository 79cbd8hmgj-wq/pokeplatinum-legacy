"""GBA decomp battle-animation sprite strips (pokeruby / pokeemerald / pokefirered ``graphics/battle_anims/sprites/*.png``).

These are already indexed PNGs (index 0 = transparent).  A unit is DECODED when the PNG is a valid 4bpp-compatible
indexed image: tile aligned, <= 16 colours, every pixel index inside the palette.  Frame layout lives in C tables,
so ``frame_count`` counts sheets (1) and ``oam_budget`` is null.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from .catalog import Unit
from .common import DECODED, STRUCTURAL_ONLY, UNSUPPORTED, sha256_bytes, sha256_file
from .render import Frame, frames_hash


def png_unit(library: str, root: Path, rel: str):
    path = root / rel
    uid = f"{library}:{rel}"
    sha = sha256_file(path)
    base = dict(id=uid, library=library, source=rel, sha256=sha, type="gba_indexed_png",
                members=[{"name": rel, "sha256": sha, "size": path.stat().st_size}])
    try:
        im = Image.open(path)
        im.load()
    except Exception as e:                                   # noqa: BLE001 - any PIL failure is a decode failure
        return Unit(**base, status=UNSUPPORTED, error_reason=f"PNG_OPEN: {type(e).__name__}: {e}"), None
    if im.mode != "P":
        return Unit(**base, status=UNSUPPORTED, error_reason=f"not an indexed PNG (mode {im.mode})"), None
    w, h = im.size
    pal = im.getpalette() or []
    colours = len(pal) // 3
    idx = im.tobytes()
    top = max(idx) if idx else 0
    if w % 8 or h % 8:
        return Unit(**base, status=STRUCTURAL_ONLY, error_reason=f"{w}x{h} is not 8x8-tile aligned"), None
    if top >= colours:
        return Unit(**base, status=UNSUPPORTED, error_reason=f"pixel index {top} outside {colours}-colour palette"), None
    used = top + 1
    if used > 16:
        return Unit(**base, status=STRUCTURAL_ONLY, palette_size=used,
                    error_reason=f"uses {used} palette entries (> 16): not a 4bpp OBJ sheet"), None
    rgba = bytearray(w * h * 4)
    for i, v in enumerate(idx):
        if v:
            rgba[4 * i:4 * i + 4] = bytes((pal[3 * v], pal[3 * v + 1], pal[3 * v + 2], 255))
    f = Frame(w, h, bytes(rgba))
    if not f.opaque_pixels:
        return Unit(**base, status=STRUCTURAL_ONLY, error_reason="image is entirely transparent"), None
    tiles = sum(1 for ty in range(h // 8) for tx in range(w // 8)
                if any(idx[(ty * 8 + y) * w + tx * 8:(ty * 8 + y) * w + tx * 8 + 8].strip(b"\0") for y in range(8)))
    u = Unit(**base, status=DECODED, frame_count=1, palette_size=used, dimensions={"min": [w, h], "max": [w, h]},
             tile_budget=tiles, oam_budget=None, visual_sha256=frames_hash([f]),
             extra={"index_sha256": sha256_bytes(f"{w}x{h}:".encode() + idx)})
    return u, f
