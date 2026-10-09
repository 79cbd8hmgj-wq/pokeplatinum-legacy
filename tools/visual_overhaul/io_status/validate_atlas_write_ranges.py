#!/usr/bin/env python3
"""Check conservative battler/shadow CPU atlas write ranges against candidate 16px glyph strips.
Source constants are verified to fail closed if upstream layout changes.
Not a runtime/3D-palette test.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
SRC = (ROOT / "src/pokemon_sprite.c").read_text()

expected = {
    "MON_SPRITE_CHAR_BUF_TILES_W": 32,
    "MON_SPRITE_CHAR_BUF_TILES_H": 32,
    "MAN_Y_OFFSET": 0x80,
    "MAN_CHAR_OFFSET": 0x2800,
    "MAN_LAST_SPRITE_CHAR_OFFSET_1": 0x50,
    "MAN_LAST_SPRITE_CHAR_OFFSET_2": 0x2828,
    "MAN_SHADOW_CHAR_OFFSET": 0x5050,
}
for name, value in expected.items():
    m = re.search(r"^#define\s+" + name + r"\s+(0x[0-9A-Fa-f]+|\d+)\b", SRC, re.M)
    assert m and int(m.group(1), 0) == value, f"source layout changed: {name}"
assert "MI_CpuFill8(&monSpriteMan->charRawData[0], rawCharData[0], MON_SPRITE_CHAR_BUF_SIZE)" in SRC
assert "NNS_G2dLoadImage2DMapping(&monSpriteMan->charData" in SRC
# The loops and offsets must match this interpretation. Fail on changes.
for fragment in (
    "for (y = 0; y < MON_SPRITE_HEIGHT; y++)",
    "for (x = 0; x < MON_SPRITE_WIDTH / 2; x++)",
    "for (i = 0; i < MON_SPRITE_HEIGHT; i++)",
    "for (j = 0; j < MON_SPRITE_WIDTH / 4; j++)",
    "y * MAN_Y_OFFSET + x + i * MAN_CHAR_OFFSET",
    "y * MAN_Y_OFFSET + x + MAN_LAST_SPRITE_CHAR_OFFSET_1",
    "y * MAN_Y_OFFSET + x + MAN_LAST_SPRITE_CHAR_OFFSET_2",
    "i * MAN_Y_OFFSET + j + MAN_SHADOW_CHAR_OFFSET",
):
    assert fragment in SRC, f"source pattern changed: {fragment}"

STRIDE = 128  # bytes per 256-pixel row in 4bpp texture
SIZE = 32768
writes = {}

def reserve(label, indices):
    for pos in indices:
        assert 0 <= pos < SIZE, (label, pos)
        writes.setdefault(pos, set()).add(label)

# Each frame is 80x80; two frames side by side => 40 bytes/row.
for battler in range(3):
    reserve(f"battler{battler}", (y * STRIDE + battler * 0x2800 + x for y in range(80) for x in range(40)))
# Fourth battler uses two distinct byte offsets for its frame halves.
reserve("battler3_left", (y * STRIDE + 0x50 + x for y in range(80) for x in range(20)))
reserve("battler3_right", (y * STRIDE + 0x2828 + x for y in range(80) for x in range(20, 40)))
reserve("shadows", (y * STRIDE + 0x5050 + x for y in range(80) for x in range(40)))
collisions = {k: v for k, v in writes.items() if len(v) > 1}
assert not collisions, f"unexpected overlapping battler/shadow atlas writes: {len(collisions)}"

def rect_is_free(x, y, width=16, height=16):
    assert x % 2 == 0 and 0 <= x <= 256 - width and 0 <= y <= 256 - height
    return all(row * STRIDE + byte not in writes
               for row in range(y, y + height)
               for byte in range(x // 2, (x + width) // 2))

# Two 16x16 frames per glyph, two glyphs = four disjoint rectangles.
# Place all on bottom 16-pixel strip, where no battler/shadow write occurs.
glyph_rects = [(0, 240), (16, 240), (32, 240), (48, 240)]
assert all(rect_is_free(x, y) for x, y in glyph_rects)
assert len(writes) == 16000, len(writes)
print(f"PASS: {len(writes)} / {SIZE} bytes occupied by modeled sprite/shadow writes")
print("PASS: glyph 16x16 rectangles in bottom strip:", glyph_rects)
print("CONSTRAINT: atlas is initially fully filled; glyphs must be inserted AFTER initialization, and uploaded through the owned texture path.")
print("NOT PROVEN: dynamic palette allocation, 3D display timing, or runtime visual correctness.")
