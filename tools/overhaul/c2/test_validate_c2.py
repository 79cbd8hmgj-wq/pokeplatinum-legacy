#!/usr/bin/env python3
"""Mutation tests: the C2 validator must pass the clean tree and reject each corruption."""
from __future__ import annotations

import copy
import sys

from validate_c2 import load_ctx, load_live, validate

CTX = load_ctx()
LIVE = load_live()


def run(fn):
    live, ctx = copy.deepcopy(LIVE), copy.deepcopy(CTX)
    fn(live, ctx)
    return validate(live, ctx)


def sub(key, old, new, count=1):
    def f(live, ctx):
        assert old in live["src"][key], (key, old)
        live["src"][key] = live["src"][key].replace(old, new, count)
    return f


def mv(d, **kw):
    def f(live, ctx):
        live["moves"][d].update(kw)
    return f


def eff(d, t=None, chance=None):
    def f(live, ctx):
        if t is not None:
            live["moves"][d]["effect"]["type"] = t
        if chance is not None:
            live["moves"][d]["effect"]["chance"] = chance
    return f


def drop_defog_line(pattern):
    def f(live, ctx):
        lines = live["src"]["defog"].splitlines()
        kept = [ln for ln in lines if pattern not in ln]
        assert len(kept) < len(lines), pattern
        live["src"]["defog"] = "\n".join(kept)
    return f


def add_defog(line):
    def f(live, ctx):
        live["src"]["defog"] += "\n    " + line + "\n"
    return f


def price(table, item, val):
    return sub(table, f"{{ ITEM_{item}, ", f"{{ ITEM_{item}, {val}, X", 1)  # placeholder, replaced below


def set_pair(key, item, new):
    import re

    def f(live, ctx):
        s, n = re.subn(rf"(\{{ ITEM_{item}, )\d+( \}})", rf"\g<1>{new}\2", live["src"][key], count=1)
        assert n == 1, (key, item)
        live["src"][key] = s
    return f


def item_price(tm, val):
    def f(live, ctx):
        live["tm_items"][tm]["price"] = val
    return f


def species(tm, name, add=True):
    def f(live, ctx):
        (live["species"][tm].add if add else live["species"][tm].discard)(name)
    return f


def fp(rel, token, n):
    def f(live, ctx):
        live["fingerprint"].setdefault(rel, {})[token] = n
    return f


def reorder_guard(sh):
    call = "Shop_AlreadyOwnsTM(shopMenu)) {"
    sh = sh.replace(call, "FALSE) {", 1)
    return sh.replace("currMoney < shopMenu->itemPrice", "currMoney < shopMenu->itemPrice || " + call.replace(") {", ""), 1)


CALLBACKS_REUSABLE = "if (usedItem < ITEM_TM01 || usedItem > ITEM_HM08) {"

CASES = {
    # HM data
    "Cut wrong BP": mv("cut", power=50),
    "Cut wrong accuracy": mv("cut", accuracy=95),
    "Cut loses high-crit effect": eff("cut", "BATTLE_EFFECT_HIT"),
    "Cut PP changed": mv("cut", pp=25),
    "Fly loses two-turn effect": eff("fly", "BATTLE_EFFECT_HIT"),
    "Fly wrong BP (vanilla 90)": mv("fly", power=90),
    "Fly wrong accuracy": mv("fly", accuracy=95),
    "Surf accidentally changed (BP)": mv("surf", power=90),
    "Surf effect changed": eff("surf", "BATTLE_EFFECT_HIT"),
    "Strength accidentally changed": mv("strength", power=90),
    "Rock Smash wrong BP": mv("rock_smash", power=40),
    "Rock Smash loses 50% Defense drop": eff("rock_smash", "BATTLE_EFFECT_HIT", 0),
    "Rock Smash chance changed": eff("rock_smash", chance=30),
    "Rock Climb wrong accuracy": mv("rock_climb", accuracy=85),
    "Rock Climb loses confusion": eff("rock_climb", "BATTLE_EFFECT_HIT", 0),
    "Rock Climb confusion chance changed": eff("rock_climb", chance=10),
    "Waterfall altered (BP)": mv("waterfall", power=90),
    "Waterfall flinch removed": eff("waterfall", "BATTLE_EFFECT_HIT", 0),
    "Defog PP changed": mv("defog", pp=10),
    # Defog behaviour
    "Defog only clears target-side hazards (Spikes)": drop_defog_line("CHECK_SIDE_COND_CLEAR, SIDE_COND_SPIKES_LAYERS, _ATK_TOXIC_SPIKES"),
    "Defog fails to clear Toxic Spikes (attacker)": drop_defog_line("CHECK_SIDE_COND_CLEAR, SIDE_COND_TOXIC_SPIKES_LAYERS, _ATK_STEALTH_ROCK"),
    "Defog fails to clear Stealth Rock (attacker)": drop_defog_line("UpdateVar OPCODE_FLAG_OFF, BTLVAR_SIDE_CONDITIONS_ATTACKER, SIDE_CONDITION_STEALTH_ROCK"),
    "Defog fails to clear Stealth Rock (defender)": drop_defog_line("UpdateVar OPCODE_FLAG_OFF, BTLVAR_SIDE_CONDITIONS_DEFENDER, SIDE_CONDITION_STEALTH_ROCK"),
    "Defog fails to clear Spikes (defender)": drop_defog_line("CheckSideCondition BTLSCR_DEFENDER, CHECK_SIDE_COND_CLEAR, SIDE_COND_SPIKES_LAYERS"),
    "Defog fails to clear Toxic Spikes (defender)": drop_defog_line("CheckSideCondition BTLSCR_DEFENDER, CHECK_SIDE_COND_CLEAR, SIDE_COND_TOXIC_SPIKES_LAYERS"),
    "Defog clears user's own Reflect": add_defog("CheckSideCondition BTLSCR_ATTACKER, CHECK_SIDE_COND_CLEAR, SIDE_COND_REFLECT_TURNS, _181"),
    "Defog clears user's own Light Screen": add_defog("CheckSideCondition BTLSCR_ATTACKER, CHECK_SIDE_COND_CLEAR, SIDE_COND_LIGHT_SCREEN_TURNS, _181"),
    "Defog clears user's own Safeguard/Mist via mask": add_defog("UpdateVar OPCODE_FLAG_OFF, BTLVAR_SIDE_CONDITIONS_ATTACKER, SIDE_CONDITION_MIST"),
    "Defog stops clearing target Reflect": drop_defog_line("CheckSideCondition BTLSCR_DEFENDER, CHECK_SIDE_COND_CLEAR, SIDE_COND_REFLECT_TURNS"),
    "Defog stops clearing target Mist": drop_defog_line("CheckSideCondition BTLSCR_DEFENDER, CHECK_SIDE_COND_CLEAR, SIDE_COND_MIST_TURNS"),
    "Defog stops clearing target Safeguard": drop_defog_line("CheckSideCondition BTLSCR_DEFENDER, CHECK_SIDE_COND_CLEAR, SIDE_COND_SAFEGUARD_TURNS"),
    "Defog loses evasion drop": sub("defog", "MOVE_SUBSCRIPT_PTR_EVASION_DOWN_1_STAGE", "MOVE_SUBSCRIPT_PTR_NONE"),
    # reusable TMs
    "TM still consumed after teaching (vanilla guard)": sub("party_callbacks", CALLBACKS_REUSABLE, "if (Item_IsHMMove(application->partyMenu->learnedMove) == FALSE) {"),
    "generic consumables reusable (removal deleted)": sub("party_callbacks", "Bag_TryRemoveItem(application->partyMenu->bag, application->partyMenu->usedItemID, 1, HEAP_ID_PARTY_MENU);\n        }\n\n        Pokemon_UpdateFriendship", "}\n\n        Pokemon_UpdateFriendship"),
    "other consumable path made reusable (Sacred Ash removal)": sub("party_callbacks", "Bag_TryRemoveItem(application->partyMenu->bag, application->partyMenu->usedItemID, 1, HEAP_ID_PARTY_MENU);\n                application->partyMenu->menuSelectionResult", "application->partyMenu->menuSelectionResult"),
    "party main consumable removal deleted": sub("party_main", "Bag_TryRemoveItem(app->partyMenu->bag, app->partyMenu->usedItemID, 1, HEAP_ID_PARTY_MENU);", ""),
    "reusable guard wrong range": sub("party_callbacks", CALLBACKS_REUSABLE, "if (usedItem < ITEM_TM01 || usedItem > ITEM_TM92) {"),
    # TM roster
    "TM21 assignment regression (Frustration)": lambda l, c: l["tm_items"]["TM21"].update(teachesMove="MOVE_FRUSTRATION"),
    "TM78 assignment regression (Captivate)": lambda l, c: l["tm_items"]["TM78"].update(teachesMove="MOVE_CAPTIVATE"),
    "TM21 compat regression (recipient lost)": species("TM21", "charizard", add=False),
    "TM21 compat leak (Starly)": species("TM21", "starly"),
    "TM78 compat regression (recipient lost)": species("TM78", "persian", add=False),
    "TM78 compat leak (old Captivate mask)": species("TM78", "tyranitar"),
    # Game Corner
    "Game Corner wrong price (Substitute)": set_pair("game_corner", "TM90", 2000),
    "Game Corner wrong price (Giga Impact vanilla)": set_pair("game_corner", "TM68", 20000),
    "Game Corner wrong price (Air Slash)": set_pair("game_corner", "TM21", 8000),
    "Game Corner wrong price (Rest)": set_pair("game_corner", "TM44", 2000),
    "Game Corner held-item reward modified": set_pair("game_corner", "WIDE_LENS", 1500),
    "Game Corner prize removed": sub("game_corner", "        { ITEM_TM74, 5000 },\n", ""),
    # Frontier
    "Frontier wrong price (Toxic, vanilla 32)": set_pair("shop_menu", "TM06", 32),
    "Frontier wrong price (U-turn)": set_pair("shop_menu", "TM89", 40),
    "Frontier wrong price (Earthquake)": set_pair("shop_menu", "TM26", 80),
    "Frontier exchange-corner table out of sync": set_pair("frontier_unused", "TM04", 48),
    "Frontier unrelated item price modified": set_pair("shop_menu", "CHOICE_BAND", 32),
    "Frontier U-turn missing from shop list": sub("scrcmd", "        ITEM_TM89,\n", ""),
    "Frontier TM missing from price table": sub("shop_menu", "        { ITEM_TM89, 20 },\n", ""),
    # Dept store
    "Department Store TM price modified": item_price("TM35", 5000),
    "Department Store HM price modified": item_price("HM01", 1),
    # duplicate guards
    "shop duplicate guard missing": sub("shop_menu", "if (Shop_AlreadyOwnsTM(shopMenu)) {", "if (FALSE) {"),
    "shop duplicate guard after money check": lambda l, c: l["src"].__setitem__("shop_menu", reorder_guard(l["src"]["shop_menu"])),
    "shop duplicate guard applies to all items": sub("shop_menu", "return itemId >= ITEM_TM01 && itemId < ITEM_HM01;", "return TRUE;"),
    "shop duplicate message missing": lambda l, c: l["msg_0543"].discard("pl_msg_00000543_00039"),
    "Game Corner duplicate check after Coins check": lambda l, c: l["src"].__setitem__("prize_script", l["src"]["prize_script"].replace("CheckItem VAR_0x8000, 1, VAR_RESULT", "Nop")),
    "Game Corner duplicate message missing": lambda l, c: l["msg_prize"].discard("VeilstoneCityPrizeExchange_Text_AlreadyHaveTM"),
    # acquisition
    "TM relocated (Galactic HQ TM21 moved)": fp("res/field/events/events_galactic_hq_3f.json", "ITEM_TM21", 0),
    "TM relocated (new TM pickup added)": fp("res/field/scripts/scripts_route_204_north.s", "ITEM_TM21", 1),
    "TM78 Route 204 NPC removed": fp("res/field/scripts/scripts_route_204_north.s", "ITEM_TM78", 0),
    # created moves
    "custom move ID damaged": lambda l, c: l["src"].__setitem__("moves_txt", l["src"]["moves_txt"].replace("MOVE_STAR_JAB", "MOVE_STAR_JABX")),
    "MAX_MOVES regression": lambda l, c: l["src"].__setitem__("moves_txt", l["src"]["moves_txt"].replace("MOVE_STAR_JAB\nMAX_MOVES", "MOVE_STAR_JAB\nMOVE_X\nMAX_MOVES")),
    # manifest integrity
    "manifest drops an HM": lambda l, c: c["manifest"]["hm_battle"].pop("surf"),
    "manifest shrinks Game Corner table": lambda l, c: c["manifest"]["game_corner"]["tm_prices"].pop("TM68"),
}

FORWARD_COMPAT = {  # legitimate later changes that must NOT break C2
    "HM description rewritten": lambda l, c: l["moves"]["cut"].__setitem__("description", ["x\n"]),
    "HM contest data retuned": lambda l, c: l["moves"]["fly"].__setitem__("contest", {"effect": "X", "type": "Y"}),
    "Defog comments/labels reformatted": lambda l, c: l["src"].__setitem__("defog", l["src"]["defog"] + "\n// extra comment\n"),
}


def main() -> int:
    base = validate(copy.deepcopy(LIVE), copy.deepcopy(CTX))
    if base:
        print("clean tree rejected:", base)
        return 1
    bad = 0
    rejected = 0
    for name, fn in CASES.items():
        try:
            problems = run(fn)
        except Exception as e:  # a broken mutation is a test bug, not a pass
            print(f"ERROR     {name}: {e!r}")
            bad += 1
            continue
        if problems:
            rejected += 1
        else:
            print(f"ACCEPTED  {name}  <-- should have been rejected")
            bad += 1
    fwd_ok = 0
    for name, fn in FORWARD_COMPAT.items():
        if run(fn):
            print(f"REJECTED  {name}  <-- forward-compatible change must be accepted")
            bad += 1
        else:
            fwd_ok += 1
    print(f"rejecting mutations: {rejected}/{len(CASES)}; forward-compatible cases: {fwd_ok}/{len(FORWARD_COMPAT)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
