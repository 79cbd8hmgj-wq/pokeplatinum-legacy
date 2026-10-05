#!/usr/bin/env python3
"""Low-level helpers for Pokémon Ranger 2 sprite package inspection.

This module deliberately implements only the container layers that are well-defined
and independently testable here:

* Nintendo DS LZ10 decompression
* NARC member extraction
* filename recovery from a simple Nitro FNTB name table when present
* resource classification by filename suffix and Nitro magic

It does not guess at Ranger's .cac or NCER cell semantics. Rendering code should
consume the extracted resources through an explicit backend instead of silently
inventing geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


class RangerPackageError(RuntimeError):
    pass


def lz10_decompress(data: bytes) -> bytes:
    if len(data) < 4 or data[0] != 0x10:
        raise RangerPackageError("input is not Nintendo DS LZ10 data")
    out_size = int.from_bytes(data[1:4], "little")
    src = 4
    out = bytearray()
    while len(out) < out_size:
        if src >= len(data):
            raise RangerPackageError("truncated LZ10 flag stream")
        flags = data[src]
        src += 1
        for bit in range(7, -1, -1):
            if len(out) >= out_size:
                break
            if flags & (1 << bit):
                if src + 1 >= len(data):
                    raise RangerPackageError("truncated LZ10 back-reference")
                a = data[src]
                b = data[src + 1]
                src += 2
                length = (a >> 4) + 3
                disp = ((a & 0x0F) << 8) | b
                distance = disp + 1
                if distance > len(out):
                    raise RangerPackageError(
                        f"invalid LZ10 back-reference distance {distance} at {src - 2}"
                    )
                for _ in range(length):
                    out.append(out[-distance])
                    if len(out) >= out_size:
                        break
            else:
                if src >= len(data):
                    raise RangerPackageError("truncated LZ10 literal")
                out.append(data[src])
                src += 1
    return bytes(out)


@dataclass(frozen=True)
class NarcMember:
    index: int
    name: str
    data: bytes


def _nitro_blocks(data: bytes) -> dict[bytes, tuple[int, int]]:
    if len(data) < 16:
        raise RangerPackageError("Nitro container too short")
    block_count = struct.unpack_from("<H", data, 0x0E)[0]
    pos = struct.unpack_from("<H", data, 0x0C)[0]
    blocks: dict[bytes, tuple[int, int]] = {}
    for _ in range(block_count):
        if pos + 8 > len(data):
            raise RangerPackageError("truncated Nitro block header")
        magic = data[pos:pos + 4]
        size = struct.unpack_from("<I", data, pos + 4)[0]
        if size < 8 or pos + size > len(data):
            raise RangerPackageError(f"invalid Nitro block {magic!r} size {size}")
        blocks[magic] = (pos, size)
        pos += size
    return blocks


def _parse_flat_fntb_names(block: bytes, count: int) -> list[str] | None:
    """Recover names from the common single-directory FNTB layout.

    Ranger packages observed in the project are flat archives. If the table is not
    flat or cannot be decoded conservatively, callers fall back to stable member
    names rather than guessing.
    """
    if len(block) < 16:
        return None
    payload = block[8:]
    if len(payload) < 8:
        return None

    subtable_off, first_file_id, parent = struct.unpack_from("<IHH", payload, 0)
    if first_file_id != 0 or subtable_off >= len(payload):
        return None

    pos = subtable_off
    names: list[str] = []
    while pos < len(payload) and len(names) < count:
        n = payload[pos]
        pos += 1
        if n == 0:
            break
        is_dir = bool(n & 0x80)
        length = n & 0x7F
        if pos + length > len(payload):
            return None
        raw = payload[pos:pos + length]
        pos += length
        if is_dir:
            if pos + 2 > len(payload):
                return None
            pos += 2
            return None
        try:
            names.append(raw.decode("ascii"))
        except UnicodeDecodeError:
            return None

    if len(names) != count:
        return None
    return names


def extract_narc(data: bytes) -> list[NarcMember]:
    if data[:4] not in {b"NARC", b"CRAN"}:
        raise RangerPackageError(f"decompressed package is not NARC: magic={data[:4]!r}")

    blocks = _nitro_blocks(data)
    fat = blocks.get(b"BTAF") or blocks.get(b"FATB")
    fnt = blocks.get(b"BTNF") or blocks.get(b"FNTB")
    img = blocks.get(b"GMIF") or blocks.get(b"FIMG")
    if fat is None or img is None:
        raise RangerPackageError("NARC missing FATB/FIMG blocks")

    fat_pos, fat_size = fat
    fat_block = data[fat_pos:fat_pos + fat_size]
    count = struct.unpack_from("<H", fat_block, 8)[0]
    entries_off = 12
    if entries_off + count * 8 > len(fat_block):
        raise RangerPackageError("truncated NARC FAT entries")

    img_pos, img_size = img
    img_payload = data[img_pos + 8:img_pos + img_size]

    names: list[str] | None = None
    if fnt is not None:
        p, s = fnt
        names = _parse_flat_fntb_names(data[p:p + s], count)

    members: list[NarcMember] = []
    for i in range(count):
        start, end = struct.unpack_from("<II", fat_block, entries_off + i * 8)
        if start > end or end > len(img_payload):
            raise RangerPackageError(
                f"NARC member {i} range {start:#x}:{end:#x} outside FIMG"
            )
        name = names[i] if names else f"member_{i:03d}.bin"
        members.append(NarcMember(i, name, img_payload[start:end]))
    return members


def classify_member(name: str, data: bytes) -> str:
    lower = name.lower()
    if lower.endswith(".cac"):
        return "cac"
    if lower.endswith(".nclr"):
        return "nclr"
    if lower.endswith(".ncbr"):
        return "ncbr"
    if lower.endswith(".ncer"):
        return "ncer"

    magic = data[:4]
    # Nitro headers are stored little-endian, so disk magic is reversed.
    if magic in {b"RLCN", b"NCLR"}:
        return "nclr"
    if magic in {b"RECN", b"NCER"}:
        return "ncer"
    if magic in {b"RGCN", b"NCGR"}:
        return "ncgr"
    return "unknown"


def extract_package(path: Path) -> tuple[bytes, list[NarcMember]]:
    compressed = path.read_bytes()
    decompressed = lz10_decompress(compressed)
    return decompressed, extract_narc(decompressed)
