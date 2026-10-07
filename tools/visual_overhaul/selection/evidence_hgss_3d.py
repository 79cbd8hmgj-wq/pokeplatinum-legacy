#!/usr/bin/env python3
"""Evidence closure C: HGSS field/building 3D resources vs Platinum, by targeted census (no full HGSS recatalog).

Sources (pinned donor checkouts, read-only):
  HGSS files/fielddata/build_model/bm_field.narc (340 BMD0 outdoor buildings), bm_room.narc (222 BMD0 interiors),
       files/a/0/4/4 (106 BTX0 map texture sets), files/a/0/6/5 (676 land-data blobs: terrain NSBMD)
  Platinum res/field/props/models (NSBMD props/buildings), res/field/props/texture_sets, res/field/maps/texture_sets
Writes mining/evidence/hgss_3d_census.json + contact sheets. Nothing under res/ or src/ is modified.

  usage: evidence_hgss_3d.py --hgss-root DIR [--pt-root DIR] [--render]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import ndspy.narc
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import nsbmd_preview as N  # noqa: E402

OUT = ROOT / "docs/visual_overhaul/selection/mining/evidence"


def tex_hashes(d: bytes):
    """[(name, w, h, fmt, exact_hash, near_hash, rgba)] for every texture in a BMD0/BTX0 blob."""
    mdl, tex = N.parse_bmd(d)
    if tex is None:
        return []
    T = N.parse_tex0(d, tex)
    out = []
    for nm, tx in T["texs"].items():
        try:
            im = N.decode_tex(d, T, tx, nm)
        except Exception:  # noqa: BLE001
            continue
        if not (im[..., 3] > 0).any():
            continue
        ex = hashlib.sha1(im.tobytes() + bytes([tx["w"] & 255, tx["h"] & 255])).hexdigest()[:16]
        small = np.asarray(Image.fromarray(im, "RGBA").convert("RGB").resize((8, 8), Image.BOX)) // 24
        near = hashlib.sha1(small.tobytes()).hexdigest()[:12]
        out.append((nm, tx["w"], tx["h"], tx["fmt"], ex, near, im))
    return out


def model_stats(d: bytes):
    mdl, tex = N.parse_bmd(d)
    m = N.parse_models(d, mdl)[0]
    tris = 0
    mn = np.array([1e9] * 3)
    mx = -mn
    for _, dl in m["shapes"]:
        for t in N.parse_dl(dl, m["scale"]):
            tris += 1
            for v in t:
                mn = np.minimum(mn, v[0])
                mx = np.maximum(mx, v[0])
    return {"name": m["name"], "shapes": len(m["shapes"]), "tris": tris, "extent": [round(float(x), 2) for x in (mx - mn)] if tris else [0, 0, 0]}


def sheet(images, path: Path, cols=16, cell=64):
    rows = (len(images) + cols - 1) // cols
    s = Image.new("RGB", (cols * (cell + 1), rows * (cell + 1)), (30, 30, 40))
    for i, im in enumerate(images):
        im = (Image.fromarray(im, "RGBA") if isinstance(im, np.ndarray) else im).convert("RGBA")
        k = min(cell / im.width, cell / im.height)
        im2 = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)
        s.paste(im2, ((i % cols) * (cell + 1), (i // cols) * (cell + 1)), im2)
    s.save(path, optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", type=Path, required=True)
    ap.add_argument("--pt-root", type=Path, default=ROOT)
    ap.add_argument("--render", action="store_true")
    a = ap.parse_args()
    H, P = a.hgss_root / "files", a.pt_root / "res/field"
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"schema_version": 1}

    # --- Platinum texture universe (props + map sets + embedded in prop models)
    pt_ex, pt_near, pt_n = set(), set(), 0
    for f in list((P / "props/texture_sets").glob("*.nsbtx")) + list((P / "maps/texture_sets").glob("*.nsbtx")) + list((P / "props/models").glob("*.nsbmd")):
        for nm, w, h, fmt, ex, near, _ in tex_hashes(f.read_bytes()):
            pt_n += 1
            pt_ex.add(ex)
            pt_near.add(near)
    res["platinum"] = {"textures_decoded": pt_n, "unique_exact": len(pt_ex), "prop_models": len(list((P / "props/models").glob("*.nsbmd"))),
                       "prop_texture_sets": len(list((P / "props/texture_sets").glob("*.nsbtx"))), "map_texture_sets": len(list((P / "maps/texture_sets").glob("*.nsbtx")))}

    # --- HGSS map texture sets (a/0/4/4)
    novel_imgs, shared = [], 0
    seen = set()
    n_tex = 0
    sets = []
    for i, blob in enumerate(ndspy.narc.NARC.fromFile(str(H / "a/0/4/4")).files):
        th = tex_hashes(blob)
        sets.append(len(th))
        for nm, w, h, fmt, ex, near, im in th:
            n_tex += 1
            if ex in seen:
                continue
            seen.add(ex)
            if ex in pt_ex:
                shared += 1
            elif near in pt_near:
                shared += 0  # near-match: recolour/variation of a Platinum texture; counted separately below
            else:
                novel_imgs.append((w * h, nm, im))
    near_only = 0
    seen2 = set()
    for blob in ndspy.narc.NARC.fromFile(str(H / "a/0/4/4")).files:
        for nm, w, h, fmt, ex, near, im in tex_hashes(blob):
            if ex in seen2:
                continue
            seen2.add(ex)
            if ex not in pt_ex and near in pt_near:
                near_only += 1
    res["hgss_map_textures"] = {"sets": len(sets), "textures": n_tex, "unique_exact": len(seen), "identical_to_platinum": shared, "near_match_only": near_only,
                                "novel_unique": len(novel_imgs), "novel_pct": round(100 * len(novel_imgs) / max(1, len(seen)), 1),
                                "novel_names_sample": sorted({n for _, n, _ in novel_imgs})[:60]}
    novel_imgs.sort(key=lambda t: -t[0])
    sheet([t[2] for t in novel_imgs[:512]], OUT / "hgss_map_textures_novel.png", cols=32, cell=48)

    # --- HGSS buildings
    for key, nf in (("bm_field", "bm_field.narc"), ("bm_room", "bm_room.narc")):
        files = ndspy.narc.NARC.fromFile(str(H / "fielddata/build_model" / nf)).files
        rows, bt_new, bt_all, imgs = [], 0, 0, []
        for i, blob in enumerate(files):
            try:
                st = model_stats(blob)
                th = tex_hashes(blob)
            except Exception as e:  # noqa: BLE001
                rows.append({"idx": i, "error": repr(e)[:80]})
                continue
            st["idx"] = i
            st["textures"] = len(th)
            st["tex_novel"] = sum(1 for t in th if t[4] not in pt_ex and t[5] not in pt_near)
            st["tex_identical_pt"] = sum(1 for t in th if t[4] in pt_ex)
            rows.append(st)
            if a.render and st["tris"]:
                try:
                    im, _ = N.render_model(blob, size=96)
                    if im:
                        imgs.append(im)
                except Exception:  # noqa: BLE001
                    pass
        ok = [r for r in rows if "tris" in r]
        res[key] = {"models": len(files), "decoded": len(ok), "errors": len(rows) - len(ok), "tris_total": sum(r["tris"] for r in ok),
                    "with_any_novel_texture": sum(1 for r in ok if r["tex_novel"]), "all_textures_identical_to_platinum": sum(1 for r in ok if r["textures"] and r["tex_identical_pt"] == r["textures"]),
                    "no_texture": sum(1 for r in ok if not r["textures"]), "rows": rows}
        if imgs:
            sheet(imgs, OUT / f"hgss_{key}_models.png", cols=20, cell=96)

    # --- HGSS land data terrain
    land = ndspy.narc.NARC.fromFile(str(H / "a/0/6/5")).files
    tri_counts, terr_ok = [], 0
    for blob in land:
        try:
            pm, props, model_sz = struct.unpack_from("<III", blob, 0)
            mo = 16 + pm + props
            mo = blob.find(b"BMD0", mo, mo + 64)
            if mo < 0:
                continue
            mb = blob[mo:mo + model_sz]
            if mb[:4] != b"BMD0":
                continue
            m = N.parse_models(mb, N.parse_bmd(mb)[0])[0]
            tri_counts.append(sum(len(N.parse_dl(dl, m["scale"])) for _, dl in m["shapes"]))
            terr_ok += 1
        except Exception:  # noqa: BLE001
            pass
    res["hgss_land_data"] = {"maps": len(land), "terrain_models_decoded": terr_ok, "tris_median": int(np.median(tri_counts)) if tri_counts else 0, "tris_max": max(tri_counts or [0])}
    (OUT / "hgss_3d_census.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk not in ("rows", "novel_names_sample")} if isinstance(v, dict) else v) for k, v in res.items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
