#!/usr/bin/env python3
"""Generate non-installed Pokédex scroll-strip composition previews.

This intentionally does not overwrite the NSCR-linked tile graphics: those must
first be audited for tile indices and VRAM capacity. Output is a preview only.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import argparse

ROOT = Path(__file__).resolve().parents[2]
GRAPHICS = ROOT / "res/graphics/pokedex"

def preview(name: str, width: int, height: int) -> Image.Image:
    source = Image.open(GRAPHICS / name)
    if source.size != (width, height) or source.mode != "P":
        raise ValueError(f"{name}: unexpected dimensions or indexed format")
    # Compose an independent RGB preview, leaving game source pixels unchanged.
    base = Image.new("RGB", source.size, "#e8dfe9")
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, 0, width - 1, height - 1), outline="#59446b", width=2)
    draw.line((8, 9, width - 9, 9), fill="#c3a56c", width=2)
    draw.line((8, height - 9, width - 9, height - 9), fill="#a79ab5", width=1)
    if height >= 64:
        draw.rounded_rectangle((12, 15, 244, 47), radius=6, fill="#f8f3f5", outline="#ab94bc", width=2)
    else:
        draw.line((12, 13, 244, 13), fill="#bca6c7", width=1)
    return base

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for source, dims in (
        ("scroll_main_background.png", (256, 64)),
        ("scroll_sub_background.png", (256, 24)),
    ):
        im = preview(source, *dims)
        output = args.output_dir / source
        im.save(output)
        print(f"PREVIEW ONLY: {output}")

if __name__ == "__main__":
    main()
