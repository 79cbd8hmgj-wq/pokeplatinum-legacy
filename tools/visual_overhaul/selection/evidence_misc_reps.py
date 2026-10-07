#!/usr/bin/env python3
"""Evidence closure A/B/C tail: representative renders for the small needs-evidence families.

  * Ranger 2 interface packages i024 / i059 / i072_* (NCER cells, existing package renderer)
  * HGSS mmodel NSBTX sheets 22 / 54 / 69 / 70, HGSS egg + shadow battle forms (decomp PNGs)
  * PMD Sky GROUND/p09p01a1.wan (SkyTemple decode, all frames)
Writes one contact sheet + JSON metrics under mining/evidence/. Read-only on donor checkouts.

  usage: evidence_misc_reps.py --ranger-root D --hgss-root D --pmd-root D
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import nsbmd_preview as N  # noqa: E402
import recover_lane_b_ranger_embedded as rb  # noqa: E402
import render_ranger_ncer_preview as rnp  # noqa: E402

OUT = ROOT / "docs/visual_overhaul/selection/mining/evidence"


def row(imgs, cell=48, n=12):
    S = Image.new("RGB", (n * (cell + 2), cell + 2), (56, 56, 76))
    for i, im in enumerate(imgs[:n]):
        im = im.convert("RGBA")
        k = min(cell / im.width, cell / im.height, 3.0)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)
        S.paste(im, (i * (cell + 2), 0), im)
    return S


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranger-root", type=Path, required=True)
    ap.add_argument("--hgss-root", type=Path, required=True)
    ap.add_argument("--pmd-root", type=Path, required=True)
    a = ap.parse_args()
    rows, labels, metrics = [], [], {}
    import ntft_tex
    for pk in ("i024", "i059", "i072_00", "i072_01", "i072_02"):
        cells = []
        if pk.startswith("i072"):
            base = a.ranger_root / f"res/prebuilt/data/interface/{pk}"
            mode, w_, h_, px, _ = ntft_tex.decode_ntft(base.with_suffix(".ntft").read_bytes(), ntft_tex.read_ntfp(base.with_suffix(".ntfp")))
            im = Image.new("RGBA", (w_, h_))
            im.putdata([(*[(c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31], al) for al, c in px])
            cells = [im]
            rows.append(row(cells, cell=96, n=2))
            labels.append(f"ranger_interface/{pk}")
            metrics[f"ranger_interface/{pk}"] = {"ntft_mode": mode, "size": [w_, h_]}
            continue
        with tempfile.TemporaryDirectory() as t:
            mem = rb.load_members(a.ranger_root / f"res/prebuilt/data/interface/{pk}_LZ.bin", Path(t))
            pal = rnp.read_palette(next(p for n, p in sorted(mem.items()) if n.endswith(".NCLR")))
            gfx = [p for n, p in sorted(mem.items()) if n.endswith((".NCBR", ".NCGR"))]
            ncer = [p for n, p in sorted(mem.items()) if n.endswith(".NCER")]
            if not ncer:  # raster NCBR bitmap and/or NSCR tilemap packages (no cell bank)
                from evidence_ranger_tiled import read_pal
                nclr = [p for n, p in sorted(mem.items()) if n.endswith(".NCLR")]
                pal2 = read_pal(nclr[-1])
                scr = [p for n, p in sorted(mem.items()) if n.endswith(".NSCR")]
                if scr and gfx:
                    tiles, bpp = rb.read_chars_bg(gfx[0])
                    w_, h_, ent = rb.read_nscr(scr[0])
                    img, _mx = rb.render_screen(w_, h_, ent, tiles, bpp, len(pal2))
                    im = Image.new("RGBA", (w_, h_), (0, 0, 0, 255))
                    im.putdata([(*pal2[v], 255) if v and v < len(pal2) else (0, 0, 0, 255) for v in img])
                    cells.append(im)
                elif gfx:
                    sw, sh, tiles = rnp.read_chars(gfx[0], cells=None)
                    w_, h_, px = sw, len(tiles) * 64 // max(1, sw), None
                    im = Image.new("RGBA", (sw, max(1, len(tiles) * 64 // sw)))
                    flat = [v for tile in tiles for v in tile]
                    flat += [0] * (im.width * im.height - len(flat))
                    im.putdata([(*pal2[v], 255) if v < len(pal2) else (255, 0, 255, 255) for v in flat[: im.width * im.height]])
                    cells.append(im)
            for gp, cp in zip(gfx, ncer):
                bank = rnp.read_cells(cp)
                sw, _sh, tiles = rnp.read_chars(gp, cells=bank)
                for oams in bank:
                    w_, h_, px = rnp.render_cell(oams, sw, tiles, 32)
                    tmp = Path(t) / "c.png"
                    rnp.write_indexed_png(tmp, w_, h_, px, pal)
                    cells.append(Image.open(tmp).convert("RGBA").copy())
        rows.append(row(cells))
        labels.append(f"ranger_interface/{pk}")
        metrics[f"ranger_interface/{pk}"] = {"cells": len(cells), "sizes": sorted({c.size for c in cells})[:4]}
    for n in (22, 54, 69, 70):
        d = (a.hgss_root / f"files/data/mmodel/mmodel/mmodel_{n:08d}.NSBTX").read_bytes()
        T = N.parse_tex0(d, N.parse_bmd(d)[1])
        ims = [Image.fromarray(N.decode_tex(d, T, tx, nm), "RGBA") for nm, tx in T["texs"].items()]
        rows.append(row(ims))
        labels.append(f"hgss_mmodel_{n}")
        metrics[f"hgss_mmodel_{n}"] = {"textures": len(ims), "sizes": sorted({im.size for im in ims}), "palettes": len(T["pals"])}
    for nm, p in (("form_egg_manaphy", "egg/manaphy.png"), ("form_egg_normal", "egg/normal.png"), ("form_shadow", "shadow.png")):
        im = Image.open(a.hgss_root / "files/poketool/pokegra/otherpoke" / p).convert("RGBA")
        rows.append(row([im], cell=96, n=2))
        labels.append(nm)
        metrics[nm] = {"size": list(im.size)}
    from skytemple_files.graphics.wan_wat.handler import WanHandler
    w = WanHandler.deserialize((a.pmd_root / "files/GROUND/p09p01a1.wan").read_bytes())
    fr = [w.render_frame(f)[0] for f in w.frames]
    rows.append(row(fr, cell=40))
    labels.append("pmd_ground_p09p01a1.wan")
    metrics["pmd_ground_p09p01a1.wan"] = {"frames": len(fr), "anim_groups": len(w.anim_groups), "frame_size": list(fr[0].size) if fr else None}
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height for r in rows)), (30, 30, 40))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(OUT / "misc_representatives.png", optimize=True)
    (OUT / "misc_representatives.json").write_text(json.dumps({"schema_version": 1, "rows": labels, "metrics": metrics}, indent=1) + "\n")
    print(labels, metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
