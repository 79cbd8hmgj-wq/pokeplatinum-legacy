#!/usr/bin/env python3
"""D6: write frontier_rewards / frontier_shop_prices / rematch_access / print_rewards manifests.

Before values are read from START_SHA with git; targets are read from the working tree, so a manifest
can only be generated for a tree that already carries the change.  validate_postgame.py re-checks
every record against the live source (manifest/source drift).
"""
import json
import re

import frontier_lib as L

MULT = "FRONTIER_BP_PAYOUT_MULTIPLIER"
AUTH_BP = "docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md s3, s14; implementation plan F1"

PAYOUTS = [
    ("tower", "src/unk_02049D08.c", "BattleTower_GiveBattlePointsReward",
     "WifiBattleTowerRecord_UpdateBattlePoints(battleTower->unk_74, battlePoints, BATTLE_POINTS_FUNC_ADD);",
     "battlePoints *= FRONTIER_BP_PAYOUT_MULTIPLIER;",
     "ordinary round, wifi/link-multi ranks, Palmer Silver/Gold (20 BP base) - all pass through this single credit point"),
    ("factory", "src/overlay104/ov104_022339B4.c", "ov104_022347F8", "return v0;", "return v0 * FRONTIER_BP_PAYOUT_MULTIPLIER;",
     "ordinary round and Thorton Silver/Gold (20 BP base); script GiveBattlePoints credits the returned value"),
    ("castle", "src/overlay104/battle_castle.c", "BattleCastle_GetEarnedBP", "return bp;", "return bp * FRONTIER_BP_PAYOUT_MULTIPLIER;",
     "ordinary round and Darach Silver/Gold; Castle Points are a separate currency and are not touched"),
    ("hall_round", "src/overlay104/battle_hall.c", "BattleHall_GetEarnedBP", "return bp;", "return bp * FRONTIER_BP_PAYOUT_MULTIPLIER;",
     "ordinary Hall round and Argenta Silver/Gold"),
    ("arcade_round", "src/overlay104/battle_arcade.c", "BattleArcade_GetEarnedBP", "return bp;", "return bp * FRONTIER_BP_PAYOUT_MULTIPLIER;",
     "ordinary round and Dahlia Silver/Gold"),
    ("arcade_roulette", "src/overlay104/battle_arcade_helpers.c", "BattleArcade_GetFreeBPFromEvent", "return bp;", "return bp * FRONTIER_BP_PAYOUT_MULTIPLIER;",
     "Arcade roulette +1 BP / +3 BP events (base 1 -> 2, 3 -> 6 in round 1-3 tier; higher tiers scale likewise)"),
    ("hall_record_keeper", "src/scrcmd_battle_hall.c", "ScrCmd_GetBattleHallRecordKeeperStats",
     None, "earnedBP *= FRONTIER_BP_PAYOUT_MULTIPLIER;",
     "Battle Hall record-keeper win-total milestones are Battle Hall BP awards and are doubled once at the credit point"),
]

# Tables and credit paths that must stay byte-identical to START_SHA (multiplier lives only at the payout points above).
UNCHANGED = [
    ("src/overlay104/battle_castle.c", "sBPPerRoundSolo", "castle BP table"),
    ("src/overlay104/battle_hall.c", "sBPPerRoundSolo", "hall BP table"),
    ("src/overlay104/battle_arcade.c", "sBPPerRoundSolo", "arcade BP table"),
    ("src/overlay104/battle_arcade_helpers.c", "sBonus1BP", "arcade +1 BP table"),
    ("src/overlay104/battle_arcade_helpers.c", "sBonus3BP", "arcade +3 BP table"),
]


def main():
    base = L.git_show(L.START_SHA, "include/constants/battle_frontier.h")
    cur = L.read("include/constants/battle_frontier.h")
    milestones = {k: int(re.search(rf"#define {k}\s+(\d+)", cur).group(1)) for k in
                  ("HALL_STREAK_SILVER_BATTLE", "HALL_STREAK_GOLD_BATTLE", "CASTLE_STREAK_SILVER_BATTLE", "CASTLE_STREAK_GOLD_BATTLE")}
    for k, v in milestones.items():
        assert int(re.search(rf"#define {k}\s+(\d+)", base).group(1)) == v
    recs = []
    for name, path, fn, before, target, note in PAYOUTS:
        assert target in L.read(path), (name, target)
        recs.append({"facility_path": name, "source_path": path, "function": fn,
                     "before": before or "(no multiplier)", "target": target, "multiplier": 2,
                     "authority": AUTH_BP, "guard": "target appears exactly once in the file; base tables identical to start SHA", "covers": note})
    out = {
        "schema": "frontier_rewards/1", "start_sha": L.START_SHA,
        "multiplier_constant": {"source_path": "include/constants/battle_frontier.h", "name": MULT, "before": "(undefined)", "target": 2,
                                "authority": AUTH_BP, "guard": "define value is exactly 2"},
        "payout_points": recs,
        "unchanged_unmultiplied_credit_paths": [
            {"source_path": "src/unk_020494DC.c", "function": "ScrCmd_GiveBattlePoints", "note": "field-script GiveBattlePoints (print milestone bonuses use this path and must stay 1x)"},
            {"source_path": "src/overlay104/frscrcmd.c", "function": "FrontierScrCmd_GiveBattlePoints", "note": "frontier-script credit of values already doubled at their source"},
        ],
        "unchanged_base_tables": [{"source_path": a, "symbol": b, "label": c} for a, b, c in UNCHANGED],
        "castle_points": {"altered": False, "note": "no Castle Point (CP) code was touched; BattleCastle_GetEarnedBP is the only Castle edit"},
        "milestones_unchanged": milestones,
        "milestones_note": "Tower/Factory/Castle/Arcade streak 21/49 and Hall battle 50/170 are untouched; Tower/Factory/Arcade use literal 21/49 in their own files.",
    }
    json.dump(out, open(L.p("docs/overhaul/implementation/postgame/frontier_rewards.json"), "w"), indent=2)
    open(L.p("docs/overhaul/implementation/postgame/frontier_rewards.json"), "a").write("\n")

    # shop
    src = L.read("src/overlay007/shop_menu.c")
    base_src = L.git_show(L.START_SHA, "src/overlay007/shop_menu.c")
    tab = lambda s: re.findall(r"\{ (ITEM_\w+), (\d+) \}", s[s.index("itemToBpPrice"):s.index("itemToBpPrice") + 3000].split("};")[0])
    prices = {k: int(v) for k, v in tab(src)}
    base_prices = {k: int(v) for k, v in tab(base_src)}
    assert prices == base_prices
    tm_locked = {"ITEM_TM06": 16, "ITEM_TM73": 16, "ITEM_TM61": 16, "ITEM_TM45": 16, "ITEM_TM40": 20, "ITEM_TM31": 20, "ITEM_TM89": 20,
                 "ITEM_TM08": 24, "ITEM_TM04": 24, "ITEM_TM81": 32, "ITEM_TM30": 32, "ITEM_TM53": 32,
                 "ITEM_TM36": 40, "ITEM_TM59": 40, "ITEM_TM71": 40, "ITEM_TM26": 40}
    for k, v in tm_locked.items():
        assert prices[k] == v, k
    shop = {
        "schema": "frontier_shop_prices/1", "start_sha": L.START_SHA,
        "source_path": "src/overlay007/shop_menu.c", "table": "Shop_GetItemBPPrice::itemToBpPrice",
        "authority": "docs/overhaul/tm_hm/TM_HM_SPEC.md s4 (Battle Frontier); BATTLE_FRONTIER_POSTGAME_SPEC.md s4",
        "result": "NO D6 SOURCE EDIT: the locked reduced TM BP prices were already applied by the C2 TM/HM mechanics commit (11fa503c) and are present at the D6 start SHA; every non-TM price is the live vanilla value.",
        "changed_records": [],
        "locked_tm_prices": tm_locked,
        "non_tm_prices_frozen": {k: v for k, v in prices.items() if k not in tm_locked},
        "guard": "full table equals start-SHA table; TM entries equal the locked prices; any other difference fails validate_postgame.py",
    }
    json.dump(shop, open(L.p("docs/overhaul/implementation/postgame/frontier_shop_prices.json"), "w"), indent=2)
    open(L.p("docs/overhaul/implementation/postgame/frontier_shop_prices.json"), "a").write("\n")


def rematch_and_print():
    AUTH = "docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md"
    rematch = {
        "schema": "rematch_access/1", "start_sha": L.START_SHA,
        "changed_records": [
            {"source_path": "res/field/scripts/scripts_survival_area.s", "symbol": "SurvivalArea_Rival",
             "before": "GetDayOfWeek; GoToIfEq SUNDAY/SATURDAY -> SurvivalArea_RivalBattle; otherwise idle chatter",
             "target": "GoTo SurvivalArea_RivalBattle (daily flag FLAG_DAILY_DEFEATED_SURVIVAL_AREA_RIVAL still gates repeats)",
             "authority": AUTH + " s9; plan F6", "guard": "no DAY_OF_WEEK reference remains in the file; daily flag set on victory and checked first"},
            {"source_path": "res/field/scripts/scripts_battleground.s", "symbol": "Battleground_ExpertM -> Battleground_OfferNewTrainers",
             "before": "ExpertM only talks; trainers regenerate once per calendar day (FLAG_DAILY_SET_BATTLEGROUND_TRAINERS)",
             "target": "after the group is resolved the proprietor clears the 13 per-trainer daily defeated flags and FLAG_DAILY_SET_BATTLEGROUND_TRAINERS, then re-enters the map so OnTransition regenerates up to 4 slots",
             "authority": AUTH + " s7; plan F5", "guard": "reshuffle requires every visible slot defeated or declined; partner prerequisite hides unchanged"},
            {"source_path": "src/scrcmd.c", "symbol": "ScrCmd_GetRandomBattlegroundTrainers",
             "before": "first leader slot chosen uniformly",
             "target": "first leader slot retried up to 8 times to avoid the previous group (cheap, best-effort duplicate avoidance)",
             "authority": AUTH + " s7 (avoid obvious immediate duplicates where practical)", "guard": "slot 2/3 selection and stat-trainer selection unchanged"},
        ],
        "audited_no_change": {
            "gym_leader_pool": {"source_path": "src/scrcmd.c", "symbol": "sBattlegroundGymLeaders", "count": 8,
                                 "rematch_trainer_ids": "Battleground_SetTrainer*: TRAINER_LEADER_*_REMATCH"},
            "partner_pool": ["Cheryl", "Riley", "Marley", "Buck", "Mira"],
            "league": {"flag": "FLAG_ARRESTED_CHARON_STARK_MOUNTAIN",
                        "rooms": ["aaron", "bertha", "flint", "lucian", "champion"],
                        "note": "E4/Cynthia rooms already choose *_REMATCH trainers on the postgame flag and are repeatable; nothing real-time gates them"},
            "fight_area": {"source_path": "res/field/scripts/scripts_fight_area.s",
                            "trainers": ["TRAINER_LEADER_VOLKNER_FIGHT_AREA", "TRAINER_ELITE_FOUR_FLINT_FIGHT_AREA",
                                         "TRAINER_RIVAL_FIGHT_AREA_PIPLUP", "TRAINER_RIVAL_FIGHT_AREA_TURTWIG", "TRAINER_RIVAL_FIGHT_AREA_CHIMCHAR"],
                            "note": "all five references resolve to trainer-overhaul records; script flow untouched"},
        },
    }
    json.dump(rematch, open(L.p("docs/overhaul/implementation/postgame/rematch_access.json"), "w"), indent=2)
    open(L.p("docs/overhaul/implementation/postgame/rematch_access.json"), "a").write("\n")

    prints = {
        "schema": "print_rewards/1", "start_sha": L.START_SHA,
        "authority": AUTH + " s13; plan F8",
        "new_flags": [
            {"source_path": "generated/vars_flags.txt", "before": "FLAG_UNUSED_0x02D2", "target": "FLAG_RECEIVED_FRONTIER_ALL_SILVER_BP"},
            {"source_path": "generated/vars_flags.txt", "before": "FLAG_UNUSED_0x02D3", "target": "FLAG_RECEIVED_FRONTIER_ALL_SILVER_PP_MAX"},
            {"source_path": "generated/vars_flags.txt", "before": "FLAG_UNUSED_0x02D4", "target": "FLAG_RECEIVED_FRONTIER_ALL_GOLD_BP"},
            {"source_path": "generated/vars_flags.txt", "before": "FLAG_UNUSED_0x02D5", "target": "FLAG_RECEIVED_FRONTIER_ALL_GOLD_MASTER_BALL"},
        ],
        "per_facility": [
            {"facility": f, "source_path": f"res/field/scripts/scripts_battle_{f}.s", "state_var": f"VAR_BATTLE_{f.upper()}_PRINT_STATE",
             "silver": {"transition": "1->2", "bp": 10}, "gold": {"transition": "3->4", "bp": 30},
             "guard": "the print-state transition itself is the one-time guard; the claim routine only runs while the state is 1 or 3"}
            for f in ("tower", "factory", "castle", "hall", "arcade")],
        "all_prints": {
            "source_path": "res/field/scripts/scripts_common.s", "entry": "CommonScript_ProcessFrontierPrintRewards (0x80B)",
            "silver": {"requires": "all five print states >= 2", "bp": 50, "item": "ITEM_PP_MAX", "bp_flag": "FLAG_RECEIVED_FRONTIER_ALL_SILVER_BP", "item_flag": "FLAG_RECEIVED_FRONTIER_ALL_SILVER_PP_MAX"},
            "gold": {"requires": "all five print states == 4", "bp": 100, "item": "ITEM_MASTER_BALL", "bp_flag": "FLAG_RECEIVED_FRONTIER_ALL_GOLD_BP", "item_flag": "FLAG_RECEIVED_FRONTIER_ALL_GOLD_MASTER_BALL"},
            "full_bag": "CanFitItem is checked first; on failure the BP half stays granted (its own flag), the item flag stays clear, and the routine is re-run at every facility print claim, facility end-of-challenge, and Tower end-of-challenge",
            "guard": "the item flag is set only after AddItem succeeded; each half has its own flag so neither can be granted twice",
        },
        "text": {"source_path": "res/text/common_strings.json", "added": ["CommonStrings_Text_FrontierPrintBPReceived", "CommonStrings_Text_FrontierRewardBagFull"]},
    }
    json.dump(prints, open(L.p("docs/overhaul/implementation/postgame/print_rewards.json"), "w"), indent=2)
    open(L.p("docs/overhaul/implementation/postgame/print_rewards.json"), "a").write("\n")


if __name__ == "__main__":
    main()
    rematch_and_print()
    main()
