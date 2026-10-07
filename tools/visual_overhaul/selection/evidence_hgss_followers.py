#!/usr/bin/env python3
"""Evidence closure D: HGSS follower-Pokemon NSBTX sheets as a component library (the follower *system* stays deferred).

Decodes the 2-palette, 8-texture mmodel sheets (572 = 538 x 32x32 + 34 x 64x64), measures frame distinctness, writes a
representative contact sheet and per-sheet metrics. Read-only on the HGSS checkout; modifies no Platinum resource.

  usage: evidence_hgss_followers.py --hgss-root DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import nsbmd_preview as N  # noqa: E402

OUT = ROOT / "docs/visual_overhaul/selection/mining/evidence"


def decode_sheet(d: bytes):
    mdl, tex = N.parse_bmd(d)
    T = N.parse_tex0(d, tex)
    if len(T["texs"]) != 8 or len(T["pals"]) != 2:
        return None
    pals = T["pal_order"]
    frames = {p: [] for p in pals}
    for nm, tx in T["texs"].items():
        for p in pals:
            frames[p].append(N.decode_tex(d, T, tx, p))
    return list(T["texs"]), pals, frames


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", type=Path, required=True)
    ap.add_argument("--sample", type=int, default=28)
    a = ap.parse_args()
    D = a.hgss_root / "files/data/mmodel/mmodel"
    rows, sheets = [], []
    for f in sorted(D.glob("*.NSBTX")):
        r = decode_sheet(f.read_bytes())
        if not r:
            continue
        names, pals, fr = r
        p0, p1 = pals
        a0 = fr[p0]
        distinct = len({hashlib.sha1(x.tobytes()).hexdigest() for x in a0})
        bbox_h = [int(np.ptp(np.where(x[..., 3] > 0)[0]) + 1) if (x[..., 3] > 0).any() else 0 for x in a0]
        rows.append({"file": f.name, "size": a0[0].shape[1], "frames": len(a0), "distinct_frames": distinct, "palettes": 2, "max_sprite_h": max(bbox_h),
                     "shiny_differs": bool(any((x != y).any() for x, y in zip(fr[p0], fr[p1]))), "tex_names": names[:8]})
        sheets.append((f.name, a0, fr[p1]))
    step = max(1, len(sheets) // a.sample)
    pick = sheets[::step][: a.sample]
    cell = 32
    S = Image.new("RGB", (8 * (cell + 1) * 2 + 8, len(pick) * (cell + 1)), (40, 60, 40))
    for r, (nm, f0, f1) in enumerate(pick):
        for k in range(8):
            for off, fr in ((0, f0), (8 * (cell + 1) + 8, f1)):
                im = Image.fromarray(fr[k], "RGBA")
                if im.width != cell:
                    im = im.resize((cell, cell), Image.NEAREST)
                S.paste(im, (off + k * (cell + 1), r * (cell + 1)), im)
    sp = OUT / "hgss_follower_sheets.png"
    S.save(sp, optimize=True)
    big = [r for r in rows if r["size"] == 64]
    res = {"schema_version": 1, "sheets": len(rows), "size_32": sum(r["size"] == 32 for r in rows), "size_64": len(big), "frames_per_sheet": 8,
           "mean_distinct_frames": round(sum(r["distinct_frames"] for r in rows) / max(1, len(rows)), 2), "shiny_palette_differs": sum(r["shiny_differs"] for r in rows),
           "sample_png": str(sp.relative_to(ROOT)), "rows": rows}
    (OUT / "hgss_follower_sheets.json").write_text(json.dumps(res, indent=1) + "\n")
    print({k: v for k, v in res.items() if k != "rows"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
