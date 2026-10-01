"""Read encounter data as it existed at the pinned base commit (git object store).

The authoring helpers use this so generated manifests are reproducible even after the
live JSON files have been rewritten by the apply step.
"""
from __future__ import annotations

import json
import subprocess
from functools import lru_cache

from common import BASE_COMMIT, ROOT, encounter_files, map_name


@lru_cache(maxsize=None)
def base_encounter(name: str) -> dict:
    out = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:res/field/encounters/encounters_{name}.json"],
        cwd=ROOT, check=True, capture_output=True, text=True).stdout
    return json.loads(out)


@lru_cache(maxsize=None)
def base_trailing_newline(name: str) -> bool:
    out = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:res/field/encounters/encounters_{name}.json"],
        cwd=ROOT, check=True, capture_output=True, text=True).stdout
    return out.endswith("\n")


def all_base_maps() -> list[str]:
    return [map_name(p) for p in encounter_files()]
