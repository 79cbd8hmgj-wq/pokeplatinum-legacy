#!/usr/bin/env python3
"""Evidence closure B1: minimum tiled-background (NCGR+NCLR+NSCR) preview for Ranger 2 event / ending / title / menu bundles.

Not a general Ranger renderer: LZ10 -> NARC -> first NSCR(s) + NCGR + NCLR -> composed BG preview, reusing the
verified helpers in recover_lane_b_ranger_embedded.py. Renders every tilemap bundle, writes per-bundle metrics plus
family contact sheets. Reads the pinned pokeranger2 checkout only.

  usage: evidence_ranger_tiled.py --ranger-root /path/to/pokeranger2
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import recover_lane_b_ranger_embedded as rb  # noqa: E402

OUT = ROOT / "docs/visual_overhaul/selection/mining/evidence"
FAMILIES = {"event": "ranger_event", "ending": "ranger_ending", "title": "ranger_title", "menu": "ranger_menu"}


def read_pal(path: Path):
    raw = path.read_bytes()
    size = struct.unpack_from("<I", raw, 0x20)[0]
    cols = []
    for pos in range(0x28, min(len(raw), 0x28 + size), 2):
        v = struct.unpack_from("<H", raw, pos)[0]
        cols.append(((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31))
    return cols


def render(pkg: Path):
    with tempfile.TemporaryDirectory() as t:
        mem = rb.load_members(pkg, Path(t))
        by = {}
        for n, p in sorted(mem.items()):
            by.setdefault(n.rsplit(".", 1)[-1], []).append(p)
        if not (by.get("NSCR") and by.get("NCGR") and by.get("NCLR")):
            return None, {"members": {k: len(v) for k, v in by.items()}, "error": "no NSCR+NCGR+NCLR"}
        tiles, bpp = rb.read_chars_bg(by["NCGR"][0])
        pal = read_pal(by["NCLR"][0])
        shots = []
        for sp in by["NSCR"][:4]:
            w, h, ent = rb.read_nscr(sp)
            img, mx = rb.render_screen(w, h, ent, tiles, bpp, len(pal))
            im = Image.new("RGB", (w, h), (255, 0, 255))
            px = im.load()
            nz = 0
            cols = set()
            for i, v in enumerate(img):
                if v:
                    nz += 1
                    c = pal[v] if v < len(pal) else (255, 0, 255)
                    cols.add(c)
                    px[i % w, i // w] = c
                else:
                    px[i % w, i // w] = pal[0] if pal else (0, 0, 0)
            a = np.asarray(im).astype(int)
            r, g, b = a[..., 0], a[..., 1], a[..., 2]
            paper = ((r > 200) & (g > 195) & (b > 165) & (r - b < 70) & (r - b > 10)).mean()
            green = ((g > r + 25) & (g > b + 25)).mean()
            shots.append((im, {"w": w, "h": h, "nonzero_pct": round(100 * nz / (w * h), 1), "colors": len(cols), "max_index": mx, "paper_pct": round(100 * float(paper), 1),
                               "green_pct": round(100 * float(green), 1)}))
        meta = {"members": {k: len(v) for k, v in by.items()}, "bpp": bpp, "tiles": len(tiles), "pal_colors": len(pal), "screens": [m for _, m in shots]}
        return shots, meta


def sheet(items, path: Path, cols=8, tw=128, th=96):
    rows = (len(items) + cols - 1) // cols
    s = Image.new("RGB", (cols * (tw + 2), rows * (th + 2)), (24, 24, 24))
    for i, im in enumerate(items):
        s.paste(im.convert("RGB").resize((tw, th), Image.NEAREST), ((i % cols) * (tw + 2), (i // cols) * (th + 2)))
    s.save(path, optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranger-root", type=Path, required=True)
    a = ap.parse_args()
    D = a.ranger_root / "res/prebuilt/data"
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": 1, "source": "pokeranger2 res/prebuilt/data", "bundles": {}, "sheets": {}}
    for sub, fam in FAMILIES.items():
        thumbs = []
        for p in sorted((D / sub).glob("*_LZ.bin")):
            try:
                shots, meta = render(p)
            except Exception as e:  # noqa: BLE001
                result["bundles"][p.name] = {"family": fam, "error": repr(e)[:160]}
                continue
            meta["family"] = fam
            result["bundles"][p.name] = meta
            if shots:
                thumbs.append(shots[0][0])
        if thumbs:
            sp = OUT / f"ranger_tiled_{sub}.png"
            sheet(thumbs, sp)
            result["sheets"][sub] = {"png": str(sp.relative_to(ROOT)), "n": len(thumbs)}
    (OUT / "ranger_tiled_bundles.json").write_text(json.dumps(result, indent=1) + "\n")
    ok = sum(1 for b in result["bundles"].values() if b.get("screens"))
    print(f"bundles {len(result['bundles'])}, rendered {ok}, sheets {result['sheets']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
