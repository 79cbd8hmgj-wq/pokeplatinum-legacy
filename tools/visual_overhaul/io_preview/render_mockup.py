#!/usr/bin/env python3
"""Static composite of popup + IO-PREVIEW cards (NOT an emulator capture).

Emulates MapNamePopUp_DrawWindowFrame + MapNamePopUp_DrawAreaCard at the data level:
converts the PNGs with the repo's own nitrogfx (same flags as meson), decodes the
resulting NCGR tile stream, and replays the tile blits into a 256x40 window bitmap using
the palette of the popup style the card is gated on. This proves the PNG->NCGR tile order
matches the C blit loop; it does not prove runtime behaviour. The map name text is not drawn.

usage: render_mockup.py <nitrogfx-binary> <out.png>
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
POP = ROOT / "res/graphics/map_popups"

POPUP_W_TILES, POPUP_H_TILES = 17, 5
CARD_W_TILES, CARD_H_TILES = 13, 5
CARD_TILE_X = 18
WINDOW_W, WINDOW_H = 256, 40


def convert(nitrogfx, png, out, extra):
    subprocess.run([nitrogfx, str(png), str(out), "-version101", "-sopc", "-convertTo4Bpp", *extra], check=True)


def decode_tiles(ncgr_path):
    data = Path(ncgr_path).read_bytes()
    pos = data.index(b"RAHC")
    # RAHC: magic(4) size(4) h(2) w(2) depth(4) pad(4) mapping(4) flags(4) dataSize(4) dataOffset(4) | tile data
    n = int.from_bytes(data[pos + 0x18 : pos + 0x1C], "little")
    tiles = []
    base = pos + 0x20
    for t in range(n // 32):
        raw = data[base + t * 32 : base + t * 32 + 32]
        px = []
        for row in range(8):
            line = []
            for b in raw[row * 4 : row * 4 + 4]:
                line += [b & 0xF, b >> 4]
            px.append(line)
        tiles.append(px)
    return tiles


def blit(window, tiles, count, w_tiles, tile_x0):
    for i in range(count):
        tx, ty = tile_x0 + i % w_tiles, i // w_tiles
        for y in range(8):
            for x in range(8):
                c = tiles[i][y][x]
                if c != 0:  # Window_BlitBitmapRect skips colour index 0
                    window[ty * 8 + y][tx * 8 + x] = c


def render(nitrogfx, rows, out_png):
    """rows: list of (popup_style_name, card_png_stem or None)."""
    sheet_rows = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        popups = {}
        for style, card in rows:
            if style not in popups:
                convert(nitrogfx, POP / f"{style}_popup.png", td / f"{style}.NCGR", ["-width", "32", "-num_tiles", "96"])
                popups[style] = decode_tiles(td / f"{style}.NCGR")
            window = [[0] * WINDOW_W for _ in range(WINDOW_H)]
            blit(window, popups[style], POPUP_W_TILES * POPUP_H_TILES, POPUP_W_TILES, 0)
            if card:
                n = CARD_W_TILES * CARD_H_TILES
                convert(nitrogfx, POP / f"{card}.png", td / f"{card}.NCGR", ["-num_tiles", str(n)])
                blit(window, decode_tiles(td / f"{card}.NCGR"), n, CARD_W_TILES, CARD_TILE_X)
            pal = Image.open(POP / f"{style}_popup.png").getpalette()[: 16 * 3]
            img = Image.new("P", (WINDOW_W, WINDOW_H))
            img.putpalette(pal + [0] * (768 - len(pal)))
            img.putdata([c for row in window for c in row])
            sheet_rows.append(img.convert("RGB"))
    scale = 2
    sheet = Image.new("RGB", (WINDOW_W * scale, (WINDOW_H + 4) * scale * len(sheet_rows)), (24, 24, 24))
    for i, im in enumerate(sheet_rows):
        sheet.paste(im.resize((WINDOW_W * scale, WINDOW_H * scale), Image.NEAREST), (0, i * (WINDOW_H + 4) * scale))
    sheet.save(out_png)


if __name__ == "__main__":
    # imported lazily so render() stays usable from the validator without a circular import
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import validate_area_cards

    nitrogfx, out = sys.argv[1], sys.argv[2]
    render(nitrogfx, validate_area_cards.mockup_rows(), out)
    print("wrote", out)
