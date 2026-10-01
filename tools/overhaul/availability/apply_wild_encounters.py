#!/usr/bin/env python3
"""Apply wild_encounters.json + special_systems.json to res/field/encounters/*.json with before-value guards.

  apply_wild_encounters.py --bands E0,E1            apply only maps whose zone band is listed
  apply_wild_encounters.py --bands all --dry-run    show what would change
Fails closed: any slot whose live value is neither the manifest 'before' nor 'after' aborts the run untouched.
Idempotent: re-running after a successful apply changes nothing.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys

from base_source import base_trailing_newline
from common import BANDS, ENC_DIR, dump_encounter
from state import GuardError, apply_special, apply_wild, live_state, load_manifest
from zone_index import zone_index


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", default="land,water,special", help="subset of land,water,special")
    ap.add_argument("--bands", default="all", help="comma list of bands, or 'all'")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    bands = set(BANDS) if args.bands == "all" else set(args.bands.split(","))
    if not bands <= set(BANDS):
        print("unknown band in", bands, file=sys.stderr)
        return 2
    wild, special = load_manifest("wild_encounters.json"), load_manifest("special_systems.json")
    zidx = zone_index(wild)
    selected = {n for n, z in zidx.items() if z["band"] in bands}
    # dual-slot / radar / swarm / honey / garden / marsh arrays belong to whichever map file holds them
    before = live_state()
    after = copy.deepcopy(before)
    try:
        groups = set(args.groups.split(","))
        wg = sorted(groups & {"land", "water"})
        n_wild = apply_wild(after, wild, check=True, only_maps=selected, only_groups=wg) if wg else 0
        n_spec = apply_special(after, special, check=True, only_maps=selected) if "special" in groups else 0
    except GuardError as e:
        print(f"GUARD FAILURE (nothing written): {e}", file=sys.stderr)
        return 1
    changed = [n for n in after if after[n] != before[n]]
    print(f"groups={args.groups} bands={sorted(bands, key=BANDS.index)} maps selected={len(selected)} wild entries={n_wild} "
          f"special arrays={n_spec} files changed={len(changed)}")
    if args.dry_run:
        for n in changed:
            print("  would change", n)
        return 0
    for n in changed:
        text = dump_encounter(after[n]) + ("\n" if base_trailing_newline(n) else "")
        (ENC_DIR / f"encounters_{n}.json").write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
