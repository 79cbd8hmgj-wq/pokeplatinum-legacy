"""RGBA frame helpers and deterministic contact-sheet composition (Pillow)."""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw

from .common import sha256_bytes


@dataclass
class Frame:
    width: int
    height: int
    rgba: bytes                       # width*height*4

    def image(self) -> Image.Image:
        return Image.frombytes("RGBA", (self.width, self.height), self.rgba)

    @property
    def opaque_pixels(self) -> int:
        return sum(1 for i in range(3, len(self.rgba), 4) if self.rgba[i])


def indexed_to_frame(w: int, h: int, px: bytes, palette_rgb: list[tuple[int, int, int]]) -> Frame:
    """Resolve palette indices (0 = transparent) to RGBA.  Raises IndexError on an out-of-range index (caller maps it)."""
    out = bytearray(w * h * 4)
    for i, v in enumerate(px):
        if v:
            r, g, b = palette_rgb[v]
            out[4 * i:4 * i + 4] = bytes((r, g, b, 255))
    return Frame(w, h, bytes(out))


def frames_hash(frames: list[Frame]) -> str:
    return sha256_bytes(b"|".join(f"{f.width}x{f.height}:".encode() + sha256_bytes(f.rgba).encode() for f in frames))


def contact_sheet(frames: list[Frame], labels: list[str] | None = None, cell: int = 0, columns: int = 8,
                  scale: int = 2, bg=(48, 48, 56), pad: int = 4) -> Image.Image:
    """Grid of frames, each centred in a uniform cell on a neutral background with a checker under transparency."""
    if not frames:
        return Image.new("RGB", (8, 8), bg)
    m = cell or max(max(f.width, f.height) for f in frames)
    m = max(m, 8)
    cs = m * scale
    cols = max(1, min(columns, len(frames)))
    rows = (len(frames) + cols - 1) // cols
    label_h = 10 if labels else 0
    sheet = Image.new("RGB", (cols * (cs + pad) + pad, rows * (cs + pad + label_h) + pad), bg)
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        cx = pad + (i % cols) * (cs + pad)
        cy = pad + (i // cols) * (cs + pad + label_h)
        tile = Image.new("RGB", (cs, cs), (88, 88, 96))
        td = ImageDraw.Draw(tile)
        for y in range(0, cs, 8):
            for x in range(0, cs, 8):
                if (x // 8 + y // 8) % 2:
                    td.rectangle((x, y, x + 7, y + 7), fill=(104, 104, 112))
        img = f.image()
        if scale != 1:
            img = img.resize((f.width * scale, f.height * scale), Image.NEAREST)
        if img.width > cs or img.height > cs:
            img = img.crop((0, 0, min(img.width, cs), min(img.height, cs)))
        tile.paste(img, ((cs - img.width) // 2, (cs - img.height) // 2), img)
        sheet.paste(tile, (cx, cy))
        if labels:
            d.text((cx, cy + cs), labels[i][:max(4, cs // 6)], fill=(210, 210, 210))
    return sheet


def save_png(img: Image.Image, path) -> None:
    """Deterministic PNG (no timestamps / metadata)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=False, compress_level=9)
