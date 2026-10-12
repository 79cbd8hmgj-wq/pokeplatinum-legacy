#!/usr/bin/env python3
"""Validate rendered Ranger effect candidates against their real donor packages.

These are provenance-backed previews, not installed Platinum resources.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("output", type=Path)
    cli.add_argument("donor_root", type=Path)
    args = cli.parse_args()
    report = json.loads((args.output / "PROVENANCE.json").read_text())
    assert report["stage"] == "rendered-candidates-not-installed"
    assert len(report["entries"]) == 3
    total = 0
    for record in report["entries"]:
        assert record["curation"] not in {"reject", "decode_issue"}
        assert record["installed_in_rom"] is False
        source = (args.donor_root / record["donor_relative_path"]).resolve()
        assert source.is_relative_to(args.donor_root.resolve())
        assert source.is_file() and sha(source) == record["donor_sha256"]
        frames = record["generated_frames"]
        assert frames and len(frames) == record["rendered_cell_count"]
        for entry in frames:
            frame = (args.output / entry["path"]).resolve()
            assert frame.is_relative_to(args.output.resolve())
            assert frame.is_file() and sha(frame) == entry["sha256"]
            with Image.open(frame) as image:
                assert image.format == "PNG"
                assert image.width > 0 and image.height > 0
                image.verify()
            total += 1
    print(f"PASS: {total} donor effect cell PNGs verified against Ranger source packages; not installed in ROM")

if __name__ == "__main__":
    main()
