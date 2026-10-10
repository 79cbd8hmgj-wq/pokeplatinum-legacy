#!/usr/bin/env python3
"""Extract ranked battle-effect donor candidates from Opal's existing selection database.

Source-backed, read-only; does not claim that candidate sprites are ROM-ready.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "docs/visual_overhaul/selection/IMPLEMENTATION_QUEUE.json"
CATALOG = ROOT / "docs/visual_overhaul/DONOR_ASSET_CATALOG.json"
def main():
    queue = json.loads(QUEUE.read_text())
    assert CATALOG.is_file(), "Missing 64,841-asset donor catalog"
    ranked = queue["ranked"]
    candidates = [
        {
            "rank": entry["rank"],
            "source": entry["source_id"],
            "title": entry["title"],
            "host": entry["host"],
            "opportunity_ids": entry.get("top_records", []),
            "library_id": entry.get("library_id"),
            "status": "requires_visual_and_format_selection",
        }
        for entry in ranked
        if entry.get("host", "").startswith("battle move")
        or entry.get("subsystem") in {"battle_effects_particles", "battle_backgrounds_hud"}
    ]
    assert candidates, "No ranked battle donors selected"
    assert any(c["source"] == "ranger2" for c in candidates)
    print(json.dumps({"authority": str(QUEUE.relative_to(ROOT)),
                      "catalog": str(CATALOG.relative_to(ROOT)),
                      "candidate_count": len(candidates),
                      "candidates": candidates}, indent=2))

if __name__ == "__main__":
    main()
