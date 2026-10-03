#!/usr/bin/env python3
"""D6 F3: apply the targeted Frontier set corrections and write frontier_set_changes.json.

Each change carries a before-value guard (moves + nature must match the live source exactly) and is
applied in place; the script is idempotent only in the sense that it refuses to run twice (the guard
fails once a set already has the target value).  Run with --check to verify an applied tree.
"""
import json
import sys

import frontier_lib as L

AUTH = "docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md s5; implementation plan F3"

# set -> (reason, authority detail, before moves, after moves, before nature, after nature)
CHANGES = [
    ("farfetchd_1", "RETYPE: Fighting/Flying Farfetch'd had no Fighting move", "spec s5 retyped Pokemon",
     ["MOVE_SLASH", "MOVE_AIR_CUTTER", "MOVE_KNOCK_OFF", "MOVE_SWORDS_DANCE"],
     ["MOVE_SLASH", "MOVE_CLOSE_COMBAT", "MOVE_KNOCK_OFF", "MOVE_SWORDS_DANCE"], None, None),
    ("raichu_1", "STAT: all-physical set on Atk 70 / SpA 100 Raichu; keeps Steel STAB via Flash Cannon", "spec s5 redistributed stats; Electric/Steel Raichu",
     ["MOVE_THUNDER_PUNCH", "MOVE_IRON_TAIL", "MOVE_SLAM", "MOVE_QUICK_ATTACK"],
     ["MOVE_THUNDERBOLT", "MOVE_FLASH_CANNON", "MOVE_GRASS_KNOT", "MOVE_QUICK_ATTACK"], "NATURE_ADAMANT", "NATURE_MODEST"),
    ("raichu_2", "STAT: all-physical set on Atk 70 / SpA 100 Raichu", "spec s5 redistributed stats",
     ["MOVE_THUNDER_PUNCH", "MOVE_FOCUS_PUNCH", "MOVE_SWEET_KISS", "MOVE_THUNDER_WAVE"],
     ["MOVE_THUNDER", "MOVE_FOCUS_BLAST", "MOVE_SWEET_KISS", "MOVE_THUNDER_WAVE"], "NATURE_JOLLY", "NATURE_TIMID"),
    ("raichu_4", "STAT: all-physical set on Atk 70 / SpA 100 Raichu; adds Steel STAB", "spec s5 redistributed stats; Electric/Steel Raichu",
     ["MOVE_VOLT_TACKLE", "MOVE_RETURN", "MOVE_BRICK_BREAK", "MOVE_THUNDER_WAVE"],
     ["MOVE_VOLT_TACKLE", "MOVE_FLASH_CANNON", "MOVE_BRICK_BREAK", "MOVE_THUNDER_WAVE"], "NATURE_ADAMANT", "NATURE_HARDY"),
    ("glalie_3", "STAT: all-special set on Atk 90 / SpA 70 Glalie; adds Steel STAB", "spec s5 Ice/Steel Glalie",
     ["MOVE_ICE_BEAM", "MOVE_SHADOW_BALL", "MOVE_SIGNAL_BEAM", "MOVE_WATER_PULSE"],
     ["MOVE_FROST_RUSH", "MOVE_SHADOW_BALL", "MOVE_IRON_HEAD", "MOVE_ICE_BEAM"], "NATURE_MODEST", "NATURE_HARDY"),
    ("glalie_4", "STAT: all-special set on Atk 90 / SpA 70 Glalie; adds Steel STAB", "spec s5 Ice/Steel Glalie",
     ["MOVE_BLIZZARD", "MOVE_DARK_PULSE", "MOVE_SHEER_COLD", "MOVE_HAIL"],
     ["MOVE_BLIZZARD", "MOVE_IRON_HEAD", "MOVE_SHEER_COLD", "MOVE_HAIL"], "NATURE_MODEST", "NATURE_HARDY"),
    ("ledian_1", "STAT: all-special set on Atk 85 / SpA 45 Ledian (new Iron Fist ability)", "spec s5 changed abilities + stats",
     ["MOVE_SILVER_WIND", "MOVE_AIR_CUTTER", "MOVE_AGILITY", "MOVE_BATON_PASS"],
     ["MOVE_DRAIN_PUNCH", "MOVE_AERIAL_ACE", "MOVE_AGILITY", "MOVE_BATON_PASS"], "NATURE_TIMID", "NATURE_JOLLY"),
    ("beedrill_1", "REMOVED: Assurance no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_TWINEEDLE", "MOVE_TOXIC", "MOVE_ASSURANCE", "MOVE_AGILITY"],
     ["MOVE_TWINEEDLE", "MOVE_TOXIC", "MOVE_POISON_JAB", "MOVE_AGILITY"], None, None),
    ("cacturne_1", "REMOVED: Faint Attack no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_BULLET_SEED", "MOVE_FAINT_ATTACK", "MOVE_SPIKES", "MOVE_INGRAIN"],
     ["MOVE_BULLET_SEED", "MOVE_SUCKER_PUNCH", "MOVE_SPIKES", "MOVE_INGRAIN"], None, None),
    ("carnivine_2", "REMOVED: Wring Out no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_SEED_BOMB", "MOVE_WRING_OUT", "MOVE_CRUNCH", "MOVE_INGRAIN"],
     ["MOVE_SEED_BOMB", "MOVE_POWER_WHIP", "MOVE_CRUNCH", "MOVE_INGRAIN"], None, None),
    ("kabutops_1", "REMOVED: Metal Sound no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_AQUA_JET", "MOVE_ROCK_TOMB", "MOVE_HARDEN", "MOVE_METAL_SOUND"],
     ["MOVE_AQUA_JET", "MOVE_ROCK_TOMB", "MOVE_HARDEN", "MOVE_STEALTH_ROCK"], None, None),
    ("lumineon_1", "REMOVED: Captivate no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_WATER_GUN", "MOVE_U_TURN", "MOVE_CAPTIVATE", "MOVE_ATTRACT"],
     ["MOVE_WATER_GUN", "MOVE_U_TURN", "MOVE_AQUA_RING", "MOVE_ATTRACT"], None, None),
    ("masquerain_1", "REMOVED: Scary Face no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_SILVER_WIND", "MOVE_AIR_CUTTER", "MOVE_SWEET_SCENT", "MOVE_SCARY_FACE"],
     ["MOVE_SILVER_WIND", "MOVE_AIR_CUTTER", "MOVE_SWEET_SCENT", "MOVE_STUN_SPORE"], None, None),
    ("relicanth_1", "REMOVED: Mud Sport no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_WATER_PULSE", "MOVE_ROCK_TOMB", "MOVE_MUD_SPORT", "MOVE_HARDEN"],
     ["MOVE_WATER_PULSE", "MOVE_ROCK_TOMB", "MOVE_YAWN", "MOVE_HARDEN"], None, None),
    ("solrock_1", "REMOVED: Psywave no longer learnable", "spec s5 C3 learnset identity",
     ["MOVE_PSYWAVE", "MOVE_ROCK_TOMB", "MOVE_COSMIC_POWER", "MOVE_LIGHT_SCREEN"],
     ["MOVE_PSYCHIC", "MOVE_ROCK_TOMB", "MOVE_COSMIC_POWER", "MOVE_LIGHT_SCREEN"], None, None),
]


HALL_SRC = "src/overlay104/battle_hall_helpers.c"
HALL_SKIP = {"SPECIES_WORMADAM"}  # form-specific entries (Sandy/Trash) cannot be read from the base species record


def hall_pool():
    """Returns (source text, species list, [(start, end, t0, t1)] spans of each type pair)."""
    import re
    src = L.read(HALL_SRC)
    m = re.search(r"sBattleHallPotentialOpponents\[\]\s*=\s*\{(.*?)\};", src, re.S)
    species = re.findall(r"SPECIES_\w+", m.group(1))
    t = re.search(r"sBattleHallPotentialOpponentTypes\[\]\[2\]\s*=\s*\{(.*?)\};", src, re.S)
    spans = [(t.start(1) + x.start(), t.start(1) + x.end(), x.group(1), x.group(2))
             for x in re.finditer(r"\{\s*(TYPE_\w+),\s*(TYPE_\w+)\s*\}", t.group(1))]
    assert len(species) == len(spans), (len(species), len(spans))
    return src, species, spans


def hall_changes(check):
    src, species, spans = hall_pool()
    out, edits = [], []
    for i, (spc, (a, b, t0, t1)) in enumerate(zip(species, spans)):
        if spc in HALL_SKIP:
            continue
        cur = L.species_data(spc)["types"]
        if check:
            assert {t0, t1} == set(cur), f"Hall pool entry {i} {spc}: {t0},{t1} vs {cur}"
            continue
        if {t0, t1} != set(cur):
            new = f"{{ {cur[0]}, {cur[1]} }}"
            edits.append((a, b, new))
            out.append({"source_path": HALL_SRC, "field": f"sBattleHallPotentialOpponentTypes[{i}] ({spc})",
                        "before": [t0, t1], "target": list(cur),
                        "authority": "spec s14 Hall: retyped Pokemon must be classified by overhaul types; static pool audited for retype drift",
                        "guard": "pair equals the species' vanilla type pair at apply time"})
    for a, b, new in sorted(edits, reverse=True):
        src = src[:a] + new + src[b:]
    if edits:
        with open(L.p(HALL_SRC), "w") as f:
            f.write(src)
    return out


def path_of(name):
    return f"{L.SETS_DIR}/{name}.json"


def main():
    check = "--check" in sys.argv
    records = []
    for name, reason, auth, bm, am, bn, an in CHANGES:
        path = path_of(name)
        with open(L.p(path)) as f:
            text = f.read()
        d = json.loads(text)
        if check:
            assert d["moves"] == am, (name, d["moves"])
            if an:
                assert d["nature"] == an, (name, d["nature"])
        else:
            assert d["moves"] == bm, f"guard failed for {name}: {d['moves']}"
            if bn:
                assert d["nature"] == bn, f"guard failed for {name}: {d['nature']}"
            d["moves"] = am
            if an:
                d["nature"] = an
            out = json.dumps(d, indent=4) + ("\n" if text.endswith("\n") else "")
            with open(L.p(path), "w") as f:
                f.write(out)
        rec = {"source_path": path, "field": "moves", "before": bm, "target": am,
               "authority": f"{AUTH}; {auth}", "guard": "live moves equal before-value at apply time", "reason": reason}
        if an:
            rec["nature"] = {"before": bn, "target": an}
        records.append(rec)
    hall = hall_changes(check) if True else []
    if check:
        hall = json.load(open(L.p("docs/overhaul/implementation/postgame/frontier_set_changes.json")))["hall_pool_type_changes"]
    manifest = {
        "schema": "frontier_set_changes/1",
        "start_sha": L.START_SHA,
        "brain_edits": 0,
        "brain_note": "F4: the Silver/Gold Brain sets (Palmer, Dahlia, Darach) were audited separately; no overhaul-caused conflict was found. Thorton and Argenta use rental/type-pool formats with no fixed sets.",
        "changes": records,
        "hall_pool_type_changes": hall,
    }
    if not check:
        with open(L.p("docs/overhaul/implementation/postgame/frontier_set_changes.json"), "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
    print(("checked" if check else "applied"), len(records), "set changes,", len(hall), "Hall pool type entries")


if __name__ == "__main__":
    main()
