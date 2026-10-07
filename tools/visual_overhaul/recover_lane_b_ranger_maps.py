#!/usr/bin/env python3
"""Technical recovery for Ranger2 field-map resources (res/prebuilt/data/field/map).

Facts established from the corpus (441 maps):
  *.map.tex.lz : LZ10 -> 'TEX\\0' + NARC of NARCs; every inner NARC is one texture chip =
                 RGCN (fmt 3, scan=1) + RLCN (256 colours).  The RGCN header tile geometry is
                 4bpp-equivalent: pixels are an 8bpp scanline raster of width wt*4, height ht*8
                 (verified visually: coherent map art; index 0 is the colour key).
  *.map.dat.lz : LZ10 -> NARC with members  MPIF (map header), TXIF (chip table), LYR (layer
                 data, NARC-in-NARC), CTA / PLA (small structured tables).
Outcomes:
  tex package + chips  -> valid_render when every chip decodes nonblank with full palette coverage
  dat MPIF/TXIF/CTA/PLA -> non-visual structured tables (parsed; no pixel payload): reject
  dat LYR / dat package -> remain decode_issue until layers are composed against the chips
No Platinum resources are modified.
"""
from __future__ import annotations

import argparse
import json
import struct
from collections import Counter
from pathlib import Path

from nitro_narc import lz10_decompress

TABLE_MAGICS = {b"MPIF": "map header (dimensions/chip size)", b"TXIF": "chip index table",
                b"CTA\x00": "attribute table", b"PLA\x00": "placement table"}


def narc_members(b: bytes) -> list[bytes]:
    if b[:4] != b"NARC":
        raise ValueError("not NARC")
    pos = struct.unpack_from("<H", b, 0xC)[0]
    fat = struct.unpack_from("<I", b, pos + 4)[0]
    cnt = struct.unpack_from("<I", b, pos + 8)[0]
    ent = [struct.unpack_from("<II", b, pos + 12 + i * 8) for i in range(cnt)]
    fnt = pos + fat
    base = fnt + struct.unpack_from("<I", b, fnt + 4)[0] + 8
    return [b[base + s:base + e] for s, e in ent]


def decode_chip(inner: list[bytes]) -> tuple[int, int, int]:
    gfx = next((m for m in inner if m[:4] == b"RGCN"), None)
    pal = next((m for m in inner if m[:4] == b"RLCN"), None)
    if gfx is None or pal is None:
        raise ValueError("chip lacks RGCN/RLCN")
    wt, ht, fmt = struct.unpack_from("<HHI", gfx, 0x18)
    scan = struct.unpack_from("<I", gfx, 0x24)[0]
    size = struct.unpack_from("<I", gfx, 0x28)[0]
    body = gfx[0x30:0x30 + size]
    if fmt != 3 or scan != 1 or len(body) != size or wt * ht * 32 != size:
        raise ValueError("chip geometry/format differs from the verified scanline layout")
    ncol = struct.unpack_from("<I", pal, 0x20)[0] // 2
    if ncol < 256 or max(body) >= ncol:
        raise ValueError("palette does not cover chip indices")
    nonkey = sum(1 for v in body if v)
    if nonkey == 0:
        raise ValueError("blank chip")
    return wt * 4, ht * 8, nonkey


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", type=Path, required=True)
    ap.add_argument("--ranger-root", type=Path, required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    recs = [r for r in json.loads(a.curation.read_text())["records"]
            if r["source_id"] == "ranger2" and r["review_status"] == "decode_issue" and "/field/map/" in r["source_path"]]
    pkg_eval: dict[str, dict] = {}
    for sp in sorted({r["source_path"] for r in recs}):
        p = a.ranger_root / sp
        ev: dict = {"kind": "other"}
        try:
            raw = lz10_decompress(p.read_bytes())
            if sp.endswith(".map.tex.lz") and raw[:4] == b"TEX\x00":
                chips, bad = [], []
                for o in narc_members(raw[4:]):
                    try:
                        chips.append(decode_chip(narc_members(o)))
                    except Exception as e:  # noqa: BLE001
                        bad.append(str(e)[:80])
                ev = {"kind": "tex", "chips": len(chips), "bad": bad, "sizes": sorted({(w, h) for w, h, _ in chips})[:6]}
            elif sp.endswith(".map.dat.lz") and raw[:4] == b"NARC":
                ev = {"kind": "dat", "members": [m[:4] for m in narc_members(raw)], "sizes": [len(m) for m in narc_members(raw)]}
            else:
                ev = {"kind": "unknown", "magic": raw[:4].hex()}
        except Exception as e:  # noqa: BLE001
            ev = {"kind": "error", "error": str(e)[:100]}
        pkg_eval[sp] = ev
    rows = []
    for r in recs:
        ev = pkg_eval[r["source_path"]]
        aid = r["asset_id"]
        st, det = "unresolved", ""
        if ev["kind"] == "tex" and r["asset_type"] == "compressed_visual_package":
            if ev["chips"] and not ev["bad"]:
                st, det = "valid_render", f"{ev['chips']} texture chips decode nonblank (8bpp scanline, 256-colour palette); sizes {ev['sizes']}"
            else:
                st, det = "decode_failure", f"{ev['chips']} ok chips; bad: {ev['bad'][:2]}"
        elif ev["kind"] == "dat" and ":embedded:" in aid:
            idx = int(aid.rsplit("member_", 1)[1])
            mg = ev["members"][idx]
            if mg in TABLE_MAGICS:
                st, det = "non_visual_table", f"{mg!r} {TABLE_MAGICS[mg]}, {ev['sizes'][idx]} bytes, no pixel payload"
            elif mg == b"LYR\x00":
                st, det = "layers_not_composed", "layer data needs composition against the chips"
        elif ev["kind"] == "dat":
            st, det = "layers_not_composed", "package holds layer data not yet composed"
        rows.append({"asset_id": aid, "source_path": r["source_path"], "technical_state": st, "detail": det})
    decisions = []
    for x in rows:
        if x["technical_state"] == "valid_render":
            decisions.append({"asset_id": x["asset_id"], "review_status": "usable", "reason_code": "ranger_map_chips_valid_render",
                              "reason": "Ranger field-map texture package: every chip decodes (verified 8bpp scanline layout) to nonblank map art with full palette coverage; environment/field texture material.",
                              "technical_state": x["technical_state"], "detail": x["detail"]})
        elif x["technical_state"] == "non_visual_table":
            decisions.append({"asset_id": x["asset_id"], "review_status": "reject", "reason_code": "ranger_map_structured_table",
                              "reason": "Ranger field-map header/index/attribute table: parsed structured data with no pixel payload, not standalone visual art.",
                              "technical_state": x["technical_state"], "detail": x["detail"]})
    states = Counter(x["technical_state"] for x in rows)
    res = {"schema_version": 1, "scope": "lane_b_ranger_maps", "asset_count": len(rows), "technical_state_counts": dict(states),
           "records": rows, "decisions": decisions}
    a.write_json.write_text(json.dumps(res, indent=1) + "\n")
    md = ["# Lane B Ranger Field-Map Recovery", "", "Texture-chip decode and structured-table classification. No Platinum resources modified.", "",
          "| State | Assets |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in sorted(states.items())]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(states))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
