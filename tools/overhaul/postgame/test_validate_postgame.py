#!/usr/bin/env python3
"""Mutation tests: each mutation of the live source must make validate_postgame.py FAIL the matching check."""
import sys

import frontier_lib as L
import validate_postgame as VP


def run(path, old, new, count=1):
    def reader(p):
        t = L.read(p)
        if p == path:
            assert old in t, (p, old)
            t = t.replace(old, new, count)
        return t
    v = VP.V(reader)
    for fn in (v.check_bp, v.check_milestones_and_castle, v.check_shop, v.check_battleground, v.check_rematches, v.check_prints):
        try:
            fn()
        except Exception as e:  # a crash while parsing a mutated file also counts as detection
            v.rec(f"{fn.__name__} crashed", False, repr(e))
    return [r for r in v.results if r[1] == "FAIL"]


MUTATIONS = {
    "4x payout (double application)": ("src/overlay104/battle_castle.c", "return bp * FRONTIER_BP_PAYOUT_MULTIPLIER;", "return bp * FRONTIER_BP_PAYOUT_MULTIPLIER * FRONTIER_BP_PAYOUT_MULTIPLIER;"),
    "multiplier 3x": ("include/constants/battle_frontier.h", "FRONTIER_BP_PAYOUT_MULTIPLIER 2", "FRONTIER_BP_PAYOUT_MULTIPLIER 3"),
    "tower payout missing": ("src/unk_02049D08.c", "battlePoints *= FRONTIER_BP_PAYOUT_MULTIPLIER;", ""),
    "credit command also doubles": ("src/unk_020494DC.c", "WifiBattleTowerRecord_UpdateBattlePoints(SaveData_GetWifiBattleTowerRecord(saveData), value, BATTLE_POINTS_FUNC_ADD);\n\n    return FALSE;\n}\n\nBOOL ScrCmd_RemoveBattlePoints", "WifiBattleTowerRecord_UpdateBattlePoints(SaveData_GetWifiBattleTowerRecord(saveData), value * FRONTIER_BP_PAYOUT_MULTIPLIER, BATTLE_POINTS_FUNC_ADD);\n\n    return FALSE;\n}\n\nBOOL ScrCmd_RemoveBattlePoints"),
    "wrong TM price": ("src/overlay007/shop_menu.c", "{ ITEM_TM26, 40 }", "{ ITEM_TM26, 80 }"),
    "non-TM price changed": ("src/overlay007/shop_menu.c", "{ ITEM_CHOICE_BAND, 48 }", "{ ITEM_CHOICE_BAND, 24 }"),
    "Rival weekend-only again": ("res/field/scripts/scripts_survival_area.s", "    GoTo SurvivalArea_RivalBattle\n    End\n", "    GetDayOfWeek VAR_MAP_LOCAL_0x00\n    GoTo SurvivalArea_RivalBattle\n    End\n"),
    "Battleground calendar-locked": ("res/field/scripts/scripts_battleground.s", "Battleground_OnTransition:\n", "Battleground_OnTransition:\n    GetDayOfWeek VAR_RESULT\n"),
    "Battleground reshuffle forgets a daily flag": ("res/field/scripts/scripts_battleground.s", "    ClearFlag FLAG_DAILY_DEFEATED_BATTLEGROUND_MIRA\n", ""),
    "Master Ball flag set before bag check": ("res/field/scripts/scripts_common.s", "GoToIfSet FLAG_RECEIVED_FRONTIER_ALL_GOLD_BP, CommonScript_GiveFrontierAllGoldItem", "SetFlag FLAG_RECEIVED_FRONTIER_ALL_GOLD_MASTER_BALL\n    GoToIfSet FLAG_RECEIVED_FRONTIER_ALL_GOLD_BP, CommonScript_GiveFrontierAllGoldItem"),
    "duplicate print BP path": ("res/field/scripts/scripts_battle_arcade.s", "    SetVar VAR_0x8004, 10\n    Common_GiveFrontierPrintBP\n", "    SetVar VAR_0x8004, 10\n    Common_GiveFrontierPrintBP\n    Common_GiveFrontierPrintBP\n"),
    "League rematch not flag-gated": ("res/field/scripts/scripts_pokemon_league_aaron_room.s", "CallIfUnset FLAG_ARRESTED_CHARON_STARK_MOUNTAIN, PokemonLeagueAaronRoom_StartAaronBattle", ""),
}


def main():
    bad = 0
    assert not run("src/scrcmd.c", "previousTrainers", "previousTrainers")[:0] or True
    for name, (path, old, new) in MUTATIONS.items():
        fails = run(path, old, new)
        status = "detected" if fails else "MISSED"
        bad += 0 if fails else 1
        print(f"{status}: {name} ({len(fails)} failing checks)")
    # baseline must be clean
    base = run("src/scrcmd.c", "previousTrainers", "previousTrainers")
    print("baseline failures:", len(base))
    return bad + len(base)


if __name__ == "__main__":
    sys.exit(main())
