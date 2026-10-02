#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/economy/economy_manifest.json.

Before-values are read from the pinned base commit; after-values come from the locked spec (and the mechanical
status-medicine derivation). Fails closed if live source disagrees with the locked after-values.
"""
from __future__ import annotations

import json
import os

from economy_lib import *

SPEC = "docs/overhaul/economy/EXP_ECONOMY_SPEC.md"


def main():
    live, base = load_live(), load_base()
    edits = []
    for k, v in LOCKED_PRICES.items():
        sec = "s6 Vitamins" if k in ("hp_up", "protein", "iron", "calcium", "zinc", "carbos") else "s5 Healing"
        edits.append({"category": "item_price", "key": k, "path": f"res/items/data/{k}.json", "field": "price",
                      "before": base["prices"][k], "after": v, "authority": f"{SPEC}#{sec}", "gate": "unchanged (existing vendors)"})
    for k in STATUS_MEDICINES:
        edits.append({"category": "item_price", "key": k, "path": f"res/items/data/{k}.json", "field": "price",
                      "before": base["prices"][k], "after": status_target(base["prices"][k]),
                      "authority": f"{SPEC}#s5 status medicine (mechanical: lowest clean 50-increment >= 75% of vanilla)",
                      "gate": "unchanged (existing vendors)"})
    edits.append({"category": "item_price", "key": "rare_candy", "path": "res/items/data/rare_candy.json", "field": "price",
                  "before": base["prices"]["rare_candy"], "after": 5000, "authority": f"{SPEC}#s10 (preferred 5000)",
                  "gate": "postgame only (FLAG_GAME_COMPLETED)"})
    bt = parse_prize_table(base["src"]["prize"])
    for k, (b, a) in PRIZE_CHANGES.items():
        assert bt[k] == b, (k, bt[k])
        edits.append({"category": "trainer_prize_multiplier", "key": k, "path": SRC["prize"], "before": b, "after": a,
                      "authority": f"{SPEC}#s4"})
    tutors = []
    for i, (n, o) in enumerate(zip(live["tutors"], base["tutors"])):
        assert n["move"] == o["move"] and n["location"] == o["location"]
        tutors.append({"index": i, "move": o["move"], "location": o["location"], "path": SRC["tutors"],
                       "before": {k: o[k] for k in SHARD_FIELDS}, "after": {k: -(-o[k] // 2) for k in SHARD_FIELDS},
                       "authority": f"{SPEC}#s8"})
        assert {k: n[k] for k in SHARD_FIELDS} == tutors[-1]["after"], o["move"]
    man = {
        "schema": "economy_manifest/1", "base_commit": BASE_COMMIT, "spec": SPEC,
        "edits": edits, "tutors": tutors,
        "exp": {"path": SRC["battle_script"], "authority": f"{SPEC}#s2",
                "raw_pool": "floor(base_exp_reward * defeated_level / 7)", "battle_pool_percent": 60, "team_pool": "raw - battle_pool",
                "remainder_policy": "lowest party slots first, battle pool and team pool independently; pre-modifier sum == raw (legacy min-1 only for battle-group members whose total would be 0)",
                "evs": "actual participants only", "modifiers_unchanged": ["Lucky Egg 1.5x", "trainer 1.5x", "traded 1.5x", "foreign traded 1.7x"],
                "gate": "global"},
        "move_reminder": {"path": SRC["reminder_script"], "text": SRC["reminder_text"], "before": "ITEM_HEART_SCALE x1 per lesson",
                          "after": "free", "authority": f"{SPEC}#s7", "gate": "Pastoria (unchanged)"},
        "evolution_stone_shop": {"vendor_id": STONE_VENDOR_ID, "vendor_script": SRC["vitamin_vendor_script"], "stock_path": SRC["marts"],
                                 "stock_array": "VeilstoneDeptStoreStock_2F_MID", "before": parse_stock_arrays(base["src"]["marts"])["VeilstoneDeptStoreStock_2F_MID"],
                                 "added": required_stones(), "base_prices": {s: base["prices"][s[5:].lower()] for s in required_stones()},
                                 "authority": f"{SPEC}#s9", "gate": "Veilstone Department Store (reachable at/after 4th-badge window, before E4); not postgame-gated"},
        "rare_candy_postgame": {"vendor_id": RARE_CANDY_VENDOR_ID, "stock_array": "FightAreaPostgameStock", "stock_path": SRC["marts"],
                                "script": SRC["fight_area_script"], "price": 5000, "price_note": "5000 chosen: item JSON price only drives purchase and 50% sell value (2400 -> 2500); no other code reads it",
                                "authority": f"{SPEC}#s10", "gate": "FLAG_GAME_COMPLETED (Fight Area clown vendor)"},
        "frozen_c2_economy_files": list(C2_ECONOMY_FILES),
    }
    out = os.path.join(ROOT, MANIFEST)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(man, f, indent=2)
        f.write("\n")
    print(f"{len(edits)} edits, {len(tutors)} tutor entries -> {MANIFEST}")


if __name__ == "__main__":
    main()
