#!/usr/bin/env python3
"""D7 standalone species/C3 validator: replays the 225 archived guarded ledger POSTCONDITIONS against live source
(audit only - never re-applies them), plus the locked final corrections and structural identity checks."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import recover_c3h_ledgers as rec  # noqa: E402
from qa_lib import Checker, lines, species_data, text  # noqa: E402

TYPES = {f"TYPE_{t}" for t in ("NORMAL FIRE WATER ELECTRIC GRASS ICE FIGHTING POISON GROUND FLYING PSYCHIC BUG ROCK GHOST DRAGON DARK STEEL MYSTERY").split()}


def main():
    c = Checker("species/C3 validation")
    live = species_data()
    ledgers = rec.decode_ledgers(text("docs/overhaul/implementation/archive/c3h-apply-species-original.yml"))
    c.check([len(l["changes"]) for l in ledgers] == rec.EXPECTED_COUNTS and sum(len(l["changes"]) for l in ledgers) == 225, "C3H ledger counts != [67,27,40,53,38]")
    for li, led in enumerate(ledgers):
        for ch in led["changes"]:
            d, op, sp = live[ch["species"]], ch["operation"], ch["species"]
            ls = [tuple(x) for x in d["learnset"]["by_level"]]
            tag = f"L{li + 1} {sp} {op}"
            if op == "set_abilities":
                c.check(d["abilities"] == ch["to"], f"{tag}: {d['abilities']} != {ch['to']}")
            elif op == "set_base_stat":
                c.check(d["base_stats"][ch["stat"]] == ch["to"], f"{tag} {ch['stat']}: {d['base_stats'][ch['stat']]} != {ch['to']}")
            elif op == "set_types":
                c.check(d["types"] == ch["to"], f"{tag}: {d['types']} != {ch['to']}")
            elif op == "replace_level_move":
                c.check(tuple(ch["to"]) in ls, f"{tag}: {ch['to']} absent")
            elif op == "insert_level_move":
                c.check(tuple(ch["entry"]) in ls, f"{tag}: {ch['entry']} absent")
            elif op == "remove_level_move":
                c.check(tuple(ch["entry"]) not in ls, f"{tag}: {ch['entry']} still present")
            else:
                c.check(False, f"{tag}: unknown operation")
    ls = lambda s: {tuple(x) for x in live[s]["learnset"]["by_level"]}
    for s, entries in {"banette": [(31, "MOVE_SHADOW_BALL"), (38, "MOVE_CURSED_STITCH"), (42, "MOVE_SHADOW_CLAW")],
                       "torkoal": [(52, "MOVE_YAWN"), (55, "MOVE_HEAT_WAVE")], "seviper": [(55, "MOVE_SLUDGE_BOMB")],
                       "glalie": [(43, "MOVE_IRON_HEAD")]}.items():
        for e in entries:
            c.check(e in ls(s), f"final correction {s} {e} missing")
    c.check(live["glalie"]["types"] == ["TYPE_ICE", "TYPE_STEEL"], f"glalie types {live['glalie']['types']}")
    moves, abilities, species = set(lines("generated/moves.txt")), set(lines("generated/abilities.txt")), set(lines("generated/species.txt"))
    for s, d in live.items():
        if s == "none":  # placeholder slot (all-zero stats)
            continue
        by = d["learnset"]["by_level"]
        c.check([l for l, _ in by] == sorted(l for l, _ in by), f"{s}: level-up learnset not ascending")
        c.check(all(m in moves for _, m in by), f"{s}: invalid level-up move")
        c.check(all(t in TYPES for t in d["types"]), f"{s}: invalid type {d['types']}")
        c.check(all(a in abilities for a in d["abilities"]), f"{s}: invalid ability {d['abilities']}")
        c.check(all(1 <= v <= 255 for v in d["base_stats"].values()), f"{s}: base stat out of range")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
