#!/usr/bin/env python3
"""Resolve the 218 Lane A decode_issue records.

* 164 HGSS source PNGs: zero-byte files in the donor tree (gender-duplicate placeholders; every one has a
  non-empty opposite-gender sibling that is curated on its own) -> reject, no pixel data exists.
* 54 Ranger Pokemon cells whose OAM tiles are absent from their own group's character data:
  every graphics resource of the package is tried.  A cell is promoted only when at least one resource
  supplies ALL referenced tiles, the render is nonblank, and every complete candidate renders identically
  (tile source then does not matter).  Cells where candidates disagree stay decode_issue; cells whose
  tiles exist in no resource of the package are rejected as unrenderable (defect in the donor data).
No Platinum resources are modified.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import recover_lane_b_ranger_embedded as rb
import render_ranger_ncer_preview as m


def missing_refs(oams, sw, tiles):
    miss = 0
    for a0, a1, a2 in oams:
        shape = (a0 >> 14) & 3
        if shape not in m.SHAPE_SIZE:
            continue
        w, h = m.SHAPE_SIZE[shape][(a1 >> 14) & 3]
        for ty in range(h // 8):
            for tx in range(w // 8):
                row, col = divmod((a2 & 0x3FF) + ty * 32 + tx, 32)
                if col >= sw or row * sw + col >= len(tiles):
                    miss += 1
    return miss


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane-a", type=Path, required=True)
    ap.add_argument("--hgss-root", type=Path, required=True)
    ap.add_argument("--ranger-root", type=Path, required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    recs = [r for r in json.loads(a.lane_a.read_text())["records"] if r["review_status"] == "decode_issue"]
    decisions, rows = [], []
    for r in [x for x in recs if x["source_id"] == "hgss"]:
        p = a.hgss_root / r["source_path"]
        size = os.path.getsize(p)
        sib = Path(str(p).replace("/male/", "/FEMALE/").replace("/female/", "/male/").replace("/FEMALE/", "/female/"))
        sib_ok = sib.exists() and os.path.getsize(sib) > 0
        if size == 0 and sib_ok:
            decisions.append({"asset_id": r["asset_id"], "review_status": "reject", "reason_code": "zero_byte_gender_placeholder",
                              "reason": "Donor file is zero bytes (gender-duplicate placeholder): no pixel data exists. The opposite-gender sibling sprite is a real image and is curated separately.",
                              "detail": f"size=0; sibling {sib.relative_to(a.hgss_root)} is {os.path.getsize(sib)} bytes"})
        rows.append({"asset_id": r["asset_id"], "state": "zero_byte" if size == 0 else "other", "sibling_nonempty": sib_ok})
    byg = defaultdict(list)
    for r in recs:
        if r["source_id"] == "ranger2":
            g = r["group"]
            byg[g].append((r["asset_id"], int(r["asset_id"].rsplit("cell_", 1)[1])))
    R = a.ranger_root / "res/prebuilt/data/poke"
    for g, cells in sorted(byg.items()):
        stem = "_".join(g.split("_")[:2])
        with tempfile.TemporaryDirectory() as t:
            ms = rb.load_members(R / f"{stem}_LZ.bin", Path(t))
            cb = m.read_cells(ms[g + ".NCER"])
            gfx = {k: v for k, v in ms.items() if k.endswith((".NCBR", ".NCGR"))}
            for aid, ci in cells:
                complete = {}
                best_miss = 10**9
                best_px = 0
                for k, v in sorted(gfx.items()):
                    try:
                        sw, _, tiles = m.read_chars(v, cells=cb)
                    except Exception:  # noqa: BLE001
                        continue
                    miss = missing_refs(cb[ci], sw, tiles)
                    if miss < best_miss:
                        best_miss = miss
                        best_px = sum(1 for v in m.render_cell(cb[ci], sw, tiles, 32)[2] if v)
                    if miss == 0:
                        w, h, px = m.render_cell(cb[ci], sw, tiles, 32)
                        complete[k] = (w, h, tuple(px))
                distinct = {v for v in complete.values()}
                nonblank = [k for k, v in complete.items() if any(v[2])]
                if complete and len(distinct) == 1 and nonblank:
                    decisions.append({"asset_id": aid, "review_status": "usable", "reason_code": "ranger_tiles_in_sibling_resource",
                                      "reason": "Cell tiles are absent from its own group's character data but present in sibling graphics of the same package; every complete candidate renders identically and nonblank.",
                                      "detail": f"{len(complete)} complete candidate(s): {sorted(complete)}"})
                    st = "usable"
                elif complete:
                    st = "ambiguous_candidates"
                elif best_miss > 0 and best_px == 0:
                    decisions.append({"asset_id": aid, "review_status": "reject", "reason_code": "ranger_cell_tiles_absent_in_package",
                                      "reason": "Cell references character tiles that no graphics resource in its package contains and the best candidate renders fully blank; the donor data cannot render it.",
                                      "detail": f"best candidate misses {best_miss} tile reference(s) and renders 0 pixels"})
                    st = "tiles_absent_blank"
                elif best_miss > 0:
                    st = "partial_render_missing_tiles"
                rows.append({"asset_id": aid, "state": st})
    states = Counter(x["state"] for x in rows)
    dec_counts = Counter((d["review_status"], d["reason_code"]) for d in decisions)
    res = {"schema_version": 1, "scope": "lane_a_residual", "asset_count": len(rows), "state_counts": dict(states),
           "decision_counts": {f"{s}:{c}": n for (s, c), n in sorted(dec_counts.items())}, "records": rows, "decisions": decisions}
    a.write_json.write_text(json.dumps(res, indent=1) + "\n")
    md = ["# Lane A Residual Recovery", "", "Resolution of the 218 Lane A decode_issue records. No Platinum resources modified.", "",
          "| Decision | Reason | Assets |", "|---|---|---:|"] + [f"| {s} | {c} | {n} |" for (s, c), n in sorted(dec_counts.items())]
    md += ["", f"Unresolved (ambiguous tile source): **{states.get('ambiguous_candidates', 0)}**"]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(states), {f"{s}:{c}": n for (s, c), n in dec_counts.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
