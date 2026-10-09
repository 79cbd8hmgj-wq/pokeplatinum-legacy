#!/usr/bin/env python3
"""Validate a provenance-first IO-FOL-SHEETS pilot against frozen repository evidence.

No species identity inference, donor extraction, graphics conversion, or Platinum integration.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
manifest = json.loads((ROOT / "docs/visual_overhaul/implementation/io_fol_sheets_pilot_manifest.json").read_text())
evidence = json.loads((ROOT / manifest["evidence"]).read_text())
assert manifest["feature"] == "IO-FOL-SHEETS"
assert manifest["scope"] == "library_only_no_following_mechanic"
assert manifest["species_identity"] == "unverified_do_not_infer_from_filename"
assert evidence["sheets"] == 572 and evidence["size_32"] == 538 and evidence["size_64"] == 34
assert evidence["frames_per_sheet"] == manifest["expected_frames_per_sheet"] == 8
assert evidence["shiny_palette_differs"] == 572
rows = {r["file"]: r for r in evidence["rows"]}
assert len(rows) == evidence["sheets"]
seen = set()
for entry in manifest["pilot"]:
    name = entry["source_file"]
    assert name not in seen, f"duplicate donor: {name}"
    seen.add(name)
    assert name in rows, f"donor absent from evidence: {name}"
    row = rows[name]
    assert row["size"] == entry["expected_size"], f"dimension mismatch: {name}"
    assert row["palettes"] == manifest["expected_palette_variants"] == 2, name
    assert row["frames"] == 8 and row["distinct_frames"] >= 1, name
    assert row["shiny_differs"], name
    assert len(row["tex_names"]) == 8, name
assert len(seen) == 6
print("PASS: six distinct evidence-backed sheets, 8 frames and 2 palettes each")
print("NOTE: this proves catalog metadata only; it does not prove species identity, raw donor files, converter output or runtime compatibility")
