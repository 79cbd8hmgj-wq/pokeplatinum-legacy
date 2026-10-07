#!/usr/bin/env python3
"""Evidence closure E: targeted HGSS party (plist_gra) / Pokedex (zukan_gra) / camera viewfinder UI preview next to Platinum's counterparts.

Only the three catalogued HGSS UI groups are touched. zukan_gra and the viewfinder are decomp PNGs (indexed); plist_gra NSCR
screens are composed with the minimal tilemap helpers from the Ranger work. Read-only; no Platinum resource is modified.

  usage: evidence_hgss_ui.py --hgss-root DIR
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import recover_lane_b_ranger_embedded as rb  # noqa: E402
from evidence_ranger_tiled import read_pal  # noqa: E402

OUT = ROOT / "docs/visual_overhaul/selection/mining/evidence"


def grid(imgs, path, cols, cell_w, cell_h, bg=(48, 48, 64)):
    rows = (len(imgs) + cols - 1) // cols
    S = Image.new("RGB", (cols * (cell_w + 2), rows * (cell_h + 2)), bg)
    for i, im in enumerate(imgs):
        im = im.convert("RGBA")
        k = min(cell_w / im.width, cell_h / im.height, 2.0)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)
        S.paste(im, ((i % cols) * (cell_w + 2), (i // cols) * (cell_h + 2)), im)
    S.save(path, optimize=True)


def plist_screens(G: Path, stem: str = "plist_gra"):
    files = sorted(G.glob(stem + "_*"))
    num = lambda p: int(re.search(r"_(\d+)\.", p.name).group(1))
    by = {p: num(p) for p in files}
    out = []
    for s in [p for p in files if p.suffix == "NSCR" or p.name.endswith(".NSCR")]:
        n = by[s]
        pre = [p for p in files if by[p] < n]
        gfx = [p for p in pre if p.name.endswith(".NCGR")][-2:]
        pal = [p for p in pre if p.name.endswith(".NCLR")][-1:]
        if not gfx or not pal:
            continue
        try:
            w, h, ent = rb.read_nscr(s)
        except Exception:  # noqa: BLE001
            continue
        P = read_pal(pal[0])
        for g in gfx[::-1]:
            try:
                tiles, bpp = rb.read_chars_bg(g)
            except Exception:  # noqa: BLE001
                continue
            img, mx = rb.render_screen(w, h, ent, tiles, bpp, len(P))
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            px = im.load()
            for i, v in enumerate(img):
                px[i % w, i // w] = (*P[v], 255) if v and v < len(P) else (0, 0, 0, 255)
            out.append((f"{s.name}+{g.name}", im))
            break
    return out


def png_tiles(path: Path):
    im = Image.open(path)
    if im.mode not in ("P", "L"):
        raise ValueError("not indexed")
    W, H = im.size
    vals = list(im.getdata())
    if im.mode == "L" and all(v % 17 == 0 for v in vals):
        vals = [v // 17 for v in vals]  # 4-bit grayscale PNG: PIL scales index*17
    bpp = 4 if max(vals) < 16 else 8
    tiles = []
    for ty in range(H // 8):
        for tx in range(W // 8):
            tiles.append([vals[(ty * 8 + y) * W + tx * 8 + x] for y in range(8) for x in range(8)])
    return tiles, bpp


def png_screens(G: Path, stem: str):
    files = sorted(G.glob(stem + "_*"))
    num = lambda p: int(re.search(r"_(\d+)\.", p.name).group(1))
    out = []
    for s in [p for p in files if p.name.endswith(".NSCR")]:
        n = num(s)
        pre = [p for p in files if num(p) < n]
        png = [p for p in pre if p.name.endswith(".png")][-1:]
        pal = [p for p in pre if p.name.endswith(".NCLR")][-1:] or [p for p in files if p.name.endswith(".NCLR")][:1]
        if not png or not pal:
            continue
        try:
            w, h, ent = rb.read_nscr(s)
            tiles, bpp = png_tiles(png[0])
        except Exception:  # noqa: BLE001
            continue
        P = read_pal(pal[0])
        img, mx = rb.render_screen(w, h, ent, tiles, bpp, len(P))
        im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        px = im.load()
        for i, v in enumerate(img):
            if v and v < len(P):
                px[i % w, i // w] = (*P[v], 255)
        out.append((f"{s.name}+{png[0].name}", im))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", type=Path, required=True)
    ap.add_argument("--pt-root", type=Path, default=ROOT)
    a = ap.parse_args()
    G = a.hgss_root / "files/graphic"
    zuk = [Image.open(p) for p in sorted((G / "zukan_gra").glob("*.png"))]
    pt = [Image.open(p) for p in sorted((a.pt_root / "res/graphics/pokedex").glob("*.png"))]
    OUT.mkdir(parents=True, exist_ok=True)
    grid(zuk, OUT / "hgss_zukan_gra.png", 8, 120, 96)
    grid(pt, OUT / "platinum_pokedex_png.png", 8, 120, 96)
    cam = Image.open(G / "camera_viewfinder/camera_viewfinder.png")
    pl = plist_screens(G / "plist_gra")
    zs = png_screens(G / "zukan_gra", "zukan_gra")
    grid([im for _, im in zs], OUT / "hgss_zukan_screens.png", 4, 256, 192)
    grid([cam] + [im for _, im in pl], OUT / "hgss_camera_plist.png", 3, 256, 192)
    meta = {"schema_version": 1, "zukan_gra_png": len(zuk), "platinum_pokedex_png": len(pt), "camera_viewfinder_size": list(cam.size), "plist_screens": [n for n, _ in pl], "zukan_screens": [n for n, _ in zs],
            "sheets": ["hgss_zukan_gra.png", "platinum_pokedex_png.png", "hgss_camera_plist.png"]}
    (OUT / "hgss_ui_targeted.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
