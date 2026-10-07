#!/usr/bin/env python3
"""Donor-free tests for the hgss_field_3d catalog extension and its mining (python3 test_field_3d.py)."""
from __future__ import annotations

import collections

from common import *  # noqa: F401,F403
import mapping

cat = jload(EXT_DIR / "hgss_field_3d" / "CATALOG.json")
cur = jload(EXT_DIR / "hgss_field_3d" / "CURATION.json")
A = {a["asset_id"]: a for a in cat["assets"]}
base_ids = {a["asset_id"] for a in jload(VO / "DONOR_ASSET_CATALOG.json")["assets"]}
others = set()
for e in extensions():
    if e["id"] != "hgss_field_3d":
        others |= {a["asset_id"] for a in jload(EXT_DIR / e["catalog"])["assets"]}


def ok(msg):
    print("ok  ", msg)


assert len(A) == len(cat["assets"]) == len(cur["records"]) and set(A) == {r["asset_id"] for r in cur["records"]}
assert not (set(A) & base_ids) and not (set(A) & others)
ok("catalog and curation cover the same unique ids, disjoint from the base catalog and the other extensions")
assert all(src["source_commit"] and len(src["source_commit"]) == 40 for src in cat["sources"]) and all(a["source_metadata"]["source_commit"] == cat["sources"][0]["source_commit"] for a in A.values())
ok("every asset pins the same 40-hex HGSS commit")
by = collections.Counter(a["asset_type"] for a in A.values())
assert by == {"nitro_map_texture": 3659, "nitro_model_bmd0": 562, "nsbtx_pokemon_sheet": 572}, by
ok("asset counts: 562 models, 3659 map textures, 572 follower sheets")
groups = jload(GROUPS_JSON)["groups"]
g3 = [g for g in groups if g["subsystem"] in ("field_building_models", "field_texture_sets", "overworld_pokemon_sheets")]
assert collections.Counter(g["subsystem"] for g in g3) == {"field_building_models": 562, "field_texture_sets": 106, "overworld_pokemon_sheets": 572}
assert sum(g["member_count"] for g in g3) == sum(1 for r in cur["records"] if r["review_status"] == "usable")
ok("1,240 groups (562 / 106 / 572) hold every usable asset exactly once")
fol = [a for a in A.values() if a["asset_type"] == "nsbtx_pokemon_sheet"]
assert all(a["source_metadata"]["frames"] == 8 and a["source_metadata"]["palette_count"] == 2 for a in fol)
assert sum(a["source_metadata"]["slot_placeholder"] for a in fol) == 6 and sum(1 for a in fol if a["species_dex"]) == 566
ok("follower sheets: 8 frames, 2 palettes, 566 species-resolved + 6 slot placeholders")
no_overlap = {r["source_path"] for r in cur["records"]}
human = jload(EXT_DIR / "hgss_field_sprites" / "CATALOG.json")["assets"]
assert not (no_overlap & {a["source_path"] for a in human})
ok("follower sheets do not overlap the human field-sprite extension")
pool = jload(SEL / "OPPORTUNITY_POOL.json")
new = [r for r in pool["records"] if r.get("origin") == "mined" and r["domain"] in ("models", "textures", "overworld_pokemon") and r["source_id"] == "hgss"]
assert new and all(r["classification"] != "replacement_candidate" for r in new)
ok("no whole-asset replacement candidate is produced for the extension (structural conversion / contract mismatch)")
assert not any(r["status"] == "needs_evidence" for r in new)
ok("no new needs-evidence records (decoded + rendered evidence)")
for g in g3[:3]:
    c = mapping.classify({"source_id": "hgss", "source_path": g["sample_paths"][0]})
    assert c["unit"] == g["unit"]
ok("mapping is stable for sample paths")
