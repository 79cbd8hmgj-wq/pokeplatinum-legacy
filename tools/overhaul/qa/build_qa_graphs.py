#!/usr/bin/env python3
"""D7 canonical completion graphs (Pokédex 493, evolution, event dependency, progression gates).

Reads LIVE source (res/pokemon/*/data.json, include/data/mart_items.h, generated/species.txt) plus the locked
availability / special-acquisition / D5 event manifests, writes four deterministic JSON artifacts under
docs/overhaul/qa/, and fails (exit 1) on any completion-proof violation.

    python3 tools/overhaul/qa/build_qa_graphs.py            # regenerate + validate
    python3 tools/overhaul/qa/build_qa_graphs.py --check    # validate + require committed artifacts are current

Nothing here marks Pokédex entries or edits saves: a species counts only when a manifest-declared, source-validated
acquisition path (wild / scripted gift / event / breeding / evolution) reaches it. Output carries no timestamps or
commit hashes so reruns are byte-stable.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
IMPL = "docs/overhaul/implementation"
QA = "docs/overhaul/qa"
OUT = {"pokedex": "pokedex_493_graph.json", "evolution": "evolution_graph.json",
       "events": "event_dependency_graph.json", "gates": "progression_gates.json"}

# AVAILABILITY_ARCHITECTURE.md s1 band table (order is the progression order).
BANDS = [("E0", "start-Oreburgh"), ("E1", "Oreburgh-Eterna"), ("M1", "Eterna-Pastoria"), ("M2", "Pastoria-Canalave"),
         ("L1", "Canalave-Snowpoint"), ("L2", "Snowpoint-eighth badge"), ("P0", "eighth badge-Elite Four"),
         ("P1", "Hall of Fame onward")]
BAND_IDX = {b: i for i, (b, _) in enumerate(BANDS)}
PRE_E4 = {b for b, _ in BANDS if b != "P1"}
STONES = ["ITEM_FIRE_STONE", "ITEM_WATER_STONE", "ITEM_THUNDERSTONE", "ITEM_LEAF_STONE", "ITEM_MOON_STONE",
          "ITEM_SUN_STONE", "ITEM_SHINY_STONE", "ITEM_DUSK_STONE", "ITEM_DAWN_STONE"]
STONE_BAND = "M1"  # Veilstone Dept. Store 2F (4th Gym city) sits in Eterna-Pastoria; economy_manifest.evolution_stone_shop.gate
FORBIDDEN_EVO = {"EVO_TRADE", "EVO_TRADE_WITH_HELD_ITEM", "EVO_LEVEL_WITH_HELD_ITEM_DAY", "EVO_LEVEL_WITH_HELD_ITEM_NIGHT"}
# Non-item evolution requirements and the in-save mechanism that satisfies them.
LOCATION_EVOS = {"EVO_LEVEL_MAGNETIC_FIELD": "Mt. Coronet magnetic field map (native)",
                 "EVO_LEVEL_MOSS_ROCK": "Moss Rock, Eterna Forest (native)", "EVO_LEVEL_ICE_ROCK": "Ice Rock, Route 217 (native)"}
NATIVE_EVOS = {"EVO_LEVEL": "level", "EVO_LEVEL_HAPPINESS": "friendship", "EVO_LEVEL_HAPPINESS_DAY": "friendship+day",
               "EVO_LEVEL_HAPPINESS_NIGHT": "friendship+night", "EVO_LEVEL_BEAUTY": "beauty (Pokéblock/Poffin)",
               "EVO_LEVEL_MALE": "level+male", "EVO_LEVEL_FEMALE": "level+female", "EVO_LEVEL_PID_LOW": "level+PID",
               "EVO_LEVEL_PID_HIGH": "level+PID", "EVO_LEVEL_NINJASK": "level", "EVO_LEVEL_SHEDINJA": "level+empty slot+Poké Ball",
               "EVO_LEVEL_ATK_GT_DEF": "level+stat", "EVO_LEVEL_ATK_EQ_DEF": "level+stat", "EVO_LEVEL_ATK_LT_DEF": "level+stat",
               "EVO_LEVEL_SPATK_GT_ATK": "level+stat", "EVO_LEVEL_SPATK_GE_ATK": "level+stat", "EVO_LEVEL_ATK_GT_SPATK": "level+stat",
               "EVO_LEVEL_SPDEF_GT_DEF": "level+stat", "EVO_LEVEL_NIGHT": "level+night", "EVO_LEVEL_DAY": "level+day"}
ITEM_EVOS = {"EVO_USE_ITEM", "EVO_USE_ITEM_MALE", "EVO_USE_ITEM_FEMALE"}
# Wild families with no entry in wild_encounters.json because the vanilla source is retained and validated untouched
# (AVAILABILITY_SOURCE_AUDIT.md: Unown forms untouched; Solaceon Ruins, M1).
VANILLA_RETAINED_WILD = {"unown": "Solaceon Ruins (vanilla table untouched, AVAILABILITY_SOURCE_AUDIT.md)"}
ALLOWED_EVENT_CLASSES = {"NATIVE_STATIC", "NATIVE_ROAMER", "NATIVE_RUIN", "RESTORED_EVENT", "BREEDING_ONLY",
                         "RARE_POSTGAME_HABITAT", "HIDDEN_MYTHICAL_STATIC", "NON_LEGENDARY_EVENT_INFRASTRUCTURE"}
EXTERNAL_WORDS = re.compile(r"\b(trade|wfc|wi-?fi|multiplayer|slot-?2|gba cartridge|nintendo wfc|other game|mystery gift)\b", re.I)


def jl(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def dumps(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def species_names():
    """id -> SPECIES_* for #001-#493 (generated/species.txt: line index == species id, line 0 is SPECIES_NONE)."""
    with open(os.path.join(ROOT, "generated/species.txt"), encoding="utf-8") as f:
        names = [l.strip() for l in f if l.strip()]
    if names[1] != "SPECIES_BULBASAUR" or names[493] != "SPECIES_ARCEUS":
        raise SystemExit("FAIL generated/species.txt layout unexpected")
    return {i: names[i] for i in range(1, 494)}


def load_live(names):
    """species -> {dir, evolutions, offspring, egg_groups, gender, learn}"""
    live = {}
    for p in glob.glob(os.path.join(ROOT, "res/pokemon/*/data.json")):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        live[os.path.basename(os.path.dirname(p))] = d
    # dir -> species: dir name is the lowercase species suffix (minor aliasing handled via name normalisation)
    norm = {re.sub(r"[^a-z0-9]", "", k): k for k in live}
    out = {}
    for sid, sp in names.items():
        key = re.sub(r"[^a-z0-9]", "", sp[len("SPECIES_"):].lower())
        if key not in norm:
            raise SystemExit(f"FAIL no res/pokemon dir for {sp}")
        out[sp] = live[norm[key]] | {"_dir": norm[key]}
    return out


def families_from_edges(names, live):
    parent = {s: s for s in names.values()}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for sp, d in live.items():
        for e in d.get("evolutions", []):
            tgt = e[-1]
            if tgt in parent:
                parent[find(tgt)] = find(sp)
        off = d.get("offspring")
        if off in parent and off != sp:
            parent[find(off)] = find(sp)
    return {s: find(s) for s in parent}


def mart_has_stones():
    with open(os.path.join(ROOT, "include/data/mart_items.h"), encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"VeilstoneDeptStoreStock_2F_MID\[\]\s*=\s*\{(.*?)\};", src, re.S)
    body = m.group(1) if m else ""
    return {s: (s in body) for s in STONES}


def build():
    errors, notes, drift = [], [], {}
    names = species_names()
    assert len(names) == 493, len(names)
    live = load_live(names)
    fam_root = families_from_edges(names, live)
    fam_manifest = jl(f"{IMPL}/availability_families.json")["families"]
    spec_acq = jl(f"{IMPL}/special_acquisitions.json")
    wild = jl(f"{IMPL}/wild_encounters.json")
    nat = jl(f"{IMPL}/events/native_legendary_events.json")["events"]
    leg = jl(f"{IMPL}/events/legacy_legendary_encounters.json")["encounters"]
    myth = jl(f"{IMPL}/events/mythical_statics.json")["statics"]
    stone_shop = mart_has_stones()
    for s, ok in stone_shop.items():
        if not ok:
            errors.append(f"evolution stone {s} missing from VeilstoneDeptStoreStock_2F_MID (renewable pre-E4 source)")

    sp_to_fam = {c: f for f in fam_manifest for c in f["components"]}
    wild_by_fam = {}
    for e in wild["entries"]:
        wild_by_fam.setdefault(e["family_id"], []).append(e)
    event_by_sp = {e["species"]: ("native", e) for e in nat}
    event_by_sp |= {e["species"]: ("legacy_habitat", e) for e in leg}
    event_by_sp |= {e["species"]: ("mythical_static", e) for e in myth}

    # ---- evolution edges (live source) ----
    edges, evo_in = [], {}
    for sp, d in sorted(live.items(), key=lambda kv: kv[0]):
        for idx, e in enumerate(d.get("evolutions", [])):
            method, tgt = e[0], e[-1]
            args = e[1:-1]
            rec = {"from": sp, "to": tgt, "method": method, "args": args, "index": idx}
            if method in FORBIDDEN_EVO:
                rec["requirement"] = "FORBIDDEN"
                errors.append(f"{sp}->{tgt}: forbidden evolution method {method} (trade/held-item)")
            elif method in ITEM_EVOS:
                item = args[0]
                rec["requirement"] = f"item:{item}"
                if item in STONES and stone_shop.get(item):
                    rec["gate"], rec["item_source"] = STONE_BAND, "Veilstone Dept. Store 2F (renewable, pre-E4)"
                else:
                    errors.append(f"{sp}->{tgt}: evolution item {item} is not a renewable pre-E4 stone")
            elif method in LOCATION_EVOS:
                rec["requirement"], rec["gate"] = LOCATION_EVOS[method], "native-location"
            elif method == "EVO_LEVEL_KNOW_MOVE":
                mv = args[0]
                d2 = live[sp]
                ls = {m for _, m in d2["learnset"]["by_level"]} | set(d2["learnset"].get("by_tutor", [])) | \
                    set(d2["learnset"].get("egg_moves", []))
                rec["requirement"] = f"know:{mv}"
                if mv in ls:
                    how = [k for k, v in (("level-up", {m for _, m in d2["learnset"]["by_level"]}),
                                          ("tutor", set(d2["learnset"].get("by_tutor", []))),
                                          ("egg", set(d2["learnset"].get("egg_moves", [])))) if mv in v]
                    rec["move_source"] = how
                else:
                    errors.append(f"{sp}->{tgt}: move-known evolution needs {mv} but {sp} has no level/tutor/egg source")
            elif method == "EVO_LEVEL_SPECIES_IN_PARTY":
                rec["requirement"] = f"party:{args[0]}"
                rec["party_species"] = args[0]
            elif method in NATIVE_EVOS:
                rec["requirement"] = NATIVE_EVOS[method]
            else:
                errors.append(f"{sp}->{tgt}: unclassified evolution method {method}")
            if tgt not in names.values():
                errors.append(f"{sp}: evolution target {tgt} is not a #001-#493 species")
            edges.append(rec)
            evo_in.setdefault(tgt, []).append(rec)

    # ---- acquisition entry points ----
    entry, source_info = set(), {}
    for sp in names.values():
        fam = sp_to_fam.get(sp)
        if fam is None:
            errors.append(f"{sp}: not in availability_families.json")
            continue
        fid, status = fam["family_id"], fam["availability_status"]
        is_entry = sp in fam["entry_stage"]
        info = {"family_id": fid, "family_status": status, "entry_stage": is_entry,
                "external_dependency_flags": list(fam.get("external_dependency_flags", []))}
        if fam["classification"] == "NONLEGENDARY":
            if status == "PLACE_WILD":
                ents = wild_by_fam.get(fid, [])
                if ents:
                    bmin = min(ents, key=lambda e: BAND_IDX[e["band"]])["band"]
                    info["source"] = "wild"
                    info["methods"] = sorted({e["method"] for e in ents})
                    info["min_rate_pct"] = min(e["rate_pct"] for e in ents)
                    info["max_rate_pct"] = max(e["rate_pct"] for e in ents)
                    info["earliest_band"] = bmin
                    if bmin != fam["earliest_progression_band"]:
                        drift[fid] = {"live_wild_earliest": bmin, "family_manifest_band": fam["earliest_progression_band"]}
                elif fid in VANILLA_RETAINED_WILD:
                    info["source"], info["earliest_band"] = "wild", fam["earliest_progression_band"]
                    info["methods"], info["vanilla_retained"] = ["land"], VANILLA_RETAINED_WILD[fid]
                else:
                    errors.append(f"{sp}: PLACE_WILD family {fid} has no wild entry")
                    info["earliest_band"] = None
            elif status == "SPECIAL_ACQUISITION":
                key = fam["special_acquisition_key"]
                info["source"], info["special_key"] = "special_acquisition", key
                info["earliest_band"] = fam["earliest_progression_band"]
            else:
                errors.append(f"{sp}: nonlegendary family {fid} has status {status}")
        else:
            ev = event_by_sp.get(sp)
            if ev:
                kind, rec = ev
                info["source"], info["event_class"] = "legendary_event", rec["acquisition_class"]
                info["earliest_band"] = "P1" if rec.get("hall_of_fame_required") or kind in ("legacy_habitat", "mythical_static") else None
                if rec["acquisition_class"] not in ALLOWED_EVENT_CLASSES:
                    errors.append(f"{sp}: unexpected event class {rec['acquisition_class']}")
                ext = rec.get("external_dependency_removed", "")
                blob = json.dumps(rec.get("target_gates", [])) + str(rec.get("map_system", ""))
                if EXTERNAL_WORDS.search(blob):
                    errors.append(f"{sp}: event gates mention an external dependency: {blob[:80]}")
            elif sp == "SPECIES_PHIONE":
                info["source"] = "breeding"
            else:
                errors.append(f"{sp}: legendary/mythical species has no D5 event source")
        info["is_acquisition_entry"] = is_entry
        source_info[sp] = info
        if info.get("source") and (is_entry or fam["classification"] != "NONLEGENDARY"):
            entry.add(sp)

    # ---- reachability closure (evolution + breeding), one save ----
    reach = set(entry)
    changed = True
    while changed:
        changed = False
        for sp, d in live.items():
            if sp in reach:
                continue
            via = None
            for rec in evo_in.get(sp, []):
                item_ok = not rec["requirement"].startswith("item:") or "gate" in rec
                if rec["from"] in reach and rec["requirement"] != "FORBIDDEN" and item_ok:
                    if rec.get("party_species") and rec["party_species"] not in reach:
                        continue
                    via = ("evolution", rec["from"])
                    break
            if via is None:
                # baby stage obtained by breeding a reachable family member (Day Care)
                for other, d2 in live.items():
                    if other in reach and d2.get("offspring") == sp and other != sp \
                            and "EGG_GROUP_UNDISCOVERED" not in d2.get("egg_groups", []):
                        via = ("breeding", other)
                        break
            if via is None and source_info.get(sp, {}).get("source") == "breeding":
                if "SPECIES_MANAPHY" in reach:
                    via = ("breeding", "SPECIES_MANAPHY")
            if via:
                reach.add(sp)
                source_info[sp].setdefault("derived_via", []).append({"kind": via[0], "from": via[1]})
                changed = True
    for sp in names.values():
        if sp not in reach:
            errors.append(f"{sp}: unreachable in one save")

    # ---- family-level checks ----
    fam_members = {}
    for sp, r in fam_root.items():
        fam_members.setdefault(r, []).append(sp)
    fam_summary = []
    for fam in fam_manifest:
        fid = fam["family_id"]
        if fam["classification"] != "NONLEGENDARY":
            continue
        comps = [c for c in fam["components"]]
        bands = {source_info[c].get("earliest_band") for c in comps if source_info[c].get("is_acquisition_entry")}
        bands.discard(None)
        eb = min(bands, key=lambda b: BAND_IDX[b]) if bands else None
        if eb is None or eb not in PRE_E4:
            errors.append(f"family {fid}: no deterministic pre-Elite Four entry (band {eb})")
        wild_ents = wild_by_fam.get(fid, [])
        if fam["availability_status"] == "PLACE_WILD" and fid not in VANILLA_RETAINED_WILD:
            sole = [e for e in wild_ents if not e["bonus_system"] and e["method"] != "super_rod"]
            if not sole:
                errors.append(f"family {fid}: only postgame/bonus-system wild sources")
        # live family == manifest family
        roots = {fam_root[c] for c in comps}
        if len(roots) != 1:
            errors.append(f"family {fid}: live evolution components split across {sorted(roots)}")
        fam_summary.append({"family_id": fid, "entry_band": eb, "members": comps})

    # ---- Pokédex graph artifact ----
    dex = []
    for sid, sp in sorted(names.items()):
        d = live[sp]
        info = source_info.get(sp, {})
        dex.append({
            "dex": sid, "species": sp, "family_id": info.get("family_id"),
            "acquisition": {k: v for k, v in info.items() if k not in ("family_id", "family_status", "external_dependency_flags")},
            "family_status": info.get("family_status"),
            "evolves_from": sorted({r["from"] for r in evo_in.get(sp, [])}),
            "evolves_to": sorted({e[-1] for e in d.get("evolutions", [])}),
            "evolution_requirements": [r["requirement"] for r in evo_in.get(sp, [])],
            "breeding_dependency": any(x.get("kind") == "breeding" for x in info.get("derived_via", [])),
            "external_dependency_flags": info.get("external_dependency_flags", []),
            "form_note": "Unown/Rotom/Shaymin/Giratina/Deoxys forms are collection extras, not separate completion entries"
            if sp in ("SPECIES_UNOWN", "SPECIES_ROTOM", "SPECIES_SHAYMIN", "SPECIES_GIRATINA", "SPECIES_DEOXYS") else None,
            "reachable_in_one_save": sp in reach,
        })
    pokedex = {"schema": "pokeplatinum-overhaul/d7-pokedex-493-graph/v1",
               "method": "reachability closure over entry points (wild/special/event) + live evolution edges + Day Care offspring; "
                         "no save editing or Pokédex-bit injection counted",
               "summary": {"species": 493, "reachable": sum(1 for x in dex if x["reachable_in_one_save"]),
                           "nonlegendary_families": len(fam_summary),
                           "legendary_or_mythical_species": sum(1 for x in dex if x["acquisition"].get("source") in ("legendary_event", "breeding") and x["family_status"] == "RESERVED_LATER_PHASE"),
                           "external_dependencies": sum(1 for x in dex if x["external_dependency_flags"])},
               "arceus_capstone": "SPECIES_ARCEUS #493 requires caught #001-#492 (CheckPokedexCaughtAllButArceus); no other species depends on it",
               "species": dex, "families": fam_summary}

    # ---- evolution graph artifact ----
    evolution = {"schema": "pokeplatinum-overhaul/d7-evolution-graph/v1",
                 "stones": {s: {"vendor": "Veilstone Dept. Store 2F", "in_live_stock": stone_shop[s]} for s in STONES},
                 "summary": {"edges": len(edges), "forbidden": sum(1 for e in edges if e["requirement"] == "FORBIDDEN"),
                             "item_edges": sum(1 for e in edges if e["requirement"].startswith("item:")),
                             "move_known_edges": sum(1 for e in edges if e["requirement"].startswith("know:")),
                             "trade_or_held_item_edges": sum(1 for e in edges if e["method"] in FORBIDDEN_EVO)},
                 "edges": edges}

    # ---- event dependency graph ----
    nodes, dep = {}, []

    def node(n, kind):
        nodes.setdefault(n, kind)

    node("FLAG_GAME_COMPLETED", "gate")
    node("NATIONAL_DEX", "gate")
    dep.append(("NATIONAL_DEX", "FLAG_GAME_COMPLETED"))
    for ev in nat + leg + myth:
        sp = ev["species"]
        node(sp, "species_event")
        if ev.get("hall_of_fame_required") or "FLAG_GAME_COMPLETED" in json.dumps(ev.get("target_gates", [])):
            dep.append((sp, "FLAG_GAME_COMPLETED"))
        gates = json.dumps(ev.get("target_gates", []))
        if "National Dex" in gates:
            dep.append((sp, "NATIONAL_DEX"))
        for g in sorted(set(re.findall(r"FLAG_WOKE_UP_[A-Z_]+", gates))):
            node(g, "gate")
            dep.append((sp, g))
        for p in ev.get("internal_prerequisites", []):
            dep.append((sp, p))
        us = ev.get("unlock_source")
        if us:
            node(us["item"], "item")
            dep.append((sp, us["item"]))
            if us.get("command") == "CheckPokedexCaughtAllButArceus":
                node("DEX_001_492_CAUGHT", "gate")
                dep.append((sp, "DEX_001_492_CAUGHT"))
    if any(e["species"] == "SPECIES_SHAYMIN" for e in nat):
        node("ITEM_OAKS_LETTER", "item")
        dep.append(("SPECIES_SHAYMIN", "ITEM_OAKS_LETTER"))
        dep.append(("ITEM_OAKS_LETTER", "FLAG_GAME_COMPLETED"))
    # dex completion gate depends on every other species' acquisition node
    for sid, sp in sorted(names.items()):
        if sp == "SPECIES_ARCEUS":
            continue
        node(sp, nodes.get(sp, "species_acquisition"))
        dep.append(("DEX_001_492_CAUGHT", sp))
    # cycle check (DFS over a plain dict)
    adj = {}
    for a, b in dep:
        adj.setdefault(a, set()).add(b)
    state, cyc = {}, []

    def dfs(u, path):
        state[u] = 1
        for v in sorted(adj.get(u, ())):
            if state.get(v) == 1:
                cyc.append(path + [u, v])
            elif state.get(v) is None:
                dfs(v, path + [u])
        state[u] = 2

    sys.setrecursionlimit(10000)
    for n in sorted(set(nodes) | set(adj)):
        if state.get(n) is None:
            dfs(n, [])
    for c in cyc:
        errors.append("circular event dependency: " + " -> ".join(c))
    # Arceus must be the only species that depends on the dex-completion gate, and nothing depends on Arceus.
    gate_users = sorted({a for a, b in dep if b == "DEX_001_492_CAUGHT"} - {"DEX_001_492_CAUGHT"})
    if gate_users != ["SPECIES_ARCEUS"]:
        errors.append(f"dex-completion gate users must be exactly Arceus, got {gate_users}")
    if any(b == "SPECIES_ARCEUS" for _, b in dep):
        errors.append("something depends on Arceus (capstone must be terminal)")
    events = {"schema": "pokeplatinum-overhaul/d7-event-dependency-graph/v1",
              "nodes": dict(sorted(nodes.items())), "requires": sorted({f"{a} -> {b}" for a, b in dep if not a == "DEX_001_492_CAUGHT"}),
              "dex_completion_gate": {"node": "DEX_001_492_CAUGHT", "requires_species_count": 492, "consumer": gate_users},
              "summary": {"event_species": len(nat) + len(leg) + len(myth), "cycles": len(cyc),
                          "external_dependency_flags": 0}}

    # ---- progression gates ----
    per_band, cum = {b: [] for b, _ in BANDS}, 0
    for f in fam_summary:
        if f["entry_band"]:
            per_band[f["entry_band"]].append(f["family_id"])
    gates = {"schema": "pokeplatinum-overhaul/d7-progression-gates/v1",
             "bands": [{"band": b, "boundary": bd, "pre_e4": b in PRE_E4,
                        "nonlegendary_families_first_available": len(per_band[b]),
                        "cumulative_families": (cum := cum + len(per_band[b]))} for b, bd in BANDS],
             "method_gates": wild["method_gates"],
             "stone_shop": {"vendor": "Veilstone Dept. Store 2F", "band": STONE_BAND, "stones": STONES},
             "postgame_gates": {"FLAG_GAME_COMPLETED": "legendary legacy habitats, Regis, Darkrai, Shaymin, Arceus, Manaphy, Mew/Celebi/Jirachi/Deoxys"},
             "families_by_band": {b: sorted(v) for b, v in per_band.items()},
             "band_drift_vs_family_manifest": dict(sorted(drift.items())),
             "summary": {"nonlegendary_families": len(fam_summary), "band_drift_families": len(drift), "postgame_only_nonlegendary_families": len(per_band["P1"])}}
    if per_band["P1"]:
        errors.append(f"postgame-only nonlegendary families: {sorted(per_band['P1'])}")

    return {"pokedex": pokedex, "evolution": evolution, "events": events, "gates": gates}, errors, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="also require committed artifacts to be byte-identical")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    arts, errors, notes = build()
    stale = []
    for key, fn in OUT.items():
        path = os.path.join(ROOT, QA, fn)
        text = dumps(arts[key])
        if a.check:
            cur = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if cur != text:
                stale.append(fn)
        elif not a.no_write:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
    for n in notes:
        print("NOTE", n)
    for s in stale:
        errors.append(f"committed artifact {s} is stale (regenerate with build_qa_graphs.py)")
    for e in errors:
        print("FAIL", e)
    p = arts["pokedex"]["summary"]
    print(f"QA graphs: {p['reachable']}/493 reachable, {p['nonlegendary_families']} nonlegendary families, "
          f"{arts['evolution']['summary']['edges']} evolution edges, {arts['events']['summary']['cycles']} event cycles, "
          f"{len(errors)} failure(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
