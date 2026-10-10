#!/usr/bin/env python3
"""Validate donor-derived battle sprites installed through res/graphics/battle/moves."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOVES_GFX = ROOT / "res/graphics/battle/moves"
PROV_DIR = ROOT / "docs/visual_overhaul/b1_installed_donors"
TILE_BUDGET = 256
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


for prov_path in sorted(PROV_DIR.glob("*.provenance.json")):
    prov = json.loads(prov_path.read_text())
    name = prov["name"]
    check(prov["frames"] and all(len(f["cell_sha256"]) == 64 for f in prov["frames"]), f"{name}: provenance frames/hashes")
    check(prov["obj_tiles"] <= TILE_BUDGET, f"{name}: {prov['obj_tiles']} tiles over budget")
    check(len(prov["palette_colours_rgb555"]) <= 15, f"{name}: >15 colours")
    for suffix in (".png", "_cell.json", "_anim.json"):
        check((MOVES_GFX / (name + suffix)).is_file(), f"{name}{suffix} missing")
    meson = (MOVES_GFX / "meson.build").read_text()
    check(meson.count(f"'{name}.png'") == 2, f"{name}: png must be in pngs and pngs_for_pal")
    check(f"'{name}_cell.json'" in meson and f"'{name}_anim.json'" in meson, f"{name}: cell/anim not in meson")
    for order, line in (("anim_ncgr", f"{name}.NCGR.lz"), ("anim_nclr", f"{name}.NCLR"),
                        ("anim_ncer", f"{name}_cell.NCER.lz"), ("anim_nanr", f"{name}_anim.NANR.lz")):
        lines = (MOVES_GFX / f"{order}.order").read_text().split()
        check(lines.count(line) == 1, f"{name}: {line} not exactly once in {order}.order")
    cells = json.loads((MOVES_GFX / f"{name}_cell.json").read_text())
    anim = json.loads((MOVES_GFX / f"{name}_anim.json").read_text())
    check(cells["cellCount"] == len(prov["frames"]) == anim["frameCount"], f"{name}: frame counts disagree")
    check(anim["sequences"][0]["playbackMode"] == 1, f"{name}: must play once (OFFSET_AND_ANIMATE frees on end)")
    users = [p for p in (ROOT / "res/moves").glob("*/anim.s") if f"{name}_NCGR_lz" in p.read_text()]
    check(users, f"{name}: installed but referenced by no move script")
    for p in users:
        text = p.read_text()
        check(text.count("InitSpriteManager") == text.count("FreeSpriteManager"), f"{p}: unbalanced sprite manager")
        check(re.search(rf"AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, {name}_NCGR_lz, {name}_NCLR, "
                        rf"{name}_cell_NCER_lz, {name}_anim_NANR_lz", text), f"{p}: bad AddSpriteWithFunc")
    print(f"{name}: {len(prov['frames'])} frames, {prov['obj_tiles']} tiles, used by {len(users)} moves")

if failures:
    print("\n".join("FAIL: " + f for f in failures))
    sys.exit(1)
print("PASS: installed donor sprites are registered and referenced consistently")
