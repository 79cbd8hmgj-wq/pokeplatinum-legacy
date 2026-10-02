#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/c2_mechanics_manifest.json.

Before-values are read from the pinned base commit (not typed in); after-values are the locked C2 spec.
"""
from __future__ import annotations

import json
import os
import re

from c2_lib import *

HM_FINAL = {  # dir: (name, class, type, power, accuracy, pp, effect, chance, changed)
    "cut": ("Cut", "CLASS_PHYSICAL", "TYPE_NORMAL", 70, 100, 30, "BATTLE_EFFECT_HIGH_CRITICAL", 0, True),
    "fly": ("Fly", "CLASS_PHYSICAL", "TYPE_FLYING", 100, 100, 15, "BATTLE_EFFECT_FLY", 0, True),
    "surf": ("Surf", "CLASS_SPECIAL", "TYPE_WATER", 95, 100, 15, "BATTLE_EFFECT_DOUBLE_DAMAGE_DIVE", 0, False),
    "strength": ("Strength", "CLASS_PHYSICAL", "TYPE_NORMAL", 80, 100, 15, "BATTLE_EFFECT_HIT", 0, False),
    "defog": ("Defog", "CLASS_STATUS", "TYPE_FLYING", 0, 0, 15, "BATTLE_EFFECT_REMOVE_HAZARDS_SCREENS_EVA_DOWN", 0, True),
    "rock_smash": ("Rock Smash", "CLASS_PHYSICAL", "TYPE_FIGHTING", 60, 100, 15, "BATTLE_EFFECT_LOWER_DEFENSE_HIT", 50, True),
    "waterfall": ("Waterfall", "CLASS_PHYSICAL", "TYPE_WATER", 80, 100, 15, "BATTLE_EFFECT_FLINCH_HIT", 20, False),
    "rock_climb": ("Rock Climb", "CLASS_PHYSICAL", "TYPE_NORMAL", 90, 95, 20, "BATTLE_EFFECT_CONFUSE_HIT", 20, True),
}
GAME_CORNER = {"TM90": 1000, "TM58": 1000, "TM75": 2000, "TM32": 2000, "TM44": 2500, "TM89": 3000, "TM10": 3000, "TM27": 3000,
               "TM21": 4000, "TM35": 4000, "TM24": 4000, "TM13": 4000, "TM29": 4000, "TM74": 5000, "TM68": 6000}
FRONTIER_BP = {"TM06": 16, "TM73": 16, "TM61": 16, "TM45": 16, "TM40": 20, "TM31": 20, "TM89": 20, "TM08": 24, "TM04": 24,
               "TM81": 32, "TM30": 32, "TM53": 32, "TM36": 40, "TM59": 40, "TM71": 40, "TM26": 40}


def base_json(rel):
    return json.loads(base_text(rel))


def main():
    hms = {}
    for d, (name, cls, typ, pw, acc, pp, eff, ch, changed) in HM_FINAL.items():
        b = base_json(f"res/moves/{d}/data.json")
        before = {"power": b["power"], "accuracy": b["accuracy"], "pp": b["pp"], "effect": b["effect"]["type"], "chance": b["effect"]["chance"]}
        after = {"power": pw, "accuracy": acc, "pp": pp, "effect": eff, "chance": ch}
        hms[d] = {"name": name, "hm": f"HM{list(HM_FINAL).index(d) + 1:02d}", "class": cls, "type": typ, "range": b["range"],
                  "source": f"res/moves/{d}/data.json", "owner": f"c2.hm.{d}", "changed": changed,
                  "expected_before": before, "expected_after": after}
        assert d == "defog" or (before != after) == changed, d  # Defog changes in its battle subscript, not data.json
    gc_base = parse_pairs(base_text(SRC["game_corner"]), "sGameCornerPrizeData")
    gc = {"source": SRC["game_corner"], "owner": "c2.economy.game_corner",
          "unchanged_prizes": [[i, p] for i, p in gc_base if not re.fullmatch(r"ITEM_TM\d\d", i)],
          "tm_prices": {k: {"expected_before": dict(gc_base)[f"ITEM_{k}"], "expected_after": v} for k, v in GAME_CORNER.items()},
          "tm_order": [i for i, _ in gc_base if re.fullmatch(r"ITEM_TM\d\d", i)]}
    shop_base = parse_pairs(base_text(SRC["shop_menu"]), "itemToBpPrice")
    fr_base = dict(shop_base)
    fr = {"sources": [SRC["shop_menu"], SRC["frontier_unused"]], "owner": "c2.economy.frontier",
          "unchanged_item_prices": [[i, p] for i, p in shop_base if not re.fullmatch(r"ITEM_TM\d\d", i)],
          "tm_prices": {k: {"expected_before": fr_base.get(f"ITEM_{k}"), "expected_after": v} for k, v in FRONTIER_BP.items()},
          "tm_list_order": list(FRONTIER_BP),
          "note": "TM89 U-turn is not in the live Frontier TM shop at base; the locked table lists it at 20 BP, so it is added (list + price)."}
    tm_prices = {}
    for p in sorted(glob_items()):
        tm_prices[os.path.basename(p)[:-5].upper()] = base_json(p)["price"]
    # The retail/decomp baseline gives TM78 on Route 204 North, but locked C2 progression
    # intentionally keeps reusable Power Gem late in Victory Road. Build the expected final
    # acquisition fingerprint as "baseline + this one explicit locked override".
    acquisition_fp = field_tm_fingerprint(lambda r: base_text(r), base_files())
    route204 = "res/field/scripts/scripts_route_204_north.s"
    victory = "res/field/scripts/scripts_victory_road_1f.s"
    if route204 in acquisition_fp:
        acquisition_fp[route204].pop("ITEM_TM78", None)
        if not acquisition_fp[route204]:
            acquisition_fp.pop(route204)
    acquisition_fp.setdefault(victory, {})["ITEM_TM78"] = 1

    manifest = {
        "version": 1, "domain": "c2-tm-hm-mechanics", "status": "LOCKED_IMPLEMENTED",
        "base_commit": BASE_COMMIT,
        "authority": ["docs/overhaul/tm_hm/TM_HM_SPEC.md", "docs/overhaul/MASTER_SPEC.md"],
        "counts": {"tms": 92, "hms": 8, "changed_hms": 5, "game_corner_tm_prices": 15, "frontier_tm_prices": 16},
        "hm_battle": hms,
        "defog_semantics": {
            "source": SRC["defog"], "owner": "c2.hm.defog",
            "both_sides_hazards": ["SPIKES", "TOXIC_SPIKES", "STEALTH_ROCK"],
            "target_side_only": ["REFLECT", "LIGHT_SCREEN", "SAFEGUARD", "MIST"],
            "evasion_minus": 1,
        },
        "reusable_tm": {
            "source": SRC["party_callbacks"], "owner": "c2.tm.reusable", "function": "TeachMove",
            "expected_before": "removal guarded by Item_IsHMMove(learnedMove) == FALSE",
            "expected_after": "removal guarded by usedItem < ITEM_TM01 || usedItem > ITEM_HM08",
            "other_bag_removals_pinned": {SRC["party_callbacks"]: 3, SRC["party_main"]: 3},
        },
        "tm_roster": {
            "owner": "c2.tm.roster",
            "tm21": {"source": "res/items/data/tm21.json", "expected_before": "MOVE_FRUSTRATION", "expected_after": "MOVE_AIR_SLASH", "recipients": 49},
            "tm78": {"source": "res/items/data/tm78.json", "expected_before": "MOVE_CAPTIVATE", "expected_after": "MOVE_POWER_GEM", "recipients": 27},
            "discrepancy": "Task brief and C3H record said the TM21/TM78 assignments were already implemented; live source only had the compatibility masks. The item->move assignment is applied here.",
        },
        "game_corner": gc,
        "frontier": fr,
        "department_store": {"rule": "KEEP", "owner": "c2.economy.dept_store", "tm_hm_item_prices": tm_prices,
                             "tm21_tm78_price_note": "TM21/TM78 item prices keep their vanilla slot price."},
        "duplicate_vendor_protection": {
            "owner": "c2.economy.duplicate_guard",
            "shop_menu": {"source": SRC["shop_menu"], "check_before": "currMoney < shopMenu->itemPrice", "scope": "MART_TYPE_NORMAL + MART_TYPE_FRONTIER, TM items only", "message": "pl_msg_00000543_00039"},
            "game_corner": {"source": SRC["prize_script"], "message": "VeilstoneCityPrizeExchange_Text_AlreadyHaveTM", "check_before": ["HasCoins", "SubtractCoins"]},
        },
        "first_acquisition_keep": {
            "owner": "c2.tm.acquisition_keep",
            "fingerprint_base": BASE_COMMIT,
            "tm78_override": {
                "retail_source": route204,
                "locked_source": victory,
                "method": "Victory Road 1F Collector gift",
                "save_compat_flag": "FLAG_RECEIVED_ROUTE_204_NORTH_TM78",
            },
            "field_tm_fingerprint": acquisition_fp,
        },
        "text_corrections": {
            "res/text/oreburgh_city.json": "OreburghCity_Text_TMsSingleUseHMsOverAndOver no longer claims TMs are single use",
            "res/text/route_204_north.json": "Route204North Ace Trainer now teaches reusable-TM behavior without awarding TM78",
        },
        "created_moves_pin": {"max_moves": 490, "first": 468, "last": 489, "count": 22},
        "excluded_systems": ["species stats/types/abilities", "species learnsets", "TM compatibility masks (TM21/TM78 + C3 additions)",
                             "encounter tables", "availability gifts", "evolution tables", "trainer teams", "Poke Ball mechanics",
                             "breeding", "general economy", "legendary events", "visual assets/maps/lighting/UI", "tutor consolidation",
                             "field-move decoupling", "world TM pickup relocation except the locked TM78 Route 204 -> Victory Road override"],
    }
    path = os.path.join(ROOT, MANIFEST)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote", MANIFEST)


def glob_items():
    return [p for p in git("ls-tree", "-r", "--name-only", BASE_COMMIT, "res/items/data").split() if re.search(r"/[th]m\d\d\.json$", p)]


def base_files():
    return [p for p in git("ls-tree", "-r", "--name-only", BASE_COMMIT, "res/field").split()
            if re.match(r"res/field/(scripts/[^/]+\.s|events/[^/]+\.json)$", p)]


if __name__ == "__main__":
    main()
