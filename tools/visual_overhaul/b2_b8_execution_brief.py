#!/usr/bin/env python3
"""Compact B2–B8 implementation brief and source-backed manifest verification.

No ROM, ARM toolchain, network access, source modification or third-party packages.
Design specifications are not proof of implementation or runtime correctness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REL = "docs/visual_overhaul/B2_B8_IMPLEMENTATION_MANIFEST.json"


def verify(root: Path, data: dict) -> dict:
    failures = []
    phases = data.get("phases", [])
    archetypes = data.get("cinematic_archetypes", [])
    donors = data.get("verified_installed_donors", [])
    candidates = data.get("unverified_candidate_families", [])

    def require(condition: bool, description: str) -> None:
        if not condition:
            failures.append(description)

    require(data.get("schema_version") == "1.0", "unknown manifest schema")
    ids = [item.get("id") for item in phases]
    require(ids == [f"B{i}" for i in range(2, 9)], "phase order must be B2 through B8")
    arch_ids = [item.get("id") for item in archetypes]
    require(len(arch_ids) == len(set(arch_ids)) and len(arch_ids) > 0, "archetypes missing or duplicated")
    donor_ids = [item.get("id") for item in donors]
    require(len(donor_ids) == len(set(donor_ids)) and len(donor_ids) == 3, "B1 imported donors missing or duplicated")

    mapped = set()
    overlaps = {}
    for group in archetypes:
        moves = group.get("moves", [])
        require(bool(moves) and bool(group.get("stages")) and bool(group.get("guards")),
                f"missing design details in {group.get('id')}")
        require(len(moves) == len(set(moves)), f"duplicate moves in {group.get('id')}")
        for move in moves:
            mapped.add(move)
            overlaps.setdefault(move, []).append(group.get("id"))
            script = root / "res/moves" / move / "anim.s"
            require(script.is_file(), f"missing move script: {script.relative_to(root)}")
    for phase in phases:
        require(bool(phase.get("deliverables")) and bool(phase.get("gates")),
                f"missing deliverable/gate in {phase.get('id')}")
        for target in phase.get("source_targets", []):
            require((root / target).exists(), f"missing source target: {target}")

    for donor in donors:
        name = donor["id"]
        p = root / donor["provenance"]
        r = root / donor["recipe"]
        require(p.is_file() and r.is_file(), f"provenance/recipe missing: {name}")
        if not p.is_file() or not r.is_file():
            continue
        try:
            proof = json.loads(p.read_text(encoding="utf-8"))
            recipe = json.loads(r.read_text(encoding="utf-8"))
            require(proof["name"] == recipe["name"] == name, f"identity mismatch: {name}")
            require(proof["obj_tiles"] == donor["obj_tiles"] <= 256, f"OBJ budget mismatch: {name}")
            require(len(proof["frames"]) == donor["frames"] == len(recipe["frames"]),
                    f"frame count mismatch: {name}")
            require(len(proof["palette_colours_rgb555"]) == donor["opaque_colors"],
                    f"palette mismatch: {name}")
            require(proof["donor_package"].startswith(donor["donor_package"]),
                    f"package mismatch: {name}")
            require(donor["status"] == "installed", f"unverified imported donor: {name}")
        except (ValueError, KeyError, TypeError) as exc:
            failures.append(f"unreadable/mismatched donor record: {name}: {exc}")

    for candidate in candidates:
        require(candidate.get("status") != "installed",
                f"unverified candidate falsely marked installed: {candidate.get('family')}")
    require(bool(data.get("source_gate")) and bool(data.get("owner_runtime_cases")),
            "hard source/owner runtime boundaries missing")
    return {
        "valid": not failures,
        "failures": failures,
        "phases": len(phases),
        "cinematic_archetypes": len(archetypes),
        "mapped_move_scripts": len(mapped),
        "installed_donors": donor_ids,
        "overlapping_move_assignments_for_review": {
            move: groups for move, groups in sorted(overlaps.items()) if len(groups) > 1
        },
        "runtime_status": "not tested; owner verification deferred",
    }


def brief(data: dict, phase_id: str, archetype_id: str | None) -> dict:
    phase = next((x for x in data["phases"] if x["id"] == phase_id), None)
    if phase is None:
        raise ValueError(f"Unknown phase {phase_id}")
    items = [x for x in data["cinematic_archetypes"]
             if archetype_id is not None and x["id"] == archetype_id]
    if archetype_id is not None and not items:
        raise ValueError(f"Unknown archetype {archetype_id}")
    if phase_id == "B2" and archetype_id is None:
        targets = {p.split("/")[2] for p in phase["source_targets"] if p.startswith("res/moves/")}
        items = [x for x in data["cinematic_archetypes"] if targets.intersection(x["moves"])]
    return {
        "kind": "source_implementation_brief_not_completion_report",
        "phase": phase_id,
        "deliverables": phase["deliverables"],
        "edit_targets": phase["source_targets"],
        "acceptance_gates": phase["gates"],
        "selected_archetypes": [
            {k: item[k] for k in ("id", "moves", "stages", "guards", "donor_family", "status")}
            for item in items
        ],
        "existing_donors_reuse_not_reextract": [
            {k: d[k] for k in ("id", "recipe", "provenance", "moves")}
            for d in data["verified_installed_donors"]
        ] if phase_id in ("B2", "B8") else [],
        "owner_only_runtime_checks": data["owner_runtime_cases"] if phase_id == "B8" else [],
        "general_guardrails": data["source_gate"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify", action="store_true", help="check manifest against source/installed donors")
    parser.add_argument("--phase", choices=[f"B{i}" for i in range(2, 9)], default="B2")
    parser.add_argument("--archetype", help="optional single cinematic archetype")
    parser.add_argument("--output", type=Path, help="write JSON to file instead of stdout")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    data = json.loads((root / REL).read_text(encoding="utf-8"))
    outcome = verify(root, data) if args.verify else brief(data, args.phase, args.archetype)
    serialized = json.dumps(outcome, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    if args.verify and not outcome["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
