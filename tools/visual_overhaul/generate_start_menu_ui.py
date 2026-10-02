#!/usr/bin/env python3

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
START_MENU_DIR = ROOT / "res" / "graphics" / "start_menu"


def make_cursor() -> None:
    """Rebuild the 96x32 start-menu selection frame without changing its sprite contract."""
    source = Image.open(START_MENU_DIR / "cursor.png")
    palette = list(source.getpalette())

    image = Image.new("P", (96, 32), 0)
    image.putpalette(palette)
    pixels = image.load()

    accent = 15

    # Two-pixel cut-corner frame. The selected menu icon already supplies
    # animation; this frame is intentionally restrained so the icon remains
    # the visual focus.
    for x in range(8, 88):
        pixels[x, 5] = accent
        pixels[x, 6] = accent
        pixels[x, 25] = accent
        pixels[x, 26] = accent

    for y in range(9, 23):
        pixels[4, y] = accent
        pixels[5, y] = accent
        pixels[90, y] = accent
        pixels[91, y] = accent

    corner_pixels = (
        (5, 8), (6, 7), (7, 6),
        (88, 6), (89, 7), (90, 8),
        (5, 23), (6, 24), (7, 25),
        (88, 25), (89, 24), (90, 23),
    )
    for x, y in corner_pixels:
        pixels[x, y] = accent

    # Small inward chevron at the leading edge makes selection direction
    # obvious without adding another palette entry.
    chevron = (
        (7, 13), (8, 14), (9, 15), (10, 16),
        (9, 17), (8, 18), (7, 19),
    )
    for x, y in chevron:
        pixels[x, y] = accent

    image.save(START_MENU_DIR / "cursor.png")


def main() -> None:
    make_cursor()


if __name__ == "__main__":
    main()
