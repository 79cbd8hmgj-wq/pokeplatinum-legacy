#!/usr/bin/env python3
"""Static validation for AV1 (animated battle presentation batch).

Checks, without building:
  * every AV1 move script loads/unloads the same particle systems and only
    creates emitters on loaded systems, with emitter indices < the .spa emitter
    count (SPL header, low 16 bits of the word at offset 8);
  * move data.json files are untouched relative to git HEAD (no balance edits);
  * UI NANR JSON is internally consistent (frame/result counts, result ids,
    cell indices) and sequence counts match the retail contract;
  * the UI generator output is current.
"""

import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOVES = ["ember", "fire_spin", "thunder_shock", "spark", "psybeam", "swift"]
PARTICLES = ROOT / "res/graphics/battle/particles"
errors = []


def err(msg):
    errors.append(msg)


def spa_emitters(name):
    d = (PARTICLES / f"{name}.spa").read_bytes()
    if d[:4] != b" APS":
        err(f"{name}.spa: bad magic")
        return 0
    return struct.unpack_from("<H", d, 8)[0]


def check_move(move):
    path = ROOT / f"res/moves/{move}/anim.s"
    text = path.read_text()
    loaded, unloaded, spa_of = set(), set(), {}
    for m in re.finditer(r"LoadParticleResource\s+(\d+),\s*(\w+)_spa", text):
        loaded.add(int(m.group(1)))
        spa_of[int(m.group(1))] = m.group(2)
    for m in re.finditer(r"UnloadParticleSystem\s+(\d+)", text):
        unloaded.add(int(m.group(1)))
    if loaded != unloaded:
        err(f"{move}: loaded systems {sorted(loaded)} != unloaded {sorted(unloaded)}")
    if len(loaded) < 1:
        err(f"{move}: no particle systems")
    for m in re.finditer(r"CreateEmitter\s+(\d+),\s*(\d+),", text):
        sysid, em = int(m.group(1)), int(m.group(2))
        if sysid not in loaded:
            err(f"{move}: emitter on unloaded system {sysid}")
            continue
        n = spa_emitters(spa_of[sysid])
        if em >= n:
            err(f"{move}: emitter {em} >= {n} in {spa_of[sysid]}.spa")
    if len(re.findall(r"BeginLoop", text)) != len(re.findall(r"EndLoop", text)):
        err(f"{move}: unbalanced loops")
    if text.count("    End\n") + text.count("    End") < 1:
        err(f"{move}: missing End")
    # data.json untouched
    diff = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", f"res/moves/{move}/data.json"],
                          cwd=ROOT).returncode
    if diff not in (0, 128, 1):
        err(f"{move}: data.json diff check failed")
    if diff == 1:
        err(f"{move}: data.json modified (AV1 must not change move properties)")


def check_nanr(path, expect_seq, cell_json):
    d = json.loads((ROOT / path).read_text())
    cells = json.loads((ROOT / cell_json).read_text())["cellCount"]
    if d["sequenceCount"] != expect_seq or len(d["sequences"]) != expect_seq:
        err(f"{path}: sequence count != {expect_seq}")
    total = 0
    for s in d["sequences"]:
        if s["frameCount"] != len(s["frameData"]):
            err(f"{path}: frameCount mismatch")
        if not 0 <= s["loopStartFrame"] < s["frameCount"]:
            err(f"{path}: loopStartFrame out of range")
        total += s["frameCount"]
        for f in s["frameData"]:
            if not 0 <= f["resultId"] < len(d["animationResults"]):
                err(f"{path}: resultId out of range")
            if not 0 <= f["frameDelay"] <= 255:
                err(f"{path}: delay out of range")
    if d["frameCount"] != total:
        err(f"{path}: header frameCount {d['frameCount']} != {total}")
    if d["resultCount"] != len(d["animationResults"]):
        err(f"{path}: resultCount mismatch")
    for r in d["animationResults"]:
        if r["index"] >= cells:
            err(f"{path}: cell index {r['index']} >= {cells}")
        if r["resultType"] == 2 and not (abs(r["positionX"]) <= 8 and abs(r["positionY"]) <= 8):
            err(f"{path}: translation too large")


for mv in MOVES:
    check_move(mv)
check_nanr("res/graphics/battle/interface/cursor_anim.json", 4, "res/graphics/battle/interface/cursor_cell.json")
check_nanr("res/graphics/battle/healthbox/arrows_wide_anim.json", 1, "res/graphics/battle/healthbox/arrows_wide_cell.json")
if subprocess.run([sys.executable, str(ROOT / "tools/visual_overhaul/generate_av1_battle_ui_anim.py"), "--check"]).returncode:
    err("UI generator output is stale")

if errors:
    print("\n".join("FAIL: " + e for e in errors))
    sys.exit(1)
print(f"AV1 static validation OK ({len(MOVES)} moves, 2 UI animations)")
