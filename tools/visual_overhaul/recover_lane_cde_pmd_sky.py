#!/usr/bin/env python3
"""Technical recovery for PMD Sky records in review-queue lanes C/D/E.

Reference decoder: skytemple-files.  Families handled:
  MAP_BG  bma+bpc+bpl (+bpa)  -> composed static map background (BPA = animated-tile companion)
  BGP     full-screen background image
  WAN / WTE                   -> same evaluation as the Lane B PMD pass
  CHR+PAL FONT frame tiles    -> tile strip rendered with its same-stem palette
Other FONT/SYSTEM data files are left unresolved here (reported, not rejected).
No Platinum resources are modified.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from recover_lane_b_pmd_sky import eval_wan, eval_wte


def nonblank(im) -> bool:
    im = im.convert("RGBA")
    return im.getchannel("A").getbbox() is not None and len(set(im.convert("RGB").resize((64, 64)).getdata())) > 1


def render_bg(stem: str, files: dict[str, Path], bpa_paths: list[Path] | None = None):
    from skytemple_files.graphics.bma.handler import BmaHandler
    from skytemple_files.graphics.bpc.handler import BpcHandler
    from skytemple_files.graphics.bpl.handler import BplHandler
    bma = BmaHandler.deserialize(files["bma"].read_bytes())
    bpc = BpcHandler.deserialize(files["bpc"].read_bytes(), bma.tiling_width, bma.tiling_height)
    bpl = BplHandler.deserialize(files["bpl"].read_bytes())
    try:
        return bma.to_pil(bpc, bpl, [None] * 8, False, False, False, True)[0]
    except AssertionError:
        pass
    # The map references animated tiles: supply its same-stem BPA(s).  Slot order is held in
    # bg_list.dat (not consulted here); try each slot position until the BMA/BPC accept it.
    from skytemple_files.graphics.bpa.handler import BpaHandler
    bpas = [BpaHandler.deserialize(p.read_bytes()) for p in (bpa_paths or [])]
    for slot in range(8):
        slots = [None] * 8
        for i, b in enumerate(bpas):
            slots[(slot + i) % 8] = b
        try:
            return bma.to_pil(bpc, bpl, slots, False, False, False, True)[0]
        except AssertionError:
            continue
    raise AssertionError("no BPA slot assignment accepted")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curation", type=Path, required=True)
    ap.add_argument("--pmd-root", type=Path, required=True)
    ap.add_argument("--write-json", type=Path, required=True)
    ap.add_argument("--write-md", type=Path, required=True)
    a = ap.parse_args()
    recs = [r for r in json.loads(a.curation.read_text())["records"]
            if r["source_id"] == "pmd_sky" and r["review_status"] == "decode_issue"]
    rows: dict[str, dict] = {}
    groups: dict[str, dict[str, tuple[dict, Path]]] = defaultdict(dict)
    for r in recs:
        p = a.pmd_root / r["source_path"]
        ext = p.suffix.lower().lstrip(".")
        rows[r["asset_id"]] = {"asset_id": r["asset_id"], "source_path": r["source_path"], "suffix": ext,
                               "technical_state": "unresolved", "detail": ""}
        if r["source_path"].startswith("files/MAP_BG/") and ext in ("bma", "bpc", "bpl", "bpa"):
            groups[("__bpa__" if ext == "bpa" else p.stem)][ext + (p.stem if ext == "bpa" else "")] = (r, p)
    ok_stems = set()
    for stem, g in groups.items():
        if stem == "__bpa__":
            continue
        need = {k: g[k][1] for k in ("bma", "bpc", "bpl") if k in g}
        if len(need) < 3:
            for k, (r, p) in g.items():
                if not k.startswith("bpa"):
                    rows[r["asset_id"]].update(technical_state="no_pair", detail="incomplete BMA/BPC/BPL set")
            continue
        try:
            bpas = [p for k, (r, p) in groups.get("__bpa__", {}).items()
                    if p.stem.startswith(stem) and len(p.stem) == len(stem) + 1 and p.stem[-1].isdigit()]
            im = render_bg(stem, need, sorted(bpas))
            st, det = ("valid_render", f"{im.size[0]}x{im.size[1]} composed background") if nonblank(im) else ("blank_render", "blank background")
        except Exception as e:  # noqa: BLE001
            st, det = "decode_failure", (str(e) or repr(e))[:140]
        for k in ("bma", "bpc", "bpl"):
            rows[g[k][0]["asset_id"]].update(technical_state=st, detail=det)
        if st == "valid_render":
            ok_stems.add(stem)
    for stem, g in groups.items():
        for k, (r, p) in g.items():
            if k.startswith("bpa"):
                parent = next((c for c in ok_stems if p.stem.startswith(c) and len(p.stem) == len(c) + 1 and p.stem[-1].isdigit()), "")
                try:
                    from skytemple_files.graphics.bpa.handler import BpaHandler
                    BpaHandler.deserialize(p.read_bytes())
                    ok = True
                except Exception as e:  # noqa: BLE001
                    rows[r["asset_id"]].update(technical_state="decode_failure", detail=str(e)[:120])
                    ok = False
                if ok:
                    if parent in ok_stems:
                        rows[r["asset_id"]].update(technical_state="companion_of_valid", detail="animated-tile (BPA) companion of valid composed background")
                    else:
                        rows[r["asset_id"]].update(technical_state="no_pair", detail="no valid same-stem background")
    chr_pal = {}
    for r in recs:
        p = a.pmd_root / r["source_path"]
        ext = p.suffix.lower().lstrip(".")
        row = rows[r["asset_id"]]
        try:
            if ext == "bgp":
                from skytemple_files.graphics.bgp.handler import BgpHandler
                im = BgpHandler.deserialize(p.read_bytes()).to_pil()
                row.update(technical_state="valid_render" if nonblank(im) else "blank_render", detail=f"{im.size[0]}x{im.size[1]} background")
            elif ext in ("wan", "wat", "wba"):
                st, det = eval_wan(p.read_bytes()); row.update(technical_state=st, detail=det)
            elif ext == "wte":
                st, det = eval_wte(p.read_bytes()); row.update(technical_state=st, detail=det)
            elif ext in ("chr", "pal") and r["source_path"].startswith("files/FONT/"):
                chr_pal.setdefault(p.with_suffix("").as_posix(), {})[ext] = (r, p)
        except Exception as e:  # noqa: BLE001
            row.update(technical_state="decode_failure", detail=(str(e) or repr(e))[:140])
    for key, d in chr_pal.items():
        if "chr" in d and "pal" in d:
            try:
                from skytemple_files.graphics.chr.handler import ChrHandler
                from skytemple_files.graphics.pal.handler import PalHandler
                c = ChrHandler.deserialize(d["chr"][1].read_bytes())
                pal = PalHandler.deserialize(d["pal"][1].read_bytes())
                c.set_palette(pal)
                im = c.to_pil().convert("RGBA")
                st, det = ("valid_render", f"{c.get_nb_tiles()} tiles with paired palette") if nonblank(im) else ("blank_render", "blank tiles")
            except Exception as e:  # noqa: BLE001
                st, det = "decode_failure", (str(e) or repr(e))[:140]
            for k in ("chr", "pal"):
                rows[d[k][0]["asset_id"]].update(technical_state=st, detail=det)
    out = sorted(rows.values(), key=lambda x: x["asset_id"])
    decisions = []
    for x in out:
        if x["technical_state"] == "valid_render":
            code, why = ("pmd_valid_render_plausible_use", "PMD Sky resource decodes with the SkyTemple reference decoder to nonblank imagery (background/UI/sprite material) with plausible Platinum use.")
        elif x["technical_state"] == "companion_of_valid":
            code, why = ("pmd_bpa_companion_of_valid_background", "Animated-tile companion of a valid composed PMD background.")
        else:
            continue
        decisions.append({"asset_id": x["asset_id"], "review_status": "usable", "reason_code": code, "reason": why,
                          "technical_state": x["technical_state"], "detail": x["detail"]})
    states = Counter(x["technical_state"] for x in out)
    suffix_states = {f"{s}:{k}": v for (s, k), v in sorted(Counter((x["suffix"], x["technical_state"]) for x in out).items())}
    res = {"schema_version": 1, "scope": "lane_cde_pmd_sky", "decoder": "skytemple-files 1.8.5", "asset_count": len(out),
           "technical_state_counts": dict(states), "suffix_state_counts": suffix_states, "records": out, "decisions": decisions}
    a.write_json.write_text(json.dumps(res, indent=1) + "\n")
    md = ["# Lanes C/D/E PMD Sky Recovery", "", "SkyTemple reference-decoder audit. No Platinum resources are modified.", "",
          f"- Assets: **{len(out)}**", "", "| Suffix:state | Assets |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in suffix_states.items()]
    a.write_md.write_text("\n".join(md) + "\n")
    print(dict(states))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
