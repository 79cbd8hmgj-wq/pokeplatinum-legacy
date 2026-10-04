#!/usr/bin/env python3
"""Validate the G7.2A battle healthbox chrome.

The healthbox refresh is palette-only: pixel indices (geometry), cell data and
every non-chrome palette entry (HP-state, status, white, black) must stay
identical to retail, and the new chrome must give the white name/HP glyphs a
high-contrast field.
"""

import hashlib
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HEALTHBOX = ROOT / "res" / "graphics" / "battle" / "healthbox"

INDEX_DIGESTS = {
    "player_singles.png": "0c4e5ef045f5b56e7886d8c280fd61c714c5941485515fd4184458de903ebf84",
    "enemy.png": "be3e2d64a128c5c9f939811c6d010adf3fb2143fd1d46fc2c8ad2e95a540d3bf",
    "player_doubles.png": "cfdf8d6cc3e027b8bb7b4f9f7b3379ed9d508a358845940edbc866bb672b1a2b",
    "healthbox_parts.png": "239606e37588edb2e69292ab5136273c2c0a710a383215b53546ecb7fb493aec",
}
SIZES = {
    "player_singles.png": (128, 64),
    "enemy.png": (128, 64),
    "player_doubles.png": (128, 64),
    "healthbox_parts.png": (624, 8),
}
# Entries that carry gameplay information or glyph colors and must not move.
KEEP = {
    0: (156, 180, 238),
    5: (0, 0, 0),
    6: (24, 197, 32),
    7: (189, 115, 0),
    8: (238, 172, 0),
    9: (172, 49, 16),
    10: (255, 65, 16),
    11: (24, 98, 189),
    12: (65, 148, 230),
    13: (222, 65, 205),
    14: (255, 255, 255),
}
# Retail (G5) values of the entries G7.2A retunes, used for "no worse than" checks.
G5_CHROME = {3: (62, 89, 112), 15: (78, 101, 119)}
NEW_CHROME = {
    1: (176, 208, 236),
    2: (12, 20, 40),
    3: (46, 70, 98),
    4: (236, 244, 250),
    15: (36, 54, 80),
}

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def luminance(rgb):
    def chan(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main():
    palettes = {}
    for name, digest in INDEX_DIGESTS.items():
        image = Image.open(HEALTHBOX / name)
        check(image.size == SIZES[name], f"{name}: size changed to {image.size}")
        check(image.mode == "P", f"{name}: not indexed")
        check(hashlib.sha256(image.tobytes()).hexdigest() == digest,
              f"{name}: pixel indices changed (palette-only pass)")
        pal = image.getpalette()
        palettes[name] = [tuple(pal[i * 3:i * 3 + 3]) for i in range(16)]

    reference = palettes["player_singles.png"]
    for name, pal in palettes.items():
        check(pal == reference, f"{name}: preview palette differs from player_singles.png")
    for index, color in KEEP.items():
        check(reference[index] == color, f"palette entry {index} changed: {reference[index]}")
    for index, color in NEW_CHROME.items():
        check(reference[index] == color, f"chrome entry {index} is not the G7.2A value")

    white = reference[14]
    check(contrast(white, reference[15]) >= 7.0, "white vs panel fill contrast < 7:1")
    check(contrast(white, reference[3]) >= 5.0, "white vs steel rail contrast < 5:1")
    check(contrast(reference[2], reference[15]) >= 1.2, "outline indistinguishable from fill")
    check(contrast(reference[4], reference[15]) >= 7.0, "bright edge vs fill contrast < 7:1")
    # HP-state / status colors must separate from the retuned rail and panel at
    # least as well as they did against the G5 chrome.
    for index in (6, 7, 8, 9, 10):
        for chrome in (3, 15):
            before = contrast(reference[index], G5_CHROME[chrome])
            after = contrast(reference[index], reference[chrome])
            check(after >= before - 0.05,
                  f"HP/status color {index} separates worse from entry {chrome} "
                  f"({after:.2f} < {before:.2f})")

    if failures:
        print("G7.2A battle HUD validation FAILED:")
        for failure in failures:
            print(" -", failure)
        sys.exit(1)
    print("G7.2A battle HUD validation passed")


if __name__ == "__main__":
    main()
