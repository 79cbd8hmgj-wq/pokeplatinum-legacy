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



# The scroll cursor and wait dial are NOT drawn with the standard window
# palette at runtime: they are blitted onto the right-hand bar of the *message
# frame* tiles (frame tiles +10/+11) and rendered with that frame's palette.
# Only entries 1-4 are stable across the frame family (1 white, 2 per-frame
# dark, 3 light grey, 4 mid grey), so the art uses a white fill with a dark
# outline (and a grey dial ring) that reads on any frame's dark bar colour.
# The bar is 11 px wide (cols 0-10 of the 16x16 cell); cols 11+ are the frame's
# own outline/halo/transparent edge and must not be painted over.
DIAL_HEAD = 1
DIAL_TRAIL = 3
DIAL_REST = 4

# 9x6 down-pointing triangle; '.' leaves the frame bar visible.
CURSOR_ART = (
    "222222222",
    "211111112",
    ".2111112.",
    "..21112..",
    "...212...",
    "....2....",
)
CURSOR_TOP = (4, 5, 6)  # per-frame bounce; the printer cycles frames 0,1,2,1
# DrawMessageBoxScrollCursor blits source cell cols 4.. to bar cols 1.., so the
# art starts at source col 4 (bar col 1) and ends at source col 12 (bar col 9).
CURSOR_SRC_X = 4


def make_scroll_cursor(palette: list[int]) -> None:
    """Build the 3-frame scroll cursor tile sheet without changing its resource contract.

    The NCGR is 12 tiles = 3 frames x (2x2 tiles); frame ``f`` owns tiles
    ``4f..4f+3`` in TL, TR, BL, BR order.  The sheet is therefore authored in
    16x16 cell coordinates and scattered into the 8x8 tile strip.
    """
    frame_count = 3
    image = Image.new("P", (frame_count * 4 * 8, 8), 0)
    image.putpalette(palette)
    pixels = image.load()

    for frame, top in enumerate(CURSOR_TOP):
        for row, line in enumerate(CURSOR_ART):
            for col, char in enumerate(line):
                if char == ".":
                    continue

                cell_x = CURSOR_SRC_X + col
                cell_y = top + row
                tile = frame * 4 + (cell_y // 8) * 2 + (cell_x // 8)
                pixels[tile * 8 + cell_x % 8, cell_y % 8] = int(char)

    image.save(WINDOW_DIR / "scroll_cursor.png")


# 2x2 dot top-left corners on a radius-4 ring, clockwise from north, all inside
# cell cols 0-9 so nothing reaches the frame outline at col 11.
DIAL_POINTS = (
    (4, 3),
    (7, 4),
    (8, 7),
    (7, 10),
    (4, 11),
    (1, 10),
    (0, 7),
    (1, 4),
)


def make_wait_dial(palette: list[int]) -> None:
    """Build the 8-frame 16x16 wait spinner (white head, light trail, grey ring)."""
    frame_count = 8
    frame_width = 16
    frame_height = 16
    image = Image.new("P", (frame_width, frame_count * frame_height), 0)
    image.putpalette(palette)
    pixels = image.load()

    for frame in range(frame_count):
        y_origin = frame * frame_height

        for point_index, (x, y) in enumerate(DIAL_POINTS):
            if point_index == frame:
                palette_index = DIAL_HEAD
            elif point_index == (frame - 1) % frame_count:
                palette_index = DIAL_TRAIL
            else:
                palette_index = DIAL_REST

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
