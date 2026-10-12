"""Offline SPL replay: a deterministic Python port of the particle *state* update in Platinum's ``lib/spl``.

Ported from `SPLEmitter_Init/Update`, `SPLEmitter_EmitParticles/EmitChildren`, `SPLAnim_*`, `SPLBehavior_*` and the
`SPLRandom` LCG (``state = state * 0x5EEDF715 + 0x1B0CB173``).  Integer fixed-point arithmetic follows the source
(`FX_MUL = (a*b)>>12`, arithmetic right shifts).

What is NOT reproduced bit-exactly (labelled in every replay's ``assumptions``):
  * ``FX_SinIdx/FX_CosIdx`` and ``VEC_Normalize`` use floating point instead of the NitroSDK tables / fixed sqrt
    (affects circle/hemisphere/cylinder placement, spin, rotation by a few LSBs - never counts or timing);
  * the initial ``gSPLRandomState`` (the game seeds it from battle state) - a caller-supplied seed is used;
  * the camera: previews use a fixed orthographic front view; the real battle camera / emitter origin come from
    the move script, which this phase does not interpret;
  * which emitters of an archive a move spawns, and when: the replay spawns the chosen emitters at frame 0.
Draw-time behaviour (polygon types, view space, directional billboards) is exposed as raw flags, not simulated.
"""
from __future__ import annotations

import functools
import math
from dataclasses import dataclass, field

from .spl_emitter import Emitter, SplFile

M32 = 0xFFFFFFFF


@functools.lru_cache(maxsize=None)
def fx_sin(idx: int) -> int:
    """Stand-in for FX_SinIdx: 16-bit angle index (0x10000 = full turn) -> sine in 1/4096 units, rounded to nearest (not the NitroSDK table)."""
    return round(math.sin(2 * math.pi * (idx & 0xFFFF) / 65536) * 4096)


def fx_cos(idx: int) -> int:
    return fx_sin(idx + 0x4000)


def fx_mul(a: int, b: int) -> int:
    return (a * b) >> 12


def s32(v: int) -> int:
    v &= M32
    return v - (1 << 32) if v >> 31 else v


class Lcg:
    """`SPLRandom_Next`: ``s = s*0x5eedf715 + 0x1b0cb173 (mod 2^32)``; ``U32(bits)`` takes the top ``bits``."""

    def __init__(self, seed: int):
        self.s = seed & M32

    def next(self) -> int:
        self.s = (self.s * 0x5EEDF715 + 0x1B0CB173) & M32
        return self.s

    def u32(self, bits: int) -> int:
        return self.next() >> (32 - bits)

    def fx32(self, bits: int) -> int:
        return s32(self.next()) >> (32 - bits)

    def scaled_range(self, num: int, rng: int) -> int:                       # SPLRandom_ScaledRangeFX32
        return (num * (255 - ((rng * self.u32(8)) >> 8))) >> 8

    def double_scaled_range(self, num: int, rng: int) -> int:                # SPLRandom_DoubleScaledRangeFX32
        return (num * (255 + rng - ((rng * self.u32(8)) >> 7))) >> 8

    def range_fx32(self, num: int) -> int:                                   # SPLRandom_RangeFX32
        return (num * self.u32(9) - (num << 8)) >> 8

    def between_fx32(self, lo: int, hi: int) -> int:                         # SPLRandom_BetweenFX32
        return s32((hi - lo) * self.u32(12) + lo * 4096)

    def unit_vec(self, xy_only=False) -> list[int]:                          # SPLRandom_VecFx32(_XY): float normalise
        v = [self.fx32(24), self.fx32(24), 0 if xy_only else self.fx32(24)]
        n = math.sqrt(sum(c * c for c in v))
        return [0, 0, 0] if n == 0 else [int(c * 4096 / n) for c in v]


@dataclass
class Particle:
    pos: list
    vel: list
    emitter_pos: list
    base_scale: int
    anim_scale: int = 4096
    color: int = 0
    base_alpha: int = 31
    anim_alpha: int = 31
    rotation: int = 0
    angular_vel: int = 0
    life: int = 1
    age: int = 0
    texture: int = 0
    loop_factor: int = 0
    life_factor: int = 0
    life_offset: int = 0
    child: bool = False


class EmitterState:
    def __init__(self, em: Emitter, rng: Lcg, origin=(0, 0, 0)):
        self.em, self.rng = em, rng
        h = em.header
        self.age = 0
        self.started = False
        self.pos = [origin[k] + h["emitter_base_pos_fx32"][k] for k in range(3)]
        self.frac = 0
        self.particles: list[Particle] = []
        self.children: list[Particle] = []
        self.emitted_per_step: list[int] = []
        self.terminated = False

    # ---------------------------------------------------------------- emission (SPLEmitter_EmitParticles)
    def _emit(self):
        em, h, rng = self.em, self.em.header, self.rng
        f = em.flags
        total_fx = h["emission_count_fx32"] + self.frac
        total = total_fx >> 12
        self.frac = total_fx & 0xFFF
        self.emitted_per_step.append(total)
        et = f["emission_type"]
        radius, length = h["radius_fx32"], h["length_fx32"]
        axis = [h["axis_fx16"][k] for k in range(3)]
        for i in range(total):
            pos, vel_tmp = [0, 0, 0], None
            if et == 1:
                pos = [fx_mul(c, radius) for c in rng.unit_vec()]
            elif et in (2, 5, 6, 7, 3):
                if et == 2:
                    v = rng.unit_vec(True)
                    pos = [fx_mul(v[0], radius), fx_mul(v[1], radius), 0]
                elif et == 3:
                    idx = (i * 65536) // max(total, 1)             # source: idx = (emission * FX32_CONST(16)) / totalEmissions
                    pos = [fx_mul(fx_sin(idx), radius), fx_mul(fx_cos(idx), radius), 0]
                elif et == 5:
                    v = rng.unit_vec(True)
                    pos = [fx_mul(fx_mul(v[0], radius), rng.range_fx32(4096)), fx_mul(fx_mul(v[1], radius), rng.range_fx32(4096)), 0]
                elif et == 6:
                    vel_tmp = rng.unit_vec(True)
                    pos = [fx_mul(vel_tmp[0], radius), fx_mul(vel_tmp[1], radius), rng.range_fx32(length)]
                else:
                    vel_tmp = rng.unit_vec(True)
                    pos = [fx_mul(fx_mul(vel_tmp[0], radius), rng.range_fx32(4096)),
                           fx_mul(fx_mul(vel_tmp[1], radius), rng.range_fx32(4096)), rng.range_fx32(length)]
            elif et == 4:
                v = rng.unit_vec()
                pos = [fx_mul(fx_mul(c, radius), rng.range_fx32(4096)) for c in v]
            elif et in (8, 9):
                v = rng.unit_vec()
                if v[1] < 0:                                        # emitter "up" axis assumed +Y (axis tilt not modelled)
                    v = [-c for c in v]
                if et == 8:
                    pos = [fx_mul(c, radius) for c in v]
                else:
                    pos = [fx_mul(fx_mul(c, radius), (rng.range_fx32(4096) >> 1) + 2048) for c in v]
            mag_pos = rng.double_scaled_range(h["init_vel_pos_amp_fx32"], h["rand_init_vel"])
            mag_axis = rng.double_scaled_range(h["init_vel_axis_amp_fx32"], h["rand_init_vel"])
            if et == 0 or pos == [0, 0, 0]:
                nrm = rng.unit_vec()
            else:
                n = math.sqrt(sum(c * c for c in pos)) or 1.0
                nrm = [int(c * 4096 / n) for c in pos]
            vel = [fx_mul(nrm[k], mag_pos) + fx_mul(axis[k], mag_axis) for k in range(3)]
            bs = rng.double_scaled_range(h["base_scale_fx32"], h["rand_base_scale"])
            color = h["color_bgr555"]
            if em.color and em.color["random_start"]:
                color = [em.color["start_bgr555"], h["color_bgr555"], em.color["end_bgr555"]][rng.u32(12) % 3]
            rot = rng.next() if f["random_init_angle"] else h["init_angle"]
            ang_vel = ((rng.between_fx32(h["min_rotation"], h["max_rotation"]) & M32) >> 12) if f["has_rotation"] else 0
            life = rng.scaled_range(h["particle_life"], h["rand_life"]) + 1
            if f["has_tex_anim"] and em.tex["randomize_init"]:
                tex = em.tex["textures"][rng.u32(12) % max(em.tex["frame_count"], 1)]
            elif f["has_tex_anim"]:
                tex = em.tex["textures"][0]
            else:
                tex = h["texture_index"]
            p = Particle(pos, vel, list(self.pos), bs, 4096, color, h["base_alpha"], 31, rot & 0xFFFF,
                         ang_vel & 0xFFFF, life, 0, tex, 0xFFFF // max(h["loop_frames"], 1), 0xFFFF // life, 0)
            if f["randomize_looped_anim"]:
                p.life_offset = rng.u32(8)
            self.particles.insert(0, p)

    # ---------------------------------------------------------------- children (SPLEmitter_EmitChildren)
    def _emit_children(self, par: Particle):
        c = self.em.child
        vel_ratio = (c["velocity_ratio"] * 4096 * 16) >> 12                  # FX_MUL(ratio*ONE, 1/256 in fx = 16)
        for _ in range(c["emission_count"]):
            vel = [fx_mul(par.vel[k], vel_ratio) + self.rng.range_fx32(c["random_init_vel_mag_fx16"]) for k in range(3)]
            ps = par.base_scale * par.anim_scale >> 12
            ch = Particle(list(par.pos), vel, list(par.emitter_pos), ps * (c["scale_ratio"] + 1) >> 6, 4096,
                          c["color_bgr555"] if c["use_child_color"] else par.color,
                          (par.base_alpha * (par.anim_alpha + 1)) >> 5, 31,
                          0 if c["rotation_type"] == 0 else par.rotation,
                          par.angular_vel if c["rotation_type"] == 2 else 0, max(c["life"], 1), 0, c["texture"],
                          0xFFFF // max(par.life // 2, 1), 0xFFFF // par.life, 0, True)
            self.children.insert(0, ch)

    # ---------------------------------------------------------------- animation curves (SPLAnim_*)
    def _anims(self, p: Particle):
        em, f = self.em, self.em.flags
        h = em.header
        lr_noloop = ((p.life_factor * p.age) >> 8) & 255
        lr_loop = (p.life_offset + ((p.loop_factor * p.age) >> 8)) & 255
        if f["has_scale_anim"]:
            a, lr = em.scale, lr_loop if em.scale["loop"] else lr_noloop
            if lr < a["in"]:
                p.anim_scale = a["start_fx16"] + _cdiv(lr * (a["mid_fx16"] - a["start_fx16"]), max(a["in"], 1))
            elif lr < a["out"]:
                p.anim_scale = a["mid_fx16"]
            else:
                p.anim_scale = a["end_fx16"] + _cdiv((lr - 255) * (a["end_fx16"] - a["mid_fx16"]), max(255 - a["out"], 1))
        if f["has_color_anim"] and not em.color["random_start"]:
            a, lr = em.color, lr_loop if em.color["loop"] else lr_noloop
            p.color = _color_anim(a, h["color_bgr555"], lr)
        if f["has_alpha_anim"]:
            a, lr = em.alpha, lr_loop if em.alpha["loop"] else lr_noloop
            if lr < a["in"]:
                v = a["start"] + _cdiv(lr * (a["mid"] - a["start"]), max(a["in"], 1))
            elif lr < a["out"]:
                v = a["mid"]
            else:
                v = a["end"] + _cdiv((lr - 255) * (a["end"] - a["mid"]), max(255 - a["out"], 1))
            p.anim_alpha = self.rng.scaled_range(v, a["random_range"])
        if f["has_tex_anim"] and not em.tex["randomize_init"]:
            lr = lr_loop if em.tex["loop"] else lr_noloop
            for i in range(em.tex["frame_count"]):
                if lr < em.tex["step"] * (i + 1):
                    p.texture = em.tex["textures"][i]
                    break

    # ---------------------------------------------------------------- behaviours (SPLBehavior_*)
    def _behaviors(self, p: Particle, acc: list, which: dict):
        for name, b in which.items():
            if name == "gravity":
                for k in range(3):
                    acc[k] += b["magnitude_fx16"][k]
            elif name == "random":
                if b["apply_interval"] and p.age % b["apply_interval"] == 0:
                    for k in range(3):
                        acc[k] += self.rng.range_fx32(b["magnitude_fx16"][k])
            elif name == "magnet":
                for k in range(3):
                    acc[k] += (b["force_fx16"] * ((b["target_fx32"][k] - p.pos[k]) - p.vel[k])) >> 12
            elif name == "spin":
                c, s = fx_cos(b["angle"]), fx_sin(b["angle"])
                x, y, z = p.pos
                if b["axis"] == 0:
                    p.pos = [x, (c * y - s * z) >> 12, (s * y + c * z) >> 12]
                elif b["axis"] == 1:
                    p.pos = [(c * x + s * z) >> 12, y, (-s * x + c * z) >> 12]
                else:
                    p.pos = [(c * x - s * y) >> 12, (s * x + c * y) >> 12, z]
            elif name == "collision":
                y, ey = b["plane_y_fx32"], p.emitter_pos[1]
                crossed = (ey < y and ey + p.pos[1] > y) or (ey >= y and ey + p.pos[1] < y)
                if crossed:
                    p.pos[1] = y - ey
                    if b["type"] == 0:
                        p.age = p.life
                    else:
                        p.vel[1] = -fx_mul(p.vel[1], b["elasticity_fx16"])
            elif name == "convergence":
                for k in range(3):
                    p.pos[k] += fx_mul(b["force_fx16"], b["target_fx32"][k] - p.pos[k])

    # ---------------------------------------------------------------- one frame (SPLEmitter_Update)
    def update(self):
        em, h, f = self.em, self.em.header, self.em.flags
        if not self.started and self.age >= h["start_delay"]:
            self.started, self.age = True, 0
        if h["emitter_life"] == 0 or self.age < h["emitter_life"]:
            if self.age % max(h["emission_interval"], 1) == 0 and not self.terminated and self.started:
                self._emit()
        air = h["air_resistance"] + 384
        for p in list(self.particles):
            self._anims(p)
            acc = [0, 0, 0]
            if f["follow_emitter"]:
                p.emitter_pos = list(self.pos)
            self._behaviors(p, acc, em.behaviors)
            p.rotation = (p.rotation + p.angular_vel) & 0xFFFF
            p.vel = [(v * air) >> 9 for v in p.vel]
            p.vel = [p.vel[k] + acc[k] for k in range(3)]
            p.pos = [p.pos[k] + p.vel[k] for k in range(3)]
            if f["has_child"]:
                c = em.child
                delay = ((p.life << 12) * (c["emission_delay"] << 12)) >> 12
                diff = (p.age << 12) - (delay >> 8)
                if diff >= 0 and ((diff >> 12) % max(c["emission_interval"], 1)) == 0:
                    self._emit_children(p)
            p.age += 1
            if p.age > p.life:
                self.particles.remove(p)
        if f["has_child"]:
            c = em.child
            for p in list(self.children):
                lr = min(255, (p.age << 8) // p.life)
                if c["has_scale_anim"]:
                    p.anim_scale = c["end_scale_fx16"] + _cdiv((c["end_scale_fx16"] - 4096) * (lr - 255), 255)
                if c["has_alpha_anim"]:
                    p.anim_alpha = ((255 - lr) * 31) // 255
                acc = [0, 0, 0]
                if c["follow_emitter"]:
                    p.emitter_pos = list(self.pos)
                self._behaviors(p, acc, em.behaviors if c["uses_behaviors"] else {})
                p.rotation = (p.rotation + p.angular_vel) & 0xFFFF
                p.vel = [(v * air) >> 9 for v in p.vel]
                p.vel = [p.vel[k] + acc[k] for k in range(3)]
                p.pos = [p.pos[k] + p.vel[k] for k in range(3)]
                p.age += 1
                if p.age > p.life:
                    self.children.remove(p)
        self.age += 1

    @property
    def finished(self) -> bool:
        h = self.em.header
        done = self.em.flags["self_maintaining"] and h["emitter_life"] != 0 and self.started and self.age > h["emitter_life"]
        return bool((done or self.terminated) and not self.particles and not self.children)


def _cdiv(a: int, b: int) -> int:
    """C integer division (truncates toward zero) - Python's ``//`` floors."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _color_anim(a: dict, peak_rgb: int, lr: int) -> int:
    ch = lambda c, s: (c >> s) & 31                                          # noqa: E731
    def mix(c0, c1, num, den):
        out = 0
        for s in (0, 5, 10):
            x, y = ch(c0, s), ch(c1, s)
            out |= ((x + _cdiv(num * (y - x), den)) & 31) << s
        return out
    if lr < a["in"]:
        return a["start_bgr555"]
    if lr < a["peak"]:
        return mix(a["start_bgr555"], peak_rgb, lr - a["in"], max(a["peak"] - a["in"], 1)) if a["interpolate"] else peak_rgb
    if lr < a["out"]:
        return mix(peak_rgb, a["end_bgr555"], lr - a["peak"], max(a["out"] - a["peak"], 1)) if a["interpolate"] else a["end_bgr555"]
    return a["end_bgr555"]


@dataclass
class Replay:
    frames: list = field(default_factory=list)          # per frame: list of particle snapshots
    per_frame_counts: list = field(default_factory=list)
    assumptions: list = field(default_factory=list)
    seed: int = 0
    emitters: list = field(default_factory=list)


ASSUMPTIONS = [
    "RNG seed is caller-supplied (the game seeds gSPLRandomState at run time)",
    "all selected emitters are created at frame 0 at the origin (move-script emitter timing/position is not decoded)",
    "FX_SinIdx/FX_CosIdx are a rounded math.sin stand-in and VEC_Normalize uses floating point, not the NitroSDK tables/fixed sqrt (affects LSBs of placement, not counts or timing)",
    "the rotation sign convention of MTX_RotX/Y/Z33 used by the spin behaviour is not verified (direction of spin could be mirrored)",
    "emitter axis tilt for circle/cylinder/hemisphere emission is not modelled (axes assumed world-aligned, hemisphere up = +Y)",
    "orthographic front camera; world->pixel scale is chosen per preview (the battle camera is not decoded)",
    "draw types polygon/directional/view-space are exposed as flags but rendered as billboards",
]


def replay(spl: SplFile, frames: int = 60, seed: int = 0x2B7E1516, only: list[int] | None = None) -> Replay:
    rng = Lcg(seed)
    chosen = [e for e in spl.emitters if only is None or e.index in only]
    states = [EmitterState(e, rng) for e in chosen]
    rp = Replay(assumptions=list(ASSUMPTIONS), seed=seed, emitters=[e.index for e in chosen])
    for _ in range(frames):
        snap = []
        for st in states:
            st.update()
            for p in st.particles:
                snap.append(_snap(st, p))
            for p in st.children:
                snap.append(_snap(st, p))
        rp.frames.append(snap)
        rp.per_frame_counts.append(len(snap))
    rp.emitted_per_step = [s.emitted_per_step for s in states]
    return rp


def _snap(st: EmitterState, p: Particle) -> dict:
    e = st.em
    h = e.header
    aspect = h["aspect_fx16"]
    if p.child:
        sx = sy = p.base_scale * p.anim_scale >> 12
    else:
        sy = p.base_scale
        sx = fx_mul(sy, aspect)
        d = h["scale_anim_dir"]
        if d == 0:
            sx, sy = fx_mul(sx, p.anim_scale), fx_mul(sy, p.anim_scale)
        elif d == 1:
            sx = fx_mul(sx, p.anim_scale)
        else:
            sy = fx_mul(sy, p.anim_scale)
    alpha = (p.base_alpha * (p.anim_alpha + 1)) >> 5
    return {"emitter": e.index, "child": p.child,
            "x": p.pos[0] + p.emitter_pos[0], "y": p.pos[1] + p.emitter_pos[1], "z": p.pos[2] + p.emitter_pos[2],
            "sx": sx, "sy": sy, "alpha31": alpha, "color": p.color, "texture": p.texture,
            "rotation": p.rotation, "age": p.age, "life": p.life}
