#!/usr/bin/env python3
"""Produce a source-grounded B1 effect-import readiness ledger.

No donor pixels are installed here: each row identifies original data and its
actual conversion gate. Preview contact sheets are not treated as ROM art.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/visual_overhaul/selection/ledgers/battle_effects_particles.json"
# Post-B1 installed resources are authoritative. Historic donor ledgers used
# provisional host guesses before actual conversion and ROM installation.
TARGETS = {
    "e002": ("stone_edge", "ranger_rock_burst"),
    "e009": ("ice_beam", "ranger_ice_bloom"),
    "e010": ("flamethrower", "ranger_fire_bloom"),
}
def make_report():
    data = json.loads(LEDGER.read_text())
    entries = {}
    for record in data["decisions"]:
        identity = record.get("asset_identity") or {}
        unit = identity.get("unit", "")
        suffix = unit.rsplit("/", 1)[-1]
        if suffix not in TARGETS or record.get("source_id") != "ranger2":
            continue
        # Several decisions can represent different classifications of a source.
        if suffix in entries and record.get("role") != "promoted":
            continue
        host, installed_resource = TARGETS[suffix]
        entries[suffix] = {
            "source_unit": unit,
            "host": f"res/moves/{host}/anim.s",
            "intent": "reuse already installed donor resource",
            "installed_resource": installed_resource,
            "provenance": f"docs/visual_overhaul/b1_installed_donors/{installed_resource}.provenance.json",
            "recipe": f"tools/visual_overhaul/b1_recipes/{installed_resource}.json",
            "source_members": sorted(set(identity.get("sample_paths") or [])),
            "source_member_count": identity.get("member_count"),
            "source_digest": identity.get("member_digest"),
            "curation": (record.get("curation_trace") or {}).get("status"),
            "decision": record.get("role"),
            "format_family": record.get("format_family"),
            "conversion_requirement": record.get("conversion_requirement"),
            "historical_classification_needs_conversion": record.get("conversion_requirement") in ("not_portable", None),
            "needs_decode": False,
            "installed_in_rom": True,
            "next_action": "reuse installed B1 sprite and provenance; do not re-extract unless authoring a different asset",
        }
    assert len(entries) == len(TARGETS), f"Missing donor source units: {set(TARGETS) - set(entries)}"
    for record in entries.values():
        assert record["source_members"] and record["source_digest"]
        assert record["curation"] not in ("decode_issue", "reject")
    return {"authority": str(LEDGER.relative_to(ROOT)),
            "status": "reconciled_with_installed_b1_donors",
            "entries": [entries[k] for k in sorted(entries)]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(make_report(), indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    else:
        print(result, end="")

if __name__ == "__main__":
    main()
