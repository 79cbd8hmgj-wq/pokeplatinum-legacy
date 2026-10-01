#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/encounter_zones.json (map -> zone, band, gate, methods, level band, family budget)."""
from __future__ import annotations

import json
import sys

from base_source import all_base_maps, base_encounter
from common import BANDS, BASE_COMMIT, IMPL_DIR, ZONES
from manifest_io import dumps_compact
from state import WATER_METHODS, apply_wild, base_state, load_manifest
from zone_index import zone_index
from zones_data import ADJACENT, BAND_GATES, UNMODIFIED

FAMILY_CAP = {"ordinary": 8, "connector": 5, "signature": 9, "water": 4, "unmodified": None}


def main() -> int:
    wild = load_manifest("wild_encounters.json")
    fams = json.load(open(IMPL_DIR / "availability_families.json"))["families"]
    fam_of = {s: f["family_id"] for f in fams for s in f["components"]}
    st = base_state()
    apply_wild(st, wild, check=True)
    idx = zone_index(wild)
    by_map_entries = {}
    for e in wild["entries"]:
        by_map_entries.setdefault(e["map"], []).append(e)
    maps = {}
    for name in all_base_maps():
        if name not in idx:
            print("map without zone metadata:", name, file=sys.stderr)
            return 1
        z = idx[name]
        j = st[name]
        methods = []
        if j.get("land_rate"):
            methods.append("land")
        methods += [m for m in WATER_METHODS if j.get(f"{m}_rate")]
        levels = {}
        if j.get("land_rate"):
            lv = [e["level"] for e in j["land_encounters"]]
            levels["land"] = [min(lv), max(lv)]
        for m in WATER_METHODS:
            if j.get(f"{m}_rate"):
                levels[m] = [min(e["level_min"] for e in j[f"{m}_encounters"]),
                             max(e["level_max"] for e in j[f"{m}_encounters"])]
        used = {}
        if j.get("land_rate"):
            sp = {e["species"] for e in j["land_encounters"]} | set(j["day"]) | set(j["night"])
            used["land"] = sorted({fam_of[s] for s in sp if s in fam_of})
        for m in WATER_METHODS:
            if j.get(f"{m}_rate"):
                used[m] = sorted({fam_of[e["species"]] for e in j[f"{m}_encounters"] if e["species"] in fam_of})
        kind = z["kind"]
        cap = FAMILY_CAP.get(kind, 8)
        if kind == "water":
            cap_desc = {"water_per_method": 4}
        elif kind == "unmodified":
            cap_desc = None
        else:
            cap_desc = {"land": cap, "water_per_method": 4}
        maps[name] = {
            "zone": z["zone"], "band": z["band"], "story_gate": BAND_GATES[z["band"]],
            "kind": kind, "authored_by_this_work": z["authored"],
            "encounter_methods": methods, "intended_level_band": levels,
            "family_cap_budget": cap_desc,
            "families_in_final_tables": {k: len(v) for k, v in used.items()},
            "note": UNMODIFIED[name][2] if name in UNMODIFIED else wild["maps"][name].get("group"),
        }
    out = {
        "schema": "availability_encounter_zones/1", "base_commit": BASE_COMMIT,
        "zones": {"START": "Twinleaf-Jubilife meadow, lake edge, farm fringe", "ORE": "Oreburgh mine/gate/foothills",
                  "FOREST": "Floaroma, Eterna woodland, Old Chateau", "CYCLE": "routes 206-208 scrub, Wayward Cave",
                  "HEARTH": "Hearthome-Solaceon pasture/ruins", "MARSH": "routes 212-213, Great Marsh, Valor shore",
                  "CORONET": "lower/upper Mt. Coronet", "IRON": "Fuego, Canalave, Iron Island",
                  "COAST": "freshwater/estuary/sea separated by method", "SNOW": "routes 216-217, Acuity",
                  "DRY": "route 214 and dry pockets", "EAST": "Valor-Sunyshore-route 222/223",
                  "DEEP": "deep caves and Victory Road", "POST": "routes 224-230 and islands, postgame"},
        "bands": BAND_GATES,
        "density_targets": {"ordinary_land_families": "6-8", "connector": "4-5", "signature_max": 9, "water_per_method": "3-4"},
        "adjacency": [{"a": a, "b": b, "continuous": c} for a, b, c in ADJACENT],
        "level_policy": "slots keep the base-commit level of the same slot (route level curve preserved)",
        "maps": maps,
    }
    path = IMPL_DIR / "encounter_zones.json"
    path.write_text(dumps_compact(out, line_arrays=("adjacency",)))
    print(len(maps), "maps ->", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
