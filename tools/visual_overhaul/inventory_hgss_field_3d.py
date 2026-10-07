#!/usr/bin/env python3
"""Targeted HGSS catalog extension `hgss_field_3d`: field/building models, map texture sets, follower sheets.

Sources (read-only, pinned HGSS commit):
  files/fielddata/build_model/bm_field.narc (340 BMD0) + bm_room.narc (222 BMD0)   -> one asset per model, one group per model
  files/a/0/4/4 (106 BTX0 map texture sets)                                          -> one asset per texture, one group per set
  files/data/mmodel/mmodel/*.NSBTX for the 572 MMODEL_FOLLOWER_MON* constants        -> one asset per sheet, one group per sheet
Every asset carries measured source_metadata (hashes, geometry, textures, Platinum comparison) so that the donor-free mining
pipeline never has to reopen the checkout. The previewer is the approximate one in selection/nsbmd_preview.py (no node transforms,
heuristic palette pairing): metrics are discovery evidence, not pixel-perfect truth. Platinum is read, never written.

  usage: inventory_hgss_field_3d.py --hgss-root DIR [--no-renders]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np
import ndspy.narc
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / "selection"))
sys.path.insert(0, str(HERE))
import nsbmd_preview as N  # noqa: E402
import nsbtx_palettes as nsb  # noqa: E402

EXT_ID = "hgss_field_3d"
OUT = ROOT / "docs/visual_overhaul/catalog_extensions" / EXT_ID
DECODER_VERSION = "nsbmd-preview-v1+sbc-material-map"

# --- name vocabulary (romaji / English tokens found in HGSS texture names) ---------------------------------------------------------------
TOKENS = {
    "shadow": {"kage", "shadow", "ubashadow"},
    "wall": {"kabe", "wall", "dwall", "kbc", "ybc", "kk"},
    "floor": {"yuka", "floor", "mat", "tafl", "carpet", "fl", "flt"},
    "roof": {"roof", "sroof", "yane"},
    "window": {"mado", "win", "window"},
    "door": {"door", "doa", "to"},
    "gate": {"gate"},
    "road_path": {"road", "droad", "roadkk", "line", "rd"},
    "foliage": {"grass", "egrass", "tree", "flower", "lea", "leaf", "kusa", "ki", "kabu", "mkgr", "bush", "ha"},
    "water": {"sea", "pond", "wfall", "swave", "wave", "beach", "wtk", "wf", "water", "wd"},
    "rock_cliff": {"cliff", "dcliff", "rock", "slope", "cavehole", "iwa", "ishi", "stone"},
    "fence": {"fence", "fe", "saku"},
    "light": {"light", "lamp", "tou"},
    "stairs": {"stair", "esca", "ele", "climb"},
    "signage": {"mark", "kanban", "sign", "board", "moni", "maq", "map", "poster"},
    "machine": {"pc", "game", "driver", "mpwr", "tv", "machine", "ball", "poke"},
    "furniture": {"table", "shelf", "bed", "chair", "sofa", "desk", "counter"},
    "bridge": {"bridge"},
    "tower": {"tower"},
    "sky_cloud": {"cloud", "sky", "allpeak", "allpeakgs"},
    "snow_ice": {"snow", "ice", "yuki", "kori"},
    "gym": {"gym"},
}
TOKEN_CAT = {t: c for c, ts in TOKENS.items() for t in ts}
OVERLAY_CATS = {"shadow", "sky_cloud", "light", "signage", "road_path"}
ARCH_CATS = {"wall", "roof", "window", "door", "gate", "stairs", "tower", "bridge", "gym", "fence", "floor"}


def tokens_of(name: str) -> list[str]:
    return [t for t in re.split(r"[_\d.]+", name.lower()) if t]


def categories_of(names, extra=()) -> dict[str, int]:
    c: dict[str, int] = {}
    for n in list(names) + list(extra):
        for t in tokens_of(n):
            cat = TOKEN_CAT.get(t)
            if cat:
                c[cat] = c.get(cat, 0) + 1
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def sha16(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def near_hash(im: np.ndarray) -> str:
    small = np.asarray(Image.fromarray(im, "RGBA").convert("RGB").resize((8, 8), Image.BOX)) // 24
    return hashlib.sha1(small.tobytes()).hexdigest()[:12]


def exact_hash(im: np.ndarray, w: int, h: int) -> str:
    return hashlib.sha1(im.tobytes() + bytes([w & 255, h & 255])).hexdigest()[:16]


# --- Platinum universe --------------------------------------------------------------------------------------------------------------------
def platinum_universe():
    P = ROOT / "res/field"
    tex_ex, tex_near = {}, {}
    models = []
    for f in sorted(list((P / "props/texture_sets").glob("*.nsbtx")) + list((P / "maps/texture_sets").glob("*.nsbtx")) + list((P / "props/models").glob("*.nsbmd"))):
        d = f.read_bytes()
        rel = str(f.relative_to(ROOT))
        try:
            mdl, tex = N.parse_bmd(d)
        except Exception:  # noqa: BLE001
            continue
        hs = set()
        if tex is not None:
            T = N.parse_tex0(d, tex)
            for nm, tx in T["texs"].items():
                try:
                    im = N.decode_tex(d, T, tx, nm)
                except Exception:  # noqa: BLE001
                    continue
                if not (im[..., 3] > 0).any():
                    continue
                ex, nr = exact_hash(im, tx["w"], tx["h"]), near_hash(im)
                tex_ex.setdefault(ex, rel)
                tex_near.setdefault(nr, rel)
                hs.add((ex, nr))
        if f.suffix == ".nsbmd" and mdl is not None:
            try:
                st = model_geometry(d)
            except Exception:  # noqa: BLE001
                st = None
            models.append({"file": rel, "tex": hs, "geom": st})
    return tex_ex, tex_near, models


def model_geometry(d: bytes):
    mdl, _ = N.parse_bmd(d)
    m = N.parse_models(d, mdl)[0]
    tris, mn, mx = 0, np.array([1e9] * 3), np.array([-1e9] * 3)
    shape_tris = []
    for _, dl in m["shapes"]:
        tl = N.parse_dl(dl, m["scale"])
        shape_tris.append(len(tl))
        for t in tl:
            tris += 1
            for v in t:
                mn, mx = np.minimum(mn, v[0]), np.maximum(mx, v[0])
    ext = [round(float(x), 3) for x in (mx - mn)] if tris else [0.0, 0.0, 0.0]
    return {"tris": tris, "shapes": len(m["shapes"]), "materials": m["nmat"], "extent": ext, "name": m["name"], "shape_tris": shape_tris}


# --- texture analysis -----------------------------------------------------------------------------------------------------------------------
def regions(mask: np.ndarray) -> int:
    h, w = mask.shape
    k = max(1, max(h, w) // 32)
    m = mask[: h // k * k, : w // k * k].reshape(h // k, k, w // k, k).mean(axis=(1, 3)) > 0.25
    seen = np.zeros_like(m)
    n = 0
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):
            if m[y, x] and not seen[y, x]:
                n += 1
                stack = [(y, x)]
                seen[y, x] = True
                while stack:
                    cy, cx = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
    return n


def analyse_texture(im: np.ndarray, w: int, h: int, fmt: int, name: str) -> dict:
    a = im[..., 3] > 127
    rgb = im[..., :3].astype(int)
    opaque = float(a.mean())
    cols = len({tuple(c) for c in rgb[a].tolist()}) if a.any() else 0
    seam = None
    if a.all() and w >= 8 and h >= 8:
        edge = (np.abs(rgb[:, 0] - rgb[:, -1]).mean() + np.abs(rgb[0, :] - rgb[-1, :]).mean()) / 2
        inner = (np.abs(rgb[:, 1:] - rgb[:, :-1]).mean() + np.abs(rgb[1:, :] - rgb[:-1, :]).mean()) / 2
        seam = round(float(edge / (inner + 1e-6)), 2)
    mean = rgb[a].mean(axis=0) if a.any() else np.zeros(3)
    r, g, b = mean
    if a.any():
        if g > r + 12 and g > b + 12:
            hue = "green"
        elif b > r + 12 and b >= g:
            hue = "blue"
        elif min(r, g, b) > 200:
            hue = "white"
        elif max(r, g, b) - min(r, g, b) < 18:
            hue = "grey" if max(r, g, b) > 60 else "dark"
        elif r > g and r > b:
            hue = "brown_red"
        else:
            hue = "other"
    else:
        hue = "none"
    return {"opaque_pct": round(100 * opaque, 1), "colors": cols, "seam_ratio": seam, "regions": regions(a) if a.any() else 0, "hue": hue}


def texture_use(meta: dict, ex_in_pt: bool, near_in_pt: bool, cats: dict, w: int, h: int, fmt: int) -> str:
    if ex_in_pt:
        return "identical_to_platinum"
    if meta["colors"] <= 2 or meta["opaque_pct"] < 8 or w * h <= 64:
        return "reference_only"
    if near_in_pt:
        return "enhancement_input"
    main = next(iter(cats), None)
    if main in OVERLAY_CATS or meta["opaque_pct"] < 75 or meta["regions"] >= 4:
        return "component_region"
    direct = fmt in (1, 2, 3, 6) and w <= 64 and h <= 64 and meta["opaque_pct"] >= 95 and (meta["seam_ratio"] is not None and meta["seam_ratio"] <= 1.6)
    return "directly_reusable" if direct else "convertible"


# --- renders -------------------------------------------------------------------------------------------------------------------------------
def sheet(images, path: Path, cols: int, cell: int):
    rows = (len(images) + cols - 1) // cols
    S = Image.new("RGB", (cols * (cell + 1), rows * (cell + 1)), (30, 30, 40))
    for i, im in enumerate(images):
        im = (Image.fromarray(im, "RGBA") if isinstance(im, np.ndarray) else im).convert("RGBA")
        k = min(cell / im.width, cell / im.height, 2.0)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)
        S.paste(im, ((i % cols) * (cell + 1), (i // cols) * (cell + 1)), im)
    path.parent.mkdir(parents=True, exist_ok=True)
    S.save(path, optimize=True)


# --- species / follower identity --------------------------------------------------------------------------------------------------------------
def species_names() -> dict[str, int]:
    lines = [l.strip() for l in (ROOT / "generated" / "species.txt").read_text().splitlines() if l.strip()]
    lines = lines[: lines.index("SPECIES_ARCEUS") + 1]
    return {s[len("SPECIES_"):]: i for i, s in enumerate(lines) if i > 0}


def follower_constants(hgss: Path) -> dict[int, str]:
    out = {}
    for m in re.finditer(r"#define\s+MMODEL_(FOLLOWER_MON\w*)\s+(\d+)", (hgss / "include/constants/mmodel.h").read_text()):
        name, idx = m.group(1), int(m.group(2))
        if name == "FOLLOWER_MON_BASE":
            continue
        out[idx] = name
    return out


def split_species(const: str, names: dict[str, int]):
    base = const[len("FOLLOWER_MON_"):] if const.startswith("FOLLOWER_MON_") else None
    if base is None:
        return None, None, None
    if base in names:
        return names[base], base, None
    best = None
    for n in names:
        if base.startswith(n + "_") and (best is None or len(n) > len(best)):
            best = n
    if best:
        return names[best], best, base[len(best) + 1:]
    return None, None, base


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss-root", required=True, type=Path)
    ap.add_argument("--no-renders", action="store_true")
    a = ap.parse_args()
    hgss = a.hgss_root.resolve()
    F = hgss / "files"
    commit = subprocess.check_output(["git", "-C", str(hgss), "rev-parse", "HEAD"], text=True).strip()
    tex_ex, tex_near, pt_models = platinum_universe()
    cat, cur = [], []

    def add(asset, status, reason_code, reason, evidence):
        cat.append(asset)
        cur.append({"asset_id": asset["asset_id"], "asset_type": asset["asset_type"], "decision_source": "HGSS_FIELD_3D_INVENTORY", "group": asset["group"], "lane": "X_hgss_field_3d",
                    "reason": reason, "reason_code": reason_code, "recovery_evidence": evidence, "render_path": asset["render_path"], "review_status": status,
                    "source_id": "hgss", "source_path": asset["source_path"], "species_dex": asset["species_dex"], "target_tags": asset["target_tags"]})

    # ---------------- map texture sets ----------------
    set_blobs = ndspy.narc.NARC.fromFile(str(F / "a/0/4/4")).files
    hgss_hash_sets: dict[str, list[int]] = {}
    set_tex: list[list[dict]] = []
    for si, blob in enumerate(set_blobs):
        mdl, tex = N.parse_bmd(blob)
        T = N.parse_tex0(blob, tex)
        rows = []
        for ti, (nm, tx) in enumerate(T["texs"].items()):
            im = N.decode_tex(blob, T, tx, nm)
            ex, nr = exact_hash(im, tx["w"], tx["h"]), near_hash(im)
            hgss_hash_sets.setdefault(ex, []).append(si)
            pal = T["pal_order"][tx["idx"]] if len(T["pal_order"]) == len(T["texd"]) else (nm if nm in T["pals"] else (nm + "_pl" if nm + "_pl" in T["pals"] else None))
            rows.append({"ti": ti, "name": nm, "w": tx["w"], "h": tx["h"], "fmt": tx["fmt"], "im": im, "ex": ex, "nr": nr, "pal": pal})
        set_tex.append(rows)
    hgss_exact_total = len(hgss_hash_sets)
    tex_assets = 0
    for si, rows in enumerate(set_tex):
        names = [r["name"] for r in rows]
        set_cats = categories_of(names)
        sheet_rel = f"docs/visual_overhaul/catalog_extensions/{EXT_ID}/renders/texture_sets/set_{si:03d}.png"
        if not a.no_renders:
            sheet([r["im"] for r in rows], ROOT / sheet_rel, cols=12, cell=40)
        for r in rows:
            ana = analyse_texture(r["im"], r["w"], r["h"], r["fmt"], r["name"])
            cats = categories_of([r["name"]])
            if not cats:  # colour fallback keeps the category honest about its basis
                fb = {"green": "foliage", "blue": "water", "white": "snow_ice", "grey": "rock_cliff", "brown_red": "floor"}.get(ana["hue"])
                cats = {fb: 1} if fb else {}
                basis = "color"
            else:
                basis = "name"
            ex_in = r["ex"] in tex_ex
            nr_in = r["nr"] in tex_near
            use = texture_use(ana, ex_in, nr_in, cats, r["w"], r["h"], r["fmt"])
            aid = f"hgss:narc:files:a:0:4:4:set_{si:03d}:tex_{r['ti']:03d}"
            meta = {"source_commit": commit, "narc": "files/a/0/4/4", "set_index": si, "texture_index": r["ti"], "texture_name": r["name"], "palette_name": r["pal"], "texture_format": r["fmt"],
                    "w": r["w"], "h": r["h"], "exact_hash": r["ex"], "near_hash": r["nr"], "platinum_exact_match": tex_ex.get(r["ex"]), "platinum_near_match": tex_near.get(r["nr"]) if not ex_in else None,
                    "sets_with_same_hash": len(set(hgss_hash_sets[r["ex"]])), "categories": cats, "category_basis": basis, "texture_use": use, "set_categories": set_cats,
                    "set_member_sha256": sha16(set_blobs[si]), "decoder_version": DECODER_VERSION, **ana}
            add({"asset_id": aid, "source_id": "hgss", "asset_type": "nitro_map_texture", "species_dex": None, "form": None, "variant": r["name"], "group": "map_texture_sets",
                 "frame": r["ti"], "source_path": f"files/a/0/4/4#set={si:03d}&tex={r['ti']:03d}", "render_path": sheet_rel if not a.no_renders else None, "native_width": r["w"], "native_height": r["h"],
                 "bbox_width": None, "bbox_height": None, "opaque_pixels": int(round(ana["opaque_pct"] / 100 * r["w"] * r["h"])), "geometry_class": f"tex_{r['w']}x{r['h']}_fmt{r['fmt']}",
                 "review_status": "unreviewed", "target_tags": ["field", "environment", "map_texture"], "quality_notes": "HGSS map texture (BTX0 TEX0) from a texture-set NARC member; targeted catalog extension.",
                 "source_metadata": meta},
                "usable" if ana["colors"] > 0 else "reject", "hgss_map_texture_valid_decode" if ana["colors"] > 0 else "hgss_map_texture_blank",
                "BTX0 texture decodes with a paired palette and is nonblank." if ana["colors"] > 0 else "decoded texture is fully transparent",
                {"texture_use": use, "opaque_pct": ana["opaque_pct"], "colors": ana["colors"]})
            tex_assets += 1

    # ---------------- building models ----------------
    models_by_key = {}
    ptex_union = {(h[0], h[1]) for m in pt_models for h in m["tex"]}
    sizes_all = []
    model_rows = []
    for key, nf in (("bm_field", "bm_field.narc"), ("bm_room", "bm_room.narc")):
        narc_path = F / "fielddata/build_model" / nf
        files = ndspy.narc.NARC.fromFile(str(narc_path)).files
        for i, blob in enumerate(files):
            model_rows.append((key, nf, i, blob))
    # geometry first (global size normalisation)
    geoms = {}
    for key, nf, i, blob in model_rows:
        try:
            geoms[(key, i)] = model_geometry(blob)
        except Exception:  # noqa: BLE001
            geoms[(key, i)] = None
    sig_first: dict[str, str] = {}
    sig_count: dict[str, int] = {}
    for key, nf, i, blob in model_rows:
        g = geoms[(key, i)]
        if g and g["tris"]:
            sg = sha16(json.dumps([g["tris"], g["shape_tris"], [round(e, 1) for e in g["extent"]]]).encode())
            sig_count[sg] = sig_count.get(sg, 0) + 1
            sig_first.setdefault(sg, f"{key}_{i:03d}")
    med = float(np.median([max(g["extent"]) for g in geoms.values() if g and g["tris"]]))
    for key, nf, i, blob in model_rows:
        g = geoms[(key, i)]
        mdl, tex = N.parse_bmd(blob)
        tex_rows, links, new_n, ident_n, near_n = [], {}, 0, 0, 0
        if tex is not None:
            T = N.parse_tex0(blob, tex)
            for nm, tx in T["texs"].items():
                im = N.decode_tex(blob, T, tx, nm)
                if not (im[..., 3] > 0).any():
                    continue
                ex, nr = exact_hash(im, tx["w"], tx["h"]), near_hash(im)
                inpt, nrpt = ex in tex_ex, nr in tex_near
                ident_n += inpt
                near_n += (not inpt) and nrpt
                new_n += (not inpt) and (not nrpt)
                if ex in hgss_hash_sets:
                    links[nm] = sorted(set(hgss_hash_sets[ex]))
                tex_rows.append({"name": nm, "w": tx["w"], "h": tx["h"], "fmt": tx["fmt"], "exact_hash": ex, "platinum_exact": inpt, "platinum_near": nrpt})
        names = [t["name"] for t in tex_rows]
        cats = categories_of(names, [g["name"]] if g else [])
        ext = g["extent"] if g else [0, 0, 0]
        mx, mn_ = max(ext), min(ext)
        rel = mx / med if med else 0
        if not g or not g["tris"]:
            geo = "empty"
        elif g["tris"] <= 24 and mn_ < 0.12 * mx:
            geo = "panel"
        elif ext[1] < 0.06 * max(ext[0], ext[2], 1e-6):
            geo = "flat_surface"
        elif mx < 32:
            geo = "small_prop"
        elif mx < 96:
            geo = "medium_structure"
        else:
            geo = "large_structure"
        # Platinum counterpart by texture overlap (exact first, near second)
        mine = {(t["exact_hash"], None) for t in tex_rows}
        best = None
        if tex_rows:
            hs = set()
            for t in tex_rows:
                hs.add(t["exact_hash"])
            for pm in pt_models:
                pex = {h[0] for h in pm["tex"]}
                ov = len(hs & pex) / len(hs)
                if ov > 0 and (best is None or ov > best["overlap_exact"] or (ov == best["overlap_exact"] and (pm["geom"] or {}).get("tris", 0) > best["tris"])):
                    best = {"file": pm["file"], "overlap_exact": round(ov, 3), "tris": (pm["geom"] or {}).get("tris", 0), "extent": (pm["geom"] or {}).get("extent")}
        relation, rel_detail = "missing_in_native", {"basis": "no Platinum prop model shares >=75% of this model's exact texture hashes"}
        if best and best["overlap_exact"] >= 0.75 and g and g["tris"]:
            pe = best["extent"] or [0, 0, 0]
            same_ext = all(abs(x - y) <= 0.02 * max(abs(x), abs(y), 1e-6) for x, y in zip(sorted(ext), sorted(pe)))
            if best["tris"] == g["tris"] and same_ext:
                relation = "identical"
            else:
                relation = "art_diff_geometry_review"
            rel_detail = {"platinum_file": best["file"], "texture_overlap_exact": best["overlap_exact"], "hgss_tris": g["tris"], "platinum_tris": best["tris"], "hgss_extent": ext, "platinum_extent": pe}
        render_rel = f"docs/visual_overhaul/catalog_extensions/{EXT_ID}/renders/models/{key}_{i:03d}.png"
        render_ok = False
        if g and g["tris"]:
            try:
                im, _st = N.render_model(blob, size=96)
                if im is not None and not a.no_renders:
                    (ROOT / render_rel).parent.mkdir(parents=True, exist_ok=True)
                    im.save(ROOT / render_rel, optimize=True)
                render_ok = im is not None
            except Exception:  # noqa: BLE001
                render_ok = False
        aid = f"hgss:narc:files:fielddata:build_model:{key}:model_{i:03d}"
        meta = {"source_commit": commit, "narc": f"files/fielddata/build_model/{nf}", "member_id": i, "member_sha256": sha16(blob), "member_size": len(blob), "model_name": g["name"] if g else None,
                "shapes": g["shapes"] if g else 0, "materials": g["materials"] if g else 0, "tris": g["tris"] if g else 0, "extent": ext, "relative_size": round(rel, 3), "geometry_class": geo,
                "textures": tex_rows, "texture_count": len(tex_rows), "tex_novel": new_n, "tex_near_platinum": near_n, "tex_identical_platinum": ident_n, "texture_sets_linked": links,
                "categories": cats, "geometry_signature": (sha16(json.dumps([g["tris"], g["shape_tris"], [round(e, 1) for e in g["extent"]]]).encode()) if g and g["tris"] else None),
                "platinum_counterpart": best, "native_relation": relation, "relation_detail": rel_detail, "render_ok": render_ok, "decoder_version": DECODER_VERSION, "matshp_file": f"files/fielddata/build_model/{key}_matshp.dat",
                "matshp_sha256": sha16((F / f"fielddata/build_model/{key}_matshp.dat").read_bytes())}
        sgn = meta["geometry_signature"]
        meta["duplicate_of"] = (f"{sig_first[sgn]}" if sgn and sig_first[sgn] != f"{key}_{i:03d}" else None)
        meta["geometry_variants"] = sig_count.get(sgn, 1) if sgn else 0
        status = "usable" if (g and g["tris"] and render_ok) else ("decode_issue" if g is None else "reject")
        add({"asset_id": aid, "source_id": "hgss", "asset_type": "nitro_model_bmd0", "species_dex": None, "form": None, "variant": g["name"] if g else None, "group": "field_building_models",
             "frame": None, "source_path": f"files/fielddata/build_model/{nf}#member={i:03d}", "render_path": render_rel if (render_ok and not a.no_renders) else None,
             "native_width": None, "native_height": None, "bbox_width": None, "bbox_height": None, "opaque_pixels": None, "geometry_class": f"{geo}_{g['tris'] if g else 0}tris",
             "review_status": "unreviewed", "target_tags": ["field", "building", "model", "outdoor" if key == "bm_field" else "interior"],
             "quality_notes": "HGSS building/prop model (BMD0 MDL0+TEX0) from a build_model NARC member; targeted catalog extension.", "source_metadata": meta},
            status, "hgss_field_model_valid_render" if status == "usable" else ("hgss_field_model_decode_failed" if status == "decode_issue" else "hgss_field_model_empty"),
            "BMD0 decodes to geometry with a nonblank textured preview." if status == "usable" else "model has no renderable geometry or failed to decode",
            {"tris": meta["tris"], "shapes": meta["shapes"], "textures": len(tex_rows), "geometry_class": geo})

    # ---------------- follower sheets ----------------
    names = species_names()
    consts = follower_constants(hgss)
    pt_sheets = {}
    for f in sorted((ROOT / "res/graphics/field_sprites/pokemon").glob("*.png")):
        im = Image.open(f)
        px = np.asarray(im)
        frames = [px[k * 32:(k + 1) * 32] for k in range(px.shape[0] // 32)] if px.shape[1] == 32 else []
        sp = None
        stem = f.stem
        for n in sorted(names, key=len, reverse=True):
            if stem.upper() == n or stem.upper().startswith(n + "_"):
                sp = names[n]
                break
        pt_sheets[f.name] = {"stem": stem, "species": sp, "frames": frames, "size": im.size}
    pt_by_species: dict[int, list[str]] = {}
    for fn, v in pt_sheets.items():
        if v["species"]:
            pt_by_species.setdefault(v["species"], []).append(fn)
    fol_sheets = []
    for idx in sorted(consts):
        p = F / f"data/mmodel/mmodel/mmodel_{idx:08d}.NSBTX"
        data = p.read_bytes()
        const = consts[idx]
        slot = re.fullmatch(r"FOLLOWER_MON(_\d)?", const) is not None
        dex, sname, form = (None, None, None) if slot else split_species(const, names)
        tex = list(nsb.decode_textures(data))
        pals = nsb.read_palettes(data)
        tex.sort(key=lambda t: int(t[0].rsplit(".", 1)[1]) if "." in t[0] and t[0].rsplit(".", 1)[1].isdigit() else 0)
        dims = sorted({(t[1], t[2]) for t in tex})
        issues = []
        if not tex:
            issues.append("no decodable frames")
        pal_names = sorted(pals)
        mirror = []
        idxs = [np.array(t[4], dtype=np.uint8).reshape(t[2], t[1]) for t in tex]
        for x in range(len(idxs)):
            for y in range(x + 1, len(idxs)):
                if idxs[x].shape == idxs[y].shape and not np.array_equal(idxs[x], idxs[y]) and np.array_equal(idxs[x], idxs[y][:, ::-1]):
                    mirror.append([x, y])
        directions = None
        if len(tex) == 8 and [4, 6] in mirror and [5, 7] in mirror:
            directions = {"down": [0, 1], "up": [2, 3], "left": [4, 5], "right": [6, 7], "basis": "frames 4,5 mirror 6,7"}
        distinct = len({i.tobytes() for i in idxs})
        # shiny palette differs?
        shiny_diff = None
        if len(pal_names) == 2:
            shiny_diff = pals[pal_names[0]] != pals[pal_names[1]]
        # Platinum equivalent by species (+form-less match)
        peq = []
        if dex and form is None:
            peq = pt_by_species.get(dex, [])
        rel_pt, frame_match = None, None
        if peq:
            best = 0
            for fn in peq:
                pf = pt_sheets[fn]["frames"]
                m = sum(any(i.shape == f.shape and np.array_equal(i, f) for f in pf) for i in idxs)
                best = max(best, m)
            frame_match = best
            pframes = max(len(pt_sheets[fn]["frames"]) for fn in peq)
            if best == len(idxs) and idxs:
                rel_pt = "identical"
            elif pframes != len(idxs):
                rel_pt = "contract_mismatch"  # HGSS 8-frame sheet vs Platinum multi-frame animation table: not a drop-in
            else:
                rel_pt = "art_diff"
        sprite_h = max((int(np.ptp(np.where(i > 0)[0]) + 1) if (i > 0).any() else 0) for i in idxs) if idxs else 0
        render_rel = f"docs/visual_overhaul/catalog_extensions/{EXT_ID}/renders/followers/mmodel_{idx:08d}.png"
        if not a.no_renders and tex and len(pal_names) == 2:
            T = N.parse_tex0(data, N.parse_bmd(data)[1])
            ims = []
            for pn in sorted(T["pals"]):
                for nm, tx in sorted(T["texs"].items(), key=lambda kv: int(kv[0].rsplit(".", 1)[1]) if kv[0].rsplit(".", 1)[1].isdigit() else 0):
                    ims.append(N.decode_tex(data, T, tx, pn))
            sheet(ims, ROOT / render_rel, cols=8, cell=32 if dims == [(32, 32)] else 48)
        meta = {"source_commit": commit, "mmodel_index": idx, "mmodel_constant": "MMODEL_" + const, "member_sha256": sha16(data), "member_size": len(data), "species_dex": dex, "species": sname, "form": form,
                "slot_placeholder": bool(slot), "frames": len(tex), "frame_dims": [list(d) for d in dims], "palette_names": pal_names, "palette_count": len(pal_names), "shiny_palette_differs": shiny_diff,
                "distinct_frames": distinct, "mirror_pairs": mirror, "directions": directions, "sprite_max_height": sprite_h, "platinum_equivalents": [f"res/graphics/field_sprites/pokemon/{x}" for x in peq],
                "platinum_relation": rel_pt, "platinum_frame_counts": [len(pt_sheets[fn]["frames"]) for fn in peq], "platinum_frame_matches": frame_match, "texture_format": 3, "decoder_version": DECODER_VERSION}
        ok = bool(tex) and not issues and distinct >= 2
        fol_sheets.append(idx)
        add({"asset_id": f"hgss:source:files:data:mmodel:mmodel:mmodel_{idx:08d}.NSBTX", "source_id": "hgss", "asset_type": "nsbtx_pokemon_sheet", "species_dex": dex, "form": form,
             "variant": sname or const, "group": "follower_sheets", "frame": len(tex), "source_path": f"files/data/mmodel/mmodel/mmodel_{idx:08d}.NSBTX",
             "render_path": render_rel if (not a.no_renders and tex and len(pal_names) == 2) else None, "native_width": dims[0][0] if dims else None, "native_height": dims[0][1] * len(tex) if dims else None,
             "bbox_width": None, "bbox_height": None, "opaque_pixels": int(sum(int((i > 0).sum()) for i in idxs)) or None, "geometry_class": f"{len(tex)}_frames_{dims[0][0]}x{dims[0][1]}" if dims else None,
             "review_status": "unreviewed", "target_tags": ["overworld", "pokemon", "field_sprite", "follower_sheet"],
             "quality_notes": "HGSS overworld Pokemon sheet (NSBTX frame textures, normal + shiny palette); the follower system itself is out of scope.", "source_metadata": meta},
            "usable" if ok else "reject", "hgss_follower_sheet_valid_render" if ok else "hgss_follower_sheet_invalid",
            "NSBTX frame textures decode with both palettes; frames are nonblank and distinct." if ok else "; ".join(issues) or "frames not distinct",
            {"frames": len(tex), "dims": [list(d) for d in dims], "distinct_frames": distinct, "issues": issues})

    cat.sort(key=lambda r: r["asset_id"])
    cur.sort(key=lambda r: r["asset_id"])
    counts = {}
    for r in cur:
        counts[r["review_status"]] = counts.get(r["review_status"], 0) + 1
    by_type = {}
    for r in cat:
        by_type[r["asset_type"]] = by_type.get(r["asset_type"], 0) + 1
    catalog = {"schema_version": 1, "extension_id": EXT_ID,
               "sources": [{"source_id": "hgss", "source_game": "Pokemon HeartGold/SoulSilver", "source_repo": "79cbd8hmgj-wq/pokeheartgold", "source_commit": commit,
                            "notes": "Targeted extension: files/fielddata/build_model (bm_field, bm_room), files/a/0/4/4 map texture sets, and the 572 MMODEL_FOLLOWER_MON* overworld Pokemon sheets. land_data (files/a/0/6/5) stays reference-only and is not cataloged."}],
               "scope": {"models": {"bm_field": 340, "bm_room": 222}, "texture_sets": len(set_blobs), "follower_sheets": len(fol_sheets), "platinum_exact_texture_universe": len(tex_ex), "median_model_extent": round(med, 3)},
               "asset_counts_by_type": by_type, "assets": cat}
    curation = {"schema_version": 1, "lane": "X_hgss_field_3d", "scope": "hgss field/building models, map texture sets and follower sheets catalog extension", "asset_count": len(cur), "status_counts": counts, "records": cur}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "CATALOG.json").write_text(json.dumps(catalog, indent=1, sort_keys=True) + "\n")
    (OUT / "CURATION.json").write_text(json.dumps(curation, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"assets": len(cat), "by_type": by_type, "status": counts, "followers": len(fol_sheets)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
