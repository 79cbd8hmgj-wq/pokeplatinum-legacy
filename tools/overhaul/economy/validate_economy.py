#!/usr/bin/env python3
"""Validate the locked EXP/economy implementation against current source, the pinned base and the manifest."""
from __future__ import annotations

import json
import re
import sys

import exp_model
from economy_lib import *


def check_exp(live: dict, P: list[str]):
    bs, ctx, consts = live["src"]["battle_script"], live["src"]["battle_context"], live["src"]["battle_consts"]
    m = re.search(r"#define EXP_BATTLE_POOL_PERCENT\s+(\d+)", consts)
    if not m or int(m.group(1)) != exp_model.BATTLE_POOL_PERCENT:
        P.append(f"EXP: EXP_BATTLE_POOL_PERCENT must be {exp_model.BATTLE_POOL_PERCENT} (60/40 split)")
    if consts.find("#define EXP_BATTLE_POOL_PERCENT") > consts.find("#endif // POKEPLATINUM_CONSTANTS_BATTLE_H"):
        P.append("EXP: EXP_BATTLE_POOL_PERCENT must remain inside the battle.h include guard")
    a = bs.find("static BOOL BtlCmd_CalcExpGain(BattleSystem *battleSys, BattleContext *battleCtx)\n{")
    z = bs.find("enum GetExpTaskState {")
    if a < 0 or z < a:
        P.append("EXP: BtlCmd_CalcExpGain not found")
        return
    calc = bs[a:z]
    task_a = bs.find("static void BattleScript_GetExpTask(SysTask *task, void *inData)\n{")
    task_z = bs.find("static void BattleScript_CalcEffortValues(Party *party, int slot, int species, int form)\n{")
    task = bs[task_a:task_z] if task_a >= 0 and task_z > task_a else ""
    if not task:
        P.append("EXP: BattleScript_GetExpTask not found")
        return
    need = {
        "raw pool formula": "(exp * battleCtx->battleMons[battleCtx->faintedMon].level) / 7",
        "base reward source": "SPECIES_DATA_BASE_EXP_REWARD",
        "battle pool uses EXP_BATTLE_POOL_PERCENT": "battlePool = exp * EXP_BATTLE_POOL_PERCENT / 100",
        "team pool is the conserved remainder": "teamPool = exp - battlePool",
        "empty battle group redistributes battle pool": "if (battleGroupCount == 0 && eligibleCount != 0)",
        "empty battle group conservation": "teamPool += battlePool",
        "battle pool divided by battle group": "battlePool / battleGroupCount",
        "team pool divided by every eligible member": "teamPool / eligibleCount",
        "battle remainder policy": "battleRemainder",
        "team remainder policy": "teamRemainder",
        "egg exclusion": "MON_DATA_IS_EGG, NULL) == FALSE",
        "fainted exclusion": "Pokemon_GetValue(mon, MON_DATA_HP, NULL)",
        "Lv100 exclusion": "MON_DATA_LEVEL, NULL) < MAX_POKEMON_LEVEL",
        "recipients = all eligible": "battleCtx->expRecipientMask = eligibleMask",
    }
    for label, frag in need.items():
        if frag not in calc:
            P.append(f"EXP: {label} missing ({frag!r})")
    if re.search(r"/\s*2\)|exp\s*/\s*2|\*\s*50\s*/\s*100", calc):
        P.append("EXP: vanilla 50/50 Exp. Share split restored")
    if "gainedExp" in bs or "sharedExp" in bs or "gainedExp" in ctx or "sharedExp" in ctx:
        P.append("EXP: legacy gainedExp/sharedExp (full-EXP / separate Exp. Share pool) still present")
    # Battle group is a UNIQUE union: one condition (participant || Exp. Share) increments the count once.
    grp = re.search(r"if \(\(battleCtx->sideGetExpMask\[[^\]]+\] & FlagIndex\(i\)\)\s*\|\|\s*BattleSystem_GetItemData\(battleCtx, item, ITEM_PARAM_HOLD_EFFECT\) == HOLD_EFFECT_EXP_SHARE\) \{(.*?)\n                \}", calc, re.S)
    if not grp or grp.group(1).count("battleGroupCount++") != 1 or "battleGroupMask |=" not in grp.group(1):
        P.append("EXP: battle group must be the unique union of participants and Exp. Share holders (counted once)")
    elig = re.search(r"if \(Pokemon_GetValue\(mon, MON_DATA_SPECIES.*?\{(.*?)u16 item", calc, re.S)
    if not elig:
        P.append("EXP: eligibility test not found")
    elif elig.group(0).count("&&") != 3:
        P.append("EXP: eligibility must test valid species, not Egg, HP > 0 and level < 100")
    counts_ok = calc.count("eligibleCount++") == 1 and calc.count("battleGroupCount++") == 1
    if not counts_ok:
        P.append("EXP: denominators (eligibleCount/battleGroupCount) must each be incremented exactly once per eligible member")
    # Team share must include every eligible member, battle group or not.
    ts = re.search(r"if \(eligibleMask & FlagIndex\(i\)\) \{\s*battleCtx->expAlloc\[i\] \+= teamPool / eligibleCount;", calc)
    if not ts:
        P.append("EXP: team recipients omitted (every eligible member must receive teamPool / eligibleCount)")
    # Recipient loop must walk every eligible member (not just participants/holders).
    if "expRecipientMask & FlagIndex(slot)" not in task or "HOLD_EFFECT_EXP_SHARE ||" in task:
        P.append("EXP: recipient iteration must use the eligible-recipient mask")
    if "totalExp = data->battleCtx->expAlloc[slot];" not in task:
        P.append("EXP: task does not take its per-slot allocation")
    # EVs: participants only.
    ev = re.search(r"if \(data->battleCtx->sideGetExpMask\[battler\] & FlagIndex\(slot\)\) \{\s*BattleScript_CalcEffortValues\(", task)
    if not ev or task.count("BattleScript_CalcEffortValues(") != 1:
        P.append("EXP: EVs must be granted only to actual participants (sideGetExpMask gate)")
    # Individual modifiers: unchanged values/order.
    seq = [
        "if (itemEffect == HOLD_EFFECT_EXP_UP) {\n                totalExp = totalExp * 150 / 100;",
        "if (battleType & BATTLE_TYPE_TRAINER) {\n                totalExp = totalExp * 150 / 100;",
        "totalExp = totalExp * 170 / 100;",
        "totalExp = totalExp * 150 / 100;\n                }\n\n                msg.id = BattleStrings_Text_PokemonGainedABoostedExpPoints",
    ]
    pos = [task.find(s) for s in seq]
    if min(pos) < 0 or pos != sorted(pos):
        P.append("EXP: Lucky Egg / trainer 1.5x / traded 1.5x / foreign 1.7x modifiers altered or reordered")
    if len(re.findall(r"totalExp = totalExp \*", task)) != 4:
        P.append("EXP: unexpected extra EXP multiplier (no Emerald multipliers allowed)")
    if "expRecipientMask &= " not in task:
        P.append("EXP: recipient bit never cleared after processing (re-iteration risk)")
    if "sideGetExpMask[battler] = 0;" not in task:
        P.append("EXP: final participant-state cleanup missing")


def check_prices(live: dict, base: dict, P: list[str]):
    """Permanent D2 invariants only; unrelated future item-price owners are not frozen here."""
    lp, bp = live["prices"], base["prices"]
    for k, v in LOCKED_PRICES.items():
        if lp.get(k) != v:
            P.append(f"price {k}: {lp.get(k)} != locked {v}")
    for k in STATUS_MEDICINES:
        want = status_target(bp[k])
        if lp.get(k) != want:
            P.append(f"status medicine {k}: {lp.get(k)} != derived {want} (from vanilla {bp[k]})")
    if lp.get("rare_candy") not in RARE_CANDY_PRICES:
        P.append(f"rare_candy price {lp.get('rare_candy')} not in {RARE_CANDY_PRICES}")


def check_prizes(live: dict, base: dict, P: list[str]):
    lt, bt = parse_prize_table(live["src"]["prize"]), parse_prize_table(base["src"]["prize"])
    if set(lt) != set(bt):
        P.append("prize table: class set changed")
    for k in sorted(bt):
        want = PRIZE_CHANGES[k][1] if k in PRIZE_CHANGES else bt[k]
        if k in PRIZE_CHANGES and bt[k] != PRIZE_CHANGES[k][0]:
            P.append(f"prize table: base {k} {bt[k]} != guard {PRIZE_CHANGES[k][0]}")
        if lt.get(k) != want:
            P.append(f"prize multiplier {k}: {lt.get(k)} != expected {want}")
    for k, v in {"TRAINER_CLASS_RIVAL": 25, "TRAINER_CLASS_CHAMPION": 50}.items():
        if k in lt and lt[k] != bt[k]:
            P.append(f"prize multiplier {k} changed")


def check_reminder(live: dict, P: list[str]):
    s, t = live["src"]["reminder_script"], json.loads(live["src"]["reminder_text"])
    mm = s[s.index("PastoriaCityEastHouse_MoveManiac:"):s.index("PastoriaCityEastHouse_Youngster:")]
    for bad in ("ITEM_HEART_SCALE", "RemoveItem", "CheckItem", "BufferItemNameWithArticle", "HeartScale"):
        if bad in mm:
            P.append(f"Move Reminder still references {bad} (must be free)")
    for need in ("SelectMoveTutorPokemon", "CheckHasLearnableReminderMoves", "OpenMoveReminderMenu", "CheckLearnedReminderMove",
                 "PARTY_SLOT_NONE", "0xFF", "EggsCantLearnMoves", "NoMovesToTeach", "TeachWhichMove", "TutorWhichPokemon"):
        if need not in mm:
            P.append(f"Move Reminder flow lost: {need}")
    cancel_branches = len(re.findall(r"GoToIfEq VAR_(?:0x8005, PARTY_SLOT_NONE|RESULT, 0xFF),", mm))
    if cancel_branches != 2:
        P.append("Move Reminder: cancel/refusal branches (party select + move menu) altered")
    for m in t["messages"]:
        txt = m.get("en_US")
        txt = "".join(txt) if isinstance(txt, list) else (txt or "")
        if m["id"].startswith("PastoriaCityEastHouse_Text_") and "NewspaperGivesHeartScales" not in m["id"] and "Heart Scale" in txt:
            P.append(f"Move Reminder text still demands a Heart Scale: {m['id']}")
    ids = {m["id"] for m in t["messages"]}
    for sym in re.findall(r"PastoriaCityEastHouse_Text_\w+", mm):
        if sym not in ids:
            P.append(f"Move Reminder script references missing text {sym}")


def check_tutors(live: dict, base: dict, P: list[str]):
    lt, bt = live["tutors"], base["tutors"]
    if len(lt) != len(bt):
        P.append(f"tutors: entry count {len(lt)} != {len(bt)}")
        return
    for i, (n, o) in enumerate(zip(lt, bt)):
        if set(n) != set(o):
            P.append(f"tutor[{i}] {o.get('move')}: field set changed")
            continue
        for k in o:
            if k in SHARD_FIELDS:
                want = -(-o[k] // 2)
                if n[k] != want:
                    P.append(f"tutor[{i}] {o['move']}.{k}: {n[k]} != ceil({o[k]}/2)={want}")
                if (o[k] == 0) != (n[k] == 0):
                    P.append(f"tutor[{i}] {o['move']}.{k}: zero/nonzero identity changed")
            elif n[k] != o[k]:
                P.append(f"tutor[{i}] {o['move']}: non-cost field {k} changed {o[k]!r}->{n[k]!r} (move/location locked)")
        if sum(n[k] for k in SHARD_FIELDS) < 1 <= sum(o[k] for k in SHARD_FIELDS):
            P.append(f"tutor[{i}] {o['move']}: paid tutor became free")


def check_stock(live: dict, base: dict, P: list[str]):
    src = live["src"]["marts"]
    arrays, vmap = parse_stock_arrays(src), parse_vendor_map(src)
    barrays, bvmap = parse_stock_arrays(base["src"]["marts"]), parse_vendor_map(base["src"]["marts"])
    ids = live["src"]["mart_ids"].split()
    for v in vmap:
        if v not in ids:
            P.append(f"vendor id {v} missing from generated/mart_specialties_id.txt")
    pre_items = set()
    for vid in PRE_E4_VENDOR_IDS & set(vmap):
        pre_items |= set(arrays.get(vmap[vid], []))
    pre_items |= {i for i in re.findall(r"\{ (ITEM_\w+), 0x\d \}", src)}
    stock = arrays.get(vmap.get(STONE_VENDOR_ID, ""), [])
    # Stones: all required, purchasable repeatably, pre-E4, from the Veilstone Department Store.
    for stone in required_stones():
        if stone not in stock:
            P.append(f"required evolution stone {stone} missing from repeatable pre-E4 vendor {STONE_VENDOR_ID}")
        if stone not in pre_items:
            P.append(f"required evolution stone {stone} not purchasable pre-E4")
    if "ITEM_OVAL_STONE" in stock:
        P.append("obsolete non-evolution item Oval Stone added as an evolution requirement/stock")
    vs = live["src"]["vitamin_vendor_script"]
    mid = vs[vs.index("VeilstoneStore2F_MiddleVendor:"):]
    if STONE_VENDOR_ID not in mid or "FLAG_GAME_COMPLETED" in mid.split("\n\n")[0]:
        P.append("stone vendor script missing or gated behind postgame")
    # Rare Candy: at least one unlimited source must remain postgame-only.
    rc_vendor = vmap.get(RARE_CANDY_VENDOR_ID)
    if rc_vendor is None or "ITEM_RARE_CANDY" not in arrays.get(rc_vendor, []):
        P.append("postgame Rare Candy vendor stock missing")
    for vid, arr_name in vmap.items():
        if vid in PRE_E4_VENDOR_IDS and "ITEM_RARE_CANDY" in arrays.get(arr_name, []):
            P.append(f"Rare Candy sold from pre-E4 specialty vendor {vid}")
    if "ITEM_RARE_CANDY" in re.findall(r"\{ (ITEM_\w+), 0x\d \}", src):
        P.append("Rare Candy in common mart table (pre-E4 unlimited)")
    if RARE_CANDY_VENDOR_ID in PRE_E4_VENDOR_IDS:
        P.append("Rare Candy vendor classified as pre-E4")
    fa = live["src"]["fight_area_script"]
    clown = fa[fa.index("FightAreaMart_Clown:"):]
    gate = clown.find("GoToIfUnset FLAG_GAME_COMPLETED")
    shop = clown.find(RARE_CANDY_VENDOR_ID)
    if gate < 0 or shop < 0 or gate > shop:
        P.append("unlimited Rare Candy available pre-E4: postgame gate (FLAG_GAME_COMPLETED) must precede the shop")

def check_pr_scope(live: dict, base: dict, P: list[str]):
    """PR-local guardrails. Mutation tests use these; permanent validation does not freeze later subsystem owners."""
    lp, bp = live["prices"], base["prices"]
    if set(lp) != set(bp):
        P.append("items: item price file set changed")
    allowed = set(LOCKED_PRICES) | set(STATUS_MEDICINES) | {"rare_candy"}
    for k in sorted(lp):
        if k not in allowed and lp[k] != bp.get(k):
            P.append(f"PR scope: unapproved item price edit: {k} {bp.get(k)} -> {lp[k]}")

    src = live["src"]["marts"]
    arrays, vmap = parse_stock_arrays(src), parse_vendor_map(src)
    barrays, bvmap = parse_stock_arrays(base["src"]["marts"]), parse_vendor_map(base["src"]["marts"])
    stone_array = vmap.get(STONE_VENDOR_ID)
    for name, before_items in barrays.items():
        if name == stone_array:
            continue
        if name in arrays and arrays[name] != before_items:
            P.append(f"PR scope: unrelated shop stock modified: {name}")
    if stone_array and stone_array in arrays:
        base_stock = barrays[bvmap[STONE_VENDOR_ID]]
        if [i for i in arrays[stone_array] if i not in required_stones()] != base_stock:
            P.append("PR scope: stone vendor existing stock changed")

    for rel in C2_ECONOMY_FILES:
        if live["c2_files"][rel] != base["c2_files"][rel]:
            P.append(f"PR scope: C2 Game Corner/Frontier TM economy source modified: {rel}")


def check_manifest(live: dict, base: dict, man: dict, P: list[str]):
    if man.get("base_commit") != BASE_COMMIT:
        P.append("manifest base_commit mismatch")
    for e in man["edits"]:
        k = e["key"]
        if e["category"] == "item_price":
            if base["prices"][k] != e["before"] or live["prices"][k] != e["after"]:
                P.append(f"manifest item_price {k}: before/after do not match base/live")
        elif e["category"] == "trainer_prize_multiplier":
            if parse_prize_table(base["src"]["prize"])[k] != e["before"] or parse_prize_table(live["src"]["prize"])[k] != e["after"]:
                P.append(f"manifest prize {k}: before/after do not match base/live")
    want = len(LOCKED_PRICES) + len(STATUS_MEDICINES) + 1
    got = sum(1 for e in man["edits"] if e["category"] == "item_price")
    if got != want:
        P.append(f"manifest item_price edit count {got} != {want}")
    if sum(1 for e in man["edits"] if e["category"] == "trainer_prize_multiplier") != len(PRIZE_CHANGES):
        P.append("manifest prize edit count mismatch")
    if len(man["tutors"]) != len(live["tutors"]):
        P.append("manifest tutor count mismatch")


def validate(live: dict, base: dict, man: dict | None = None, enforce_pr_scope: bool = False) -> list[str]:
    P: list[str] = []
    check_exp(live, P)
    check_prices(live, base, P)
    check_prizes(live, base, P)
    check_reminder(live, P)
    check_tutors(live, base, P)
    check_stock(live, base, P)
    if man is not None:
        check_manifest(live, base, man, P)
    if enforce_pr_scope:
        check_pr_scope(live, base, P)
    return P


def main() -> int:
    live, base = load_live(), load_base()
    man = json.loads(read(MANIFEST))
    P = validate(live, base, man)
    print(f"economy validation: {len(P)} failure(s)")
    for p in P:
        print("FAIL:", p)
    return 1 if P else 0


if __name__ == "__main__":
    sys.exit(main())
