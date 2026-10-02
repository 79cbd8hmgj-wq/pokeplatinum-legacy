"""Trainer -> map -> availability-band helpers (read-only; derived from field events + availability manifests)."""
from __future__ import annotations

import functools
import glob
import json
import os

from trainer_lib import p, species_data

BAND_ORDER = ["E0", "E1", "M1", "M2", "L1", "L2", "P0", "P1"]
# Interior/event-only maps absent from encounter_zones.json (band active while the player is inside).
EXTRA_MAP_BAND = {
    "cafe": "M1", "oreburgh_city_gym": "E0", "pastoria_city_gym": "M1", "canalave_city_gym": "M2",
    "snowpoint_city_gym": "L1", "sunyshore_city_gym_room_1": "L2", "sunyshore_city_gym_room_2": "L2",
    "sunyshore_city_gym_room_3": "L2", "veilstone_city_gym": "M1", "fuego_ironworks_building": "M1",
    "valley_windworks_building": "E1", "team_galactic_eterna_building_1f": "E1",
    "team_galactic_eterna_building_2f": "E1", "team_galactic_eterna_building_3f": "E1",
    "galactic_hq_1f": "L1", "galactic_hq_2f": "L1", "galactic_hq_3f": "L1", "galactic_hq_b2f": "L1",
    "lake_valor_drained": "L2", "route_222_west_house": "L2",
}
for _i in range(1, 7):
    EXTRA_MAP_BAND[f"hearthome_city_dp_gym_trainer_room_{_i}"] = "M1"
for _i in (1, 2):
    EXTRA_MAP_BAND[f"hearthome_city_gym_trainer_room_{_i}"] = "M1"


@functools.lru_cache(None)
def zone_bands() -> dict[str, str]:
    with open(p("docs/overhaul/implementation/encounter_zones.json"), encoding="utf-8") as f:
        z = json.load(f)["maps"]
    out = {k: v["band"] for k, v in z.items()}
    out.update(EXTRA_MAP_BAND)
    return out


@functools.lru_cache(None)
def trainer_maps() -> dict[str, list[str]]:
    """{trainer file stem: [event map names]} for trainers placed as map objects."""
    out: dict[str, list[str]] = {}
    for f in sorted(glob.glob(p("res/field/events/*.json"))):
        m = os.path.basename(f)[len("events_"):-5]
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        for o in d["object_events"]:
            if o["trainer_type"] != "TRAINER_TYPE_NONE" and str(o["script"]).startswith("TRAINER_"):
                out.setdefault(o["script"][len("TRAINER_"):].lower(), []).append(m)
    return out


def trainer_band(tid: str) -> str | None:
    """Latest (most permissive) availability band over the maps hosting the trainer, or None if unmapped."""
    maps = trainer_maps().get(tid)
    if not maps:
        return None
    bands = [zone_bands().get(m) for m in maps]
    bands = [b for b in bands if b]
    if not bands:
        return None
    return max(bands, key=BAND_ORDER.index)


@functools.lru_cache(None)
def family_band() -> dict[str, str | None]:
    with open(p("docs/overhaul/implementation/availability_families.json"), encoding="utf-8") as f:
        fams = json.load(f)["families"]
    out = {}
    for fam in fams:
        for c in fam["components"]:
            out[c] = fam["earliest_progression_band"]
    return out


@functools.lru_cache(None)
def special_species() -> frozenset[str]:
    """Species in gift/static/fossil-style families (SPECIAL_ACQUISITION); not used as random ordinary-trainer filler."""
    with open(p("docs/overhaul/implementation/availability_families.json"), encoding="utf-8") as f:
        fams = json.load(f)["families"]
    return frozenset(c for fam in fams if fam["availability_status"] == "SPECIAL_ACQUISITION" for c in fam["components"])


def species_band(const: str) -> str | None:
    return family_band().get(const)


def band_le(a: str, b: str) -> bool:
    return BAND_ORDER.index(a) <= BAND_ORDER.index(b)
