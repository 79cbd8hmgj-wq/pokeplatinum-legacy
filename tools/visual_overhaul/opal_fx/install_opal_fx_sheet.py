#!/usr/bin/env python3
"""Idempotently register a build_opal_fx_sheet.py output in res/graphics/battle/moves.

Usage: install_opal_fx_sheet.py <build_dir> <name>

Copies <name>.png/_cell.json/_anim.json (+ palette variants) into the move graphics directory, appends the
four NARC order files (existing NAIX indices are unchanged) and adds the files to the matching meson lists.
Palette variants are palette-only PNGs (no_cell_pngs_for_pal) producing extra NCLR members.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GFX = ROOT / "res/graphics/battle/moves"
PROV = ROOT / "docs/visual_overhaul/opal_installed_fx"


def add_line(path: Path, line: str):
    lines = path.read_text().splitlines()
    if line not in lines:
        path.write_text("\n".join(lines + [line]) + "\n")


def add_to_list(meson: str, list_name: str, entry: str) -> str:
    pattern = re.compile(rf"(^{list_name} = files\(\n(?:    '[^']+',\n(?:    #[^\n]*\n)*)*)(\)\n)", re.M)
    match = pattern.search(meson)
    if not match:
        raise SystemExit(f"meson list {list_name} not found")
    if f"'{entry}'" in match.group(1):
        return meson
    return meson[:match.end(1)] + f"    '{entry}',\n" + meson[match.start(2):]


def install(build_dir: Path, name: str):
    prov = json.loads((build_dir / f"{name}.provenance.json").read_text())
    for suffix in (".png", "_cell.json", "_anim.json"):
        shutil.copy2(build_dir / (name + suffix), GFX / (name + suffix))
    PROV.mkdir(parents=True, exist_ok=True)
    shutil.copy2(build_dir / f"{name}.provenance.json", PROV / f"{name}.provenance.json")
    add_line(GFX / "anim_ncgr.order", f"{name}.NCGR.lz")
    add_line(GFX / "anim_nclr.order", f"{name}.NCLR")
    add_line(GFX / "anim_ncer.order", f"{name}_cell.NCER.lz")
    add_line(GFX / "anim_nanr.order", f"{name}_anim.NANR.lz")
    meson = (GFX / "meson.build").read_text()
    meson = add_to_list(meson, "pngs", f"{name}.png")
    meson = add_to_list(meson, "pngs_for_pal", f"{name}.png")
    meson = add_to_list(meson, "cell_jsons", f"{name}_cell.json")
    meson = add_to_list(meson, "cellanm_jsons", f"{name}_anim.json")
    for variant in prov["palette_variants_rgb555"]:
        vname = f"{name}_{variant}"
        shutil.copy2(build_dir / f"{vname}.png", GFX / f"{vname}.png")
        add_line(GFX / "anim_nclr.order", f"{vname}.NCLR")
        meson = add_to_list(meson, "no_cell_pngs_for_pal", f"{vname}.png")
    (GFX / "meson.build").write_text(meson)


if __name__ == "__main__":
    install(Path(sys.argv[1]).resolve(), sys.argv[2])
