#!/usr/bin/env python3
"""Evidence closure B2: Ranger 2 Pokemon pose-set families (_w / _a* / _s / _t) via the existing package renderer.

Renders every res/prebuilt/data/poke/p*_LZ.bin package (all NCER sets), records per-set cell counts, cell sizes and
whether the set is a coherent frame sequence, and writes contact sheets of a deterministic sample. No Platinum resource is touched.

  usage: evidence_ranger_poke.py --ranger-root /path/to/pokeranger2
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
import render_ranger_pokemon_package as rp  # noqa: E402

OUT = ROOT / "docs/visual_overhaul/selection/mining/evidence"


def suffix(stem: str) -> str:
    m = re.search(r"_([a-z])\d*$", stem)
    return m.group(1) if m else "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranger-root", type=Path, required=True)
    ap.add_argument("--sample", type=int, default=14)
    a = ap.parse_args()
    pkgs = sorted((a.ranger_root / "res/prebuilt/data/poke").glob("p*_LZ.bin"))
    OUT.mkdir(parents=True, exist_ok=True)
    rows, errors, rendered = {}, [], {}
    step = max(1, len(pkgs) // a.sample)
    sample = {p.name for p in pkgs[::step][: a.sample]}
    sheet_rows = []
    for p in pkgs:
        with tempfile.TemporaryDirectory() as t:
            try:
                import io, contextlib
                with contextlib.redirect_stdout(io.StringIO()):
                    rp.render_package(p, Path(t), 32)
            except Exception as e:  # noqa: BLE001
                errors.append({"package": p.name, "error": repr(e)[:120]})
                continue
            info = {}
            row_imgs = {}
            for d in sorted(Path(t).iterdir()):
                if not d.is_dir() or d.name == "_cac":
                    continue
                cells = sorted(d.glob("cell_*.png"))
                sizes, nonblank = set(), 0
                imgs = []
                for c in cells:
                    im = Image.open(c).convert("RGBA")
                    sizes.add(im.size)
                    nonblank += im.getchannel("A").getbbox() is not None
                    imgs.append(im)
                info[d.name] = {"set": suffix(d.name), "cells": len(cells), "nonblank": nonblank, "sizes": sorted(sizes)[:4]}
                if p.name in sample:
                    row_imgs[d.name] = imgs
            rows[p.name] = info
            if row_imgs:
                sheet_rows.append((p.name, row_imgs))
    # contact sheet: per package, per set, up to 6 frames
    T = 48
    height = sum(len(r) * (T + 2) for _, r in sheet_rows)
    sheet = Image.new("RGB", (6 * (T + 2) + 4, max(height, 1)), (60, 60, 80))
    y = 0
    for _, r in sheet_rows:
        for _, imgs in sorted(r.items()):
            for i, im in enumerate(imgs[:6]):
                if im.getbbox() is None:
                    continue
                s = min(T / im.width, T / im.height, 2.0)
                im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.NEAREST)
                sheet.paste(im2, (2 + i * (T + 2), y), im2)
            y += T + 2
    sp = OUT / "ranger_poke_sets.png"
    sheet.save(sp, optimize=True)
    tot = {}
    for info in rows.values():
        for s in info.values():
            k = s["set"]
            t = tot.setdefault(k, {"sets": 0, "cells": 0, "nonblank_sets": 0, "min_cells": 999, "max_cells": 0})
            t["sets"] += 1
            t["cells"] += s["cells"]
            t["nonblank_sets"] += s["nonblank"] > 0
            t["min_cells"] = min(t["min_cells"], s["cells"])
            t["max_cells"] = max(t["max_cells"], s["cells"])
    (OUT / "ranger_poke_sets.json").write_text(json.dumps({"schema_version": 1, "packages": rows, "errors": errors, "totals_by_set": tot,
                                                             "sample_sheet": str(sp.relative_to(ROOT)), "sample_packages": sorted(sample)}, indent=1) + "\n")
    print(f"packages {len(pkgs)}, rendered {len(rows)}, errors {len(errors)}, totals {tot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
