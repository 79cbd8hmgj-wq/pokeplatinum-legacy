#!/usr/bin/env python3

from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PARTY_DIR = ROOT / "res" / "graphics" / "party_menu"
PALETTE_PATH = PARTY_DIR / "shared.pal"

# Palette banks 0 and 1 drive the party-menu cursor/buttons/shared chrome.
# Keep all later banks untouched because they contain member/status/subscreen colors.
BANK_OVERRIDES = {
    0: [
        (98, 123, 123),   # transparent/key entry preserved
        (28, 45, 66),     # deep navy outline
        (248, 252, 255),   # cool white
        (41, 89, 184),     # royal blue shadow
        (47, 130, 230),    # clear blue
        (130, 199, 246),   # sky highlight
        (246, 172, 57),    # gold state accent
        (207, 220, 230),   # light slate
        (238, 103, 103),   # soft coral
        (184, 95, 105),    # coral shadow
        (121, 140, 158),   # slate
        (255, 190, 190),   # pale coral
        (188, 205, 218),   # cool panel
        (213, 225, 234),   # pale panel
        (255, 255, 255),   # white
        (246, 172, 57),    # gold focus
    ],
    1: [
        (98, 123, 123),   # transparent/key entry preserved
        (28, 45, 66),
        (248, 252, 255),
        (41, 89, 184),
        (47, 130, 230),
        (130, 199, 246),
        (246, 172, 57),
        (207, 220, 230),
        (238, 103, 103),
        (184, 95, 105),
        (121, 140, 158),
        (255, 190, 190),
        (188, 205, 218),
        (213, 225, 234),
        (255, 255, 255),
        (76, 174, 171),   # teal alternate-state focus
    ],
}


def load_palette() -> tuple[list[str], list[tuple[int, int, int]]]:
    lines = PALETTE_PATH.read_text().splitlines()
    if lines[:3] != ["JASC-PAL", "0100", "256"]:
        raise ValueError("Unexpected party-menu JASC palette header")
    colors = [tuple(map(int, line.split())) for line in lines[3:]]
    if len(colors) != 256:
        raise ValueError(f"Expected 256 colors, found {len(colors)}")
    return lines[:3], colors



def png_palette(filename: str) -> list[int]:
    source = Image.open(PARTY_DIR / filename)
    palette = source.getpalette()
    if palette is None:
        raise ValueError(f"{filename} is not an indexed PNG")
    return list(palette)


def draw_chamfered_outline(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    outer: int,
    inner: int,
    chamfer: int,
) -> None:
    left, top, right, bottom = box
    outer_points = [
        (left + chamfer, top),
        (right - chamfer, top),
        (right, top + chamfer),
        (right, bottom - chamfer),
        (right - chamfer, bottom),
        (left + chamfer, bottom),
        (left, bottom - chamfer),
        (left, top + chamfer),
    ]
    draw.line(outer_points + [outer_points[0]], fill=outer, width=2)

    inset = 3
    left += inset
    top += inset
    right -= inset
    bottom -= inset
    inner_chamfer = max(2, chamfer - 2)
    inner_points = [
        (left + inner_chamfer, top),
        (right - inner_chamfer, top),
        (right, top + inner_chamfer),
        (right, bottom - inner_chamfer),
        (right - inner_chamfer, bottom),
        (left + inner_chamfer, bottom),
        (left, bottom - inner_chamfer),
        (left, top + inner_chamfer),
    ]
    draw.line(inner_points + [inner_points[0]], fill=inner, width=1)


def draw_round_left_outline(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    outer: int,
    inner: int,
) -> None:
    left, top, right, bottom = box
    radius = 11

    # Pixel-art rounded leading edge with a square trailing edge.
    outer_points = [
        (left + radius, top),
        (right, top),
        (right, bottom),
        (left + radius, bottom),
        (left + 6, bottom - 2),
        (left + 2, bottom - 6),
        (left, bottom - radius),
        (left, top + radius),
        (left + 2, top + 6),
        (left + 6, top + 2),
    ]
    draw.line(outer_points + [outer_points[0]], fill=outer, width=2)

    inset = 3
    inner_points = [
        (left + radius, top + inset),
        (right - inset, top + inset),
        (right - inset, bottom - inset),
        (left + radius, bottom - inset),
        (left + 7, bottom - 5),
        (left + 4, bottom - 8),
        (left + 3, bottom - radius),
        (left + 3, top + radius),
        (left + 4, top + 8),
        (left + 7, top + 5),
    ]
    draw.line(inner_points + [inner_points[0]], fill=inner, width=1)


def draw_focus_brackets(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    color: int,
    left_run: int,
    left_rise: int,
) -> None:
    """Thicken the four corners of a focused cursor so selection is not color-only.

    Brackets sit on the existing frame inset (rows/columns 2-4 from the edge)
    and never leave the 128x48 cell, so OAM geometry is unchanged.
    """
    left, top, right, bottom = box
    run = 10
    rise = 8
    # (x0, x1, y0, y1) rectangles: horizontal then vertical bar per corner.
    rects = (
        (left + left_run, left + left_run + run, top + 2, top + 4),
        (left + 2, left + 4, top + left_rise, top + left_rise + rise),
        (right - run - 3, right - 3, top + 2, top + 4),
        (right - 4, right - 2, top + 5, top + 5 + rise),
        (left + left_run, left + left_run + run, bottom - 4, bottom - 2),
        (left + 2, left + 4, bottom - left_rise - rise, bottom - left_rise),
        (right - run - 3, right - 3, bottom - 4, bottom - 2),
        (right - 4, right - 2, bottom - 5 - rise, bottom - 5),
    )
    for x0, x1, y0, y1 in rects:
        draw.rectangle((x0, y0, x1, y1), fill=color)


def make_cursor() -> None:
    """Rebuild the four 128x48 party cursor states without changing cell/OAM geometry."""
    image = Image.new("P", (128, 195), 0)
    image.putpalette(png_palette("cursor.png"))
    draw = ImageDraw.Draw(image)

    starts = (0, 49, 98, 147)
    state_specs = (
        ("chamfer", 15, 1),
        ("round", 15, 1),
        ("chamfer", 2, 7),
        ("round", 2, 7),
    )

    for y, (shape, outer, inner) in zip(starts, state_specs):
        box = (1, y + 2, 126, y + 45)
        if shape == "chamfer":
            draw_chamfered_outline(draw, box, outer, inner, chamfer=6)
            run, rise = 8, 8
        else:
            draw_round_left_outline(draw, box, outer, inner)
            run, rise = 14, 14
        if outer == 15:
            # G7.4A: focused member card gets heavy corner brackets (shape cue).
            draw_focus_brackets(draw, box, 15, run, rise)

    image.save(PARTY_DIR / "cursor.png")


def draw_button(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    outline: int,
    fill: int,
    highlight: int,
) -> None:
    left, top, right, bottom = box
    points = [
        (left + 5, top),
        (right - 5, top),
        (right, top + 5),
        (right, bottom - 5),
        (right - 5, bottom),
        (left + 5, bottom),
        (left, bottom - 5),
        (left, top + 5),
    ]
    draw.polygon(points, fill=fill, outline=outline)

    # G7.4A: inset second ring on focused buttons (white) so focus is a shape
    # change as well as a color change; normal buttons get a deep base edge.
    if outline == 15:
        draw.line(
            [(left + 3, top + 2), (left + 3, bottom - 4), (left + 5, bottom - 2),
             (right - 5, bottom - 2), (right - 3, bottom - 4), (right - 3, top + 4)],
            fill=2, width=1,
        )
    else:
        draw.line([(left + 5, bottom - 1), (right - 5, bottom - 1)], fill=3, width=1)

    # One-pixel top/left highlight gives depth without returning to the heavy
    # retail bevel.
    highlight_points = [
        (left + 6, top + 2),
        (right - 6, top + 2),
        (right - 2, top + 6),
    ]
    draw.line(highlight_points, fill=highlight, width=1)


def make_buttons() -> None:
    """Rebuild large and compact party buttons while preserving the 4-cell contract."""
    image = Image.new("P", (56, 99), 0)
    image.putpalette(png_palette("button.png"))
    draw = ImageDraw.Draw(image)

    # Source packing: two 56x32 cells followed by two 56x16 cells, separated
    # by the same one-pixel gutters used by the retail editable PNG.
    frames = (
        ((0, 0, 55, 31), 1, 4, 5),    # large normal
        ((0, 33, 55, 64), 15, 5, 2),  # large focused
        ((0, 66, 55, 81), 1, 4, 5),   # compact normal
        ((0, 83, 55, 98), 15, 5, 2),  # compact focused
    )
    for box, outline, fill, highlight in frames:
        draw_button(draw, box, outline, fill, highlight)

    image.save(PARTY_DIR / "button.png")

def main() -> None:
    header, colors = load_palette()

    for bank, entries in BANK_OVERRIDES.items():
        if len(entries) != 16:
            raise ValueError(f"Bank {bank} must contain exactly 16 colors")
        start = bank * 16
        colors[start:start + 16] = entries

    out = header + [f"{r} {g} {b}" for r, g, b in colors]
    PALETTE_PATH.write_text("\n".join(out) + "\n")
    make_cursor()
    make_buttons()


if __name__ == "__main__":
    main()
