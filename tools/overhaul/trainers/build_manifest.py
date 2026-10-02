#!/usr/bin/env python3
"""Generate the D1 trainer manifests from the pinned base commit + locked spec tables.

Outputs (docs/overhaul/implementation/trainers/):
  trainer_overhaul_manifest.json   inventory + every intentionally changed record (before guards, target parties)
  trainer_archetypes.json          ordinary-trainer transformation rules
  trainer_validation_rules.json    machine-readable validator policy

Base state is read from BASE_COMMIT (git), so regeneration is idempotent after the edits are applied.
"""
from __future__ import annotations

import collections
import copy
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import curated_sets as C
import locked_teams as L
import ordinary as O
import rival_sets as R
from area_lib import trainer_band, trainer_maps
from trainer_lib import (ARCHETYPES, BASE_COMMIT, FRONTIER_DIR, MANIFEST, OUT_DIR, RULES, ROOT, TRAINER_DIR, frontier_fingerprint,
                         move_data, species_data, trainer_files)

GYM_GATE = {
    "leader_roark": "Oreburgh Gym (badge 1)", "leader_gardenia": "Eterna Gym (badge 2)", "leader_fantina": "Hearthome Gym (badge 3)",
    "leader_maylene": "Veilstone Gym (badge 4)", "leader_wake": "Pastoria Gym (badge 5)", "leader_byron": "Canalave Gym (badge 6)",
    "leader_candice": "Snowpoint Gym (badge 7)", "leader_volkner": "Sunyshore Gym (badge 8)",
}
from build_manifest_consts import ACE_LEVEL  # noqa: E402
GATE = {
    "commander_mars_valley_windworks": "Valley Windworks", "commander_jupiter_team_galactic_eterna_building": "Eterna Galactic Building",
    "commander_saturn_valor_cavern": "Valor Cavern", "commander_mars_lake_verity": "Lake Verity (late)",
    "commander_saturn_galactic_hq": "Galactic HQ", "galactic_boss_cyrus_galactic_hq": "Galactic HQ",
    "galactic_boss_cyrus_distortion_world": "Distortion World", "commander_mars_spear_pillar": "Spear Pillar",
    "commander_jupiter_spear_pillar": "Spear Pillar", "commander_mars_stark_mountain": "Stark Mountain (postgame)",
    "commander_jupiter_stark_mountain": "Stark Mountain (postgame)",
    "elite_four_aaron": "Pokémon League", "elite_four_bertha": "Pokémon League", "elite_four_flint": "Pokémon League",
    "elite_four_lucian": "Pokémon League", "champion_cynthia": "Pokémon League",
}
RIVAL_GATE = {"rival_route_209": "Route 209", "rival_pastoria_city": "Pastoria City", "rival_canalave_city": "Canalave City",
              "rival_pokemon_league": "Pokémon League", "rival_fight_area": "Fight Area (postgame)",
              "rival_survival_area_1": "Survival Area (postgame)", "rival_survival_area_2": "Survival Area (postgame)",
              "rival_survival_area_unused": "Survival Area (unused record)"}
# Intro/special rival or boss records deliberately outside the locked scope.
UNCHANGED_LOCKED_OUT = {
    "rival_route_201_*": "intro fight (single starter-stage mon), not in locked scope",
    "rival_route_203_*": "locked as 2-mon Lv7-9 intro; species/levels already match the spec",
    "rival_spear_pillar_*": "not named by the locked spec/plan",
    "galactic_boss_cyrus_celestic_town_ruins": "not named by the locked spec/plan",
    "elite_four_flint_fight_area": "postgame Fight Area variant, not named by the locked spec/plan",
    "leader_volkner_fight_area": "postgame Fight Area variant, not named by the locked spec/plan",
}


def git_show(rel: str) -> str:
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{rel}"], cwd=ROOT, text=True)


def base_trainer(tid: str) -> dict:
    return json.loads(git_show(f"{TRAINER_DIR}/{tid}.json"))


def base_sha(tid: str) -> str:
    return hashlib.sha256(git_show(f"{TRAINER_DIR}/{tid}.json").encode()).hexdigest()


def phash(party: list[dict]) -> str:
    return hashlib.sha256(json.dumps(party, sort_keys=True).encode()).hexdigest()[:16]


def mem(species: str, level: int, item: str | None, moves: list[str] | None, iv: int, seal: int, explicit_items: bool,
        explicit_moves: bool) -> dict:
    it = None
    if explicit_items:
        it = "ITEM_" + item if item and not item.startswith("ITEM_") else (item or "ITEM_NONE")
    return {
        "species": species if species.startswith("SPECIES_") else "SPECIES_" + species,
        "form": 0, "level": level, "item": it,
        "moves": ["MOVE_" + m if not m.startswith("MOVE_") else m for m in moves] if explicit_moves else None,
        "iv_scale": iv, "ball_seal": seal,
    }


def modal_iv(base: dict) -> int:
    return collections.Counter(m["iv_scale"] for m in base["party"]).most_common(1)[0][0]


def iv_for(base: dict, species: str, slot: int | None = None) -> tuple[int, int]:
    s = species if species.startswith("SPECIES_") else "SPECIES_" + species
    for m in base["party"]:
        if m["species"] == s:
            return m["iv_scale"], m["ball_seal"]
    return modal_iv(base), 0


def entry(tid: str, category: str, gate: str, rationale: str, base: dict, party: list[dict], extra: dict | None = None) -> dict:
    lv = [m["level"] for m in party]
    e = {
        "id": tid, "path": f"{TRAINER_DIR}/{tid}.json", "category": category, "story_gate": gate, "rationale": rationale,
        "before": {"sha256": base_sha(tid), "party_hash": phash(base["party"]),
                   "party_summary": [f"{m['species'][8:]}:{m['level']}" for m in base["party"]]},
        "target": {"party": party},
        "expected_party_size": len(party), "level_band": [min(lv), max(lv)],
        "target_ai_flags": None, "target_bag_items": None,
    }
    if extra:
        e.update(extra)
    return e


def team_entry(tid, category, gate, rationale, team, base, moves_override=None, extra=None):
    explicit_items = any(it for _, _, it, _ in team)
    party = []
    for i, (sp, lv, it, mv) in enumerate(team):
        moves = moves_override[i] if moves_override else mv
        iv, seal = iv_for(base, sp)
        party.append(mem(sp, lv, it, moves, iv, seal, explicit_items, True))
    return entry(tid, category, gate, rationale, base, party, extra)


def build_gyms() -> list[dict]:
    out = []
    for tid, team in L.GYMS.items():
        e = team_entry(tid, "gym_leader", GYM_GATE[tid], "T1_GYM_LOCKED", team, base_trainer(tid), extra={
            "ace_level": ACE_LEVEL[tid]})
        out.append(e)
    return out


def build_rival() -> list[dict]:
    out = []
    for fight in R.FIGHTS:
        g = R.FIGHT_GROUP[fight]
        for br in R.BRANCHES:
            tid = f"{fight}_{br}"
            base = base_trainer(tid)
            has_items = g in ("canalave", "league") or fight != "rival_survival_area_unused" and g == "league"
            party_t = []
            for m in base["party"]:
                s = m["species"][8:]
                s = R.EVOLVE.get(g, {}).get(s, s)
                item = None
                if g == "canalave" and s in R.STARTER_FINAL:
                    item = "SITRUS_BERRY"
                if g == "league":
                    if s in R.STARTER_FINAL:
                        item = "SITRUS_BERRY"
                    if s == "SNORLAX":
                        item = "CHESTO_BERRY"
                party_t.append((s, m["level"], item, R.SETS[g][s], m["iv_scale"], m["ball_seal"]))
            explicit_items = any(t[2] for t in party_t)
            party = [mem(s, lv, it, mv, iv, seal, explicit_items, True) for s, lv, it, mv, iv, seal in party_t]
            out.append(entry(tid, "rival", RIVAL_GATE[fight], "T2_RIVAL_BRANCH", base, party,
                             {"rival_branch": br, "rival_fight": fight}))
    return out


def build_galactic() -> list[dict]:
    out = []
    for tid, team in L.GALACTIC.items():
        cat = "galactic_boss" if tid.startswith("galactic_boss") else "galactic_commander"
        out.append(team_entry(tid, cat, GATE[tid], "T3_GALACTIC_LOCKED" if "spear" not in tid and "stark" not in tid and "lake" not in tid
                              and "galactic_hq" not in tid or tid.startswith("galactic_boss") else "T3_COMMANDER_SCALING",
                              team, base_trainer(tid), moves_override=C.CURATED[tid]))
    return out


def build_elite() -> list[dict]:
    out = []
    for tid, team in L.ELITE.items():
        cat = "champion" if tid.startswith("champion") else "elite_four"
        out.append(team_entry(tid, cat, GATE[tid], "T4_ELITE_LOCKED", team, base_trainer(tid), moves_override=C.CURATED[tid]))
    return out


def build_rematch() -> list[dict]:
    out = []
    for tid, species in L.REMATCH_SPECIES.items():
        base = base_trainer(tid)
        lv = [m["level"] for m in base["party"]]
        assert len(lv) == len(species), tid
        # the ace keeps the base record's last-slot item
        ace_item = base["party"][-1]["item"]
        items = [None] * (len(species) - 1) + [ace_item.replace("ITEM_", "") if ace_item else None]
        if any(m["item"] and m["item"] != "ITEM_NONE" for m in base["party"][:-1]):
            items = [m["item"].replace("ITEM_", "") if m["item"] and m["item"] != "ITEM_NONE" else None for m in base["party"]]
        team = [(s, l, i, None) for s, l, i in zip(species, lv, items)]
        cat = "champion_rematch" if tid.startswith("champion") else ("elite_four_rematch" if tid.startswith("elite") else "gym_rematch")
        out.append(team_entry(tid, cat, "postgame rematch", "T6_REMATCH_LOCKED", team, base, moves_override=C.CURATED[tid]))
    return out


def ordinary_ids() -> list[str]:
    return [t for t in trainer_files() if O.is_ordinary(t)]


def build_ordinary() -> tuple[list[dict], dict]:
    ids = ordinary_ids()
    base = {t: base_trainer(t) for t in ids}
    active = set(trainer_maps())
    usage = O.Usage()
    for t in ids:
        if t in active:
            for m in base[t]["party"]:
                usage.add(m["species"])
    work = {t: copy.deepcopy(base[t]["party"]) for t in ids}
    tags: dict[str, collections.Counter] = {t: collections.Counter() for t in ids}
    kept_family: dict[tuple[str, int], str] = {}
    unresolved = []

    def set_species(t, i, new, tag):
        old = work[t][i]["species"]
        if t in active:
            usage.add(old, -1)
            usage.add(new, 1)
        work[t][i]["species"] = new
        tags[t][tag] += 1

    # R1-R3 per trainer
    for t in ids:
        b = O.effective_band(t, work[t])
        grunt = O.is_grunt(t)
        for i, m in enumerate(work[t]):
            ns = O.sync_evolution(m["species"], m["level"])
            if ns != m["species"]:
                set_species(t, i, ns, "R1_evolution_sync")
        for i, m in enumerate(work[t]):
            sb = O.species_band(m["species"])
            if sb is not None and not O.band_le(sb, b):
                excl = {x["species"] for x in work[t]}
                c = O.pick(m["species"], m["level"], b, grunt, excl, usage, t)
                if c:
                    set_species(t, i, c, "R2_availability")
                else:
                    unresolved.append((t, m["species"]))
        if not base[t]["double_battle"]:
            seen = set()
            for i, m in enumerate(work[t]):
                if m["species"] in seen:
                    excl = {x["species"] for x in work[t]}
                    c = O.pick(m["species"], m["level"], b, grunt, excl, usage, t + str(i))
                    if c:
                        set_species(t, i, c, "R3_duplicate")
                        seen.add(c)
                        continue
                seen.add(m["species"])
    # R4 global caps (active, non-rematch trainers only; <= 2 swaps per trainer)
    order = sorted((t for t in ids if t in active), key=lambda t: O.h("r4", t))
    for t in order:
        swaps = 0
        b = O.effective_band(t, work[t])
        for i, m in enumerate(work[t]):
            if swaps >= O.MAX_SWAPS_PER_TRAINER:
                break
            s = m["species"]
            if usage.species[s] > O.CAP_SPECIES or usage.family[O.family_of(s)] > O.CAP_FAMILY:
                if base[t]["double_battle"]:
                    continue
                excl = {x["species"] for x in work[t]}
                c = O.pick(s, m["level"], b, O.is_grunt(t), excl, usage, "r4" + t + str(i))
                if c:
                    set_species(t, i, c, "R4_usage_cap")
                    swaps += 1
    # R5 moves (explicit-move teams only) + assemble
    entries = []
    for t in ids:
        bp = base[t]["party"]
        explicit_moves = bp[0]["moves"] is not None
        out_party = []
        changed = False
        for i, m in enumerate(work[t]):
            nm = copy.deepcopy(m)
            b0 = bp[i]
            if explicit_moves:
                if nm["species"] != b0["species"]:
                    same_family = O.family_of(nm["species"]) == O.family_of(b0["species"])
                    keep = [x for x in b0["moves"] if x in O.legal_moves(nm["species"], nm["level"]) and O.usable(x)] if same_family else []
                    if len(keep) < 3:
                        nat = [x for x in O.natural_moves(nm["species"], nm["level"]) if x not in keep]
                        keep = (keep + nat)[:4] if same_family else O.natural_moves(nm["species"], nm["level"])
                    nm["moves"] = keep
                else:
                    wm = O.weak_moves(nm["species"], nm["level"], b0["moves"])
                    if wm != b0["moves"]:
                        tags[t]["R5_moves"] += 1
                    nm["moves"] = wm
                if not nm["moves"]:
                    nm["moves"] = O.natural_moves(nm["species"], nm["level"])
            out_party.append(nm)
            if nm != b0:
                changed = True
        if changed:
            cat = "ordinary_rematch" if "rematch" in t else "ordinary"
            e = entry(t, cat, str(trainer_band(t) or "n/a"), "T5_ORDINARY_ARCHETYPE" if cat == "ordinary" else "T5_ORDINARY_REMATCH_SYNC",
                      base[t], out_party, {"rules_applied": dict(tags[t]), "band_used": O.effective_band(t, work[t])})
            entries.append(e)
    return entries, {"unresolved": unresolved}


def created_recipients() -> dict:
    with open(os.path.join(ROOT, "docs/overhaul/implementation/created_moves_manifest.json"), encoding="utf-8") as f:
        mv = json.load(f)["moves"]
    out = {}
    for m in mv:
        names = ["SPECIES_" + n.upper().replace("'", "").replace(". ", "_").replace(" ", "_").replace("-", "_")
                 for n in m["distribution"] if " " not in n or n in ("Mr. Mime", "Mime Jr.")]
        out[m["const"]] = sorted(set(names))
    return out


def classify_all(changed_ids: set[str]) -> dict:
    inv = collections.defaultdict(list)
    maps = trainer_maps()
    for t in trainer_files():
        if t.startswith("leader_") and "rematch" not in t and "fight_area" not in t:
            c = "gym_leader"
        elif t.startswith("leader_") and "rematch" in t:
            c = "gym_rematch"
        elif t.startswith("leader_"):
            c = "postgame_variant_unmodified"
        elif t.startswith("elite_four") and "rematch" in t:
            c = "elite_four_rematch"
        elif t.startswith("elite_four") and "fight_area" in t:
            c = "postgame_variant_unmodified"
        elif t.startswith("elite_four"):
            c = "elite_four"
        elif t.startswith("champion") and "rematch" in t:
            c = "champion_rematch"
        elif t.startswith("champion"):
            c = "champion"
        elif t.startswith("rival_"):
            c = "rival"
        elif t.startswith("galactic_boss"):
            c = "galactic_boss"
        elif t.startswith("commander_"):
            c = "galactic_commander"
        elif "dummy" in t:
            c = "unused_dummy"
        elif "_unused" in t:
            c = "unused_record"
        elif t.startswith(O.SPECIAL_PREFIXES):
            c = "story_special_unmodified"
        elif "rematch" in t:
            c = "ordinary_rematch"
        elif t in maps:
            c = "ordinary_active"
        else:
            c = "ordinary_script_placed"
        inv[c].append(t)
    return {k: sorted(v) for k, v in sorted(inv.items())}


def main() -> int:
    entries = build_gyms() + build_rival() + build_galactic() + build_elite() + build_rematch()
    ord_entries, info = build_ordinary()
    entries += ord_entries
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "duplicate manifest ids"
    inv = classify_all(set(ids))
    frontier_files = sorted(os.path.relpath(os.path.join(dp, f), ROOT) for dp, _, fs in os.walk(os.path.join(ROOT, FRONTIER_DIR)) for f in fs)
    manifest = {
        "schema": "trainer_overhaul_manifest/1",
        "base_commit": BASE_COMMIT,
        "authority": "docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md + TRAINER_IMPLEMENTATION_PLAN.md (LOCKED)",
        "iv_scale_semantics": {
            "formula": "IV = iv_scale * 31 / 255 (src/trainer_data.c; MAX_IV_SCALE=255), stored in a u8 and applied to all six stats; "
                       "also seeds the personality RNG (iv_scale + level + species + trainerID)",
            "policy": "iv_scale is NOT normalized; retained members keep their value, new members take the base record's value for the "
                      "same species (else the record's modal value)",
            "known_outlier": "leader_volkner Electivire iv_scale=2500 (>255 wraps in the u8); preserved, reported as a warning",
        },
        "inventory": {
            "counts": {k: len(v) for k, v in inv.items()},
            "total_trainer_records": len(trainer_files()),
            "active_map_placed_trainers": len(trainer_maps()),
            "categories": inv,
            "frontier": {"directory": FRONTIER_DIR, "file_count": len(frontier_files), "fingerprint_sha256": frontier_fingerprint(),
                         "policy": "out of scope; validator asserts unchanged"},
        },
        "unchanged_by_design": UNCHANGED_LOCKED_OUT,
        "unresolved_ordinary_replacements": info["unresolved"],
        "entry_count": len(entries),
        "entries": sorted(entries, key=lambda e: (e["category"], e["id"])),
    }
    import policy
    os.makedirs(os.path.join(ROOT, OUT_DIR), exist_ok=True)
    for rel, data in ((ARCHETYPES, policy.archetypes()), (RULES, policy.rules(created_recipients()))):
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
            f.write("\n")
    with open(os.path.join(ROOT, MANIFEST), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"manifest entries={len(entries)} (ordinary={len(ord_entries)}) unresolved={len(info['unresolved'])}")
    print(json.dumps(manifest["inventory"]["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
