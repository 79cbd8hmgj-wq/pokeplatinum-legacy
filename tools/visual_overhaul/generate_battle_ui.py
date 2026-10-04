#!/usr/bin/env python3

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HEALTHBOX_DIR = ROOT / "res" / "graphics" / "battle" / "healthbox"

# Normal battle healthboxes share the palette generated from player_singles.png.
# Only the chrome entries change here; HP/status colors remain untouched.
CHROME_PALETTE_OVERRIDES = {
    1: (190, 207, 220),  # cool edge highlight
    2: (24, 37, 52),     # deep navy outline
    3: (62, 89, 112),    # steel-blue rail
    4: (232, 241, 247),  # bright highlight
    15: (78, 101, 119),  # slate panel fill
}

PREVIEW_SYNC_FILES = (
    "player_singles.png",
    "player_doubles.png",
    "enemy.png",
    "healthbox_parts.png",
)


def apply_palette(filename: str) -> None:
    path = HEALTHBOX_DIR / filename
    image = Image.open(path)
    palette = list(image.getpalette())

    for index, rgb in CHROME_PALETTE_OVERRIDES.items():
        palette[index * 3:index * 3 + 3] = rgb

    image.putpalette(palette)
    image.save(path)



def make_battle_cursor() -> None:
    """G7.1A focus bracket: bold three-pixel L-corner with a navy keyline.

    The single 16x16 corner cursor is flipped by its NCER for all four corners,
    so cell/animation/OAM data are unchanged.  The shape (not just its color)
    marks focus: a heavy white-edged amber bracket that reads on both the dark
    G7 command deck and the lighter bag/party sub-screens.
    """
    path = ROOT / "res" / "graphics" / "battle" / "interface" / "cursor.png"
    source = Image.open(path)
    palette = list(source.getpalette())
    palette[1 * 3:1 * 3 + 3] = (10, 18, 48)       # keyline
    palette[14 * 3:14 * 3 + 3] = (255, 255, 255)  # outer highlight
    palette[15 * 3:15 * 3 + 3] = (255, 205, 48)   # focus fill

    image = Image.new("P", (16, 16), 0)
    image.putpalette(palette)
    pixels = image.load()

    def in_bracket(x: int, y: int) -> bool:
        return (2 <= x <= 11 and 2 <= y <= 4) or (2 <= x <= 4 and 2 <= y <= 11)

    for y in range(16):
        for x in range(16):
            if in_bracket(x, y):
                pixels[x, y] = 14 if (x == 2 or y == 2) else 15
            elif any(
                in_bracket(x + dx, y + dy)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
            ):
                pixels[x, y] = 1

    image.save(path)


def main() -> None:
    for filename in PREVIEW_SYNC_FILES:
        apply_palette(filename)
    make_battle_cursor()


if __name__ == "__main__":
    main()
