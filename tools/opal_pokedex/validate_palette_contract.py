#!/usr/bin/env python3
"""Verify the first Opal Pokédex palette implementation without changing tile contracts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPHICS = ROOT / "res/graphics/pokedex"
EXPECTED = {
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

print("PASS: Opal Pokédex scroll/sub palettes retain 256 indexed RGB entries")
