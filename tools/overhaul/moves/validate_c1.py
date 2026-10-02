#!/usr/bin/env python3
"""Validate live source against the locked C1 82-edit manifest (and surrounding invariants).

Exit status is non-zero on any problem. `validate(live, ctx)` is pure so mutation tests can corrupt copies.
"""
from __future__ import annotations

import copy
import re
import sys

from c1_lib import *

C1_SCRIPT = "res/moves/razor_wind/script.s"
C1_ANIM = "res/moves/razor_wind/anim.s"


def load_ctx() -> dict:
    ctx = {"manifest": load_json(MANIFEST), "guards": load_json(GUARDS), "base": base_moves()}
    ctx["moves_txt"] = open(os.path.join(ROOT, "generated/moves.txt")).read().split()
    ctx["battle_lib"] = open(os.path.join(ROOT, "src/battle/battle_lib.c")).read()
    ctx["razor_script"] = open(os.path.join(ROOT, C1_SCRIPT)).read()
    ctx["razor_anim"] = open(os.path.join(ROOT, C1_ANIM)).read()
    ctx["created_dirs"] = None
    return ctx


def strip(d: dict) -> dict:
    return copy.deepcopy(d)


def validate(live: dict, ctx: dict) -> list[str]:
    P: list[str] = []
    man, g, base = ctx["manifest"], ctx["guards"], ctx["base"]
    edits = man["edits"]
    if len(edits) != 82 or man["expected_edit_count"] != 82 or g["edit_count"] != 82 or len(g["edits"]) != 82:
        P.append("edit count != 82")
    if len({e["move"] for e in edits}) != 82:
        P.append("duplicate manifest moves")
    if [(e["move"], e["target"]) for e in edits] != [(e["move"], e["after"]) for e in g["edits"]]:
        P.append("guards disagree with manifest")
    # Permanent C1 validation is intentionally scoped to the 82 C1-owned move records.
    # Later passes may legitimately change unrelated moves (including the actual Platinum HMs).
    # Within a C1-edited record, fields not owned by C1 remain pinned unless a later-pass
    # override is explicitly recorded in the guard schema.
    for e in edits:
        rec = live.get(e["move"], [])
        if len(rec) != 1:
            P.append(f"{e['move']}: live record count {len(rec)}")
            continue
        _, d = rec[0]
        _, b = unique(base, e["move"])
        cur = read_fields(d)
        for k, v in e["target"].items():
            if cur[k] != v:
                P.append(f"{e['move']}: {k} live {cur[k]!r} != locked {v!r}")
        for k in sorted(set(b) | set(d)):
            if k in FIELDS:
                exp = e["target"].get(k, b.get(k))
                if d.get(k) != exp:
                    P.append(f"{e['move']}: unexpected {k} {b.get(k)!r}->{d.get(k)!r}")
            elif k == "effect":
                exp_type = e["target"].get("effect_type", b["effect"]["type"])
                if d["effect"]["type"] != exp_type:
                    P.append(f"{e['move']}: unexpected effect type {b['effect']['type']}->{d['effect']['type']}")
                if d["effect"].get("chance") != b["effect"].get("chance"):
                    P.append(f"{e['move']}: effect chance changed")
            elif k == "description" and e["move"] == "Razor Wind":
                if d[k] != RAZOR_WIND_DESC or any("two-turn" in x.lower() or "second" in x.lower() for x in d[k]):
                    P.append("Razor Wind: description not updated")
            elif d.get(k) != b.get(k):
                P.append(f"{e['move']}: unexpected {k} change")
    # Razor Wind behavior plumbing: single-turn, no charge message or charge animation branch.
    if "BufferMessage" in ctx["razor_script"] or "PokemonWhippedUpAWhirlwind" in ctx["razor_script"]:
        P.append("Razor Wind script still contains charge-turn message")
    if "JumpIfEffectChanceOdd" in ctx["razor_anim"] or "EMITTER_CB_SET_POS_TO_ATTACKER" in ctx["razor_anim"]:
        P.append("Razor Wind animation still contains charge-turn branch")
    if "CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER_SIDE" not in ctx["razor_anim"]:
        P.append("Razor Wind strike animation missing")
    # KEEP invariants
    for name, vals in g["keep_invariants"].items():
        rec = live.get(name)
        if not rec or read_fields(rec[0][1]) != vals:
            P.append(f"KEEP violated: {name}")
    if "Magma Storm" in live:
        d = live["Magma Storm"][0][1]
        if (d["power"], d["accuracy"], d["pp"]) != (120, 70, 5):
            P.append("Magma Storm KEEP 120/70/5 violated")
    # created moves
    mt = ctx["moves_txt"]
    if len(mt) != 491 or mt[-1] != "MAX_MOVES" or mt[468] != "MOVE_STATIC_STRIKE" or mt[489] != "MOVE_STAR_JAB":
        P.append("move id allocation / MAX_MOVES damaged")
    for const in ("MOVE_RESONANT_SLASH", "MOVE_STAR_JAB"):
        if const not in ctx["battle_lib"]:
            P.append(f"{const} registry missing")
    mv = live.get("Magnet Volley")
    if not mv:
        P.append("Magnet Volley missing")
    else:
        d = mv[0][1]
        if (d["power"], d["effect"]["type"]) != (25, "BATTLE_EFFECT_HIT_THREE_TIMES_EQUAL_POWER"):
            P.append("Magnet Volley not exactly 3x25 equal-power")
    return P


def main() -> int:
    ctx = load_ctx()
    problems = validate(live_moves(), ctx)
    for p in problems:
        print("FAIL:", p)
    print(f"C1 validation: {'FAIL' if problems else 'OK'} ({len(problems)} problems, 82 edits)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
