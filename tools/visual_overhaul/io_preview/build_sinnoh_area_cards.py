#!/usr/bin/env python3
"""Generate the IO-PREVIEW Sinnoh expansion cards (Route 217, Mt. Coronet, Lake Verity,
Lake Acuity, Distortion World).

Output : res/graphics/map_popups/card_<slug>_{day,dusk,night}.png (Distortion World: one file)
         104x40 px (13x5 tiles), 4bpp-compatible indexed, converted to NCGR by meson.

Same contract as build_eterna_forest_card.py (whose frame helpers are reused so every card has
the popup's 2 px white border / 2 px black shadow / rounded corners): a card is drawn into the
blank right-hand tiles of the 32x5-tile popup window, so it must share the BG palette of the
popup STYLE it is gated on. Each scene therefore reads the first 16 palette entries of its own
style PNG (route / cave / lake) verbatim and never redefines a colour. Time-of-day variants
differ only in which indices they use.

Pixel sources: none. Procedural, hand-parameterised Platinum-native art. Deterministic.
"""
import random
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_eterna_forest_card as base  # noqa: E402  (frame geometry + drawing helpers)

OUT = base.OUT
W, H = base.W, base.H
WHITE, BLACK = base.WHITE, base.BLACK
X0, Y0 = base.BOX[0] + base.BORDER, base.BOX[1] + base.BORDER
X1, Y1 = base.BOX[2] - base.BORDER, base.BOX[3] - base.BORDER
VARIANTS = ("day", "dusk", "night")


class Ctx:
    """Drawing surface restricted to the card's inner (rounded) area."""

    def __init__(self, style, seed):
        self.style = style
        self.img = Image.new("P", (W, H), base.TRANSPARENT)
        with Image.open(base.OUT / f"{style}_popup.png") as im:
            self.img.putpalette(im.getpalette()[: 16 * 3] + [0] * (256 * 3 - 16 * 3))
        self.px = self.img.load()
        self.inner = base.build_frame(self.px)
        self.rng = random.Random(seed)

    def set(self, x, y, c):
        if (x, y) in self.inner:
            self.px[x, y] = c

    def rect(self, x0, y0, x1, y1, c):
        base.fill_rect(self.px, self.inner, x0, y0, x1, y1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        base.fill_ellipse(self.px, self.inner, cx, cy, rx, ry, c)

    def dither(self, x0, y0, x1, y1, a, b):
        base.dither(self.px, self.inner, x0, y0, x1, y1, a, b)

    def bands(self, y0, y1, pairs):
        """Split [y0, y1] into len(pairs) dithered bands, top to bottom."""
        n = len(pairs)
        for i, (a, b) in enumerate(pairs):
            ya = y0 + (y1 - y0 + 1) * i // n
            yb = y0 + (y1 - y0 + 1) * (i + 1) // n - 1
            self.dither(X0, ya, X1, yb, a, b)

    def specks(self, count, colors, y_lo=None, y_hi=None, x_lo=None, x_hi=None):
        for _ in range(count):
            x = self.rng.randrange(x_lo if x_lo is not None else X0 + 1, x_hi if x_hi is not None else X1)
            y = self.rng.randrange(y_lo if y_lo is not None else Y0 + 1, y_hi if y_hi is not None else Y1)
            self.set(x, y, self.rng.choice(colors))

    def tri(self, cx, top, base_y, half, c):
        """Filled isosceles triangle."""
        height = max(base_y - top, 1)
        for y in range(top, base_y + 1):
            h = half * (y - top) // height
            for x in range(cx - h, cx + h + 1):
                self.set(x, y, c)

    def ridge(self, peaks, floor_y, rock, shade, snow=None, snow_line=None, dither_to=None):
        """Mountain silhouette from (cx, peak_y, slope) peaks; the right flank is shaded,
        pixels above snow_line (a y) get the snow colour."""
        for x in range(X0, X1 + 1):
            best = None
            for cx, py, slope in peaks:
                y = py + int(abs(x - cx) * slope)
                if best is None or y < best[0]:
                    best = (y, cx)
            top, cx = best
            for y in range(top, floor_y + 1):
                col = rock if x <= cx else shade
                if snow is not None and y < snow_line + ((x * 7) % 3) - 1:
                    col = snow if x <= cx or (x + y) % 2 == 0 else rock
                self.set(x, y, col)


# --- shared scene pieces -------------------------------------------------------------------

def pine(c, cx, base_y, tiers, half, body, cap, trunk):
    """Snow-dusted conifer: stacked triangles, snow on each tier's upper rows."""
    c.rect(cx, base_y - 1, cx, base_y + 1, trunk)
    ty = base_y - 2
    for t in range(tiers):
        th = 6
        top = ty - th
        c.tri(cx, top, ty, max(half - t, 2), body)
        # snow on the tier's two upper rows
        for y in (top, top + 1):
            for x in range(cx - (y - top) - 1, cx + (y - top) + 2):
                if (x + y) % 3:
                    c.set(x, y, cap)
        ty -= 4


def stars(c, count, colors, y_hi):
    c.specks(count, colors, y_lo=Y0 + 1, y_hi=y_hi)


# --- Route 217: blizzard route ----------------------------------------------------------------

def route_217(v):
    # route palette: 9-12 greens, 13-15 sky blues, 4/5 lavender, 6/7 sand, 1 white
    c = Ctx("route", "route217_" + v)
    horizon = Y0 + 16
    if v == "day":
        c.bands(Y0, horizon, [(14, 13), (15, 14)])
        far, ground, shade, body, cap, trunk = 5, (1, 15), 4, 9, 1, 8
    elif v == "dusk":
        c.bands(Y0, horizon, [(5, 4), (4, 6), (6, 7)])
        far, ground, shade, body, cap, trunk = 8, (4, 1), 5, 9, 4, 3
    else:
        c.bands(Y0, horizon, [(3, 3), (3, 5)])
        stars(c, 10, [1, 1, 4], horizon - 4)
        far, ground, shade, body, cap, trunk = 5, (4, 5), 8, 9, 5, 3
    # far snow hills
    c.ridge([(X0 + 14, horizon - 6, 0.7), (X0 + 64, horizon - 8, 0.55)], horizon + 3, far, shade)
    c.ridge([(X0 + 30, horizon - 3, 0.9), (X0 + 84, horizon - 4, 0.8)], horizon + 3, ground[0], ground[1])
    # snowfield
    c.dither(X0, horizon + 3, X1, Y1, *ground)
    c.rect(X0, horizon + 9, X1, Y1, ground[0])
    for tx, by, tiers, half in [(X0 + 8, horizon + 8, 3, 6), (X0 + 24, horizon + 5, 2, 5), (X0 + 60, horizon + 6, 2, 5),
                                (X0 + 76, horizon + 9, 3, 7), (X0 + 90, horizon + 5, 2, 5)]:
        pine(c, tx, by, tiers, half, body, cap, trunk)
    # drifting snow (blizzard): white flecks over the scene, a few darker on the ground
    flake = [1, 1, 1, 4] if v != "day" else [1, 1, 1, 15]
    c.specks(26, flake, y_lo=Y0 + 1, y_hi=horizon + 4)
    return c.img


# --- Mt. Coronet: snow-capped peak ---------------------------------------------------------------

def mt_coronet(v):
    # cave palette: 6 dark gray, 8 stone, 9/10 brown rock, 11/12 tan, 13-15 sky, 4/5 lavender
    c = Ctx("cave", "coronet_" + v)
    floor = Y1
    if v == "day":
        c.bands(Y0, Y1, [(15, 14), (14, 13)])
        far, rock, shade, snow = 5, 8, 6, 1
        far_top = 4
    elif v == "dusk":
        c.bands(Y0, Y1, [(12, 11), (11, 10)])
        far, rock, shade, snow = 5, 6, 3, 12
        far_top = 5
    else:
        c.bands(Y0, Y1, [(3, 3)])
        stars(c, 14, [1, 1, 4], Y0 + 14)
        c.ellipse(X0 + 74, Y0 + 7, 4, 4, 1)
        far, rock, shade, snow = 6, 6, 3, 4
        far_top = 6
    c.ridge([(X0 + 10, Y0 + 11, 1.0), (X0 + 80, Y0 + 9, 1.1)], floor, far, far)  # distant range
    c.ridge([(X0 + 44, Y0 + 3, 1.15)], floor, rock, shade, snow=snow, snow_line=Y0 + 12)  # Coronet's peak
    c.ridge([(X0 + 8, Y0 + 19, 0.9), (X0 + 88, Y0 + 17, 0.9)], floor, rock, shade)  # foreground flanks
    c.dither(X0, Y1 - 2, X1, Y1, shade, rock)
    if v != "day":
        c.specks(5, [far_top], y_lo=Y0 + 8, y_hi=Y0 + 16)
    return c.img


# --- Lakes -------------------------------------------------------------------------------------

def _water(c, y_top, light, mid, glint, seed):
    c.rect(X0, y_top, X1, Y1, mid)
    rng = random.Random(seed)
    for y in range(y_top + 1, Y1, 3):
        for _ in range(5):
            x = rng.randrange(X0 + 1, X1 - 8)
            c.rect(x, y, x + rng.randrange(3, 9), y, light)
    for y in range(y_top, Y1 + 1, 6):
        c.rect(X0, y, X1, y, mid)
    c.specks(6, [glint], y_lo=y_top + 2, y_hi=Y1 - 1)


def lake_verity(v):
    # lake palette: 9-12 greens, 13-15 water blues, 4/5/6 lavender-gray, 7 olive sand, 1 white
    c = Ctx("lake", "verity_" + v)
    horizon = Y0 + 13
    if v == "day":
        c.bands(Y0, horizon, [(15, 14), (14, 13)])
        hill, tree, water = 11, 9, (13, 14, 15)
    elif v == "dusk":
        c.bands(Y0, horizon, [(5, 4), (4, 7), (7, 12)])
        hill, tree, water = 9, 6, (5, 4, 7)
    else:
        c.bands(Y0, horizon, [(3, 3)])
        stars(c, 12, [1, 1, 4], horizon - 3)
        c.ellipse(X0 + 20, Y0 + 5, 3, 3, 1)
        hill, tree, water = 6, 3, (6, 5, 4)
    c.ridge([(X0 + 22, horizon - 6, 0.55), (X0 + 70, horizon - 7, 0.5)], horizon + 2, hill, tree)
    for tx in range(X0 + 2, X1, 7):  # shoreline trees
        c.ellipse(tx, horizon, 4, 3, tree)
    _water(c, horizon + 2, water[2], water[0], water[1], "verity_" + v)
    # Lake Verity's islet: a small grove mid-lake with its reflection
    c.ellipse(X0 + 56, horizon + 5, 10, 2, hill)
    for tx in (X0 + 51, X0 + 56, X0 + 61):
        c.ellipse(tx, horizon + 2, 3, 3, tree)
    c.dither(X0 + 46, horizon + 8, X0 + 66, horizon + 10, water[2], water[0])
    if v == "night":
        for y in range(horizon + 6, Y1, 2):  # moon path on the water
            c.rect(X0 + 17 + (y % 3), y, X0 + 22 - (y % 3), y, 4)
    return c.img


def lake_acuity(v):
    c = Ctx("lake", "acuity_" + v)
    horizon = Y0 + 12
    if v == "day":
        c.bands(Y0, horizon, [(14, 13), (15, 14)])
        far, snow, shade, water, tree = 5, 1, 4, (14, 15, 1), 9
    elif v == "dusk":
        c.bands(Y0, horizon, [(5, 4), (4, 7)])
        far, snow, shade, water, tree = 6, 4, 5, (5, 4, 15), 9
    else:
        c.bands(Y0, horizon, [(3, 3)])
        stars(c, 14, [1, 1, 4], horizon - 3)
        far, snow, shade, water, tree = 6, 4, 5, (6, 5, 4), 6
    # snow-capped hills framing the lake
    c.ridge([(X0 + 16, horizon - 8, 1.1), (X0 + 76, horizon - 9, 1.0)], horizon + 2, far, shade, snow=snow, snow_line=horizon - 2)
    _water(c, horizon + 2, water[1], water[0], water[2], "acuity_" + v)
    # ice floes
    for fx, fy, rx in [(X0 + 14, horizon + 8, 7), (X0 + 52, horizon + 11, 9), (X0 + 80, horizon + 7, 6), (X0 + 34, horizon + 15, 6)]:
        c.ellipse(fx, fy, rx, 2, snow)
        c.rect(fx - rx + 2, fy + 1, fx + rx - 2, fy + 1, shade)
    # snowy shore + pines along the bottom-left and right edges
    c.ellipse(X0 + 4, Y1 + 3, 20, 5, snow)
    c.ellipse(X1 - 4, Y1 + 3, 18, 4, snow)
    pine(c, X0 + 10, Y1 - 6, 2, 5, tree, snow, shade)
    pine(c, X1 - 12, Y1 - 5, 2, 5, tree, snow, shade)
    c.specks(14, [snow, snow, shade], y_lo=Y0 + 1, y_hi=horizon + 8)
    return c.img


# --- Distortion World: timeless ----------------------------------------------------------------

def distortion_world(_v):
    # cave palette: black void, 4/5 lavender, 6 dark gray, 9/11/12 brown-tan rock, 1 white
    c = Ctx("cave", "distortion_world")
    c.rect(X0, Y0, X1, Y1, BLACK)
    cx, cy = X0 + 62, Y0 + 13
    for i, (rx, ry, col) in enumerate([(30, 12, 6), (24, 9, 5), (18, 7, 6), (12, 5, 4), (7, 3, 6), (3, 2, 1)]):
        c.ellipse(cx, cy, rx, ry, col)
    c.dither(cx - 14, cy - 3, cx + 14, cy + 3, 3, 6)
    # a floating slab, an inverted slab and tilted blocks (the world's broken geometry)
    def slab(x, y, w, h, top, side, edge, skew=0):
        for i in range(h):
            xs = x + (skew * i) // max(h - 1, 1)
            c.rect(xs, y + i, xs + w, y + i, side if i else top)
        c.rect(x, y, x + w, y, edge)
    slab(X0 + 4, Y0 + 15, 26, 5, 12, 9, 1, skew=3)
    slab(X0 + 44, Y0 + 3, 18, 4, 11, 6, 1, skew=-3)    # hangs upside-down
    slab(X0 + 70, Y0 + 20, 20, 4, 12, 9, 1, skew=4)
    slab(X0 + 22, Y0 + 24, 12, 3, 4, 5, 1)
    for bx, by in [(X0 + 38, Y0 + 12), (X0 + 86, Y0 + 9), (X0 + 12, Y0 + 5), (X0 + 56, Y0 + 24)]:
        c.rect(bx, by, bx + 2, by + 2, 11)
        c.rect(bx + 1, by + 1, bx + 2, by + 2, 9)
    c.specks(18, [5, 6, 11, 1], y_lo=Y0 + 1, y_hi=Y1)
    return c.img


# slug -> (builder, variants written). Order is NOT the NARC order; map_popup.order is.
SCENES = {
    "route_217": (route_217, VARIANTS),
    "mt_coronet": (mt_coronet, VARIANTS),
    "lake_verity": (lake_verity, VARIANTS),
    "lake_acuity": (lake_acuity, VARIANTS),
    "distortion_world": (distortion_world, (None,)),
}


def card_name(slug, variant):
    return f"card_{slug}.png" if variant is None else f"card_{slug}_{variant}.png"


def main():
    for slug, (fn, variants) in SCENES.items():
        for v in variants:
            fn(v).save(OUT / card_name(slug, v), optimize=False)
            print("wrote", card_name(slug, v))


if __name__ == "__main__":
    main()
