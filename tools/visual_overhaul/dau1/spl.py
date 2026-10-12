"""NitroSystem SPL particle archive (``.spa``) - header, emitter inventory and texture decoding.

Format facts below are established from real samples (pokediamond ``wazaeffect/effectdata/{waza,ball}_particle``,
602 files) and the field layout in the decomp's ``spl_texture.h``; every file is validated structurally
(blocks must tile the file exactly, texture byte sizes must equal width*height*bits/8):

  header  0x20 : " APS" "12_1" | u16 emitter_count | u16 texture_count | u32 0 | u32 emitter_block_size |
                 u32 texture_block_size | u32 texture_block_offset | u32 0 ; emitter_block follows the header
  emitter block: emitter_count variable-size SPLRes records (NOT decoded here: inventory only)
  texture block: texture_count records, each
                 " TPS" | u32 param (fmt:4 s:4 t:4 rep:2 flp:2 plt0:1 ...) | u32 pixel_bytes | u32 palette_offset
                 | u32 palette_bytes | u32 record_bytes | 3 x u32 | pixels | palette (BGR555)
Texture size = (8 << s) x (8 << t); fmt 1 = A3I5, 2 = 4-colour, 3 = 16-colour, 4 = 256-colour, 6 = A5I3, 7 = direct,
5 = 4x4 compressed (not decoded).  Emitter (particle behaviour) decoding is out of scope for DAU1.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .catalog import Unit
from .common import DECODED, STRUCTURAL_ONLY, UNSUPPORTED, DecodeError, Reader, bgr555_to_rgb, sha256_bytes
from .render import Frame, frames_hash

MAGIC = b" APS"
FMT_BITS = {1: 8, 2: 2, 3: 4, 4: 8, 6: 8, 7: 16}


@dataclass
class SplTexture:
    fmt: int
    width: int
    height: int
    transparent0: bool
    frame: Frame | None
    palette_colors: int


@dataclass
class SplArchive:
    version: str
    emitters: int
    emitter_bytes: int
    textures: list[SplTexture] = field(default_factory=list)


def parse_spl(data: bytes) -> SplArchive:
    r = Reader(data, "SPL")
    r.magic(0, MAGIC)
    version = r.raw(4, 4).decode("ascii", "replace")
    nres, ntex = r.u16(8), r.u16(10)
    res_bytes, tex_bytes, tex_off = r.u32(16), r.u32(20), r.u32(24)
    if nres > 4096 or ntex > 4096:
        raise DecodeError("LIMIT", f"{nres} emitters / {ntex} textures")
    if 0x20 + res_bytes != tex_off or tex_off + tex_bytes != len(data):
        raise DecodeError("BAD_OFFSET", f"blocks do not tile the file: hdr 0x20 + {res_bytes:#x} != {tex_off:#x} "
                                        f"or {tex_off:#x} + {tex_bytes:#x} != {len(data):#x}")
    arch = SplArchive(version, nres, res_bytes)
    pos = tex_off
    for i in range(ntex):
        r.magic(pos, b" TPS")
        param, pix, pal_off, pal_bytes, rec = r.u32(pos + 4), r.u32(pos + 8), r.u32(pos + 12), r.u32(pos + 16), r.u32(pos + 20)
        fmt, s, t = param & 15, (param >> 4) & 15, (param >> 8) & 15
        plt0 = bool((param >> 16) & 1)
        if rec < 0x20 or pos + rec > len(data):
            raise DecodeError("BAD_OFFSET", f"texture {i}: record size {rec:#x}")
        if s > 7 or t > 7 or fmt not in FMT_BITS and fmt != 5:
            raise DecodeError("BAD_HEADER", f"texture {i}: fmt {fmt} s {s} t {t}")
        w, h = 8 << s, 8 << t
        if fmt == 5:
            arch.textures.append(SplTexture(fmt, w, h, plt0, None, 0))
            pos += rec
            continue
        need = w * h * FMT_BITS[fmt] // 8
        if pix != need or pal_off != 0x20 + pix or pos + 0x20 + pix + pal_bytes > pos + rec:
            raise DecodeError("BAD_HEADER", f"texture {i}: {w}x{h} fmt {fmt} needs {need} px bytes, header says {pix}")
        pixels = r.raw(pos + 0x20, pix)
        pal = [r.u16(pos + pal_off + 2 * k) for k in range(pal_bytes // 2)]
        arch.textures.append(_render_texture(i, fmt, w, h, plt0, pixels, pal))
        pos += rec
    if pos != len(data):
        raise DecodeError("BAD_OFFSET", f"texture records end at {pos:#x}, file is {len(data):#x}")
    return arch


def _render_texture(i, fmt, w, h, plt0, px, pal) -> SplTexture:
    out = bytearray(w * h * 4)

    def col(idx):
        if idx >= len(pal):
            raise DecodeError("BAD_PALETTE_INDEX", f"texture {i}: index {idx} outside {len(pal)}-colour palette")
        return bgr555_to_rgb(pal[idx])

    n = w * h
    for p in range(n):
        if fmt == 1:
            b = px[p]; idx, a = b & 31, (b >> 5) * 255 // 7
        elif fmt == 6:
            b = px[p]; idx, a = b & 7, (b >> 3) * 255 // 31
        elif fmt == 2:
            idx, a = (px[p >> 2] >> ((p & 3) * 2)) & 3, 255
        elif fmt == 3:
            idx, a = (px[p >> 1] >> ((p & 1) * 4)) & 15, 255
        elif fmt == 4:
            idx, a = px[p], 255
        else:                                                 # direct colour, bit 15 = opaque
            v = px[2 * p] | px[2 * p + 1] << 8
            c = bgr555_to_rgb(v)
            out[4 * p:4 * p + 4] = bytes((*c, 255 if v & 0x8000 else 0))
            continue
        if fmt in (2, 3, 4) and plt0 and idx == 0:
            a = 0
        if a:
            out[4 * p:4 * p + 4] = bytes((*col(idx), a))
    return SplTexture(fmt, w, h, plt0, Frame(w, h, bytes(out)), len(pal))


def spl_unit(library: str, rel: str, data: bytes):
    """Catalog unit + frames for one .spa: frame_count = decoded textures, oam/tile budgets null (emitters not decoded)."""
    sha = sha256_bytes(data)
    base = dict(id=f"{library}:{rel}", library=library, source=rel, sha256=sha, type="spl_particle_archive",
                members=[{"name": rel, "sha256": sha, "size": len(data)}])
    try:
        a = parse_spl(data)
    except DecodeError as e:
        return Unit(**base, status=UNSUPPORTED, error_reason=f"{e.code}: {e.message}"), []
    frames = [t.frame for t in a.textures if t.frame is not None and t.frame.opaque_pixels]
    undecoded = [i for i, t in enumerate(a.textures) if t.frame is None]
    extra = {"version": a.version, "emitters": a.emitters, "emitter_block_bytes": a.emitter_bytes,
             "textures": len(a.textures), "tex_formats": sorted({t.fmt for t in a.textures}),
             "emitter_decoding": "not implemented (inventory only)"}
    if not frames:
        return Unit(**base, status=STRUCTURAL_ONLY, extra=extra,
                    error_reason="no texture with visible pixels (" + (f"{len(undecoded)} 4x4-compressed texture(s) undecoded"
                                                                       if undecoded else "all blank") + ")"), []
    u = Unit(**base, status=DECODED, frame_count=len(frames),
             palette_size=max(t.palette_colors for t in a.textures),
             dimensions={"min": [min(f.width for f in frames), min(f.height for f in frames)],
                         "max": [max(f.width for f in frames), max(f.height for f in frames)]},
             tile_budget=None, oam_budget=None, visual_sha256=frames_hash(frames), extra=extra)
    if undecoded:
        u.warnings.append(f"{len(undecoded)} 4x4-compressed texture(s) not decoded")
    return u, frames
