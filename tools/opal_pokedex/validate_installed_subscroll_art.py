#!/usr/bin/env python3
"""Validate the first installed Opal Pokédex sub-scroll tile-atlas art patch."""
from pathlib import Path
from PIL import Image

path = Path(__file__).resolve().parents[2] / "res/graphics/pokedex/scroll_sub_background.png"
image = Image.open(path)
assert image.mode == "P" and image.size == (256, 24)
assert len(image.getpalette()) >= 16 * 3
assert max(image.getdata()) < 16, "DS background graphics must remain indexed 4bpp"
# The Opal trim uses existing palette index 14, requiring no new palette bank.
# Keep an explicit observable footprint to prevent accidental rollback.
assert sum(value == 14 for value in image.getdata()) >= 81
print("PASS: installed Pokédex sub-scroll atlas retains indexed geometry and V3 trim")
