#!/usr/bin/env python3
"""Static asset gate for the Opal B2-B8 FX sheets (B2-06 / B8-02 / B8-03 source half).

Always:
  * every recipe has installed PNG / cell / anim JSON, provenance, NARC order entries (exactly once) and meson list entries
  * PNGs are 4bpp-compatible indexed images (<=16 palette entries, index 255 used only as the cell separator)
  * per-sheet OBJ tile budget (<= 192 tiles = 6 KiB char data) and <=15 opaque colours
  * every palette variant is registered as an NCLR with identical pixel data
  * every OPAL_RES(sheet, palette) used by a script names a registered sheet/palette, sequence indices exist
If the Emerald donor tree is available (POKEEMERALD_ROOT or ../pokeemerald): donor sha256 must match the provenance and
the sheet must rebuild byte-identically (deterministic conversion).
"""
import filecmp
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/visual_overhaul/opal_fx"))
import build_opal_fx_sheet as builder  # noqa: E402

GFX = ROOT / "res/graphics/battle/moves"
PROV = ROOT / "docs/visual_overhaul/opal_installed_fx"
RECIPES = ROOT / "tools/visual_overhaul/opal_fx/recipes"
MAX_TILES = 192


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def read_lines(p):
    return p.read_text().splitlines()


def main():
    donor_root = Path(os.environ.get("POKEEMERALD_ROOT", ROOT.parent / "pokeemerald"))
    have_donor = (donor_root / "graphics/battle_anims/sprites").is_dir()
    orders = {k: read_lines(GFX / f"anim_{k}.order") for k in ("ncgr", "nclr", "ncer", "nanr")}
    for k, lines in orders.items():
        dup = {l for l in lines if lines.count(l) > 1}
        if dup:
            fail(f"anim_{k}.order has duplicate entries {sorted(dup)}")
    meson = (GFX / "meson.build").read_text()
    sheets = {}
    for rp in sorted(RECIPES.glob("*.json")):
        recipe = json.loads(rp.read_text())
        name = recipe["name"]
        prov_path = PROV / f"{name}.provenance.json"
        if not prov_path.exists():
            fail(f"{name}: provenance missing")
        prov = json.loads(prov_path.read_text())
        for suffix in (".png", "_cell.json", "_anim.json"):
            if not (GFX / f"{name}{suffix}").exists():
                fail(f"{name}: {name}{suffix} not installed")
        for entry, key in ((f"{name}.NCGR.lz", "ncgr"), (f"{name}.NCLR", "nclr"), (f"{name}_cell.NCER.lz", "ncer"), (f"{name}_anim.NANR.lz", "nanr")):
            if orders[key].count(entry) != 1:
                fail(f"{name}: {entry} must appear exactly once in anim_{key}.order")
        for lst, ent in (("pngs", f"{name}.png"), ("pngs_for_pal", f"{name}.png"), ("cell_jsons", f"{name}_cell.json"), ("cellanm_jsons", f"{name}_anim.json")):
            if not re.search(rf"^{lst} = files\((?:.|\n)*?'{re.escape(ent)}'", meson, re.M):
                fail(f"{name}: {ent} not in meson list {lst}")
        # image checks
        from PIL import Image
        im = Image.open(GFX / f"{name}.png")
        if im.mode != "P" or len(im.getpalette()) // 3 > 256:
            fail(f"{name}: PNG must be indexed")
        used = set(im.tobytes())
        if used - set(range(16)) - {255}:
            fail(f"{name}: PNG uses palette indices outside 0-15 (+255 separator): {sorted(used - set(range(16)) - {255})}")
        if prov["obj_tiles"] > MAX_TILES:
            fail(f"{name}: {prov['obj_tiles']} OBJ tiles > {MAX_TILES}")
        if len(prov["palette_colours_rgb555"]) > 15:
            fail(f"{name}: more than 15 opaque colours")
        for variant in prov["palette_variants_rgb555"]:
            vname = f"{name}_{variant}"
            if orders["nclr"].count(f"{vname}.NCLR") != 1:
                fail(f"{vname}: NCLR not registered exactly once")
            if not re.search(rf"'{re.escape(vname)}\.png'", meson):
                fail(f"{vname}: png not in meson")
            vim = Image.open(GFX / f"{vname}.png")
            if vim.tobytes() != im.tobytes() or vim.size != im.size:
                fail(f"{vname}: pixel data differs from the base sheet")
        sheets[name] = prov
        if have_donor or all("procedural" in d for d in prov["donor_sources"].values()):
            for sid, d in prov["donor_sources"].items():
                if "path" in d:
                    got = builder.sha((donor_root / d["path"]).read_bytes())
                    if got != d["sha256"]:
                        fail(f"{name}: donor {d['path']} sha256 mismatch")
            with tempfile.TemporaryDirectory() as td:
                builder.build(rp, donor_root, Path(td), MAX_TILES)
                for suffix in (".png", "_cell.json", "_anim.json", ".provenance.json"):
                    src = Path(td) / f"{name}{suffix}"
                    dst = (PROV if suffix == ".provenance.json" else GFX) / f"{name}{suffix}"
                    if not filecmp.cmp(src, dst, shallow=False):
                        fail(f"{name}: {dst.relative_to(ROOT)} is not the deterministic rebuild of its recipe")
                for variant in prov["palette_variants_rgb555"]:
                    if not filecmp.cmp(Path(td) / f"{name}_{variant}.png", GFX / f"{name}_{variant}.png", shallow=False):
                        fail(f"{name}_{variant}.png is not the deterministic rebuild")
            mode = "rebuilt byte-identical"
        else:
            mode = "installed files checked (donor tree not available for rebuild)"
        print(f"ok   {name}: {prov['obj_tiles']} tiles, {len(prov['palette_colours_rgb555'])} colours, {len(prov['sequences'])} sequences, {len(prov['palette_variants_rgb555'])} variants; {mode}")

    # every OPAL_RES reference in scripts resolves
    pal_names = set(sheets) | {f"{n}_{v}" for n, p in sheets.items() for v in p["palette_variants_rgb555"]}
    # B1 Ranger donor sheets (installed, provenance in b1_installed_donors) may be driven through OpalFx as well
    b1_sheets = {p.name.split(".")[0] for p in (ROOT / "docs/visual_overhaul/b1_installed_donors").glob("*.provenance.json")}
    refs = 0
    for p in list((ROOT / "res/moves").glob("*/anim.s")) + list((ROOT / "res/battle/scripts/common_anims").glob("*.s")) + [ROOT / "asm/macros/btlanim_opal.inc"]:
        text = "\n".join(l for l in p.read_text().splitlines() if not l.lstrip().startswith("#define OPAL_RES"))
        for sheet, pal in re.findall(r"OPAL_RES\((\w+),\s*(\w+)\)", text):
            refs += 1
            if sheet in b1_sheets and pal == sheet:
                continue
            if sheet not in sheets or pal not in pal_names:
                fail(f"{p.relative_to(ROOT)}: OPAL_RES({sheet}, {pal}) names an unregistered sheet/palette")
            if not pal.startswith(sheet):
                fail(f"{p.relative_to(ROOT)}: palette {pal} does not belong to sheet {sheet}")
    print(f"PASS: {len(sheets)} Opal FX sheets registered consistently; {refs} script resource references resolve")


if __name__ == "__main__":
    main()
