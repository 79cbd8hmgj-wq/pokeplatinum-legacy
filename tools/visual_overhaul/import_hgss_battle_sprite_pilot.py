#!/usr/bin/env python3

"""Stage a small HGSS battle-sprite runtime pilot into Platinum.

Only views that already passed BOTH G3 safety gates are eligible:
- frame geometry: geometry-close
- palette/index contract: direct-index-safe

Platinum's normal/shiny palettes and sprite_data.json animation metadata are never
modified by this importer. The pilot is deliberately representative rather than exhaustive.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLATINUM_POKEMON = ROOT / "res" / "pokemon"

DEFAULT_PILOT = (
    "SPECIES_VENUSAUR",   # large/wide front silhouette
    "SPECIES_DITTO",      # very small/simple silhouette
    "SPECIES_GROWLITHE",  # quadruped
    "SPECIES_LAPRAS",     # large asymmetric silhouette
    "SPECIES_PSYDUCK",    # medium humanoid/round silhouette
    "SPECIES_TYRANITAR",  # tall/heavy silhouette
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-root", required=True, type=Path)
    parser.add_argument("--compatibility-manifest", required=True, type=Path)
    parser.add_argument(
        "--species",
        nargs="*",
        default=list(DEFAULT_PILOT),
        help="Species constants to stage. Defaults to the representative G3 pilot.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def target_path(species: str, view: str) -> Path:
    dirname = species.removeprefix("SPECIES_").lower()
    return PLATINUM_POKEMON / dirname / view


def main() -> None:
    args = parse_args()
    manifest = json.loads(args.compatibility_manifest.read_text())
    requested = set(args.species)

    allowed_species = set(manifest["direct_index_safe_species"])
    invalid = sorted(requested - allowed_species)
    if invalid:
        raise SystemExit(
            "Refusing unsafe pilot species not classified direct-index-safe: "
            + ", ".join(invalid)
        )

    selected = [
        entry
        for entry in manifest["entries"]
        if entry["species"] in requested
        and entry["status"] == "direct-index-safe"
    ]
    if not selected:
        raise SystemExit("No eligible donor views selected.")

    touched_species: set[str] = set()
    copied = 0
    for entry in selected:
        donor = args.donor_root / entry["donor_path"]
        target = target_path(entry["species"], entry["view"])
        if not donor.exists():
            raise SystemExit(f"Missing donor: {donor}")
        if not target.exists():
            raise SystemExit(f"Missing Platinum target: {target}")

        print(f"{entry['species']}: {entry['view']} <- {entry['donor_path']}")
        if not args.dry_run:
            shutil.copyfile(donor, target)
        touched_species.add(entry["species"])
        copied += 1

    # Guardrail: importer is intentionally sprite-art-only.
    forbidden = []
    for species in touched_species:
        dirname = species.removeprefix("SPECIES_").lower()
        for name in ("normal.pal", "shiny.pal", "sprite_data.json", "data.json"):
            path = PLATINUM_POKEMON / dirname / name
            if not path.exists():
                forbidden.append(str(path))
    if forbidden:
        raise SystemExit("Expected preserved Platinum contract files missing: " + ", ".join(forbidden))

    print(
        f"{'Would stage' if args.dry_run else 'Staged'} {copied} safe HGSS sprite views "
        f"across {len(touched_species)} species."
    )


if __name__ == "__main__":
    main()
