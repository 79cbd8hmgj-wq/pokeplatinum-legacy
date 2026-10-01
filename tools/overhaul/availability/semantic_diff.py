#!/usr/bin/env python3
"""Semantic diff: live res/field/encounters/*.json  vs  base commit + manifests (for the selected bands).

  semantic_diff.py --bands E0,E1     maps in those bands must equal the manifest target; all other maps must equal base
  semantic_diff.py --bands all       full manifest must be applied
Also audits that nothing outside the allowed scope changed (git diff against the pinned base commit).
Exit status non-zero on any discrepancy.
"""
from __future__ import annotations

import argparse
import copy
import subprocess
import sys

from common import BANDS, BASE_COMMIT, ROOT
from state import apply_special, apply_wild, base_state, live_state, load_manifest
from zone_index import zone_index

ALLOWED_PREFIXES = ("res/field/encounters/", "docs/overhaul/", "tools/overhaul/", ".github/")


def diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: key missing")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} != {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += diff(x, y, f"{path}[{i}]")
    elif a != b:
        out.append(f"{path}: expected {a!r}, live {b!r}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", default="land,water,special", help="subset of land,water,special")
    ap.add_argument("--bands", default="all")
    args = ap.parse_args()
    bands = set(BANDS) if args.bands == "all" else set(args.bands.split(","))
    wild, special = load_manifest("wild_encounters.json"), load_manifest("special_systems.json")
    zidx = zone_index(wild)
    selected = {n for n, z in zidx.items() if z["band"] in bands}
    expect = base_state()
    groups = set(args.groups.split(","))
    wg = sorted(groups & {"land", "water"})
    if wg:
        apply_wild(expect, wild, check=True, only_maps=selected, only_groups=wg)
    if "special" in groups:
        apply_special(expect, special, check=True, only_maps=selected)
    live = live_state()
    problems = []
    for name in sorted(expect):
        d = diff(expect[name], live[name])
        if d:
            problems += [f"{name}{x}" for x in d[:6]] + ([f"{name}: ... {len(d) - 6} more"] if len(d) > 6 else [])
    changed_maps = sum(1 for n in expect if expect[n] != base_state_cache(n))
    # scope audit
    names = subprocess.run(["git", "diff", "--name-only", BASE_COMMIT], cwd=ROOT, capture_output=True, text=True).stdout.split()
    names += subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    outside = sorted(n for n in set(names) if not n.startswith(ALLOWED_PREFIXES))
    print(f"bands={sorted(bands, key=BANDS.index)}: {len(selected)} maps in scope, {changed_maps} encounter files expected to differ from base")
    if outside:
        problems += [f"file changed outside allowed scope: {n}" for n in outside]
    for p in problems:
        print("DIFF", p)
    print(f"RESULT: {len(problems)} discrepancy(ies)")
    return 1 if problems else 0


_BASE = None


def base_state_cache(n):
    global _BASE
    if _BASE is None:
        _BASE = base_state()
    return _BASE[n]


if __name__ == "__main__":
    sys.exit(main())
