#!/usr/bin/env python3
"""Mutation tests: the economy validator must pass the clean tree and reject each corruption."""
from __future__ import annotations

import copy
import json
import sys

from economy_lib import *
from validate_economy import validate

LIVE, BASE = load_live(), load_base()
MAN = json.loads(read(MANIFEST))


def run(fn):
    live = copy.deepcopy(LIVE)
    fn(live)
    return validate(live, BASE, MAN)


def sub(key, old, new, count=1):
    def f(live):
        assert old in live["src"][key], (key, old)
        live["src"][key] = live["src"][key].replace(old, new, count)
    return f


def regex_sub(key, pattern, repl):
    import re

    def f(live):
        out, n = re.subn(pattern, repl, live["src"][key], count=1, flags=re.S)
        assert n == 1, (key, pattern)
        live["src"][key] = out
    return f


def price(item, v):
    return lambda live: live["prices"].__setitem__(item, v)


def tutor(i, **kw):
    return lambda live: live["tutors"][i].update(kw)


def drop_stone(stone):
    return sub("marts", f"    {stone},\n", "", 1)


CASES = {
    # EXP
    "5050_split_restored": sub("battle_consts", "EXP_BATTLE_POOL_PERCENT 60", "EXP_BATTLE_POOL_PERCENT 50"),
    "modern_full_exp_for_everyone": sub("battle_script", "teamPool / eligibleCount;", "exp;"),
    "party_size_pool_inflation": sub("battle_script", "teamPool / eligibleCount;", "teamPool;"),
    "exp_share_adds_extra_exp": sub("battle_script", "battleCtx->expAlloc[i] += battlePool / battleGroupCount;",
                                    "battleCtx->expAlloc[i] += battlePool / battleGroupCount + exp / 2;"),
    "participant_expshare_double_count": sub("battle_script", "battleGroupCount++;", "battleGroupCount++;\n                    battleGroupCount++;"),
    "fainted_denominator_bug": sub("battle_script", "&& Pokemon_GetValue(mon, MON_DATA_HP, NULL)\n                && Pokemon_GetValue(mon, MON_DATA_LEVEL", "&& Pokemon_GetValue(mon, MON_DATA_LEVEL"),
    "lv100_denominator_bug": regex_sub("battle_script", r"\n\s*&& Pokemon_GetValue\(mon, MON_DATA_LEVEL, NULL\) < MAX_POKEMON_LEVEL\) \{\n(\s*)u16 item", r") {\n\1u16 item"),
    "egg_denominator_bug": regex_sub("battle_script", r"\n\s*&& Pokemon_GetValue\(mon, MON_DATA_IS_EGG, NULL\) == FALSE", ""),
    "team_recipient_omitted": sub("battle_script", "if (eligibleMask & FlagIndex(i)) {\n                battleCtx->expAlloc[i] += teamPool", "if (battleGroupMask & FlagIndex(i)) {\n                battleCtx->expAlloc[i] += teamPool"),
    "recipient_mask_participants_only": sub("battle_script", "data->battleCtx->expRecipientMask & FlagIndex(slot)", "data->battleCtx->sideGetExpMask[battler] & FlagIndex(slot)"),
    "evs_to_bench": regex_sub("battle_script", r"if \(data->battleCtx->sideGetExpMask\[battler\] & FlagIndex\(slot\)\) \{\n(\s*)BattleScript_CalcEffortValues", r"if (TRUE) {\n\1BattleScript_CalcEffortValues"),
    "evs_to_expshare_holder": regex_sub("battle_script", r"if \(data->battleCtx->sideGetExpMask\[battler\] & FlagIndex\(slot\)\) \{\n(\s*)BattleScript_CalcEffortValues", r"if ((data->battleCtx->sideGetExpMask[battler] & FlagIndex(slot)) || itemEffect == HOLD_EFFECT_EXP_SHARE) {\n\1BattleScript_CalcEffortValues"),
    "trainer_bonus_altered": sub("battle_script", "if (battleType & BATTLE_TYPE_TRAINER) {\n                totalExp = totalExp * 150 / 100;", "if (battleType & BATTLE_TYPE_TRAINER) {\n                totalExp = totalExp * 200 / 100;"),
    "lucky_egg_altered": sub("battle_script", "if (itemEffect == HOLD_EFFECT_EXP_UP) {\n                totalExp = totalExp * 150 / 100;", "if (itemEffect == HOLD_EFFECT_EXP_UP) {\n                totalExp = totalExp * 200 / 100;"),
    "foreign_trade_altered": sub("battle_script", "totalExp = totalExp * 170 / 100;", "totalExp = totalExp * 150 / 100;"),
    "traded_altered": sub("battle_script", "totalExp = totalExp * 150 / 100;\n                }\n\n                msg.id = BattleStrings_Text_PokemonGainedABoostedExpPoints", "totalExp = totalExp * 120 / 100;\n                }\n\n                msg.id = BattleStrings_Text_PokemonGainedABoostedExpPoints"),
    "emerald_multiplier_added": sub("battle_script", "totalExp = data->battleCtx->expAlloc[slot];", "totalExp = data->battleCtx->expAlloc[slot];\n            totalExp = totalExp * 3 / 2;"),
    "raw_pool_formula_changed": sub("battle_script", "level) / 7;\n\n        u32 battlePool", "level) / 5;\n\n        u32 battlePool"),
    "empty_battle_group_loses_battle_pool": sub("battle_script", "            teamPool += battlePool;\n            battlePool = 0;\n", "            battlePool = 0;\n"),
    "battle_pool_constant_outside_guard": sub("battle_consts", "#define EXP_BATTLE_POOL_PERCENT 60\n\n#endif // POKEPLATINUM_CONSTANTS_BATTLE_H", "#endif // POKEPLATINUM_CONSTANTS_BATTLE_H\n\n#define EXP_BATTLE_POOL_PERCENT 60"),
    "participant_state_cleanup_removed": sub("battle_script", "        data->battleCtx->sideGetExpMask[battler] = 0;\n", ""),
    # Prices
    "potion_price_wrong": price("potion", 250),
    "full_restore_price_wrong": price("full_restore", 3000),
    "vitamin_price_wrong": price("protein", 9800),
    "status_price_wrong": price("full_heal", 600),
    "pokeball_price_edit": price("ultra_ball", 1000),
    "great_ball_price_edit": price("great_ball", 500),
    "unrelated_item_price_edit": price("max_revive", 3000),
    "tm_base_price_edit": price("tm01", 1),
    "rare_candy_wrong_price": price("rare_candy", 9999),
    "tuber_not_raised": regex_sub("prize", r"(TRAINER_CLASS_TUBER_MALE\]\s*= )3,", r"\g<1>1,"),
    "unrelated_trainer_multiplier_edit": regex_sub("prize", r"(TRAINER_CLASS_ACE_TRAINER_MALE\]\s*= )15,", r"\g<1>20,"),
    "gym_leader_multiplier_edit": regex_sub("prize", r"(TRAINER_CLASS_LEADER_ROARK\]\s*= )\d+,", r"\g<1>40,"),
    # Move Reminder
    "heart_scale_still_consumed": sub("reminder_script", "GoToIfEq VAR_RESULT, 0xFF, PastoriaCityEastHouse_ComeBackAnytime\n    ReleaseAll", "GoToIfEq VAR_RESULT, 0xFF, PastoriaCityEastHouse_ComeBackAnytime\n    RemoveItem ITEM_HEART_SCALE, 1, VAR_RESULT\n    ReleaseAll"),
    "heart_scale_still_required": sub("reminder_script", "    SetFlag FLAG_TALKED_TO_PASTORIA_CITY_EAST_HOUSE_MOVE_MANIAC\n", "    SetFlag FLAG_TALKED_TO_PASTORIA_CITY_EAST_HOUSE_MOVE_MANIAC\n    CheckItem ITEM_HEART_SCALE, 1, VAR_RESULT\n"),
    "reminder_dialogue_demands_heart_scale": sub("reminder_text", "come back and see me anytime.", "come back with a Heart Scale."),
    "reminder_cancel_removed": sub("reminder_script", "    GoToIfEq VAR_RESULT, 0xFF, PastoriaCityEastHouse_ComeBackAnytime\n", ""),
    "reminder_pool_check_removed": sub("reminder_script", "    CheckHasLearnableReminderMoves VAR_RESULT, VAR_0x8005\n", ""),
    # Tutors
    "tutor_cost_unhalved": tutor(0, redCost=2),
    "tutor_cost_floor_not_ceil": tutor(1, redCost=1),
    "tutor_free": lambda live: [live["tutors"][2].update({k: 0 for k in SHARD_FIELDS})],
    "tutor_zero_became_nonzero": tutor(0, greenCost=1),
    "tutor_move_changed": tutor(3, move="MOVE_SPLASH"),
    "tutor_location_changed": tutor(3, location="TUTOR_LOCATION_SURVIVAL_AREA"),
    "tutor_entry_dropped": lambda live: live["tutors"].pop(),
    # Stones
    **{f"stone_missing_{s[5:].lower()}": drop_stone(s) for s in ("ITEM_FIRE_STONE", "ITEM_MOON_STONE", "ITEM_SUN_STONE", "ITEM_DAWN_STONE")},
    "stone_vendor_postgame_gated": sub("vitamin_vendor_script", "VeilstoneStore2F_MiddleVendor:\n", "VeilstoneStore2F_MiddleVendor:\n    GoToIfUnset FLAG_GAME_COMPLETED, VeilstoneStore2F_Directory\n"),
    "oval_stone_added": sub("marts", "    ITEM_DAWN_STONE,\n", "    ITEM_DAWN_STONE,\n    ITEM_OVAL_STONE,\n"),
    "vitamin_stock_changed": sub("marts", "    ITEM_ZINC,\n", "", 1),
    # Rare Candy
    "rare_candy_in_common_mart": sub("marts", "    { ITEM_POKE_BALL, 0x1 },", "    { ITEM_RARE_CANDY, 0x1 },\n    { ITEM_POKE_BALL, 0x1 },"),
    "rare_candy_in_veilstone": sub("marts", "    ITEM_DAWN_STONE,\n", "    ITEM_DAWN_STONE,\n    ITEM_RARE_CANDY,\n"),
    "rare_candy_postgame_gate_removed": sub("fight_area_script", "    GoToIfUnset FLAG_GAME_COMPLETED, FightAreaMart_ClownNoStock\n", ""),
    "rare_candy_vendor_missing": sub("marts", "const u16 FightAreaPostgameStock[] = {\n    ITEM_RARE_CANDY,", "const u16 FightAreaPostgameStock[] = {\n    ITEM_POTION,"),
    # Frozen C2 economy
    "game_corner_modified": lambda live: live["c2_files"].__setitem__("src/scrcmd_game_corner_prize.c", live["c2_files"]["src/scrcmd_game_corner_prize.c"] + "\n// x"),
    "frontier_shop_modified": lambda live: live["c2_files"].__setitem__("src/overlay007/shop_menu.c", live["c2_files"]["src/overlay007/shop_menu.c"] + "\n// x"),
    "frontier_exchange_modified": lambda live: live["c2_files"].__setitem__("src/scrcmd.c", live["c2_files"]["src/scrcmd.c"] + "\n// x"),
}


def main() -> int:
    clean = validate(copy.deepcopy(LIVE), BASE, MAN)
    ok = not clean
    print(f"clean tree: {'PASS' if ok else 'FAIL'} ({len(clean)} failures)")
    for p in clean:
        print("   ", p)
    caught = 0
    for name, fn in CASES.items():
        try:
            failures = run(fn)
        except AssertionError as e:
            print(f"BROKEN CASE {name}: mutation did not apply {e}")
            ok = False
            continue
        if failures:
            caught += 1
        else:
            print(f"MISSED: {name}")
            ok = False
    print(f"mutations caught: {caught}/{len(CASES)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
