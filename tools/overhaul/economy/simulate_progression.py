#!/usr/bin/env python3
"""Deterministic progression calibration model (NOT a claim to reproduce human play).

Inputs (all read from the repository): trainer party files (res/trainers/data), species base EXP yields and growth
rates (res/pokemon/*/data.json), growth tables (res/pokemon/.shared/exp_tables.csv) and the provisional wild manifest.
Compares the overhaul's conserved team-wide EXP against the vanilla single-recipient behavior.

Segments are the 14 locked main-story ace targets. Ordinary trainers are bucketed by their ace level into the segment
whose boss ace is the first >= that level. Profiles take a fixed share of ordinary trainers and a fixed number of wild
KOs per segment; a rotating party picks participants round-robin.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import statistics
import sys

import exp_model
from economy_lib import ROOT, read

BOSSES = [("Roark", "leader_roark", 14), ("Gardenia", "leader_gardenia", 22), ("Fantina", "leader_fantina", 27),
          ("Maylene", "leader_maylene", 32), ("Wake", "leader_wake", 37), ("Byron", "leader_byron", 41),
          ("Candice", "leader_candice", 44), ("Volkner", "leader_volkner", 50), ("Aaron", "elite_four_aaron", 53),
          ("Bertha", "elite_four_bertha", 55), ("Flint", "elite_four_flint", 57), ("Lucian", "elite_four_lucian", 59),
          ("Cynthia", "champion_cynthia", 62)]
ORDINARY_EXCLUDE = ("leader_", "elite_four", "champion", "commander", "galactic_boss", "rival", "dummy", "frontier", "_rematch",
                    "lucas", "dawn", "ruin_maniac_cyrus", "_fight_area", "_spear_pillar", "_stark", "galactic")
GROWTH_COLUMN = {"EXP_RATE_MEDIUM_FAST": "medium_fast", "EXP_RATE_ERRATIC": "erratic", "EXP_RATE_FLUCTUATING": "fluctuating",
                 "EXP_RATE_MEDIUM_SLOW": "medium_slow", "EXP_RATE_FAST": "fast", "EXP_RATE_SLOW": "slow"}

# profile: share of ordinary trainers fought, wild KOs per segment, rotation size (members that take turns as participant),
#          Exp. Share holders (benched holders), mean boss-KOs participants.
PROFILES = {
    "direct": dict(trainer_share=0.15, wild_kos=6, rotation=2, holders=1, party=5),
    "normal": dict(trainer_share=0.65, wild_kos=14, rotation=4, holders=0, party=6),
    "completionist": dict(trainer_share=1.0, wild_kos=24, rotation=5, holders=0, party=6),
}
# Growth mix of the modelled party and the segment at which each member joins (joiners arrive at avg level - 3, min 5).
PARTY = [("medium_slow", 0), ("medium_fast", 0), ("medium_slow", 0), ("fast", 1), ("medium_fast", 2), ("slow", 3)]


def load_tables():
    with open(os.path.join(ROOT, "res/pokemon/.shared/exp_tables.csv")) as f:
        rows = list(csv.DictReader(f))
    return {col: [int(r[col]) for r in rows] for col in GROWTH_COLUMN.values()}


def species_info(const: str, cache: dict):
    if const in cache:
        return cache[const]
    d = os.path.join(ROOT, "res/pokemon", const[len("SPECIES_"):].lower(), "data.json")
    info = None
    if os.path.exists(d):
        j = json.load(open(d))
        info = (j["base_exp_reward"], GROWTH_COLUMN.get(j["exp_rate"], "medium_fast"))
    cache[const] = info
    return info


def trainer_levels(path):
    j = json.load(open(path))
    return [(p["species"], p["level"]) for p in j["party"]]


def collect_segments(cache):
    bounds = [b[2] for b in BOSSES]
    seg_kos = [[] for _ in BOSSES]   # ordinary trainer KOs (base_exp, level)
    boss_kos = [[] for _ in BOSSES]
    ace_live = []
    missing = set()
    for i, (name, stem, target) in enumerate(BOSSES):
        mons = trainer_levels(os.path.join(ROOT, "res/trainers/data", stem + ".json"))
        ace_live.append(max(l for _, l in mons))
        for sp, lv in mons:
            info = species_info(sp, cache)
            if info:
                boss_kos[i].append((info[0], lv))
            else:
                missing.add(sp)
    for path in sorted(glob.glob(os.path.join(ROOT, "res/trainers/data/*.json"))):
        stem = os.path.basename(path)[:-5]
        if any(x in stem for x in ORDINARY_EXCLUDE):
            continue
        mons = trainer_levels(path)
        if not mons:
            continue
        ace = max(l for _, l in mons)
        seg = next((i for i, b in enumerate(bounds) if ace <= b), None)
        if seg is None:
            continue
        for sp, lv in mons:
            info = species_info(sp, cache)
            if info:
                seg_kos[seg].append((info[0], lv))
            else:
                missing.add(sp)
    return seg_kos, boss_kos, ace_live, missing


def wild_per_segment(cache):
    path = os.path.join(ROOT, "docs/overhaul/implementation/wild_encounters.json")
    entries = json.load(open(path))["entries"]
    bounds = [0] + [b[2] for b in BOSSES]
    segs = [[] for _ in BOSSES]
    for e in entries:
        if e["method"] not in ("land", "surf") or e["rate_pct"] <= 0:
            continue
        info = species_info(e["species"], cache)
        if not info:
            continue
        lv = (e["level_min"] + e["level_max"]) / 2
        for i in range(len(BOSSES)):
            if bounds[i] - 6 < lv <= bounds[i + 1]:
                segs[i].append((info[0], round(lv), e["rate_pct"]))
                break
    out = []
    for s in segs:
        if not s:
            out.append((50, 10))
            continue
        w = sum(r for _, _, r in s)
        out.append((sum(b * r for b, _, r in s) / w, sum(l * r for _, l, r in s) / w))
    return out


def level_for(exp, table):
    lv = 1
    for l in range(1, 101):
        if table[l] <= exp:
            lv = l
    return lv


def simulate(profile: str, team_wide: bool, tables, seg_kos, boss_kos, wild, aces):
    p = PROFILES[profile]
    members = []  # dict(growth, exp, joined)
    rows = []
    kos_done = 0
    for si in range(len(BOSSES)):
        for growth, join in PARTY[:p["party"]]:
            if join == si and not any(m["slot"] == len(members) for m in members):
                start = 5 if not members else max(5, int(statistics.mean(level_for(m["exp"], tables[m["growth"]]) for m in members)) - 3)
                members.append(dict(slot=len(members), growth=growth, exp=tables[growth][start]))
        if si == 0 and not members:
            members.append(dict(slot=0, growth="medium_slow", exp=tables["medium_slow"][5]))

        def fight(base_exp, level, trainer):
            nonlocal kos_done
            mem = [exp_model.Member(slot=m["slot"], level=level_for(m["exp"], tables[m["growth"]]),
                                    exp_share=(team_wide and m["slot"] >= len(members) - p["holders"] and m["slot"] > 0))
                   for m in members]
            n_rot = min(p["rotation"], len(members))
            part = {(kos_done + k) % n_rot for k in range(1 if not trainer else 1)}
            # Slots outside the rotation never fight; the rotation is the set of lowest slots.
            mem = [exp_model.Member(**{**m.__dict__, "participant": m.slot in part}) for m in mem]
            raw = exp_model.raw_pool(base_exp, level)
            if team_wide:
                got = exp_model.payout(base_exp, level, mem, trainer)
            else:  # vanilla: participants split the raw pool; Exp. Share holders hold a flat 50/50 split (modelled as none)
                parts = [m for m in mem if exp_model.eligible(m) and m.participant]
                got = {m.slot: exp_model.final_exp(max(1, raw // max(1, len(parts))), m, trainer) for m in parts}
            for m in members:
                m["exp"] += got.get(m["slot"], 0)
            kos_done += 1

        wb, wl = wild[si]
        for _ in range(p["wild_kos"]):
            fight(wb, round(wl), False)
        ordinary = seg_kos[si]
        take = int(round(len(ordinary) * p["trainer_share"]))
        step = len(ordinary) / take if take else 0
        for k in range(take):
            b, l = ordinary[int(k * step)]
            fight(b, l, True)
        for b, l in boss_kos[si]:
            fight(b, l, True)
        lv = sorted(level_for(m["exp"], tables[m["growth"]]) for m in members)
        rows.append(dict(boss=BOSSES[si][0], ace=aces[si], avg=round(statistics.mean(lv), 1), median=statistics.median(lv),
                         max=max(lv), min=min(lv), members=len(lv)))
    return rows


def flags(profile, rows):
    out = []
    for r in rows:
        d = r["avg"] - r["ace"]
        if profile == "direct" and d < -4:
            out.append(f"{r['boss']}: direct avg {r['avg']} is {-d:.1f} below ace {r['ace']} (> 4)")
        if profile == "normal" and d < -3:
            out.append(f"{r['boss']}: normal avg {r['avg']} is {-d:.1f} below ace {r['ace']} (> 3)")
        if profile in ("normal", "completionist") and d > 2:
            out.append(f"{r['boss']}: {profile} avg {r['avg']} is {d:.1f} above ace {r['ace']} (> 2)")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write full results to this path")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    tables, cache = load_tables(), {}
    seg_kos, boss_kos, aces, missing = collect_segments(cache)
    wild = wild_per_segment(cache)
    spec_aces = [b[2] for b in BOSSES]
    result = {"aces_live": aces, "aces_spec": spec_aces, "ordinary_ko_counts": [len(s) for s in seg_kos],
              "unresolved_species": sorted(missing), "profiles": {}}
    for prof in PROFILES:
        tw = simulate(prof, True, tables, seg_kos, boss_kos, wild, spec_aces)
        van = simulate(prof, False, tables, seg_kos, boss_kos, wild, spec_aces)
        result["profiles"][prof] = {"team_wide": tw, "vanilla": van, "flags": flags(prof, tw), "vanilla_flags": flags(prof, van)}
    if args.json:
        with open(args.json, "w") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    if not args.quiet:
        for prof, r in result["profiles"].items():
            print(f"\n== {prof} (party {PROFILES[prof]['party']}, rotation {PROFILES[prof]['rotation']}) ==")
            print(f"{'boss':9}{'ace':>4}{'avg':>7}{'med':>6}{'max':>5}{'min':>5} | vanilla avg  d_team  d_van")
            for t, v in zip(r["team_wide"], r["vanilla"]):
                print(f"{t['boss']:9}{t['ace']:>4}{t['avg']:>7}{t['median']:>6}{t['max']:>5}{t['min']:>5} | {v['avg']:>11}  {t['avg'] - t['ace']:+6.1f} {v['avg'] - v['ace']:+6.1f}")
            for fl in r["flags"]:
                print("  FLAG:", fl)
    return 0


if __name__ == "__main__":
    sys.exit(main())
