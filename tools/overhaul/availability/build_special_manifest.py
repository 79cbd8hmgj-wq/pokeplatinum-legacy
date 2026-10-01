#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/special_systems.json.

Policy (AVAILABILITY_ARCHITECTURE.md s.3, user-approved at policy level):
  * dual-slot  -> neutralised: slots 8/9 are mirrored into every cartridge array, so cartridge state cannot change a table
  * Radar / swarm / Honey / Trophy Garden dailies / Great Marsh dailies -> kept as bonus systems; every species they
    can produce points at a deterministic fixed fallback in wild_encounters.json
  * Great Marsh before/after National Dex arrays -> unified (after set); the Dex no longer changes the Marsh table
Nothing here chooses a USER_DECISION_REQUIRED design: decision families are recorded as such, never invented.
"""
from __future__ import annotations

import sys

from base_source import all_base_maps, base_encounter
from common import BASE_COMMIT, IMPL_DIR
from fallback import FallbackResolver
from manifest_io import dumps_compact
from state import VERSIONS, apply_wild, base_state, load_manifest

SWARM_MAPS = ["route_201", "route_202", "route_203", "route_206", "route_207", "route_208", "route_209", "route_214",
              "route_215", "route_217", "route_218", "route_221", "route_222", "route_224", "route_225", "route_226",
              "route_227", "route_228", "route_229", "route_230", "valley_windworks_outside", "eterna_forest"]


def main() -> int:
    wild = load_manifest("wild_encounters.json")
    st = base_state()
    apply_wild(st, wild, check=True)          # target wild state (before special arrays)
    fb = FallbackResolver(st, wild)

    def describe(sp):
        return {"species": sp, **fb.resolve(sp)}

    out = {"schema": "availability_special_systems/1", "base_commit": BASE_COMMIT,
           "status": "policy-level conversions only; no USER_DECISION_REQUIRED item is decided here"}

    dual = {}
    for name in all_base_maps():
        j = st[name]
        if "land_encounters" not in j or not j.get("land_rate"):
            continue
        after = [j["land_encounters"][8]["species"], j["land_encounters"][9]["species"]]
        before = {v: base_encounter(name)[v] for v in VERSIONS}
        former = sorted({sp for arr in before.values() for sp in arr if sp not in after and sp != "SPECIES_NONE"})
        dual[name] = {"before": before, "after": after,
                      "former_cartridge_species": [describe(sp) for sp in former]}
    out["dual_slot"] = {"policy": "NEUTRALIZED: every cartridge array mirrors land slots 8/9; no Slot-2 effect remains",
                        "maps": dual}

    radar, swarm = {}, {}
    for name in all_base_maps():
        j = st[name]
        if "land_encounters" in j and j.get("land_rate"):
            radar[name] = {"replaces_land_slots": [4, 5, 10, 11], "before": j["radar"], "after": j["radar"],
                           "entries": [describe(sp) for sp in j["radar"]]}
    for name in SWARM_MAPS:
        j = st[name]
        swarm[name] = {"replaces_land_slots": [0, 1], "before": j["swarms"], "after": j["swarms"],
                       "entries": [describe(sp) for sp in j["swarms"]]}
    out["radar"] = {"policy": "BONUS_ONLY: chaining/rarity; every species has a fixed ordinary path", "maps": radar}
    out["swarm"] = {"policy": "BONUS_ONLY: temporary abundance on the swarm map; never first availability",
                    "swarm_map_source": "src/overlay006/swarm.c sSwarmMapIdTable", "maps": swarm}

    h = st["honey_tree"]
    out["honey"] = {"policy": "BONUS_ONLY: efficient thematic method; never exclusive",
                    "tiers": {t: {"before": h[t], "after": h[t], "entries": [describe(sp) for sp in h[t]]}
                              for t in ("common", "uncommon", "rare")}}

    tg = st["trophy_garden"]["daily_encounters"]
    out["trophy_garden"] = {
        "policy": "BONUS_ONLY: rotating showcase (slots 6/7, only after National Dex per wild_encounters.c). "
                  "Decision families (Eevee, Happiny/Chansey, Castform) stay in the rotation untouched.",
        "daily": {"before": tg, "after": tg, "entries": [describe(sp) for sp in tg]}}

    gm = st["great_marsh_lookout"]
    out["great_marsh"] = {
        "policy": "BONUS_ONLY dailies on stable per-area cores; before/after National Dex arrays unified so the Dex "
                  "never changes the Marsh table",
        "arrays": {
            "before_national_dex": {"before": gm["before_national_dex"], "after": gm["after_national_dex"],
                                    "entries": [describe(sp) for sp in gm["after_national_dex"]]},
            "after_national_dex": {"before": gm["after_national_dex"], "after": gm["after_national_dex"],
                                   "entries": [describe(sp) for sp in gm["after_national_dex"]]}}}
    path = IMPL_DIR / "special_systems.json"
    path.write_text(dumps_compact(out, line_arrays=("entries",)))
    print("special systems ->", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
