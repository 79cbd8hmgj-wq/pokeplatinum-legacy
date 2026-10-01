"""Authoring helpers: turn compact per-map plans into explicit manifest entries.

Levels are inherited slot-for-slot from the *base commit* tables (so route level curves are
preserved) unless a plan overrides them. Every generated entry carries a before-value guard.
"""
from __future__ import annotations

from base_source import base_encounter
from common import LAND_RATES, WATER_RATES, SPECIES_ID

LAND_CORE_SLOTS = [0, 1, 2, 4, 5, 6, 7]   # slot 2 is time-invariant here; slot 3 carries time-of-day flavour
LAND_TAIL_SLOTS = [8, 9, 10, 11]


def sp(name: str) -> str:
    s = "SPECIES_" + name.upper()
    if s not in SPECIES_ID:
        raise KeyError(f"unknown species {name!r}")
    return s


def _names(s):
    return s.split() if isinstance(s, str) else list(s)


class Plan:
    def __init__(self):
        self.maps: dict[str, dict] = {}

    def land(self, name, zone, band, kind, core, time3, tail, level_overrides=None, note=None, group=None):
        """core: 7 species -> slots 0,1,2,4,5,6,7 (all time-invariant; slots 0/1 are 20%, 2/4/5 are 10%, 6/7 are 5%).
        time3: (morning, day, night) species for slot 3 (10%, time-of-day flavour).
        tail: 4 species -> slots 8..11 (4/4/1/1%; slots 8/9 are dual-slot replacement positions)."""
        core, tail = _names(core), _names(tail)
        t3 = _names(time3)
        assert len(core) == 7 and len(tail) == 4 and len(t3) == 3, name
        morning, day, night = [core[2], t3[0]], [core[2], t3[1]], [core[2], t3[2]]
        base = base_encounter(name)
        assert base["land_rate"] > 0, f"{name}: base land_rate is 0; cannot add land encounters"
        slots = {}
        for s, v in zip(LAND_CORE_SLOTS, core):
            slots[s] = v
        slots[3] = t3[0]
        for s, v in zip(LAND_TAIL_SLOTS, tail):
            slots[s] = v
        entries = []
        for s in range(12):
            b = base["land_encounters"][s]
            lvl = (level_overrides or {}).get(s, b["level"])
            keep = slots[s] == "="            # "=" keeps the base species (used to leave USER_DECISION families untouched)
            entries.append(dict(method="land", slot=s, species=b["species"] if keep else sp(slots[s]), level_min=lvl, level_max=lvl,
                                time_condition="morning" if s == 3 else "any",
                                before=dict(species=b["species"], level_min=b["level"], level_max=b["level"])))
        for cond, arr, key in (("day", day, "day"), ("night", night, "night")):
            for i, v in enumerate(arr):
                entries.append(dict(method=f"land_{cond}", slot=2 + i, species=sp(v),
                                    level_min=base["land_encounters"][2 + i]["level"],
                                    level_max=base["land_encounters"][2 + i]["level"], time_condition=cond,
                                    before=dict(species=base[key][i], level_min=None, level_max=None)))
        m = self.maps.setdefault(name, dict(zone=zone, band=band, kind=kind, entries=[], note=note, group=group))
        m["entries"].extend(entries)
        m["zone"], m["band"], m["kind"] = zone, band, kind
        return self

    def water(self, name, zone, band, kind="water", **methods):
        """methods: surf/old_rod/good_rod/super_rod = list of 5 species (or None to keep a slot)."""
        base = base_encounter(name)
        m = self.maps.setdefault(name, dict(zone=zone, band=band, kind=kind, entries=[], note=None, group=None))
        if m["band"] != band and m["kind"] == "water":
            m["band"] = band
        for meth, species in methods.items():
            assert base.get(f"{meth}_rate", 0) > 0, f"{name}: base {meth}_rate is 0"
            species = _names(species)
            assert len(species) == 5, (name, meth)
            for i, v in enumerate(species):
                if v in ("-", None):
                    continue
                b = base[f"{meth}_encounters"][i]
                m["entries"].append(dict(method=meth, slot=i, species=sp(v), level_min=b["level_min"],
                                         level_max=b["level_max"], time_condition="any",
                                         before=dict(species=b["species"], level_min=b["level_min"], level_max=b["level_max"])))
        m["zone"] = m["zone"] or zone
        return self
