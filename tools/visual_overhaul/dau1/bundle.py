"""Nitro cell-bundle decoding: pair NCER + NCGR/NCBR + NCLR (+ NANR), render every cell, validate, measure budgets.

``decode_cell_bundle`` is the single place that decides whether a bundle is truly DECODED:
 * every cell renders without error;
 * no OAM references a tile outside the paired character data;
 * no pixel references a palette entry outside the paired NCLR;
 * at least one cell has visible pixels.
Anything else is reported with an evidence-bearing reason and a non-DECODED status.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import nitro2d as n2
from .common import DECODED, STRUCTURAL_ONLY, UNSUPPORTED, DecodeError, lz_decompress
from .render import Frame, frames_hash, indexed_to_frame


@dataclass
class BundleResult:
    status: str
    reason: str | None = None
    frames: list[Frame] = field(default_factory=list)
    palette_size: int | None = None
    tile_budget: int | None = None       # distinct char tiles referenced by the whole bank
    oam_budget: int | None = None        # max OAM entries in one cell
    dimensions: dict | None = None
    cell_count: int = 0
    anim_sequences: int | None = None
    anim_frames: int | None = None
    warnings: list[str] = field(default_factory=list)
    visual_sha256: str | None = None
    mapping: str = ""
    blank_cells: list[int] = field(default_factory=list)
    invalid_cells: list[int] = field(default_factory=list)
    valid_frames: int = 0
    affine_objects: int = 0


def classify(data: bytes) -> str | None:
    """Return 'NCER','NCGR','NCLR','NANR','NSCR' or None; transparently looks through LZ10/LZ11."""
    tags = {b"RECN": "NCER", b"RGCN": "NCGR", b"RLCN": "NCLR", b"RNAN": "NANR", b"RCSN": "NSCR"}
    return tags.get(data[:4])


def maybe_decompress(data: bytes) -> bytes:
    if len(data) > 8 and data[0] in (0x10, 0x11):
        try:
            out = lz_decompress(data)
        except DecodeError:
            return data
        if classify(out) or out[:4] in (b"NARC", b" APS"):
            return out
    return data


def _max_tile_extent(bank: n2.CellBank, char_mapping: int, bpp: int) -> int:
    """Highest character-tile index (exclusive) the bank can touch, for pairing."""
    unit = n2.boundary_unit(char_mapping)
    tb = 32 if bpp == 4 else 64
    top = 0
    for oams in bank.cells:
        for o in oams:
            try:
                g = n2.oam_geometry(o)
            except DecodeError:
                continue
            if g["disabled"]:
                continue
            wt, ht = g["w"] // 8, g["h"] // 8
            if unit is None:
                end = (g["tile"] // 32 + ht - 1) * 32 + g["tile"] % 32 + wt   # position in a 32-wide VRAM grid
            else:
                end = g["tile"] * unit // tb + wt * ht
            top = max(top, end)
    return top


def decode_cell_bundle(ncer: bytes, ncgr: bytes, nclr: bytes, nanr: bytes | None = None,
                       raster_width: int | None = None, trust_scan_header: bool = True) -> BundleResult:
    """``trust_scan_header=False`` reproduces the Ranger 2 behaviour (scan width inferred from the cells)."""
    warns: list[str] = []
    try:
        bank = n2.parse_ncer(ncer, "NCER")
        chars = n2.parse_ncgr(ncgr, "NCGR")
        pal = n2.parse_nclr(nclr, "NCLR")
    except DecodeError as e:
        return BundleResult(UNSUPPORTED, f"{e.code}: {e.message}")
    if chars.bpp == 8 and pal.bpp == 4 and len(pal.colors) <= 16:
        warns.append("8bpp character data with a 16-colour palette")
    try:
        width = raster_width
        if chars.scanned and not width:
            hdr = chars.tiles_x
            if trust_scan_header and hdr and chars.tile_count % hdr == 0 and hdr >= _used_cols(bank):
                width = hdr
            else:
                width = n2.infer_raster_width(bank.cells, chars.tile_count)
        sheet_w, tiles = chars.tiles(width)
    except DecodeError as e:
        return BundleResult(UNSUPPORTED, f"{e.code}: {e.message}")
    rgb = pal.rgb()
    frames: list[Frame] = []
    tile_set: set = set()
    unmapped = bad_pal = affine = 0
    blank_cells: list[int] = []
    invalid_cells: list[int] = []
    max_oam = 0
    dims_min = dims_max = None
    try:
        for ci, oams in enumerate(bank.cells):
            rc = n2.render_cell(oams, tiles, sheet_w, chars.mapping, chars.bpp)
            unmapped += rc.unmapped_tiles
            affine += rc.affine_objects
            if rc.blank:
                blank_cells.append(ci)
            cell_bad = rc.unmapped_tiles > 0
            max_oam = max(max_oam, rc.oam_count)
            hi = max(rc.pixels)
            if hi >= len(rgb):
                bad_pal += 1
                cell_bad = True
                rgb_use = rgb + [(255, 0, 255)] * (hi + 1 - len(rgb))   # magenta marks the invalid reference
            else:
                rgb_use = rgb
            frames.append(indexed_to_frame(rc.width, rc.height, rc.pixels, rgb_use))
            if cell_bad:
                invalid_cells.append(ci)
            for o in oams:
                try:
                    g = n2.oam_geometry(o)
                except DecodeError:
                    continue
                if not g["disabled"]:
                    tile_set.update(_obj_tiles(g, chars.mapping, chars.bpp))
            d = (rc.width, rc.height)
            dims_min = d if dims_min is None else (min(dims_min[0], d[0]), min(dims_min[1], d[1]))
            dims_max = d if dims_max is None else (max(dims_max[0], d[0]), max(dims_max[1], d[1]))
    except DecodeError as e:
        return BundleResult(UNSUPPORTED, f"{e.code}: {e.message}")
    valid = [i for i in range(len(frames)) if i not in set(invalid_cells) and i not in set(blank_cells)]
    res = BundleResult(
        DECODED, None, frames, len(pal.colors), len(tile_set), max_oam,
        {"min": list(dims_min), "max": list(dims_max)} if dims_min else None, len(bank.cells),
        warnings=warns, mapping=("2D" if n2.boundary_unit(chars.mapping) is None
                                 else f"1D/{n2.boundary_unit(chars.mapping)}B"),
        blank_cells=blank_cells, invalid_cells=invalid_cells, valid_frames=len(valid), affine_objects=affine)
    if nanr:
        try:
            ab = n2.parse_nanr(nanr, "NANR")
            res.anim_sequences, res.anim_frames = len(ab.sequences), ab.total_frames
            bad = sum(1 for s in ab.sequences for c, _ in s if c >= len(bank.cells))
            if bad:
                res.warnings.append(f"NANR references {bad} cell indices outside the bank")
        except DecodeError as e:
            res.warnings.append(f"NANR not decoded: {e.code}")
    if not bank.cells:
        res.status, res.reason = STRUCTURAL_ONLY, "cell bank has zero cells"
    elif not valid:
        res.status = STRUCTURAL_ONLY
        res.reason = (f"no cell renders cleanly: {len(blank_cells)} blank, {len(invalid_cells)} with "
                      f"{unmapped} out-of-range tile ref(s) / {bad_pal} palette overflow(s)")
    elif invalid_cells:
        res.warnings.append(f"{len(invalid_cells)} of {len(bank.cells)} cells reference tiles/palette outside the "
                            f"paired data (cells {invalid_cells[:8]}{'...' if len(invalid_cells) > 8 else ''}); "
                            "only the other cells are usable")
    if affine:
        res.warnings.append(f"{affine} affine OBJ(s) rendered without rotation/scale")
    res.visual_sha256 = frames_hash([frames[i] for i in valid]) if res.status == DECODED else None
    return res


def _used_cols(bank: n2.CellBank) -> int:
    cols = 1
    for oams in bank.cells:
        for o in oams:
            try:
                g = n2.oam_geometry(o)
            except DecodeError:
                continue
            cols = max(cols, g["tile"] % 32 + g["w"] // 8)
    return cols


def _obj_tiles(g: dict, char_mapping: int, bpp: int):
    unit = n2.boundary_unit(char_mapping)
    tb = 32 if bpp == 4 else 64
    wt, ht = g["w"] // 8, g["h"] // 8
    for ty in range(ht):
        for tx in range(wt):
            if unit is None:
                yield (g["tile"] // 32 + ty) * 32 + g["tile"] % 32 + tx
            else:
                yield g["tile"] * unit // tb + ty * wt + tx


# ------------------------------------------------------------------------------------- pairing
ADJACENT = 4          # max member-index distance for a palette pairing to count as evidence rather than a guess
@dataclass
class Member:
    index: int
    name: str | None
    kind: str
    data: bytes


def classify_members(members: list[n2.NarcMember]) -> list[Member]:
    out = []
    for m in members:
        d = maybe_decompress(m.data)
        k = classify(d)
        if k:
            out.append(Member(m.index, m.name, k, d))
    return out


def pair_bundles(members: list[Member]):
    """Deterministically pair each NCER with its NCGR/NCLR/NANR.

    Named members (Ranger packages) pair by file stem.  Anonymous members (HGSS) pair by index proximity with a
    validity test: the character data must contain every tile the bank references and the palette must cover every
    palette row the OAMs select.  Yields (ncer, ncgr|None, nclr|None, nanr|None, how).
    """
    by_kind = {k: [m for m in members if m.kind == k] for k in ("NCER", "NCGR", "NCLR", "NANR")}
    named = all(m.name for m in members)
    for ncer in by_kind["NCER"]:
        try:
            bank = n2.parse_ncer(ncer.data)
        except DecodeError:
            yield ncer, None, None, None, "unparsed"
            continue
        if named:
            stem = ncer.name.rsplit(".", 1)[0]
            g = next((m for m in by_kind["NCGR"] if m.name.rsplit(".", 1)[0] == stem), None) or \
                next((m for m in members if m.name.endswith(".NCBR") and m.name.rsplit(".", 1)[0] == stem), None)
            a = next((m for m in by_kind["NANR"] if m.name.rsplit(".", 1)[0] == stem), None)
            p = next((m for m in by_kind["NCLR"] if m.name.rsplit(".", 1)[0] == stem), None) or \
                (by_kind["NCLR"][0] if by_kind["NCLR"] else None)
            yield ncer, g, p, a, "stem"
            continue
        g, p = _best_char(ncer, bank, by_kind["NCGR"]), _best_pal(ncer, bank, by_kind["NCLR"])
        unique = len(by_kind["NCLR"]) == 1
        near = p is not None and (unique or abs(p.index - ncer.index) <= ADJACENT)
        yield ncer, g, p, _nearest_anim(ncer, bank, by_kind["NANR"]), (
            "unique-palette" if unique else "proximity") if near else "proximity-distant"


def _best_char(ncer: Member, bank: n2.CellBank, chars: list[Member]):
    cands = sorted((m for m in chars), key=lambda m: (abs(m.index - ncer.index), m.index > ncer.index))
    first = None
    for m in cands[:8]:
        try:
            cd = n2.parse_ncgr(m.data)
        except DecodeError:
            continue
        first = first or m
        if _max_tile_extent(bank, cd.mapping, cd.bpp) <= cd.tile_count:
            return m
    return first


def _best_pal(ncer: Member, bank: n2.CellBank, pals: list[Member]):
    need = 0
    for oams in bank.cells:
        for o in oams:
            need = max(need, (o[2] >> 12) + 1)
    cands = sorted(pals, key=lambda m: (abs(m.index - ncer.index), m.index > ncer.index))
    first = None
    for m in cands[:8]:
        try:
            p = n2.parse_nclr(m.data)
        except DecodeError:
            continue
        first = first or m
        if p.rows >= need or p.bpp == 8:
            return m
    return first


def _nearest_anim(ncer: Member, bank: n2.CellBank, anims: list[Member]):
    cands = sorted(anims, key=lambda m: (abs(m.index - ncer.index), m.index > ncer.index))
    for m in cands[:3]:
        if abs(m.index - ncer.index) > 3:
            break
        try:
            ab = n2.parse_nanr(m.data)
        except DecodeError:
            continue
        if all(c < len(bank.cells) for s in ab.sequences for c, _ in s):
            return m
    return None
