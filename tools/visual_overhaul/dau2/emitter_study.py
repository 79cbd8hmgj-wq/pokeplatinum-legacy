"""Corpus-wide SPL emitter study + representative offline replays + declarative ``emitter_recipe.json`` export.

Coverage categories (reported with real counts; see EMITTER_RESEARCH.md for what each does and does not prove):
  DECODED_TEXTURE_ONLY      DAU1 baseline: textures decode, emitter block not interpreted
  EMITTER_FIELDS_VERIFIED   emitter block tiles the file exactly AND every parsed field passes the structural checks below
  EMITTER_PREVIEW_VERIFIED  an offline replay exists whose invariants hold against the Platinum lib/spl port (NOT a runtime capture)
  CANDIDATE_REVIEWED        an owner (human) reviewed it as a candidate - always 0 until the owner acts
  BLOCKED_SOURCE            the file is not in the checkout (base-ROM-extracted)
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from dau1 import spl as dspl
from dau1.common import DecodeError
from nitro_narc import read_narc

from . import spl_emitter as E
from . import spl_sim as S

LIB_SPL_REFS = {   # every semantic used by the replay, traced to the matching Platinum source (file:function)
    "resource layout / optional-block order": "lib/spl/src/spl_manager.c:SPLManager_LoadResources",
    "header and flag bit layout": "lib/spl/include/spl_resource.h:SPLResourceHeader/SPLResourceFlags",
    "behaviour record layouts": "lib/spl/include/spl_behavior.h",
    "emitter start/emit gating, per-frame update order": "lib/spl/src/spl_emitter.c:SPLEmitter_Update, spl_manager.c:SPLManager_Update",
    "spawn count (fractional accumulator), emission shapes, initial velocity/scale/life": "lib/spl/src/spl_emit.c:SPLEmitter_EmitParticles",
    "child particles": "lib/spl/src/spl_emit.c:SPLEmitter_EmitChildren",
    "scale/colour/alpha/texture curves": "lib/spl/src/spl_anim.c",
    "gravity/random/magnet/spin/collision/convergence": "lib/spl/src/spl_behavior.c",
    "RNG": "lib/spl/include/spl_random.h:SPLRandom_Next",
    "billboard size = 2*scale (quad -1..1)": "lib/spl/src/spl_draw.c:SPLDraw_Billboard/SPLUtil_DrawXYPlane",
}


def iter_corpus(ws: Path, root: Path):
    """Yield (library, id, relpath, member, bytes) for every .spa reachable: Platinum res/, Diamond loose .bin, HGSS NARC members."""
    for p in sorted((root / "res").rglob("*.spa")):
        rel = p.relative_to(root).as_posix()
        yield "platinum", f"platinum:{rel}", rel, None, p.read_bytes()
    d = ws / "pokediamond"
    if d.is_dir():
        for dp, dn, fn in os.walk(d / "files"):
            dn.sort()
            for f in sorted(fn):
                p = Path(dp) / f
                if p.suffix == ".bin" and p.stat().st_size >= 32:
                    with open(p, "rb") as fh:
                        if fh.read(4) != b" APS":
                            continue
                    rel = p.relative_to(d).as_posix()
                    yield "diamond", f"diamond:{rel}", rel, None, p.read_bytes()
    h = ws / "pokeheartgold"
    if h.is_dir():
        for dp, dn, fn in os.walk(h / "files"):
            dn.sort()
            for f in sorted(fn):
                p = Path(dp) / f
                with open(p, "rb") as fh:
                    if fh.read(4) != b"NARC":
                        continue
                try:
                    members, _ = read_narc(p)
                except Exception:                                          # noqa: BLE001
                    continue
                rel = p.relative_to(h).as_posix()
                for k, m in enumerate(members):
                    if m[:4] == b" APS":
                        yield "hgss", f"hgss:{rel}#{k}", rel, k, m


def check_emitters(spl: E.SplFile) -> tuple[list[str], int]:
    """Structural sanity checks on parsed fields. Returns (issues, nonzero_reserved_count)."""
    issues, nz = [], 0
    nt = spl.texture_count
    for e in spl.emitters:
        h, f, tag = e.header, e.flags, f"emitter {e.index}"
        if h["particle_life"] == 0 and f["has_child"] == 0:
            issues.append(f"{tag}: particle_life 0")
        if h["emission_interval"] == 0:
            issues.append(f"{tag}: emission_interval 0 (game divides by it)")
        if h["loop_frames"] == 0:
            issues.append(f"{tag}: loop_frames 0 (game divides by it)")
        if not f["has_tex_anim"] and nt and h["texture_index"] >= nt:
            issues.append(f"{tag}: texture_index {h['texture_index']} >= {nt}")
        if e.tex:
            if not 1 <= e.tex["frame_count"] <= 8:
                issues.append(f"{tag}: tex anim frame_count {e.tex['frame_count']}")
            for t in e.tex["textures"][: min(e.tex["frame_count"], 8)]:
                if nt and t >= nt:
                    issues.append(f"{tag}: tex anim texture {t} >= {nt}")
        if e.child and nt and e.child["texture"] >= nt:
            issues.append(f"{tag}: child texture {e.child['texture']} >= {nt}")
        if e.child and e.child["life"] == 0:
            issues.append(f"{tag}: child life 0")
        if "random" in e.behaviors and e.behaviors["random"]["apply_interval"] == 0:
            issues.append(f"{tag}: random behaviour interval 0 (game takes modulo)")
        for k, v in e.unknown.items():
            vals = v if isinstance(v, list) else [v]
            nz += sum(1 for x in vals if x)
    return issues, nz


def study_archive(lib: str, uid: str, data: bytes) -> dict:
    rec = {"id": uid, "library": lib, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    try:
        spl = E.parse_emitters(data)
    except DecodeError as e:
        rec.update(category="DECODED_TEXTURE_ONLY", parse_error=f"{e.code}: {e.message}")
        return rec
    issues, nz = check_emitters(spl)
    kinds = {}
    for e in spl.emitters:
        kinds[E.EMISSION_TYPES[e.flags["emission_type"]]] = kinds.get(E.EMISSION_TYPES[e.flags["emission_type"]], 0) + 1
    rec.update(category="EMITTER_FIELDS_VERIFIED" if not issues else "EMITTER_FIELDS_PARSED_WITH_ANOMALIES",
               emitters=spl.emitter_count, textures=spl.texture_count, emitter_block_bytes=spl.emitter_block_size,
               emission_types=dict(sorted(kinds.items())), nonzero_reserved_fields=nz, issues=issues[:6], issue_count=len(issues),
               features={"children": sum(1 for e in spl.emitters if e.child), "behaviors": sum(len(e.behaviors) for e in spl.emitters),
                         "scale_anim": sum(1 for e in spl.emitters if e.scale), "alpha_anim": sum(1 for e in spl.emitters if e.alpha),
                         "color_anim": sum(1 for e in spl.emitters if e.color), "tex_anim": sum(1 for e in spl.emitters if e.tex)})
    return rec


def texture_vram(data: bytes) -> dict:
    """Texture/palette byte totals straight from the .spa texture records (Nitro texture VRAM; palette VRAM separate)."""
    from dau1.common import Reader
    r = Reader(data)
    ntex, tex_off = r.u16(10), r.u32(24)
    pos, tex_b, pal_b = tex_off, 0, 0
    for _ in range(ntex):
        pix, pal = r.u32(pos + 8), r.u32(pos + 16)
        tex_b += pix
        pal_b += pal
        pos += r.u32(pos + 20)
    return {"textures": ntex, "texture_vram_bytes": tex_b, "palette_vram_bytes": pal_b}


# ------------------------------------------------------------------------------------------- replay + recipe
DS_QUAD_LIMIT = 1536          # 6144 vertices / 4 per quad (GX vertex RAM); the 2048-polygon cap is higher


def replay_invariants(spl: E.SplFile, rp: S.Replay, frames: int) -> dict:
    """Checks that must hold if the port of SPLEmitter_Update is internally consistent with the parsed fields."""
    res = {}
    expect_spawn = []
    for e in spl.emitters:
        if e.index not in rp.emitters:
            continue
        h = e.header
        st = 0
        acc = 0
        age = h["start_delay"]              # emission starts at age 0 after the start delay
        series = []
        # expected per-emission-step spawn counts from the fractional accumulator alone
        steps = 0
        n_emit_frames = 0
        for f in range(frames):
            started = f >= h["start_delay"]
            local = f - h["start_delay"] if started else 0
            if started and (h["emitter_life"] == 0 or local < h["emitter_life"]) and local % max(h["emission_interval"], 1) == 0:
                tot = h["emission_count_fx32"] + acc
                series.append(tot >> 12)
                acc = tot & 0xFFF
        expect_spawn.append(series)
    res["spawn_schedule_matches"] = bool(expect_spawn) and all(
        s[: len(rp.emitted_per_step[i])] == rp.emitted_per_step[i][: len(s)] and len(s) == len(rp.emitted_per_step[i])
        for i, s in enumerate(expect_spawn))
    max_age_ok = all(p["age"] <= p["life"] + 1 for fr in rp.frames for p in fr)
    res["particle_age_within_life"] = max_age_ok
    res["peak_live_particles"] = max(rp.per_frame_counts) if rp.per_frame_counts else 0
    res["within_ds_quad_limit"] = res["peak_live_particles"] <= DS_QUAD_LIMIT
    res["deterministic"] = None            # filled by caller (replay twice)
    return res


def recipe(game_label: str, source: dict, spl: E.SplFile, data: bytes, rp: S.Replay, inv: dict, cross: dict, frames: int, opal_fx: dict | None) -> dict:
    vram = texture_vram(data)
    peak = max(rp.per_frame_counts) if rp.per_frame_counts else 0
    return {
        "schema": "emitter_recipe/1",
        "purpose": "declarative description of a decoded SPL effect for later hand-mapping into Opal's existing animation macros; NOT a runtime interpreter",
        "source": source,
        "verified_fields": {"emitters": [e.to_json() for e in spl.emitters if e.index in rp.emitters]},
        "semantics_source": LIB_SPL_REFS,
        "unknowns": [
            "which emitters the move script actually creates, when, and where (battle script / particle-index tables not decoded)",
            "emitter user-callback behaviour (position/velocity updates driven by the battle engine)",
            "real battle camera and world->screen scale",
            "NitroSDK fixed-point sin/cos tables and normalise (rounded math.sin / float stand-ins used); MTX_Rot*33 sign convention of the spin behaviour unverified",
            "draw-time semantics of polygon / directional / view-space draw types (flags kept, not simulated)",
            "initial gSPLRandomState (caller seed)",
        ],
        "replay": {"frames": frames, "seed": rp.seed, "emitters_replayed": rp.emitters, "assumptions": rp.assumptions,
                   "per_frame_live_particles": rp.per_frame_counts, "spawned_per_emission_step": rp.emitted_per_step, "invariants": inv},
        "cross_game_agreement": cross,
        "resource_estimate": {"gx_3d": {"peak_live_particles": peak, "polygons_per_frame_peak": peak, "vertices_per_frame_peak": peak * 4,
                                        "ds_vertex_limit": 6144, **vram, "texture_vram_note": "bytes from the .spa texture records; VRAM placement not modelled"},
                              "obj_conversion_if_flattened": opal_fx or "not estimated (texture-only DAU1 estimate unavailable)",
                              "claim_limit": "static counts from the replay and file headers; not a performance measurement"},
        "status": "EMITTER_PREVIEW_VERIFIED_AGAINST_SOURCE_PORT_NOT_RUNTIME_CAPTURED",
    }
