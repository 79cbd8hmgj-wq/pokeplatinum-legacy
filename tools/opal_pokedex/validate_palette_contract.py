#!/usr/bin/env python3
"""Verify the first Opal Pokédex palette implementation without changing tile contracts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPHICS = ROOT / "res/graphics/pokedex"
EXPECTED = {
    "banner_sinnoh.pal": {0: (222, 211, 238), 5: (142, 125, 181), 11: (207, 179, 114)},
    "banner_national.pal": {0: (222, 211, 238), 5: (142, 125, 181), 11: (150, 141, 140)},
    "banner_default.pal": {0: (220, 207, 232), 5: (121, 101, 160), 15: (236, 215, 154)},
    "info.pal": {0: (224, 216, 233), 1: (99, 85, 123), 12: (145, 116, 172)},
    "search.pal": {0: (225, 214, 234), 3: (79, 57, 105), 11: (228, 192, 213)},
    "register.pal": {0: (225, 214, 234), 8: (208, 175, 109), 13: (126, 82, 125)},
    "background_sub_2.pal": {0: (220, 204, 224), 1: (135, 174, 189), 14: (99, 182, 196)},
    "background_sub_3.pal": {0: (220, 204, 224), 1: (157, 118, 83), 14: (224, 168, 125)},
    "background_scroll_default.pal": {0: (216, 202, 221), 4: (97, 84, 117), 11: (132, 98, 135)},
    "background_scroll_sinnoh.pal": {0: (216, 202, 221), 6: (166, 121, 165), 11: (86, 62, 100)},
    "background_scroll_national.pal": {0: (216, 202, 221), 5: (243, 225, 196), 11: (91, 65, 94)},
    "background_sub_1.pal": {0: (220, 204, 224), 9: (92, 76, 119), 11: (242, 224, 198)},
}

for filename, swatches in EXPECTED.items():
    lines = (GRAPHICS / filename).read_text().strip().splitlines()
    assert lines[:3] == ["JASC-PAL", "0100", "256"], filename
    assert len(lines) == 259, (filename, len(lines))
    palette = [tuple(map(int, line.split())) for line in lines[3:]]
    assert len(palette) == 256
    assert all(len(rgb) == 3 and all(0 <= c <= 255 for c in rgb) for rgb in palette)
    for index, expected in swatches.items():
        assert palette[index] == expected, (filename, index, palette[index])

# Scroll background resources are tile strips, not full LCD-sized images.
# Keep exact source dimensions and indexed four-bit palettes when updating art.
import struct
for name, expected_size in (
    ("scroll_main_background.png", (256, 64)),
    ("scroll_sub_background.png", (256, 24)),
):
    data = (GRAPHICS / name).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", name
    assert struct.unpack_from(">II", data, 16) == expected_size, name
    assert data[24] == 4 and data[25] == 3, f"{name}: expected indexed 4bpp"

print("PASS: Opal Pokédex shared/Sinnoh/National scroll and sub palettes retain 256 indexed RGB entries")
