#!/usr/bin/env python3
"""Validate B2-B8 planning handoff against committed donor provenance.

No external downloads, emulator or ARM toolchain required.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
manifest = json.loads((root / "docs/visual_overhaul/B2_B8_PREIMPLEMENTATION_MANIFEST.json").read_text())
assert manifest["schema"] == "opal.b2_b8.preimplementation.v1"
assert {phase["id"] for phase in manifest["phases"]} == {f"B{i}" for i in range(2, 9)}
assert len({asset["resource"] for asset in manifest["verified_installed"]}) == 3
assert len({arch["id"] for arch in manifest["archetypes"]}) == 6
for asset in manifest["verified_installed"]:
    p = root / asset["provenance"]
    recipe = root / asset["recipe"]
    assert p.is_file() and recipe.is_file(), asset["resource"]
    record = json.loads(p.read_text())
    rec = json.loads(recipe.read_text())
    assert record["name"] == asset["resource"] == rec["name"]
    assert record["obj_tiles"] == asset["obj_tiles"] <= 256
    assert len(record["frames"]) == asset["frames"] == len(rec["frames"])
    assert record["donor_package"].startswith(asset["package"])
    assert record["donor"] == rec["donor"] == asset["source"]
    assert all(len(frame["cell_sha256"]) == 64 for frame in record["frames"])
assert all("status" in item and item["status"] != "installed" for item in manifest["candidate_priorities"])
print("PASS: B2-B8 handoff matches committed donor recipes, provenance and phase scope")
