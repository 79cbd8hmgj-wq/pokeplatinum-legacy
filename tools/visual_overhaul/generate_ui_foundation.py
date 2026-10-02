#!/usr/bin/env python3

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WINDOW_DIR = ROOT / "res" / "graphics" / "windows"

# Both standard window images share the palette emitted by standard_system.png.
# Palette index 0 remains the transparent/background entry used by the retail art.
PALETTE_OVERRIDES = {
    0: (0, 197, 0),
    1: (248, 252, 255),  # system fill
    2: (188, 207, 220),  # system highlight
    3: (82, 112, 139),   # system midtone
    4: (28, 45, 66),     # system outline
    6: (190, 246, 238),  # field highlight
    7: (76, 174, 171),   # field midtone
    8: (28, 45, 66),     # field outline
    10: (248, 252, 255), # field fill
}


def shared_palette() -> list[int]:
    source = Image.open(WINDOW_DIR / "standard_system.png")
    palette = list(source.getpalette())

    for index, rgb in PALETTE_OVERRIDES.items():
        palette[index * 3:index * 3 + 3] = rgb

    return palette


def make_window_frame(filename: str, outer: int, mid: int, light: int, fill: int, palette: list[int]) -> None:
    image = Image.new("P", (24, 24), 0)
    image.putpalette(palette)
    pixels = image.load()

    def digit(value: int) -> str:
        return format(value, "X")

    o = digit(outer)
    m = digit(mid)
    l = digit(light)
    f = digit(fill)

    top_left = [
        "00000000",
        "00000000",
        f"000{o}{o}{o}{o}{o}",
        f"00{o}{m}{m}{m}{m}{m}",
        f"00{o}{m}{l}{l}{l}{l}",
        f"00{o}{m}{l}{f}{f}{f}",
        f"00{o}{m}{l}{f}{f}{f}",
        f"00{o}{m}{l}{f}{f}{f}",
    ]

    top = [
        "00000000",
        "00000000",
        o * 8,
        m * 8,
        l * 8,
        f * 8,
        f * 8,
        f * 8,
    ]

    top_right = [row[::-1] for row in top_left]
    left = [f"00{o}{m}{l}{f}{f}{f}"] * 8
    center = [f * 8] * 8
    right = [row[::-1] for row in left]
    bottom_left = list(reversed(top_left))
    bottom = list(reversed(top))
    bottom_right = [row[::-1] for row in bottom_left]

    tiles = [
        [top_left, top, top_right],
        [left, center, right],
        [bottom_left, bottom, bottom_right],
    ]

    for tile_y in range(3):
        for tile_x in range(3):
            tile = tiles[tile_y][tile_x]
            for y, row in enumerate(tile):
                for x, value in enumerate(row):
                    pixels[tile_x * 8 + x, tile_y * 8 + y] = int(value, 16)

    image.save(WINDOW_DIR / filename)


def main() -> None:
    palette = shared_palette()

    # Cleaner, higher-contrast global system frame.
    make_window_frame(
        "standard_system.png",
        outer=4,
        mid=3,
        light=2,
        fill=1,
        palette=palette,
    )

    # Teal field frame using the same 16-color NCLR as standard_system.
    make_window_frame(
        "standard_field.png",
        outer=8,
        mid=7,
        light=6,
        fill=10,
        palette=palette,
    )


if __name__ == "__main__":
    main()
