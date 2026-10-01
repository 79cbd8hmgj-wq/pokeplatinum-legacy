#!/usr/bin/env python3
"""Scope audit for the special-acquisition pass: only the listed files may differ from the merged availability baseline.

  special_scope_audit.py [--base f89dfc79]
Fails if species/move/trainer/TM/evolution data, the landed ordinary encounter files, or the 184-family wild manifest changed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from common import ROOT

ALLOWED_EXACT = {
    "generated/vars_flags.txt", "src/underground/mining.c", "src/overlay006/feebas_fishing.c",
    "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s", "res/field/scripts/scripts_celestic_town_southwest_house.s",
    "res/field/scripts/scripts_veilstone_city.s", "res/field/scripts/scripts_route_209.s",
    "res/field/scripts/scripts_old_chateau_back_middle_west_room.s",
    "res/text/sandgem_town_pokemon_research_lab.json", "res/text/celestic_town_southwest_house.json",
    "res/text/veilstone_city.json", "res/text/route_209.json", "res/text/old_chateau_back_middle_west_room.json",
    "docs/overhaul/implementation/availability_families.json", "docs/overhaul/implementation/special_systems.json",
    "docs/overhaul/implementation/special_acquisitions.json", "docs/overhaul/STATUS.md",
}
ALLOWED_PREFIX = ("tools/overhaul/availability/", "docs/overhaul/implementation/SPECIAL_ACQUISITION", "docs/overhaul/implementation/AVAILABILITY_")
MUST_BE_UNCHANGED = ("res/pokemon/", "res/moves/", "res/trainers/", "res/field/encounters/", "res/items/",
                     "docs/overhaul/implementation/wild_encounters.json", "docs/overhaul/implementation/encounter_zones.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="f89dfc79")
    args = ap.parse_args()
    names = subprocess.run(["git", "diff", "--name-only", args.base], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    names += subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    bad = []
    for n in sorted(set(names)):
        if n.startswith(MUST_BE_UNCHANGED):
            bad.append(f"{n}: protected data changed")
        elif n not in ALLOWED_EXACT and not n.startswith(ALLOWED_PREFIX):
            bad.append(f"{n}: outside the special-acquisition scope")
    print(f"{len(set(names))} changed/new files vs {args.base}")
    for b in bad:
        print("SCOPE", b)
    print(f"RESULT: {len(bad)} scope violation(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
