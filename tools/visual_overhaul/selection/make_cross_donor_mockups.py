#!/usr/bin/env python3
"""Cross-donor implementation-plan evidence mockups (design evidence only).

Generates the three comparison sheets referenced by
docs/visual_overhaul/selection/CROSS_DONOR_IMPLEMENTATION_PLAN.md into
docs/visual_overhaul/selection/synthesis/.

READ-ONLY with respect to the game: nothing under res/ or src/ is written.
Every composite below is an *indicative procedural simulation* (deterministic
rules on the real Platinum index data, existing palette entries only). It is
not final art; final art is hand-authored at implementation time and goes
through human visual review.
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "visual_overhaul" / "selection" / "synthesis"
TRAINERS = ROOT / "res" / "trainers" / "classes"
HGSS_RENDERS = ROOT / "docs" / "visual_overhaul" / "catalog_extensions" / "hgss_trainer_sprites" / "renders"
TERRAIN = ROOT / "res" / "graphics" / "battle" / "terrain"
EVID = ROOT / "docs" / "visual_overhaul" / "selection" / "mining" / "evidence"

FONT = ImageFont.load_default()
BG = (206, 214, 224)


def read_pal(path):
    lines = path.read_text().split("\n")[3:]
    return [tuple(int(v) for v in ln.split()) for ln in lines if ln.strip()][:16]


def to_rgba(idx_im, pal):
    px = idx_im.load()
    out = Image.new("RGBA", idx_im.size)
    op = out.load()
    for y in range(idx_im.height):
        for x in range(idx_im.width):
            i = px[x, y]
            op[x, y] = (0, 0, 0, 0) if i == 0 else (*pal[i], 255)
    return out


def label(draw, xy, text, fill=(20, 30, 50)):
    draw.text(xy, text, fill=fill, font=FONT)


# --------------------------------------------------------------------------
# Track A: Ace Trainer component enhancement
# --------------------------------------------------------------------------

def neighbours(px, w, h, x, y):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            yield px[nx, ny]
        else:
            yield 0


def enhance_female(src):
    im = src.copy()
    px, ref = im.load(), src.load()
    w, h = im.size
    # 1. hair: re-derive clustered highlight bands from Platinum's own 3 greens
    for y in range(5, 30):
        for x in range(33, 62):
            i = ref[x, y]
            if i not in (4, 5):
                continue
            band = ((x * 2 + y * 3) % 14) // 4  # diagonal strand bands, 0..3
            below = ref[x, y + 1] if y + 1 < h else 0
            right = ref[x + 1, y]
            shadow_edge = below in (6, 15) or right in (6, 15)
            if band == 3 or shadow_edge:
                px[x, y] = 5
            elif band == 2 and i == 5:
                px[x, y] = 4
            else:
                px[x, y] = 4 if i == 4 else i
            if shadow_edge and band == 3 and below == 6:
                px[x, y] = 6
    # 2. jacket: zip-seam highlight + collar notch using the existing light brown
    for y in range(33, 42):
        for x in range(30, 44):
            if ref[x, y] == 8 and ref[x - 1, y] in (8, 9) and (y % 2 == 1):
                px[x, y] = 7
    for x in range(36, 42):  # hem seam
        if ref[x, 44] in (8, 9, 7):
            px[x, 44] = 8
    return im


def enhance_male(src):
    im = src.copy()
    px, ref = im.load(), src.load()
    # 1. fold shading: 1px light folds on the sleeve/torso mid-brown (idx 8)
    for y in range(25, 37):
        for x in range(30, 50):
            if ref[x, y] == 8 and (x + 2 * y) % 4 == 0 and ref[x, y - 1] in (8, 3, 7):
                px[x, y] = 7
    # 2. centre zip highlight line
    for y in range(26, 36):
        if ref[40, y] in (7, 8, 3):
            px[40, y] = 7
    # 3. hem seam
    for x in range(36, 46):
        if ref[x, 36] in (7, 8, 3, 9):
            px[x, 36] = 8
    # 4. fingerless glove on the free (left) hand: dark glove over the palm
    for y in range(47, 51):
        for x in range(24, 31):
            if ref[x, y] in (8, 9, 11, 12):
                px[x, y] = 3 if ref[x, y] != 12 else 12
    return im


def track_a():
    pal = read_pal_from_png(TRAINERS / "ace_trainer_male" / "front.png")
    rows = []
    stats = {}
    for name, fn, hid in (("male", enhance_male, "024"), ("female", enhance_female, "025")):
        base = Image.open(TRAINERS / f"ace_trainer_{name}" / "front.png")
        enh = fn(base)
        a, b = base.load(), enh.load()
        changed = sum(1 for y in range(80) for x in range(80) if a[x, y] != b[x, y])
        opaque = sum(1 for y in range(80) for x in range(80) if a[x, y] != 0)
        stats[name] = {"opaque_px": opaque, "changed_px": changed, "pct_changed": round(100 * changed / opaque, 1)}
        donor = Image.open(HGSS_RENDERS / f"front_{hid}.png").convert("RGBA")
        prov = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
        pp = prov.load()
        for y in range(80):
            for x in range(80):
                if a[x, y] == 0 and b[x, y] == 0:
                    continue
                pp[x, y] = (255, 214, 0, 255) if a[x, y] != b[x, y] else (150, 160, 175, 255)
        rows.append((to_rgba(base, pal), donor, to_rgba(enh, pal), prov))
    s = 4
    pad = 8
    head = 22
    cw = 80 * s
    sheet = Image.new("RGBA", (4 * cw + 5 * pad, 2 * (cw + head) + 3 * pad + 70), BG + (255,))
    d = ImageDraw.Draw(sheet)
    titles = ["1. Platinum baseline (res/trainers/classes)", "2. HGSS donor (reference only)",
              "3. Proposed composite (indicative)", "4. Provenance map"]
    y = pad
    for r, row in enumerate(rows):
        for c, im in enumerate(row):
            x = pad + c * (cw + pad)
            if r == 0:
                label(d, (x, y), titles[c])
            tile = Image.new("RGBA", (cw, cw), (57, 115, 172, 255) if c != 1 else (53, 170, 140, 255))
            if c == 3:
                tile = Image.new("RGBA", (cw, cw), (40, 48, 64, 255))
            tile.alpha_composite(im.resize((cw, cw), Image.NEAREST))
            sheet.alpha_composite(tile, (x, y + head))
        y += cw + head + pad
    label(d, (pad, y), "Provenance: grey = Platinum-native pixel untouched | yellow = newly authored/derived pixel (shading re-expressed in the Platinum ramp).", )
    label(d, (pad, y + 14), "Direct donor pixels: 0   Modified donor pixels: 0   (HGSS contributes shading *treatment*, not pixels.)")
    label(d, (pad, y + 28), "Indicative procedural simulation on the real Platinum index data, existing 16-colour palette only. Not final art;")
    label(d, (pad, y + 42), "final pixels are hand-authored per the plan and require human visual review before any import.")
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(OUT / "track_a_ace_trainer_comparison.png")
    return stats


def read_pal_from_png(path):
    im = Image.open(path)
    flat = im.getpalette()[:48]
    return [tuple(flat[i:i + 3]) for i in range(0, 48, 3)]


# --------------------------------------------------------------------------
# Track B: palette cycling on the battle terrain platform
# --------------------------------------------------------------------------

def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def cycle_frames(terrain, palfile, nframes=8, scale=3):
    pal = read_pal(TERRAIN / terrain / palfile)
    base = Image.open(TERRAIN / terrain / "enemy.png")
    px = base.load()
    w, h = base.size
    # crest ramp = non-outline indices lighter than the platform body (idx 8)
    body = lum(pal[8])
    crest = [i for i in range(3, 15) if lum(pal[i]) > body + 12]
    crest.sort(key=lambda i: lum(pal[i]))
    ramp = [pal[i] for i in crest]
    n = max(len(ramp), 1)
    frames = []
    for f in range(nframes):
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        op = out.load()
        for y in range(h):
            for x in range(w):
                i = px[x, y]
                if i == 0:
                    continue
                if i in crest:
                    phase = (x // 4 - f) % (2 * n)  # travelling crest, ping-pong ramp
                    k = phase if phase < n else 2 * n - 1 - phase
                    op[x, y] = (*ramp[k], 255)
                else:
                    op[x, y] = (*pal[i], 255)
        frames.append(out.resize((w * scale, h * scale), Image.NEAREST))
    return frames, crest


def track_b():
    frames, crest = cycle_frames("water", "day.pal", 8)
    w, h = frames[0].size
    donor = Image.open(EVID / "pmd_mapbg_bpa_d17p33a.png").convert("RGBA")
    dw = donor.width // 4
    donor_tiles = [donor.crop((i * dw, 0, (i + 1) * dw, donor.height)) for i in range(4)]
    dscale = w / dw
    donor_tiles = [t.resize((w, int(t.height * dscale)), Image.LANCZOS) for t in donor_tiles]
    pad = 8
    cols = 4
    sheet_w = cols * (w + pad) + pad
    sheet = Image.new("RGBA", (sheet_w, 22 + donor_tiles[0].height + 22 + 2 * (h + pad) + 62), BG + (255,))
    d = ImageDraw.Draw(sheet)
    y = pad
    label(d, (pad, y), "PMD Sky MAP_BG d17p33a (animated-tile + palette-animation technique) - REFERENCE ONLY, no pixels reused")
    y += 14
    for i, t in enumerate(donor_tiles):
        sheet.alpha_composite(t, (pad + i * (w + pad), y))
    y += donor_tiles[0].height + pad
    label(d, (pad, y), "Platinum water terrain platform (G5 palette day.pal): frames 0-7 of the proposed crest cycle (indicative simulation)")
    y += 14
    for i, fr in enumerate(frames):
        row, col = divmod(i, cols)
        bgc = Image.new("RGBA", fr.size, (184, 216, 255, 255))
        bgc.alpha_composite(fr)
        sheet.alpha_composite(bgc, (pad + col * (w + pad), y + row * (h + pad)))
    y += 2 * (h + pad)
    label(d, (pad, y), "Baseline = a single static frame. Proposal = same sprite, same 16-colour budget, crest indices cycled each N frames")
    label(d, (pad, y + 14), "by a data-driven table (terrain, first_index, count, period). Needs one-time re-authoring so crest pixels are phase-coded.")
    label(d, (pad, y + 28), "Reusable: distortion_world cracks (pulse), cave crystals (glint), ice (glint), league arenas, any 4bpp BG/OBJ palette.")
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(OUT / "track_b_water_platform_palette_cycle.png")
    frames_rgb = []
    for fr in frames:
        bgc = Image.new("RGBA", fr.size, (184, 216, 255, 255))
        bgc.alpha_composite(fr)
        frames_rgb.append(bgc.convert("RGB"))
    frames_rgb[0].save(OUT / "track_b_water_platform_palette_cycle.gif", save_all=True,
                       append_images=frames_rgb[1:], duration=120, loop=0)
    return {"crest_indices": crest}


# --------------------------------------------------------------------------
# Track C: Sinnoh newspaper still-scene card (layout mockup)
# --------------------------------------------------------------------------

NAVY = (28, 45, 66)
PAPER = (232, 238, 247)
INK = (40, 52, 74)
TEAL = (62, 140, 150)
RULE = (120, 136, 160)


def track_c():
    W, H, S = 256, 192, 3
    card = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(card)
    d.rectangle((0, 0, W - 1, H - 1), outline=NAVY)
    d.rectangle((3, 3, W - 4, H - 4), outline=RULE)
    # masthead
    d.rectangle((6, 6, W - 7, 30), fill=NAVY)
    d.text((14, 12), "POKeMON NEWS PRESS", fill=PAPER, font=FONT)
    d.text((14, 22), "SINNOH EDITION", fill=(160, 190, 220), font=FONT)
    d.text((W - 98, 12), "Vol. 12  Solaceon", fill=PAPER, font=FONT)
    d.line((6, 34, W - 7, 34), fill=NAVY)
    # headline
    d.text((10, 38), "WEEKLY POKe BALL ROUNDUP", fill=NAVY, font=FONT)
    d.line((10, 50, W - 11, 50), fill=RULE)
    # illustration well with real Platinum item icons
    d.rectangle((10, 56, 98, 124), outline=NAVY, fill=(214, 226, 240))
    icons = ["dusk_ball", "heal_ball", "quick_ball", "dive_ball"]
    for k, n in enumerate(icons):
        p = ROOT / "res" / "items" / "icons" / f"{n}.png"
        if p.exists():
            ic = Image.open(p).convert("P")
            pal = ic.getpalette()
            rgba = Image.new("RGBA", ic.size)
            ip, rp = ic.load(), rgba.load()
            for yy in range(ic.height):
                for xx in range(ic.width):
                    v = ip[xx, yy]
                    rp[xx, yy] = (0, 0, 0, 0) if v == 0 else (pal[v * 3], pal[v * 3 + 1], pal[v * 3 + 2], 255)
            card.paste(rgba, (20 + (k % 2) * 36, 62 + (k // 2) * 30), rgba)
    d.text((12, 128), "Fig. 1  New Ball types", fill=INK, font=FONT)
    # body columns (placeholder rules, real text uses Platinum font/message path)
    for col, x0 in enumerate((106, 182)):
        for r in range(9):
            d.line((x0, 58 + r * 9, x0 + 66, 58 + r * 9), fill=RULE)
    d.text((106, 134), "Dusk . Heal . Quick . Dive", fill=TEAL, font=FONT)
    # article tab strip (state: selected = Dusk Ball)
    d.line((6, 152, W - 7, 152), fill=NAVY)
    tabs = ["Dusk Ball", "Heal Ball", "Quick Ball", "Dive Ball"]
    for k, t in enumerate(tabs):
        x0 = 10 + k * 60
        sel = k == 0
        d.rectangle((x0, 156, x0 + 56, 173), fill=NAVY if sel else (200, 212, 228), outline=NAVY)
        d.text((x0 + 6, 161), t, fill=PAPER if sel else INK, font=FONT)
    d.text((10, 178), "Up/Down: article    A: read    B: close", fill=INK, font=FONT)
    big = card.resize((W * S, H * S), Image.NEAREST)
    sheet = Image.new("RGB", (W * S + 16, H * S + 90), BG)
    sheet.paste(big, (8, 8))
    d2 = ImageDraw.Draw(sheet)
    base_y = H * S + 16
    d2.text((8, base_y), "Layout mockup (256x192 top-screen card). Platinum-native: item icons (res/items/icons), G7 navy/teal palette, message path.", fill=(20, 30, 50), font=FONT)
    d2.text((8, base_y + 14), "Ranger 2 contributes layout/composition only (masthead / headline / well / column / state-tab), zero donor pixels.", fill=(20, 30, 50), font=FONT)
    d2.text((8, base_y + 28), "Placeholder typography (PIL bitmap font); shipped text goes through Platinum's message/text pipeline. Illustration well is a stand-in for authored art.", fill=(20, 30, 50), font=FONT)
    d2.text((8, base_y + 42), "Baseline today: a PC menu + plain message-box text; no still-scene presentation exists in Platinum.", fill=(20, 30, 50), font=FONT)
    sheet.save(OUT / "track_c_news_press_card_mockup.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stats = {"track_a": track_a(), "track_b": track_b()}
    track_c()
    (OUT / "mockup_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
