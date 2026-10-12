"""SPL (``.spa``) emitter-block parser, verified against the Platinum ``lib/spl`` sources.

Everything decoded here is defined by `lib/spl/include/spl_resource.h`, `spl_behavior.h` and `SPLManager_LoadResources`
(`lib/spl/src/spl_manager.c`).  An emitter record is laid out as

  SPLResourceHeader (0x58) | [SPLScaleAnim 0x0C] [SPLColorAnim 0x0C] [SPLAlphaAnim 0x08] [SPLTexAnim 0x0C]
  [SPLChildResource 0x10] | [Gravity 0x08] [Random 0x08] [Magnet 0x10] [Spin 0x04] [CollisionPlane 0x08]
  [Convergence 0x10]

where each optional block is present iff its flag bit in the header is set (in exactly that order).  The strongest
format evidence is *tiling*: for every real archive the emitter records must consume the emitter block to the byte.
Sizes of the individually uncertain structs are therefore verified by the corpus (see ``test_dau2_sources.py``), not
assumed.  Fixed point: fx32 = 20.12, fx16 = 1.3.12 (signed); angles are 0x10000 per turn.

Semantics that the sources do not pin down are NOT interpreted: they stay as raw integers under ``unknown``.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

from dau1.common import DecodeError, Reader

HDR_SIZE, SCALE_SIZE, COLOR_SIZE, ALPHA_SIZE, TEX_SIZE, CHILD_SIZE = 0x58, 0x0C, 0x0C, 0x08, 0x0C, 0x14
BEHAVIOR_SIZES = {"gravity": 0x08, "random": 0x08, "magnet": 0x10, "spin": 0x04, "collision": 0x08, "convergence": 0x10}
FILE_HDR = 0x20
MAX_EMITTERS = 4096

EMISSION_TYPES = ["point", "sphere_surface", "circle_border", "circle_border_uniform", "sphere", "circle",
                  "cylinder_surface", "cylinder", "hemisphere_surface", "hemisphere"]
DRAW_TYPES = ["billboard", "directional_billboard", "polygon", "directional_polygon", "directional_polygon_center"]
CIRCLE_AXES = ["z", "y", "x", "emitter"]

FLAG_BITS = {  # name -> (shift, width)
    "emission_type": (0, 4), "draw_type": (4, 2), "circle_axis": (6, 2), "has_scale_anim": (8, 1),
    "has_color_anim": (9, 1), "has_alpha_anim": (10, 1), "has_tex_anim": (11, 1), "has_rotation": (12, 1),
    "random_init_angle": (13, 1), "self_maintaining": (14, 1), "follow_emitter": (15, 1), "has_child": (16, 1),
    "polygon_rot_axis": (17, 2), "polygon_ref_plane": (19, 1), "randomize_looped_anim": (20, 1),
    "draw_children_first": (21, 1), "hide_parent": (22, 1), "use_view_space": (23, 1), "has_gravity": (24, 1),
    "has_random": (25, 1), "has_magnet": (26, 1), "has_spin": (27, 1), "has_collision": (28, 1),
    "has_convergence": (29, 1), "fixed_polygon_id": (30, 1), "child_fixed_polygon_id": (31, 1),
}


def fx32(v: int) -> float:
    return v / 4096.0


def _bits(word: int, shift: int, width: int) -> int:
    return (word >> shift) & ((1 << width) - 1)


def _sx(v: int, bits: int) -> int:
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


@dataclass
class Emitter:
    index: int
    offset: int
    size: int
    flags: dict
    header: dict
    scale: dict | None = None
    color: dict | None = None
    alpha: dict | None = None
    tex: dict | None = None
    child: dict | None = None
    behaviors: dict = field(default_factory=dict)
    unknown: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        d = {"index": self.index, "offset": self.offset, "size": self.size, "flags": self.flags, "header": self.header,
             "behaviors": self.behaviors, "unknown": self.unknown}
        for k in ("scale", "color", "alpha", "tex", "child"):
            if getattr(self, k) is not None:
                d[k] = getattr(self, k)
        return d


@dataclass
class SplFile:
    version: str
    emitter_count: int
    texture_count: int
    emitter_block_size: int
    texture_block_offset: int
    emitters: list[Emitter]


def _s32(v: int) -> int:
    return v - (1 << 32) if v >> 31 else v


def parse_emitter(r: Reader, o: int, index: int, limit: int) -> Emitter:
    """Parse one emitter record starting at ``o``; never reads at or beyond ``limit``."""
    if o + HDR_SIZE > limit:
        raise DecodeError("TRUNCATED", f"emitter {index}: header at {o:#x} overruns block end {limit:#x}")
    word = r.u32(o)
    flags = {n: _bits(word, s, w) for n, (s, w) in FLAG_BITS.items()}
    if flags["emission_type"] >= len(EMISSION_TYPES):
        raise DecodeError("BAD_HEADER", f"emitter {index}: emission type {flags['emission_type']}")
    if flags["draw_type"] >= len(DRAW_TYPES):
        raise DecodeError("BAD_HEADER", f"emitter {index}: draw type {flags['draw_type']}")
    rnd, m0, m1, m2 = r.u32(o + 0x40), r.u32(o + 0x44), r.u32(o + 0x48), r.u32(o + 0x4C)
    hdr = {
        "emitter_base_pos_fx32": [_s32(r.u32(o + 4 + 4 * k)) for k in range(3)],
        "emission_count_fx32": _s32(r.u32(o + 0x10)),
        "radius_fx32": _s32(r.u32(o + 0x14)),
        "length_fx32": _s32(r.u32(o + 0x18)),
        "axis_fx16": [struct.unpack_from("<h", r.raw(o + 0x1C + 2 * k, 2))[0] for k in range(3)],
        "color_bgr555": r.u16(o + 0x22),
        "init_vel_pos_amp_fx32": _s32(r.u32(o + 0x24)),
        "init_vel_axis_amp_fx32": _s32(r.u32(o + 0x28)),
        "base_scale_fx32": _s32(r.u32(o + 0x2C)),
        "aspect_fx16": r.s16(o + 0x30),
        "start_delay": r.u16(o + 0x32),
        "min_rotation": r.s16(o + 0x34),
        "max_rotation": r.s16(o + 0x36),
        "init_angle": r.u16(o + 0x38),
        "emitter_life": r.u16(o + 0x3C),
        "particle_life": r.u16(o + 0x3E),
        "rand_base_scale": rnd & 255, "rand_life": (rnd >> 8) & 255, "rand_init_vel": (rnd >> 16) & 255,
        "emission_interval": m0 & 255, "base_alpha": (m0 >> 8) & 255,
        "air_resistance": (m0 >> 16) & 255, "texture_index": (m0 >> 24) & 255,
        "loop_frames": m1 & 255, "dbb_scale": (m1 >> 8) & 0xFFFF, "tile_s": (m1 >> 24) & 3, "tile_t": (m1 >> 26) & 3,
        "scale_anim_dir": (m1 >> 28) & 7, "dpol_face_emitter": (m1 >> 31) & 1,
        "flip_s": m2 & 1, "flip_t": (m2 >> 1) & 1,
        "polygon_x_fx16": r.s16(o + 0x50), "polygon_y_fx16": r.s16(o + 0x52),
        "user_flags": r.u8(o + 0x54),
    }
    unknown = {"reserved_0x3A": r.u16(o + 0x3A), "rand_reserved": (rnd >> 24) & 255, "misc1_reserved_none": 0,
               "misc2_reserved": m2 >> 2, "user_reserved": r.u32(o + 0x54) >> 8}
    pos = o + HDR_SIZE
    em = Emitter(index, o, 0, flags, hdr, unknown=unknown)

    def need(n, what):
        if pos + n > limit:
            raise DecodeError("TRUNCATED", f"emitter {index}: {what} at {pos:#x} overruns block end {limit:#x}")

    if flags["has_scale_anim"]:
        need(SCALE_SIZE, "scale anim")
        em.scale = {"start_fx16": r.s16(pos), "mid_fx16": r.s16(pos + 2), "end_fx16": r.s16(pos + 4),
                    "in": r.u8(pos + 6), "out": r.u8(pos + 7), "loop": r.u16(pos + 8) & 1}
        em.unknown["scale_reserved"] = [r.u16(pos + 8) >> 1, r.u16(pos + 10)]
        pos += SCALE_SIZE
    if flags["has_color_anim"]:
        need(COLOR_SIZE, "color anim")
        c = r.u32(pos + 4)
        f = r.u16(pos + 8)
        em.color = {"start_bgr555": r.u16(pos), "end_bgr555": r.u16(pos + 2), "in": c & 255, "peak": (c >> 8) & 255,
                    "out": (c >> 16) & 255, "random_start": f & 1, "loop": (f >> 1) & 1, "interpolate": (f >> 2) & 1}
        em.unknown["color_reserved"] = [c >> 24, f >> 3, r.u16(pos + 10)]
        pos += COLOR_SIZE
    if flags["has_alpha_anim"]:
        need(ALPHA_SIZE, "alpha anim")
        a, f = r.u16(pos), r.u16(pos + 2)
        em.alpha = {"start": a & 31, "mid": (a >> 5) & 31, "end": (a >> 10) & 31, "random_range": f & 255,
                    "loop": (f >> 8) & 1, "in": r.u8(pos + 4), "out": r.u8(pos + 5)}
        em.unknown["alpha_reserved"] = [a >> 15, f >> 9, r.u16(pos + 6)]
        pos += ALPHA_SIZE
    if flags["has_tex_anim"]:
        need(TEX_SIZE, "texture anim")
        p = r.u32(pos + 8)
        em.tex = {"textures": list(r.raw(pos, 8)), "frame_count": p & 255, "step": (p >> 8) & 255,
                  "randomize_init": (p >> 16) & 1, "loop": (p >> 17) & 1}
        em.unknown["tex_reserved"] = p >> 18
        pos += TEX_SIZE
    if flags["has_child"]:
        need(CHILD_SIZE, "child resource")
        cf, cm, cm2 = r.u16(pos), r.u32(pos + 12), r.u32(pos + 16)
        em.child = {"uses_behaviors": cf & 1, "has_scale_anim": (cf >> 1) & 1, "has_alpha_anim": (cf >> 2) & 1,
                    "rotation_type": (cf >> 3) & 3, "follow_emitter": (cf >> 5) & 1, "use_child_color": (cf >> 6) & 1,
                    "draw_type": (cf >> 7) & 3, "polygon_rot_axis": (cf >> 9) & 3, "polygon_ref_plane": (cf >> 11) & 1,
                    "random_init_vel_mag_fx16": r.s16(pos + 2), "end_scale_fx16": r.s16(pos + 4), "life": r.u16(pos + 6),
                    "velocity_ratio": r.u8(pos + 8), "scale_ratio": r.u8(pos + 9), "color_bgr555": r.u16(pos + 10),
                    "emission_count": cm & 255, "emission_delay": (cm >> 8) & 255, "emission_interval": (cm >> 16) & 255,
                    "texture": (cm >> 24) & 255, "tile_s": cm2 & 3, "tile_t": (cm2 >> 2) & 3, "flip_s": (cm2 >> 4) & 1,
                    "flip_t": (cm2 >> 5) & 1, "dpol_face_emitter": (cm2 >> 6) & 1}
        em.unknown["child_reserved"] = [cf >> 12, cm2 >> 7]
        pos += CHILD_SIZE
    for name in ("gravity", "random", "magnet", "spin", "collision", "convergence"):
        if not flags["has_" + name]:
            continue
        n = BEHAVIOR_SIZES[name]
        need(n, name + " behavior")
        s16 = lambda k: r.s16(pos + k)           # noqa: E731
        if name == "gravity":
            em.behaviors[name] = {"magnitude_fx16": [s16(0), s16(2), s16(4)]}
        elif name == "random":
            em.behaviors[name] = {"magnitude_fx16": [s16(0), s16(2), s16(4)], "apply_interval": r.u16(pos + 6)}
        elif name in ("magnet", "convergence"):
            em.behaviors[name] = {"target_fx32": [_s32(r.u32(pos + 4 * k)) for k in range(3)], "force_fx16": s16(12)}
        elif name == "spin":
            em.behaviors[name] = {"angle": r.u16(pos), "axis": r.u16(pos + 2)}
        else:
            em.behaviors[name] = {"plane_y_fx32": _s32(r.u32(pos)), "elasticity_fx16": s16(4), "type": r.u16(pos + 6) & 3}
        pos += n
    em.size = pos - o
    return em


def parse_emitters(data: bytes) -> SplFile:
    """Parse every emitter record of one ``.spa``.  Fails closed unless the records tile the emitter block exactly."""
    r = Reader(data, "SPL")
    r.magic(0, b" APS")
    version = r.raw(4, 4).decode("ascii", "replace")
    nres, ntex = r.u16(8), r.u16(10)
    res_bytes, tex_bytes, tex_off = r.u32(16), r.u32(20), r.u32(24)
    if nres > MAX_EMITTERS:
        raise DecodeError("LIMIT", f"{nres} emitters")
    if FILE_HDR + res_bytes != tex_off or tex_off + tex_bytes != len(data):
        raise DecodeError("BAD_OFFSET", "emitter/texture blocks do not tile the file")
    pos, out = FILE_HDR, []
    for i in range(nres):
        em = parse_emitter(r, pos, i, tex_off)
        out.append(em)
        pos += em.size
    if pos != tex_off:
        raise DecodeError("BAD_OFFSET", f"emitter records end at {pos:#x}, block ends at {tex_off:#x}")
    return SplFile(version, nres, ntex, res_bytes, tex_off, out)
