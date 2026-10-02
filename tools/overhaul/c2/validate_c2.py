#!/usr/bin/env python3
"""Validate live source against the locked C2 TM/HM mechanics manifest.

`validate(live, ctx)` is pure so the mutation tests can corrupt copies. Non-zero exit on any problem.
Forward-compatible by design: only C2-owned data is pinned (HM records, Defog script, TeachMove consumption,
TM21/TM78 roster, Game Corner / Frontier TM tables, vendor guards, TM item prices, TM placement fingerprint).
"""
from __future__ import annotations

import re
import sys

from c2_lib import *


def load_ctx() -> dict:
    return {"manifest": load_json(MANIFEST), "tm21_78_recipients": load_json("docs/overhaul/implementation/tm_compat_manifest.json"),
            "created": load_json("docs/overhaul/implementation/created_moves_manifest.json")}


def load_live() -> dict:
    live = {"moves": {d: load_json(f"res/moves/{d}/data.json") for d in HM_DIRS}, "src": {k: read(v) for k, v in SRC.items()}}
    live["tm_items"] = {os.path.basename(p)[:-5].upper(): load_json(p) for p in tm_item_files()}
    live["fingerprint"] = field_tm_fingerprint()
    live["species"] = tm_species_sets()
    live["msg_0543"] = {m["id"] for m in load_json("res/text/unk_0543.json")["messages"]}
    live["msg_prize"] = {m["id"] for m in load_json("res/text/veilstone_city_prize_exchange.json")["messages"]}
    live["move_dirs"] = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, "res/moves/*/data.json"))}
    return live


def _lines(src: str) -> list[str]:
    return [ln.strip() for ln in src.splitlines()]


def check_defog(src: str, man: dict, P: list[str]):
    lines = _lines(src)
    clears = lambda who, cond: any(re.match(rf"CheckSideCondition BTLSCR_{who}, CHECK_SIDE_COND_CLEAR, SIDE_COND_{cond}\b", ln) for ln in lines)
    rock = lambda who: any(re.match(rf"UpdateVar OPCODE_FLAG_OFF, BTLVAR_SIDE_CONDITIONS_{who}, SIDE_CONDITION_STEALTH_ROCK$", ln) for ln in lines)
    for who in ("DEFENDER", "ATTACKER"):
        for cond in ("SPIKES_LAYERS", "TOXIC_SPIKES_LAYERS"):
            if not clears(who, cond):
                P.append(f"Defog: {who.lower()} side {cond} not cleared")
        if not rock(who):
            P.append(f"Defog: {who.lower()} side Stealth Rock not cleared")
    for cond in ("REFLECT_TURNS", "LIGHT_SCREEN_TURNS", "SAFEGUARD_TURNS", "MIST_TURNS"):
        if not clears("DEFENDER", cond):
            P.append(f"Defog: target side {cond} not cleared")
        if clears("ATTACKER", cond):
            P.append(f"Defog: clears the user's own {cond}")
    if any(re.search(r"BTLVAR_SIDE_CONDITIONS_ATTACKER, SIDE_CONDITION_(REFLECT|LIGHT_SCREEN|SAFEGUARD|MIST)", ln) and "FLAG_OFF" in ln for ln in lines):
        P.append("Defog: clears the user's own screens via side-condition mask")
    if "MOVE_SUBSCRIPT_PTR_EVASION_DOWN_1_STAGE" not in src or "BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE" not in src:
        P.append("Defog: evasion -1 missing")
    if "FIELD_CONDITION_DEEP_FOG" not in src:
        P.append("Defog: deep-fog clearing lost")
    # attacker-side clears must not be dead code: they are reached in the main (non-jumped) flow
    if "CHECK_SIDE_COND_VAL_ZERO" not in src:
        P.append("Defog: zero-check structure lost")


def check_reusable(live_src: dict, man: dict, P: list[str]):
    cb = live_src["party_callbacks"]
    m = re.search(r"static void TeachMove\([^;]*?\)\n\{.*?\n}\n", cb, re.S)
    if not m:
        P.append("TeachMove not found")
        return
    body = m.group(0)
    guard = re.search(r"if \(usedItem < ITEM_TM01 \|\| usedItem > ITEM_HM08\) \{\s*Bag_TryRemoveItem\(", body)
    if not guard:
        if "Item_IsHMMove" in body and "Bag_TryRemoveItem" in body:
            P.append("TM still consumed after successful teaching (vanilla Item_IsHMMove guard)")
        elif "Bag_TryRemoveItem" not in body:
            P.append("TeachMove never consumes any item (generic consumables would become reusable)")
        else:
            P.append("TeachMove removal guard is not the TM/HM item-range condition")
    if "u16 usedItem = application->partyMenu->usedItemID;" not in body:
        P.append("TeachMove: usedItem not derived from partyMenu->usedItemID")
    for rel, n in man["reusable_tm"]["other_bag_removals_pinned"].items():
        key = "party_callbacks" if "callbacks" in rel else "party_main"
        have = live_src[key].count("Bag_TryRemoveItem")
        if have != n:
            P.append(f"{rel}: Bag_TryRemoveItem count {have} != pinned {n} (non-TM consumables must stay consumable)")


def check_hms(live: dict, man: dict, P: list[str]):
    for d, spec in man["hm_battle"].items():
        rec = live["moves"].get(d)
        if rec is None:
            P.append(f"{spec['name']}: record missing")
            continue
        exp = spec["expected_after"]
        got = {"power": rec["power"], "accuracy": rec["accuracy"], "pp": rec["pp"], "effect": rec["effect"]["type"], "chance": rec["effect"]["chance"]}
        for k, v in exp.items():
            if got[k] != v:
                P.append(f"{spec['name']}: {k} live {got[k]!r} != locked {v!r}")
        for k, mk in (("class", "class"), ("type", "type"), ("range", "range")):
            if rec[k] != spec[mk]:
                P.append(f"{spec['name']}: {k} changed {spec[mk]!r}->{rec[k]!r}")
    fly = live["moves"].get("fly")
    if fly and fly["effect"]["type"] != "BATTLE_EFFECT_FLY":
        P.append("Fly: lost its two-turn semi-invulnerable effect")


def check_economy(live: dict, man: dict, P: list[str]):
    # Game Corner
    gc = parse_pairs(live["src"]["game_corner"], "sGameCornerPrizeData")
    gcd = dict(gc)
    for k, v in man["game_corner"]["tm_prices"].items():
        if gcd.get(f"ITEM_{k}") != v["expected_after"]:
            P.append(f"Game Corner {k}: price {gcd.get(f'ITEM_{k}')} != locked {v['expected_after']}")
    if [i for i, _ in gc if re.fullmatch(r"ITEM_TM\d\d", i)] != man["game_corner"]["tm_order"]:
        P.append("Game Corner: TM prize list changed/reordered")
    if [list(x) for x in gc if not re.fullmatch(r"ITEM_TM\d\d", x[0])] != man["game_corner"]["unchanged_prizes"]:
        P.append("Game Corner: unrelated (held-item) prize modified")
    if len(gc) != len(man["game_corner"]["tm_order"]) + len(man["game_corner"]["unchanged_prizes"]):
        P.append("Game Corner: prize count changed")
    # Frontier (live shop + unused exchange-corner table must agree)
    fr = man["frontier"]
    shop = parse_pairs(live["src"]["shop_menu"], "itemToBpPrice")
    unused = parse_pairs(live["src"]["frontier_unused"], "prizeList")
    for label, tbl in (("shop_menu", shop), ("exchange corner", unused)):
        d = dict(tbl)
        for k, v in fr["tm_prices"].items():
            if d.get(f"ITEM_{k}") != v["expected_after"]:
                P.append(f"Frontier ({label}) {k}: BP {d.get(f'ITEM_{k}')} != locked {v['expected_after']}")
        if [list(x) for x in tbl if not re.fullmatch(r"ITEM_TM\d\d", x[0])] != fr["unchanged_item_prices"]:
            P.append(f"Frontier ({label}): non-TM item price/list modified")
        if [i[5:] for i, _ in tbl if re.fullmatch(r"ITEM_TM\d\d", i)] != fr["tm_list_order"]:
            P.append(f"Frontier ({label}): TM list differs from locked 16")
    sc = live["src"]["scrcmd"]
    right = re.search(r"BattleFrontierRightExchangeServiceCorner\[\] = \{(.*?)\};", sc, re.S)
    ids = re.findall(r"ITEM_(TM\d\d)", right.group(1)) if right else []
    if ids != fr["tm_list_order"]:
        P.append("Frontier TM shop list (scrcmd) != locked 16")
    # Department Store / all TM+HM item prices unchanged
    for k, price in man["department_store"]["tm_hm_item_prices"].items():
        got = live["tm_items"].get(k, {}).get("price")
        if got != price:
            P.append(f"Department Store/{k}: item price {got} != KEEP {price}")


def check_duplicate_guards(live: dict, man: dict, P: list[str]):
    sh = live["src"]["shop_menu"]
    if "pl_msg_00000543_00039" not in live["msg_0543"]:
        P.append("shop duplicate message pl_msg_00000543_00039 missing")
    own = sh.find("Shop_AlreadyOwnsTM(shopMenu)) {")
    money = sh.find("currMoney < shopMenu->itemPrice")
    if own < 0:
        P.append("shop: duplicate-TM guard missing")
    elif money < 0 or own > money:
        P.append("shop: duplicate-TM guard must run before the money/BP check")
    helper = re.search(r"static BOOL Shop_AlreadyOwnsTM\([^;]*?\)\n\{.*?\n}\n", sh, re.S)
    if not helper or "Bag_GetItemQuantity" not in helper.group(0) or "Shop_IsTM" not in helper.group(0):
        P.append("shop: duplicate guard does not check TM ownership")
    elif "MART_TYPE_NORMAL" not in helper.group(0) or "MART_TYPE_FRONTIER" not in helper.group(0):
        P.append("shop: duplicate guard scope (normal + frontier marts) lost")
    isTM = re.search(r"static BOOL Shop_IsTM\([^;]*?\)\n\{.*?\n}\n", sh, re.S)
    if not isTM or "ITEM_TM01" not in isTM.group(0) or "ITEM_HM01" not in isTM.group(0):
        P.append("shop: Shop_IsTM must be the TM range (not generic items)")
    if "Shop_IsTM(shopMenu->itemId)) {\n            shopMenu->itemAmountMax = 1;" not in sh:
        P.append("shop: TM quantity cap lost")
    ps = live["src"]["prize_script"]
    if "VeilstoneCityPrizeExchange_Text_AlreadyHaveTM" not in live["msg_prize"]:
        P.append("Game Corner duplicate message missing")
    a = ps.find("CheckItem VAR_0x8000, 1, VAR_RESULT")
    b = ps.find("HasCoins VAR_RESULT, VAR_0x8001")
    c = ps.find("SubtractCoins VAR_0x8001")
    if a < 0 or not (a < b < c):
        P.append("Game Corner: duplicate check must precede HasCoins/SubtractCoins")


def check_roster(live: dict, ctx: dict, man: dict, P: list[str]):
    r = man["tm_roster"]
    for key in ("tm21", "tm78"):
        got = live["tm_items"].get(key.upper(), {}).get("teachesMove")
        if got != r[key]["expected_after"]:
            P.append(f"{key.upper()} assignment: {got!r} != {r[key]['expected_after']!r}")
    # Compatibility: counts + exact recipient sets from the locked C3H manifest
    for key, tm in (("tm21", "TM21"), ("tm78", "TM78")):
        want = set(ctx["tm21_78_recipients"][key]["recipients"])
        got = live["species"][tm]
        if len(got) != r[key]["recipients"]:
            P.append(f"{tm} compatibility count {len(got)} != {r[key]['recipients']}")
        if got != want:
            P.append(f"{tm} compatibility set differs: +{sorted(got - want)} -{sorted(want - got)}")


def check_acquisition(live: dict, man: dict, P: list[str]):
    base = man["first_acquisition_keep"]["field_tm_fingerprint"]
    cur = live["fingerprint"]
    for rel in sorted(set(base) | set(cur)):
        if base.get(rel) != cur.get(rel):
            P.append(f"TM placement changed in {rel}: {base.get(rel)} -> {cur.get(rel)}")


def check_created(live: dict, ctx: dict, P: list[str]):
    toks = live["src"]["moves_txt"].split()
    if "MAX_MOVES" not in toks or toks.index("MAX_MOVES") != ctx["manifest"]["created_moves_pin"]["max_moves"]:
        P.append("MAX_MOVES != 490")
    for m in ctx["created"]["moves"]:
        if m["const"] not in toks or toks.index(m["const"]) != m["id"]:
            P.append(f"created move {m['const']} id/registration damaged")


def validate(live: dict, ctx: dict) -> list[str]:
    P: list[str] = []
    man = ctx["manifest"]
    c = man["counts"]
    if c["tms"] != 92 or c["hms"] != 8 or c["changed_hms"] != 5 or len(man["hm_battle"]) != 8:
        P.append("manifest counts wrong")
    if sum(1 for v in man["hm_battle"].values() if v["changed"]) != 5:
        P.append("manifest must mark exactly five changed HMs")
    if len(man["game_corner"]["tm_prices"]) != 15 or len(man["frontier"]["tm_prices"]) != 16:
        P.append("manifest price table sizes wrong")
    check_hms(live, man, P)
    check_defog(live["src"]["defog"], man, P)
    check_reusable(live["src"], man, P)
    check_economy(live, man, P)
    check_duplicate_guards(live, man, P)
    check_roster(live, ctx, man, P)
    check_acquisition(live, man, P)
    check_created(live, ctx, P)
    return P


def main() -> int:
    problems = validate(load_live(), load_ctx())
    for p in problems:
        print("FAIL:", p)
    print(f"C2 validation: {'OK' if not problems else 'FAILED'} ({len(problems)} problems)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
