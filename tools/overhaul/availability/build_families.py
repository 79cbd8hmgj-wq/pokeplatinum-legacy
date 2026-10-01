#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/availability_families.json.

Families are connected components of the evolution graph in live source (res/pokemon/*/data.json).
Each nonlegendary component is joined to its row in the approved Pass 3 matrix; rows are matched by
National Dex number, so a component without exactly one row (or a row spanning components) is a hard error.
"""
from __future__ import annotations

import collections
import json
import re
import sys

from arch_matrix import parse_matrix
from base_source import all_base_maps, base_encounter
from common import (BASE_COMMIT, IMPL_DIR, LEGENDARY_DEX, SPECIES, dex, evolution_edges)
from manifest_io import dumps_compact

# Section 5 (USER APPROVAL REQUIRED) items -> decision keys. Claude must not choose these.
DECISIONS = {
    "STARTER_DISTRIBUTION": ["Bulbasaur", "Charmander", "Squirtle", "Chikorita", "Cyndaquil", "Totodile",
                              "Treecko", "Torchic", "Mudkip", "Turtwig", "Chimchar", "Piplup"],
    "FOSSIL_ACQUISITION": ["Omanyte", "Kabuto", "Aerodactyl", "Lileep", "Anorith", "Cranidos", "Shieldon"],
    "SPIRITOMB_QUEST": ["Spiritomb"],
    "ROTOM_UNLOCK_PRESENTATION": ["Rotom"],
    "TYROGUE_GIFT_VS_HABITAT": ["Tyrogue/Hitmons"],
    "HAPPINY_CHANSEY_GIFT_VS_HABITAT": ["Happiny/Chansey"],
    "EEVEE_GIFT_VS_WILD_BALANCE": ["Eevee"],
    "PORYGON_ACQUISITION_PRESENTATION": ["Porygon"],
    "RIOLU_REPEATABILITY": ["Riolu"],
    "CASTFORM_GIFT_VS_HABITAT": ["Castform"],
    "FEEBAS_IMPLEMENTATION": ["Feebas"],
}
LABEL_TO_DECISION = {lbl: key for key, lbls in DECISIONS.items() for lbl in lbls}
# Pseudo-legendary catch-up habitats are a separate USER_DECISION (secondary habitat only).
PSEUDO = ["Dratini", "Larvitar", "Bagon", "Gible", "Beldum"]

# Dependencies present in current source for decision families (left in place until the user decides).
KNOWN_CURRENT_DEPENDENCIES = {"feebas": ["RANDOM_TILE (elusive rod tile, current source)"],
                              "spiritomb": ["MULTIPLAYER (Underground interaction counter, current source)"]}
BONUS_KEYWORDS = [("Radar", "RADAR"), ("swarm", "SWARM"), ("Honey", "HONEY"), ("Marsh", "GREAT_MARSH"),
                  ("Garden", "TROPHY_GARDEN"), ("daily", "GREAT_MARSH")]


def norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower().replace("♀", "f").replace("♂", "m"))


def components() -> dict[str, list[str]]:
    par = {s: s for s in SPECIES[1:494]}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for a, b, _ in evolution_edges():
        if a in par and b in par:
            par[find(a)] = find(b)
    comps = collections.defaultdict(list)
    for s in SPECIES[1:494]:
        comps[find(s)].append(s)
    has_pre = {b for _, b, _ in evolution_edges()}
    # family root = lowest-dex species with no incoming evolution edge (the earliest stage)
    return {min((m for m in v if m not in has_pre), key=dex): sorted(v, key=dex) for v in comps.values()}


def resolve_entry_stages(text: str, members: list[str]) -> tuple[list[str], list[str]]:
    toks = [t for t in re.split(r",|/| or ", text) if t.strip()]
    found, unresolved = [], []
    names = {m: norm(m[len("SPECIES_"):]) for m in members}
    for t in toks:
        n = norm(t)
        hit = [m for m, nm in names.items() if n.startswith(nm) or nm == n]
        hit = sorted(hit, key=lambda m: -len(names[m]))[:1]
        if hit:
            found.append(hit[0])
        else:
            unresolved.append(t.strip())
    return found, unresolved


def legacy_sources() -> dict[str, list[dict]]:
    """Where each species can be met in *base* encounter data (before this work)."""
    from common import LAND_RATES, WATER_RATES, SLOT_ROLES
    src = collections.defaultdict(list)

    def add(sp, **kw):
        if sp != "SPECIES_NONE":
            src[sp].append(kw)

    for name in all_base_maps():
        j = base_encounter(name)
        if "land_encounters" in j and j["land_rate"]:
            for i, e in enumerate(j["land_encounters"]):
                add(e["species"], map=name, method="land", slot=i, role=SLOT_ROLES[i], rate=LAND_RATES[i])
            for arr, role in (("swarms", "swarm"), ("day", "time_day"), ("night", "time_night"), ("radar", "radar")):
                for i, sp in enumerate(j[arr]):
                    add(sp, map=name, method=arr, slot=i, role=role)
            for ver in ("ruby", "sapphire", "emerald", "firered", "leafgreen"):
                for i, sp in enumerate(j[ver]):
                    add(sp, map=name, method=f"dual_slot_{ver}", slot=i, role="dual_slot")
        for m in ("surf", "old_rod", "good_rod", "super_rod"):
            if j.get(f"{m}_rate"):
                for i, e in enumerate(j[f"{m}_encounters"]):
                    add(e["species"], map=name, method=m, slot=i, role="water", rate=WATER_RATES[m][i])
        if name == "honey_tree":
            for tier in ("common", "uncommon", "rare"):
                for i, sp in enumerate(j[tier]):
                    add(sp, map=name, method=f"honey_{tier}", slot=i, role="honey")
        if name == "trophy_garden":
            for i, sp in enumerate(j.get("daily_encounters", [])):
                add(sp, map=name, method="trophy_garden_daily", slot=i, role="garden_daily")
        if name == "great_marsh_lookout":
            for k in ("before_national_dex", "after_national_dex"):
                for i, sp in enumerate(j[k]):
                    add(sp, map=name, method=f"marsh_{k}", slot=i, role="marsh_daily")
        if "elusive_rod_encounter" in j:
            add(j["elusive_rod_encounter"]["species"], map=name, method="elusive_rod_tile", slot=0, role="random_tile")
    return src


def main() -> int:
    rows = parse_matrix()
    comps = components()
    fam_of = {s: root for root, mem in comps.items() for s in mem}
    row_of: dict[int, int] = {}
    for i, r in enumerate(rows):
        for d in r["dex"]:
            assert d not in row_of, f"dex {d} in two matrix rows"
            row_of[d] = i
    legacy = legacy_sources()

    families, problems = [], []
    used_rows = set()
    for root, mem in sorted(comps.items(), key=lambda kv: dex(kv[0])):
        dexes = [dex(s) for s in mem]
        leg = all(d in LEGENDARY_DEX for d in dexes)
        fid = root[len("SPECIES_"):].lower()
        legacy_src = sorted({(s["map"], s["method"]) for m in mem for s in legacy.get(m, [])})
        if leg:
            families.append({
                "family_id": fid, "components": mem, "dex": dexes,
                "classification": "LEGENDARY_OR_MYTHICAL", "availability_status": "RESERVED_LATER_PHASE",
                "earliest_progression_band": None, "acquisition_class": "RESERVED_LATER_PHASE",
                "entry_stage": [], "rarity_tier": None, "renewable_retry_safe": None,
                "special_system_bonus": [], "external_dependency_flags": [],
                "placement_confidence": "n/a", "user_decision_required": False, "user_decision_key": None,
                "note": "Legendary/Mythical quests are owned by the later phase; no wild placement here.",
            })
            continue
        ridx = {row_of.get(d) for d in dexes}
        if len(ridx) != 1 or None in ridx:
            problems.append(f"{fid}: matrix rows {ridx}")
            continue
        r = rows[ridx.pop()]
        used_rows.add(r["label"])
        stages, unresolved = resolve_entry_stages(r["entry_stage_text"], mem)
        if unresolved and "TBD" not in r["area"] and not stages:
            problems.append(f"{fid}: unresolved entry stage {unresolved}")
        decision = LABEL_TO_DECISION.get(r["label"])
        bonus = sorted({tag for kw, tag in BONUS_KEYWORDS if kw.lower() in (r["note"] + " " + r["area"]).lower()})
        deps = sorted({s["method"].split("_")[0] if s["method"].startswith(("dual_slot", "honey", "marsh")) else s["method"]
                       for m in mem for s in legacy.get(m, []) if s["role"] in
                       ("dual_slot", "radar", "swarm", "honey", "garden_daily", "marsh_daily", "random_tile")})
        # legacy flags: only report as *dependency* when species has no stable legacy route at all
        stable = [s for m in mem for s in legacy.get(m, [])
                  if s["role"] in ("fixed", "water", "time_day", "time_night") or s["role"] in ("swarm",) and False]
        stable_fixed = [s for s in stable if s["role"] in ("fixed", "water")]
        legacy_dependency = []
        if not stable_fixed and not decision:
            kinds = sorted({s["role"] for m in mem for s in legacy.get(m, [])})
            legacy_dependency = kinds or ["NO_LEGACY_WILD_ROUTE"]
        fam = {
            "family_id": fid, "label": r["label"], "components": mem, "dex": dexes,
            "classification": "NONLEGENDARY",
            "availability_status": "USER_DECISION_REQUIRED" if decision else "PLACE_WILD",
            "earliest_progression_band": r["earliest"],
            "origin_section": r["origin_section"],
            "area_system_text": r["area"],
            "acquisition_class": "SPECIAL_DECISION_REQUIRED" if decision else "WILD_FIXED",
            "entry_stage": stages, "entry_stage_text": r["entry_stage_text"],
            "rarity_tier": r["tier"], "pre_e4": r["pre_e4"] == "Y",
            "renewable_retry_safe": None if decision else True,
            "special_system_bonus": bonus,
            "external_dependency_flags": (["PENDING_USER_DECISION"] + KNOWN_CURRENT_DEPENDENCIES.get(fid, [])) if decision else [],
            "legacy_dependency_flags_in_base_source": legacy_dependency,
            "placement_confidence": r["confidence"],
            "user_decision_required": bool(decision),
            "user_decision_key": decision,
            "note": r["note"],
        }
        if r["label"] in PSEUDO:
            fam["secondary_catchup_habitat"] = "USER_DECISION_REQUIRED"
        families.append(fam)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    unused = [r["label"] for r in rows if r["label"] not in used_rows]
    if unused:
        print("matrix rows not matched to a component:", unused, file=sys.stderr)
        return 1

    out = {
        "schema": "availability_families/1",
        "base_commit": BASE_COMMIT,
        "authority": "docs/overhaul/AVAILABILITY_ARCHITECTURE.md (Pass 3 matrix); components from live evolution data",
        "note": ("Family components are connected components of res/pokemon/*/data.json evolution edges "
                 "(method-independent, so Pass A evolution-method changes cannot change membership)."),
        "decisions_unresolved": {k: v for k, v in DECISIONS.items()},
        "counts": {
            "families_total": len(families),
            "nonlegendary": sum(f["classification"] == "NONLEGENDARY" for f in families),
            "reserved_later_phase": sum(f["classification"] != "NONLEGENDARY" for f in families),
            "place_wild": sum(f.get("availability_status") == "PLACE_WILD" for f in families),
            "user_decision_required": sum(f.get("user_decision_required", False) for f in families),
        },
        "families": families,
    }
    path = IMPL_DIR / "availability_families.json"
    path.write_text(dumps_compact(out, line_arrays=("families",)))
    print(json.dumps(out["counts"]), "->", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
