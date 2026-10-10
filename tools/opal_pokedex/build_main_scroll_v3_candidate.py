#!/usr/bin/env python3
"""Rebuild a 4bpp Pokédex main-scroll atlas with subtle Opal edge trim.

This operates on the actual tile atlas, not a rendered screenshot. It only edits
solid-color tiles referenced by the NSCR, so the embedded SINNOH/NATIONAL lettering,
icon silhouettes, and preexisting detailed tiles remain byte-for-byte identical.
Run with --output for a candidate PNG; --check validates the safety invariants.
"""
import argparse
from collections import Counter
from pathlib import Path
from struct import unpack_from
from PIL import Image

ROOT = Path(__file__).resolve().parents[2] / "res/graphics/pokedex"
SOURCE = ROOT / "scroll_main_background.png"
SCREEN = ROOT / "scroll_main_background.NSCR"


def tiles_used():
    data = SCREEN.read_bytes()
    assert data[:4] == b"RCSN" and data[16:20] == b"NRCS"
    length = unpack_from("<I", data, 32)[0]
    assert 36 + length == len(data) and length == 32 * 24 * 2
    return Counter(unpack_from("<H", data, i)[0] & 1023 for i in range(36, 36 + length, 2))


def transform():
    src = Image.open(SOURCE)
    assert src.mode == "P" and src.size == (256, 64)
    assert max(src.getdata()) < 16
    out = src.copy()
    counts = tiles_used()
    assert max(counts) < 256
    changed = []
    # Target only repeated, strictly flat tiles, preserving all composed labels.
    for tile, uses in sorted(counts.items()):
        if uses < 4:
            continue
        x, y = (tile % 32) * 8, (tile // 32) * 8
        pixels = [src.getpixel((x + dx, y + dy)) for dy in range(8) for dx in range(8)]
        if len(set(pixels)) != 1 or pixels[0] in (0, 1):
            continue
        # Preserve the original background with a slim gold pinstripe.
        for dx in range(1, 7):
            out.putpixel((x + dx, y + 6), 9)
        changed.append(tile)
    # The installed atlas may already carry the chosen V3 trim; regeneration must be idempotent.
    x197, y197 = (197 % 32) * 8, (197 // 32) * 8
    assert all(out.getpixel((x197 + dx, y197 + 6)) == 9 for dx in range(1, 7)), "Expected installed V3 trim on tile 197"
    # Ensure untouched tile pixels remain bit-identical.
    changed_set = set(changed)
    for tile in range(256):
        if tile in changed_set:
            continue
        x, y = (tile % 32) * 8, (tile // 32) * 8
        assert src.crop((x, y, x + 8, y + 8)).tobytes() == out.crop((x, y, x + 8, y + 8)).tobytes()
    assert out.mode == "P" and out.size == src.size and max(out.getdata()) < 16
    return out, changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output, changed = transform()
    print(f"Candidate tiles changed: {changed}")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output.save(args.output)
    if args.check:
        assert not args.output, "--check must not write candidate outputs"


if __name__ == "__main__":
    main()
