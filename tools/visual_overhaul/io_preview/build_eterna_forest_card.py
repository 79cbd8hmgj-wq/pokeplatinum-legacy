#!/usr/bin/env python3
"""Generate the IO-PREVIEW Eterna Forest location-card art (3 time-of-day variants).

Output : res/graphics/map_popups/card_eterna_forest_{day,dusk,night}.png
         104x40 px (13x5 tiles), 4bpp-compatible indexed, converted to NCGR by meson.

The card is drawn into the right-hand tiles of the existing 32x5-tile map-name
popup window, which are otherwise blank. It therefore has to share the popup's
BG palette slot: every variant uses the 16-colour palette of forest_popup.png
verbatim (read from that file, never redefined here). Time-of-day variants differ
only in which palette indices are used, not in the palette.

Pixel sources: none. The scene is procedural, hand-parameterised Platinum-native
art; no HGSS/FireRed pixels are used (those are structural references only).
Deterministic: re-running overwrites the outputs with identical bytes.
"""
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
POPUP = ROOT / "res/graphics/map_popups/forest_popup.png"
OUT = ROOT / "res/graphics/map_popups"

W, H = 104, 40

# Palette indices of forest_popup.png (see the palette dump in IO_PREVIEW_ETERNA_FOREST.md).
TRANSPARENT = 0
WHITE = 1
BLACK = 3
LAVENDER_LIGHT, LAVENDER = 4, 5
PEACH, SAND, STONE = 6, 7, 8
GREEN = {"dark": 9, "mid": 10, "light": 11, "bright": 12}
SKY = {"blue": 13, "pale": 14, "haze": 15}

# Card box geometry inside the 104x40 canvas (mirrors the popup's 2px white border,
# 2px black drop shadow and 2px corner rounding).
BOX = (1, 3, 98, 34)  # x0, y0, x1, y1 inclusive (border outer edge)
BORDER = 2
SHADOW = 2


def popup_palette():
    with Image.open(POPUP) as im:
        flat = im.getpalette()[: 16 * 3]
    return flat


def rounded_mask(x0, y0, x1, y1):
    """Box membership with the popup's 2px diagonal corner cut."""
    cut = {0: 2, 1: 1}  # rows/cols from the edge -> pixels trimmed
    pts = set()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dy = min(y - y0, y1 - y)
            dx = min(x - x0, x1 - x)
            if dy in cut and dx < cut[dy]:
                continue
            pts.add((x, y))
    return pts


def build_frame(px):
    outer = rounded_mask(*BOX)
    for x, y in rounded_mask(BOX[0] + SHADOW, BOX[1] + SHADOW, BOX[2] + SHADOW, BOX[3] + SHADOW):
        if (x, y) not in outer:
            px[x, y] = BLACK
    for x, y in outer:
        px[x, y] = WHITE
    inner = rounded_mask(BOX[0] + BORDER, BOX[1] + BORDER, BOX[2] - BORDER, BOX[3] - BORDER)
    return inner


def fill_ellipse(px, inner, cx, cy, rx, ry, color):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0 and (x, y) in inner:
                px[x, y] = color


def fill_rect(px, inner, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) in inner:
                px[x, y] = color


def dither(px, inner, x0, y0, x1, y1, a, b):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) in inner:
                px[x, y] = a if (x + y) % 2 == 0 else b


# Per-variant scene recipe: sky band, canopy tones back->front, trunk, floor, accents.
RECIPES = {
    "day": {
        "sky": [(SKY["haze"], SKY["pale"]), (SKY["pale"], SKY["blue"])],
        "canopy": [GREEN["mid"], GREEN["light"], GREEN["bright"]],
        "shade": GREEN["dark"],
        "trunk": PEACH,
        "floor": [SAND, STONE],
        "beam": SKY["haze"],
        "orb": None,
        "specks": [],
    },
    "dusk": {
        "sky": [(SAND, PEACH), (PEACH, LAVENDER_LIGHT)],
        "canopy": [GREEN["mid"], GREEN["dark"], GREEN["mid"]],
        "shade": GREEN["dark"],
        "trunk": STONE,
        "floor": [STONE, LAVENDER],
        "beam": SAND,
        "orb": (80, 16, 7, SAND),
        "specks": [],
    },
    "night": {
        "sky": [(BLACK, BLACK), (BLACK, BLACK)],
        "canopy": [BLACK, LAVENDER, STONE],
        "shade": BLACK,
        "trunk": STONE,
        "floor": [BLACK, STONE],
        "beam": LAVENDER_LIGHT,
        "orb": (84, 12, 5, WHITE),
        "specks": [SAND, SAND, WHITE],  # fireflies / stars
    },
}


def build_card(name):
    r = RECIPES[name]
    rng = random.Random("eterna_forest_card_" + name)
    img = Image.new("P", (W, H), TRANSPARENT)
    img.putpalette(popup_palette() + [0] * (256 * 3 - 16 * 3))
    px = img.load()
    inner = build_frame(px)
    x0, y0 = BOX[0] + BORDER, BOX[1] + BORDER
    x1, y1 = BOX[2] - BORDER, BOX[3] - BORDER

    # Sky gap visible between the trunks (two dithered bands).
    third = (y1 - y0) // 3
    dither(px, inner, x0, y0, x1, y0 + third, *r["sky"][0])
    dither(px, inner, x0, y0 + third + 1, x1, y1, *r["sky"][1])

    if r["orb"]:
        cx, cy, rad, col = r["orb"]
        fill_ellipse(px, inner, cx, cy, rad, rad, col)

    # Back canopy row: wide overlapping blobs, tones alternate for depth.
    for i, cx in enumerate(range(x0 - 4, x1 + 8, 13)):
        cy = y0 + 6 + (i % 2) * 3
        fill_ellipse(px, inner, cx, cy, 11, 8, r["canopy"][i % len(r["canopy"])])
    # Light shafts: diagonal dithered beams crossing the back canopy.
    for sx in (x0 + 18, x0 + 52, x0 + 78):
        for y in range(y0 + 2, y0 + 20):
            for dx in range(3):
                x = sx + (y - y0) // 2 + dx
                if (x, y) in inner and (x + y) % 2 == 0:
                    px[x, y] = r["beam"]

    # Trunks with canopy blobs on top (front row), far to near.
    floor_y = y1 - 4
    trunks = [x0 + 8, x0 + 24, x0 + 40, x0 + 58, x0 + 73, x0 + 88]
    for i, tx in enumerate(trunks):
        top = y0 + 11 + (i % 3) * 2
        fill_rect(px, inner, tx, top, tx + 1, floor_y, r["trunk"])
        c = r["canopy"][(i + 1) % len(r["canopy"])]
        fill_ellipse(px, inner, tx + 0.5, top - 1, 8, 7, c)
        # underside shade keeps the blob from reading as a flat disc
        fill_ellipse(px, inner, tx + 0.5, top + 3, 7, 3, r["shade"])
        fill_ellipse(px, inner, tx + 0.5, top - 3, 5, 3, c)

    # Forest floor (two-tone dithered strip).
    dither(px, inner, x0, floor_y + 1, x1, y1, *r["floor"])

    # Night accents: sparse fireflies in the clearing between trunks.
    for _ in range(16 if r["specks"] else 0):
        x = rng.randrange(x0 + 2, x1 - 2)
        y = rng.randrange(y0 + 2, floor_y - 2)
        if (x, y) in inner:
            px[x, y] = rng.choice(r["specks"])
    return img


def main():
    for name in RECIPES:
        build_card(name).save(OUT / f"card_eterna_forest_{name}.png", optimize=False)
        print("wrote", f"card_eterna_forest_{name}.png")


if __name__ == "__main__":
    main()
