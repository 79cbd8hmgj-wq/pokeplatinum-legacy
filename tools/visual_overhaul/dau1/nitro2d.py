"""Bounded Nitro 2D parsers: NARC, NCLR, NCGR/NCBR, NCER, NANR, plus an OAM cell renderer.

Everything validates offsets/sizes against the buffer and raises ``DecodeError`` (never IndexError / struct.error).
Pure Python, deterministic.  Cell rendering is pixel-compatible with ``render_ranger_ncer_preview.render_cell``
(2D mapping, 32-tile stride) and additionally honours the NCER VRAM mapping mode for 1D-mapped banks.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .common import (MAX_CELL_PIXELS, MAX_ENTRIES, DecodeError, Reader, bgr555_to_rgb)

SHAPE_SIZE = {
    0: ((8, 8), (16, 16), (32, 32), (64, 64)),
    1: ((16, 8), (32, 8), (32, 16), (64, 32)),
    2: ((8, 16), (8, 32), (16, 32), (32, 64)),
}


# ------------------------------------------------------------------------------------------ NARC
@dataclass
class NarcMember:
    index: int
    name: str | None
    data: bytes


def _parse_fnt(fnt: bytes, count: int) -> dict[int, str]:
    """Best-effort name table (file id -> path).  Anonymous FNTs (the common case) yield {}."""
    names: dict[int, str] = {}
    if len(fnt) < 8:
        return names
    r = Reader(fnt, "FNT")
    root_sub, first_id, dir_count = r.u32(0), r.u16(4), r.u16(6)
    if root_sub == 4 or dir_count == 0 or dir_count > 4096:
        return names

    def walk(dir_index: int, prefix: str, depth: int) -> None:
        if depth > 8:
            raise DecodeError("LIMIT", "FNT too deep")
        base = 8 * dir_index
        pos, fid = r.u32(base), r.u16(base + 4)
        guard = 0
        while True:
            guard += 1
            if guard > MAX_ENTRIES:
                raise DecodeError("LIMIT", "FNT entries")
            ln = r.u8(pos)
            pos += 1
            if ln == 0:
                return
            name = r.raw(pos, ln & 0x7F).decode("ascii", "replace")
            pos += ln & 0x7F
            if ln & 0x80:
                sub = r.u16(pos) & 0xFFF
                pos += 2
                walk(sub, f"{prefix}{name}/", depth + 1)
            else:
                names[fid] = f"{prefix}{name}"
                fid += 1

    try:
        walk(0, "", 0)
    except DecodeError:
        return {}
    return {k: v for k, v in names.items() if k < count}


def parse_narc(data: bytes, what: str = "NARC") -> list[NarcMember]:
    r = Reader(data, what)
    r.magic(0, b"NARC")
    file_size, header_size, blocks = r.u32(8), r.u16(12), r.u16(14)
    if header_size != 16 or file_size > len(data) or file_size < 16:
        raise DecodeError("BAD_HEADER", f"{what}: size/header ({file_size},{header_size}) vs {len(data)}")
    pos = header_size
    r.magic(pos, b"BTAF")
    fatb_size, count = r.u32(pos + 4), r.u32(pos + 8)
    if count > MAX_ENTRIES or fatb_size != 12 + 8 * count:
        raise DecodeError("BAD_HEADER", f"{what}: FATB count={count} size={fatb_size}")
    entries = [(r.u32(pos + 12 + 8 * i), r.u32(pos + 16 + 8 * i)) for i in range(count)]
    fnt_pos = pos + fatb_size
    r.magic(fnt_pos, b"BTNF")
    fnt_size = r.u32(fnt_pos + 4)
    fimg = fnt_pos + fnt_size
    r.magic(fimg, b"GMIF")
    img_size = r.u32(fimg + 4)
    base = fimg + 8
    if fimg + img_size > len(data) or fnt_size < 16:
        raise DecodeError("BAD_HEADER", f"{what}: FNT/FIMG extents")
    names = _parse_fnt(r.raw(fnt_pos + 8, fnt_size - 8), count)
    members = []
    for i, (s, e) in enumerate(entries):
        if e < s or base + e > fimg + img_size:
            raise DecodeError("BAD_OFFSET", f"{what}: member {i} range {s:#x}..{e:#x} outside FIMG")
        members.append(NarcMember(i, names.get(i), data[base + s:base + e]))
    return members


# -------------------------------------------------------------------------------- Nitro blocks
class Blocks(dict):
    """{tag: (offset, size)} plus ``warnings`` for tolerated header quirks."""

    warnings: list


def nitro_blocks(data: bytes, magic: bytes, what: str) -> Blocks:
    """Return the block table of a Nitro file ("RLCN", "RGCN", "RECN", "RNAN", ...).

    The declared file size is *not* trusted (Ranger 2 NCLRs store a wrong value); blocks are bounded by the real buffer
    and the discrepancy is recorded in ``.warnings``.
    """
    r = Reader(data, what)
    r.magic(0, magic)
    if r.u16(4) != 0xFEFF:
        raise DecodeError("BAD_HEADER", f"{what}: byte-order mark")
    size, hsize, n = r.u32(8), r.u16(12), r.u16(14)
    if hsize < 16 or n == 0 or n > 8:
        raise DecodeError("BAD_HEADER", f"{what}: hdr={hsize} blocks={n}")
    out, pos = Blocks(), hsize
    out.warnings = [] if size == len(data) else [f"declared file size {size} != actual {len(data)}"]
    for k in range(n):
        if pos == len(data) and k > 0:        # declared trailing block (e.g. SOPC) was stripped from the file
            out.warnings.append(f"{n - k} declared block(s) missing at end of file")
            break
        tag = r.raw(pos, 4)
        bsize = r.u32(pos + 4)
        if bsize < 8 or pos + bsize > len(data):
            raise DecodeError("BAD_OFFSET", f"{what}: block {tag!r} size {bsize} outside {len(data)}")
        out[tag] = (pos, bsize)
        pos += bsize
    return out


# ------------------------------------------------------------------------------------- NCLR
@dataclass
class Palette:
    colors: list[int]          # BGR555 words
    bpp: int                   # 4 (16-colour rows) or 8 (256 colours)
    warnings: list = field(default_factory=list)

    @property
    def rows(self) -> int:
        return (len(self.colors) + 15) // 16

    def rgb(self) -> list[tuple[int, int, int]]:
        return [bgr555_to_rgb(c) for c in self.colors]


def parse_nclr(data: bytes, what: str = "NCLR") -> Palette:
    blocks = nitro_blocks(data, b"RLCN", what)
    if b"TTLP" not in blocks:
        raise DecodeError("BAD_HEADER", f"{what}: no TTLP block")
    pos, bsize = blocks[b"TTLP"]
    r = Reader(data, what)
    depth = r.u32(pos + 8) & 0xFFFF            # high half carries an unrelated flag in some HGSS files
    dsize = r.u32(pos + 16)
    doff = r.u32(pos + 20)
    start = pos + 8 + doff
    if depth not in (3, 4):
        raise DecodeError("UNSUPPORTED", f"{what}: palette depth {depth}")
    warns = list(blocks.warnings)
    if dsize == 0 or dsize % 2 or start >= len(data):
        raise DecodeError("BAD_OFFSET", f"{what}: palette data {dsize} at {start:#x} (file {len(data)})")
    if start + dsize > len(data):                       # header over-states the data: keep what is really there
        warns.append(f"palette data truncated: header says {dsize} bytes, {len(data) - start} present")
        dsize = (len(data) - start) // 2 * 2
    n = min(dsize // 2, 256 if depth == 4 else 4096)
    colors = [r.u16(start + 2 * i) for i in range(n)]
    return Palette(colors, 8 if depth == 4 else 4, warns)


# ------------------------------------------------------------------------------------- NCGR
@dataclass
class CharData:
    bpp: int
    tiles_x: int | None        # None when the header stores 0xFFFF / 0
    tiles_y: int | None
    scanned: bool
    mapping: int
    body: bytes
    tile_count: int
    sbi: bool = False

    def tiles(self, raster_w_tiles: int | None = None) -> tuple[int, list[bytes]]:
        """Return (sheet_width_tiles, tiles); each tile is 64 palette indices.  Scanned data needs a width."""
        tb = 32 if self.bpp == 4 else 64
        if not self.scanned:
            width = self.tiles_x if self.tiles_x else 32 if self.bpp == 4 else 16
            return width, [_tile_px(self.body[i * tb:(i + 1) * tb], self.bpp) for i in range(self.tile_count)]
        w = raster_w_tiles or self.tiles_x
        if not w or self.tile_count % w:
            raise DecodeError("UNSUPPORTED", f"scanned raster width {w} does not divide {self.tile_count} tiles")
        rows = self.tile_count // w
        stride = w * tb // 8                       # bytes per pixel row
        out = []
        for ty in range(rows):
            for tx in range(w):
                px = bytearray()
                for y in range(8):
                    s = (ty * 8 + y) * stride + tx * tb // 8
                    px += _row_px(self.body[s:s + tb // 8], self.bpp)
                out.append(bytes(px))
        return w, out


def _row_px(chunk: bytes, bpp: int) -> bytes:
    if bpp == 8:
        return bytes(chunk)
    out = bytearray()
    for b in chunk:
        out.append(b & 15)
        out.append(b >> 4)
    return bytes(out)


def _tile_px(raw: bytes, bpp: int) -> bytes:
    return _row_px(raw, bpp)


def parse_ncgr(data: bytes, what: str = "NCGR") -> CharData:
    blocks = nitro_blocks(data, b"RGCN", what)
    if b"RAHC" not in blocks:
        raise DecodeError("BAD_HEADER", f"{what}: no RAHC block")
    pos, _ = blocks[b"RAHC"]
    r = Reader(data, what)
    ty, tx = r.u16(pos + 8), r.u16(pos + 10)
    fmt, mapping, scan, dsize, doff = r.u32(pos + 12), r.u32(pos + 16), r.u32(pos + 20), r.u32(pos + 24), r.u32(pos + 28)
    if fmt not in (3, 4):
        raise DecodeError("UNSUPPORTED", f"{what}: character format {fmt} (only 4bpp/8bpp)")
    bpp = 4 if fmt == 3 else 8
    tb = 32 if bpp == 4 else 64
    start = pos + 8 + doff
    if start + dsize > len(data) or dsize % tb:
        raise DecodeError("BAD_OFFSET", f"{what}: char data {dsize} at {start:#x} (tile {tb})")
    count = dsize // tb
    if tx not in (0, 0xFFFF) and ty not in (0, 0xFFFF) and tx * ty != count:
        raise DecodeError("BAD_HEADER", f"{what}: geometry {tx}x{ty} != {count} tiles")
    return CharData(bpp, None if tx in (0, 0xFFFF) else tx, None if ty in (0, 0xFFFF) else ty,
                    scan == 1, mapping, data[start:start + dsize], count)


# ------------------------------------------------------------------------------------- NCER
Oam = tuple[int, int, int]


@dataclass
class CellBank:
    mapping: int                          # NCER VRAM mapping mode (0 = 2D, 0x10.. = 1D 32K..256K)
    cells: list[list[Oam]]
    has_extended: bool
    has_vram_transfer: bool

    def oam_total(self) -> int:
        return sum(len(c) for c in self.cells)


def parse_ncer(data: bytes, what: str = "NCER") -> CellBank:
    blocks = nitro_blocks(data, b"RECN", what)
    if b"KBEC" not in blocks:
        raise DecodeError("BAD_HEADER", f"{what}: no KBEC block")
    pos, bsize = blocks[b"KBEC"]
    end = pos + bsize
    r = Reader(data, what)
    count, attr = r.u16(pos + 8), r.u16(pos + 10)
    cell_off, mapping, vram_off = r.u32(pos + 12), r.u32(pos + 16), r.u32(pos + 20)
    if count > MAX_ENTRIES:
        raise DecodeError("LIMIT", f"{what}: {count} cells")
    ext = bool(attr & 1)
    stride = 16 if ext else 8
    table = pos + 8 + cell_off
    oam_base = table + count * stride
    if oam_base > end:
        raise DecodeError("BAD_OFFSET", f"{what}: cell table runs past block")
    cells = []
    for i in range(count):
        e = table + i * stride
        n, rel = r.u16(e), r.u32(e + 4)
        s = oam_base + rel
        if s + n * 6 > end:
            raise DecodeError("BAD_OFFSET", f"{what}: cell {i} OAM range {s:#x}+{n * 6} exceeds block")
        cells.append([(r.u16(s + 6 * k), r.u16(s + 6 * k + 2), r.u16(s + 6 * k + 4)) for k in range(n)])
    return CellBank(mapping, cells, ext, bool(vram_off))


def oam_geometry(oam: Oam):
    a0, a1, a2 = oam
    shape, size = (a0 >> 14) & 3, (a1 >> 14) & 3
    if shape not in SHAPE_SIZE:
        raise DecodeError("BAD_OAM", f"OAM shape {shape}")
    w, h = SHAPE_SIZE[shape][size]
    x, y = a1 & 0x1FF, a0 & 0xFF
    return {
        "w": w, "h": h,
        "x": x - 0x200 if x >= 0x100 else x,
        "y": y - 0x100 if y >= 0x80 else y,
        "tile": a2 & 0x3FF, "pal": a2 >> 12,
        "affine": bool(a0 & 0x100), "disabled": bool(a0 & 0x200) and not (a0 & 0x100),
        "hflip": bool(a1 & 0x1000) and not (a0 & 0x100), "vflip": bool(a1 & 0x2000) and not (a0 & 0x100),
        "color256": bool(a0 & 0x2000), "mode": (a0 >> 10) & 3,
    }


# ------------------------------------------------------------------------------------- NANR
@dataclass
class AnimBank:
    sequences: list[list[tuple[int, int]]]       # per sequence: [(cell index, duration frames)]
    total_frames: int


def parse_nanr(data: bytes, what: str = "NANR") -> AnimBank:
    blocks = nitro_blocks(data, b"RNAN", what)
    if b"KNBA" not in blocks:
        raise DecodeError("BAD_HEADER", f"{what}: no KNBA block")
    pos, bsize = blocks[b"KNBA"]
    end = pos + bsize
    r = Reader(data, what)
    nseq, nfrm = r.u16(pos + 8), r.u16(pos + 10)
    seq_off, frm_off, dat_off = r.u32(pos + 12), r.u32(pos + 16), r.u32(pos + 20)
    if nseq > MAX_ENTRIES or nfrm > MAX_ENTRIES:
        raise DecodeError("LIMIT", f"{what}: {nseq} sequences / {nfrm} frames")
    base = pos + 8
    seqs = []
    for i in range(nseq):
        e = base + seq_off + 16 * i
        n, first = r.u16(e), r.u32(e + 12)
        out = []
        for k in range(n):
            f = base + frm_off + first + 8 * k
            if f + 8 > end:
                raise DecodeError("BAD_OFFSET", f"{what}: frame record outside block")
            d, dur = r.u32(f), r.u16(f + 4)
            cell_ref = base + dat_off + d
            if cell_ref + 2 > end:
                raise DecodeError("BAD_OFFSET", f"{what}: frame data outside block")
            out.append((r.u16(cell_ref), dur))
        seqs.append(out)
    return AnimBank(seqs, nfrm)


# --------------------------------------------------------------------------------- rendering
def boundary_unit(char_mapping: int) -> int | None:
    """Bytes per OAM tile index step for a 1D-mapped NCGR (GXOBJVRAMMode), or None for 2D mapping.

    NCGR stores the GXOBJVRAMMode: 0 = 2D; 0x10 | (shift << 20) = 1D with a (32 << shift)-byte boundary.
    """
    if char_mapping & 0x10:
        return 32 << ((char_mapping >> 20) & 3)
    return None


def _tile_lookup(chars: list[bytes], sheet_w: int, char_mapping: int, bpp: int):
    """Return f(obj_tile, ty, tx, obj_w_tiles) -> 64-index tile (or None when outside the data)."""
    unit = boundary_unit(char_mapping)
    tb = 32 if bpp == 4 else 64

    def lookup(tile: int, ty: int, tx: int, wt: int):
        if unit is None:                                   # 2D mapping: fixed 32-tile (4bpp) / 16-tile (8bpp) rows
            stride = 32 if bpp == 4 else 16
            row, col = divmod(tile, stride)
            col += tx
            if col >= sheet_w:
                return None
            idx = (row + ty) * sheet_w + col
        else:                                              # 1D mapping: contiguous row-major, boundary = unit bytes
            idx = (tile * unit) // tb + ty * wt + tx
        return chars[idx] if 0 <= idx < len(chars) else None

    return lookup


@dataclass
class RenderedCell:
    width: int
    height: int
    pixels: bytes                  # 1 byte/pixel palette index (palette row folded in for 4bpp); 0 = transparent
    oam_count: int
    tiles_touched: int             # distinct char tiles referenced (tile-budget estimate)
    unmapped_tiles: int            # tile references outside the character data
    affine_objects: int
    blank: bool = field(default=False)


def render_cell(oams: list[Oam], chars: list[bytes], sheet_w: int, char_mapping: int, bpp: int) -> RenderedCell:
    geoms = [oam_geometry(o) for o in oams]
    objs = [g for g in geoms if not g["disabled"]]
    affine = sum(1 for g in objs if g["affine"])
    if not objs:
        return RenderedCell(1, 1, b"\0", len(oams), 0, 0, 0, True)
    lookup = _tile_lookup(chars, sheet_w, char_mapping, bpp)
    min_x = min(g["x"] for g in objs)
    min_y = min(g["y"] for g in objs)
    max_x = max(g["x"] + g["w"] for g in objs)
    max_y = max(g["y"] + g["h"] for g in objs)
    w, h = max_x - min_x, max_y - min_y
    if w * h > MAX_CELL_PIXELS:
        raise DecodeError("LIMIT", f"cell {w}x{h}")
    canvas = bytearray(w * h)
    touched, unmapped = set(), 0
    for g in objs:
        wt, ht = g["w"] // 8, g["h"] // 8
        obj_bpp = 8 if g["color256"] else bpp
        for ty in range(ht):
            for tx in range(wt):
                sty = ht - 1 - ty if g["vflip"] else ty
                stx = wt - 1 - tx if g["hflip"] else tx
                tile = lookup(g["tile"], sty, stx, wt)
                if tile is None:
                    unmapped += 1
                    continue
                touched.add((g["tile"], sty, stx, wt))
                for iy in range(8):
                    sy = 7 - iy if g["vflip"] else iy
                    for ix in range(8):
                        sx = 7 - ix if g["hflip"] else ix
                        v = tile[sy * 8 + sx]
                        if not v:
                            continue
                        if obj_bpp == 4:
                            v += g["pal"] * 16
                        canvas[(g["y"] - min_y + ty * 8 + iy) * w + (g["x"] - min_x + tx * 8 + ix)] = v & 0xFF
    return RenderedCell(w, h, bytes(canvas), len(oams), len(touched), unmapped, affine, not any(canvas))


def infer_raster_width(cells: list[list[Oam]], total_tiles: int) -> int:
    """Row width (tiles) for scanline ('NCBR') data, which is not stored in the file (see render_ranger_ncer_preview)."""
    cols = rows = 1
    for oams in cells:
        for o in oams:
            try:
                g = oam_geometry(o)
            except DecodeError:
                continue
            cols = max(cols, g["tile"] % 32 + g["w"] // 8)
            rows = max(rows, g["tile"] // 32 + g["h"] // 8)
    for width in (32, 16, 8, 4, 2, 1):
        if total_tiles % width == 0 and width >= cols and total_tiles // width >= rows:
            return width
    return 32
