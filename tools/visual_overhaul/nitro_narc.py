#!/usr/bin/env python3
"""Minimal, deterministic Nitro NARC / LZ10 / NCGR / NCLR / NSCR helpers.

Used by the G7 generators to author resources that live inside prebuilt
NARC archives (for example ``res/prebuilt/battle/graphic/pl_batt_bg.narc``).
Everything here is pure Python and byte-for-byte deterministic.
"""

import struct


def read_narc(path):
    """Return the list of member byte strings in a NARC file."""
    data = open(path, "rb").read()
    if data[:4] != b"NARC":
        raise ValueError(f"{path}: not a NARC")
    pos = struct.unpack_from("<H", data, 0x0C)[0]
    if data[pos:pos + 4] != b"BTAF":
        raise ValueError(f"{path}: missing FATB")
    fatb_size, count = struct.unpack_from("<II", data, pos + 4)
    entries = [struct.unpack_from("<II", data, pos + 12 + 8 * i) for i in range(count)]
    fnt = pos + fatb_size
    if data[fnt:fnt + 4] != b"BTNF":
        raise ValueError(f"{path}: missing FNT")
    fnt_size = struct.unpack_from("<I", data, fnt + 4)[0]
    fimg = fnt + fnt_size
    if data[fimg:fimg + 4] != b"GMIF":
        raise ValueError(f"{path}: missing FIMG")
    base = fimg + 8
    members = [data[base + s:base + e] for s, e in entries]
    fnt_raw = data[fnt:fnt + fnt_size]
    return members, fnt_raw


def write_narc(members, fnt_raw):
    """Serialize members into a NARC with 4-byte aligned member starts."""
    entries = []
    blob = bytearray()
    for member in members:
        while len(blob) % 4:
            blob.append(0xFF)
        start = len(blob)
        blob += member
        entries.append((start, len(blob)))
    while len(blob) % 4:
        blob.append(0xFF)

    fatb = b"BTAF" + struct.pack("<II", 12 + 8 * len(entries), len(entries))
    fatb += b"".join(struct.pack("<II", s, e) for s, e in entries)
    fimg = b"GMIF" + struct.pack("<I", 8 + len(blob)) + bytes(blob)
    total = 16 + len(fatb) + len(fnt_raw) + len(fimg)
    header = b"NARC" + struct.pack("<HHIHH", 0xFFFE, 0x0100, total, 16, 3)
    return header + fatb + fnt_raw + fimg


def lz10_decompress(src):
    if src[0] != 0x10:
        raise ValueError("not an LZ10 stream")
    size = src[1] | src[2] << 8 | src[3] << 16
    out = bytearray()
    i = 4
    while len(out) < size:
        flags = src[i]
        i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                v = src[i] << 8 | src[i + 1]
                i += 2
                length = (v >> 12) + 3
                disp = (v & 0xFFF) + 1
                for _ in range(length):
                    out.append(out[-disp])
            else:
                out.append(src[i])
                i += 1
    return bytes(out[:size])


def lz10_compress(data):
    """Greedy LZ10 encoder (deterministic; any valid stream decodes identically)."""
    n = len(data)
    out = bytearray([0x10, n & 0xFF, n >> 8 & 0xFF, n >> 16 & 0xFF])
    table = {}
    i = 0
    flag_pos = None
    bit = 8
    while i < n:
        if bit == 8:
            flag_pos = len(out)
            out.append(0)
            bit = 0
        best_len = 0
        best_disp = 0
        if i + 3 <= n:
            key = data[i:i + 3]
            for j in reversed(table.get(key, [])[-32:]):
                disp = i - j
                if disp > 0x1000:
                    break
                length = 3
                while length < 18 and i + length < n and data[j + length] == data[i + length]:
                    length += 1
                if length > best_len:
                    best_len, best_disp = length, disp
                    if length == 18:
                        break
        if best_len >= 3:
            out[flag_pos] |= 0x80 >> bit
            v = (best_len - 3) << 12 | (best_disp - 1)
            out.append(v >> 8)
            out.append(v & 0xFF)
            step = best_len
        else:
            out.append(data[i])
            step = 1
        for k in range(step):
            if i + k + 3 <= n:
                table.setdefault(data[i + k:i + k + 3], []).append(i + k)
        i += step
        bit += 1
    while len(out) % 4:
        out.append(0)
    return bytes(out)


# --- NCGR (RGCN) 4bpp tile data -------------------------------------------

NCGR_DATA_OFFSET = 0x30


def ncgr_tiles(raw):
    """Decode a 4bpp NCGR into a list of 64-entry pixel lists."""
    if raw[:4] != b"RGCN":
        raise ValueError("not an NCGR")
    body = raw[NCGR_DATA_OFFSET:]
    tiles = []
    for t in range(len(body) // 32):
        px = []
        for byte in body[t * 32:(t + 1) * 32]:
            px.append(byte & 15)
            px.append(byte >> 4)
        tiles.append(px)
    return tiles


def ncgr_replace_tiles(raw, tiles):
    """Return raw with the pixel data replaced by ``tiles`` (same tile count)."""
    body = bytearray()
    for px in tiles:
        for i in range(0, 64, 2):
            body.append(px[i] | px[i + 1] << 4)
    if len(body) != len(raw) - NCGR_DATA_OFFSET:
        raise ValueError("tile count changed")
    return raw[:NCGR_DATA_OFFSET] + bytes(body)


# --- NCLR (RLCN) ------------------------------------------------------------

NCLR_DATA_OFFSET = 0x28


def bgr555(rgb):
    r, g, b = rgb
    return (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10


def nclr_colors(raw):
    count = (len(raw) - NCLR_DATA_OFFSET) // 2
    return [struct.unpack_from("<H", raw, NCLR_DATA_OFFSET + 2 * i)[0] for i in range(count)]


def nclr_set_colors(raw, updates):
    """``updates`` maps color index -> 15-bit BGR value."""
    out = bytearray(raw)
    for idx, value in updates.items():
        struct.pack_into("<H", out, NCLR_DATA_OFFSET + 2 * idx, value)
    return bytes(out)


# --- NSCR (RCSN) ------------------------------------------------------------

NSCR_DATA_OFFSET = 0x24


def nscr_entries(raw):
    return list(struct.unpack_from("<1024H", raw, NSCR_DATA_OFFSET))


def nscr_replace(raw, entries):
    out = bytearray(raw)
    struct.pack_into("<1024H", out, NSCR_DATA_OFFSET, *entries)
    return bytes(out)
