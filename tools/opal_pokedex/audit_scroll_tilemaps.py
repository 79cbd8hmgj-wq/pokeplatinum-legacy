#!/usr/bin/env python3
"""Report Pokédex scroll screen tilemap references and source-asset tile sizes.

This produces machine-readable evidence for future art replacement. It does
not assume tile IDs start at zero or infer runtime tilebase from a PNG alone.
"""
from pathlib import Path
from struct import unpack_from
import json

ROOT = Path(__file__).resolve().parents[2] / "res/graphics/pokedex"
PAIRS = (
    ("scroll_main_background.png", "scroll_main_background.NSCR", (256, 64)),
    ("scroll_sub_background.png", "scroll_sub.NSCR", (256, 24)),
)


def inspect(png_name, nscr_name, size):
    png = (ROOT / png_name).read_bytes()
    assert png[:8] == bytes.fromhex("89504e470d0a1a0a"), png_name
    assert unpack_from(">II", png, 16) == size, png_name
    assert (png[24], png[25]) == (4, 3), png_name
    data = (ROOT / nscr_name).read_bytes()
    assert data[:4] == b"RCSN", nscr_name
    assert data[16:20] == b"NRCS", nscr_name
    file_size = unpack_from("<I", data, 8)[0]
    section_size = unpack_from("<I", data, 20)[0]
    assert file_size == len(data), nscr_name
    assert section_size + 16 == len(data), nscr_name
    payload_len = unpack_from("<I", data, 32)[0]
    assert payload_len % 2 == 0 and 36 + payload_len == len(data), nscr_name
    entries = [unpack_from("<H", data, 36 + offset)[0] for offset in range(0, payload_len, 2)]
    tile_ids = [entry & 0x3FF for entry in entries]
    palette_banks = sorted({entry >> 12 for entry in entries})
    atlas_count = size[0] // 8 * (size[1] // 8)
    unresolved = sorted({tile for tile in tile_ids if tile >= atlas_count})
    return {
        "png": png_name, "nscr": nscr_name,
        "png_tiles": atlas_count,
        "screen_entries": len(entries),
        "min_map_tile_id": min(tile_ids),
        "max_map_tile_id": max(tile_ids),
        "unique_map_tiles": len(set(tile_ids)),
        "palette_banks": palette_banks,
        "unresolved_atlas_tile_ids": unresolved,
        "unresolved_map_entries": sum(tile >= atlas_count for tile in tile_ids),
        "self_contained_tilemap": len(unresolved) == 0,
        "requires_runtime_tilebase_trace": True,
    }


def main():
    report = [inspect(*pair) for pair in PAIRS]
    print(json.dumps(report, indent=2))
    assert all(row["screen_entries"] == 768 for row in report)
    assert report[0]["self_contained_tilemap"] is False, "Main tilemap dependency needs investigation"
    assert report[1]["self_contained_tilemap"] is True, "Sub-screen atlas should be self-contained"
    assert report[0]["palette_banks"] == [5]
    assert report[1]["palette_banks"] == [3]


if __name__ == "__main__":
    main()
