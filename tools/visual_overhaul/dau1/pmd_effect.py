"""Pokemon Mystery Dungeon: Explorers of Sky - ``files/EFFECT/effect.bin`` decoder.

Container:  u32 0, u32 count, then count * (u32 offset, u32 length); entries are mostly SIR0-wrapped "effect WAN"
sprites (entries 0..267), plus screen-effect tables and two non-SIR0 blobs.

Effect WAN layout (little endian; all pointers are SIR0 content-relative absolute offsets):

  header      : u32 ptr_anim_info, u32 ptr_image_info, u16 image_type (1..3), u16 unk
  image info  : u32 ptr_image_table, u32 ptr_palette_info, u16 unk, u16 is256, u16 unk, u16 image_count
  palette info: u32 ptr_palette_data, u16 unk, u16 colour_count, u16 unk, u16 palette_flags (0x1xx: offset by low nibble)
  palette data: 4 bytes per colour (R, G, B, pad)
  image table : image_count * u32 ptr -> per image a list of pixel strips
                  strip = u32 ptr_pixels, u16 byte_count, u16 unk, u32 z_sort ; a strip with (0,0) ends the list
                  a strip whose ptr field is not in the SIR0 relocation list is a run of zeroes (blank strip)
  anim info   : u32 ptr_metaframe_table, u32 ptr_offset_table, u32 ptr_anim_group_table, u16 group_count
  meta frame  : 10 bytes: s16 image_index?, u16 unk, u8 flag(0 = drawn in front) ... see MetaPiece below
  anim group  : u32 ptr_sequence_table, u16 length, u16 pad ; sequence = u32 ptr list -> frames of
                  (u16 duration, u16 meta_frame, s16 off_x, s16 off_y, u16 shadow_x, u16 shadow_y), 0 duration ends

The format knowledge comes from public community documentation of the game's own file layout and was
cross-checked against an independent reference implementation (see docs/visual_overhaul/asset_unlock/PROVENANCE.md);
this module is an original implementation.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

from .common import DECODED, STRUCTURAL_ONLY, UNSUPPORTED, DecodeError, Reader, sha256_bytes
from .render import Frame

DIM_TABLE = [(1, 1), (2, 2), (4, 4), (8, 8), (2, 1), (4, 1), (4, 2), (8, 4), (1, 2), (1, 4), (2, 4), (4, 8)]
CENTER = (256, 508)            # sprite-space origin of the effect coordinate plane (512 x 1024)
MAX_PIECES = 4096


# ------------------------------------------------------------------------------------------ container
def parse_pack(data: bytes) -> list[tuple[int, int]]:
    """Return [(offset, length)] for every entry of a PMD pack file (effect.bin, monster.bin ...)."""
    r = Reader(data, "pack")
    if r.u32(0) != 0:
        raise DecodeError("BAD_HEADER", "pack file must start with u32 0")
    n = r.u32(4)
    if n == 0 or n > 65536 or 8 + 8 * n > len(data):
        raise DecodeError("BAD_HEADER", f"pack entry count {n}")
    out = []
    for i in range(n):
        o, l = r.u32(8 + 8 * i), r.u32(12 + 8 * i)
        if o + l > len(data):
            raise DecodeError("BAD_OFFSET", f"pack entry {i}: {o:#x}+{l:#x} beyond {len(data):#x}")
        out.append((o, l))
    return out


# ------------------------------------------------------------------------------------------ SIR0
@dataclass
class Sir0:
    content_ptr: int
    relocations: set[int]          # offsets (within the file) that hold pointers


def parse_sir0(data: bytes) -> Sir0:
    r = Reader(data, "SIR0")
    r.magic(0, b"SIR0")
    content, plist = r.u32(4), r.u32(8)
    if content >= len(data) or plist >= len(data) or content < 16:
        raise DecodeError("BAD_OFFSET", f"SIR0 content/list pointers {content:#x}/{plist:#x} vs {len(data):#x}")
    rel, pos, cur, guard = set(), plist, 0, 0
    while True:
        guard += 1
        if guard > 1_000_000:
            raise DecodeError("LIMIT", "SIR0 relocation list too long")
        val, chunks = 0, 0
        while True:
            b = r.u8(pos)
            pos += 1
            val = (val << 7) | (b & 0x7F)
            chunks += 1
            if not (b & 0x80):
                break
            if chunks > 5:
                raise DecodeError("BAD_HEADER", "SIR0 relocation varint too long")
        if val == 0:
            break
        cur += val
        rel.add(cur)
    return Sir0(content, rel)


# ------------------------------------------------------------------------------------------ model
@dataclass
class MetaPiece:
    image: int
    palette: int
    w_tiles: int
    h_tiles: int
    x: int
    y: int
    hflip: bool
    vflip: bool
    front: bool


@dataclass
class EffectWan:
    image_type: int
    is256: int
    palettes: list[list[tuple[int, int, int]]]       # rows of RGB (16 or 256 entries)
    images: list[bytes]                              # per image: concatenated pixel indices (one byte per pixel)
    metaframes: list[list[MetaPiece]]
    sequences: list[list[tuple[int, int]]]           # [(metaframe index, duration)]
    atlas: tuple[int, int] | None = None             # type-3 sprites: (width, height) of the single atlas image
    palette_offset: int = 0
    warnings: list[str] = field(default_factory=list)

    def block_stream(self) -> bytes:
        """256-colour sprites: images padded to 128-byte blocks and concatenated (pieces address it in blocks)."""
        out = bytearray()
        for img in self.images:
            out += img
            out += bytes(-len(out) % 128)
        return bytes(out)


def parse_effect_wan(data: bytes) -> EffectWan:
    sir = parse_sir0(data)
    r = Reader(data, "effect WAN")
    hdr = sir.content_ptr
    ptr_anim, ptr_img = r.u32(hdr), r.u32(hdr + 4)
    itype = r.u16(hdr + 8)
    if ptr_anim == 0 and ptr_img == 0:
        raise DecodeError("UNSUPPORTED", "null anim/image pointers (not a sprite)")
    if itype < 1 or itype > 3:
        raise DecodeError("UNSUPPORTED", f"image_type {itype} is not an effect sprite (expected 1..3)")
    for name, p in (("anim info", ptr_anim), ("image info", ptr_img)):
        if p >= len(data):
            raise DecodeError("BAD_OFFSET", f"{name} pointer {p:#x} beyond {len(data):#x}")
    warns: list[str] = []
    palettes: list[list[tuple[int, int, int]]] = []
    images: list[bytes] = []
    is256 = 0
    pal_off = 0
    atlas = None
    if ptr_img:
        ptr_tab, ptr_pal = r.u32(ptr_img), r.u32(ptr_img + 4)
        is256 = r.u16(ptr_img + 10)
        count = r.u16(ptr_img + 14)
        if ptr_tab == 0 or ptr_pal == 0:
            raise DecodeError("BAD_OFFSET", "null table/palette pointer in image info")
        if is256 not in (0, 1, 4):
            raise DecodeError("UNSUPPORTED", f"colour mode {is256}")
        ptr_colors = r.u32(ptr_pal)
        flags = r.u16(ptr_pal + 10)
        pal_off = flags & 15 if (flags >> 8) else 0
        if ptr_colors == 0 or ptr_colors > ptr_pal:
            raise DecodeError("BAD_OFFSET", f"palette data pointer {ptr_colors:#x} vs info {ptr_pal:#x}")
        total = (ptr_pal - ptr_colors) // 4              # the palette block ends where its info record begins
        per_row = 16
        for row in range(total // per_row):
            rows = []
            for c in range(per_row):
                rr, gg, bb = r.raw(ptr_colors + 4 * (row * per_row + c), 3)
                rows.append(((rr >> 3) * 255 // 31, (gg >> 3) * 255 // 31, (bb >> 3) * 255 // 31))   # DS 5-bit channels
            palettes.append(rows)
        if not palettes:
            raise DecodeError("BAD_OFFSET", "palette block holds no complete 16-colour row")
        if is256 == 4:
            raise DecodeError("UNSUPPORTED", "colour mode 4 (single known sprite, layout unresolved)")
        if count == 0 or count > 4096:
            raise DecodeError("BAD_HEADER", f"image count {count}")
        ptrs = [r.u32(ptr_tab + 4 * i) for i in range(count)]
        if itype == 3:
            p0 = ptrs[0]
            src, aw, ah = r.u32(p0), r.u16(p0 + 4), r.u16(p0 + 6)
            if src >= p0 or aw == 0 or ah == 0:
                raise DecodeError("BAD_OFFSET", f"atlas source {src:#x} / {aw}x{ah}")
            raw = r.raw(src, p0 - src)
            images.append(_unpack(raw, is256))
            atlas = (aw, ah)
        else:
            for pi, p in enumerate(ptrs):
                strips, q, guard = [], p, 0
                while True:
                    guard += 1
                    if guard > 4096:
                        raise DecodeError("LIMIT", f"image {pi}: strip list too long")
                    src, amt = r.u32(q), r.u16(q + 4)
                    if src == 0 and amt == 0:
                        break
                    if q in sir.relocations:
                        raw = r.raw(src, amt)
                    else:
                        raw = bytes(amt)                                # blank strip
                    strips.append(_unpack(raw, is256))
                    q += 12
                images.append(b"".join(strips))
    metaframes: list[list[MetaPiece]] = []
    sequences: list[list[tuple[int, int]]] = []
    if ptr_anim:
        ptr_mf, ptr_groups, ngroups = r.u32(ptr_anim), r.u32(ptr_anim + 8), r.u16(ptr_anim + 12)
        if ptr_mf == 0 or ptr_groups == 0 or ptr_groups < ptr_mf:
            raise DecodeError("BAD_OFFSET", f"anim table pointers {ptr_mf:#x}/{ptr_groups:#x}")
        seq_ptrs = []
        for g in range(ngroups):
            base, length = r.u32(ptr_groups + 8 * g), r.u16(ptr_groups + 8 * g + 4)
            seq_ptrs.extend(r.u32(base + 4 * k) for k in range(length))
        first_seq_table = r.u32(ptr_groups) if ngroups else ptr_groups
        end_mf = min(first_seq_table if first_seq_table > ptr_mf else ptr_groups, len(data))
        mf_ptrs = [r.u32(p) for p in range(ptr_mf, end_mf - 3, 4)]
        if len(mf_ptrs) > MAX_PIECES:
            raise DecodeError("LIMIT", f"{len(mf_ptrs)} metaframes")
        if itype != 3:
            for mp in mf_ptrs:
                pieces, q, guard = [], mp, 0
                while True:
                    guard += 1
                    if guard > 256:
                        raise DecodeError("LIMIT", "metaframe has >256 pieces")
                    draw = r.u8(q + 3)
                    ydata, xdata = r.u16(q + 4), r.u16(q + 6)
                    block, pal = r.u8(q + 8), r.u8(q + 9) // 16
                    flags = xdata // 2048
                    dim = DIM_TABLE[(ydata // 16384) * 4 + flags // 8] if (ydata // 16384) * 4 + flags // 8 < 12 else None
                    if dim is None:
                        raise DecodeError("BAD_OAM", f"invalid piece dimension code {(ydata // 16384, flags // 8)}")
                    pieces.append(MetaPiece(block, pal, dim[0], dim[1], xdata % 512, ydata % 1024,
                                            bool(flags // 2 % 2), bool(flags // 4 % 2), draw == 0))
                    q += 10
                    if flags % 2 == 1:
                        break
                metaframes.append(pieces)
        for sp in seq_ptrs:
            seq, q, guard = [], sp, 0
            while True:
                guard += 1
                if guard > 4096:
                    raise DecodeError("LIMIT", "animation sequence too long")
                dur, idx = r.u16(q), r.u16(q + 2)
                if dur == 0:
                    break
                seq.append((idx, dur))
                q += 12
            sequences.append(seq)
    return EffectWan(itype, is256, palettes, images, metaframes, sequences, atlas, pal_off, warns)


def _unpack(raw: bytes, is256: int) -> bytes:
    if is256:
        return bytes(raw)
    out = bytearray(len(raw) * 2)
    out[0::2] = bytes(b & 15 for b in raw)
    out[1::2] = bytes(b >> 4 for b in raw)
    return bytes(out)


# ------------------------------------------------------------------------------------------ render
def _piece_pixels(wan: EffectWan, p: MetaPiece) -> bytes | None:
    """Index data of one piece as a (w*8) x (h*8) row-major bitmap (tiles are laid out row-major), or None if short."""
    need = p.w_tiles * p.h_tiles * 64
    if wan.is256:
        stream = wan._stream if hasattr(wan, "_stream") else None
        if stream is None:
            stream = wan._stream = wan.block_stream()
        base = p.image * 128
        if base >= len(stream):
            raise DecodeError("BAD_OFFSET", f"piece block {p.image} beyond {len(stream) // 128} blocks")
        src = stream[base:base + need]
        if len(src) < need:
            raise DecodeError("TRUNCATED", f"block {p.image}: {len(src)} px left, piece needs {need}")
    else:
        if p.image >= len(wan.images):
            raise DecodeError("BAD_OFFSET", f"piece references image {p.image} of {len(wan.images)}")
        src = wan.images[p.image]
        if len(src) < need:
            raise DecodeError("TRUNCATED", f"image {p.image} holds {len(src)} px, piece needs {need}")
    W = p.w_tiles * 8
    out = bytearray(W * p.h_tiles * 8)
    for ty in range(p.h_tiles):
        for tx in range(p.w_tiles):
            t = (ty * p.w_tiles + tx) * 64
            for y in range(8):
                s = t + y * 8
                d = (ty * 8 + y) * W + tx * 8
                out[d:d + 8] = src[s:s + 8]
    return bytes(out)


def resolve_row(wan: EffectWan, row: int) -> int | None:
    """Map a piece's palette selector to a row of the file palette.

    Selectors below the row count index the file rows directly; selectors in [base, base + rows) (base = the low nibble
    of the palette-info flags, 13 for most sprites) address them relative to the sprite's palette base bank.  Any other
    selector refers to a palette the file does not define (a run-time bank) and is reported, never guessed.
    """
    n = len(wan.palettes)
    if 0 <= row < n:
        return row
    base = wan.palette_offset
    if base and base <= row < base + n:
        return row - base
    return None


def render_metaframe(wan: EffectWan, pieces: list[MetaPiece], box: tuple[int, int, int, int]) -> Frame | None:
    """Composite a metaframe into the (x0, y0, x1, y1) box (sprite-space).  Back pieces draw first."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    rgba = bytearray(w * h * 4)
    drew = False
    for p in sorted(pieces, key=lambda q: q.front):         # back (front=False) first, then front
        bm = _piece_pixels(wan, p)
        if bm is None:
            continue
        row = resolve_row(wan, p.palette)
        if row is None:
            raise DecodeError("BAD_PALETTE_INDEX", f"piece palette row {p.palette} of {len(wan.palettes)}")
        pal = wan.palettes[row]
        if wan.is256:                                     # values 16..31 address the 16 colours of the row
            pal = [(0, 0, 0)] * 16 + list(pal)
        pw, ph = p.w_tiles * 8, p.h_tiles * 8
        for py in range(ph):
            sy = ph - 1 - py if p.vflip else py
            for px in range(pw):
                sx = pw - 1 - px if p.hflip else px
                v = bm[sy * pw + sx]
                if not v:
                    continue
                if v >= len(pal) or (wan.is256 and v < 16):
                    raise DecodeError("BAD_PALETTE_INDEX", f"pixel index {v} outside the row's addressable range")
                dx, dy = p.x + px - x0, p.y + py - y0
                if 0 <= dx < w and 0 <= dy < h:
                    rgba[(dy * w + dx) * 4:(dy * w + dx) * 4 + 4] = bytes((*pal[v], 255))
                    drew = True
    return Frame(w, h, bytes(rgba)) if drew else None


def metaframe_box(pieces: list[MetaPiece]) -> tuple[int, int, int, int]:
    return (min(p.x for p in pieces), min(p.y for p in pieces),
            max(p.x + p.w_tiles * 8 for p in pieces), max(p.y + p.h_tiles * 8 for p in pieces))


@dataclass
class EffectResult:
    status: str
    reason: str | None = None
    frames: list[Frame] = field(default_factory=list)
    palette_rows: int = 0
    palette_colors: int = 0
    tile_budget: int | None = None
    oam_budget: int | None = None
    dimensions: dict | None = None
    metaframes: int = 0
    sequences: int = 0
    image_type: int | None = None
    warnings: list[str] = field(default_factory=list)
    blank_metaframes: int = 0
    invalid_metaframes: list[int] = field(default_factory=list)


def decode_effect_entry(data: bytes) -> EffectResult:
    if data[:4] != b"SIR0":
        return EffectResult(STRUCTURAL_ONLY, f"entry is not SIR0 (starts {data[:4].hex()}); screen-effect/auxiliary table, not a sprite")
    try:
        wan = parse_effect_wan(data)
    except DecodeError as e:
        status = UNSUPPORTED if e.code in ("UNSUPPORTED",) else UNSUPPORTED
        return EffectResult(status, f"{e.code}: {e.message}")
    res = EffectResult(DECODED, None, [], len(wan.palettes), max((len(p) for p in wan.palettes), default=0),
                       metaframes=len(wan.metaframes), sequences=len(wan.sequences), image_type=wan.image_type,
                       warnings=list(wan.warnings))
    if wan.image_type == 3:
        return _decode_atlas(wan, res)
    if not wan.images or not wan.metaframes:
        res.status, res.reason = STRUCTURAL_ONLY, "no image data or no metaframes"
        return res
    try:
        boxes = [metaframe_box(m) for m in wan.metaframes if m]
        gx0, gy0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
        gx1, gy1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
        if (gx1 - gx0) * (gy1 - gy0) > 1 << 20:
            raise DecodeError("LIMIT", f"effect extent {gx1 - gx0}x{gy1 - gy0}")
        used_images: set[int] = set()
        max_pieces = 0
        invalid: list[int] = []
        for mi, m in enumerate(wan.metaframes):
            if not m:
                continue
            try:
                f = render_metaframe(wan, m, metaframe_box(m))
            except DecodeError as e:
                if e.code != "BAD_PALETTE_INDEX":
                    raise
                invalid.append(mi)               # piece selects a palette row the file does not define
                continue
            if f is None:
                res.blank_metaframes += 1
                continue
            res.frames.append(f)
            max_pieces = max(max_pieces, len(m))
            used_images.update(p.image for p in m)
        res.invalid_metaframes = invalid
        if invalid:
            rows_used = sorted({p.palette for mi in invalid for p in wan.metaframes[mi] if resolve_row(wan, p.palette) is None})
            res.warnings.append(f"{len(invalid)} of {len(wan.metaframes)} metaframes select palette rows {rows_used} but the "
                                f"file defines {len(wan.palettes)} row(s); those metaframes are not counted")
    except DecodeError as e:
        res.status, res.reason, res.frames = UNSUPPORTED, f"{e.code}: {e.message}", []
        return res
    if not res.frames:
        if res.invalid_metaframes:
            res.status = UNSUPPORTED
            res.reason = ("every metaframe selects a palette row the file does not define (run-time palette bank); "
                          + res.warnings[-1])
        else:
            res.status, res.reason = STRUCTURAL_ONLY, "every metaframe renders blank"
        return res
    res.oam_budget = max_pieces
    res.tile_budget = (sum(len(wan.images[i]) // 64 for i in used_images if i < len(wan.images))
                       if not wan.is256 else len(wan.block_stream()) // 64)
    res.dimensions = {"min": [min(f.width for f in res.frames), min(f.height for f in res.frames)],
                      "max": [max(f.width for f in res.frames), max(f.height for f in res.frames)]}
    return res


def _decode_atlas(wan: EffectWan, res: EffectResult) -> EffectResult:
    aw, ah = wan.atlas
    px = wan.images[0]
    rows = max(len(px) // (aw * ah), 1)
    if not wan.palettes:
        res.status, res.reason = STRUCTURAL_ONLY, "atlas sprite without palette"
        return res
    pal = wan.palettes[0] if not wan.is256 else wan.palettes[0]
    h = rows * ah
    out = bytearray(aw * h * 4)
    for i in range(min(len(px), aw * h)):
        v = px[i]
        if v:
            if v >= len(pal):
                res.status, res.reason = UNSUPPORTED, f"BAD_PALETTE_INDEX: atlas pixel {v} beyond {len(pal)} colours"
                return res
            out[4 * i:4 * i + 4] = bytes((*pal[v], 255))
    f = Frame(aw, h, bytes(out))
    if not f.opaque_pixels:
        res.status, res.reason = STRUCTURAL_ONLY, "atlas renders blank"
        return res
    res.frames = [f]
    res.dimensions = {"min": [aw, h], "max": [aw, h]}
    res.tile_budget = len(px) // 64
    res.warnings.append("type-3 atlas: metaframes not decoded (layout unresolved); whole atlas rendered")
    return res


def entry_hash(data: bytes) -> str:
    return sha256_bytes(data)
