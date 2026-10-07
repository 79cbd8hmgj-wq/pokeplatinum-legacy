#!/usr/bin/env python3
"""Evidence closure A1: PMD Sky MAP_BG animated-tile (BPA) and palette-animation (BPL) families.

Decodes every MAP_BG background that owns a .bpa companion (the 85 'pmd_mapbg_*<digit>' needs_evidence groups) with the
SkyTemple file library, measures how much of the composed image actually animates, and renders a few representative
strips. Reads the pinned pmd-sky checkout only; writes evidence JSON + small PNGs; touches no Platinum resource.

  usage: evidence_pmd_mapbg.py --pmd-root /path/to/pmd-sky
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT_JSON = ROOT / "docs/visual_overhaul/selection/mining/evidence/pmd_mapbg_bpa.json"
OUT_DIR = ROOT / "docs/visual_overhaul/selection/mining/evidence"

REPS = {"d": ["d01p11a", "d14p12a"], "v": None, "p": None, "h": None, "g": None, "t": None, "s": None}  # filled by family below


def load(root: Path, stem: str):
    from skytemple_files.graphics.bma.handler import BmaHandler
    from skytemple_files.graphics.bpa.handler import BpaHandler
    from skytemple_files.graphics.bpc.handler import BpcHandler
    from skytemple_files.graphics.bpl.handler import BplHandler
    R = root / "files/MAP_BG"
    bma = BmaHandler.deserialize((R / f"{stem}.bma").read_bytes())
    bpl = BplHandler.deserialize((R / f"{stem}.bpl").read_bytes())
    bpc = BpcHandler.deserialize((R / f"{stem}.bpc").read_bytes(), tiling_width=bma.tiling_width, tiling_height=bma.tiling_height)
    bpas = [None] * 8
    names = []
    for p in sorted(R.glob(f"{stem}?.bpa")):
        d = int(p.stem[-1])
        if 1 <= d <= 8:
            bpas[d - 1] = BpaHandler.deserialize(p.read_bytes())
            names.append(p.name)
    return bma, bpl, bpc, bpas, names


def analyse(root: Path, stem: str, keep_frames: bool):
    bma, bpl, bpc, bpas, names = load(root, stem)
    pal_ani_ok = True
    try:
        frames = bma.to_pil(bpc, bpl, bpas, bpl.has_palette_animation, False)
    except ValueError:  # skytemple-files + current Pillow reject putpalette on the palette-animation path; BPA frames still render
        pal_ani_ok = False
        frames = bma.to_pil(bpc, bpl, bpas, False, False)
    nf = len(frames)
    arr = [np.asarray(f.convert("RGBA")).astype(np.int16) for f in frames]
    h, w = arr[0].shape[:2]
    diff = np.zeros((h, w), bool)
    for a in arr[1:]:
        diff |= (np.abs(a - arr[0]).sum(axis=2) > 0)
    rec = {
        "stem": stem, "bpa_files": names, "canvas": [w, h], "frames": nf, "bpa_frames": [b.number_of_frames if b else 0 for b in bpas],
        "bpa_tiles": [b.number_of_tiles if b else 0 for b in bpas], "palette_animation": bool(bpl.has_palette_animation),
        "animated_px_pct": round(100.0 * float(diff.mean()), 2) if nf > 1 else 0.0,
        "layers": bma.number_of_layers, "palette_animation_rendered": pal_ani_ok or not bpl.has_palette_animation,
    }
    return rec, (frames if keep_frames else None)


def strip(frames, path: Path, crop_to_motion: bool = True):
    arr = [np.asarray(f.convert("RGBA")).astype(np.int16) for f in frames]
    diff = np.zeros(arr[0].shape[:2], bool)
    for a in arr[1:]:
        diff |= (np.abs(a - arr[0]).sum(axis=2) > 0)
    ys, xs = np.where(diff)
    if len(ys) and crop_to_motion:
        pad = 24
        box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(arr[0].shape[1], xs.max() + pad), min(arr[0].shape[0], ys.max() + pad))
    else:
        box = (0, 0, arr[0].shape[1], arr[0].shape[0])
    if box[2] - box[0] > 512:
        c = (box[0] + box[2]) // 2
        box = (c - 256, box[1], c + 256, box[3])
    if box[3] - box[1] > 256:
        c = (box[1] + box[3]) // 2
        box = (box[0], c - 128, box[2], c + 128)
    pick = [frames[i] for i in sorted({0, len(frames) // 4, len(frames) // 2, 3 * len(frames) // 4})][:4]
    tiles = [f.convert("RGB").crop(box) for f in pick]
    W, H = tiles[0].size
    sheet = Image.new("RGB", (W * len(tiles) + 4 * (len(tiles) - 1), H), (40, 0, 40))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * (W + 4), 0))
    sheet.save(path, optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmd-root", type=Path, required=True)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    R = a.pmd_root / "files/MAP_BG"
    stems = sorted({p.stem[:-1] for p in R.glob("*?.bpa")})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows, errors = [], []
    best = {}
    for s in stems:
        try:
            rec, fr = analyse(a.pmd_root, s, keep_frames=not a.no_render)
        except Exception as e:  # noqa: BLE001
            errors.append({"stem": s, "error": repr(e)[:200]})
            continue
        rows.append(rec)
        if fr is not None and rec["frames"] > 1:
            fam = s[0]
            if fam not in best or rec["animated_px_pct"] * min(rec["frames"], 8) > best[fam][0]:
                best[fam] = (rec["animated_px_pct"] * min(rec["frames"], 8), s, fr)
    rendered = {}
    for fam, (_, s, fr) in best.items():
        p = OUT_DIR / f"pmd_mapbg_bpa_{s}.png"
        strip(fr, p)
        rendered[fam] = {"stem": s, "png": str(p.relative_to(ROOT))}
    # palette-animated backgrounds without BPA (technique census; not part of the queue)
    pal_only = []
    for p in sorted(R.glob("*.bpl")):
        st = p.stem
        if st in stems:
            continue
        try:
            from skytemple_files.graphics.bpl.handler import BplHandler
            if BplHandler.deserialize(p.read_bytes()).has_palette_animation:
                pal_only.append(st)
        except Exception:  # noqa: BLE001
            pass
    OUT_JSON.write_text(json.dumps({"schema_version": 1, "source": "pmd-sky files/MAP_BG via skytemple-files", "rows": rows, "errors": errors,
                                    "representative_renders": rendered, "palette_animated_without_bpa": pal_only}, indent=1) + "\n")
    print(f"decoded {len(rows)}/{len(stems)} stems, errors {len(errors)}, animated {sum(r['frames'] > 1 for r in rows)}, palette-only bgs {len(pal_only)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
