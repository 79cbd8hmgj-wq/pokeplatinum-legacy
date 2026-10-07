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
    """Render a cell under 1D OBJ tile mapping (tile id advances linearly)."""
    objs = [o for o in oams if ((o[0] >> 14) & 3) in nrp.SHAPE_SIZE]
    if not objs:
        return 1, 1, [0]
    wt0 = max(nrp.SHAPE_SIZE[(o[0] >> 14) & 3][(o[1] >> 14) & 3][0] for o in objs) // 8
    # per-object linear indexing: temporarily emulate with stride == object width
    if len({nrp.SHAPE_SIZE[(o[0] >> 14) & 3][(o[1] >> 14) & 3][0] for o in objs}) == 1:
        return render_cell(oams, wt0, tiles, wt0)
    raise ValueError("mixed object widths under 1D mapping")


def load_members(pkg: Path, tmp: Path) -> dict[str, Path]:
    raw = pkg.read_bytes()
    if not raw or raw[0] != 0x10:
        raise ValueError("not LZ10")
    payload = lz10_decompress(raw)
    if payload[:4] != b"NARC":
        raise ValueError("LZ10 payload is not NARC")
    extract_narc_members(payload, tmp)
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


def evaluate_package(pkg: Path) -> dict:
    out = {"members": {}, "pairs": []}
    with tempfile.TemporaryDirectory(prefix="lbr_") as t:
        members = load_members(pkg, Path(t))
        pal_tab = {p.stem: p for n, p in members.items() if n.endswith(".NCLR")}
        gfx_tab = {p.stem: p for n, p in members.items() if n.endswith((".NCBR", ".NCGR"))}
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
        for n in members:
            if n.endswith((".NCBR", ".NCGR")) and n in used_gfx:
                out["members"][n] = {"state": "valid_render", "detail": "used by valid NCER render"}
            elif n.endswith(".NCLR") and n in used_pal:
                out["members"][n] = {"state": "valid_render", "detail": "used by valid NCER render"}
            elif n.endswith(".cac"):
                st = Path(n).stem
                if st in ok_ncer:
                    out["members"][n] = {"state": "companion_of_valid", "detail": "cell-animation companion of valid NCER"}
            elif n.endswith((".NCBR", ".NCGR", ".NCLR")):
                out["members"][n] = {"state": "no_pair", "detail": "not consumed by any valid render"}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", type=Path, required=True)
    ap.add_argument("--ranger-root", type=Path, required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    recs = json.loads(a.curation.read_text())["records"]
    todo = [r for r in recs if r["source_id"] == "ranger2" and r["review_status"] == "decode_issue"
            and "/field/map/" not in r["source_path"]]
    by_pkg: dict[str, list[dict]] = {}
    for r in todo:
        by_pkg.setdefault(r["source_path"], []).append(r)
    rows, pkg_state = [], {}
    for sp, rs in sorted(by_pkg.items()):
        try:
            ev = evaluate_package(a.ranger_root / sp)
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
    res = {"schema_version": 1, "scope": "lane_b_ranger_embedded", "asset_count": len(rows),
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
