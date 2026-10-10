#!/usr/bin/env python3
"""Static checks for Opal Bag V3 panel source images.

Run: python tools/opal_bag/validate_v3_panels.py
This tests SOURCE ART only, not compiled Platinum graphics.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
from PIL import Image

HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "generate_v3_panels.py"
W, H = 256, 192

def check(p: Path):
    with Image.open(p) as image:
        assert image.size == (W, H), f"{p.name}: invalid dimensions {image.size}"
        assert image.mode == "P", f"{p.name}: expected indexed P mode, got {image.mode}"
        entries = image.getcolors(W * H)
        assert entries is not None
        indexes = {palette_index for _, palette_index in entries}
        assert len(indexes) <= 16 and all(0 <= v < 16 for v in indexes), (
            f"{p.name}: not a 4bpp-compatible indexed image"
        )
        assert image.getpalette() is not None
        return p.read_bytes()

def main():
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        for directory in (first, second):
            subprocess.run(
                [sys.executable, str(GENERATOR), "--output", directory],
                check=True,
            )
        for screen in ("main", "sub"):
            name = f"opal_v3_{screen}_panel_source.png"
            first_bytes = check(Path(first) / name)
            second_bytes = check(Path(second) / name)
            assert first_bytes == second_bytes, f"{name} output is not deterministic"
            print(f"PASS {name}: 256x192, indexed <=16 colors, deterministic")
    print("PASS source art preflight; compiled NCGR/NSCR/NCLR and ROM checks still required.")

if __name__ == "__main__":
    main()
