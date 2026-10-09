#!/usr/bin/env python3
"""AV1 animated battle-UI generator.

Rewrites only the NANR animation sequences (never cells, pixels or palettes) of:

  * res/graphics/battle/interface/cursor_anim.json
      Battle command / move / target cursor.  Each of the four corner brackets
      gets a one-shot "lock-on" intro (snap inward from 5px) that plays every
      time the cursor is (re)positioned via ManagedSprite_SetAnim, followed by
      an eased breathing loop (loopStartFrame skips the intro on later loops).
      Sequence order/count and the 16px cell contract are unchanged.
  * res/graphics/battle/healthbox/arrows_wide_anim.json
      Active-battler marker arrow.  Same cell sweep as retail, but the hold
      phase becomes a gentle 2px bob (switches results to cell+translate).

The tool is idempotent: output is derived from constants below, not from the
current content of the files.  Donor inspiration: Ranger 2 styler/cursor
timing (IO-FX-SEQ launch/impact/settle phasing) and HGSS command-cursor snap.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURSOR = ROOT / "res/graphics/battle/interface/cursor_anim.json"
ARROWS = ROOT / "res/graphics/battle/healthbox/arrows_wide_anim.json"


def ser(v, depth):
    if isinstance(v, dict):
        pad = "\t" * (depth + 1)
        items = [f'{pad}"{k}":\t{ser(x, depth + 1)}' for k, x in v.items()]
        return "{\n" + ",\n".join(items) + "\n" + "\t" * depth + "}"
    if isinstance(v, list):
        if v and isinstance(v[0], dict):
            return "[" + ", ".join(ser(i, depth + 1) for i in v) + "]"
        return "[" + ", ".join(ser(i, depth) for i in v) + "]"
    return json.dumps(v)


def dump(doc):
    return ser(doc, 0)


def sequence(frames, loop_start):
    return {
        "frameCount": len(frames),
        "loopStartFrame": loop_start,
        "animationElement": 2,
        "animationType": 1,
        "playbackMode": 2,
        "frameData": [{"frameDelay": d, "resultId": r} for d, r in frames],
    }


def build_cursor(base):
    # Corner direction (sign of outward X/Y) per sequence, matching retail.
    signs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    mags = [0, 1, 2, 3, 4, 5]  # px outward; result index = mag
    # (delay, magnitude): intro snap-in, then eased breathing loop.
    intro = [(1, 5), (2, 3), (2, 1)]
    loop = [(7, 0), (4, 1), (7, 2), (4, 1)]
    seqs, results = [], []
    for cell, (sx, sy) in enumerate(signs):
        res_base = len(results)
        for m in mags:
            results.append({"resultType": 2, "index": cell,
                            "positionX": sx * m, "positionY": sy * m})
        seqs.append(sequence([(d, res_base + m) for d, m in intro + loop], len(intro)))
    base["sequenceCount"] = 4
    base["frameCount"] = sum(s["frameCount"] for s in seqs)
    base["sequences"] = seqs
    base["animationResults"] = results
    base["resultCount"] = len(results)
    return base


def build_arrows(base):
    # (delay, cell index, y offset). Cell sweep identical to retail; the hold
    # frame (cell 4) becomes a 4-step bob.
    steps = [(0, 0, 0), (4, 1, 0), (4, 2, 0), (4, 3, 0),
             (4, 4, 0), (4, 4, -1), (4, 4, -2), (4, 4, -1), (6, 5, 0)]
    results = [{"resultType": 2, "index": c, "positionX": 0, "positionY": y}
               for _, c, y in steps]
    base["sequences"] = [sequence([(d, i) for i, (d, _, _) in enumerate(steps)], 0)]
    base["frameCount"] = len(steps)
    base["animationResults"] = results
    base["resultCount"] = len(results)
    return base


def main():
    check = "--check" in sys.argv
    ok = True
    for path, fn in ((CURSOR, build_cursor), (ARROWS, build_arrows)):
        doc = json.loads(path.read_text())
        text = dump(fn(doc))
        if check:
            if path.read_text() != text:
                print(f"STALE: {path.relative_to(ROOT)}")
                ok = False
        else:
            path.write_text(text)
            print(f"wrote {path.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
