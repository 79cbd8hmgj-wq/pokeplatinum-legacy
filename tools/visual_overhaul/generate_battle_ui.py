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


def main() -> None:
    for filename in PREVIEW_SYNC_FILES:
        apply_palette(filename)


if __name__ == "__main__":
    main()
