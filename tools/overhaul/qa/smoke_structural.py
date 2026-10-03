#!/usr/bin/env python3
"""D7 Phase 7 host-side structural smoke checks. NOT runtime evidence: these exercise the repository's host models and
data files only (no ROM, no emulator). Release behavior is untouched; nothing here is compiled into the game."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "economy"))
sys.path.insert(0, os.path.join(HERE, "..", "pokeballs"))
import exp_model as xm  # noqa: E402
from pokeball_model import ball_mod, catch_rate  # noqa: E402
from qa_lib import Checker, jl, text  # noqa: E402

ACES = {"leader_roark": 14, "leader_gardenia": 22, "leader_fantina": 27, "leader_maylene": 32, "leader_wake": 37,
        "leader_byron": 41, "leader_candice": 44, "leader_volkner": 50, "elite_four_aaron": 53, "elite_four_bertha": 55,
        "elite_four_flint": 57, "elite_four_lucian": 59, "champion_cynthia": 62}


def main():
    c = Checker("structural smoke (host-side, not runtime)")
    # 1. representative trainer battle setup: 8 Gyms + E4 + Cynthia
    for stem, ace in ACES.items():
        t = jl(f"res/trainers/data/{stem}.json")
        party = t["party"]
        c.check(1 <= len(party) <= 6 and max(m["level"] for m in party) == ace, f"{stem}: ace level/party size")
        c.check(all(m["moves"] and len(m["moves"]) <= 4 and all(x.startswith("MOVE_") for x in m["moves"]) for m in party), f"{stem}: moveset shape")
        c.check(bool(t["ai_flags"]), f"{stem}: no AI flags")
    # 2. EXP conservation with 1, 3 and 6 eligible members; EVs only for participants
    for n in (1, 3, 6):
        party = [xm.Member(slot=i, level=30, participant=(i == 0)) for i in range(n)]
        raw = xm.raw_pool(100, 30)
        alloc = xm.allocate(raw, party)
        c.check(sum(alloc.values()) == raw, f"EXP not conserved for {n} eligible: {sum(alloc.values())} != {raw}")
        c.check(xm.ev_recipients(party) == [0], f"EV recipients for {n} eligible must be the participant only")
    c.check(sum(xm.payout(100, 30, [xm.Member(slot=i, level=30, participant=(i == 0)) for i in range(6)], False).values())
            >= xm.raw_pool(100, 30), "6-eligible payout below the conserved pool")
    # 3. capture multipliers (locked D3 values) and the standard baseline
    c.check((ball_mod("quick", turns=0), ball_mod("quick", turns=1)) == (50, 10), "Quick Ball first-turn/later")
    c.check((ball_mod("repeat", caught=True), ball_mod("repeat", caught=False)) == (35, 10), "Repeat Ball")
    c.check((ball_mod("heal"),) == (15,), "Heal Ball multiplier")
    c.check(catch_rate(45, ball_mod("quick", turns=0), 100, 100) > catch_rate(45, 10, 100, 100), "Quick Ball turn-one advantage")
    # 4. shop inventory: renewable evolution stones live in the Veilstone 2F stock
    mart = text("include/data/mart_items.h")
    c.check(all(s in mart for s in ("ITEM_FIRE_STONE", "ITEM_WATER_STONE", "ITEM_THUNDERSTONE", "ITEM_LEAF_STONE", "ITEM_MOON_STONE",
                                    "ITEM_SUN_STONE", "ITEM_SHINY_STONE", "ITEM_DUSK_STONE", "ITEM_DAWN_STONE")), "evolution stones missing from mart stock")
    # 5. event flags / legendary retry state (manifest shape; behavior is covered by validate_legendary_availability.py)
    nat = jl("docs/overhaul/implementation/events/native_legendary_events.json")["events"]
    for e in nat:
        if e["one_time_vs_renewable"] == "ONE_TIME_UNTIL_CAPTURED":
            c.check(bool(e.get("retry_behavior")) and (e.get("respawn_guard") is not None or e.get("reset_script") is not None
                                                       or e.get("capture_flag") is not None or e.get("consumed_markers")),
                    f"{e['species']}: no retry/respawn record")
    # 6. Frontier BP reward / postgame access manifests present and non-empty
    for f in ("frontier_rewards", "print_rewards", "rematch_access", "frontier_shop_prices"):
        c.check(bool(jl(f"docs/overhaul/implementation/postgame/{f}.json")), f"postgame manifest {f} empty")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
