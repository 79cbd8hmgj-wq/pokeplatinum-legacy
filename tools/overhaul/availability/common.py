"""Shared loaders for the availability implementation tooling.

Everything here reads live repository source (species table, evolution data,
encounter JSON) so manifests are derived from, and validated against, current files.
"""
from __future__ import annotations

import glob
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENC_DIR = ROOT / "res" / "field" / "encounters"
IMPL_DIR = Path(os.environ["AVAIL_IMPL_DIR"]) if os.environ.get("AVAIL_IMPL_DIR") else ROOT / "docs" / "overhaul" / "implementation"
ARCH_DOC = ROOT / "docs" / "overhaul" / "AVAILABILITY_ARCHITECTURE.md"

# Pinned implementation base (current main when the availability work started).
BASE_COMMIT = "cb420c0d"

BANDS = ["E0", "E1", "M1", "M2", "L1", "L2", "P0", "P1"]
PRE_E4_BANDS = BANDS[:7]
ZONES = ["START", "ORE", "FOREST", "CYCLE", "HEARTH", "MARSH", "CORONET", "IRON",
         "COAST", "SNOW", "DRY", "EAST", "DEEP", "POST"]

# Fixed slot probabilities from src/overlay006/wild_encounters.c
LAND_RATES = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]      # GetGroundEncounterSlot
SURF_RATES = [60, 30, 5, 4, 1]                              # GetWaterEncounterSlot
OLD_ROD_RATES = [60, 30, 5, 4, 1]                           # GetRodEncounterSlot
GOOD_ROD_RATES = [40, 40, 15, 4, 1]
SUPER_ROD_RATES = [40, 40, 15, 4, 1]
WATER_RATES = {"surf": SURF_RATES, "old_rod": OLD_ROD_RATES,
               "good_rod": GOOD_ROD_RATES, "super_rod": SUPER_ROD_RATES}
REQUIRED_MIN_RATE = 5

# Land-slot roles (see WildEncounters_TryWildEncounter):
#  0,1  replaced by swarm species on the active swarm map
#  2,3  morning default; replaced by day / night species
#  6,7  replaced by Trophy Garden dailies / Great Marsh Safari dailies
#  8,9  replaced by dual-slot (GBA cartridge) species
SLOT_ROLES = {0: "swarm", 1: "swarm", 2: "time", 3: "time", 4: "fixed", 5: "fixed",
              6: "garden_marsh", 7: "garden_marsh", 8: "dual_slot", 9: "dual_slot",
              10: "fixed", 11: "fixed"}


def species_list() -> list[str]:
    return [l.strip() for l in (ROOT / "generated" / "species.txt").read_text().splitlines()]


SPECIES = species_list()
SPECIES_ID = {n: i for i, n in enumerate(SPECIES)}


def dex(name: str) -> int:
    return SPECIES_ID[name]


LEGENDARY_DEX = set([144, 145, 146, 150, 151, 243, 244, 245, 249, 250, 251,
                     377, 378, 379, 380, 381, 382, 383, 384, 385, 386] + list(range(480, 494)))


def pokemon_dir_for(const: str) -> Path | None:
    # res/pokemon/<lower name>; a few species differ, so match by constant lookup.
    p = ROOT / "res" / "pokemon" / const[len("SPECIES_"):].lower()
    return p if p.exists() else None


def evolution_edges() -> list[tuple[str, str, list]]:
    """(from_species, to_species, raw_evolution_entry) for every evolution row in source."""
    edges = []
    for f in sorted(glob.glob(str(ROOT / "res" / "pokemon" / "*" / "data.json"))):
        name = "SPECIES_" + Path(f).parent.name.upper()
        data = json.load(open(f))
        for entry in data.get("evolutions", []):
            edges.append((name, entry[-1], entry))
    return edges


def encounter_files() -> list[Path]:
    return sorted(ENC_DIR.glob("encounters_*.json"))


def map_name(path: Path) -> str:
    return path.name[len("encounters_"):-len(".json")]


def load_encounter(name: str) -> dict:
    return json.load(open(ENC_DIR / f"encounters_{name}.json"))


def dump_encounter(data: dict) -> str:
    # repository files use 4-space indent, no trailing newline
    return json.dumps(data, indent=4, ensure_ascii=False)
