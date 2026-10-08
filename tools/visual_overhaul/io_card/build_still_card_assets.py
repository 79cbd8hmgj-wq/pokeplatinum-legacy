#!/usr/bin/env python3
"""Generate the IO-CARD still-card art set (Solaceon News Press pilot).

Inputs : res/items/icons/{dusk,heal,quick,dive}_ball.png (Platinum-native 32x32 item icons)
Outputs: res/graphics/still_card/*.png  (4bpp indexed; converted to NCGR/NCLR by meson)

Deterministic: re-running overwrites the outputs with identical bytes.
No donor pixels are used; the Ranger-2 influence is structural only
(masthead / rule / illustration well / column layout / state variants).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
ICONS = ROOT / "res/items/icons"
OUT = ROOT / "res/graphics/still_card"

ARTICLES = [("dusk", "dusk_ball"), ("heal", "heal_ball"), ("quick", "quick_ball"), ("dive", "dive_ball")]

# Shared 16-colour page palette (index 0 is the BG backdrop colour).
PAGE_PAL = [
    (0xEF, 0xE6, 0xC8),  # 0 paper
    (0x10, 0x18, 0x30),  # 1 ink
    (0x1F, 0x3C, 0x7A),  # 2 navy
    (0x2A, 0x8C, 0x96),  # 3 teal
    (0x8A, 0xCF, 0xCF),  # 4 light teal
    (0xD6, 0xC9, 0xA0),  # 5 shaded paper
    (0x56, 0x68, 0x90),  # 6 slate
    (0xFF, 0xFF, 0xFF),  # 7 white
    (0xF8, 0xF2, 0xDC),  # 8 bright paper
    (0xB8, 0xAA, 0x7C),  # 9 column grey
] + [(0, 0, 0)] * 6

# Panel palette (bottom screen). Index 8 is the tab fill; the "active" variant swaps it.
PANEL_PAL = list(PAGE_PAL)
PANEL_PAL[0] = (0x14, 0x28, 0x56)  # navy backdrop
PANEL_PAL[8] = (0xEF, 0xE6, 0xC8)  # inactive tab fill
PANEL_ACTIVE_PAL = list(PANEL_PAL)
PANEL_ACTIVE_PAL[8] = (0xF2, 0xC9, 0x4C)  # active tab fill


def save(img, name):
    img.save(OUT / name, optimize=False)


def new_img(w, h, pal):
    img = Image.new("P", (w, h), 0)
    flat = []
    for c in pal:
        flat.extend(c)
    img.putpalette(flat)
    return img


def build_page():
    img = new_img(256, 192, PAGE_PAL)
    d = ImageDraw.Draw(img)
    # outer frame
    d.rectangle([0, 0, 255, 191], outline=2, width=2)
    d.rectangle([2, 2, 253, 189], outline=3, width=1)
    # masthead ornaments (diamonds + rules); masthead text is drawn at runtime
    for cx in (14, 241):
        d.polygon([(cx, 8), (cx + 6, 15), (cx, 22), (cx - 6, 15)], fill=3, outline=2)
        d.polygon([(cx, 12), (cx + 2, 15), (cx, 18), (cx - 2, 15)], fill=4)
    d.line([(26, 15), (82, 15)], fill=6)
    d.line([(174, 15), (230, 15)], fill=6)
    # double rule under masthead
    d.rectangle([6, 30, 249, 31], fill=2)
    d.line([(6, 34), (249, 34)], fill=3)
    # headline strip
    d.rectangle([6, 38, 249, 55], fill=5)
    d.line([(6, 56), (249, 56)], fill=1)
    # faux newspaper columns either side of the illustration well
    for x0, x1 in ((10, 80), (176, 246)):
        for i, y in enumerate(range(64, 130, 6)):
            end = x1 if i % 4 != 3 else x1 - 22
            d.line([(x0, y), (end, y)], fill=9)
    # illustration well 88..167 x 60..131, halo pattern
    d.rectangle([90, 62, 169, 133], fill=6)  # drop shadow
    d.rectangle([88, 60, 167, 131], fill=8, outline=2, width=2)
    cx, cy = 128, 96
    for r, col in ((34, 4), (26, 8), (18, 4), (10, 8)):
        d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=col)
    # body rule
    d.line([(6, 133), (249, 133)], fill=2)
    d.line([(6, 134), (249, 134)], fill=3)
    save(img, "page.png")


def build_panel(pal, name, size=(256, 192), buttons=True):
    img = new_img(size[0], size[1], pal)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 255, 191], outline=3, width=2)
    d.rectangle([2, 2, 253, 189], outline=6, width=1)
    if buttons:
        for i in range(5):
            top = 16 + i * 32
            d.rectangle([26, top + 2, 233, top + 25], fill=1)  # shadow
            d.rectangle([24, top, 231, top + 23], fill=8, outline=7, width=1)
            d.rectangle([25, top + 1, 230, top + 22], outline=2, width=1)
    save(img, name)


def build_art(key, icon):
    src = Image.open(ICONS / f"{icon}.png")
    assert src.mode == "P" and src.size == (32, 32), icon
    pal = src.getpalette()[:48]
    pal += [0] * (48 - len(pal))
    # 64x72: first tile row is blank so tile 0 stays transparent for cleared cells.
    img = Image.new("P", (64, 72), 0)
    img.putpalette(pal)
    big = src.resize((64, 64), Image.NEAREST)
    img.paste(big, (0, 8))
    save(img, f"art_{key}.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    build_page()
    build_panel(PANEL_PAL, "panel.png")
    build_panel(PANEL_ACTIVE_PAL, "panel_active.png")
    for key, icon in ARTICLES:
        build_art(key, icon)
    print("wrote", len(list(OUT.glob("*.png"))), "pngs to", OUT)


if __name__ == "__main__":
    sys.exit(main())
