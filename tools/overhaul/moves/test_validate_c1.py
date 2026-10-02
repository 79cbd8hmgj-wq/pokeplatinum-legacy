#!/usr/bin/env python3
"""Mutation tests: the C1 validator must pass the clean tree and reject each corruption."""
from __future__ import annotations

import copy
import sys

from c1_lib import live_moves
from validate_c1 import load_ctx, validate

CTX = load_ctx()
LIVE = live_moves()


def mutated(fn):
    live, ctx = copy.deepcopy(LIVE), copy.deepcopy(CTX)
    fn(live, ctx)
    return validate(live, ctx)


def setf(name, key, val):
    def f(live, ctx):
        live[name][0][1][key] = val
    return f


def seteffect(name, val):
    def f(live, ctx):
        live[name][0][1]["effect"]["type"] = val
    return f


def vanilla(name):
    def f(live, ctx):
        live[name][0][1].update({k: CTX["base"][name][0][1][k] for k in ("power", "accuracy", "pp")})
    return f


def moves_txt(i, val):
    def f(live, ctx):
        ctx["moves_txt"][i] = val
    return f


CASES = {
    "power change (Fury Cutter wrong BP)": setf("Fury Cutter", "power", 25),
    "revert to vanilla (Fury Cutter)": vanilla("Fury Cutter"),
    "accuracy change (Hypnosis)": setf("Hypnosis", "accuracy", 60),
    "PP change (Bind)": setf("Bind", "pp", 15),
    "secondary chance (Rock Tomb)": lambda l, c: l["Rock Tomb"][0][1]["effect"].__setitem__("chance", 50),
    "high-crit behavior (Razor Wind back to charge)": seteffect("Razor Wind", "BATTLE_EFFECT_CHARGE_TURN_HIGH_CRIT"),
    "high-crit behavior (Razor Wind loses crit)": seteffect("Razor Wind", "BATTLE_EFFECT_HIT"),
    "multi-hit (Pin Missile effect)": seteffect("Pin Missile", "BATTLE_EFFECT_HIT"),
    "trapping (Fire Spin effect)": seteffect("Fire Spin", "BATTLE_EFFECT_HIT"),
    "trapping value (Sand Tomb Emerald 50/95)": lambda l, c: l["Sand Tomb"][0][1].update(power=50, accuracy=95),
    "HM later-pass value (Rock Smash)": setf("Rock Smash", "power", 60),
    "HM later-pass value (Cut)": setf("Cut", "accuracy", 100),
    "KEEP invariant (Magma Storm)": setf("Magma Storm", "power", 100),
    "KEEP invariant (Rock Slide)": setf("Rock Slide", "accuracy", 80),
    "unrelated move changed (Thunderbolt)": setf("Thunderbolt", "power", 100),
    "Razor Wind description stale": lambda l, c: l["Razor Wind"][0][1].__setitem__("description", ["A two-turn attack.\n"]),
    "Razor Wind script keeps charge message": lambda l, c: c.__setitem__("razor_script", "BufferMessage x"),
    "custom move: Magnet Volley power": setf("Magnet Volley", "power", 30),
    "custom move: Magnet Volley effect": seteffect("Magnet Volley", "BATTLE_EFFECT_HIT_THREE_TIMES"),
    "custom move: Resonant Slash unregistered": lambda l, c: c.__setitem__("battle_lib", c["battle_lib"].replace("MOVE_RESONANT_SLASH", "")),
    "custom move: Star Jab unregistered": lambda l, c: c.__setitem__("battle_lib", c["battle_lib"].replace("MOVE_STAR_JAB", "")),
    "custom move: id renumbered": moves_txt(468, "MOVE_FROST_RUSH"),
    "custom move: MAX_MOVES reduced": lambda l, c: c["moves_txt"].pop(),
    "custom move record deleted": lambda l, c: l.pop("Static Strike"),
    "manifest/guards disagreement": lambda l, c: c["guards"]["edits"][5]["after"].__setitem__("pp", 99),
    "manifest count != 82": lambda l, c: c["manifest"]["edits"].pop(),
}


def main() -> int:
    clean = validate(copy.deepcopy(LIVE), copy.deepcopy(CTX))
    bad = 0
    if clean:
        print("FAIL: clean tree rejected:", clean[:3])
        bad += 1
    for name, fn in CASES.items():
        probs = mutated(fn)
        status = "rejected" if probs else "NOT REJECTED"
        if not probs:
            bad += 1
        print(f"{status:13} {name}")
    print(f"mutation tests: {len(CASES) - bad + (1 if clean else 0)}/{len(CASES)} ok" if not bad else f"{bad} FAILURES")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
