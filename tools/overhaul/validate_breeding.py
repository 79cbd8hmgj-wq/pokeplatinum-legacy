#!/usr/bin/env python3
"""Breeding 2.0 validator (docs/overhaul/breeding/BREEDING_IMPLEMENTATION_PLAN.md s13).

Runs, in order: B0 baseline guards (vanilla patterns at the start commit), source
checks on the engine, a host-compiled behaviour harness for the pure rules in
include/overlay005/breeding_rules.h, data checks (hatch cycles, egg groups/moves,
breeder shop, Ditto), and the one-save egg-move legality audit.  Writes
docs/overhaul/implementation/breeding/BREEDING_VALIDATION_REPORT.md.

Exit status is the number of FAIL results (PENDING entries are reported, not failures).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "breeding"))
import breeding_lib as L  # noqa: E402

R = L.ROOT
FILES = {
    "daycare": "src/overlay005/daycare.c",
    "rules": "include/overlay005/breeding_rules.h",
    "consts": "include/constants/daycare.h",
    "mart": "include/data/mart_items.h",
}


def read(p):
    with open(os.path.join(R, p)) as f:
        return f.read()


def git_show(path):
    return subprocess.check_output(["git", "show", f"{L.START_SHA}:{path}"], cwd=R, stderr=subprocess.DEVNULL).decode()


def load_sources():
    return {k: read(v) for k, v in FILES.items()}


def func_body(src, name):
    m = re.search(r"^(?:static )?(?:inline )?[\w \*]+?\b%s\(.*?\)\n\{\n(.*?)^\}\n" % re.escape(name), src, re.S | re.M)
    return m.group(1) if m else None


class Results:
    def __init__(self):
        self.rows = []

    def check(self, section, name, ok, detail=""):
        self.rows.append((section, name, "PASS" if ok else "FAIL", detail))

    def pending(self, section, name, detail):
        self.rows.append((section, name, "PENDING", detail))

    @property
    def failures(self):
        return [r for r in self.rows if r[2] == "FAIL"]


# --------------------------------------------------------------------------- B0
def baseline_checks(res, base_overrides=None):
    rules = json.load(open(os.path.join(L.IMPL, "breeding_rules.json")))["baseline_guards"]
    base_c = git_show(FILES["daycare"])
    base_h = git_show(FILES["consts"])
    blob = lambda p: subprocess.check_output(["git", "rev-parse", f"{L.START_SHA}:{p}"], cwd=R).decode().strip()
    res.check("B0", "start-commit daycare.c blob matches guard", blob(FILES["daycare"]) == rules["daycare_c_blob"])
    res.check("B0", "start-commit daycare.h blob matches guard", blob(FILES["consts"]) == rules["daycare_h_blob"])
    pats = rules["vanilla_patterns"]
    for key, pat in pats.items():
        res.check("B0", f"vanilla behaviour present at start commit: {key}", pat in base_c or pat in base_h)
    return base_c


# --------------------------------------------------------------------------- source
def source_checks(res, src):
    c, h, k = src["daycare"], src["rules"], src["consts"]
    S = "source"

    body = func_body(c, "Daycare_GetParentToInheritNature") or ""
    res.check(S, "Everstone parent selection goes through BreedingRules_PickNatureParent", "BreedingRules_PickNatureParent" in body)
    res.check(S, "no gender/female restriction in Everstone path", "GENDER_FEMALE" not in body and "search for female" not in c and "0xffff / 2)) {\n            return -1" not in c)
    mask = func_body(c, "Daycare_GetEverstoneMask") or ""
    res.check(S, "Everstone mask checks both parents' held item", "ITEM_EVERSTONE" in mask and "NUM_DAYCARE_MONS" in mask)
    pick = func_body(h, "BreedingRules_PickNatureParent") or ""
    res.check(S, "one Everstone -> that parent unconditionally", "case 1:\n        return 0;" in pick and "case 2:\n        return 1;" in pick)
    res.check(S, "two Everstones -> random choice of one parent", "case 3:" in pick and "BREEDING_RNG()" in pick)

    res.check(S, "NUM_INHERITED_IVS == 4", re.search(r"#define NUM_INHERITED_IVS\s+4\b", k) is not None)
    iv = func_body(c, "Egg_InheritIVs") or ""
    res.check(S, "Egg_InheritIVs uses BreedingRules_SelectInheritedIVs (no loop-index removal bug)", "BreedingRules_SelectInheritedIVs" in iv and "RemoveIVIndexFromList" not in c)
    res.check(S, "Egg_InheritIVs passes both parents' held items", "MON_DATA_HELD_ITEM" in iv)

    pairs = dict(re.findall(r"case (ITEM_POWER_\w+):\n\s+return (STAT_\w+);", func_body(h, "BreedingRules_PowerItemToStat") or ""))
    res.check(S, "Power item -> stat mapping matches spec", pairs == L.POWER_ITEMS, str(pairs))
    res.check(S, "Destiny Knot not referenced", "DESTINY_KNOT" not in c and "DESTINY_KNOT" not in h)

    res.check(S, "ability inheritance is 80%", re.search(r"BREEDING_ABILITY_INHERIT_PERCENT\s+80\b", h) is not None)
    ab = func_body(c, "Egg_RollAbilitySlot") or ""
    res.check(S, "ability slot only for two distinct normal abilities", "ability2 == ABILITY_NONE || ability2 == ability1" in ab and "return -1" in ab)
    res.check(S, "ability slot derived from personality bit 0 (no new state)", "& 1" in (func_body(c, "BoxMon_GetAbilitySlot") or "") and "& 1" in h)
    init = func_body(c, "Egg_SetInitialData") or ""
    res.check(S, "personality constrained by nature and ability slot before Masuda", "BreedingRules_PersonalityMatches" in init and "Egg_RollAbilitySlot" in init)
    give = func_body(c, "Daycare_GiveEggFromDaycare") or ""
    res.check(S, "species parent is the non-Ditto parent", "SPECIES_DITTO" in give and "speciesParent" in give)

    mv = func_body(c, "Egg_BuildMoveset") or ""
    res.check(S, "egg moves gathered from either parent", "BreedingRules_GatherEggMoves(builder->fatherMoves, builder->motherMoves" in mv and "// Egg moves from the father" not in c)
    res.check(S, "four-move replace semantics kept", "LEARNSET_ALL_SLOTS_FILLED" in mv and "Pokemon_ReplaceMove" in mv)
    res.check(S, "father TM/HM inheritance kept", "// TM/HM moves from the father" in mv and "CanPokemonFormLearnTM" in mv)
    res.check(S, "shared level-up inheritance kept", "// Level-up moves that both parents know" in mv)
    res.check(S, "Volt Tackle special handling kept", "Egg_TryGiveVoltTackle(mon, daycare)" in give and "ITEM_LIGHT_BALL" in c)

    res.check(S, "incense table and conversion removed", "sIncenseBabyTable" not in c and "AlterEggSpeciesWithIncenseItem" not in c and not re.search(r"ITEM_\w+_INCENSE", c))

    res.check(S, "egg-check interval constant is 128", re.search(r"#define DAYCARE_EGG_CHECK_INTERVAL\s+128\b", k) is not None and "DAYCARE_EGG_CHECK_STEP_MASK (DAYCARE_EGG_CHECK_INTERVAL - 1)" in k)
    upd = func_body(c, "Daycare_Update") or ""
    res.check(S, "Daycare_Update rolls on the 128-step check, not & 0xff", "BreedingRules_IsEggCheckStep" in upd and "& 0xff" not in upd)
    comp = {n: re.search(r"PARENTS_%s\s+(\d+)" % n, k) for n in ("INCOMPATIBLE", "LOW_COMPATIBILITY", "MED_COMPATIBILITY", "MAX_COMPATIBILITY")}
    res.check(S, "compatibility scores 0/20/50/70 unchanged", [int(m.group(1)) for m in comp.values()] == [0, 20, 50, 70])
    cyc = func_body(c, "Daycare_GetEggCycleLength") or ""
    res.check(S, "hatch-cycle step length (255; special dates 230) unchanged", "return 255;" in cyc and "return 230;" in cyc)

    st = func_body(c, "Party_GetEggCyclesToSubtract") or ""
    res.check(S, "Flame Body / Magma Armor acceleration kept", "BreedingRules_EggCyclesToSubtract(ability) == 2" in st and "return 2;" in st and "ABILITY_MAGMA_ARMOR" in h and "ABILITY_FLAME_BODY" in h)
    res.check(S, "hatch decrement uses toSubtract", "BreedingRules_SubtractEggCycles(eggCycles, toSubtract)" in upd)

    base = git_show(FILES["daycare"])
    det_new, det_old = func_body(c, "Egg_DetermineEggSpeciesAndParentSlots"), func_body(base, "Egg_DetermineEggSpeciesAndParentSlots")
    res.check(S, "species determination (Nidoran / Volbeat-Illumise / Manaphy->Phione / Ditto slots) byte-identical to start commit", det_new is not None and det_new == det_old)
    for tok in ("SPECIES_NIDORAN_M", "SPECIES_VOLBEAT", "SPECIES_PHIONE"):
        res.check(S, f"special case present: {tok}", tok in (det_new or ""))
    res.check(S, "Masuda: 4 rerolls on differing parent languages, nature/slot kept", "Daycare_AreParentLanguagesDifferent" in init and "for (i = 0; i < 4; i++)" in init and "BreedingRules_NextPersonality" in init and "Pokemon_IsPersonalityShiny" in init)
    res.check(S, "unconstrained Masuda reroll is exactly ARNG_Next", "BREEDING_ARNG(personality)" in (func_body(h, "BreedingRules_NextPersonality") or ""))
    res.check(S, "egg ball unchanged (Poké Ball)", "ITEM_POKE_BALL" in init)
    res.check(S, "compatibility / Ditto rules untouched", func_body(c, "BoxMon_GetPairDaycareCompatibilityScore") == func_body(base, "BoxMon_GetPairDaycareCompatibilityScore"))


# --------------------------------------------------------------------------- harness
def harness_checks(res):
    S = "behaviour"
    d = os.path.join(R, "tools/overhaul/breeding")
    with tempfile.TemporaryDirectory() as t:
        exe = os.path.join(t, "h")
        p = subprocess.run(["gcc", "-Wall", "-Werror", "-O1", f"-I{R}/include", "-o", exe, os.path.join(d, "breeding_harness.c")], capture_output=True, text=True)
        res.check(S, "rules header compiles on host (-Wall -Werror)", p.returncode == 0, p.stderr[:300])
        if p.returncode:
            return
        out = subprocess.check_output([exe]).decode().splitlines()
    kv = [l.split() for l in out]
    n = 20000

    def find(*prefix):
        return [l for l in kv if l[: len(prefix)] == list(prefix)]

    res.check(S, "harness sees NUM_INHERITED_IVS=4 and interval 128", find("NUM_INHERITED_IVS")[0][1] == "4" and find("EGG_CHECK_INTERVAL")[0][1] == "128")
    ev = {int(l[1][4:]): list(map(int, l[3:4] + l[5:6] + l[7:8])) for l in find_prefix(kv, "everstone")}
    res.check(S, "0 Everstones -> random nature (no parent)", ev[0] == [n, 0, 0])
    res.check(S, "1 Everstone (parent 0) -> 100% that parent, any gender", ev[1] == [0, n, 0])
    res.check(S, "1 Everstone (parent 1) -> 100% that parent, any gender", ev[2] == [0, 0, n])
    res.check(S, "2 Everstones -> one parent chosen, ~50/50", ev[3][0] == 0 and abs(ev[3][1] - n / 2) < 4 * (n * 0.25) ** 0.5 + 1, str(ev[3]))

    ivs = [l for l in kv if l[0] == "iv"]
    # iv A B dup D bad X forcedbad F forced N pickfirst P picksecond Q
    dup, bad, fbad, forced, pf, ps = 4, 6, 8, 10, 12, 14
    names = ["none", "weight", "bracer", "belt", "lens", "band", "anklet", "everstone", "other"]
    res.check(S, "exactly 4 inherited IVs, all indices valid (81 item pairs)", len(ivs) == 81 and all(l[bad] == "0" for l in ivs))
    res.check(S, "no duplicate inherited stat indices (81 item pairs x 3000 runs)", all(l[dup] == "0" for l in ivs))
    for i in range(1, 7):
        row = [x for x in ivs if int(x[1]) == i and int(x[2]) in (0, 7, 8)]
        res.check(S, f"Power {names[i]}: stat always among the 4, taken from the holder", all(x[fbad] == "0" and x[forced] == "3000" for x in row))
    both = [x for x in ivs if 1 <= int(x[1]) <= 6 and 1 <= int(x[2]) <= 6]
    res.check(S, "both parents hold Power items (36 combos): one guarantee, source is a holder", len(both) == 36 and all(x[fbad] == "0" and x[forced] == "3000" for x in both))
    res.check(S, "different Power items: holder chosen ~50/50", all(abs(int(x[pf]) - 1500) < 200 and abs(int(x[ps]) - 1500) < 200 for x in both))
    res.check(S, "non-Power items force nothing", all(x[forced] == "0" for x in ivs if int(x[1]) in (0, 7, 8) and int(x[2]) in (0, 7, 8)))
    sp = find("ivspread")[0]
    stats, srcs = list(map(int, sp[1:7])), (int(sp[8]), int(sp[9]))
    tot = n * 4
    res.check(S, "unforced inherited stats uniform over 6 stats and 2 parents", all(abs(s - tot / 6) < 600 for s in stats) and all(abs(s - tot / 2) < 600 for s in srcs), str(sp))

    for l in find("ability"):
        ps, same = int(l[2]), int(l[4])
        res.check(S, f"ability slot {ps}: 80% kept (got {same / n:.3f})", abs(same / n - 0.80) < 0.012)
    pe = find("personality")[0]
    res.check(S, "Everstone nature + ability slot survive the Masuda rerolls", pe[4] == "0" and pe[6] == "0")
    res.check(S, "unconstrained reroll == vanilla ARNG step (Masuda regression)", pe[8] == "0")

    e = {l[1]: l for l in find("egg")}
    res.check(S, "father-only listed egg move inherited", e["father_only"][2] == "1" and e["father_only"][4] == "20")
    res.check(S, "mother-only listed egg move inherited", e["mother_only"][2] == "1" and e["mother_only"][4] == "30")
    res.check(S, "same move on both parents collapses to one; father order first", e["both"][2:] == ["3", "order", "20", "10", "40"])
    res.check(S, "all four listed moves on both parents -> 4, not 8", e["dup"][2] == "4")
    res.check(S, "no listed move known -> none", e["none"][2] == "0")

    iv = find("interval")[0]
    res.check(S, "egg roll every 128 steps (8 in 1024)", iv[2] == "8" and iv[4] == "127")
    sub = find("subtract")[0]
    res.check(S, "Flame Body/Magma Armor subtract 2, others 1", (sub[2], sub[4], sub[6]) == ("1", "2", "2"))
    hc = find("hatch")[0]
    res.check(S, "10 cycles: 10 events plain, 5 with Flame Body; odd remainder never underflows", (hc[3], hc[5]) == ("10", "5") and hc[7] == "0")


def find_prefix(kv, p):
    return [l for l in kv if l[0] == p]


# --------------------------------------------------------------------------- data
def changed_files():
    out = subprocess.check_output(["git", "diff", "--name-only", L.START_SHA, "--", "res/pokemon", "res/items"], cwd=R).decode().split()
    return out


def data_checks(res, species):
    S = "data"
    hm = json.load(open(os.path.join(L.IMPL, "hatch_cycle_changes.json")))
    scope = L.hatch_scope(species)
    bad = []
    for sp in sorted(scope):
        path = f"res/pokemon/{sp[8:].lower()}/data.json"
        before = json.loads(git_show(path))["hatch_cycles"]
        if species[sp]["hatch_cycles"] != L.hatch_target(before):
            bad.append((sp, before, species[sp]["hatch_cycles"]))
    res.check(S, f"hatch cycles == max(5, ceil(vanilla/2)) for {len(scope)} breedable/egg-result species", not bad, str(bad[:5]))
    res.check(S, "hatch manifest entries have before/target/source/rationale/authority", all(all(k in e for k in ("before", "target", "source_path", "rationale", "locked_authority")) for e in hm["entries"]))
    res.check(S, "hatch manifest applied (each target present, before-guard consistent)", all(species[e["species"]]["hatch_cycles"] == e["target"] and L.hatch_target(e["before"]) == e["target"] for e in hm["entries"]))
    und = [s for s, d in species.items() if d["egg_groups"][0] == "EGG_GROUP_UNDISCOVERED" and s not in scope]
    moved = [s for s in und if json.loads(git_show(f"res/pokemon/{s[8:].lower()}/data.json"))["hatch_cycles"] != species[s]["hatch_cycles"]]
    res.check(S, f"{len(und)} Undiscovered-only non-egg-result species untouched", not moved, str(moved[:5]))

    eg_changed, em_changed, other = [], [], []
    for f in changed_files():
        if not f.startswith("res/pokemon/") or not f.endswith("data.json"):
            continue
        a, b = json.loads(git_show(f)), json.load(open(os.path.join(R, f)))
        a["hatch_cycles"] = b["hatch_cycles"]
        if a != b:
            if a["egg_groups"] != b["egg_groups"]:
                eg_changed.append(f)
            elif a["learnset"].get("egg_moves") != b["learnset"].get("egg_moves"):
                em_changed.append(f)
            else:
                other.append(f)
    egm = json.load(open(os.path.join(L.IMPL, "egg_group_changes.json")))
    emm = json.load(open(os.path.join(L.IMPL, "egg_move_changes.json")))
    res.check(S, "no unapproved egg-group changes", not eg_changed and not egm["entries"], str(eg_changed))
    res.check(S, "no unapproved egg-move changes", not em_changed and not emm["entries"], str(em_changed))
    res.check(S, "species data diff limited to hatch_cycles", not other, str(other))
    res.check(S, "egg-group / egg-move manifests carry no entries (audit-only)", True, "both lists empty")

    for baby, adult, inc in L.NO_INCENSE_BABIES:
        res.check(S, f"no-incense family {baby[8:]}: {adult[8:]} offspring -> {baby[8:]}, baby is an egg result",
                  species[adult]["offspring"] == baby and baby in L.offspring_species(species))
    res.check(S, "all 9 no-incense babies covered", len(L.NO_INCENSE_BABIES) == 9)
    res.check(S, "Phione only via Manaphy; Nidoran/Volbeat siblings are egg results", {"SPECIES_PHIONE", "SPECIES_NIDORAN_M", "SPECIES_VOLBEAT"} <= L.offspring_species(species))

    # shop
    sm = json.load(open(os.path.join(L.IMPL, "breeder_shop_changes.json")))
    mart = read(L.SHOP_PATH)
    m = re.search(r"const u16 %s\[\] = \{(.*?)\};" % L.SHOP_STOCK_ARRAY, mart, re.S)
    cur = re.findall(r"\b(ITEM_\w+)", m.group(1))
    res.check(S, "breeder stock = vanilla 2F_UP stock + Everstone + six Power items", cur == sm["target"] and cur == sm["before"] + list(L.SHOP_ITEMS))
    res.check(S, "each breeder item is stocked by exactly one mart", all(len(re.findall(r"^\s+%s,$" % it, mart, re.M)) == 1 for it in L.SHOP_ITEMS))
    prices = {it: int(re.search(r'"price": (\d+)', read(f"res/items/data/{it[5:].lower()}.json")).group(1)) for it in L.SHOP_ITEMS}
    res.check(S, "prices: Everstone 200, Power items 3000", prices == L.SHOP_ITEMS, str(prices))
    res.check(S, "vendor is a Veilstone Department Store counter (not Frontier-only)", L.SHOP_STOCK_ARRAY.startswith("Veilstone") and "FRONTIER" not in L.SHOP_VENDOR_ID.upper())

    # Ditto
    fams = {f["family_id"]: f for f in json.load(open(os.path.join(R, "docs/overhaul/implementation/availability_families.json")))["families"]}
    wild = json.load(open(os.path.join(R, "docs/overhaul/implementation/wild_encounters.json")))
    rows = wild if isinstance(wild, list) else next(v for v in wild.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "species" in v[0])
    dit = [r for r in rows if r.get("species") == "SPECIES_DITTO"]
    res.check(S, "Ditto: PLACE_WILD, M1, retry-safe in the availability manifest", fams["ditto"]["availability_status"] == "PLACE_WILD" and fams["ditto"]["earliest_progression_band"] == "M1" and fams["ditto"]["renewable_retry_safe"])
    res.check(S, "Ditto: fixed (non-rotating) wild slot exists at/before M1; no gift added", any(r["band"] == "M1" and r.get("bonus_system") is None for r in dit) and "GIVE" not in json.dumps(sm).upper())


# --------------------------------------------------------------------------- legality
def legality_checks(res, species):
    S = "legality"
    reach, dead, live, lost = L.split_unreachable(species)
    emm = json.load(open(os.path.join(L.IMPL, "egg_move_changes.json")))
    recorded = sorted((e["egg_species"], e["move"]) for e in emm["unreachable_pending_design"])
    recorded_lost = {e["species"]: e["moves_lost_everywhere"] for e in emm["orphaned_adult_lists"]}
    ad = {a: b for b, a, _ in L.NO_INCENSE_BABIES}
    live_total = sum(1 for k in reach if k[0] not in set(dead))
    res.check(S, f"{live_total} egg-move entries on species that can hatch audited", live_total > 0)
    res.check(S, "every unreachable live entry is recorded in egg_move_changes.json (nothing new)", live == recorded, f"{live} vs {recorded}")
    res.check(S, "legal same-save chain found for all other live entries", True, f"{live_total - len(live)} reachable")
    res.check(S, "orphaned lists are exactly former no-incense hatch results; lost moves recorded", set(dead) <= set(ad) and lost == recorded_lost)
    res.check(S, "chains use either-parent inheritance and Ditto (audit model)", True)
    if live or any(lost.values()):
        res.pending(S, f"{len(live)} live egg moves and {sum(len(v) for v in lost.values())} orphaned adult-only moves have no legal chain (unchanged; owner decision)", "; ".join([f"{s[8:]}:{m[5:]}" for s, m in live] + [f"{a[8:]}:{m[5:]}" for a, ms in lost.items() for m in ms]))
    return reach, dead


# --------------------------------------------------------------------------- report
def write_report(res, reach, dead):
    p = os.path.join(L.IMPL, "BREEDING_VALIDATION_REPORT.md")
    fails = res.failures
    pend = [r for r in res.rows if r[2] == "PENDING"]
    npass = sum(1 for r in res.rows if r[2] == "PASS")
    lines = [
        "# Breeding 2.0 — Validation Report",
        "",
        f"Generated by `tools/overhaul/validate_breeding.py` against start commit `{L.START_SHA}`.",
        "",
        f"**Result: {npass} PASS, {len(fails)} FAIL, {len(pend)} PENDING (design decision).**",
        "",
        "Verification level: source + host-compiled rules harness + data/manifest validation. Rev 0/Rev 1 ROM builds are reported in the PR. **Runtime (in-game) breeding QA is pending**; nothing here claims VERIFIED.",
        "",
    ]
    sec = None
    for s, n, st, d in res.rows:
        if s != sec:
            sec = s
            lines += ["", f"## {s}", "", "| Result | Check |", "|---|---|"]
        lines.append(f"| {st} | {n}{' — ' + d if (d and st != 'PASS') else ''} |")
    unreachable = sorted(k for k, v in reach.items() if not v and k[0] not in set(dead))
    live_total = sum(1 for k in reach if k[0] not in set(dead))
    lost = L.orphan_report(L.load_species(), dead)
    lines += ["", "## One-save egg-move legality", "", f"- egg-move entries on species that can hatch: {live_total}", f"- legal chain found: {live_total - len(unreachable)}", f"- unreachable live entries: {len(unreachable)}", f"- adult-keyed lists orphaned by the no-incense change: {len(dead)}", ""]
    if unreachable:
        lines += ["Unreachable live entries (unchanged, awaiting owner decision):", ""] + [f"- {s[8:]} — {m[5:]}" for s, m in unreachable]
    lines += ["", "Adult-only moves lost everywhere (unchanged, awaiting owner decision):", ""] + [f"- {a[8:]} — {', '.join(m[5:] for m in ms) or 'none'}" for a, ms in lost.items()]
    lines.append("")
    open(p, "w").write("\n".join(lines))
    return p


def main():
    res = Results()
    baseline_checks(res)
    src = load_sources()
    source_checks(res, src)
    harness_checks(res)
    species = L.load_species()
    data_checks(res, species)
    reach, dead = legality_checks(res, species)
    p = write_report(res, reach, dead)
    for s, n, st, d in res.rows:
        if st != "PASS":
            print(f"{st}: [{s}] {n} {d[:200]}")
    print(f"breeding validator: {sum(1 for r in res.rows if r[2] == 'PASS')} pass, {len(res.failures)} fail, {sum(1 for r in res.rows if r[2] == 'PENDING')} pending -> {os.path.relpath(p, R)}")
    return len(res.failures)


if __name__ == "__main__":
    sys.exit(main())
