#!/usr/bin/env python3
"""Targeted-review montages for the highest-value hgss_field_3d families (reads committed renders only).

Writes docs/visual_overhaul/selection/mining/review/field_3d_<family>.png and field_3d_review_groups.json (group ids per montage, in order).
"""
from __future__ import annotations

import json
import sys

from PIL import Image, ImageDraw

from common import *  # noqa: F401,F403

OUT = SEL / "mining" / "review"
FAMILIES = {"models_building_exterior": ("hgss_bm_field_building_exterior", 24), "models_room_gym_panels": (("hgss_bm_room_interior_room_shell", "hgss_bm_field_gym_structure", "hgss_bm_field_door_window_panel", "hgss_bm_room_machinery_terminal"), 24),
            "textures_top_sets": (("hgss_texset_floor_interior", "hgss_texset_foliage_ground", "hgss_texset_wall_architecture", "hgss_texset_rock_cliff", "hgss_texset_water"), 8),
            "followers_legendary": ("hgss_follower_legendary", 16), "followers_species": ("hgss_follower_species", 16)}


def main() -> int:
    pool = jload(SEL / "OPPORTUNITY_POOL.json")
    cat = {}
    for p in sorted(EXT_DIR.glob("hgss_field_3d/CATALOG.json")):
        cat = {a["asset_id"]: a for a in jload(p)["assets"]}
    members = jload(SEL / "CANDIDATE_GROUPS.json")
    sample = {}
    OUT.mkdir(parents=True, exist_ok=True)
    mapping = {}
    for name, (fam, n) in FAMILIES.items():
        fams = (fam,) if isinstance(fam, str) else fam
        recs = sorted([r for r in pool["records"] if r.get("origin") == "mined" and r["source_id"] == "hgss" and r["family"] in fams and r["status"] == "promoted"], key=lambda r: -r["composite"])
        seen, rows = set(), []
        for r in recs:
            if r["group_id"] in seen:
                continue
            seen.add(r["group_id"])
            rows.append(r)
            if len(rows) >= n:
                break
        ims, ids = [], []
        for r in rows:
            a = cat[r["member_sample"][0]]
            if a["render_path"] and (ROOT / a["render_path"]).is_file():
                im = Image.open(ROOT / a["render_path"]).convert("RGB")
                if name.startswith("followers") or name.startswith("textures"):
                    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST) if name.startswith("followers") else im
                ims.append(im)
                ids.append(r["group_id"])
        if not ims:
            continue
        cols = 4 if name.startswith(("followers", "textures")) else 6
        cw, ch = max(i.width for i in ims), max(i.height for i in ims)
        rows_n = (len(ims) + cols - 1) // cols
        S = Image.new("RGB", (cols * (cw + 4), rows_n * (ch + 4)), (24, 24, 32))
        for k, im in enumerate(ims):
            S.paste(im, ((k % cols) * (cw + 4), (k // cols) * (ch + 4)))
        S.save(OUT / f"field_3d_{name}.png", optimize=True)
        mapping[name] = ids
    jdump(OUT / "field_3d_review_groups.json", mapping)
    print({k: len(v) for k, v in mapping.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
