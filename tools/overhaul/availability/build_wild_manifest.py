#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/wild_encounters.json from the placement plan.

Authoring aid: levels and before-guards come from the pinned base commit (see base_source.py), so the
output is reproducible even after the live encounter JSON has been rewritten.
"""
from __future__ import annotations

import json
import sys

from base_source import base_encounter
from common import (BANDS, BASE_COMMIT, IMPL_DIR, LAND_RATES, WATER_RATES)
from manifest_io import dumps_compact
from wild_plan import build

METHOD_MIN_BAND = {"old_rod": "E0", "good_rod": "M1", "surf": "M1", "super_rod": "P1"}
METHOD_GATE_NOTE = {
    "old_rod": "Old Rod: Route 218 gate fisherman (res/field/scripts/scripts_route_218_gate_to_jubilife_city.s)",
    "good_rod": "Good Rod: Route 209 fisherman (scripts_route_209.s)",
    "surf": "Surf: HM03 from Celestic Town Cave (scripts_celestic_town_cave.s) after the Cyrus battle",
    "super_rod": "Super Rod: Fight Area fisherman (scripts_fight_area.s) - Battle Frontier, post Hall of Fame",
}


def later(a: str, b: str) -> str:
    return a if BANDS.index(a) >= BANDS.index(b) else b


def family_index() -> dict[str, str]:
    fams = json.load(open(IMPL_DIR / "availability_families.json"))["families"]
    return {s: f["family_id"] for f in fams for s in f["components"]}


def main() -> int:
    plan = build()
    fam_of = family_index()
    entries, maps = [], {}
    for name in sorted(plan.maps):
        m = plan.maps[name]
        base = base_encounter(name)
        maps[name] = {"zone": m["zone"], "band": m["band"], "kind": m["kind"], "group": m.get("group"),
                      "base_land_rate": base.get("land_rate"),
                      "base_water_rates": {k: base.get(f"{k}_rate") for k in ("surf", "old_rod", "good_rod", "super_rod")}}
        for e in m["entries"]:
            meth = e["method"]
            if meth == "land":
                rate = LAND_RATES[e["slot"]]
            elif meth in ("land_day", "land_night"):
                rate = LAND_RATES[e["slot"]]
            else:
                rate = WATER_RATES[meth][e["slot"]]
            band = m["band"]
            if meth in METHOD_MIN_BAND:
                band = later(band, METHOD_MIN_BAND[meth])
            before = dict(e["before"])
            entries.append({
                "map": name, "method": meth, "slot": e["slot"], "species": e["species"],
                "family_id": fam_of[e["species"]], "level_min": e["level_min"], "level_max": e["level_max"],
                "rate_pct": rate, "time_condition": e["time_condition"], "band": band, "zone": m["zone"],
                "bonus_system": None, "before": before,
            })
    out = {
        "schema": "availability_wild_encounters/1",
        "base_commit": BASE_COMMIT,
        "generated_by": "tools/overhaul/availability/build_wild_manifest.py (placement plan in plan_*.py)",
        "status": "PROVISIONAL PLACEMENT - exact maps/slots/percentages require review (AVAILABILITY_ARCHITECTURE.md s.8)",
        "slot_semantics": {
            "land": "12 slots, fixed probabilities " + str(LAND_RATES) + "; src/overlay006/wild_encounters.c GetGroundEncounterSlot",
            "land_day/land_night": "arrays replacing land slots 2,3 outside the morning; index i -> slot 2+i",
            "surf/old_rod": str(WATER_RATES["surf"]), "good_rod/super_rod": str(WATER_RATES["good_rod"]),
            "rate_floor_pct": 5,
            "levels": "land slots inherit the base-commit level of the same slot; water slots inherit base level ranges",
        },
        "method_gates": METHOD_GATE_NOTE,
        "counts": {"maps": len(maps), "entries": len(entries)},
        "maps": maps,
        "entries": entries,
    }
    path = IMPL_DIR / "wild_encounters.json"
    path.write_text(dumps_compact(out))
    print(f"{len(maps)} maps, {len(entries)} entries -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
