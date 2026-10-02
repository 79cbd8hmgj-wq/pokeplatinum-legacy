#!/usr/bin/env python3
"""Validate live source against the locked C1 82-edit manifest (and surrounding invariants).

Exit status is non-zero on any problem. `validate(live, ctx)` is pure so mutation tests can corrupt copies.
"""
from __future__ import annotations

import copy
import re
import sys

from c1_lib import *

HM_NAMES = ["Cut", "Fly", "Surf", "Strength", "Defog", "Rock Smash", "Waterfall", "Rock Climb", "Whirlpool"]
HM_C1_EDITED = {"Whirlpool"}  # only HM touched by C1; no later C2 override recorded for it
C1_SCRIPT = "res/moves/razor_wind/script.s"


def load_ctx() -> dict:
    ctx = {"manifest": load_json(MANIFEST), "guards": load_json(GUARDS), "base": base_moves()}
    ctx["moves_txt"] = open(os.path.join(ROOT, "generated/moves.txt")).read().split()
    ctx["battle_lib"] = open(os.path.join(ROOT, "src/battle/battle_lib.c")).read()
    ctx["razor_script"] = open(os.path.join(ROOT, C1_SCRIPT)).read()
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
    allowed = {}  # move -> {field: after}
    for e in edits:
        rec = live.get(e["move"], [])
        if len(rec) != 1:
            P.append(f"{e['move']}: live record count {len(rec)}")
            continue
        d = rec[0][1]
        cur = read_fields(d)
        allowed[e["move"]] = e["target"]
        for k, v in e["target"].items():
            if cur[k] != v:
                P.append(f"{e['move']}: {k} live {cur[k]!r} != locked {v!r}")
    # semantic diff of every move against pinned base: only manifest fields may differ
    for name, recs in base.items():
        if name not in live or len(live[name]) != len(recs):
            P.append(f"{name}: record missing/duplicated vs base")
            continue
        b, l = recs[0][1], live[name][0][1]
        tgt = allowed.get(name, {})
        for k in sorted(set(b) | set(l)):
            if k in FIELDS:
                if l.get(k) != (tgt.get(k, b.get(k))):
                    P.append(f"{name}: unexpected {k} {b.get(k)!r}->{l.get(k)!r}")
            elif k == "effect":
                exp_type = tgt.get("effect_type", b["effect"]["type"])
                if l["effect"]["type"] != exp_type:
                    P.append(f"{name}: unexpected effect type {b['effect']['type']}->{l['effect']['type']}")
                if l["effect"].get("chance") != b["effect"].get("chance"):
                    P.append(f"{name}: effect chance changed")
            elif k == "description" and name == "Razor Wind":
                if l[k] != RAZOR_WIND_DESC or any("two-turn" in x.lower() or "second" in x.lower() for x in l[k]):
                    P.append("Razor Wind: description not updated")
            elif l.get(k) != b.get(k):
                P.append(f"{name}: unexpected {k} change")
    for name in live:
        if name not in base:
            P.append(f"{name}: not in base (new move)")
    # Razor Wind behavior plumbing: single-turn, no charge message
    if "BufferMessage" in ctx["razor_script"]:
        P.append("Razor Wind script still contains charge-turn message")
    # KEEP invariants
    for name, vals in g["keep_invariants"].items():
        rec = live.get(name)
        if not rec or read_fields(rec[0][1]) != vals:
            P.append(f"KEEP violated: {name}")
    if "Magma Storm" in live:
        d = live["Magma Storm"][0][1]
        if (d["power"], d["accuracy"], d["pp"]) != (120, 70, 5):
            P.append("Magma Storm KEEP 120/70/5 violated")
    # HM / later-pass safeguard: HMs other than manifest-listed must equal base
    for h in HM_NAMES:
        if h in HM_C1_EDITED:
            continue
        if h in live and read_fields(live[h][0][1]) != read_fields(base[h][0][1]):
            P.append(f"HM {h} changed")
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
    if sum(1 for n in base if base[n][0][0].startswith("res/moves/") and n in live) != len(base):
        P.append("move records missing")
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
