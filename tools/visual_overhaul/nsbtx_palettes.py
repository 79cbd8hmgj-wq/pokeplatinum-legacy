"""Minimal read-only NSBTX palette/texture-info reader used by the G7.7 audit.

Only parses what the cohesion audit needs: palette names + BGR555 colours and the
texture name/dimension table. Never writes.
"""
from __future__ import annotations

import struct


def _u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def _u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def _info_block(b, off):
    """Parse an NNS 3D info block; returns (names, entries-bytes list)."""
    count = b[off + 1]
    p = off + _u16(b, off + 6)  # block hdr(4) + tree hdr(4) + patricia nodes
    entry_size = (_u16(b, p + 2) - 4) // count
    p += 4
    entries = [bytes(b[p + i * entry_size:p + (i + 1) * entry_size]) for i in range(count)]
    p += count * entry_size
    names = [bytes(b[p + i * 16:p + (i + 1) * 16]).split(b"\0")[0].decode("ascii") for i in range(count)]
    return names, entries


def read_palettes(data: bytes) -> dict[str, list[int]]:
    assert data[:4] == b"BTX0", "not an NSBTX"
    tex0 = _u32(data, 16)
    assert data[tex0:tex0 + 4] == b"TEX0"
    size = _u32(data, tex0 + 4)
    block = data[tex0:tex0 + size]
    pal_size = (_u32(block, 0x30) & 0x7FFFFFFF) << 3
    pal_info = _u32(block, 0x34)
    pal_data = _u32(block, 0x38)
    names, entries = _info_block(block, pal_info)
    offs = [_u16(e, 0) << 3 for e in entries]
    order = sorted(set(offs) | {pal_size})
    out = {}
    for name, o in zip(names, offs):
        end = order[order.index(o) + 1]
        n = (end - o) // 2
        out[name] = list(struct.unpack_from(f"<{n}H", block, pal_data + o))
    return out


def read_textures(data: bytes) -> dict[str, tuple[int, int, int]]:
    """name -> (width, height, format)."""
    tex0 = _u32(data, 16)
    block = data[tex0:_u32(data, tex0 + 4) + tex0]
    info_off = _u16(block, 0x0E)
    names, entries = _info_block(block, info_off)
    out = {}
    for name, e in zip(names, entries):
        params = _u32(e, 0)
        fmt = (params >> 26) & 7
        w = 8 << ((params >> 20) & 7)
        h = 8 << ((params >> 23) & 7)
        out[name] = (w, h, fmt)
    return out


def decode_textures(data: bytes):
    """Yield (name, w, h, fmt, indices[w*h], alphaless) for paletted formats 1-4,6.
    Compressed (5) and direct (7) formats are skipped. Read-only; used for review sheets."""
    tex0 = _u32(data, 16)
    block = data[tex0:_u32(data, tex0 + 4) + tex0]
    tex_data = _u32(block, 0x14)
    names, entries = _info_block(block, _u16(block, 0x0E))
    for name, e in zip(names, entries):
        params = _u32(e, 0)
        fmt = (params >> 26) & 7
        w = 8 << ((params >> 20) & 7)
        h = 8 << ((params >> 23) & 7)
        off = tex_data + ((params & 0xFFFF) << 3)
        n = w * h
        if fmt == 2:
            raw = block[off:off + n // 4]
            idx = [(raw[i // 4] >> (2 * (i % 4))) & 3 for i in range(n)]
        elif fmt == 3:
            raw = block[off:off + n // 2]
            idx = [(raw[i // 2] >> (4 * (i % 2))) & 15 for i in range(n)]
        elif fmt == 4:
            idx = list(block[off:off + n])
        elif fmt == 1:
            idx = [b & 31 for b in block[off:off + n]]
        elif fmt == 6:
            idx = [b & 7 for b in block[off:off + n]]
        else:
            continue
        yield name, w, h, fmt, idx
