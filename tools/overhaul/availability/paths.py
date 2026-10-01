"""Derive acquisition paths (species -> where/how/at what rate) from an encounter state."""
from __future__ import annotations

import collections
from dataclasses import dataclass, field

from common import LAND_RATES, WATER_RATES, SLOT_ROLES, BANDS
from state import WATER_METHODS

TIME_STATES = ("morning", "day", "night")
# land slots replaced by Trophy Garden / Great Marsh Safari dailies -> not stable on those maps
DAILY_REPLACED_MAPS = ("trophy_garden", "great_marsh_1", "great_marsh_2", "great_marsh_3", "great_marsh_4",
                       "great_marsh_5", "great_marsh_6")
METHOD_MIN_BAND = {"old_rod": "E0", "good_rod": "M1", "surf": "M1", "super_rod": "P1"}


@dataclass
class Path:
    map: str
    method: str
    species: str
    rates: dict          # time-state -> total % (stable slots only)
    slots: list = field(default_factory=list)

    @property
    def safari(self):
        """Great Marsh encounters are Safari-format (limited balls, fee): never the sole path for a family."""
        return self.map.startswith("great_marsh_")

    @property
    def min_rate(self):
        return min(self.rates.values())

    @property
    def max_rate(self):
        return max(self.rates.values())


def land_tables(j, mapname):
    """Return {state: [12 species]} with swarm/trophy/dual-slot replacements deliberately NOT applied."""
    base = [e["species"] for e in j["land_encounters"]]
    out = {}
    for st in TIME_STATES:
        t = list(base)
        if st == "day":
            t[2], t[3] = j["day"][0], j["day"][1]
        elif st == "night":
            t[2], t[3] = j["night"][0], j["night"][1]
        out[st] = t
    return out


def collect_paths(state: dict[str, dict]) -> list[Path]:
    paths = []
    for name, j in state.items():
        if "land_encounters" in j and j.get("land_rate"):
            tabs = land_tables(j, name)
            species = {s for t in tabs.values() for s in t}
            for sp in species:
                rates, slots = {}, []
                for st, t in tabs.items():
                    r = 0
                    for i, s in enumerate(t):
                        if s != sp:
                            continue
                        if name in DAILY_REPLACED_MAPS and i in (6, 7):
                            continue            # replaced by dailies -> not stable
                        if LAND_RATES[i] < 5:
                            continue            # below the 5% floor: never relied on
                        r += LAND_RATES[i]
                        slots.append((st, i))
                    rates[st] = r
                if max(rates.values()) > 0:
                    paths.append(Path(name, "land", sp, rates, sorted(set(slots))))
        for m in WATER_METHODS:
            if j.get(f"{m}_rate"):
                acc = collections.defaultdict(int)
                slots = collections.defaultdict(list)
                for i, e in enumerate(j[f"{m}_encounters"]):
                    sp = e["species"]
                    if sp == "SPECIES_NONE" or WATER_RATES[m][i] < 5:
                        continue
                    acc[sp] += WATER_RATES[m][i]
                    slots[sp].append(i)
                for sp, r in acc.items():
                    paths.append(Path(name, m, sp, {st: r for st in TIME_STATES}, slots[sp]))
    return paths
