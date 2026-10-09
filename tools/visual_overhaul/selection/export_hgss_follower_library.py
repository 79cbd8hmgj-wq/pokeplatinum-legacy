#!/usr/bin/env python3
"""Deterministically export ALL cataloged HGSS follower sheets, without Platinum field hooks.

Inputs: pinned evidence manifest and user-provided HGSS extraction.
Outputs: 572 sheet directories (normal/shiny x 8 PNG frames), index.json and hashes.
A missing/bad donor is a hard error; no silent partial-success export.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import nsbmd_preview as N  # noqa: E402

EVIDENCE = ROOT / "docs/visual_overhaul/selection/mining/evidence/hgss_follower_sheets.json"
SOURCE_NAME = re.compile(r"^mmodel_\d{8}\.NSBTX$")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def export(hgss_root: Path, destination: Path, check_only: bool = False) -> None:
    evidence = json.loads(EVIDENCE.read_text())
    rows = evidence["rows"]
    assert len(rows) == evidence["sheets"] == 572
    assert len({r["file"] for r in rows}) == 572
    source_root = hgss_root / "files/data/mmodel/mmodel"
    absent = [r["file"] for r in rows if not (source_root / r["file"]).is_file()]
    if absent:
        raise RuntimeError(f"Missing {len(absent)} of 572 HGSS donors, examples: {absent[:8]}")
    if check_only:
        print("PASS: all 572 raw source files present")
        return

    # Do not claim a complete export until every donor has passed decoding.
    # Existing output must be empty to prevent stale frames surviving a re-run.
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError(f"Output directory is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for row in rows:
        name = row["file"]
        assert SOURCE_NAME.fullmatch(name), name
        blob = (source_root / name).read_bytes()
        model, texbase = N.parse_bmd(blob)
        t = N.parse_tex0(blob, texbase)
        frame_names = list(t["texs"])
        palettes = list(t["pal_order"])
        if len(frame_names) != 8 or len(palettes) != 2:
            raise ValueError(f"{name}: expected 8 textures and 2 palette variants")
        if set(frame_names) != set(row["tex_names"]):
            raise ValueError(f"{name}: texture name mismatch with frozen evidence")
        sheet = destination / name.removesuffix(".NSBTX")
        sheet.mkdir(exist_ok=True)
        files = []
        for variant, palname in zip(("palette_0", "palette_1"), palettes):
            for index, texname in enumerate(frame_names):
                pixels = N.decode_tex(blob, t, t["texs"][texname], palname)
                picture = Image.fromarray(pixels, "RGBA")
                if picture.size != (row["size"], row["size"]):
                    raise ValueError(f"{name}/{variant}/{index}: unexpected dimensions {picture.size}")
                relative = f"{name.removesuffix('.NSBTX')}/{variant}_{index:02d}.png"
                file = destination / relative
                picture.save(file, format="PNG", optimize=False)
                files.append({"path": relative, "sha256": sha(file.read_bytes()), "frame": texname,
                              "palette_name": palname, "variant": variant, "size": list(picture.size)})
        entries.append({"donor_filename": name, "donor_sha256": sha(blob),
                        "species_id": None, "form_id": None,
                        "frames": files, "frame_count": 8, "palette_variants": 2})

    index = {"schema_version": 1, "source_evidence": str(EVIDENCE.relative_to(ROOT)),
             "sheet_count": len(entries), "output_count": sum(len(x["frames"]) for x in entries),
             "species_mappings_verified": False, "palette_variant_roles_verified": False, "entries": entries}
    assert index["sheet_count"] == 572 and index["output_count"] == 9152
    (destination / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    print(f"Exported {len(entries)} sheets and {index['output_count']} PNGs to {destination}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--hgss-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--check-only", action="store_true")
    args = p.parse_args()
    export(args.hgss_root, args.out, args.check_only)
