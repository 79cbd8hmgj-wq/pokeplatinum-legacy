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



def make_scroll_cursor(palette: list[int]) -> None:
    """Build the 12-frame 8x8 scroll cursor strip without changing its resource contract."""
    frame_count = 12
    frame_width = 8
    frame_height = 8
    image = Image.new("P", (frame_count * frame_width, frame_height), 0)
    image.putpalette(palette)
    pixels = image.load()

    # A restrained bounce keeps the retail 12-frame timing while replacing the
    # old cursor with a cleaner Pokemon-style down chevron.
    y_offsets = [0, 0, 1, 1, 2, 2, 1, 1, 0, 0, 1, 0]
    chevron = (
        (1, 1, 4), (6, 1, 4),
        (1, 2, 2), (2, 2, 4), (5, 2, 4), (6, 2, 2),
        (2, 3, 1), (3, 3, 4), (4, 3, 4), (5, 3, 1),
        (3, 4, 2), (4, 4, 2),
        (3, 5, 4), (4, 5, 4),
    )

    for frame, y_offset in enumerate(y_offsets):
        x_origin = frame * frame_width

        for x, y, palette_index in chevron:
            shifted_y = y + y_offset
            if shifted_y < frame_height:
                pixels[x_origin + x, shifted_y] = palette_index

    image.save(WINDOW_DIR / "scroll_cursor.png")


def make_wait_dial(palette: list[int]) -> None:
    """Build the 8-frame 16x16 wait spinner using the shared window palette."""
    frame_count = 8
    frame_width = 16
    frame_height = 16
    image = Image.new("P", (frame_width, frame_count * frame_height), 0)
    image.putpalette(palette)
    pixels = image.load()

    points = (
        (7, 1),
        (11, 3),
        (13, 7),
        (11, 11),
        (7, 13),
        (3, 11),
        (1, 7),
        (3, 3),
    )

    for frame in range(frame_count):
        y_origin = frame * frame_height

        for point_index, (x, y) in enumerate(points):
            if point_index == frame:
                palette_index = 1
            elif point_index == (frame - 1) % frame_count:
                palette_index = 2
            else:
                palette_index = 3

            for dy in range(2):
                for dx in range(2):
                    pixels[x + dx, y_origin + y + dy] = palette_index

    image.save(WINDOW_DIR / "wait_dial.png")

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

    make_scroll_cursor(palette)
    make_wait_dial(palette)


if __name__ == "__main__":
    main()
