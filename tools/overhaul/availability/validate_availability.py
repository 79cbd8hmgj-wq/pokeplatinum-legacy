#!/usr/bin/env python3
"""Availability validators (AVAILABILITY_ARCHITECTURE.md s.8).

  python3 tools/overhaul/availability/validate_availability.py [--state manifest|live] [--json report.json]

--state manifest  base commit + wild_encounters.json + special_systems.json applied in memory (pre-apply proof)
--state live      the encounter JSON files currently in the working tree (post-apply proof)
Exit status is non-zero if any FAIL is reported.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys

from base_source import base_encounter
from common import (BANDS, IMPL_DIR, LAND_RATES, LEGENDARY_DEX, PRE_E4_BANDS, REQUIRED_MIN_RATE, SPECIES,
                    SPECIES_ID, WATER_RATES, ZONES, dex, evolution_edges)
from paths import METHOD_MIN_BAND, TIME_STATES, collect_paths
from state import VERSIONS, WATER_METHODS, base_state, live_state, load_manifest, manifest_state
from zone_index import zone_index
from zones_data import ADJACENT, DENSITY_NOTES

FAIL, WARN, INFO = [], [], []


def fail(code, msg):
    FAIL.append(f"[{code}] {msg}")


def warn(code, msg):
    WARN.append(f"[{code}] {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", choices=["manifest", "live"], default="manifest")
    ap.add_argument("--json")
    args = ap.parse_args()

    fam_doc = load_manifest("availability_families.json")
    wild = load_manifest("wild_encounters.json")
    special = load_manifest("special_systems.json")
    zones = load_manifest("encounter_zones.json")
    fams = fam_doc["families"]
    fam_by_id = {f["family_id"]: f for f in fams}
    fam_of = {s: f for f in fams for s in f["components"]}
    st = manifest_state(check=True) if args.state == "manifest" else live_state()
    base = base_state()
    zidx = zone_index(wild)

    # ---------------- V1 manifest syntax / vocabulary ----------------
    for e in wild["entries"]:
        if e["species"] not in SPECIES_ID or e["species"] == "SPECIES_NONE":
            fail("V1", f"bad species {e['species']}")
        if e["band"] not in BANDS or e["zone"] not in ZONES:
            fail("V1", f"bad band/zone on {e['map']}:{e['method']}[{e['slot']}]")
        if not (1 <= e["level_min"] <= e["level_max"] <= 100):
            fail("V1", f"bad level {e}")
        if dex(e["species"]) in LEGENDARY_DEX:
            fail("V12", f"legendary/mythical species placed: {e['species']} @ {e['map']}")
        if e["rate_pct"] != (LAND_RATES[e["slot"]] if e["method"].startswith("land") else WATER_RATES[e["method"]][e["slot"]]):
            fail("V1", f"rate_pct mismatch {e['map']}:{e['method']}[{e['slot']}]")
    for n, m in wild["maps"].items():
        z = zones["maps"].get(n)
        if not z or (z["zone"], z["band"]) != (m["zone"], m["band"]):
            fail("V2", f"zone manifest disagrees with wild manifest for {n}")
    for n in base:
        if n not in zones["maps"]:
            fail("V2", f"{n} missing from encounter_zones.json")

    # ---------------- V3 family components from live evolution data ----------------
    par = {s: s for s in SPECIES[1:494]}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    edges = [(a, b) for a, b, _ in evolution_edges() if a in par and b in par]
    for a, b in edges:
        par[find(a)] = find(b)
    comp = collections.defaultdict(set)
    for s in SPECIES[1:494]:
        comp[find(s)].add(s)
    manifest_comps = {frozenset(f["components"]) for f in fams}
    if {frozenset(c) for c in comp.values()} != manifest_comps:
        fail("V3", "family components in availability_families.json differ from live evolution data")
    expected = {
        "nincada": {"NINCADA", "NINJASK", "SHEDINJA"},
        "eevee": {"EEVEE", "VAPOREON", "JOLTEON", "FLAREON", "ESPEON", "UMBREON", "LEAFEON", "GLACEON"},
        "clamperl": {"CLAMPERL", "HUNTAIL", "GOREBYSS"},
        "tyrogue": {"TYROGUE", "HITMONLEE", "HITMONCHAN", "HITMONTOP"},
        "ralts": {"RALTS", "KIRLIA", "GARDEVOIR", "GALLADE"},
        "snorunt": {"SNORUNT", "GLALIE", "FROSLASS"},
        "burmy": {"BURMY", "WORMADAM", "MOTHIM"},
        "combee": {"COMBEE", "VESPIQUEN"},
        "wurmple": {"WURMPLE", "SILCOON", "CASCOON", "BEAUTIFLY", "DUSTOX"},
        "pichu": {"PICHU", "PIKACHU", "RAICHU"},
        "azurill": {"AZURILL", "MARILL", "AZUMARILL"},
        "wynaut": {"WYNAUT", "WOBBUFFET"},
        "mime_jr": {"MIME_JR", "MR_MIME"}, "happiny": {"HAPPINY", "CHANSEY", "BLISSEY"},
        "munchlax": {"MUNCHLAX", "SNORLAX"}, "riolu": {"RIOLU", "LUCARIO"}, "mantyke": {"MANTYKE", "MANTINE"},
        "budew": {"BUDEW", "ROSELIA", "ROSERADE"}, "chingling": {"CHINGLING", "CHIMECHO"},
        "slowpoke": {"SLOWPOKE", "SLOWBRO", "SLOWKING"}, "poliwag": {"POLIWAG", "POLIWHIRL", "POLIWRATH", "POLITOED"},
        "onix": {"ONIX", "STEELIX"}, "scyther": {"SCYTHER", "SCIZOR"}, "porygon": {"PORYGON", "PORYGON2", "PORYGON_Z"},
        "electabuzz": None,
    }
    for fid, members in expected.items():
        if members is None:
            continue
        f = fam_by_id.get(fid)
        got = {s[8:] for s in f["components"]} if f else set()
        if got != members:
            fail("V3", f"family {fid}: expected {sorted(members)}, got {sorted(got)}")
    if ("SPECIES_NINCADA", "SPECIES_SHEDINJA") not in {(a, b) for a, b in edges}:
        fail("V3", "Nincada -> Shedinja edge missing from evolution data")

    # ---------------- V4 acquisition paths ----------------
    allp = collect_paths(st)
    mapband = {n: m["band"] for n, m in zidx.items()}

    def pband(p):
        b = mapband.get(p.map, "P1")
        g = METHOD_MIN_BAND.get(p.method)
        return g if g and BANDS.index(g) > BANDS.index(b) else b
    by_family = collections.defaultdict(list)
    for p in allp:
        f = fam_of.get(p.species)
        if f:
            by_family[f["family_id"]].append(p)
    verified, report_fam = 0, {}
    tier_min = {"C": 20, "U": 10, "R": 5, "S": 0, "R/U": 5, "U/R": 5, "S/R": 5, "S/U": 5, "R/S": 5}
    tier_warn = []
    for f in fams:
        fid = f["family_id"]
        if f["classification"] != "NONLEGENDARY":
            report_fam[fid] = "RESERVED_LATER_PHASE"
            continue
        if f["user_decision_required"]:
            report_fam[fid] = f"USER_DECISION_REQUIRED:{f['user_decision_key']}"
            continue
        ok_all = [p for p in by_family[fid] if pband(p) in PRE_E4_BANDS and p.min_rate >= REQUIRED_MIN_RATE]
        ok = [p for p in ok_all if not p.safari]
        if not ok_all:
            fail("V4", f"family {fid}: no stable (>=5% in every time state) PRE_E4 wild path")
            report_fam[fid] = "NO_PATH"
            continue
        if not ok:
            fail("V4", f"family {fid}: only Great Marsh (Safari-format) paths; needs a non-Safari fixed path")
            report_fam[fid] = "SAFARI_ONLY"
            continue
        verified += 1
        best = max(ok, key=lambda p: p.min_rate)
        earliest = min(ok, key=lambda p: (BANDS.index(pband(p)), -p.min_rate))
        report_fam[fid] = f"{earliest.map}:{earliest.method} {earliest.min_rate}% {pband(earliest)}"
        if best.min_rate < tier_min.get(f["rarity_tier"], 5):
            tier_warn.append(f"{fid}({f['rarity_tier']} best {best.min_rate}%)")
        # earliest band vs matrix: must not appear *earlier* than the approved earliest band
        if BANDS.index(pband(earliest)) < BANDS.index(f["earliest_progression_band"]):
            fail("V4", f"family {fid}: placed in {pband(earliest)} earlier than matrix earliest {f['earliest_progression_band']}")
        # no PRE_E4 requirement may rely on Super Rod
    if tier_warn:
        warn("V5", f"{len(tier_warn)} families whose best stable rate is below their rarity-tier floor: " + ", ".join(tier_warn))

    # ---------------- V6 decision families untouched ----------------
    def occurrences(state, species_set):
        occ = set()
        for n, j in state.items():
            if "land_encounters" in j:
                for i, e in enumerate(j["land_encounters"]):
                    if e["species"] in species_set:
                        occ.add((n, "land", i))
                for key in ("day", "night", "radar", "swarms"):
                    for i, s in enumerate(j[key]):
                        if s in species_set:
                            occ.add((n, key, i))
            for m in WATER_METHODS:
                if f"{m}_encounters" in j:
                    for i, e in enumerate(j[f"{m}_encounters"]):
                        if e["species"] in species_set:
                            occ.add((n, m, i))
            if "elusive_rod_encounter" in j and j["elusive_rod_encounter"]["species"] in species_set:
                occ.add((n, "elusive_rod", 0))
        return occ
    dec_species = {s for f in fams if f.get("user_decision_required") for s in f["components"]}
    if occurrences(base, dec_species) != occurrences(st, dec_species):
        diff = occurrences(base, dec_species) ^ occurrences(st, dec_species)
        fail("V6", f"USER_DECISION_REQUIRED species occurrences changed: {sorted(diff)[:10]}")

    # ---------------- V7 external dependencies ----------------
    for n, j in st.items():
        if "land_encounters" in j and j.get("land_rate"):
            mirror = [j["land_encounters"][8]["species"], j["land_encounters"][9]["species"]]
            for v in VERSIONS:
                if j[v] != mirror:
                    fail("V7", f"{n}: dual-slot array '{v}' still differs from slots 8/9 (cartridge state can change the table)")
    gm = st["great_marsh_lookout"]
    if gm["before_national_dex"] != gm["after_national_dex"]:
        fail("V7", "Great Marsh before/after National Dex arrays differ (Dex still gates Marsh content)")
    for sysname in ("radar", "swarm"):
        for n, rec in special[sysname]["maps"].items():
            for ent in rec["entries"]:
                if ent["fallback"] in ("NO_FALLBACK", "UNKNOWN_SPECIES"):
                    fail("V7", f"{sysname} {n}: {ent['species']} has no fixed fallback")
    for sec in ("honey", "trophy_garden", "great_marsh", "dual_slot"):
        def walk(o):
            if isinstance(o, dict):
                if o.get("fallback") in ("NO_FALLBACK", "UNKNOWN_SPECIES"):
                    fail("V7", f"{sec}: {o.get('species')} has no fixed fallback")
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(special[sec])
    # every fallback pointer must resolve to a live path
    pathset = {(p.map, p.method, p.species): p for p in allp}
    for sec in ("radar", "swarm", "honey", "trophy_garden", "great_marsh", "dual_slot"):
        def walk2(o):
            if isinstance(o, dict):
                fb = o.get("fallback")
                if isinstance(fb, dict):
                    p = pathset.get((fb["map"], fb["method"], fb["species"]))
                    if p is None or p.min_rate < REQUIRED_MIN_RATE:
                        fail("V7", f"{sec}: stale fallback {fb}")
                for v in o.values():
                    walk2(v)
            elif isinstance(o, list):
                for v in o:
                    walk2(v)
        walk2(special[sec])

    # ---------------- V8 density ----------------
    caps = {"ordinary": 8, "connector": 5, "signature": 9}
    fam_sets = {}
    for n, m in wild["maps"].items():
        j = st[n]
        kind = m["kind"]
        sp = set()
        if j.get("land_rate"):
            sp = {e["species"] for e in j["land_encounters"]} | set(j["day"]) | set(j["night"])
            used = {fam_of[s]["family_id"] for s in sp if s in fam_of}
            fam_sets[n] = used
            cap = caps.get(kind, 8)
            if len(used) > cap and n not in DENSITY_NOTES:
                fail("V8", f"{n}: {len(used)} land families > {cap} ({kind})")
            if kind == "ordinary" and len(used) < 6:
                warn("V8", f"{n}: only {len(used)} land families (ordinary target 6-8)")
            if kind == "connector" and len(used) < 4:
                warn("V8", f"{n}: only {len(used)} land families (connector target 4-5)")
        for meth in WATER_METHODS:
            if j.get(f"{meth}_rate"):
                used = {fam_of[e["species"]]["family_id"] for e in j[f"{meth}_encounters"] if e["species"] in fam_of}
                if len(used) > 4:
                    fail("V8", f"{n}:{meth}: {len(used)} water families > 4")
    for a, b, cont in ADJACENT:
        if a in fam_sets and b in fam_sets and not cont:
            inter = len(fam_sets[a] & fam_sets[b])
            small = min(len(fam_sets[a]), len(fam_sets[b]))
            if inter > small / 2:
                warn("V8", f"adjacent {a} / {b} share {inter}/{small} families (>50%) but are not marked continuous")

    # ---------------- V9 scope / stage policy ----------------
    has_in = {b for _, b in edges}
    has_out = {a for a, _ in edges}
    evolved_in_tables = collections.Counter()
    for e in wild["entries"]:
        s = e["species"]
        if s in has_in:
            evolved_in_tables["final" if s not in has_out else "middle"] += 1
    INFO.append(f"evolved-species entries in authored tables: {dict(evolved_in_tables)} of {len(wild['entries'])}")

    # ---------------- V10 reachability of every species from a placed member ----------------
    fwd = collections.defaultdict(set)
    for a, b in edges:
        fwd[a].add(b)
    breed_only, unreachable = [], []
    for f in fams:
        if f["classification"] != "NONLEGENDARY" or f["user_decision_required"]:
            continue
        placed = {p.species for p in by_family[f["family_id"]] if pband(p) in PRE_E4_BANDS and p.min_rate >= 5 and not p.safari}
        reach = set(placed)
        stack = list(placed)
        while stack:
            x = stack.pop()
            for y in fwd[x]:
                if y not in reach:
                    reach.add(y)
                    stack.append(y)
        for s in f["components"]:
            if s not in reach:
                (breed_only if s not in has_in else unreachable).append(s[8:])
    # roots not placed are baby species obtained by breeding the evolved form (no-incense rule belongs to the breeding port)
    for s in unreachable:
        fail("V10", f"{s} is neither placed nor reachable by evolution from a placed family member")
    INFO.append(f"baby/root species obtained by breeding a placed family member: {sorted(breed_only)}")

    # ---------------- V11 493 coverage ----------------
    cov = collections.Counter()
    for f in fams:
        for s in f["components"]:
            cov[report_fam[f["family_id"]].split(":")[0] if not report_fam[f["family_id"]][0].isdigit() else "x"] += 1
    status = collections.Counter()
    for f in fams:
        r = report_fam[f["family_id"]]
        key = "RESERVED_LATER_PHASE" if r.startswith("RESERVED") else "USER_DECISION_REQUIRED" if r.startswith("USER") else \
            "NO_PATH" if r == "NO_PATH" else "WILD_PRE_E4"
        status[key] += len(f["components"])
    if sum(status.values()) != 493:
        fail("V11", f"species coverage sums to {sum(status.values())}, expected 493")
    INFO.append(f"species coverage (of 493): {dict(status)}")
    INFO.append(f"nonlegendary families with a verified deterministic pre-E4 wild path: {verified}")
    INFO.append(f"USER_DECISION_REQUIRED families: {sum(1 for f in fams if f.get('user_decision_required'))}")

    print(f"state={args.state}  families={len(fams)}  wild entries={len(wild['entries'])}  maps={len(wild['maps'])}")
    for line in INFO:
        print("INFO", line)
    for w in WARN:
        print("WARN", w)
    for f in FAIL:
        print("FAIL", f)
    print(f"RESULT: {len(FAIL)} failure(s), {len(WARN)} warning(s)")
    if args.json:
        json.dump({"fail": FAIL, "warn": WARN, "info": INFO, "families": report_fam, "verified_families": verified},
                  open(args.json, "w"), indent=2)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
