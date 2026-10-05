#!/usr/bin/env python3
"""Render raw Ranger Nitro character resources to deterministic PNG previews.

This is a pre-NCER preview renderer. It decodes the standard NCLR + RGCN payload
and lays out character tiles using the width/height encoded in the RAHC block.
It deliberately does not guess Ranger CAC semantics or NCER cell composition.
"""
from __future__ import annotations

import argparse
import binascii
import struct
import zlib
from pathlib import Path


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def bgr555_to_rgb(value: int) -> tuple[int, int, int]:
    r = (value & 0x1F) * 255 // 31
    g = ((value >> 5) & 0x1F) * 255 // 31
    b = ((value >> 10) & 0x1F) * 255 // 31
    return r, g, b


def read_nclr(path: Path) -> list[tuple[int, int, int]]:
    raw = path.read_bytes()
    if raw[:4] != b"RLCN":
        raise ValueError(f"{path}: not NCLR/RLCN")
    if raw[0x10:0x14] != b"TTLP":
        raise ValueError(f"{path}: missing TTLP")
    data_size = struct.unpack_from("<I", raw, 0x20)[0]
    offset = 0x28
    if offset + data_size > len(raw):
        raise ValueError(f"{path}: palette data exceeds file")
    colors = []
    for pos in range(offset, offset + data_size, 2):
        colors.append(bgr555_to_rgb(u16(raw, pos)))
    return colors


def read_rgcn(path: Path) -> tuple[int, int, list[int]]:
    raw = path.read_bytes()
    if raw[:4] != b"RGCN":
        raise ValueError(f"{path}: not NCGR/NCBR (RGCN)")
    if raw[0x10:0x14] != b"RAHC":
        raise ValueError(f"{path}: missing RAHC")

    height_tiles = u16(raw, 0x18)
    width_tiles = u16(raw, 0x1A)
    pixel_format = u16(raw, 0x1C)
    data_size = struct.unpack_from("<I", raw, 0x28)[0]
    data_off = 0x30
    body = raw[data_off:data_off + data_size]

    if pixel_format != 3:
        raise ValueError(
            f"{path}: unsupported RGCN pixel format {pixel_format}; expected 3 (4bpp)"
        )
    expected = width_tiles * height_tiles * 32
    if expected != len(body):
        raise ValueError(
            f"{path}: geometry expects {expected} bytes, file has {len(body)}"
        )

    width = width_tiles * 8
    height = height_tiles * 8
    pixels = [0] * (width * height)

    tile = 0
    for ty in range(height_tiles):
        for tx in range(width_tiles):
            chunk = body[tile * 32:(tile + 1) * 32]
            tile += 1
            p = 0
            for y in range(8):
                for xpair in range(4):
                    byte = chunk[p]
                    p += 1
                    x = xpair * 2
                    pixels[(ty * 8 + y) * width + tx * 8 + x] = byte & 0x0F
                    pixels[(ty * 8 + y) * width + tx * 8 + x + 1] = byte >> 4

    return width, height, pixels


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png(
    path: Path,
    width: int,
    height: int,
    pixels: list[int],
    palette: list[tuple[int, int, int]],
) -> None:
    if len(palette) > 256:
        raise ValueError("PNG palette exceeds 256 colors")
    palette = palette + [(0, 0, 0)] * (256 - len(palette))
    plte = bytes(v for rgb in palette for v in rgb)

    rows = bytearray()
    for y in range(height):
        rows.append(0)
        rows.extend(pixels[y * width:(y + 1) * width])

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"PLTE", plte)
        + png_chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + png_chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--package-dir",
        required=True,
        type=Path,
        help="Directory containing extracted Ranger NARC members.",
    )
    parser.add_argument("--palette", type=Path, help="Explicit NCLR path.")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    package = args.package_dir.expanduser().resolve()
    output = args.output_dir.expanduser().resolve()
    palettes = sorted(package.glob("*.NCLR"))
    palette_path = args.palette.expanduser().resolve() if args.palette else (
        palettes[0] if palettes else None
    )
    if palette_path is None:
        raise SystemExit("No NCLR palette found; use --palette")

    palette = read_nclr(palette_path)
    graphics = sorted([*package.glob("*.NCGR"), *package.glob("*.NCBR")])
    if not graphics:
        raise SystemExit("No NCGR/NCBR files found")

    print(f"Palette: {palette_path.name} ({len(palette)} colors)")
    for gfx in graphics:
        width, height, pixels = read_rgcn(gfx)
        target = output / f"{gfx.stem}.png"
        write_png(target, width, height, pixels, palette)
        print(f"{gfx.name}: {width}x{height} -> {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
