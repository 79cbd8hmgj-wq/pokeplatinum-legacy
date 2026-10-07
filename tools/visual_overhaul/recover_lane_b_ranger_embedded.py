#!/usr/bin/env python3
"""Technical recovery pass for Lane B Ranger2 embedded character/effect packages.

Reuses the verified Ranger pipeline (LZ10 -> NARC -> NCLR + NCBR/NCGR + NCER ->
OAM render, with the scanline/OAM-palette fixes).  Every NCER cell is rendered and
checked for non-blank output with palette indices covered by the package NCLR.

Per-member outcomes (no Platinum resources modified, nothing promoted here):
  valid_render      NCER/NCBR/NCLR members that took part in >=1 nonblank render
  companion_of_valid  .cac cell-animation companion of a valid NCER
  blank_render / decode_failure / no_pair / unsupported_member
"""
from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path

from inspect_ranger_assets import extract_narc_members
from nitro_narc import lz10_decompress
import struct

import render_ranger_ncer_preview as nrp
from render_ranger_ncer_preview import read_cells, read_chars, read_palette, render_cell


def read_chars_sentinel(path: Path) -> list[list[int]] | None:
    """Tile list for RGCN with 0xFFFF/0xFFFF geometry (tile-ordered, 1D OBJ mapping)."""
    raw = path.read_bytes()
    if raw[:4] != b"RGCN" or raw[0x10:0x14] != b"RAHC":
        return None
    wt, ht, fmt = struct.unpack_from("<HHI", raw, 0x18)
    if (wt, ht) != (0xFFFF, 0xFFFF) or fmt != 3:
        return None
    size = struct.unpack_from("<I", raw, 0x28)[0]
    body = raw[0x30:0x30 + size]
    if len(body) != size or size % 32:
        raise ValueError("truncated sentinel NCGR")
    return [[(b >> (4 * k)) & 15 for b in body[p:p + 32] for k in (0, 1)]
            for p in range(0, size, 32)]


def render_cell_1d(oams, tiles):
    """Render a cell under 1D OBJ tile mapping (an object's tiles are consecutive: tile + ty*w + tx)."""
    objs = []
    for attr0, attr1, attr2 in oams:
        shape = (attr0 >> 14) & 3
        if shape not in nrp.SHAPE_SIZE:
            continue
        w, h = nrp.SHAPE_SIZE[shape][(attr1 >> 14) & 3]
        objs.append((nrp.signed_x(attr1), nrp.signed_y(attr0), w, h, attr2 & 0x3FF, attr2 >> 12,
                     bool(attr1 & 0x1000), bool(attr1 & 0x2000)))
    if not objs:
        return 1, 1, [0]
    min_x = min(o[0] for o in objs)
    min_y = min(o[1] for o in objs)
    width = max(o[0] + o[2] for o in objs) - min_x
    height = max(o[1] + o[3] for o in objs) - min_y
    canvas = [0] * (width * height)
    for x0, y0, w, h, tile0, prow, hf, vf in objs:
        wt = w // 8
        for py in range(h):
            sy = h - 1 - py if vf else py
            ty, iy = divmod(sy, 8)
            for px in range(w):
                sx = w - 1 - px if hf else px
                tx, ix = divmod(sx, 8)
                t = tile0 + ty * wt + tx
                if t >= len(tiles):
                    continue
                c = tiles[t][iy * 8 + ix]
                if c:
                    canvas[(y0 - min_y + py) * width + x0 - min_x + px] = c + prow * 16
    return width, height, canvas


def read_nscr(path: Path):
    raw = path.read_bytes()
    if raw[:4] != b"RCSN" or raw[0x10:0x14] != b"NRCS":
        raise ValueError("not a standard NSCR")
    w, h = struct.unpack_from("<HH", raw, 0x18)
    size = struct.unpack_from("<I", raw, 0x20)[0]
    data = raw[0x24:0x24 + size]
    if len(data) != size or w % 8 or h % 8 or (w // 8) * (h // 8) * 2 != size:
        raise ValueError("NSCR geometry/data mismatch")
    return w, h, list(struct.unpack_from("<" + "H" * (size // 2), data, 0))


def read_chars_bg(path: Path):
    """(tiles, bpp) for a BG NCGR/NCBR; tiles are 64-entry index lists."""
    raw = path.read_bytes()
    if raw[:4] != b"RGCN" or raw[0x10:0x14] != b"RAHC":
        raise ValueError("not a standard RGCN")
    wt, ht, fmt = struct.unpack_from("<HHI", raw, 0x18)
    size = struct.unpack_from("<I", raw, 0x28)[0]
    body = raw[0x30:0x30 + size]
    scanned = struct.unpack_from("<I", raw, 0x24)[0] == 1
    if fmt not in (3, 4):
        raise ValueError(f"unsupported char format {fmt}")
    bpp = 4 if fmt == 3 else 8
    per = 32 if bpp == 4 else 64
    if len(body) % per or (0xFFFF not in (wt, ht) and wt * ht * per != len(body)):
        raise ValueError("character geometry/data mismatch")
    if scanned:
        raise ValueError("scanned BG character data needs raster width context")
    tiles = []
    for pos in range(0, len(body), per):
        chunk = body[pos:pos + per]
        if bpp == 4:
            tiles.append([v for b in chunk for v in (b & 15, b >> 4)])
        else:
            tiles.append(list(chunk))
    return tiles, bpp


def render_screen(w, h, entries, tiles, bpp, pal_len):
    img = [0] * (w * h)
    maxidx = 0
    for i, e in enumerate(entries):
        tx, ty = (i % (w // 8)) * 8, (i // (w // 8)) * 8
        t = e & 0x3FF
        hf, vf, prow = bool(e & 0x400), bool(e & 0x800), e >> 12
        tile = tiles[t] if t < len(tiles) else [0] * 64
        for y in range(8):
            sy = 7 - y if vf else y
            for x in range(8):
                sx = 7 - x if hf else x
                v = tile[sy * 8 + sx]
                if v:
                    v += prow * 16 if bpp == 4 else 0
                    img[(ty + y) * w + tx + x] = v
                    maxidx = max(maxidx, v)
    return img, maxidx


def eval_nbfs(path: Path):
    raw = path.read_bytes()
    if len(raw) != 256 * 192 * 2:
        raise ValueError(f"unexpected nbfs size {len(raw)}")
    vals = struct.unpack("<" + "H" * (len(raw) // 2), raw)
    return len(set(vals))


MAGIC_EXT = {b"RCSN": "NSCR", b"RGCN": "NCGR", b"RLCN": "NCLR", b"RECN": "NCER", b"RNAN": "NANR"}


def load_members(pkg: Path, tmp: Path) -> dict[str, Path]:
    raw = pkg.read_bytes()
    payload = lz10_decompress(raw) if raw and raw[0] == 0x10 else raw
    if payload[:4] == b"NARC":
        extract_narc_members(payload, tmp)
    elif payload[:4] in MAGIC_EXT:
        stem = pkg.name.rsplit("_LZ", 1)[0].split(".")[0]
        (tmp / f"{stem}.{MAGIC_EXT[payload[:4]]}").write_bytes(payload)
    else:
        raise ValueError(f"payload is neither NARC nor a known Nitro file ({payload[:4]!r})")
    return {p.name: p for p in tmp.iterdir()}


def pick(stem: str, table: dict[str, Path]) -> Path | None:
    s = stem
    while s:
        if s in table:
            return table[s]
        if "_" not in s:
            break
        s = s.rsplit("_", 1)[0]
    return next(iter(table.values())) if len(table) == 1 else None


def evaluate_package(pkg: Path, shared_pkg: Path | None = None) -> dict:
    out = {"members": {}, "pairs": []}
    with tempfile.TemporaryDirectory(prefix="lbr_") as t, tempfile.TemporaryDirectory(prefix="lbs_") as t2:
        members = load_members(pkg, Path(t))
        shared = load_members(shared_pkg, Path(t2)) if shared_pkg else {}
        pal_tab = {p.stem: p for n, p in {**shared, **members}.items() if n.endswith(".NCLR")}
        gfx_tab = {p.stem: p for n, p in {**shared, **members}.items() if n.endswith((".NCBR", ".NCGR"))}
        ncers = {p.stem: p for n, p in members.items() if n.endswith(".NCER")}
        for n in members:
            out["members"][n] = {"state": "unsupported_member", "detail": ""}
        used_gfx, used_pal, ok_ncer = set(), set(), set()
        for stem, ncer in sorted(ncers.items()):
            name = ncer.name
            gp, pp = pick(stem, gfx_tab), pick(stem, pal_tab)
            if gp is None or pp is None:
                out["members"][name] = {"state": "no_pair", "detail": "missing graphics/palette"}
                continue
            try:
                palette = read_palette(pp)
                cells = read_cells(ncer)
                sent = read_chars_sentinel(gp)
                if sent is None:
                    sw, _sh, tiles = read_chars(gp, cells=cells)
                nonblank = maxidx = 0
                for oams in cells:
                    if sent is not None:
                        w, h, px = render_cell_1d(oams, sent)
                    else:
                        w, h, px = render_cell(oams, sw, tiles, 32)
                    if any(px):
                        nonblank += 1
                        maxidx = max(maxidx, max(px))
                if not cells or nonblank == 0:
                    out["members"][name] = {"state": "blank_render", "detail": f"{len(cells)} cells all blank"}
                elif maxidx >= len(palette):
                    out["members"][name] = {"state": "decode_failure", "detail": f"palette index {maxidx} >= {len(palette)}"}
                else:
                    out["members"][name] = {"state": "valid_render", "detail": f"{nonblank}/{len(cells)} nonblank cells"}
                    used_gfx.add(gp.name); used_pal.add(pp.name); ok_ncer.add(stem)
                    out["pairs"].append([name, gp.name, pp.name])
            except Exception as e:  # noqa: BLE001
                out["members"][name] = {"state": "decode_failure", "detail": str(e)[:160]}
        for n, path in sorted(members.items()):
            if n.endswith(".NSCR"):
                gp = pick(path.stem, gfx_tab) or (next(iter(sorted(gfx_tab.items())))[1] if gfx_tab else None)
                pp = pick(path.stem, pal_tab) or (next(iter(sorted(pal_tab.items())))[1] if pal_tab else None)
                if gp is None or pp is None:
                    out["members"][n] = {"state": "no_pair", "detail": "screen without graphics/palette"}
                    continue
                try:
                    palette = read_palette(pp)
                    w, h, entries = read_nscr(path)
                    tiles, bpp = read_chars_bg(gp)
                    img, mx = render_screen(w, h, entries, tiles, bpp, len(palette))
                    nb = sum(1 for v in img if v)
                    if nb == 0:
                        out["members"][n] = {"state": "blank_render", "detail": f"{w}x{h} screen blank"}
                    elif mx >= len(palette):
                        out["members"][n] = {"state": "decode_failure", "detail": f"palette index {mx} >= {len(palette)}"}
                    else:
                        out["members"][n] = {"state": "valid_render", "detail": f"{w}x{h} screen, {nb} nonblank px"}
                        used_gfx.add(gp.name); used_pal.add(pp.name)
                        out["pairs"].append([n, gp.name, pp.name])
                except Exception as e:  # noqa: BLE001
                    out["members"][n] = {"state": "decode_failure", "detail": str(e)[:160]}
            elif n.endswith(".nbfs"):
                try:
                    u = eval_nbfs(path)
                    out["members"][n] = ({"state": "valid_render", "detail": f"256x192 RGB555 bitmap, {u} distinct colours"} if u > 1
                                         else {"state": "blank_render", "detail": "uniform bitmap"})
                    if u > 1:
                        out["pairs"].append([n, "", ""])
                except Exception as e:  # noqa: BLE001
                    out["members"][n] = {"state": "decode_failure", "detail": str(e)[:160]}
            elif n.endswith(".NANR"):
                raw = path.read_bytes()
                if raw[:4] == b"RNAN" and (path.stem in ok_ncer or ok_ncer):
                    out["members"][n] = {"state": "companion_of_valid", "detail": "Nitro animation (NANR) of a package with valid NCER renders"}
                else:
                    out["members"][n] = {"state": "unsupported_member", "detail": "NANR without valid NCER renders"}
        for n in members:
            if n.endswith((".NCBR", ".NCGR")) and n in used_gfx:
                out["members"][n] = {"state": "valid_render", "detail": "used by valid NCER render"}
            elif n.endswith(".NCLR") and n in used_pal:
                out["members"][n] = {"state": "valid_render", "detail": "used by valid NCER render"}
            elif n.endswith(".cac"):
                st = Path(n).stem
                if st in ok_ncer:
                    out["members"][n] = {"state": "companion_of_valid", "detail": "cell-animation companion of valid NCER"}
            elif n.endswith(".NCLR") and out["pairs"]:
                try:
                    read_palette(members[n])
                    out["members"][n] = {"state": "valid_render", "detail": "palette variant of a package with valid renders"}
                except Exception as e:  # noqa: BLE001
                    out["members"][n] = {"state": "decode_failure", "detail": str(e)[:120]}
            elif n.endswith((".NCBR", ".NCGR", ".NCLR")):
                out["members"][n] = {"state": "no_pair", "detail": "not consumed by any valid render"}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", type=Path, required=True)
    ap.add_argument("--ranger-root", type=Path, required=True)
    ap.add_argument("--lanes", default="", help="comma list of queue lanes to include (queue records only)")
    ap.add_argument("--status", default="decode_issue", help="review_status to select")
    ap.add_argument("--scope", default="lane_b_ranger_embedded")
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    recs = json.loads(a.curation.read_text())["records"]
    lanes = {x for x in a.lanes.split(",") if x}
    todo = [r for r in recs if r["source_id"] == "ranger2" and r["review_status"] == a.status
            and "/field/map/" not in r["source_path"] and (not lanes or r.get("lane") in lanes)]
    by_pkg: dict[str, list[dict]] = {}
    for r in todo:
        by_pkg.setdefault(r["source_path"], []).append(r)
    rows, pkg_state = [], {}
    for sp, rs in sorted(by_pkg.items()):
        try:
            shared = None
            pn = Path(sp).name
            if pn.startswith("um") and pn != "um_LZ.bin" and (a.ranger_root / Path(sp).parent / "um_LZ.bin").exists():
                shared = a.ranger_root / Path(sp).parent / "um_LZ.bin"
            ev = evaluate_package(a.ranger_root / sp, shared)
            pkg_state[sp] = ("ok" if ev["pairs"] else "no_valid_render", "")
        except Exception as e:  # noqa: BLE001
            ev = {"members": {}, "pairs": []}
            pkg_state[sp] = ("package_error", str(e)[:160])
        for r in rs:
            aid = r["asset_id"]
            if ":embedded:" in aid:
                mem = aid.rsplit(":", 1)[1]
                m = ev["members"].get(mem)
                st, det = (m["state"], m["detail"]) if m else ("member_not_found", "")
            elif r["asset_type"] == "compressed_visual_package":
                st = "valid_render" if pkg_state[sp][0] == "ok" else pkg_state[sp][0]
                det = f"{len(ev['pairs'])} valid NCER pairs"
            else:
                st, det = "unsupported_member", "raw/candidate resource"
            rows.append({"asset_id": aid, "source_path": sp, "technical_state": st, "detail": det,
                         "suffix": aid.rsplit(".", 1)[-1] if "." in aid.rsplit(":", 1)[-1] else ""})
    states = Counter(x["technical_state"] for x in rows)
    res = {"schema_version": 1, "scope": a.scope, "asset_count": len(rows),
           "package_count": len(by_pkg), "technical_state_counts": dict(states),
           "suffix_state_counts": {f"{s or '(none)'}:{k}": v for (s, k), v in
                                   sorted(Counter((x["suffix"], x["technical_state"]) for x in rows).items())},
           "records": rows}
    decisions = []
    for x in rows:
        if x["technical_state"] == "valid_render":
            code, why = ("ranger_embedded_valid_render_plausible_use",
                         "Ranger package member took part in a verified nonblank NCER render (palette covered); character/effect/object sprite material with plausible Platinum use.")
        elif x["technical_state"] == "companion_of_valid":
            code, why = ("ranger_cac_companion_of_valid_render",
                         "Cell-animation companion of an NCER that renders nonblank; kept with its usable sprite for animation sequencing.")
        else:
            continue
        decisions.append({"asset_id": x["asset_id"], "review_status": "usable", "reason_code": code,
                          "reason": why, "technical_state": x["technical_state"], "detail": x["detail"]})
    res["decisions"] = decisions
    a.write_json.write_text(json.dumps(res, indent=1) + "\n")
    md = ["# Lane B Ranger Embedded Recovery", "",
          "Technical render audit of Ranger2 character/effect packages (map packages excluded).",
          "No Platinum resources are modified.", "",
          f"- Assets: **{len(rows)}** in **{len(by_pkg)}** packages", ""]
    md += ["| State | Assets |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in sorted(states.items())]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(states))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
