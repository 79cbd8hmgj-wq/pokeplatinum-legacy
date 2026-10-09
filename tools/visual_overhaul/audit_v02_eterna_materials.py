#!/usr/bin/env python3
"""V02 read-only audit: Eterna Forest map_texture_set_074 vs the HGSS texture-set donors.

Reads only. Writes review PNGs + a JSON summary. Never touches res/.

Usage:
    python3 -I tools/visual_overhaul/audit_v02_eterna_materials.py --hgss /path/to/pokeheartgold

Evidence produced:
  * which of the 57 textures in map_texture_set_074 are actually bound by the nine Eterna Forest terrain
    models (map_matrix_007 -> map_data_338..346), with the real material texture<->palette pairing;
  * UV windows, world-space quad extents and flatness per bound texture;
  * donor identity checks (byte-identical texels, bijective-relabel "recolor" matches) against all 3,659
    HGSS map textures in files/a/0/4/4;
  * review sheets and the stump-decal mock-up (illustrative only, nothing is written back).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / "selection"))
import nsbmd_preview as N  # noqa: E402

SET074 = ROOT / "res/field/maps/texture_sets/map_texture_set_074.nsbtx"
SET053 = ROOT / "res/field/maps/texture_sets/map_texture_set_053.nsbtx"
MAP_DATA = ROOT / "res/field/maps/data"
ETERNA_MAPS = range(338, 347)  # map_matrix_007 (MAP_338..MAP_346)
OUT = ROOT / "docs/visual_overhaul/review"
CATALOG = ROOT / "docs/visual_overhaul/catalog_extensions/hgss_field_3d/CATALOG.json"


def narc_members(path: Path) -> list[bytes]:
    d = path.read_bytes()
    assert d[:4] == b"NARC"
    n = struct.unpack_from("<H", d, 16 + 8)[0]
    ents = [struct.unpack_from("<II", d, 16 + 12 + 8 * i) for i in range(n)]
    p = 16
    p += struct.unpack_from("<I", d, p + 4)[0]
    p += struct.unpack_from("<I", d, p + 4)[0]
    assert d[p:p + 4] == b"GMIF"
    return [d[p + 8 + a:p + 8 + b] for a, b in ents]


def raw_idx4(d: bytes, T: dict, t: dict) -> np.ndarray:
    raw = np.frombuffer(d, np.uint8, count=t["w"] * t["h"] // 2, offset=T["tex_off"] + t["off"])
    return np.stack([raw & 15, raw >> 4], 1).reshape(-1).reshape(t["h"], t["w"])


def pal_rgb555(d: bytes, T: dict, name: str, n: int = 16) -> list[int]:
    po = T["pal_data"] + T["pals"][name][0]
    return [N.u16(d, po + 2 * k) for k in range(n)]


def bound_textures() -> tuple[dict, dict]:
    """texture -> {palette: material count}, and UV/world stats per texture, from the real terrain models."""
    pairs: dict[str, Counter] = defaultdict(Counter)
    stats: dict[str, dict] = defaultdict(lambda: dict(shapes=0, tris=0, uv_min=[1e9, 1e9], uv_max=[-1e9, -1e9],
                                                      windows=Counter()))
    for i in ETERNA_MAPS:
        d = (MAP_DATA / f"map_data_{i:03d}.bin").read_bytes()
        perm, obj, model, _ = struct.unpack_from("<IIII", d, 0)
        bm = d[16 + perm + obj:16 + perm + obj + model]
        mdl, _tex = N.parse_bmd(bm)
        for mm in N.parse_models(bm, mdl):
            mat2tex = {m: tn for tn, ids in mm["texmap"].items() for m in ids}
            for tn, ids in mm["texmap"].items():
                for pn, pids in mm["palmap"].items():
                    if set(ids) & set(pids):
                        pairs[tn][pn] += 1
            for si, (_sn, dl) in enumerate(mm["shapes"]):
                tn = mat2tex.get(mm["shape_mat"].get(si))
                tris = N.parse_dl(dl, mm["scale"])
                if tn is None or not tris:
                    continue
                s = stats[tn]
                s["shapes"] += 1
                s["tris"] += len(tris)
                for t3 in tris:
                    uv = np.array([v[1] for v in t3])
                    pos = np.array([v[0] for v in t3])
                    s["uv_min"] = np.minimum(s["uv_min"], uv.min(0)).tolist()
                    s["uv_max"] = np.maximum(s["uv_max"], uv.max(0)).tolist()
                    if np.ptp(uv[:, 0]) and np.ptp(uv[:, 1]):
                        ext = pos.max(0) - pos.min(0)
                        key = (tuple(uv.min(0).round().astype(int).tolist()), tuple(uv.max(0).round().astype(int).tolist()),
                               round(float(ext[1]), 1))
                        s["windows"][key] += 1
    return pairs, stats


def decode(d: bytes, T: dict, name: str, pal: str) -> np.ndarray:
    return N.decode_tex(d, T, T["texs"][name], pal)


def sheet(items, out: Path, cols: int = 6, sc: int = 4) -> None:
    cells = []
    for lab, im in items:
        I = Image.fromarray(im).convert("RGBA")
        k = sc if I.width <= 32 else max(2, sc // 2)
        I = I.resize((I.width * k, I.height * k), Image.NEAREST)
        bg = Image.new("RGBA", (max(I.width, 120) + 8, I.height + 22), (200, 60, 200, 255))  # magenta = transparent
        bg.paste(I, (4, 18), I)
        ImageDraw.Draw(bg).text((3, 3), lab, fill=(255, 255, 255, 255))
        cells.append(bg)
    w, h = max(c.width for c in cells), max(c.height for c in cells)
    rows = (len(cells) + cols - 1) // cols
    sh = Image.new("RGB", (cols * w, rows * h), (40, 40, 40))
    for i, c in enumerate(cells):
        sh.paste(c.convert("RGB"), ((i % cols) * w, (i // cols) * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    sh.save(out)


# ---- stump-decal mock-up -------------------------------------------------------------------------------------------------------------
# Donor member 74 of files/a/0/4/4, texture d05tree01_un (32x32 fmt3, c0). role mapping donor index -> Platinum palette index.
# Browns are merged to 5 tones so the SAME mapping fits conttree_b and tree01 (tree01 canopy uses palette idx 6/7, so those stay untouched).
DONOR_TO_PT = {0: 0, 3: 14, 2: 2, 1: 3, 4: 4, 11: 13, 9: 1, 10: 11, 5: 11, 7: 12, 8: 10, 6: 10}
NEW_BROWN_SLOTS = {1: 9, 10: 6, 11: 5, 12: 7}  # pt idx -> donor idx whose colour (graded) it takes; pt idx 13 already == donor 11


def grade_ratio(pal_orig: list[int], pal_cur: list[int]) -> np.ndarray:
    """Mean per-channel cur/orig ratio over the stump-only entries (10..13) = what G7.6 did to the cream/brown ramp."""
    c = lambda v: np.array([v & 31, (v >> 5) & 31, (v >> 10) & 31], float)  # noqa: E731
    r = np.mean([c(pal_cur[i]) / c(pal_orig[i]) for i in (10, 11, 12, 13)], axis=0)
    return r


def build_mockup(d74: bytes, T74: dict, donor_idx: np.ndarray, donor_pal: list[int], ratio: np.ndarray):
    """Return (new 4bpp index map for conttree_b, new palette list, rendered RGBA) -- in memory only."""
    t = T74["texs"]["conttree_b"]
    ix = raw_idx4(d74, T74, t).copy()
    pal = pal_rgb555(d74, T74, "conttree_b")
    for ptidx, didx in NEW_BROWN_SLOTS.items():
        v = donor_pal[didx]
        rgb = np.array([v & 31, (v >> 5) & 31, (v >> 10) & 31], float) * ratio
        r, g, b = (int(round(min(31, max(0, x)))) for x in rgb)
        pal[ptidx] = r | (g << 5) | (b << 10)
    cell = np.vectorize(DONOR_TO_PT.get)(donor_idx[3:29, 2:30])  # 26 rows x 28 cols (drop the two 6px ring caps)
    ix[36:62, :] = 0
    for x0 in (2, 34):  # two stump cells, 2px side margin each (32px cell, 28px disc)
        ix[36:62, x0:x0 + 28] = cell
    rgba = np.zeros((64, 64, 4), np.uint8)
    for y in range(64):
        for x in range(64):
            v = int(ix[y, x])
            if v == 0:
                continue
            c = pal[v]
            rgba[y, x] = ((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31, 255)
    return ix, pal, rgba


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgss", type=Path, required=True, help="pokeheartgold checkout (needs files/a/0/4/4)")
    ap.add_argument("--json", type=Path, default=ROOT / "docs/visual_overhaul/implementation/v02_eterna_material_audit.json")
    args = ap.parse_args()

    d74, d53 = SET074.read_bytes(), SET053.read_bytes()
    T74, T53 = N.parse_tex0(d74, N.u32(d74, 16)), N.parse_tex0(d53, N.u32(d53, 16))
    pairs, stats = bound_textures()
    bound = {tn: next(iter(p)) for tn, p in pairs.items()}
    print(f"{len(T74['texs'])} textures in set 074; {len(bound)} bound by Eterna terrain models")

    members = narc_members(args.hgss / "files/a/0/4/4")
    cat = {}
    for a in json.loads(CATALOG.read_text())["assets"]:
        if a["asset_type"] == "nitro_map_texture":
            m = a["source_metadata"]
            cat[(m["set_index"], m["texture_index"])] = m
    donors = []
    for si, f in enumerate(members):
        T = N.parse_tex0(f, N.u32(f, 16))
        for n, t in T["texs"].items():
            m = cat[(si, t["idx"])]
            pal = m["palette_name"] or next((c for c in (n, n + "_pl", n + "_p") if c in T["pals"]), None)  # catalog gap -> name match
            if pal is None and len(T["pal_order"]) == len(T["texs"]):
                pal = T["pal_order"][t["idx"]]  # last resort: positional pairing (only when counts match)
            donors.append(dict(set=si, name=n, w=t["w"], h=t["h"], fmt=t["fmt"], c0=t["c0"], pal=pal, idx=t["idx"],
                               rgba=N.decode_tex(f, T, t, pal) if pal else None, data=f, T=T, t=t))
    print(len(donors), "HGSS map textures decoded")

    def hg(setno, name):
        return next(x for x in donors if x["set"] == setno and x["name"] == name)

    # identity checks ------------------------------------------------------------------------------------------------------------------
    def texbytes(d, T, t):
        bits = {1: 8, 2: 2, 3: 4, 4: 8, 6: 8}.get(t["fmt"])
        return None if bits is None else d[T["tex_off"] + t["off"]:T["tex_off"] + t["off"] + t["w"] * t["h"] * bits // 8]

    def canon(d, T, t):
        b = texbytes(d, T, t)
        if b is None or t["fmt"] not in (2, 3, 4):
            return None
        raw = np.frombuffer(b, np.uint8)
        idx = {3: lambda: np.stack([raw & 15, raw >> 4], 1).reshape(-1),
               2: lambda: np.stack([(raw >> (2 * k)) & 3 for k in range(4)], 1).reshape(-1),
               4: lambda: raw}[t["fmt"]]()
        m, out = {}, []
        for v in idx.tolist():
            out.append(m.setdefault(v, len(m)))
        return hashlib.md5(bytes(out)).hexdigest()

    exact, recolor = defaultdict(set), defaultdict(set)
    ptex = {n: t for n, t in T74["texs"].items() if n in bound}
    pex = {(t["w"], t["h"], t["fmt"], hashlib.md5(texbytes(d74, T74, t) or b"").hexdigest()): n for n, t in ptex.items()}
    pcn = {(t["w"], t["h"], t["fmt"], canon(d74, T74, t)): n for n, t in ptex.items() if canon(d74, T74, t)}
    for x in donors:
        b = texbytes(x["data"], x["T"], x["t"])
        if b:
            k = (x["w"], x["h"], x["fmt"], hashlib.md5(b).hexdigest())
            if k in pex:
                exact[pex[k]].add(x["name"])
        c = canon(x["data"], x["T"], x["t"])
        if c and (x["w"], x["h"], x["fmt"], c) in pcn:
            recolor[pcn[(x["w"], x["h"], x["fmt"], c)]].add(x["name"])

    summary = dict(source=dict(set="map_texture_set_074", area_data="area_data_075", lighting="lighting_set_010",
                               hgss_commit=cat[(0, 0)]["source_commit"]), bound=[], identity=dict(
        byte_identical={k: sorted(v) for k, v in exact.items()}, same_texels_other_palette={k: sorted(v) for k, v in recolor.items()}))
    for n, t in sorted(ptex.items(), key=lambda kv: kv[1]["idx"]):
        s = stats[n]
        summary["bound"].append(dict(name=n, index=t["idx"], w=t["w"], h=t["h"], fmt=t["fmt"], c0=t["c0"], palette=bound[n],
                                     pal_pairs=dict(pairs[n]), shapes=s["shapes"], tris=s["tris"],
                                     uv_min=s["uv_min"], uv_max=s["uv_max"],
                                     windows=[dict(uv_min=list(k[0]), uv_max=list(k[1]), world_height=k[2], tris=c)
                                              for k, c in s["windows"].most_common(8)]))

    # sheets ---------------------------------------------------------------------------------------------------------------------------
    cur = [(n, decode(d74, T74, n, bound[n])) for n in ptex]
    sheet(cur, OUT / "v02_eterna_bound_textures.png", cols=5, sc=3)
    pt = lambda n: decode(d74, T74, n, bound[n])  # noqa: E731
    p0 = lambda n: decode(d53, T53, n, bound[n])  # noqa: E731
    sheet([("PT 053 tree01", p0("tree01")), ("PT 074 tree01", pt("tree01")), ("PT 053 conttree_b", p0("conttree_b")),
           ("PT 074 conttree_b", pt("conttree_b")), ("PT 074 conttree_t", pt("conttree_t")),
           ("HG s74 d05tree01", hg(74, "d05tree01")["rgba"]), ("HG s74 d05tree01_re", hg(74, "d05tree01_re")["rgba"]),
           ("HG s10 tree01_re", hg(10, "tree01_re")["rgba"]), ("HG s93 conttree3_2", hg(93, "conttree3_2")["rgba"]),
           ("HG s92 bf_tree03", hg(92, "bf_tree03")["rgba"]), ("HG s74 ubmf_r01", hg(74, "ubmf_r01")["rgba"])],
          OUT / "v02_canopy_compare.png", cols=4)
    sheet([("PT 053 criffp", p0("criffp")), ("PT 074 criffp", pt("criffp")), ("PT 053 criffp2", p0("criffp2")),
           ("PT 074 criffp2", pt("criffp2")), ("PT 074 criff", pt("criff")), ("HG s85 gsm_dcliff01", hg(85, "gsm_dcliff01")["rgba"]),
           ("HG s2 wall01_d", hg(2, "wall01_d")["rgba"]), ("HG s2 wall01_g", hg(2, "wall01_g")["rgba"]),
           ("HG s3 wall01_h", hg(3, "wall01_h")["rgba"]), ("HG s29 g02pond", hg(29, "g02pond")["rgba"]),
           ("HG s74 d05pond_line", hg(74, "d05pond_line")["rgba"]), ("HG s0 cliff01gs", hg(0, "cliff01gs")["rgba"])],
          OUT / "v02_cliff_rock_compare.png", cols=4)
    sheet([("PT 074 nectgr", pt("nectgr")), ("PT 074 ngrass", pt("ngrass")), ("PT 074 rhana", pt("rhana")),
           ("PT 074 fenter", pt("fenter")), ("PT 074 tshadow", pt("tshadow")), ("PT 074 nsandp", pt("nsandp")),
           ("HG s74 flower01", hg(74, "flower01")["rgba"]), ("HG s2 egrass", hg(2, "egrass")["rgba"]),
           ("HG s74 grass01_a", hg(74, "grass01_a")["rgba"]), ("HG s29 g02kusa_a", hg(29, "g02kusa_a")["rgba"]),
           ("HG s92 bf_ngrass", hg(92, "bf_ngrass")["rgba"]), ("HG s2 grass02_r", hg(2, "grass02_r")["rgba"]),
           ("HG s74 road01_r", hg(74, "road01_r")["rgba"])], OUT / "v02_ground_underbrush_compare.png", cols=5, sc=5)

    # palette-slot ownership: the slots the recipe rewrites (1, 10-13) must be used ONLY inside the stump windows
    own = {}
    for tn, win in (("conttree_b", (slice(36, 62), slice(0, 64))), ("tree01", (slice(0, 28), slice(34, 64)))):
        ixp = raw_idx4(d74, T74, T74["texs"][tn])
        mask = np.isin(ixp, [1, 10, 11, 12, 13])
        inside = np.zeros_like(mask)
        inside[win] = True
        own[tn] = dict(px_using_rewritten_slots=int(mask.sum()), outside_stump_window=int((mask & ~inside).sum()),
                       palette_users=sorted(k for k, v in pairs.items() if tn in v or bound.get(k) == tn),
                       palette_file_offset=hex(T74["pal_data"] + T74["pals"][bound[tn]][0]),
                       palette_block_aliases=sorted(n for n, (o, _) in T74["pals"].items() if o == T74["pals"][bound[tn]][0]))
        assert own[tn]["outside_stump_window"] == 0, tn
    summary["slot_ownership"] = own

    # stump mock-up --------------------------------------------------------------------------------------------------------------------
    dn = hg(74, "d05tree01_un")
    dix = raw_idx4(dn["data"], dn["T"], dn["t"])
    dpal = pal_rgb555(dn["data"], dn["T"], dn["pal"])
    ratio = grade_ratio(pal_rgb555(d53, T53, "conttree_b"), pal_rgb555(d74, T74, "conttree_b"))
    new_ix, new_pal, mock = build_mockup(d74, T74, dix, dpal, ratio)
    assert set(np.unique(dix).tolist()) - {0} <= set(DONOR_TO_PT), "unmapped donor index"
    assert new_ix.max() <= 15
    band = lambda im: im[36:62, :]  # noqa: E731
    sheet([("PT 053 stump band", band(p0("conttree_b"))), ("PT 074 (current)", band(pt("conttree_b"))),
           ("MOCK-UP recipe (not applied)", band(mock)), ("HG s74 d05tree01_un", dn["rgba"]),
           ("HG s2 tree01_un", hg(2, "tree01_un")["rgba"]), ("HG s93 conttree3_2 (lower)", hg(93, "conttree3_2")["rgba"][36:64])],
          OUT / "v02_stump_decal_candidate.png", cols=2, sc=6)
    summary["mockup"] = dict(grade_ratio_rgb=[round(float(x), 3) for x in ratio],
                             new_palette_entries={str(k): f"{new_pal[k]:04x}" for k in NEW_BROWN_SLOTS},
                             index_range=[int(new_ix.min()), int(new_ix.max())],
                             opaque_px_before=int((pt("conttree_b")[36:62, :, 3] > 0).sum()),
                             opaque_px_after=int((mock[36:62, :, 3] > 0).sum()))
    args.json.write_text(json.dumps(summary, indent=1, default=int) + "\n")
    print("wrote", args.json.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
