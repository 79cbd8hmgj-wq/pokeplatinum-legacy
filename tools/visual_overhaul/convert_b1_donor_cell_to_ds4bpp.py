#!/usr/bin/env python3
"""Convert recovered donor RGBA PNGs to deterministic DS 4bpp OBJ tile candidates.

Outputs raw 8x8 4bpp OBJ tiles + 16-colour RGB555 palette and provenance,
NOT a packaged NCGR/NCLR/NARC or an installed battle asset.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

def sha(b):
    return hashlib.sha256(b).hexdigest()

def convert(source: Path, destination: Path):
    with Image.open(source) as original:
        rgba = original.convert("RGBA")
    width, height = rgba.size
    if not width or not height or width > 256 or height > 256:
        raise ValueError("Source dimensions must be between 1 and 256")
    width_pad = (width + 7) & ~7
    height_pad = (height + 7) & ~7
    # Transparent index 0 is reserved; all visible colours must fit 15 RGB555 entries.
    source_pixels = list(rgba.getdata())
    rgb555 = []
    for red, green, blue, alpha in source_pixels:
        rgb555.append(None if alpha < 128 else ((red >> 3) | ((green >> 3) << 5) | ((blue >> 3) << 10)))
    colours = sorted({v for v in rgb555 if v is not None})
    if len(colours) > 15:
        raise ValueError(f"{len(colours)} opaque RGB555 colours: 4bpp OBJ supports max 15 + transparent; quantize explicitly first")
    lookup = {v: i + 1 for i, v in enumerate(colours)}
    indices = [0] * (width_pad * height_pad)
    for y in range(height):
        for x in range(width):
            val = rgb555[y * width + x]
            indices[y * width_pad + x] = 0 if val is None else lookup[val]
    output = bytearray()
    for tile_y in range(0, height_pad, 8):
        for tile_x in range(0, width_pad, 8):
            for y in range(8):
                for x in range(0, 8, 2):
                    offset = (tile_y + y) * width_pad + tile_x + x
                    output.append(indices[offset] | (indices[offset + 1] << 4))
    assert len(output) == width_pad * height_pad // 2
    palette = bytearray()
    for v in [0] + colours + [0] * (15 - len(colours)):
        palette.extend(v.to_bytes(2, "little"))
    destination.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    tiles_path = destination / (stem + ".4bpp")
    palette_path = destination / (stem + ".rgb555")
    tiles_path.write_bytes(output)
    palette_path.write_bytes(palette)
    report = {
        "source": str(source), "source_sha256": sha(source.read_bytes()),
        "source_dimensions": [width, height],
        "padded_dimensions": [width_pad, height_pad],
        "tile_count": width_pad * height_pad // 64,
        "opaque_colours": len(colours),
        "transparent_index": 0,
        "tile_order": "8x8 row-major 1D OBJ 4bpp",
        "tiles_file": tiles_path.name, "tiles_sha256": sha(output),
        "palette_file": palette_path.name, "palette_sha256": sha(palette),
        "state": "raw_DS_tile_candidate_NOT_NCGR_NCLR_or_installed_ROM_resource",
    }
    (destination / (stem + ".json")).write_text(json.dumps(report, indent=2) + "\n")
    return report

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("png", type=Path)
    cli.add_argument("output_dir", type=Path)
    args = cli.parse_args()
    print(json.dumps(convert(args.png.resolve(), args.output_dir.resolve()), indent=2))

if __name__ == "__main__":
    main()
