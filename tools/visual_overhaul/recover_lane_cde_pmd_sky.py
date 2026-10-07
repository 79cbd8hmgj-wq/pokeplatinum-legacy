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
    # BPA file name = stem + slot digit.  Try the digit as the slot index (then digit-1) first.
    for off in (0, -1):
        slots = [None] * 8
        try:
            for p in bpa_paths or []:
                slots[int(p.stem[-1]) + off] = BpaHandler.deserialize(p.read_bytes())
            return bma.to_pil(bpc, bpl, slots, False, False, False, True)[0]
        except (AssertionError, IndexError):
            continue
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


def eval_misc(path: Path, rel: str):
    """Standalone PMD UI/data resources.  Returns (state, detail) or None if not handled."""
    ext = path.suffix.lower().lstrip(".")
    data = path.read_bytes()
    if ext == "kao":
        from skytemple_files.graphics.kao.handler import KaoHandler
        k = KaoHandler.deserialize(data)
        n = 0
        for i in range(k.n_entries()):
            for sub in range(k.toc_len):
                try:
                    kk = k.get(i, sub)
                except Exception:  # noqa: BLE001
                    kk = None
                if kk is not None:
                    n += 1
                    if n == 1:
                        first = kk.get()
        return ("valid_render", f"{n} portraits ({first.size[0]}x{first.size[1]}) across {k.n_entries()} entries") if n else ("blank_render", "no portraits")
    if ext == "w16":
        from skytemple_files.graphics.w16.handler import W16Handler
        w = W16Handler.deserialize(data)
        ok = sum(1 for f in w._files if nonblank(f.get().convert("RGBA")))
        return ("valid_render", f"{ok}/{len(w._files)} nonblank images") if ok else ("blank_render", "all blank")
    if ext == "dat" and rel.startswith("files/FONT/"):
        from skytemple_files.graphics.fonts.font_dat.handler import FontDatHandler
        f = FontDatHandler.deserialize(data)
        tabs = f.to_pil()
        ok = [t for t, im in tabs.items() if im.getbbox() and len(set(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())) > 1]
        return ("valid_render", f"{len(f.entries)} glyph entries, {len(ok)} glyph table(s) nonblank") if ok else ("blank_render", "no glyph pixels")
    if ext == "pal":
        from skytemple_files.graphics.pal.handler import PalHandler
        pal = PalHandler.deserialize(data).get_palette()
        cols = {tuple(pal[i:i + 3]) for i in range(0, len(pal) - 2, 3)}
        return ("palette_only", f"{len(cols)} distinct colours") if len(cols) > 1 else ("blank_render", "uniform palette")
    if path.name == "dw_icon.bin" and (path.parent / "dw_plt.bin").exists():
        import struct as st
        from PIL import Image
        pal = [st.unpack_from("<H", (path.parent / "dw_plt.bin").read_bytes(), 2 * i)[0] for i in range(16)]
        im = Image.new("RGBA", (32, 32))
        for i, b in enumerate(data):
            for half, v in enumerate((b & 15, b >> 4)):
                px = i * 2 + half
                tile, within = divmod(px, 64)
                tx, ty = tile % 4, tile // 4
                x, y = tx * 8 + within % 8, ty * 8 + within // 8
                c = pal[v]
                im.putpixel((x, y), ((c & 31) * 8, ((c >> 5) & 31) * 8, ((c >> 10) & 31) * 8, 255 if v else 0))
        return ("valid_render", "32x32 4bpp DS banner-style icon with dw_plt.bin") if nonblank(im) else ("blank_render", "blank icon")
    if path.name == "dw_plt.bin":
        return ("palette_only", "16-colour BGR555 palette of dw_icon.bin")
    if path.name in ("te_dic.bin", "te_sdic.bin"):
        import struct as st
        cnt = st.unpack_from("<I", data, 0)[0]
        recs = [st.unpack_from("<HH", data, 4 + 8 * i) for i in range(cnt)] if 4 + 8 * cnt <= len(data) else None
        return None if recs is None else ("dictionary_table", f"count={cnt}, {len(data)} bytes")
    return None


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
    bg_dir = a.pmd_root / "files/MAP_BG"
    blank_stems = {}
    for stem, g in groups.items():
        if stem == "__bpa__":
            continue
        need = {k: g[k][1] for k in ("bma", "bpc", "bpl") if k in g}
        parent_used = ""
        if len(need) < 3 and "bma" in g:
            # Variant maps (trailing digit) may share the parent's BPC/BPL; accept only if the parent file exists on disk.
            par = stem.rstrip("0123456789") if stem[-1].isdigit() else ""
            for k in ("bpc", "bpl"):
                if k not in need and par and (bg_dir / f"{par}.{k}").exists():
                    need[k] = bg_dir / f"{par}.{k}"
                    parent_used = par
        if len(need) < 3:
            for k, (r, p) in g.items():
                if not k.startswith("bpa"):
                    rows[r["asset_id"]].update(technical_state="no_pair", detail="incomplete BMA/BPC/BPL set")
            continue
        try:
            bpas = [p for k, (r, p) in groups.get("__bpa__", {}).items()
                    if p.stem.startswith(stem) and len(p.stem) == len(stem) + 1 and p.stem[-1].isdigit()]
            im = render_bg(stem, need, sorted(bpas))
            if nonblank(im):
                st, det = "valid_render", f"{im.size[0]}x{im.size[1]} composed background" + (f" (BPC/BPL shared from parent {parent_used})" if parent_used else "")
            else:
                st, det = "blank_render", "composed background is fully transparent/uniform"
        except Exception as e:  # noqa: BLE001
            st, det = "decode_failure", (str(e) or repr(e))[:140]
        for k in ("bma", "bpc", "bpl"):
            if k in g:
                rows[g[k][0]["asset_id"]].update(technical_state=st, detail=det)
        if st == "valid_render":
            ok_stems.add(stem)
        elif st == "blank_render":
            blank_stems[stem] = need
    # blank composites: the BMA is rejected only with evidence (layers reference a single chunk id);
    # its BPC/BPL stay usable iff their tile sheet itself holds real art.
    for stem, need in blank_stems.items():
        g = groups[stem]
        try:
            from skytemple_files.graphics.bma.handler import BmaHandler
            from skytemple_files.graphics.bpc.handler import BpcHandler
            from skytemple_files.graphics.bpl.handler import BplHandler
            bma = BmaHandler.deserialize(need["bma"].read_bytes())
            ids = set(bma.layer0) | (set(bma.layer1) if bma.number_of_layers > 1 else set())
            bpc = BpcHandler.deserialize(need["bpc"].read_bytes(), bma.tiling_width, bma.tiling_height)
            bpl = BplHandler.deserialize(need["bpl"].read_bytes())
            sheet = bpc.tiles_to_pil(0, bpl.palettes, 16).convert("RGB")
            colours = len(set(sheet.get_flattened_data() if hasattr(sheet, "get_flattened_data") else sheet.getdata()))
        except Exception as e:  # noqa: BLE001
            continue
        if "bma" in g and len(ids) <= 1:
            rows[g["bma"][0]["asset_id"]].update(technical_state="blank_map", detail=f"layers reference only chunk id(s) {sorted(ids)}; composite fully transparent")
        for k in ("bpc", "bpl"):
            if k in g and need[k].parent == bg_dir and need[k].stem == stem:
                if colours >= 3:
                    rows[g[k][0]["asset_id"]].update(technical_state="valid_render", detail=f"tile sheet holds art ({colours} colours) although this map's layers are blank")
                else:
                    rows[g[k][0]["asset_id"]].update(technical_state="blank_map", detail=f"tile sheet has only {colours} colour(s) and the map layers are blank")
    # palette-only BPL variants (e.g. s13p01b2.bpl): valid when a parent stem composed successfully
    for stem, g in groups.items():
        if stem != "__bpa__" and set(g) == {"bpl"} and stem[-1].isdigit() and stem.rstrip("0123456789") in ok_stems:
            try:
                from skytemple_files.graphics.bpl.handler import BplHandler
                BplHandler.deserialize(g["bpl"][1].read_bytes())
                rows[g["bpl"][0]["asset_id"]].update(technical_state="companion_of_valid", detail=f"palette variant of valid background {stem.rstrip('0123456789')}")
            except Exception as e:  # noqa: BLE001
                rows[g["bpl"][0]["asset_id"]].update(technical_state="decode_failure", detail=str(e)[:100])
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
            elif ext == "chr" and r["source_path"].startswith("files/FONT/"):
                chr_pal.setdefault(p.with_suffix("").as_posix(), {})[ext] = (r, p)
            elif ext == "pal" and r["source_path"].startswith("files/FONT/") and p.with_suffix(".chr").exists():
                chr_pal.setdefault(p.with_suffix("").as_posix(), {})[ext] = (r, p)
            else:
                got = eval_misc(p, r["source_path"])
                if got:
                    row.update(technical_state=got[0], detail=got[1])
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
            code, why = ("pmd_companion_of_valid_background", "Animated-tile (BPA) or palette-variant (BPL) companion of a valid composed PMD background.")
        elif x["technical_state"] == "palette_only":
            code, why = ("pmd_standalone_palette_color_reference", "Valid standalone PMD palette resource (decoded colours); usable only as a colour reference, no pixel imagery of its own.")
        elif x["technical_state"] == "blank_map":
            decisions.append({"asset_id": x["asset_id"], "review_status": "reject", "reason_code": "pmd_blank_map_background",
                              "reason": "Map background resource with no visible content: its layers reference only a single blank chunk (composite fully transparent) and no tile art of its own.",
                              "technical_state": x["technical_state"], "detail": x["detail"]})
            continue
        elif x["technical_state"] == "dictionary_table":
            decisions.append({"asset_id": x["asset_id"], "review_status": "reject", "reason_code": "pmd_text_dictionary_table",
                              "reason": "Structured (offset,length) text dictionary table, not visual art.",
                              "technical_state": x["technical_state"], "detail": x["detail"]})
            continue
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
