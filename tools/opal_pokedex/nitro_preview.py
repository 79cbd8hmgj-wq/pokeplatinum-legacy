#!/usr/bin/env python3
"""Minimal Nitro graphics reader/renderer used by the Opal Pokedex tooling.

Supports LZ77 (type 0x10) compressed or raw NCGR (RGCN), NSCR (RCSN) and
NCLR (RLCN) members, and renders a tilemap + tileset + palette bank to a PNG
so Pokedex screens can be audited and previews generated without an emulator.
No third-party dependencies (PNG is written with zlib).
"""
import struct
import sys
import zlib


def lz10_decompress(data: bytes) -> bytes:
    if not data or data[0] != 0x10:
        return data
    size = int.from_bytes(data[1:4], "little")
    out = bytearray()
    pos = 4
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b0, b1 = data[pos], data[pos + 1]
                pos += 2
                length = (b0 >> 4) + 3
                disp = (((b0 & 0xF) << 8) | b1) + 1
                for _ in range(length):
                    out.append(out[-disp])
            else:
                out.append(data[pos])
                pos += 1
    return bytes(out[:size])


def _sections(data: bytes, magic: bytes):
    if data[:4] != magic:
        raise ValueError(f"expected {magic!r}, got {data[:4]!r}")
    nsec = struct.unpack_from("<H", data, 0x0E)[0]
    pos = struct.unpack_from("<H", data, 0x0C)[0]
    secs = {}
    for _ in range(nsec):
        tag = data[pos:pos + 4]
        size = struct.unpack_from("<I", data, pos + 4)[0]
        secs[tag] = data[pos + 8:pos + size]
        pos += size
    return secs


def read_ncgr(data: bytes):
    """Return (bpp, tiles[list of 64-byte pixel arrays])."""
    data = lz10_decompress(data)
    secs = _sections(data, b"RGCN")
    char = secs[b"RAHC"]
    h, w, depth = struct.unpack_from("<HHI", char, 0)
    bpp = 4 if depth == 3 else 8
    flag = struct.unpack_from("<I", char, 0x0C)[0]
    size = struct.unpack_from("<I", char, 0x10)[0]
    raw = char[0x18:0x18 + size]
    tiles = []
    step = 32 if bpp == 4 else 64
    for i in range(0, len(raw), step):
        t = raw[i:i + step]
        if len(t) < step:
            break
        if bpp == 4:
            px = bytearray()
            for b in t:
                px.append(b & 0xF)
                px.append(b >> 4)
            tiles.append(bytes(px))
        else:
            tiles.append(bytes(t))
    return bpp, tiles


def read_nscr(data: bytes):
    """Return (width_tiles, height_tiles, entries[list of u16])."""
    data = lz10_decompress(data)
    secs = _sections(data, b"RCSN")
    scrn = secs[b"NRCS"]
    w, h = struct.unpack_from("<HH", scrn, 0)
    size = struct.unpack_from("<I", scrn, 0x08)[0]
    raw = scrn[0x0C:0x0C + size]
    entries = list(struct.unpack("<%dH" % (len(raw) // 2), raw))
    return w // 8, h // 8, entries


def read_nclr(data: bytes):
    """Return list of (r,g,b) 8-bit colours."""
    data = lz10_decompress(data)
    secs = _sections(data, b"RLCN")
    pltt = secs[b"TTLP"]
    size = struct.unpack_from("<I", pltt, 0x08)[0]
    raw = pltt[0x10:0x10 + size]
    cols = []
    for (v,) in struct.iter_unpack("<H", raw[: len(raw) // 2 * 2]):
        r, g, b = v & 31, (v >> 5) & 31, (v >> 10) & 31
        cols.append((r * 255 // 31, g * 255 // 31, b * 255 // 31))
    return cols


def write_png(path, width, height, rgb: bytes):
    def chunk(tag, payload):
        c = struct.pack(">I", len(payload)) + tag + payload
        return c + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + rgb[y * width * 3:(y + 1) * width * 3] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def render_screen(path, nscr, ncgr, nclr, default_bank=0, char_offset=0):
    w, h, entries = read_nscr(open(nscr, "rb").read())
    bpp, tiles = read_ncgr(open(ncgr, "rb").read())
    pal = read_nclr(open(nclr, "rb").read())
    img = bytearray(w * 8 * h * 8 * 3)
    for ty in range(h):
        for tx in range(w):
            e = entries[ty * w + tx]
            idx = (e & 0x3FF) - char_offset
            hf, vf = (e >> 10) & 1, (e >> 11) & 1
            bank = (e >> 12) & 0xF
            if not 0 <= idx < len(tiles):
                continue
            t = tiles[idx]
            for py in range(8):
                for px in range(8):
                    sx = 7 - px if hf else px
                    sy = 7 - py if vf else py
                    ci = t[sy * 8 + sx]
                    if bpp == 4:
                        ci = ci + 16 * (bank if bank < len(pal) // 16 else default_bank)
                    col = pal[ci] if ci < len(pal) else (255, 0, 255)
                    o = ((ty * 8 + py) * w * 8 + tx * 8 + px) * 3
                    img[o:o + 3] = bytes(col)
    write_png(path, w * 8, h * 8, bytes(img))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("usage: nitro_preview.py out.png map.NSCR[.lz] tiles.NCGR[.lz] pal.NCLR")
    render_screen(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
