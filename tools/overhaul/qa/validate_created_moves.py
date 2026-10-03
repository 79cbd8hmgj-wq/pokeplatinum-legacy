#!/usr/bin/env python3
"""D7 standalone created-move validator (IDs 468-489): table, data files, registries, Magnet Volley invariant."""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from qa_lib import Checker, jl, lines, text  # noqa: E402

TYPES = {"Normal": "TYPE_NORMAL", "Fire": "TYPE_FIRE", "Water": "TYPE_WATER", "Electric": "TYPE_ELECTRIC", "Grass": "TYPE_GRASS",
         "Ice": "TYPE_ICE", "Fighting": "TYPE_FIGHTING", "Poison": "TYPE_POISON", "Ground": "TYPE_GROUND", "Flying": "TYPE_FLYING",
         "Psychic": "TYPE_PSYCHIC", "Bug": "TYPE_BUG", "Rock": "TYPE_ROCK", "Ghost": "TYPE_GHOST", "Dragon": "TYPE_DRAGON",
         "Dark": "TYPE_DARK", "Steel": "TYPE_STEEL"}
CLASSES = {"Physical": "CLASS_PHYSICAL", "Special": "CLASS_SPECIAL", "Status": "CLASS_STATUS"}


def array_containing(src, anchor):
    """Body of the brace-delimited initializer that contains `anchor`."""
    i = src.index(anchor)
    a, b = src.rfind("{", 0, i), src.index("}", i)
    return src[a:b]


def main():
    c = Checker("created-move validation")
    man = jl("docs/overhaul/implementation/created_moves_manifest.json")
    names = lines("generated/moves.txt")
    moves = man["moves"]
    al = man["allocation"]
    c.check(len(moves) == al["custom_move_count"] == 22, f"expected 22 custom moves, manifest has {len(moves)}")
    c.check([m["id"] for m in moves] == list(range(al["first_custom_move_id"], al["last_custom_move_id"] + 1)), "ids not contiguous 468..489")
    c.check(len(names) > 490 and names[490] == "MAX_MOVES" and al["max_moves_target"] == 490, "MAX_MOVES must be index 490")
    for m in moves:
        c.check(names[m["id"]] == m["const"], f"moves.txt[{m['id']}]={names[m['id']]} != {m['const']}")
        slug = m["const"][len("MOVE_"):].lower()
        try:
            d = jl(f"res/moves/{slug}/data.json")
        except OSError:
            c.check(False, f"missing res/moves/{slug}/data.json")
            continue
        c.check(d["type"] == TYPES[m["type"]], f"{m['const']} type {d['type']} != manifest {m['type']}")
        c.check(d["class"] == CLASSES[m["category"]], f"{m['const']} class {d['class']} != manifest {m['category']}")
        for k in ("power", "accuracy", "pp"):
            want = m[k] or 0  # manifest uses null for "never misses" / "no damage"
            c.check(d[k] == want, f"{m['const']} {k} {d[k]} != manifest {m[k]}")
        c.check(("MOVE_FLAG_MAKES_CONTACT" in d["flags"]) == bool(m["contact"]), f"{m['const']} contact flag != manifest")
    mv = jl("res/moves/magnet_volley/data.json")
    inv = man["implementation_invariants"]["magnet_volley"]
    c.check(mv["effect"]["type"] == "BATTLE_EFFECT_HIT_THREE_TIMES_EQUAL_POWER" and mv["power"] == inv["power_per_hit"] == 25 and inv["hits"] == 3
            and not inv["triple_kick_escalation"], "Magnet Volley must be exactly 3 equal 25-BP hits (no Triple Kick escalation)")
    c.check("MOVE_TRIPLE_KICK" not in str(mv["effect"]), "Magnet Volley must not use Triple Kick escalation")
    src = text("src/battle/battle_lib.c")
    c.check("MOVE_RESONANT_SLASH" in array_containing(src, "MOVE_HYPER_VOICE,"), "Resonant Slash missing from the sound-move registry")
    c.check("MOVE_STAR_JAB" in array_containing(src, "MOVE_BULLET_PUNCH,"), "Star Jab missing from the punching-move registry")
    c.check(man["implementation_invariants"]["sound_registry"] == ["MOVE_RESONANT_SLASH"] and
            man["implementation_invariants"]["punch_registry"] == ["MOVE_STAR_JAB"], "manifest registry invariants changed")
    # Dragon Swipe: finalized move, recipient unresolved -> must not be invented anywhere.
    from qa_lib import ROOT
    hit = []
    for pat in ("res/pokemon/*/data.json", "res/trainers/data/*.json", "res/trainers/frontier/pokemon/*.json"):
        for p in glob.glob(os.path.join(ROOT, pat)):
            if "MOVE_DRAGON_SWIPE" in open(p, encoding="utf-8").read():
                hit.append(os.path.relpath(p, ROOT))
    c.check(not hit, f"Dragon Swipe recipient invented in {hit[:3]} (historical final recipient is unresolved; do not guess)")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
