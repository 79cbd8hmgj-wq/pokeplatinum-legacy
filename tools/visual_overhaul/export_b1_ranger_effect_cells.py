#!/usr/bin/env python3
"""Export *real* Ranger 2 effect cells with provenance for Opal B1 review.

Produces PNG frame candidates and checksums, never silently installs previews
as a compiled battle resource. Donor source tree must be provided explicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path

from b1_donor_effect_import_preflight import make_report
from render_ranger_pokemon_package import render_package

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--vram-stride-tiles", type=int, default=32)
    args = p.parse_args()
    source_root = args.donor_root.resolve()
    output = args.output_dir.resolve()
    if not source_root.is_dir():
        p.error(f"missing donor root: {source_root}")
    provenance = []
    for row in make_report()["entries"]:
        if row["curation"] in ("reject", "decode_issue"):
            raise ValueError(f"Unsafe curation status: {row['source_unit']}")
        source = row["source_members"][0]
        package = source_root / source
        if not package.is_file():
            raise FileNotFoundError(f"{row['source_unit']}: {package}")
        target = output / row["source_unit"].replace("/", "_")
        count = render_package(package, target, args.vram_stride_tiles)
        images = sorted(target.rglob("*.png"))
        assert count == len(images) and count > 0
        provenance.append({
            **row,
            "donor_relative_path": source,
            "donor_sha256": sha(package),
            "rendered_cell_count": count,
            "generated_frames": [{"path": str(f.relative_to(output)), "sha256": sha(f)} for f in images],
            "installed_in_rom": False,
        })
    output.mkdir(parents=True, exist_ok=True)
    (output / "PROVENANCE.json").write_text(json.dumps({
        "stage": "rendered-candidates-not-installed",
        "entries": provenance,
    }, indent=2) + "\n")
    print(f"Exported {sum(r['rendered_cell_count'] for r in provenance)} real donor cells; no ROM resources changed")

if __name__ == "__main__":
    main()
