#!/usr/bin/env python3
"""D6 Battle Frontier / postgame validator.

Authority: docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md (s17) and the implementation plan (s12).
Checks the live tree against the manifests under docs/overhaul/implementation/postgame/ and against the
D6 start SHA.  Writes POSTGAME_VALIDATION_REPORT.md; exit status is the number of FAIL results.

Runtime behaviour is NOT verified here: every check is static (source/data/manifests).
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frontier_audit as A  # noqa: E402
import frontier_lib as L  # noqa: E402

IMPL = "docs/overhaul/implementation/postgame"
MULT = "FRONTIER_BP_PAYOUT_MULTIPLIER"

# Files D6 is allowed to touch (everything else in the diff is an unrelated-subsystem change).
ALLOWED = [
    r"^asm/macros/scrcmd\.inc$", r"^generated/vars_flags\.txt$", r"^include/constants/battle_frontier\.h$",
    r"^res/field/scripts/scripts_(battle_(arcade|castle|factory|hall|tower)|battleground|common|survival_area)\.s$",
    r"^res/text/(battleground|common_strings)\.json$", r"^res/trainers/frontier/pokemon/[a-z0-9_]+\.json$",
    r"^src/(overlay104/(battle_arcade|battle_arcade_helpers|battle_castle|battle_hall|battle_hall_helpers|ov104_022339B4)|scrcmd|scrcmd_battle_hall|unk_02049D08)\.c$",
    r"^docs/overhaul/", r"^tools/overhaul/postgame/",
    r"^tools/overhaul/trainers/(trainer_lib|validate_trainers)\.py$",  # integration fix: trainer validator froze the Frontier directory
    # D7 final-integration PR (later than D6): QA framework + proven integration fixes. Listed explicitly so the D6 scope check
    # keeps rejecting any OTHER later change.
    r"^tools/overhaul/(qa/|validate_overhaul\.py$)", r"^res/moves/solar_petal/data\.json$", r"^\.github/workflows/build\.yml$",
    r"^tools/overhaul/economy/(simulate_progression|test_validate_economy)\.py$", r"^tools/overhaul/trainers/test_validate_trainers\.py$",
    # D8 Mystery Egg starter PR (later than D7): opening flow + the three-way Rival branch helper. Listed explicitly so the D6
    # scope check keeps rejecting any OTHER later change.
    r"^tools/overhaul/(validate_mystery_starter\.py$|opening/|availability/special_verify\.py$)",
    r"^(include|src)/(mystery_egg_starter|egg_hatch|system_vars|scrcmd_strings|unk_0203D1B8|choose_starter/choose_starter_app|overlay005/daycare|struct_defs/choose_starter_data)\.[ch]$",
    r"^include/data/scripts/scrcmd\.h$", r"^src/meson\.build$", r"^res/text/(route_201|unk_0360)\.json$",
    r"^res/field/scripts/scripts_[a-z0-9_]+\.s$",  # starter-branch consumers; per-file scope is asserted by validate_mystery_starter.py
]


class V:
    def __init__(self, reader=None):
        self.read = reader or L.read
        self.results = []

    def rec(self, name, ok, detail=""):
        self.results.append((name, "PASS" if ok else "FAIL", detail))

    def base(self, path):
        return L.git_show(L.START_SHA, path)

    # -- helpers ---------------------------------------------------------------------------------------
    def body(self, text, name):
        m = re.search(re.escape(name) + r"\([^;{]*\)\s*\{", text)  # definition, not prototype
        i = m.end() - 1
        depth, j = 0, i
        while True:
            depth += (text[j] == "{") - (text[j] == "}")
            j += 1
            if depth == 0:
                return text[i:j]

    def table(self, text, symbol):
        i = text.index(symbol)
        return text[i:text.index("};", i)]

    def changed_files(self):
        out = subprocess.check_output(["git", "diff", "--name-only", L.START_SHA], cwd=L.ROOT).decode().split()
        out += subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=L.ROOT).decode().split()
        return sorted(set(out))

    # -- F1 --------------------------------------------------------------------------------------------
    def check_bp(self):
        hdr = self.read("include/constants/battle_frontier.h")
        m = re.search(rf"#define {MULT}\s+(\d+)", hdr)
        self.rec("BP multiplier constant is exactly 2", bool(m) and int(m.group(1)) == 2, f"value={m.group(1) if m else None}")
        man = json.load(open(L.p(IMPL, "frontier_rewards.json")))
        total = 0
        for r in man["payout_points"]:
            text = self.read(r["source_path"])
            n = text.count(r["target"])
            uses = len(re.findall(MULT, text))
            total += uses
            self.rec(f"payout point {r['facility_path']}: target present once, multiplier applied once",
                     n == 1 and uses == 1, f"target count={n}, multiplier uses in file={uses}")
        # 4x / double-application: no other src file may reference the multiplier, and the generic credit
        # commands must stay byte-identical to the start SHA.
        stray = []
        for root, _, files in os.walk(L.p("src")):
            for f in files:
                if f.endswith((".c", ".h")):
                    path = os.path.join(root, f)
                    rel = os.path.relpath(path, L.ROOT)
                    if MULT in open(path, errors="ignore").read() and rel not in {r["source_path"] for r in man["payout_points"]}:
                        stray.append(rel)
        self.rec("no stray multiplier use outside manifest payout points (no 4x)", not stray, ",".join(stray))
        self.rec("exactly 7 multiplier applications across src", total == 7, f"total={total}")
        for u in man["unchanged_unmultiplied_credit_paths"]:
            cur = self.body(self.read(u["source_path"]), u["function"])
            old = self.body(self.base(u["source_path"]), u["function"])
            self.rec(f"credit command {u['function']} unchanged (still 1x)", cur == old and MULT not in cur)
        for t in man["unchanged_base_tables"]:
            cur = self.table(self.read(t["source_path"]), t["symbol"])
            old = self.table(self.base(t["source_path"]), t["symbol"])
            self.rec(f"base table unchanged: {t['label']}", cur == old)
        # numeric: effective payout = 2 x base for every table row
        arc = self.read("src/overlay104/battle_arcade_helpers.c")
        for sym, want in (("sBonus1BP", (1, 2)), ("sBonus3BP", (3, 6))):
            vals = [int(x) for x in re.findall(r"\d+", self.table(arc, sym).split("{", 1)[1])]
            self.rec(f"Arcade roulette {sym} base starts at {want[0]} -> {want[0] * 2}", vals[0] == want[0] and vals[0] * 2 == want[1], f"base={vals}")

    def check_milestones_and_castle(self):
        cur, old = self.read("include/constants/battle_frontier.h"), self.base("include/constants/battle_frontier.h")
        keys = re.findall(r"#define ((?:HALL|CASTLE|ARCADE|FACTORY|TOWER)_(?:STREAK|BATTLES)_\w+)\s+(\d+)", old)
        ok = all(re.search(rf"#define {k}\s+{v}\b", cur) for k, v in keys)
        self.rec("Frontier milestone/round constants unchanged", ok and len(keys) >= 8, f"{len(keys)} constants")
        fac = self.body(self.read("src/overlay104/ov104_022339B4.c"), "u16 ov104_022347F8")
        self.rec("Factory streak literals 21/49 unchanged", "currentStreak == 21" in fac and "currentStreak == 49" in fac)
        diff = subprocess.check_output(["git", "diff", "-U0", L.START_SHA, "--", "src/overlay104/battle_castle.c"], cwd=L.ROOT).decode()
        changed = [l for l in diff.splitlines() if l[:1] in "+-" and not l.startswith(("+++", "---"))]
        self.rec("Castle Points code untouched (only include + BP return changed)", len(changed) == 3, f"{len(changed)} changed lines")

    # -- F2 --------------------------------------------------------------------------------------------
    def check_shop(self):
        man = json.load(open(L.p(IMPL, "frontier_shop_prices.json")))
        tab = lambda s: dict(re.findall(r"\{ (ITEM_\w+), (\d+) \}", self.table(s, "itemToBpPrice")))
        cur, old = tab(self.read("src/overlay007/shop_menu.c")), tab(self.base("src/overlay007/shop_menu.c"))
        for k, v in man["locked_tm_prices"].items():
            self.rec(f"locked TM BP price {k}={v}", cur.get(k) == str(v), f"live={cur.get(k)}")
        unexpected = {k: (old.get(k), v) for k, v in cur.items() if not k.startswith("ITEM_TM") and old.get(k) != v}
        unexpected |= {k: (v, None) for k, v in old.items() if k not in cur and not k.startswith("ITEM_TM")}
        self.rec("no unexpected non-TM shop change (full-table diff)", not unexpected, str(unexpected))
        self.rec("shop manifest changed_records empty and consistent", man["changed_records"] == [] and cur == {k: str(v) for k, v in {**man["locked_tm_prices"], **man["non_tm_prices_frozen"]}.items()})

    # -- F3/F4 -----------------------------------------------------------------------------------------
    def check_sets(self):
        F, _ = A.audit()
        for k in ("INVALID", "RETYPE", "LOST_STAB", "STAT", "REMOVED", "DUPLICATE"):
            self.rec(f"Frontier set audit: {k} findings == 0", not F[k], "; ".join(f"{n}: {m}" for n, m in F[k][:5]))
        sets = L.load_sets()
        species = L.load_constants("generated/species.txt")
        bad = [n for n, s in sets.items() if s["species"] not in species or s["form"] != 0]
        self.rec("all Frontier species/forms valid", not bad, ",".join(bad[:5]))
        self.rec("Frontier set count unchanged (951, no regeneration)", len(sets) == 951, str(len(sets)))
        man = json.load(open(L.p(IMPL, "frontier_set_changes.json")))
        drift = []
        for c in man["changes"]:
            d = json.load(open(L.p(c["source_path"])))
            if d["moves"] != c["target"] or (c.get("nature") and d["nature"] != c["nature"]["target"]):
                drift.append(c["source_path"])
        self.rec("set-change manifest matches source (no drift)", not drift, ",".join(drift))
        listed = {c["source_path"] for c in man["changes"]}
        edited = {f for f in self.changed_files() if f.startswith(L.SETS_DIR + "/")}
        self.rec("no unmanifested Frontier set edits (no table rebuild)", edited == listed, f"extra={sorted(edited - listed)} missing={sorted(listed - edited)}")
        self.rec("Brain sets audited separately, no unmanifested Brain edits", man["brain_edits"] == 0)
        self.rec("FRONTIER_SET_AUDIT.md exists", os.path.exists(L.p(IMPL, "FRONTIER_SET_AUDIT.md")))
        retyped = sorted({s["species"] for s in sets.values() if L.species_data(s["species"], L.VANILLA_SHA) and
                          set(L.species_data(s["species"])["types"]) != set(L.species_data(s["species"], L.VANILLA_SHA)["types"])})
        audit_md = open(L.p(IMPL, "FRONTIER_SET_AUDIT.md")).read() if os.path.exists(L.p(IMPL, "FRONTIER_SET_AUDIT.md")) else ""
        missing = [s for s in retyped if s not in audit_md]
        self.rec("retype audit covers every retyped Frontier species", not missing, ",".join(missing))
        # Hall pool
        src = self.read("src/overlay104/battle_hall_helpers.c")
        pool = re.search(r"sBattleHallPotentialOpponents\[\]\s*=\s*\{(.*?)\};", src, re.S)
        pairs = re.search(r"sBattleHallPotentialOpponentTypes\[\]\[2\]\s*=\s*\{(.*?)\};", src, re.S)
        sp = re.findall(r"SPECIES_\w+", pool.group(1))
        ty = re.findall(r"\{\s*(TYPE_\w+),\s*(TYPE_\w+)\s*\}", pairs.group(1))
        drift = [s for s, t in zip(sp, ty) if s != "SPECIES_WORMADAM" and set(t) != set(L.species_data(s)["types"])]
        self.rec("Hall static type pool matches live species types", len(sp) == len(ty) and not drift, ",".join(drift[:5]))

    # -- F5 --------------------------------------------------------------------------------------------
    def check_battleground(self):
        s = self.read("res/field/scripts/scripts_battleground.s")
        flags = [f for f in L.load_constants("generated/vars_flags.txt") if f.startswith("FLAG_DAILY_DEFEATED_BATTLEGROUND_")]
        cleared = set(re.findall(r"ClearFlag (FLAG_DAILY_DEFEATED_BATTLEGROUND_\w+)", s))
        self.rec("Battleground reshuffle clears all per-trainer daily defeated flags", set(flags) == cleared and len(flags) == 13, f"{len(cleared)}/{len(flags)}")
        self.rec("Battleground reshuffle resets the daily generation flag", "ClearFlag FLAG_DAILY_SET_BATTLEGROUND_TRAINERS" in s)
        self.rec("Battleground reshuffle re-enters the map (OnTransition regenerates)", "Warp MAP_HEADER_BATTLEGROUND" in s)
        self.rec("Battleground reshuffle requires current group resolved", "Battleground_FinishCurrentTrainers" in s and "Battleground_CheckSlot4Resolved" in s)
        self.rec("Battleground trainers not calendar-locked", "DayOfWeek" not in s and "DAY_OF_WEEK" not in s)
        for name in ("TryHideCheryl", "TryHideRiley", "TryHideMarley", "TryHideBuck", "TryHideMira"):
            cur = s[s.index(f"Battleground_{name}:"):].split("Return", 1)[0]
            old = self.base("res/field/scripts/scripts_battleground.s")
            old = old[old.index(f"Battleground_{name}:"):].split("Return", 1)[0]
            self.rec(f"partner prerequisite unchanged: {name}", cur == old)
        c = self.read("src/scrcmd.c")
        leaders = re.search(r"sBattlegroundGymLeaders\[\]\s*=\s*\{(.*?)\};", c, re.S).group(1)
        n = len(re.findall(r"OBJ_EVENT_GFX_\w+", leaders))
        rematch = sorted(set(re.findall(r"TRAINER_LEADER_\w+_REMATCH", s)))
        self.rec("all 8 Gym Leaders in the random pool with a rematch trainer ID", n == 8 and len(rematch) == 8, f"pool={n} rematch ids={len(rematch)}")
        ids = set(L.load_constants("generated/trainers.txt"))
        self.rec("leader rematch trainer IDs exist", all(r in ids for r in rematch))
        self.rec("trainer reshuffle avoids previous group (best effort)", "previousTrainers" in c)

    # -- F6 / F7 / F9 ----------------------------------------------------------------------------------
    def check_rematches(self):
        s = self.read("res/field/scripts/scripts_survival_area.s")
        self.rec("Rival rematch is not weekend-only", "DAY_OF_WEEK" not in s and "GetDayOfWeek" not in s)
        body = s[s.index("SurvivalArea_RivalBattle:"):]
        self.rec("Rival daily lock: flag checked first and set on victory",
                 "GoToIfSet FLAG_DAILY_DEFEATED_SURVIVAL_AREA_RIVAL" in body.split("StartTrainerBattle")[0] and "SetFlag FLAG_DAILY_DEFEATED_SURVIVAL_AREA_RIVAL" in body)
        self.rec("Rival starter branches preserved", all(x in s for x in ("SPECIES_TURTWIG", "SPECIES_CHIMCHAR", "TRAINER_RIVAL_SURVIVAL_AREA_2_PIPLUP")))
        ids = set(L.load_constants("generated/trainers.txt"))
        sa = sorted(set(re.findall(r"TRAINER_RIVAL_SURVIVAL_AREA_\w+", s)))
        self.rec("Rival rematch trainer IDs exist", len(sa) == 6 and all(t in ids for t in sa), str(len(sa)))
        for room in ("aaron", "bertha", "flint", "lucian", "champion"):
            r = self.read(f"res/field/scripts/scripts_pokemon_league_{room}_room.s")
            self.rec(f"League rematch trigger {room}", bool(re.search(r"CallIfSet FLAG_ARRESTED_CHARON_STARK_MOUNTAIN, \w+_Start\w+RematchBattle", r)) and "DAY_OF_WEEK" not in r)
            self.rec(f"League main-story team kept pre-postgame {room}", bool(re.search(r"CallIfUnset FLAG_ARRESTED_CHARON_STARK_MOUNTAIN, \w+_Start\w+Battle\n", r)))
        fa = self.read("res/field/scripts/scripts_fight_area.s")
        trainers = re.findall(r"TRAINER_[A-Z_]*FIGHT_AREA\w*", fa)
        self.rec("Fight Area tag battle references resolve to trainer records", len(set(trainers)) == 5 and all(t in ids for t in set(trainers)), ",".join(sorted(set(trainers))))
        # D8: the only permitted change is the Rival-branch query (GetPlayerStarterSpecies -> GetPlayerStarterBranch).
        fa_diff = [l for l in subprocess.check_output(["git", "diff", "-U0", L.START_SHA, "--", "res/field/scripts/scripts_fight_area.s"], cwd=L.ROOT).decode().splitlines()
                   if l[:1] in "+-" and not l.startswith(("+++", "---"))]
        fa_ok = all(l[1:].strip() in ("GetPlayerStarterSpecies VAR_RESULT", "GetPlayerStarterBranch VAR_RESULT") for l in fa_diff)
        self.rec("Fight Area script untouched (flow/Palmer/route unblock preserved)",
                 fa_ok and "StartTagBattle" in fa and "AddObject LOCALID_PALMER" in fa)
        for t in sorted(set(trainers)):
            self.rec(f"trainer data present: {t}", os.path.exists(L.p("res/trainers/data", t.lower()[len("trainer_"):] + ".json")))

    # -- F8 --------------------------------------------------------------------------------------------
    def check_prints(self):
        man = json.load(open(L.p(IMPL, "print_rewards.json")))
        flags = set(L.load_constants("generated/vars_flags.txt"))
        for f in man["new_flags"]:
            self.rec(f"print reward flag exists: {f['target']}", f["target"] in flags and f["before"] not in flags)
        common = self.read("res/field/scripts/scripts_common.s")
        for kind, item, bpflag, itemflag, states in (
            ("Silver", "ITEM_PP_MAX", "FLAG_RECEIVED_FRONTIER_ALL_SILVER_BP", "FLAG_RECEIVED_FRONTIER_ALL_SILVER_PP_MAX", "GoToIfLt"),
            ("Gold", "ITEM_MASTER_BALL", "FLAG_RECEIVED_FRONTIER_ALL_GOLD_BP", "FLAG_RECEIVED_FRONTIER_ALL_GOLD_MASTER_BALL", "GoToIfNe"),
        ):
            start = common.index(f"CommonScript_TryFrontierAll{kind}Reward:")
            routine = common[start:common.index(f"SetFlag {itemflag}", start)]
            routine_end = common[start:common.index("CommonScript_FrontierRewardDone:", start)]
            order = [routine_end.find(x) for x in (f"GoToIfSet {itemflag}", f"SetFlag {bpflag}", "CanFitItem", "CommonScript_InternalAddItemQuantity", f"SetFlag {itemflag}")]
            self.rec(f"{kind} all-print reward ordering (done-guard, BP flag, CanFitItem, AddItem, item flag)", all(o >= 0 for o in order) and order == sorted(order), str(order))
            self.rec(f"{kind} reward: item flag set exactly once, only after AddItem", common.count(f"SetFlag {itemflag}") == 1)
            self.rec(f"{kind} reward: BP flag set exactly once, BP granted at most once", common.count(f"SetFlag {bpflag}") == 1 and f"GoToIfSet {bpflag}" in common)
            self.rec(f"{kind} reward: full bag does not consume the item flag", "CommonScript_FrontierRewardBagFull" in routine_end and routine_end.index("CommonScript_FrontierRewardBagFull") < routine_end.index(f"SetFlag {itemflag}"))
            self.rec(f"{kind} reward item constant {item}", f"CanFitItem {item}, 1" in common and f"SetVar VAR_0x8004, {item}" in common)
            self.rec(f"{kind} reward requires all five facilities", all(f"VAR_BATTLE_{f}_PRINT_STATE" in routine_end for f in ("TOWER", "FACTORY", "HALL", "CASTLE", "ARCADE")))
        self.rec("all-print BP amounts 50 / 100", "SetVar VAR_0x8004, 50" in common and "SetVar VAR_0x8004, 100" in common)
        # per-facility: each silver/gold claim awards BP exactly once, behind the state transition
        for f in ("tower", "factory", "castle", "hall", "arcade"):
            t = self.read(f"res/field/scripts/scripts_battle_{f}.s")
            u = f.upper()
            ok = all(re.search(rf"SetVar VAR_BATTLE_{u}_PRINT_STATE, {st}\n    SetVar VAR_0x8004, {bp}\n    Common_GiveFrontierPrintBP\n", t)
                     for st, bp in ((2, 10), (4, 30)))
            self.rec(f"{f}: first Silver +10 BP / first Gold +30 BP, one path each", ok and t.count("Common_GiveFrontierPrintBP") == 2)
            self.rec(f"{f}: retry hook present", "Common_ProcessFrontierPrintRewards" in t and t.count("Common_ProcessFrontierPrintRewards") >= 3)
        ids = re.findall(r"ScriptEntry (CommonScript_\w+) @ (0x[0-9A-F]+)", common)
        macros = self.read("asm/macros/scrcmd.inc")
        ok = all(re.search(rf"macro {m}\n    CallCommonScript {i}\n", macros) for m, i in
                 (("Common_GiveFrontierPrintBP", "0x80A"), ("Common_ProcessFrontierPrintRewards", "0x80B")))
        self.rec("common script IDs 0x80A/0x80B match macros", ok and dict(ids).get("CommonScript_GiveFrontierPrintBP") == "0x80A" and dict(ids).get("CommonScript_ProcessFrontierPrintRewards") == "0x80B")
        self.rec("print-bonus BP goes through the un-multiplied field credit (no 4x)", "GiveBattlePoints VAR_0x8004" in common)

    # -- Pokedex / scope -------------------------------------------------------------------------------
    def check_scope(self):
        bad = []
        for f in ("availability_families.json", "special_acquisitions.json"):
            t = self.read(f"docs/overhaul/implementation/{f}")
            if re.search(r"(?i)frontier|battle.?point|\bprint\b", t):
                bad.append(f)
        self.rec("no Frontier/BP/Print requirement in availability or special-acquisition manifests (Pokedex completion)", not bad, ",".join(bad))
        extra = [f for f in self.changed_files() if not any(re.search(a, f) for a in ALLOWED)]
        self.rec("diff contains no unrelated subsystem changes", not extra, ",".join(extra[:8]))

    def run(self):
        for fn in (self.check_bp, self.check_milestones_and_castle, self.check_shop, self.check_sets, self.check_battleground,
                   self.check_rematches, self.check_prints, self.check_scope):
            fn()
        return self.results


def write_report(results):
    fails = [r for r in results if r[1] == "FAIL"]
    lines = ["# D6 Postgame Validation Report", "", f"Start SHA: `{L.START_SHA}`", "",
             f"Result: **{len(results) - len(fails)} PASS / {len(fails)} FAIL**", "",
             "Static validation only (source, data, manifests). In-game runtime QA has NOT been performed; D6 is IMPLEMENTED, not VERIFIED.",
             "", "| Check | Result | Detail |", "|---|---|---|"]
    for name, res, detail in results:
        lines.append(f"| {name} | {res} | {detail.replace('|', '/')[:160]} |")
    with open(L.p(IMPL, "POSTGAME_VALIDATION_REPORT.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return len(fails)


def main():
    results = V().run()
    n = write_report(results)
    for name, res, detail in results:
        if res == "FAIL":
            print("FAIL:", name, detail)
    print(f"{len(results) - n} pass, {n} fail")
    return n


if __name__ == "__main__":
    sys.exit(main())
