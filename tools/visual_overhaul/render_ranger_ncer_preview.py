#!/usr/bin/env python3
"""Render Ranger NCER cells from extracted NCLR + NCGR/NCBR resources.

This handles the standard Nitro cell-bank structure used by the first Ranger
Pokémon pilot. It intentionally ignores Ranger .cac semantics; each NCER cell is
rendered independently using OAM attributes and the paired RGCN character data.
"""
from __future__ import annotations

import argparse
import binascii
import struct
import zlib
from pathlib import Path


SHAPE_SIZE = {
    0: ((8, 8), (16, 16), (32, 32), (64, 64)),
    1: ((16, 8), (32, 8), (32, 16), (64, 32)),
    2: ((8, 16), (8, 32), (16, 32), (32, 64)),
}


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def signed_x(attr1: int) -> int:
    x = attr1 & 0x1FF
    return x - 0x200 if x >= 0x100 else x


def signed_y(attr0: int) -> int:
    y = attr0 & 0xFF
    return y - 0x100 if y >= 0x80 else y


def bgr555_to_rgb(value: int) -> tuple[int, int, int]:
    return (
        (value & 0x1F) * 255 // 31,
        ((value >> 5) & 0x1F) * 255 // 31,
        ((value >> 10) & 0x1F) * 255 // 31,
    )


def read_palette(path: Path) -> list[tuple[int, int, int]]:
    raw = path.read_bytes()
    if raw[:4] != b"RLCN" or raw[0x10:0x14] != b"TTLP":
        raise ValueError(f"{path}: not a standard NCLR")
    size = u32(raw, 0x20)
    if 0x28 + size > len(raw):
        raise ValueError(f"{path}: invalid palette size")
    return [bgr555_to_rgb(u16(raw, p)) for p in range(0x28, 0x28 + size, 2)]


def read_chars(path: Path) -> tuple[int, int, list[list[int]]]:
    raw = path.read_bytes()
    if raw[:4] != b"RGCN" or raw[0x10:0x14] != b"RAHC":
        raise ValueError(f"{path}: not a standard RGCN")
    height_tiles = u16(raw, 0x18)
    width_tiles = u16(raw, 0x1A)
    fmt = u16(raw, 0x1C)
    size = u32(raw, 0x28)
    body = raw[0x30:0x30 + size]
    if fmt != 3:
        raise ValueError(f"{path}: expected 4bpp format 3, got {fmt}")
    if len(body) != width_tiles * height_tiles * 32:
        raise ValueError(f"{path}: character geometry/data mismatch")

    tiles = []
    for pos in range(0, len(body), 32):
        px = []
        for byte in body[pos:pos + 32]:
            px.extend((byte & 0x0F, byte >> 4))
        tiles.append(px)
    return width_tiles, height_tiles, tiles


def read_cells(path: Path) -> list[list[tuple[int, int, int]]]:
    raw = path.read_bytes()
    if raw[:4] != b"RECN" or raw[0x10:0x14] != b"KBEC":
        raise ValueError(f"{path}: not a standard NCER")
    count = u16(raw, 0x18)
    cell_table = 0x30
    oam_base = cell_table + count * 8
    cells = []
    for i in range(count):
        off = cell_table + i * 8
        oam_count = u16(raw, off)
        oam_rel = u32(raw, off + 4)
        start = oam_base + oam_rel
        end = start + oam_count * 6
        if end > len(raw):
            raise ValueError(f"{path}: cell {i} OAM exceeds file")
        oams = []
        for p in range(start, end, 6):
            oams.append((u16(raw, p), u16(raw, p + 2), u16(raw, p + 4)))
        cells.append(oams)
    return cells


def tile_pixel(
    tiles: list[list[int]],
    sheet_width_tiles: int,
    logical_tile: int,
    x: int,
    y: int,
    vram_stride_tiles: int,
) -> int:
    row, col = divmod(logical_tile, vram_stride_tiles)
    source = row * sheet_width_tiles + col
    if source < 0 or source >= len(tiles):
        return 0
    return tiles[source][y * 8 + x]


def render_cell(
    oams: list[tuple[int, int, int]],
    sheet_width_tiles: int,
    tiles: list[list[int]],
    vram_stride_tiles: int,
) -> tuple[int, int, list[int]]:
    objects = []
    for attr0, attr1, attr2 in oams:
        shape = (attr0 >> 14) & 0x3
        size = (attr1 >> 14) & 0x3
        if shape not in SHAPE_SIZE:
            continue
        width, height = SHAPE_SIZE[shape][size]
        objects.append(
            {
                "x": signed_x(attr1),
                "y": signed_y(attr0),
                "width": width,
                "height": height,
                "tile": attr2 & 0x3FF,
                "hflip": bool(attr1 & 0x1000),
                "vflip": bool(attr1 & 0x2000),
            }
        )
    if not objects:
        return 1, 1, [0]

    min_x = min(obj["x"] for obj in objects)
    min_y = min(obj["y"] for obj in objects)
    max_x = max(obj["x"] + obj["width"] for obj in objects)
    max_y = max(obj["y"] + obj["height"] for obj in objects)
    width = max_x - min_x
    height = max_y - min_y
    canvas = [0] * (width * height)

    for obj in objects:
        wt = obj["width"] // 8
        ht = obj["height"] // 8
        for py in range(obj["height"]):
            sy = obj["height"] - 1 - py if obj["vflip"] else py
            ty, iy = divmod(sy, 8)
            for px in range(obj["width"]):
                sx = obj["width"] - 1 - px if obj["hflip"] else px
                tx, ix = divmod(sx, 8)
                logical = obj["tile"] + ty * vram_stride_tiles + tx
                color = tile_pixel(
                    tiles, sheet_width_tiles, logical, ix, iy, vram_stride_tiles
                )
                if color == 0:
                    continue
                dx = obj["x"] - min_x + px
                dy = obj["y"] - min_y + py
                if 0 <= dx < width and 0 <= dy < height:
                    canvas[dy * width + dx] = color
    return width, height, canvas


def chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def write_indexed_png(
    path: Path,
    width: int,
    height: int,
    pixels: list[int],
    palette: list[tuple[int, int, int]],
) -> None:
    padded = palette[:256] + [(0, 0, 0)] * max(0, 256 - len(palette))
    plte = bytes(c for rgb in padded for c in rgb)
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        rows.extend(pixels[y * width:(y + 1) * width])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"PLTE", plte)
        + chunk(b"tRNS", bytes([0] + [255] * 255))
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graphics", required=True, type=Path)
    parser.add_argument("--palette", required=True, type=Path)
    parser.add_argument("--cells", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--vram-stride-tiles",
        type=int,
        default=32,
        help="2D OBJ mapping stride in 4bpp tiles; Ranger pilot uses 32.",
    )
    args = parser.parse_args()

    palette = read_palette(args.palette)
    sheet_width, _sheet_height, tiles = read_chars(args.graphics)
    cells = read_cells(args.cells)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for i, oams in enumerate(cells):
        width, height, pixels = render_cell(
            oams, sheet_width, tiles, args.vram_stride_tiles
        )
        target = args.output_dir / f"cell_{i:03d}.png"
        write_indexed_png(target, width, height, pixels, palette)
        print(f"cell {i}: {width}x{height} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
