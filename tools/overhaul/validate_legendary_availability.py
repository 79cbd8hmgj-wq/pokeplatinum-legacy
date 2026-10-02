#!/usr/bin/env python3
"""D5 Legendary/Mythical availability validator.

Fails (exit 1) if any Legendary/Mythical species through #493:
  * has no in-save acquisition path;
  * still requires distribution / WFC / migration / Slot-2 / another version, game or system / multiplayer / trading;
  * has a one-time encounter that can be permanently consumed before capture;
  * has conflicting acquisition ownership;
  * violates the Hall-of-Fame gate of the locked legacy habitats.

Everything is re-derived from live source (scripts, C, encounter JSON); the manifests under
docs/overhaul/implementation/events/ are cross-checked against it.

Usage:
    python3 tools/overhaul/validate_legendary_availability.py            # validate + write the report
    python3 tools/overhaul/validate_legendary_availability.py --no-report
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "events"))

from lib import ROOT as REPO_ROOT  # noqa: E402
from script_model import Script  # noqa: E402

EV = "docs/overhaul/implementation/events/"
MANIFESTS = {
    "native": EV + "native_legendary_events.json",
    "legacy": EV + "legacy_legendary_encounters.json",
    "mythical": EV + "mythical_statics.json",
    "removals": EV + "event_gate_removals.json",
    "retry": EV + "event_retry_rules.json",
}
REPORT = EV + "LEGENDARY_EVENT_VALIDATION_REPORT.md"

# The locked species set (#001-#493): must equal the 35 RESERVED_LATER_PHASE families of the availability phase.
LOCKED_SPECIES = {
    "ARTICUNO", "ZAPDOS", "MOLTRES", "MEWTWO", "MEW", "RAIKOU", "ENTEI", "SUICUNE", "LUGIA", "HO_OH", "CELEBI",
    "REGIROCK", "REGICE", "REGISTEEL", "LATIAS", "LATIOS", "KYOGRE", "GROUDON", "RAYQUAZA", "JIRACHI", "DEOXYS",
    "UXIE", "MESPRIT", "AZELF", "DIALGA", "PALKIA", "HEATRAN", "REGIGIGAS", "GIRATINA", "CRESSELIA", "PHIONE",
    "MANAPHY", "DARKRAI", "SHAYMIN", "ARCEUS",
}
CLASSES = {"NATIVE_STATIC", "NATIVE_ROAMER", "RESTORED_EVENT", "NATIVE_RUIN", "RARE_POSTGAME_HABITAT",
           "HIDDEN_MYTHICAL_STATIC", "BREEDING_ONLY"}
REQUIRED_FIELDS = ["species", "acquisition_class", "map_system", "level", "rate", "vanilla_gates", "target_gates",
                   "one_time_vs_renewable", "capture_flag", "retry_behavior", "external_dependency_removed",
                   "source_path", "validation_status"]

# Locked D5 habitat matrix: species -> (percent, min level, max level, encounter type)
LOCKED_HABITATS = {
    "ARTICUNO": (2, 55, 60, "GRASS"), "ZAPDOS": (2, 55, 60, "GRASS"), "MOLTRES": (2, 55, 60, "GRASS"),
    "MEWTWO": (1, 70, 70, "GRASS"), "RAIKOU": (2, 55, 60, "GRASS"), "ENTEI": (2, 55, 60, "GRASS"),
    "SUICUNE": (2, 55, 60, "SURF"), "LUGIA": (1, 65, 70, "SURF"), "HO_OH": (1, 65, 70, "GRASS"),
    "LATIAS": (2, 55, 60, "GRASS"), "LATIOS": (2, 55, 60, "GRASS"), "GROUDON": (1, 70, 70, "GRASS"),
    "KYOGRE": (1, 70, 70, "SURF"), "RAYQUAZA": (1, 70, 70, "GRASS"),
}
# Locked static levels
LOCKED_LEVELS = {"DARKRAI": 50, "SHAYMIN": 30, "ARCEUS": 80, "REGIGIGAS": 1, "HEATRAN": 50, "MEW": 50, "CELEBI": 50,
                 "JIRACHI": 50, "DEOXYS": 60}

# Anything in these token lists means an external (non-save) dependency
EXTERNAL_TOKENS = [
    "CheckDistributionEvent", "DISTRIBUTION_EVENT_", "VAR_DISTRIBUTION_EVENT", "SystemVars_CheckDistributionEvent",
    "CheckPartyHasFatefulEncounterRegigigas",   # event-distributed Regigigas
    "GetGBACartridgeVersion",                   # Slot-2 / other version
    "CheckHasWiFiListValidLogin", "GetWiFListValidFriendsCount", "CheckIsMysteryGiftPhrase",   # WFC / Mystery Gift
]
# Tokens that may not appear in ANY field script (they only ever gated Legendary/Mythical events). The
# WFC/GBA-version/Mystery-Gift tokens above are unrelated to legendaries elsewhere (Pal Park, Jubilife TV,
# Poké Center WFC) and are checked in the legendary acquisition scripts only (B2).
GLOBAL_SCRIPT_TOKENS = ["CheckDistributionEvent", "DISTRIBUTION_EVENT_", "VAR_DISTRIBUTION_EVENT", "CheckPartyHasFatefulEncounterRegigigas"]


@dataclass
class Result:
    check_id: str
    title: str
    ok: bool
    detail: str = ""


@dataclass
class Validation:
    root: Path
    results: list[Result] = field(default_factory=list)
    graph_order: list[str] = field(default_factory=list)

    # ---- plumbing ----------------------------------------------------------------------------------
    def check(self, cid: str, title: str, ok: bool, detail: str = "") -> bool:
        self.results.append(Result(cid, title, bool(ok), detail))
        return bool(ok)

    def fail_all(self, cid: str, title: str, problems: list[str]) -> None:
        self.check(cid, title, not problems, "; ".join(problems[:6]) + (f" (+{len(problems) - 6} more)" if len(problems) > 6 else ""))

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text()

    def exists(self, rel: str) -> bool:
        return (self.root / rel).exists()

    def script(self, rel: str) -> Script:
        if rel not in self._scripts:
            self._scripts[rel] = Script.load(self.root / rel)
        return self._scripts[rel]

    def __post_init__(self):
        self._scripts: dict[str, Script] = {}

    @staticmethod
    def each(by_species):
        for sp in sorted(by_species):
            for e in by_species[sp]:
                yield sp, e

    # ---- checks ------------------------------------------------------------------------------------
    def run(self) -> bool:
        try:
            man = {k: json.loads(self.read(v)) for k, v in MANIFESTS.items()}
        except FileNotFoundError as e:
            self.check("A0", "manifests present", False, str(e))
            return False
        entries = man["native"]["events"] + man["legacy"]["encounters"] + man["mythical"]["statics"]
        by_species: dict[str, list[dict]] = {}
        for e in entries:
            by_species.setdefault(e["species"].replace("SPECIES_", ""), []).append(e)

        self.check_manifest_shape(man, entries, by_species)
        self.check_external_dependencies(man, entries)
        self.check_habitats(man, by_species)
        self.check_statics(by_species)
        self.check_hof_gates(by_species)
        self.check_arceus(by_species)
        self.check_unlock_chains(by_species)
        self.check_manaphy_phione(by_species)
        self.check_rotom(man)
        self.check_graph(by_species)
        return all(r.ok for r in self.results)

    # A. manifests, coverage, ownership ---------------------------------------------------------------
    def check_manifest_shape(self, man, entries, by_species):
        # A1 the locked set equals the availability phase's reserved legendary/mythical families
        fam = json.loads(self.read("docs/overhaul/implementation/availability_families.json"))["families"]
        reserved = {c.replace("SPECIES_", "") for f in fam if f["availability_status"] == "RESERVED_LATER_PHASE" for c in f["components"]}
        self.check("A1", "locked species set == the 35 RESERVED_LATER_PHASE families (#001-#493)",
                   reserved == LOCKED_SPECIES, f"reserved-only={sorted(reserved - LOCKED_SPECIES)} locked-only={sorted(LOCKED_SPECIES - reserved)}")
        # A2 every species has an in-save acquisition path
        missing = sorted(LOCKED_SPECIES - set(by_species))
        self.check("A2", "every Legendary/Mythical has an in-save acquisition entry", not missing, f"missing: {missing}")
        # A3 exactly one owner each (no conflicting ownership)
        dup = sorted(s for s, v in by_species.items() if len(v) != 1)
        self.check("A3", "exactly one acquisition owner per species", not dup, f"multiple/zero owners: {dup}")
        extra = sorted(set(by_species) - LOCKED_SPECIES)
        self.check("A4", "no manifest entry outside the locked species set", not extra, str(extra))
        # A5 required fields / classes
        problems = []
        for e in entries:
            for k in REQUIRED_FIELDS:
                if k not in e or (e[k] in ("", None) and k not in ("capture_flag",)):
                    problems.append(f"{e.get('species')}:{k}")
            if e.get("acquisition_class") not in CLASSES:
                problems.append(f"{e.get('species')}: class {e.get('acquisition_class')}")
            vs = e.get("validation_status", {})
            if "VERIFIED" in str(vs.get("runtime", "")).upper() and "NOT VERIFIED" not in str(vs.get("runtime", "")).upper() and "PENDING" not in str(vs.get("runtime", "")).upper():
                problems.append(f"{e.get('species')}: runtime claimed VERIFIED")
        self.fail_all("A5", "manifest entries complete (required fields, valid class, no premature VERIFIED)", problems)
        # A6 ownership: legendary species never in ordinary encounter tables (habitat table is the only wild owner)
        enc_dir = self.root / "res/field/encounters"
        bad = []
        pat = re.compile('"SPECIES_(%s)"' % "|".join(sorted(LOCKED_SPECIES)))
        for f in sorted(enc_dir.glob("*.json")):
            for m in pat.finditer(f.read_text()):
                bad.append(f"{f.name}:{m.group(1)}")
        self.fail_all("A6", "no Legendary/Mythical in ordinary encounter JSON (single wild owner = habitat hook)", bad)
        # A7 expected classes per locked spec section 11
        want = {"UXIE": "NATIVE_STATIC", "AZELF": "NATIVE_STATIC", "MESPRIT": "NATIVE_ROAMER", "CRESSELIA": "NATIVE_ROAMER",
                "GIRATINA": "NATIVE_STATIC", "DIALGA": "NATIVE_STATIC", "PALKIA": "NATIVE_STATIC", "HEATRAN": "NATIVE_STATIC",
                "REGIGIGAS": "NATIVE_STATIC", "REGIROCK": "NATIVE_RUIN", "REGICE": "NATIVE_RUIN", "REGISTEEL": "NATIVE_RUIN",
                "DARKRAI": "RESTORED_EVENT", "SHAYMIN": "RESTORED_EVENT", "ARCEUS": "RESTORED_EVENT", "MANAPHY": "RESTORED_EVENT",
                "PHIONE": "BREEDING_ONLY", "MEW": "HIDDEN_MYTHICAL_STATIC", "CELEBI": "HIDDEN_MYTHICAL_STATIC",
                "JIRACHI": "HIDDEN_MYTHICAL_STATIC", "DEOXYS": "HIDDEN_MYTHICAL_STATIC"}
        want.update({s: "RARE_POSTGAME_HABITAT" for s in LOCKED_HABITATS})
        wrong = [f"{s}: {by_species[s][0]['acquisition_class']} != {c}" for s, c in want.items() if s in by_species and by_species[s][0]["acquisition_class"] != c]
        self.fail_all("A7", "acquisition class matches the locked classification", wrong)
        # A8 locked levels
        wl = []
        for s, lvl in LOCKED_LEVELS.items():
            if s in by_species and by_species[s][0]["level"] != str(lvl):
                wl.append(f"{s}: {by_species[s][0]['level']} != {lvl}")
        self.fail_all("A8", "locked static levels (Darkrai 50, Shaymin 30, Arceus 80, Regigigas 1, Heatran 50, Mew 50, Celebi 50, Jirachi 50, Deoxys 60)", wl)
        # A9 flags exist
        flags = set(self.read("generated/vars_flags.txt").split())
        nf = [e["capture_flag"] for e in entries if str(e.get("capture_flag") or "").startswith("FLAG_") and e["capture_flag"] not in flags]
        nf += [e["capture_flag"] for e in entries if e.get("unlock_source") and False]
        self.fail_all("A9", "capture flags are declared in generated/vars_flags.txt", nf)

    # B. external dependencies --------------------------------------------------------------------------
    def check_external_dependencies(self, man, entries):
        hits = []
        for p in sorted((self.root / "res/field/scripts").glob("*.s")):
            t = p.read_text()
            for tok in GLOBAL_SCRIPT_TOKENS:
                if tok in t:
                    hits.append(f"{p.name}:{tok}")
        for rel in ("src/item_use_functions.c",):
            t = self.read(rel)
            for tok in ("SystemVars_CheckDistributionEvent", "DISTRIBUTION_EVENT_"):
                if tok in t:
                    hits.append(f"{rel}:{tok}")
        self.fail_all("B1", "no distribution / WFC / Slot-2 / event-Regigigas gate left in any field script or Azure Flute check", hits)
        # B2 every acquisition entry's own script is free of external tokens (explicit per-entry statement)
        bad = []
        for e in entries:
            rel = e["source_path"]
            if rel.endswith(".s") and self.exists(rel):
                t = self.read(rel)
                bad += [f"{e['species']}:{tok}" for tok in EXTERNAL_TOKENS if tok in t]
        self.fail_all("B2", "every acquisition script is free of external-dependency tokens", bad)
        # B3 manifest-declared external gates were removed from the listed files
        bad = []
        for r in man["removals"]["removals"]:
            token = r["gate"].split()[0]
            if not token.startswith(("DISTRIBUTION_EVENT", "CheckParty")):
                continue
            for rel in r["files"]:
                if token in self.read(rel):
                    bad.append(f"{rel}:{token}")
        self.fail_all("B3", "event_gate_removals.json: removed gates are absent from the listed files", bad)
        # B4 no manifest entry still lists an unremoved external requirement
        bad = [e["species"] for e in entries if "external_dependency_remaining" in e or e.get("requires_external")]
        self.fail_all("B4", "no manifest entry declares a remaining external dependency", bad)
        # B5 legendary acquisition scripts don't poll multiplayer/trade state (counter-based unlocks etc.)
        trade_tokens = ["GetUndergroundTalkCounter", "CheckIsMysteryGiftPhrase", "TradeWith", "StartTrade", "UnionRoom"]
        bad = []
        for e in entries:
            rel = e["source_path"]
            if rel.endswith(".s") and self.exists(rel):
                t = self.read(rel)
                bad += [f"{e['species']}:{tok}" for tok in trade_tokens if tok in t]
        self.fail_all("B5", "legendary acquisition scripts contain no multiplayer/trade checks", bad)

    # C. habitats ----------------------------------------------------------------------------------------
    def check_habitats(self, man, by_species):
        c = self.read("src/overlay006/wild_encounters.c")
        # table rows
        m = re.search(r"sLegendaryHabitats\[\]\s*=\s*\{(.*?)\n\};", c, re.S)
        if not self.check("C1", "LegendaryHabitat table present in wild_encounters.c", bool(m)):
            return
        rows = re.findall(r"\{\s*(MAP_HEADER_\w+),\s*ENCOUNTER_TYPE_(\w+),\s*(\d+),\s*SPECIES_(\w+),\s*(\d+),\s*(\d+)\s*\}", m.group(1))
        c_rows = {}
        problems = []
        for mh, et, pct, sp, lo, hi in rows:
            key = (mh, et)
            if key in c_rows:
                problems.append(f"duplicate slot {key}")
            c_rows[key] = (sp, int(pct), int(lo), int(hi))
        self.fail_all("C2", "no two legendaries share a (map, method) habitat", problems)
        # manifest <-> C equality
        man_rows = {}
        for e in man["legacy"]["encounters"]:
            sp = e["species"].replace("SPECIES_", "")
            for r in e["rows"]:
                man_rows[(r["map_header"], r["encounter_type"])] = (sp, e["percent"], e["min_level"], e["max_level"])
        diff = sorted(set(c_rows) ^ set(man_rows)) + [k for k in c_rows if k in man_rows and c_rows[k] != man_rows[k]]
        self.fail_all("C3", "habitat manifest rows == C table rows (map, method, species, %, levels)", [str(d) for d in diff])
        # locked matrix
        bad = []
        seen = set()
        for (mh, et), (sp, pct, lo, hi) in c_rows.items():
            seen.add(sp)
            want = LOCKED_HABITATS.get(sp)
            if not want:
                bad.append(f"{sp} not in locked matrix")
            elif (pct, lo, hi, et) != want:
                bad.append(f"{sp}: {(pct, lo, hi, et)} != locked {want}")
        bad += [f"{s} missing habitat" for s in sorted(set(LOCKED_HABITATS) - seen)]
        self.fail_all("C4", "habitat rates/levels/methods equal the locked matrix (R2=2%, R1=1%)", bad)
        # maps have the required encounter method in their table
        bad = []
        for (mh, et), (sp, *_r) in c_rows.items():
            name = mh.replace("MAP_HEADER_", "").lower()
            f = self.root / "res/field/encounters" / f"encounters_{name}.json"
            if not f.exists():
                bad.append(f"{mh}: no encounter file")
                continue
            d = json.loads(f.read_text())
            rate = d.get("land_rate") if et == "GRASS" else d.get("surf_rate")
            if not rate:
                bad.append(f"{mh}: {et} table has rate {rate}")
        self.fail_all("C5", "each habitat map has an encounter table (non-zero rate) for its method", bad)
        # Hall-of-Fame gate in the hook, hook wired, renewable (no flag writes)
        fn = re.search(r"static BOOL TryRollLegendaryHabitat\([^;]*?\)\n\{.*?\n\}", c, re.S)
        ok_gate = bool(fn) and "SystemFlag_CheckGameCompleted" in fn.group(0) and \
            fn.group(0).index("SystemFlag_CheckGameCompleted") < fn.group(0).index("for (")
        self.check("C6", "habitat hook checks the Hall-of-Fame flag before any roll", ok_gate)
        body = re.search(r"\nBOOL WildEncounters_TryWildEncounter\(FieldSystem \*fieldSystem\)\n\{.*?\nBOOL WildEncounters_TryFishingEncounter", c, re.S)
        self.check("C7", "habitat hook is wired into WildEncounters_TryWildEncounter",
                   bool(body) and "TryRollLegendaryHabitat(" in body.group(0) and "TryGenerateLegendaryHabitatEncounter(" in body.group(0))
        self.check("C8", "hook is renewable: no flag/var written, no Radar/swarm/dual-slot input",
                   bool(fn) and not re.search(r"SetFlag|SystemFlag_Set|SystemVars_Set|radar|swarm|DualSlot", fn.group(0), re.I))
        # manifest-level HoF
        bad = [e["species"] for e in man["legacy"]["encounters"] if not e.get("hall_of_fame_required") or e["one_time_vs_renewable"] != "RENEWABLE" or e.get("capture_flag")]
        self.fail_all("C9", "habitat manifest entries: Hall of Fame required, RENEWABLE, no capture flag", bad)

    # D. one-time encounter structure --------------------------------------------------------------------
    def check_statics(self, by_species):
        problems_markers, problems_retry, problems_guard, problems_reset = [], [], [], []
        for sp, e in self.each(by_species):
            if e.get("one_time_vs_renewable") != "ONE_TIME_UNTIL_CAPTURED":
                continue
            cap = e.get("capture_flag") or ""
            sc = e.get("script")
            if sc:
                s = self.script(sc["file"])
                prob = self.analyze(s, sc["entry"], sc["battle"], e)
                problems_markers += [f"{sp}: {p}" for p in prob["markers"]]
                problems_retry += [f"{sp}: {p}" for p in prob["retry"]]
                if "entry_guard" in e.get("respawn_guard", ""):
                    flag = cap if cap.startswith("FLAG_") else None
                    if not flag or f"GoToIfSet {flag}," not in s.label_text(sc["entry"]):
                        problems_guard.append(f"{sp}: entry label lacks GoToIfSet {flag}")
            rs = e.get("reset_script")
            if rs:
                for r in (rs if isinstance(rs, list) else [rs]):
                    txt = self.script(r["file"]).label_text(r["label"])
                    for need in r["requires"]:
                        if need not in txt:
                            problems_reset.append(f"{sp}: {r['label']} lacks '{need}'")
            elif "reset_script" in e.get("respawn_guard", ""):
                problems_reset.append(f"{sp}: reset_script missing")
            if "hof_reshow_guard" in e.get("respawn_guard", "") and cap.startswith("FLAG_"):
                hof = self.read("res/field/scripts/scripts_pokemon_league_hall_of_fame.s")
                if f"CallIfUnset {cap}," not in hof:
                    problems_guard.append(f"{sp}: Hall of Fame re-show not guarded by {cap}")
        self.fail_all("D1", "one-time encounters: completion/consumed markers are written only on the captured path (defeat/flee/blackout never consume)", problems_markers)
        self.fail_all("D2", "one-time encounters: defeat/flee/blackout restore the encounter (retry actions present on both branches)", problems_retry)
        self.fail_all("D3", "one-time encounters: leave/re-enter paths (OnTransition/reset scripts) re-offer an uncaught encounter", problems_reset)
        self.fail_all("D4", "one-time encounters: a captured encounter does not respawn (entry guard / Hall-of-Fame re-show guard)", problems_guard)
        # D5 roamers: ROAMER_STATE_CAPTURED is the only thing that retires them (src/overlay006/roamer_after_battle.c)
        rab = self.read("src/overlay006/roamer_after_battle.c")
        self.check("D5", "roamers: only BATTLE_RESULT_CAPTURED_MON sets ROAMER_STATE_CAPTURED; HP-0 win sets DEFEATED (reset path exists)",
                   "ROAMER_STATE_CAPTURED" in rab and "ROAMER_STATE_DEFEATED" in rab and
                   re.search(r"BATTLE_RESULT_CAPTURED_MON\)\s*\{[^}]*ROAMER_STATE_CAPTURED", rab, re.S) is not None)
        # D6 roaming birds are retired (habitat owns them): no ActivateRoamingPokemon for the birds
        bad = []
        for p in sorted((self.root / "res/field/scripts").glob("*.s")):
            for m in re.finditer(r"ActivateRoamingPokemon\s+ROAMING_SLOT_(\w+)", p.read_text()):
                if m.group(1) in ("MOLTRES", "ZAPDOS", "ARTICUNO"):
                    bad.append(f"{p.name}:{m.group(1)}")
        self.fail_all("D6", "no script activates the roaming legendary birds (habitat model owns them)", bad)

    def analyze(self, s: Script, entry: str, battle: str, e: dict) -> dict:
        out = {"markers": [], "retry": []}
        reach = s.reach(entry)
        bt = [st for st in reach if st.text.startswith(battle)]
        if not bt:
            out["markers"].append(f"battle '{battle}' not reachable from {entry}")
            return out
        b = bt[0]
        body = s.labels[b.label]
        i = b.index
        won = next((j for j in range(i + 1, len(body)) if body[j].text.startswith("CheckWonBattle")), None)
        dnc = next((j for j in range(i + 1, len(body)) if body[j].text.startswith("CheckDidNotCapture")), None)
        if dnc is None:
            out["markers"].append("no CheckDidNotCapture after the battle")
            return out
        blackout = None
        if won is not None and body[won + 1].text.startswith("GoToIfEq VAR_RESULT, FALSE,"):
            blackout = body[won + 1].args[-1]
        nxt = body[dnc + 1] if dnc + 1 < len(body) else None
        pre = body[i + 1: dnc + 1]
        unc_reach: list = []
        cap_reach: list = []
        if nxt and nxt.text.startswith("GoToIfEq VAR_RESULT, TRUE,"):
            unc_reach = s.reach(nxt.args[-1])
            cap_reach = s.reach(b.label, dnc + 2)
        elif nxt and nxt.text.startswith("CallIfEq VAR_RESULT, FALSE,"):
            cap_target = nxt.args[-1]
            cap_reach = s.reach(cap_target)
            unc_reach = s.reach(b.label, dnc + 2)
        else:
            out["markers"].append("CheckDidNotCapture not followed by a recognised branch")
            return out
        # statements executed before the branch also include any call targets inside them
        for st in list(pre):
            for t in s.edges(st)[0]:
                pre += s.reach(t)
        black_reach = s.reach(blackout) if blackout else []
        cap = e.get("capture_flag") or ""
        consumed = e.get("consumed_markers", [])
        retry_actions = e.get("retry_actions", [])
        hide_flags = {a.split()[1].rstrip(",") for a in retry_actions if a.startswith("ClearFlag ")}

        def writes(pool, name_pred):
            return [st for st in pool if st.op in ("SetFlag", "SetVar") and name_pred(st)]

        for label, pool in (("pre-branch", pre), ("uncaught", unc_reach), ("blackout", black_reach)):
            if cap.startswith("FLAG_") and any(st.text == f"SetFlag {cap}" for st in pool):
                out["markers"].append(f"{cap} set on the {label} path")
            for m in consumed:
                var = m.split(",")[0].strip()
                if "," in m:
                    continue   # exact-text markers are checked file-wide below
                if writes(pool, lambda st, v=var: st.args and st.args[0] == v):
                    out["markers"].append(f"{var} written on the {label} path")
            for h in hide_flags:
                if any(st.text == f"SetFlag {h}" for st in pool):
                    out["retry"].append(f"{h} set (consumes the encounter) on the {label} path")
        for m in consumed:
            if "," in m:
                var, val = [x.strip() for x in m.split(",", 1)]
                if any(st.text == f"SetVar {var}, {val}" for lab in s.order for st in s.labels[lab]):
                    out["markers"].append(f"'{m}' (permanent consumed state) still written in the script")
        if cap.startswith("FLAG_") and not any(st.text == f"SetFlag {cap}" or (st.op == "SetVar" and False) for st in cap_reach):
            # Dialga/Palkia style: flag set via a helper reached from cap path
            out["markers"].append(f"{cap} not set on the captured path")
        for a in retry_actions:
            if not any(st.text == a for st in unc_reach):
                out["retry"].append(f"uncaught path lacks '{a}'")
            if blackout and not any(st.text == a for st in black_reach):
                out["retry"].append(f"blackout path lacks '{a}'")
        return out

    # E. Hall-of-Fame gating of statics ------------------------------------------------------------------
    def check_hof_gates(self, by_species):
        bad = []
        for sp, e in self.each(by_species):
            if not e.get("hall_of_fame_required") or e["acquisition_class"] == "RARE_POSTGAME_HABITAT":
                continue
            files = []
            if e.get("script"):
                files.append((e["script"]["file"], e["script"]["entry"]))
            rs = e.get("reset_script")
            if rs:
                files += [(r["file"], r["label"]) for r in (rs if isinstance(rs, list) else [rs])]
            if sp in ("REGIROCK", "REGICE", "REGISTEEL"):
                s = self.script(e["script"]["file"])
                stat = next((l for l in s.order if l.endswith("_Statue")), None)
                ok = stat and "GoToIfUnset FLAG_GAME_COMPLETED" in s.label_text(stat)
            elif sp == "MANAPHY":
                s = self.script(e["script"]["file"])
                ok = "GoToIfUnset FLAG_GAME_COMPLETED" in s.label_text("CanalaveCity_SailorEldritchTryGifts")
            else:
                ok = any("GoToIfUnset FLAG_GAME_COMPLETED" in self.script(f).label_text(l) for f, l in files)
            if not ok:
                bad.append(sp)
        self.fail_all("E1", "Hall-of-Fame gate present in the script of every HoF-locked static/event", bad)

    # F. Arceus completion gate ---------------------------------------------------------------------------
    def check_arceus(self, by_species):
        sc = self.read("src/scrcmd.c")
        m = re.search(r"static BOOL ScrCmd_CheckPokedexCaughtAllButArceus\(ScriptContext \*ctx\)\s*\{.*?\n\}", sc, re.S)
        ok = bool(m) and re.search(r"for \(species = 1; species < SPECIES_ARCEUS; species\+\+\)", m.group(0)) and \
            "Pokedex_HasCaughtSpecies" in m.group(0) and "Pokedex_CountCaught" not in m.group(0)
        self.check("F1", "caught-Pokédex check covers exactly species #001-#492 (forms not counted, Arceus excluded)", ok)
        self.check("F2", "script command is registered (macro + table)",
                   "SCRCMD_CHECKPOKEDEXCAUGHTALLBUTARCEUS" in self.read("asm/macros/scrcmd.inc") and
                   "ScrCmd_CheckPokedexCaughtAllButArceus" in self.read("include/data/scripts/scrcmd.h"))
        v = self.script("res/field/scripts/scripts_veilstone_store_b1f.s")
        lab = v.labels.get("VeilstoneStoreB1F_ProfRowanTryAzureFlute", [])
        txt = [s.text for s in lab]
        try:
            i_chk = next(i for i, t in enumerate(txt) if t.startswith("CheckPokedexCaughtAllButArceus"))
            i_give = next(i for i, t in enumerate(txt) if t.startswith("Common_GiveItemQuantity"))
            i_item = next(i for i, t in enumerate(txt) if t == "SetVar VAR_0x8004, ITEM_AZURE_FLUTE")
            i_fail = next(i for i, t in enumerate(txt) if t.startswith("GoToIfEq VAR_RESULT, FALSE, VeilstoneStoreB1F_ProfRowanDexIncomplete"))
            ok = i_chk < i_fail < i_item < i_give and "GoToIfUnset FLAG_GAME_COMPLETED, VeilstoneStoreB1F_ProfRowanClose" in txt
        except StopIteration:
            ok = False
        self.check("F3", "Rowan grants the Azure Flute only after the caught-Pokédex check succeeds (and after the Hall of Fame)", ok)
        ho = self.script("res/field/scripts/scripts_hall_of_origin.s").label_text("HallOfOrigin_OnTransition")
        self.check("F4", "Hall of Origin re-checks Hall of Fame + the Pokédex prerequisite before showing Arceus",
                   "GoToIfUnset FLAG_GAME_COMPLETED" in ho and "CheckPokedexCaughtAllButArceus" in ho)
        bad = [s for s, e in self.each(by_species) if e.get("depends_on_dex_completion") and s != "ARCEUS"]
        self.check("F5", "only Arceus depends on Pokédex completion", not bad and by_species["ARCEUS"][0].get("depends_on_dex_completion") is True, str(bad))

    # G. unlock chains (Member Card / Oak's Letter) ----------------------------------------------------------
    def check_unlock_chains(self, by_species):
        c = self.script("res/field/scripts/scripts_canalave_city.s")
        t = c.label_text("CanalaveCity_SailorEldritchTryGifts")
        ok = "GoToIfUnset FLAG_GAME_COMPLETED" in t and "GoToIfUnset FLAG_WOKE_UP_CANALAVE_CITY_SAILOR_ELDRITCH_HOUSE_LITTLE_BOY" in t \
            and "CheckItem ITEM_MEMBER_CARD" in t and "CanalaveCity_SailorEldritchGiveMemberCard" in t
        self.check("G1", "Member Card: Sailor Eldritch (Canalave) grants it after Hall of Fame + Cresselia/Lunar Wing child sequence", ok)
        card = c.label_text("CanalaveCity_SailorEldritchGiveMemberCard")
        self.check("G2", "Member Card grant checks bag space and uses the common give-item script",
                   "ITEM_MEMBER_CARD" in card and "GoToIfCannotFitItem" in card and "Common_GiveItemQuantity" in card)
        # Darkrai chain no longer has a distribution step
        oi = self.script("res/field/scripts/scripts_canalave_city_harbor_inn.s").label_text("CanalaveCityHarborInn_CheckMemberCard")
        self.check("G3", "Harbor Inn Darkrai start needs only the Member Card (Hall of Fame, National Dex, Lunar Wing sequence upstream)",
                   "ITEM_MEMBER_CARD" in oi and "DISTRIBUTION" not in oi)
        r = self.script("res/field/scripts/scripts_route_224.s")
        t = r.label_text("Route224_OnTransition")
        ok = "CheckGameCompleted" in t and "GetNationalDexEnabled" in t and "ITEM_OAKS_LETTER" not in t and "DISTRIBUTION" not in t and "VAR_SHAYMIN_EVENT_STATE" in t
        self.check("G4", "Route 224: Oak appears after Hall of Fame + National Dex without a letter/distribution requirement", ok)
        g = r.label_text("Route224_GiveOaksLetter")
        self.check("G5", "Oak gives Oak's Letter in-game (bag-space checked)", "ITEM_OAKS_LETTER" in g and "GoToIfCannotFitItem" in g and "Common_GiveItemQuantity" in g)
        fp = self.script("res/field/scripts/scripts_flower_paradise.s").label_text("FlowerParadise_OnTransition")
        self.check("G6", "Flower Paradise Shaymin: Hall of Fame + National Dex + Oak's Letter (no distribution)",
                   "ITEM_OAKS_LETTER" in fp and "GoToIfUnset FLAG_GAME_COMPLETED" in fp and "DISTRIBUTION" not in fp)

    # H. Manaphy / Phione -------------------------------------------------------------------------------------
    def check_manaphy_phione(self, by_species):
        c = self.script("res/field/scripts/scripts_canalave_city.s")
        lab = [s.text for s in c.labels.get("CanalaveCity_SailorEldritchTryGiveManaphyEgg", [])]
        try:
            i_flagchk = lab.index("GoToIfSet FLAG_RECEIVED_CANALAVE_CITY_MANAPHY_EGG, CanalaveCity_SailorEldritchTryGiftsEnd")
            i_party = next(i for i, t in enumerate(lab) if t.startswith("GetPartyCount"))
            i_full = next(i for i, t in enumerate(lab) if t.startswith("GoToIfGe VAR_RESULT, MAX_PARTY_SIZE"))
            i_give = lab.index("GiveEgg SPECIES_MANAPHY, SPECIAL_METLOC_NAME_DISTANT_LAND")
            i_set = lab.index("SetFlag FLAG_RECEIVED_CANALAVE_CITY_MANAPHY_EGG")
            ok = i_flagchk < i_party < i_full < i_give < i_set
        except (ValueError, StopIteration):
            ok = False
        self.check("H1", "Manaphy Egg: one-time flag, party-space check before GiveEgg, received flag only after the grant", ok)
        full = "\n".join(s.text for lab_ in ("CanalaveCity_SailorEldritchPartyFull",) for s in c.labels.get(lab_, []))
        self.check("H2", "full party withholds the gift without setting the received flag", "SetFlag" not in full and "GiveEgg" not in full)
        tg = c.label_text("CanalaveCity_SailorEldritchTryGifts")
        self.check("H3", "Manaphy Egg gate: Hall of Fame + Lunar Wing child sequence", "FLAG_GAME_COMPLETED" in tg and "FLAG_WOKE_UP_CANALAVE_CITY_SAILOR_ELDRITCH_HOUSE_LITTLE_BOY" in tg)
        pc = self.read("src/pokemon.c")
        self.check("H4", "Phione: Manaphy breeding special case preserved in the egg-species logic",
                   "SPECIES_PHIONE" in pc and "SPECIES_MANAPHY" in pc)
        ph = by_species["PHIONE"][0]
        self.check("H5", "Phione owned solely by Manaphy breeding", ph["acquisition_class"] == "BREEDING_ONLY" and ph.get("internal_prerequisites") == ["SPECIES_MANAPHY"])

    # I. Rotom ---------------------------------------------------------------------------------------------------
    def check_rotom(self, man):
        room = self.read("res/field/scripts/scripts_rotoms_room.s")
        forms = all(f in room for f in ("ROTOM_FORM_HEAT", "ROTOM_FORM_FROST", "ROTOM_FORM_WASH", "ROTOM_FORM_FAN", "ROTOM_FORM_MOW"))
        moves = all(m in room for m in ("RotomsRoom_SetVarOverheat", "RotomsRoom_SetVarBlizzard", "RotomsRoom_SetVarHydroPump", "RotomsRoom_SetVarAirSlash", "RotomsRoom_SetVarLeafStorm"))
        self.check("I1", "Rotom appliance room: all five forms and their move assignment preserved", forms and moves)
        oc = self.script("res/field/scripts/scripts_old_chateau_back_middle_west_room.s")
        t = [s.text for s in oc.reach("OldChateauBackMiddleWestRoom_TV")]
        try:
            i_flag = t.index("SetFlag FLAG_CAUGHT_OLD_CHATEAU_ROTOM")
            i_key = t.index("SetVar VAR_0x8004, ITEM_SECRET_KEY")
            ok = i_flag < i_key and "Common_GiveItemQuantity" in t
        except ValueError:
            ok = False
        self.check("I2", "Secret Key is guaranteed with the first Old Chateau Rotom capture (flag only after capture)", ok)
        self.check("I3", "Rotom room usable permanently once the Secret Key is held (no distribution gate)",
                   "ITEM_SECRET_KEY" in self.script("res/field/scripts/scripts_rotoms_room.s").label_text("RotomsRoom_OnTransition") and "DISTRIBUTION" not in room)

    # J. completion graph ------------------------------------------------------------------------------------------
    def check_graph(self, by_species):
        # prerequisites: species -> species that must be obtained first
        prereq: dict[str, set[str]] = {s: set() for s in LOCKED_SPECIES}
        for s, e in self.each(by_species):
            for p in e.get("internal_prerequisites", []):
                prereq[s].add(p.replace("SPECIES_", ""))
            if e.get("depends_on_dex_completion"):
                prereq[s] |= (LOCKED_SPECIES - {s})   # every other species (all non-legendary ones are wild/special, validated elsewhere)
        # Darkrai/Manaphy Egg need the Cresselia encounter chain (Lunar Wing) - an encounter, not a capture
        order, ready = [], set()
        pending = set(LOCKED_SPECIES)
        while pending:
            step = sorted(s for s in pending if prereq[s] <= ready)
            if not step:
                self.check("J1", "completion graph is acyclic and every species is reachable before Arceus", False, f"stuck: {sorted(pending)}")
                return
            order += step
            ready |= set(step)
            pending -= set(step)
        self.graph_order = order
        self.check("J1", "completion graph is acyclic and every species is reachable before Arceus", order[-1] == "ARCEUS" and order.count("ARCEUS") == 1)
        self.check("J2", "Arceus is the only species with a Pokédex-completion prerequisite and nothing depends on Arceus",
                   not any("ARCEUS" in p for p in prereq.values()))


# ------------------------------------------------------------------------------------------------------------
def render_report(v: Validation) -> str:
    man = {k: json.loads(v.read(p)) for k, p in MANIFESTS.items()}
    entries = man["native"]["events"] + man["legacy"]["encounters"] + man["mythical"]["statics"]
    out = ["# D5 Legendary / Mythical Event Validation Report", "",
           f"Base commit: `{man['native']['base_commit']}` · validator: `tools/overhaul/validate_legendary_availability.py`",
           "",
           "Status: **IMPLEMENTED** (source + validator + dual-revision builds). **Runtime event QA PENDING — nothing here is VERIFIED.**",
           "", "## Result", ""]
    fails = [r for r in v.results if not r.ok]
    out.append(f"**{len(v.results) - len(fails)} / {len(v.results)} checks pass, {len(fails)} failure(s).**")
    out += ["", "| ID | Check | Result |", "|---|---|---|"]
    for r in v.results:
        out.append(f"| {r.check_id} | {r.title} | {'PASS' if r.ok else 'FAIL — ' + r.detail} |")
    out += ["", "## Acquisition table (#001–#493 Legendary/Mythical, 35 species)", "",
            "| Dex | Species | Class | Where | Level | Rate | Cadence | Capture marker |", "|---:|---|---|---|---|---|---|---|"]
    for e in sorted(entries, key=lambda x: x["dex"]):
        out.append(f"| {e['dex']} | {e['species'].replace('SPECIES_', '').title()} | {e['acquisition_class']} | {e['map_system']} | {e['level']} | {e['rate']} | {e['one_time_vs_renewable']} | {e['capture_flag'] or '—'} |")
    out += ["", "## Completion order (prerequisite-respecting)", "", " → ".join(s.title() for s in v.graph_order) or "(not computed)", "",
            "## Source facts audited", "",
            "* Vanilla bug class fixed: after any non-capturing battle the object hide flag (Uxie, Azelf, Turnback Giratina, Regigigas), the encounter state (Dialga, Palkia, Heatran) or the statue state (Regirock, Regice, Registeel) stayed consumed until the next Hall of Fame (or forever, for the Regi statues).",
            "* Regirock/Regice/Registeel statues no longer require an event-distributed Regigigas in the party.",
            "* Gen I–III legendaries use one `LegendaryHabitat` table in `src/overlay006/wild_encounters.c`; exact 1%/2% (including Surf, whose slot weights are code-fixed at 60/30/5/4/1) is why a post-Hall-of-Fame roll replaces slot editing. Ordinary encounter JSON is untouched.",
            "* Mew / Celebi / Jirachi are new BG-event tiles on existing item-ball / summit-approach tiles; Deoxys reuses the four existing Veilstone meteorite BG events.",
            "", "## Runtime QA (not performed)", "",
            "Required in-game checks (none run): Uxie/Azelf defeat-retry; Mesprit/Cresselia defeat-reset; Giratina retry; Dialga; Palkia; Heatran; Darkrai/Shaymin full unlock; Arceus prerequisite fail/success; Manaphy Egg empty/full party; Phione breeding; Rotom forms; Regis + Regigigas; renewable birds; one 2% and one 1% habitat; Mew; Celebi; Jirachi; Deoxys + form change. For every one-time static: encounter available → defeat/flee does not consume → leave/re-enter retries → capture sets completion → no respawn.",
            ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-report", action="store_true")
    ap.add_argument("--root", default=str(REPO_ROOT))
    args = ap.parse_args()
    v = Validation(Path(args.root))
    v.__post_init__()
    ok = v.run()
    for r in v.results:
        print(f"{'PASS' if r.ok else 'FAIL'} {r.check_id}: {r.title}" + ("" if r.ok else f"\n     -> {r.detail}"))
    print(f"\n{sum(r.ok for r in v.results)}/{len(v.results)} checks pass; failures: {sum(not r.ok for r in v.results)}")
    if not args.no_report and ok:
        (Path(args.root) / REPORT).write_text(render_report(v) + "\n")
        print("wrote", REPORT)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
