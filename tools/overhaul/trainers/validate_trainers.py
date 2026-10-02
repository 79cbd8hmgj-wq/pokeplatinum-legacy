#!/usr/bin/env python3
"""Validator for the locked D1 Trainer Overhaul.

Exit 0 = no blocking errors.  Writes docs/overhaul/implementation/trainers/TRAINER_VALIDATION_REPORT.md (deterministic).
  validate_trainers.py [--no-report] [--no-git]
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import locked_teams as L
import ordinary as O
from area_lib import band_le, species_band, trainer_band, trainer_maps
from moveset_lib import CUSTOM_MOVES, is_attack, usable
from trainer_lib import (MAX_PARTY, is_final, BASE_COMMIT, FRONTIER_DIR, MANIFEST, REPORT, RULES, ROOT, TRAINER_DIR, ai_flag_set, bst, frontier_fingerprint,
                         item_set, legal_moves, load_trainer, move_data, move_set, p, party_hash, species_data, species_set, trainer_files)


class Result:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def err(self, m: str) -> None:
        self.errors.append(m)

    def warn(self, m: str) -> None:
        self.warnings.append(m)

    def note(self, m: str) -> None:
        self.notes.append(m)


def load(rel: str) -> dict:
    with open(p(rel), encoding="utf-8") as f:
        return json.load(f)


def git_lines(*args: str) -> list[str]:
    return [ln for ln in subprocess.check_output(["git", *args], cwd=ROOT, text=True).splitlines() if ln]


def recipients_ok(move: str, species: str, rules: dict) -> bool:
    return species in rules["moves"]["created_move_recipients"].get(move, [])


# ---------------------------------------------------------------------------------------------------------------- source schema
def check_source(res: Result, rules: dict) -> dict:
    classes = {ln.strip() for ln in open(p("generated/trainer_classes.txt"), encoding="utf-8") if ln.strip()}
    data = {}
    unresolved = set(rules["moves"]["unresolved"])
    superseded = set(rules["moves"]["superseded"])
    for tid in trainer_files():
        try:
            d = load_trainer(tid)
        except Exception as ex:  # noqa: BLE001
            res.err(f"{tid}: JSON parse error {ex}")
            continue
        data[tid] = d
        if d["class"] not in classes:
            res.err(f"{tid}: unknown class {d['class']}")
        for fl in d["ai_flags"]:
            if fl not in ai_flag_set():
                res.err(f"{tid}: unknown AI flag {fl}")
        for it in d["items"]:
            if it not in item_set():
                res.err(f"{tid}: unknown bag item {it}")
        party = d["party"]
        if tid != "none" and not party:
            res.err(f"{tid}: empty party")
        if len(party) > MAX_PARTY:
            res.err(f"{tid}: oversized party ({len(party)})")
        enc_items = {type(m["item"]).__name__ for m in party}
        enc_moves = {type(m["moves"]).__name__ for m in party}
        if len(enc_items) > 1 or len(enc_moves) > 1:
            res.err(f"{tid}: non-uniform item/moves encoding across the party (trainerproc keys on the first member)")
        for i, m in enumerate(party):
            s = m["species"]
            if s not in species_set() or s == "SPECIES_NONE" or species_data(s) is None:
                res.err(f"{tid}[{i}]: invalid species {s}")
                continue
            if not isinstance(m["form"], int) or m["form"] < 0:
                res.err(f"{tid}[{i}]: invalid form {m['form']}")
            if not 1 <= m["level"] <= 100:
                res.err(f"{tid}[{i}]: invalid level {m['level']}")
            if m["item"] is not None and m["item"] not in item_set():
                res.err(f"{tid}[{i}]: invalid item {m['item']}")
            if m["moves"] is not None:
                if not 1 <= len(m["moves"]) <= 4 and "dummy" not in tid:
                    res.err(f"{tid}[{i}]: move count {len(m['moves'])}")
                for mv in m["moves"]:
                    if mv not in move_set() or mv in ("MOVE_NONE", "MAX_MOVES"):
                        res.err(f"{tid}[{i}]: invalid move {mv}")
                    if mv in unresolved or mv in superseded:
                        res.err(f"{tid}[{i}]: unresolved/superseded move {mv}")
                if len(set(m["moves"])) != len(m["moves"]):
                    res.err(f"{tid}[{i}]: duplicate move in set")
    return data


# ---------------------------------------------------------------------------------------------------------------- manifest
def check_manifest(res: Result, man: dict, data: dict, use_git: bool) -> None:
    ids = {e["id"] for e in man["entries"]}
    for e in man["entries"]:
        live = data.get(e["id"])
        if live is None:
            res.err(f"{e['id']}: manifest entry has no source record")
            continue
        if live["party"] != e["target"]["party"]:
            res.err(f"{e['id']}: source drifted from manifest target (party differs)")
        if len(live["party"]) != e["expected_party_size"]:
            res.err(f"{e['id']}: party size {len(live['party'])} != expected {e['expected_party_size']}")
        lv = [m["level"] for m in live["party"]]
        if not (e["level_band"][0] <= min(lv) and max(lv) <= e["level_band"][1]):
            res.err(f"{e['id']}: level outside declared band {e['level_band']}")
        if use_git:
            base = json.loads(subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{e['path']}"], cwd=ROOT, text=True))
            for k in base:
                if k != "party" and base[k] != live[k]:
                    res.err(f"{e['id']}: non-party field '{k}' changed (manifest only authorizes party edits)")
            if party_hash(base) != e["before"]["party_hash"]:
                res.err(f"{e['id']}: manifest before-hash does not match base commit")
    if use_git:
        changed = git_lines("diff", "--name-only", BASE_COMMIT, "--", TRAINER_DIR)
        changed += git_lines("ls-files", "--others", "--exclude-standard", "--", TRAINER_DIR)
        for rel in changed:
            tid = os.path.basename(rel)[:-5]
            if tid not in ids:
                res.err(f"{tid}: trainer record modified but absent from the manifest")
        fr = git_lines("diff", "--name-only", BASE_COMMIT, "--", FRONTIER_DIR) + git_lines("ls-files", "--others", "--exclude-standard",
                                                                                            "--", FRONTIER_DIR)
        for rel in fr:
            res.err(f"Frontier file modified: {rel}")
    if frontier_fingerprint() != man["inventory"]["frontier"]["fingerprint_sha256"]:
        res.err("Frontier fingerprint differs from the manifest inventory")


# ---------------------------------------------------------------------------------------------------------------- bosses
def category_of(man: dict) -> dict[str, str]:
    return {e["id"]: e["category"] for e in man["entries"]}


def expected_size(rules: dict, e: dict) -> int | None:
    ps = rules["party_size"]
    c, tid = e["category"], e["id"]
    v = ps.get(c)
    if isinstance(v, int):
        return v
    if isinstance(v, dict):
        if tid in v:
            return v[tid]
        if c == "rival":
            return v.get(e.get("rival_fight"))
        return v.get("default")
    return None


def check_bosses(res: Result, rules: dict, man: dict, data: dict) -> list[dict]:
    flags = set(rules["ai"]["required_flags"])
    required_cats = set(rules["ai"]["required_categories"])
    dup_cats = set(rules["duplicates"]["important_categories"])
    forb = set(rules["held_items"]["main_story_forbidden"])
    main_cats = set(rules["held_items"]["main_story_categories"])
    spec_locked = {**L.GYMS}
    for e in man["entries"]:
        tid, c = e["id"], e["category"]
        if c.startswith("ordinary"):
            continue
        d = data[tid]
        party = d["party"]
        if any(species_data(m["species"]) is None for m in party):
            continue  # reported by check_source
        sz = expected_size(rules, e)
        if sz is not None and len(party) != sz:
            res.err(f"{tid}: boss party size {len(party)} != required {sz}")
        if c in required_cats and not any(tid.startswith(x[:-1]) for x in rules["ai"]["exempt_ids"]):
            miss = flags - set(d["ai_flags"])
            if miss:
                res.err(f"{tid}: missing required boss AI flags {sorted(miss)}")
        if c in dup_cats:
            cnt = collections.Counter(m["species"] for m in party)
            for s, n in cnt.items():
                if n > 1:
                    res.err(f"{tid}: duplicate {s} on an important team")
        held = [m["item"] for m in party if m["item"] and m["item"] != "ITEM_NONE"]
        if c in main_cats:
            for it in held:
                if it in forb:
                    res.err(f"{tid}: forbidden main-story held item {it}")
            if len(held) > rules["held_items"]["max_items_per_main_story_team"]:
                res.err(f"{tid}: too many held items ({len(held)})")
        if tid == rules["held_items"]["gym1_none"] and held:
            res.err(f"{tid}: Gym 1 may not hold items")
        if c == "gym_leader":
            if sum(1 for it in d["items"] if "POTION" in it or "RESTORE" in it) > rules["bag_items"]["gym_max_heals"]:
                res.err(f"{tid}: more than {rules['bag_items']['gym_max_heals']} bag heals")
            ace = party[-1]["level"]
            if ace != rules["ace_levels"][tid]:
                res.err(f"{tid}: ace level {ace} != locked {rules['ace_levels'][tid]}")
            sp = [(m["species"][8:], m["level"], (m["item"] or "ITEM_NONE")[5:] or None, [x[5:] for x in m["moves"]]) for m in party]
            want = [(s, l, i, mv) for s, l, i, mv in spec_locked[tid]]
            sp = [(s, l, None if i in (None, "NONE") else i, mv) for s, l, i, mv in sp]
            if sp != want:
                res.err(f"{tid}: gym team does not match the locked spec exactly")
        if c == "elite_four":
            if d["items"] != rules["bag_items"]["elite_four_exact"]:
                res.err(f"{tid}: Elite Four bag must be 2 Full Restores")
        if c == "champion" and d["items"] != rules["bag_items"]["champion_exact"]:
            res.err(f"{tid}: Cynthia bag must be 4 Full Restores")
        if tid in rules["ace_levels"] and c in ("elite_four", "champion") and party[-1]["level"] != rules["ace_levels"][tid]:
            res.err(f"{tid}: ace level {party[-1]['level']} != locked {rules['ace_levels'][tid]}")
        if tid in rules["gym_theme_type"]:
            off = [m["species"] for m in party if rules["gym_theme_type"][tid] not in species_data(m["species"])["types"]]
            if len(off) > rules["max_off_type_members"]:
                res.err(f"{tid}: {len(off)} off-type members {off} (max {rules['max_off_type_members']})")
        if c in ("elite_four", "champion"):
            want = [(s, l) for s, l, _, _ in (L.ELITE[tid])]
            got = [(m["species"][8:], m["level"]) for m in party]
            if got != want:
                res.err(f"{tid}: team does not match the locked spec species/levels")
        if c in ("gym_rematch", "elite_four_rematch", "champion_rematch"):
            want = L.REMATCH_SPECIES[tid]
            if [m["species"][8:] for m in party] != want:
                res.err(f"{tid}: rematch species do not match the locked spec")
        if tid in L.GALACTIC:
            want = [(s, l) for s, l, _, _ in L.GALACTIC[tid]]
            if [(m["species"][8:], m["level"]) for m in party] != want:
                res.err(f"{tid}: galactic team does not match the manifest tables")
        # moves
        for i, m in enumerate(party):
            lvl = m["level"]
            leg = legal_moves(m["species"], lvl)
            spec_moves = set()
            if tid in spec_locked and i < len(spec_locked[tid]):
                spec_moves = {"MOVE_" + x for x in spec_locked[tid][i][3]}
            for mv in m["moves"] or []:
                if mv in CUSTOM_MOVES and not recipients_ok(mv, m["species"], rules):
                    res.err(f"{tid}[{i}]: created move {mv} on non-recipient {m['species']}")
                if mv not in leg:
                    if mv in spec_moves:
                        res.note(f"{tid}[{i}] {m['species'][8:]} L{lvl}: locked-spec move {mv[5:]} not in current learnset")
                    elif mv in CUSTOM_MOVES and recipients_ok(mv, m["species"], rules):
                        res.note(f"{tid}[{i}] {m['species'][8:]} L{lvl}: created-move recipient {mv[5:]} not yet in learnset data")
                    else:
                        res.err(f"{tid}[{i}] {m['species'][8:]} L{lvl}: illegal move {mv}")
            if m["moves"] and not any(is_attack(x) for x in m["moves"]):
                res.warn(f"{tid}[{i}]: no attacking move")
        # evolution (bosses: warnings)
        for i, m in enumerate(party):
            k = O.contradiction(m["species"], m["level"])
            if k:
                res.warn(f"{tid}[{i}] {m['species'][8:]} L{m['level']}: evolution-stage {k}-evolved vs locked evolution tables (boss/locked)")
    return []


# ---------------------------------------------------------------------------------------------------------------- rival structure
def rival_structure(res: Result, man: dict, data: dict) -> list[str]:
    lines = []
    fights = sorted({e["rival_fight"] for e in man["entries"] if e["category"] == "rival"})
    for f in fights:
        parties = {b: data[f"{f}_{b}"]["party"] for b in ("turtwig", "chimchar", "piplup")}
        n = {len(v) for v in parties.values()}
        if len(n) != 1:
            res.err(f"{f}: branch party sizes differ {n}")
            continue
        size = n.pop()
        diff_idx = []
        for i in range(size):
            sp = {b: parties[b][i]["species"] for b in parties}
            lv = {parties[b][i]["level"] for b in parties}
            if len(lv) != 1:
                res.err(f"{f}[{i}]: levels differ across branches {lv}")
            if len(set(sp.values())) > 1:
                diff_idx.append(i)
            else:
                mv = {tuple(parties[b][i]["moves"] or []) for b in parties}
                it = {parties[b][i]["item"] for b in parties}
                if len(mv) > 1 or len(it) > 1:
                    res.err(f"{f}[{i}]: shared slot has different moves/items across branches")
        allowed = {"STARAVIA", "STARAPTOR", "BUIZEL", "FLOATZEL", "ROSELIA", "ROSERADE", "PONYTA", "RAPIDASH", "MONFERNO", "PRINPLUP",
                   "GROTLE", "INFERNAPE", "EMPOLEON", "TORTERRA"}
        for i in diff_idx:
            for b in parties:
                s = parties[b][i]["species"][8:]
                if s not in allowed:
                    res.err(f"{f}[{i}]: unexpected branch-dependent species {s}")
        row = [f"`{f}`", str(size), ", ".join(f"{i + 1}" for i in diff_idx) or "-"]
        for b in ("turtwig", "chimchar", "piplup"):
            row.append(" / ".join(f"{m['species'][8:].title()} {m['level']}" for m in parties[b]))
        lines.append("| " + " | ".join(row) + " |")
        # starter ace slot is always the last slot and a starter final
        for b in parties:
            if parties[b][-1]["species"][8:] not in {"INFERNAPE", "EMPOLEON", "TORTERRA", "MONFERNO", "PRINPLUP", "GROTLE"}:
                res.err(f"{f}_{b}: last slot is not the rival starter")
    return lines


# ---------------------------------------------------------------------------------------------------------------- ordinary
def check_ordinary(res: Result, data: dict, cats: dict[str, str]) -> dict:
    stats = collections.Counter()
    maps = trainer_maps()
    use = collections.Counter()
    for tid, d in sorted(data.items()):
        if not O.is_ordinary(tid) or tid == "none":
            continue
        if not d["party"] or any(species_data(m["species"]) is None for m in d["party"]):
            continue  # reported by check_source
        band = O.effective_band(tid, d["party"])
        stats["ordinary_records"] += 1
        names = collections.Counter(m["species"] for m in d["party"])
        for i, m in enumerate(d["party"]):
            s, lvl = m["species"], m["level"]
            if tid in maps:
                use[s] += 1
            sb = species_band(s)
            if sb is not None and not band_le(sb, band):
                res.err(f"{tid}[{i}] {s[8:]}: family band {sb} later than trainer band {band}")
            if sb is None:
                res.warn(f"{tid}[{i}] {s[8:]}: reserved/unbanded family on an ordinary trainer")
            k = O.contradiction(s, lvl)
            if k:
                res.err(f"{tid}[{i}] {s[8:]} L{lvl}: evolution-stage contradiction ({k}-evolved)")
            if m["item"] and m["item"] != "ITEM_NONE" and tid.split("_")[0] in ("youngster", "lass", "bug", "school"):
                res.warn(f"{tid}[{i}]: held item {m['item'][5:]} on a beginner trainer")
            for mv in m["moves"] or []:
                if mv not in legal_moves(s, lvl):
                    res.warn(f"{tid}[{i}] {s[8:]} L{lvl}: untouched non-learnset move {mv[5:]}")
                dm = move_data(mv)
                if (dm and is_attack(mv) and dm["power"] <= 40 and lvl >= 35 and dm["type"] not in species_data(s)["types"]
                        and dm["effect"]["type"] == "BATTLE_EFFECT_HIT"):
                    res.warn(f"{tid}[{i}]: suspiciously weak move {mv[5:]} at L{lvl}")
        for s, n in names.items():
            if n > 1 and not d["double_battle"]:
                res.warn(f"{tid}: repeated species {s[8:]} x{n}")
        for m in d["party"]:
            if m["iv_scale"] > 255:
                res.warn(f"{tid}: unusual iv_scale {m['iv_scale']} (>255 wraps in the u8 IV computation)")
    for s, n in use.most_common(8):
        if n > O.CAP_SPECIES:
            res.warn(f"species usage {s[8:]} x{n} across active ordinary trainers (cap {O.CAP_SPECIES})")
    stats["distinct_species_active"] = len(use)
    return stats


def check_all_iv(res: Result, data: dict) -> None:
    seen = collections.Counter()
    for tid, d in data.items():
        if O.is_ordinary(tid):
            continue
        for m in d["party"]:
            if m["iv_scale"] > 255:
                res.warn(f"{tid}: unusual iv_scale {m['iv_scale']} on {m['species'][8:]} (preserved, not normalized)")
            seen[m["iv_scale"]] += 1


# ---------------------------------------------------------------------------------------------------------------- power curve
def strong_stab(party_member: dict) -> int:
    types = species_data(party_member["species"])["types"]
    n = 0
    for mv in party_member["moves"] or []:
        dm = move_data(mv)
        if dm and dm["power"] >= 70 and dm["type"] in types and is_attack(mv):
            n += 1
    return n


def power_curve(res: Result, rules: dict, data: dict) -> list[str]:
    rows = []
    prev = None
    for tid in rules["boss_curve_sequence"]:
        party = data[tid]["party"]
        if any(species_data(m["species"]) is None for m in party):
            continue
        lv = [m["level"] for m in party]
        avg_lv = sum(lv) / len(lv)
        avg_bst = sum(bst(m["species"]) for m in party) / len(party)
        finals = sum(1 for m in party if is_final(m["species"]) or O.contradiction(m["species"], m["level"]) == "over")
        held = sum(1 for m in party if m["item"] and m["item"] != "ITEM_NONE")
        stab = sum(strong_stab(m) for m in party)
        strength = avg_bst * (avg_lv / 50.0)
        flag = ""
        if prev:
            pr_bst, pr_str, pr_sz = prev["bst"], prev["strength"], prev["size"]
            if avg_bst / pr_bst > rules["power_curve"]["bst_jump_flag_ratio"] and len(party) <= pr_sz:
                flag = "BST jump without party-size increase"
            if strength / pr_str > rules["power_curve"]["strength_jump_flag_ratio"] and len(party) <= pr_sz:
                flag = (flag + "; " if flag else "") + "strength jump without party-size increase"
            if flag:
                why = rules["power_curve"].get("explained", {}).get(tid)
                if why:
                    res.note(f"power-curve {tid}: {flag} — explained: {why}")
                    flag += " (explained)"
                else:
                    res.warn(f"power-curve {tid}: {flag}")
        rows.append(f"| `{tid}` | {len(party)} | {avg_lv:.1f} | {max(lv)} | {avg_bst:.0f} | {finals}/{len(party)} | {held} | {stab} | "
                    f"{strength:.0f} | {flag or '-'} |")
        prev = {"bst": avg_bst, "strength": strength, "size": len(party)}
    return rows


# ---------------------------------------------------------------------------------------------------------------- report
def write_report(res: Result, man: dict, ordinary_stats: dict, rival_rows: list[str], curve_rows: list[str]) -> None:
    inv = man["inventory"]
    cat_counts = collections.Counter(e["category"] for e in man["entries"])
    out = ["# Trainer Overhaul — Validation Report", "",
           f"Generated by `tools/overhaul/validate_trainers.py` (deterministic). Base commit `{BASE_COMMIT}`.", "",
           f"**Result: {'PASS' if not res.errors else 'FAIL'}** — {len(res.errors)} error(s), {len(res.warnings)} warning(s), "
           f"{len(res.notes)} note(s).", "",
           "Runtime trainer QA: **PENDING** (not performed; see TRAINER_IMPLEMENTATION_PLAN.md section 8).", "",
           "## Inventory (base)", "", f"- trainer records: {inv['total_trainer_records']} (map-placed active: {inv['active_map_placed_trainers']})",
           f"- Frontier: {inv['frontier']['file_count']} files under `{inv['frontier']['directory']}` — fingerprint unchanged "
           f"(`{inv['frontier']['fingerprint_sha256'][:16]}…`)", "", "| category | records |", "|---|---:|"]
    out += [f"| {k} | {v} |" for k, v in inv["counts"].items()]
    out += ["", "## Manifest coverage", "", f"{man['entry_count']} intentionally changed records.", "", "| category | changed |", "|---|---:|"]
    out += [f"| {k} | {v} |" for k, v in sorted(cat_counts.items())]
    out += ["", "## iv_scale", "", man["iv_scale_semantics"]["formula"] + ".", "", man["iv_scale_semantics"]["policy"] + ".", "",
            "## Rival branch structure (generated comparison)", "",
            "Slots listed are the only slots whose species differ between starter branches; levels, shared-slot moves and items are identical.", "",
            "| fight | size | branch-dependent slots | player Turtwig | player Chimchar | player Piplup |", "|---|---:|---|---|---|---|"]
    out += rival_rows
    out += ["", "## Power-curve audit (heuristic, mandatory boss sequence)", "",
            "strength = avg BST × avg level / 50. Flags are for human review only.", "",
            "| boss | size | avg Lv | ace Lv | avg BST | final/over-evolved | held | STAB≥70 | strength | flag |", "|---|---:|---:|---:|---:|---|---:|---:|---:|---|"]
    out += curve_rows
    out += ["", "## Ordinary trainers", "", f"- ordinary records checked: {ordinary_stats.get('ordinary_records', 0)}",
            f"- distinct species used by active map-placed ordinary trainers: {ordinary_stats.get('distinct_species_active', 0)}", ""]
    for title, items in (("Errors", res.errors), ("Warnings", res.warnings), ("Notes", res.notes)):
        out += [f"## {title} ({len(items)})", ""]
        if not items:
            out += ["none", ""]
            continue
        agg = collections.Counter(x.split(":")[0].split("[")[0] for x in items)
        shown = items[:150]
        out += [f"- {x}" for x in shown]
        if len(items) > len(shown):
            out += [f"- … {len(items) - len(shown)} more (run the validator for the full list)"]
        out += [""]
    with open(p(REPORT), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-report", action="store_true")
    ap.add_argument("--no-git", action="store_true", help="skip base-commit diff checks (tests)")
    a = ap.parse_args()
    res = Result()
    rules, man = load(RULES), load(MANIFEST)
    data = check_source(res, rules)
    check_manifest(res, man, data, not a.no_git)
    check_bosses(res, rules, man, data)
    rival_rows = rival_structure(res, man, data)
    stats = check_ordinary(res, data, category_of(man))
    check_all_iv(res, data)
    curve = power_curve(res, rules, data)
    if not a.no_report:
        write_report(res, man, stats, rival_rows, curve)
    for m in res.errors[:80]:
        print("ERROR", m)
    print(f"trainer validation: {len(res.errors)} errors, {len(res.warnings)} warnings, {len(res.notes)} notes")
    return 1 if res.errors else 0


if __name__ == "__main__":
    sys.exit(main())
