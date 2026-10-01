"""Resolve a species to its deterministic fixed (non-bonus) fallback path."""
from __future__ import annotations

import json

from common import BANDS, IMPL_DIR, PRE_E4_BANDS, REQUIRED_MIN_RATE
from paths import METHOD_MIN_BAND, collect_paths
from zone_index import zone_index


class FallbackResolver:
    def __init__(self, state, wild=None):
        fams = json.load(open(IMPL_DIR / "availability_families.json"))["families"]
        self.family = {s: f for f in fams for s in f["components"]}
        self.mapband = {n: m["band"] for n, m in zone_index(wild).items()} if wild else {}
        self.by_family: dict[str, list] = {}
        for p in collect_paths(state):
            fam = self.family.get(p.species)
            if not fam:
                continue
            band = self._band(p)
            if band not in PRE_E4_BANDS or p.min_rate < REQUIRED_MIN_RATE or p.safari:
                continue
            self.by_family.setdefault(fam["family_id"], []).append((BANDS.index(band), -p.min_rate, p, band))

    def _band(self, p):
        b = self.mapband.get(p.map, "P1")      # maps outside the plan are not relied on
        g = METHOD_MIN_BAND.get(p.method)
        if g and BANDS.index(g) > BANDS.index(b):
            b = g
        return b

    def resolve(self, species):
        fam = self.family.get(species)
        if fam is None:
            return {"family_id": None, "fallback": "UNKNOWN_SPECIES"}
        if fam["classification"] != "NONLEGENDARY":
            return {"family_id": fam["family_id"], "fallback": "RESERVED_LATER_PHASE"}
        if fam["user_decision_required"]:
            return {"family_id": fam["family_id"], "fallback": "USER_DECISION_REQUIRED",
                    "decision": fam["user_decision_key"]}
        cands = sorted(self.by_family.get(fam["family_id"], []), key=lambda t: (t[0], t[1]))
        if not cands:
            return {"family_id": fam["family_id"], "fallback": "NO_FALLBACK"}
        _, _, p, band = cands[0]
        return {"family_id": fam["family_id"],
                "fallback": {"map": p.map, "method": p.method, "species": p.species, "min_rate_pct": p.min_rate,
                             "band": band}}
