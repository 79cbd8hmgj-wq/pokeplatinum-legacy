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
TARGETS = {
    "e002": ("thunderbolt", "effect component or timing donor"),
    "e009": ("shadow_ball", "effect component or timing donor"),
    "e010": ("flamethrower", "effect component or timing donor"),
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
        host, treatment = TARGETS[suffix]
        entries[suffix] = {
            "source_unit": unit,
            "host": f"res/moves/{host}/anim.s",
            "intent": treatment,
            "source_members": sorted(set(identity.get("sample_paths") or [])),
            "source_member_count": identity.get("member_count"),
            "source_digest": identity.get("member_digest"),
            "curation": (record.get("curation_trace") or {}).get("status"),
            "decision": record.get("role"),
            "format_family": record.get("format_family"),
            "conversion_requirement": record.get("conversion_requirement"),
            "needs_decode": record.get("conversion_requirement") in ("not_portable", None),
            "installed_in_rom": False,
            "next_action": "extract actual donor Nitro package; inspect NCGR/NCLR/NCER/NANR; transform to approved native battle resource and validate VRAM",
        }
    assert len(entries) == len(TARGETS), f"Missing donor source units: {set(TARGETS) - set(entries)}"
    for record in entries.values():
        assert record["source_members"] and record["source_digest"]
        assert record["curation"] not in ("decode_issue", "reject")
    return {"authority": str(LEDGER.relative_to(ROOT)),
            "status": "import-preflight-only",
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
