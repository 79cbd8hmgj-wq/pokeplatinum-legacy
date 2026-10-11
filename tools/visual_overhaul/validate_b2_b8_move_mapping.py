#!/usr/bin/env python3
"""Validate B2–B8 cinematic archetype mapping against actual Platinum move scripts.

Source-only validation. Does not claim that a proposed effect has been imported,
is VRAM-safe, or behaves correctly at runtime.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "docs/visual_overhaul/B2_B8_MOVE_ARCHETYPE_MAPPING.json"
KNOWN = {
    "projectile", "beam", "explosion", "area_surge", "melee",
    "multihit", "weather", "status", "psychic", "ground", "natural_force",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="Optional JSON inventory of actual script branch features")
    args = parser.parse_args()
    data = json.loads(MAP.read_text())
    assignments = data["assignments"]
    assert len(assignments) >= 50, "Expected broad archetype coverage"
    seen = set()
    report = {}
    for entry in assignments:
        name, kind = entry["move"], entry["archetype"]
        assert kind in KNOWN, f"Unknown archetype: {kind}"
        assert re.fullmatch(r"[a-z0-9_]+", name), f"Unexpected move name: {name}"
        pair = (name, kind)
        assert pair not in seen, f"Duplicate move/archetype: {pair}"
        seen.add(pair)
        relative = f"res/moves/{name}/anim.s"
        assert entry["script"] == relative, f"Path mismatch for {name}"
        file = ROOT / relative
        assert file.is_file(), f"Missing move script: {relative}"
        text = file.read_text()
        assert '#include "macros/btlanimcmd.inc"' in text, relative
        assert re.search(r"(?m)^\s*End\b", text), f"No End in {relative}"
        flags = {
            "contest_branch": "JumpIfContest" in text,
            "friendly_fire_branch": "JumpIfFriendlyFire" in text,
            "battler_side_branch": "JumpIfBattlerSide" in text,
            "other_branches": bool(re.search(r"\bJumpIf(?!Contest|FriendlyFire|BattlerSide)\w*", text)),
            "loads_particle_resource": "LoadParticleResource" in text,
            "sprite_manager_operations": ("InitSpriteManager" in text or "AddSprite" in text),
        }
        if name not in report:
            report[name] = {"script": relative, "archetypes": [], "source_branch_features": flags}
        report[name]["archetypes"].append(kind)
    assert len(report) >= 45, "Too few unique scripts"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"move_count": len(report), "scripts": report}, indent=2) + "\n")
    counts = {k: sum(v["source_branch_features"][k] for v in report.values()) for k in next(iter(report.values()))["source_branch_features"]}
    print(f"PASS: {len(assignments)} assignments, {len(report)} source scripts, branch feature counts: {counts}")
    print("PASS means source path integrity ONLY; timing/VRAM/run-time and candidate imports are not verified.")

if __name__ == "__main__":
    main()
