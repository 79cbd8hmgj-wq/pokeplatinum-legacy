#!/usr/bin/env python3
"""Deterministic generator for the Opal Pokedex reference-page graphics.

Writes (into res/graphics/pokedex/):
  opal_ref.pal             JASC palette: bank 0 text/bars, bank 1 art, bank 2 selected, bank 3 pressed
  opal_ref_main.png/.NSCR  top-LCD background (4bpp tileset + 32x24 tilemap)
  opal_ref_sub.png/.NSCR   bottom-LCD background (tabs, buttons, panels baked in; text is drawn at runtime)
  opal_entry.png/.NSCR     vertical "OPAL DATA" entry plate for the Info tab's sub screen (palette bank 13)

and previews into docs/opal/previews/ (renders of the installed assets, NOT emulator screenshots).

Palette tokens come from docs/visual_overhaul/MO1_1_OPAL_V3_VISUAL_DIRECTION.md:
pearl/porcelain surfaces, slate-violet framing, amethyst selection, restrained antique gold.
`--check` verifies that the checked-in outputs are current.
"""
import os
import re
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gameplay_sources as gs  # noqa: E402

GFX = gs.p("res", "graphics", "pokedex")
PREVIEW = gs.p("docs", "opal", "previews")

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
def rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


BANK1 = [  # normal art
    rgb("34354A"),  # 0 backdrop (never drawn by art tiles)
    rgb("34354A"),  # 1 slate
    rgb("3F3B52"),  # 2 violet slate
    rgb("5C4C77"),  # 3 mineral violet (frames)
    rgb("865D82"),  # 4 amethyst edge
    rgb("D8CBDC"),  # 5 light amethyst
    rgb("FAF6F4"),  # 6 pearl
    rgb("F0E9EC"),  # 7 pearl shade
    rgb("8EA5A5"),  # 8 opal blue-green
    rgb("C4A87B"),  # 9 antique gold
    rgb("E6D6B0"),  # 10 gold light
    rgb("8F7547"),  # 11 gold dark
    rgb("EEDFE8"),  # 12 opal pink tint
    rgb("E1EDE8"),  # 13 opal mint tint
    rgb("23243A"),  # 14 deep shadow
    rgb("FFFFFF"),  # 15 highlight
]
BANK2 = list(BANK1)  # selected tab: amethyst fill, gold frame
BANK2[3] = rgb("C4A87B")
BANK2[6] = rgb("D8CBDC")
BANK2[7] = rgb("C8B8D0")
BANK2[12] = rgb("E0D0E2")
BANK2[13] = rgb("D0C8E0")
BANK3 = list(BANK1)  # pressed: deeper amethyst, dark frame
BANK3[3] = rgb("3F3B52")
BANK3[6] = rgb("B09CC8")
BANK3[7] = rgb("A08CB8")
BANK3[12] = rgb("B8A4CC")
BANK3[13] = rgb("A8A0CC")
BANK0 = [  # text window colours + stat bars (TEXT_COLOR indices in opalref.c)
    rgb("34354A"),  # 0 transparent / backdrop
    rgb("292D40"),  # 1 ink
    rgb("D3CADB"),  # 2 soft shadow
    rgb("6B4F9E"),  # 3 accent violet
    rgb("967328"),  # 4 gold text
    rgb("706C84"),  # 5 dim
    rgb("2F7D5E"),  # 6 good
    rgb("A8453F"),  # 7 bad
    rgb("FAF6F4"),  # 8 header pearl
    rgb("23243A"),  # 9 header shadow
    rgb("B9A9D6"),  # 10 bar low
    rgb("8A6FC2"),  # 11 bar mid
    rgb("5E3FA0"),  # 12 bar high
    rgb("C4A87B"),  # 13 bar max (gold)
    rgb("E5DDEA"),  # 14 bar track
    rgb("FFFFFF"),  # 15
]


def palette_jasc():
    cols = BANK0 + BANK1 + BANK2 + BANK3
    cols += [(0, 0, 0)] * (256 - len(cols))
    lines = ["JASC-PAL", "0100", "256"] + ["%d %d %d" % c for c in cols]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Painter
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, fill=1):
        self.w, self.h = w, h
        self.px = [[fill] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def frame(self, x, y, w, h, c):
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def polygon(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % len(pts)]
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(round(xs[i])), int(round(xs[i + 1])) + 1):
                    self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def plate(self, x, y, w, h, frame=3, fill=6, shade=7, hi=15, speck=True):
        """Pearl plate with a 1px frame, rounded corners, top highlight and soft opal speckle."""
        self.rect(x, y, w, h, frame)
        self.rect(x + 1, y + 1, w - 2, h - 2, fill)
        for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
            self.set(cx, cy, 1)
        self.hline(x + 2, y + 1, w - 4, hi)
        self.hline(x + 1, y + h - 2, w - 2, shade)
        if speck:
            for i in range(w - 6):
                if (i * 5) % 11 == 0:
                    self.set(x + 3 + i, y + 2 + (i % 3), 12)
                if (i * 7) % 13 == 0:
                    self.set(x + 3 + i, y + h - 4 - (i % 2), 13)

    def gem(self, cx, cy, r=8):
        """Faceted opal-style gem (octagon crown + pavilion)."""
        top = [(cx - r // 2, cy - r), (cx + r // 2, cy - r), (cx + r, cy - r // 3), (cx, cy + r), (cx - r, cy - r // 3)]
        self.polygon(top, 8)
        # facets
        self.polygon([(cx - r // 2, cy - r), (cx + r // 2, cy - r), (cx + r // 4, cy - r // 3), (cx - r // 4, cy - r // 3)], 15)
        self.polygon([(cx - r, cy - r // 3), (cx - r // 4, cy - r // 3), (cx, cy + r)], 5)
        self.polygon([(cx + r, cy - r // 3), (cx + r // 4, cy - r // 3), (cx, cy + r)], 4)
        self.polygon([(cx - r // 4, cy - r // 3), (cx + r // 4, cy - r // 3), (cx, cy + r)], 13)
        self.line(cx - r // 2, cy - r, cx - r // 4, cy - r // 3, 12)
        self.line(cx + r // 2, cy - r, cx + r // 4, cy - r // 3, 12)
        # outline in gold
        pts = top + [top[0]]
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], 9)
        self.set(cx - r // 3, cy - r // 2, 15)
        self.set(cx - r // 3 + 1, cy - r // 2, 15)


FONT = {  # 5x7 caps, '#' = ink
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
}


def glyph(canvas, ch, x, y, c):
    for row, bits in enumerate(FONT[ch]):
        for col, b in enumerate(bits):
            if b == "#":
                canvas.set(x + col, y + row, c)


# ---------------------------------------------------------------------------
# Art
# ---------------------------------------------------------------------------
def header_band(c, h, y0=0):
    """Violet gradient band with a gold rule along its lower edge."""
    for y in range(h):
        if y < h * 0.40:
            base = 2
        elif y < h * 0.70:
            base = 2 if (y % 2 == 0) else 3
        else:
            base = 3
        for x in range(c.w):
            v = base
            if base in (2, 3) and (x + y) % 8 == 0 and y > 1:
                v = 4 if y > h * 0.55 else 3
            c.set(x, y0 + y, v)
    c.hline(0, y0 + h - 2, c.w, 11)
    c.hline(0, y0 + h - 1, c.w, 9)


def main_art():
    c = Canvas(256, 192, 1)
    # outer slate field with faint diagonal weave
    for y in range(192):
        for x in range(256):
            if (x + y) % 16 == 0:
                c.set(x, y, 2)
    header_band(c, 24)
    c.gem(16, 12, 8)
    # tiny gold studs along the header (restrained trim)
    for x in range(200, 252, 12):
        c.set(x, 11, 9)
        c.set(x + 1, 11, 10)
    # panel: amethyst edge, gold inner hairline, pearl interior with diagonal opal shimmer
    px, py, pw, ph = 4, 26, 248, 160
    c.rect(px, py, pw, ph, 4)
    c.rect(px + 1, py + 1, pw - 2, ph - 2, 9)
    c.rect(px + 2, py + 2, pw - 4, ph - 4, 6)
    for y in range(py + 2, py + ph - 2):
        for x in range(px + 2, px + pw - 2):
            d = (x + y) % 16
            if d in (0, 1):
                c.set(x, y, 7)
            elif d == 8:
                c.set(x, y, 12)
            elif d == 9:
                c.set(x, y, 13)
    c.hline(px + 2, py + 2, pw - 4, 15)
    c.hline(px + 2, py + ph - 3, pw - 4, 5)
    # corner ornaments
    for ox, oy, dx, dy in ((px + 4, py + 4, 1, 1), (px + pw - 5, py + 4, -1, 1), (px + 4, py + ph - 5, 1, -1), (px + pw - 5, py + ph - 5, -1, -1)):
        for i in range(5):
            c.set(ox + dx * i, oy, 11)
            c.set(ox, oy + dy * i, 11)
        c.set(ox + dx, oy + dy, 9)
    # footer rule
    c.hline(0, 189, 256, 11)
    for x in range(4, 256, 8):
        c.set(x, 190, 9)
    return c


def sub_art():
    c = Canvas(256, 192, 1)
    for y in range(192):
        for x in range(256):
            if (x + y) % 8 == 0:
                c.set(x, y, 2)
    header_band(c, 16)
    # group frames (gold hairlines with notched corners)
    def group(x, y, w, h):
        c.frame(x, y, w, h, 11)
        c.frame(x + 1, y + 1, w - 2, h - 2, 2)
        for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
            c.set(cx, cy, 9)

    group(12, 33, 232, 70)
    group(12, 107, 232, 34)
    group(68, 142, 120, 30)
    # tabs
    from_x = 16
    for row in range(2):
        for col in range(4):
            x = from_x + col * 56 + 2
            y = 40 + row * 32 + 1
            c.plate(x, y, 52, 22)
    # prev / up / down / next
    for i in range(4):
        c.plate(16 + i * 56 + 2, 112 + 1, 52, 22)
    # back
    c.plate(72 + 2, 144 + 1, 108, 22)
    # divider gems
    c.gem(128, 25, 5)
    # hint rule
    c.hline(12, 174, 232, 11)
    c.hline(12, 175, 232, 2)
    c.gem(128, 184, 4)
    return c


def entry_art():
    """32x96 vertical plate: gem + O P A L / D A T A in a 5x7 pixel face."""
    c = Canvas(32, 96, 1)
    c.plate(0, 0, 32, 96, speck=True)
    c.frame(2, 2, 28, 92, 9)
    c.gem(16, 11, 6)
    for i, ch in enumerate("OPAL"):
        glyph(c, ch, 13, 21 + i * 8, 2)
    c.hline(9, 54, 14, 9)
    for i, ch in enumerate("DATA"):
        glyph(c, ch, 13, 58 + i * 8, 2)
    return c


# ---------------------------------------------------------------------------
# Tiles / tilemaps / files
# ---------------------------------------------------------------------------
def to_tiles(canvas, bank, tile_offset=0):
    """Deduplicate 8x8 tiles. Returns (unique tiles, tilemap entries[list of u16])."""
    tiles = []
    index = {}
    entries = []
    for ty in range(canvas.h // 8):
        for tx in range(canvas.w // 8):
            t = tuple(canvas.px[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            entries.append((index[t] + tile_offset) | (bank << 12))
    return tiles, entries


def tiles_png(tiles, path_palette):
    """Indexed 4bpp PNG, 16 tiles per row (8 px tall rows)."""
    per_row = 16
    rows = (len(tiles) + per_row - 1) // per_row
    w, h = per_row * 8, rows * 8
    pix = [[0] * w for _ in range(h)]
    for i, t in enumerate(tiles):
        tx, ty = (i % per_row) * 8, (i // per_row) * 8
        for y in range(8):
            for x in range(8):
                pix[ty + y][tx + x] = t[y * 8 + x]
    return indexed_png(pix, w, h, 4, path_palette)


def indexed_png(pix, w, h, depth, palette):
    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        return c + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(h):
        raw.append(0)
        row = pix[y]
        if depth == 4:
            for x in range(0, w, 2):
                raw.append((row[x] << 4) | row[x + 1])
        else:
            raw.extend(row)
    plte = b"".join(bytes(c) for c in palette[: (1 << depth)])
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, depth, 3, 0, 0, 0))
    out += chunk(b"PLTE", plte)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return out


def rgb_png(pix_rgb, w, h):
    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        return c + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(pix_rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    out = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    return out + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def nscr(width_tiles, height_tiles, entries):
    """Nitro screen data (same container layout as the existing res/graphics/pokedex/*.NSCR)."""
    data = b"".join(struct.pack("<H", e) for e in entries)
    body = struct.pack("<HHII", width_tiles * 8, height_tiles * 8, 0, len(data)) + data
    # section tag bytes 4e 52 43 53, file magic 52 43 53 4e (matches the existing Pokedex NSCR files)
    nrcs = b"\x4e\x52\x43\x53" + struct.pack("<I", len(body) + 8) + body
    header = b"\x52\x43\x53\x4e" + b"\xff\xfe\x00\x01" + struct.pack("<I", 16 + len(nrcs)) + struct.pack("<HH", 16, 1)
    return header + nrcs


def render_preview(canvas, bank_palette, scale=1):
    w, h = canvas.w * scale, canvas.h * scale
    buf = bytearray(w * h * 3)
    for y in range(h):
        for x in range(w):
            col = bank_palette[canvas.px[y // scale][x // scale]]
            o = (y * w + x) * 3
            buf[o:o + 3] = bytes(col)
    return rgb_png(buf, w, h)


def build():
    out = {}
    main = main_art()
    sub = sub_art()
    entry = entry_art()

    mt, me = to_tiles(main, 1)
    st, se = to_tiles(sub, 1)
    et, ee = to_tiles(entry, 13, tile_offset=480)  # lives after the 480 entry_sub tiles in SUB_2

    out["opal_ref.pal"] = palette_jasc().encode()
    out["opal_ref_main.png"] = tiles_png(mt, BANK1)
    out["opal_ref_main.NSCR"] = nscr(32, 24, me)
    out["opal_ref_sub.png"] = tiles_png(st, BANK1)
    out["opal_ref_sub.NSCR"] = nscr(32, 24, se)
    out["opal_entry.png"] = tiles_png(et, BANK1)
    out["opal_entry.NSCR"] = nscr(4, 12, ee)

    previews = {
        "opal_ref_main.png": render_preview(main, BANK1, 2),
        "opal_ref_sub.png": render_preview(sub, BANK1, 2),
        "opal_ref_sub_selected_tab.png": render_preview(sub, BANK2, 2),
        "opal_entry.png": render_preview(entry, BANK1, 4),
        "opal_entry_pressed.png": render_preview(entry, BANK3, 4),
    }
    stats = {"main_tiles": len(mt), "sub_tiles": len(st), "entry_tiles": len(et)}
    return out, previews, stats


def main():
    check = "--check" in sys.argv
    out, previews, stats = build()
    # tile budgets (4bpp, 32 bytes/tile): SUB_1 char block 512 tiles, SUB_2 1024, MAIN_3 1024
    assert stats["main_tiles"] <= 1024, stats
    assert stats["sub_tiles"] <= 480, stats  # entry plate tiles start at 480 on SUB_2
    assert stats["entry_tiles"] <= 40, stats
    if check:
        stale = []
        for name, data in out.items():
            path = os.path.join(GFX, name)
            if not os.path.exists(path) or open(path, "rb").read() != data:
                stale.append(name)
        for name, data in previews.items():
            path = os.path.join(PREVIEW, name)
            if not os.path.exists(path) or open(path, "rb").read() != data:
                stale.append("preview:" + name)
        if stale:
            print("STALE:", ", ".join(stale))
            sys.exit(1)
        print("opal ref assets current", stats)
        return
    os.makedirs(PREVIEW, exist_ok=True)
    for name, data in out.items():
        with open(os.path.join(GFX, name), "wb") as f:
            f.write(data)
    for name, data in previews.items():
        with open(os.path.join(PREVIEW, name), "wb") as f:
            f.write(data)
    print("wrote", ", ".join(out), stats)


if __name__ == "__main__":
    main()
