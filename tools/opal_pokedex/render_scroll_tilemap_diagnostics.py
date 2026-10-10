#!/usr/bin/env python3
"""Render Pokédex scroll tilemap reference diagnostics.

The PNG is an indexed tile atlas; map indices can reference other allocations.
Out-of-atlas tile references are marked magenta rather than silently wrapped.
No output from this script is installed in the ROM.
"""
from pathlib import Path
import argparse
import json
import struct

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2] / "res/graphics/pokedex"
PAIRS = (
    ("scroll_main_background.png", "scroll_main_background.NSCR"),
    ("scroll_sub_background.png", "scroll_sub.NSCR"),
)


def render(atlas_name, screen_name, destination):
    source = Image.open(ROOT / atlas_name)
    assert source.mode == "P" and source.width % 8 == source.height % 8 == 0
    tiles_per_row = source.width // 8
    total_tiles = tiles_per_row * (source.height // 8)
    blob = (ROOT / screen_name).read_bytes()
    assert blob[:4] == b"RCSN"
    assert blob[16:20] == b"NRCS"
    tilemap_size = struct.unpack_from("<I", blob, 32)[0]
    assert 36 + tilemap_size == len(blob)
    entries = struct.unpack_from("<" + "H" * (tilemap_size // 2), blob, 36)
    assert len(entries) == 32 * 24
    output = Image.new("RGB", (256, 192), (238, 73, 166))
    missing = set()
    for index, entry in enumerate(entries):
        tile = entry & 1023
        dest_x, dest_y = (index % 32) * 8, (index // 32) * 8
        if tile >= total_tiles:
            missing.add(tile)
            continue
        source_x, source_y = tile % tiles_per_row * 8, tile // tiles_per_row * 8
        cut = source.crop((source_x, source_y, source_x + 8, source_y + 8))
        if entry & 0x400:
            cut = cut.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if entry & 0x800:
            cut = cut.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        output.paste(cut.convert("RGB"), (dest_x, dest_y))
    output.save(destination)
    return {"atlas": atlas_name, "map": screen_name,
            "atlas_tile_count": total_tiles,
            "mapped_tiles_outside_atlas": sorted(missing),
            "preview": str(destination)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = [render(a, b, args.output_dir / (a + ".map-preview.png")) for a, b in PAIRS]
    (args.output_dir / "tilemap-diagnostic.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
