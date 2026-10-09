#!/usr/bin/env python3
"""Validate full IO-FOL-SHEETS inventory; optional export-directory hash validation."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
manifest = json.loads((ROOT / "docs/visual_overhaul/implementation/io_fol_sheets_pilot_manifest.json").read_text())
evidence = json.loads((ROOT / manifest["evidence"]).read_text())
rows = evidence["rows"]
assert manifest["scope"] == "all_572_catalogued_sheets"
assert len(rows) == evidence["sheets"] == manifest["source_count"] == 572
assert len({r["file"] for r in rows}) == 572
assert sum(r["size"] == 32 for r in rows) == 538
assert sum(r["size"] == 64 for r in rows) == 34
assert all(r["frames"] == manifest["frames_per_sheet"] == 8 for r in rows)
assert all(r["palettes"] == manifest["palette_variants"] == 2 for r in rows)
assert all(r["shiny_differs"] for r in rows)
assert all(len(r["tex_names"]) == 8 for r in rows)
assert manifest["expected_exported_pngs"] == 572 * 8 * 2
ident = json.loads((ROOT / "docs/visual_overhaul/implementation/io_fol_sheets_hgss_identity.json").read_text())
assert len(ident["entries"]) == 572
assert {x["donor_filename"] for x in ident["entries"]} == {r["file"] for r in rows}
assert len({x["model_id"] for x in ident["entries"]}) == 572
assert sum(x["kind"] == "reserved_follower_generic" for x in ident["entries"]) == 6
assert sum(x["kind"] == "named_species_or_form" for x in ident["entries"]) == 566
assert all(x["source_symbol"] for x in ident["entries"])
assert all(x["source_symbol"].startswith("MMODEL_FOLLOWER_MON") for x in ident["entries"])
p = argparse.ArgumentParser()
p.add_argument("--export-dir", type=Path)
a = p.parse_args()
if a.export_dir:
    index = json.loads((a.export_dir / "index.json").read_text())
    assert index["sheet_count"] == 572 and index["output_count"] == 9152
    assert len(index["entries"]) == 572
    assert {e["donor_filename"] for e in index["entries"]} == {r["file"] for r in rows}
    for e in index["entries"]:
        assert len(e["frames"]) == 16
        assert e["species_id"] is None
        for f in e["frames"]:
            file = a.export_dir / f["path"]
            assert file.is_file(), file
            assert hashlib.sha256(file.read_bytes()).hexdigest() == f["sha256"], file
print("PASS: complete 572-sheet source catalog" + (" and 9,152 exported file hashes" if a.export_dir else ""))
