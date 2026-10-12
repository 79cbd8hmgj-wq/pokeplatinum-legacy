#!/usr/bin/env python3
"""Source-free host tests for Opal DAU2 (no donor bytes, no ROM): SPL emitter parser/replay, manifest binding, candidate matrix, guards."""
from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dau1.common import DecodeError                      # noqa: E402
from dau1 import spl as dspl                             # noqa: E402
from dau2 import candidates as C                         # noqa: E402
from dau2 import emitter_study as ES                     # noqa: E402
from dau2 import manifest as M                           # noqa: E402
from dau2 import spl_emitter as E                        # noqa: E402
from dau2 import spl_sim as S                            # noqa: E402
from dau2.roles import MOVE_QUERIES                      # noqa: E402


# ------------------------------------------------------------------ synthetic .spa builder (layout of lib/spl)
def flag_word(**kw) -> int:
    w = 0
    for k, v in kw.items():
        s, n = E.FLAG_BITS[k]
        assert v < (1 << n), k
        w |= v << s
    return w


def header(flags=0, count=1.0, radius=0, life=10, interval=1, start=0, emit_life=0, air=128, base_scale=4096, aspect=4096, tex=0,
           loop_frames=1, rand_life=0, vel_pos=0, vel_axis=0, axis=(0, 0, 0), color=0x7FFF, alpha=31, rot=(0, 0)) -> bytes:
    b = bytearray(0x58)
    struct.pack_into("<I", b, 0, flags)
    struct.pack_into("<III", b, 4, 0, 0, 0)
    struct.pack_into("<III", b, 0x10, int(count * 4096), radius, 0)
    struct.pack_into("<hhh", b, 0x1C, *axis)
    struct.pack_into("<H", b, 0x22, color)
    struct.pack_into("<iii", b, 0x24, vel_pos, vel_axis, base_scale)
    struct.pack_into("<hHhh", b, 0x30, aspect, start, *rot)
    struct.pack_into("<HHHH", b, 0x38, 0, 0, emit_life, life)
    struct.pack_into("<I", b, 0x40, (rand_life & 255) << 8)
    struct.pack_into("<I", b, 0x44, interval | alpha << 8 | air << 16 | tex << 24)
    struct.pack_into("<I", b, 0x48, loop_frames)
    return bytes(b)


def texture(w=8, h=8) -> bytes:
    pix = bytes(range(w * h % 256)) if False else bytes([1] * (w * h))
    pal = struct.pack("<2H", 0, 0x7FFF)
    rec = 0x20 + len(pix) + len(pal)
    s = {8: 0, 16: 1, 32: 2, 64: 3}[w]
    t = {8: 0, 16: 1, 32: 2, 64: 3}[h]
    hd = b" TPS" + struct.pack("<IIIII", 4 | s << 4 | t << 8, len(pix), 0x20 + len(pix), len(pal), rec) + b"\0" * 8
    return hd + pix + pal


def spa(emitters: list[bytes], ntex=1) -> bytes:
    eb = b"".join(emitters)
    tb = b"".join(texture() for _ in range(ntex))
    h = b" APS" + b"12_1" + struct.pack("<HHI", len(emitters), ntex, 0) + struct.pack("<III", len(eb), len(tb), 0x20 + len(eb)) + b"\0" * 4
    assert len(h) == 0x20
    return h + eb + tb


def one(**kw):
    return E.parse_emitters(spa([header(**kw)])).emitters[0]


class Parser(unittest.TestCase):
    def test_minimal_roundtrip_and_tiling(self):
        sp = E.parse_emitters(spa([header(count=1.5, life=7, interval=3)]))
        e = sp.emitters[0]
        self.assertEqual((sp.emitter_count, sp.texture_count, e.size), (1, 1, E.HDR_SIZE))
        self.assertEqual(e.header["emission_count_fx32"], 6144)
        self.assertEqual((e.header["particle_life"], e.header["emission_interval"], e.header["air_resistance"]), (7, 3, 128))

    def test_optional_blocks_follow_flag_order_and_sizes(self):
        fl = flag_word(has_scale_anim=1, has_color_anim=1, has_alpha_anim=1, has_tex_anim=1, has_child=1,
                       has_gravity=1, has_random=1, has_magnet=1, has_spin=1, has_collision=1, has_convergence=1)
        body = (struct.pack("<hhhBBHH", 0, 4096, 2048, 10, 200, 1, 0) +                          # scale 0x0C
                struct.pack("<HHIHH", 0x001F, 0x7C00, 10 | 100 << 8 | 200 << 16, 4, 0) +        # colour 0x0C
                struct.pack("<HHBBH", 0 | 31 << 5 | 20 << 10, 0x0100 | 5, 10, 240, 0) +        # alpha 0x08
                bytes([0, 1, 2, 3, 0, 0, 0, 0]) + struct.pack("<I", 3 | 4 << 8 | 1 << 16) +    # tex anim 0x0C
                struct.pack("<HhhHBBHII", 0, 0, 0, 5, 128, 63, 0x1234, 2 | 1 << 8 | 1 << 16 | 0 << 24, 0) +   # child 0x14
                struct.pack("<hhhH", 0, -50, 0, 0) +                                           # gravity 8
                struct.pack("<hhhH", 10, 10, 10, 4) +                                          # random 8
                struct.pack("<iiihH", 0, 0, 0, 100, 0) +                                       # magnet 0x10
                struct.pack("<HH", 100, 1) +                                                   # spin 4
                struct.pack("<ihH", -4096, 2048, 1) +                                          # collision 8
                struct.pack("<iiihH", 0, 4096, 0, 50, 0))                                      # convergence 0x10
        e = one_with_body(fl, body)
        self.assertEqual(e.size, E.HDR_SIZE + 0x0C + 0x0C + 0x08 + 0x0C + 0x14 + 0x08 + 0x08 + 0x10 + 0x04 + 0x08 + 0x10)
        self.assertEqual((e.scale["mid_fx16"], e.scale["in"], e.scale["out"], e.scale["loop"]), (4096, 10, 200, 1))
        self.assertEqual((e.alpha["mid"], e.alpha["end"], e.alpha["random_range"], e.alpha["loop"]), (31, 20, 5, 1))
        self.assertEqual(e.tex["textures"][:4], [0, 1, 2, 3])
        self.assertEqual((e.tex["frame_count"], e.tex["step"], e.tex["randomize_init"], e.tex["loop"]), (3, 4, 1, 0))
        self.assertEqual((e.child["life"], e.child["velocity_ratio"], e.child["scale_ratio"], e.child["emission_count"]), (5, 128, 63, 2))
        self.assertEqual(e.behaviors["gravity"]["magnitude_fx16"], [0, -50, 0])
        self.assertEqual(e.behaviors["random"]["apply_interval"], 4)
        self.assertEqual((e.behaviors["collision"]["plane_y_fx32"], e.behaviors["collision"]["type"]), (-4096, 1))
        self.assertEqual(e.behaviors["convergence"]["force_fx16"], 50)

    def test_every_truncation_fails_closed(self):
        data = spa([header(flags=flag_word(has_gravity=1)) + struct.pack("<hhhH", 0, -1, 0, 0), header()], ntex=2)
        E.parse_emitters(data)
        for n in range(len(data)):
            with self.assertRaises(DecodeError, msg=f"prefix {n}"):
                E.parse_emitters(data[:n])

    def test_trailing_or_missing_bytes_break_tiling(self):
        good = spa([header(), header()])
        extra = bytearray(good)
        extra[16:20] = struct.pack("<I", struct.unpack_from("<I", good, 16)[0] + 4)   # claim 4 more emitter bytes than records use
        extra[28:] = good[28:]
        data = good[:0x20 + 2 * E.HDR_SIZE] + b"\0\0\0\0" + good[0x20 + 2 * E.HDR_SIZE:]
        data = data[:16] + struct.pack("<II", 2 * E.HDR_SIZE + 4, struct.unpack_from("<I", good, 20)[0]) + struct.pack("<I", 0x20 + 2 * E.HDR_SIZE + 4) + data[28:]
        with self.assertRaises(DecodeError) as cm:
            E.parse_emitters(data)
        self.assertEqual(cm.exception.code, "BAD_OFFSET")

    def test_flag_bits_that_would_overrun_the_block_fail(self):
        # header says 'has child + all behaviours' but the block ends right after the header
        fl = flag_word(has_child=1, has_gravity=1)
        with self.assertRaises(DecodeError) as cm:
            E.parse_emitters(spa([header(flags=fl)]))
        self.assertIn(cm.exception.code, ("TRUNCATED", "BAD_OFFSET"))

    def test_invalid_enumerations_and_limits(self):
        with self.assertRaises(DecodeError) as cm:
            E.parse_emitters(spa([header(flags=10)]))                     # emission type 10 does not exist
        self.assertEqual(cm.exception.code, "BAD_HEADER")
        bad = bytearray(spa([header()]))
        struct.pack_into("<H", bad, 8, 5000)                               # emitter count above the cap
        with self.assertRaises(DecodeError) as cm:
            E.parse_emitters(bytes(bad))
        self.assertEqual(cm.exception.code, "LIMIT")
        with self.assertRaises(DecodeError):
            E.parse_emitters(b"NOPE" + b"\0" * 64)

    def test_signed_fields(self):
        e = one(axis=(0, -4096, 4096), rot=(-100, 200))
        self.assertEqual(e.header["axis_fx16"], [0, -4096, 4096])
        self.assertEqual((e.header["min_rotation"], e.header["max_rotation"]), (-100, 200))

    def test_dau1_texture_decode_unchanged_by_emitter_parse(self):
        data = spa([header(), header()], ntex=3)
        a = dspl.parse_spl(data)                                          # the DAU1 decoder, untouched
        self.assertEqual((a.emitters, len(a.textures)), (2, 3))
        self.assertEqual(sum(1 for t in a.textures if t.frame is not None), 3)
        u, frames = dspl.spl_unit("x", "t.spa", data)
        self.assertEqual((u.status, len(frames)), ("DECODED", 3))


def one_with_body(flags, body):
    return E.parse_emitters(spa([header(flags=flags) + body])).emitters[0]


class Replay(unittest.TestCase):
    def test_lcg_matches_the_documented_recurrence(self):
        r = S.Lcg(1)
        self.assertEqual(r.next(), (1 * 0x5EEDF715 + 0x1B0CB173) & 0xFFFFFFFF)
        r2 = S.Lcg(12345)
        s = 12345
        for _ in range(5):
            s = (s * 0x5EEDF715 + 0x1B0CB173) & 0xFFFFFFFF
            self.assertEqual(r2.next(), s)
        self.assertTrue(0 <= S.Lcg(9).u32(9) < 512)

    def test_fractional_spawn_accumulator(self):
        sp = E.parse_emitters(spa([header(count=1.5, life=100, interval=1)]))
        rp = S.replay(sp, 6)
        self.assertEqual(rp.emitted_per_step[0], [1, 2, 1, 2, 1, 2])

    def test_interval_start_delay_and_emitter_life(self):
        sp = E.parse_emitters(spa([header(count=2, interval=3, start=4, emit_life=7, life=50)]))
        rp = S.replay(sp, 20)
        # emission frames (local age 0,3,6 < 7): global frames 4, 7, 10
        self.assertEqual(rp.emitted_per_step[0], [2, 2, 2])
        self.assertEqual(rp.per_frame_counts[3], 0)
        self.assertEqual(rp.per_frame_counts[4], 2)

    def test_particle_lifetime_bounds_live_count(self):
        # one burst of one particle; lifeTime = ScaledRange(4, 0) + 1 = ((4 * 255) >> 8) + 1 = 4 (source quirk: never the nominal 5)
        sp = E.parse_emitters(spa([header(count=1, life=4, interval=1, emit_life=1)]))
        rp = S.replay(sp, 12)
        live = rp.per_frame_counts
        self.assertEqual(live[:5], [1, 1, 1, 1, 0])
        self.assertEqual(sum(live), 4)

    def test_gravity_closed_form(self):
        # point emitter, no initial velocity, no drag (air=128 -> factor exactly 1), constant acceleration g in fx16
        g = -64
        fl = flag_word(has_gravity=1)
        sp = E.parse_emitters(spa([header(flags=fl, life=100, emit_life=1) + struct.pack("<hhhH", 0, g, 0, 0)]))
        rp = S.replay(sp, 10)
        for t, snap in enumerate(rp.frames):
            self.assertEqual(len(snap), 1)
            n = t + 1                                                      # update count seen by the particle
            self.assertEqual(snap[0]["y"], g * n * (n + 1) // 2, msg=f"frame {t}")

    def test_scale_alpha_curves_follow_lib_spl(self):
        fl = flag_word(has_scale_anim=1, has_alpha_anim=1)
        body = struct.pack("<hhhBBHH", 0, 4096, 8192, 51, 204, 0, 0) + struct.pack("<HHBBH", 0 | 31 << 5 | 0 << 10, 0, 51, 204, 0)
        sp = E.parse_emitters(spa([header(flags=fl, life=254, emit_life=1) + body]))
        rp = S.replay(sp, 255)
        # lifeRate = (lifeFactor * age) >> 8 with lifeFactor = 0xFFFF // 255 = 257: age 0 -> 0; scale rises 0 -> mid over 'in' = 51
        self.assertEqual(rp.frames[0][0]["sx"], 0)
        mid = rp.frames[60][0]
        self.assertEqual(mid["sx"], 4080)      # flat region = 'mid' (1.0) times baseScale 4096 attenuated by DoubleScaledRange(255/256) = 4080
        late = rp.frames[250][0]
        self.assertTrue(4096 < late["sx"] <= 8192)

    def test_sin_stand_in_and_circle_uniform_placement(self):
        self.assertEqual((S.fx_sin(0), S.fx_sin(0x4000), S.fx_sin(0x8000), S.fx_sin(0xC000)), (0, 4096, 0, -4096))
        self.assertEqual((S.fx_cos(0), S.fx_cos(0x4000)), (4096, 0))
        sp = E.parse_emitters(spa([header(flags=flag_word(emission_type=3), radius=2 * 4096, count=4, life=50, emit_life=1)]))
        snap = S.replay(sp, 1).frames[0]
        self.assertEqual(len(snap), 4)
        # source: idx = i * 0x10000 / total; pos = (sin * r, cos * r) -> the four compass points, in either order (list pushes at the front)
        self.assertEqual(sorted((p["x"], p["y"]) for p in snap), sorted([(0, 8192), (8192, 0), (0, -8192), (-8192, 0)]))

    def test_spin_behaviour_is_integer_and_a_quarter_turn_is_exact(self):
        fl = flag_word(has_spin=1, emission_type=1)
        # sphere-surface emission gives a non-zero position; spin 0x4000 about Z (axis 2): (x, y) -> (-y, x)
        sp = E.parse_emitters(spa([header(flags=fl, radius=4096, life=50, emit_life=1) + struct.pack("<HH", 0x4000, 2)]))
        a = S.replay(sp, 2, seed=5).frames
        sp0 = E.parse_emitters(spa([header(flags=flag_word(emission_type=1), radius=4096, life=50, emit_life=1)]))
        b = S.replay(sp0, 2, seed=5).frames
        # frame 0: spin applied once to the freshly emitted position; compare with the unspun run
        x, y = b[0][0]["x"], b[0][0]["y"]
        self.assertEqual((a[0][0]["x"], a[0][0]["y"]), ((0 * x - 4096 * y) >> 12, (4096 * x + 0 * y) >> 12))

    def test_deterministic(self):
        sp = E.parse_emitters(spa([header(flags=flag_word(emission_type=1), radius=4096, count=3, life=20, vel_pos=100)]))
        a, b = S.replay(sp, 30, seed=7), S.replay(sp, 30, seed=7)
        self.assertEqual(a.frames, b.frames)
        self.assertNotEqual(S.replay(sp, 30, seed=8).frames, a.frames)

    def test_invariant_checker_agrees_with_replay(self):
        sp = E.parse_emitters(spa([header(count=0.75, life=9, interval=2, start=1)]))
        rp = S.replay(sp, 40)
        inv = ES.replay_invariants(sp, rp, 40)
        self.assertTrue(inv["spawn_schedule_matches"] and inv["particle_age_within_life"] and inv["within_ds_quad_limit"])


class Studies(unittest.TestCase):
    def test_check_emitters_flags_bad_references(self):
        sp = E.parse_emitters(spa([header(tex=5)], ntex=2))               # texture 5 of 2
        issues, _ = ES.check_emitters(sp)
        self.assertTrue(any("texture_index" in i for i in issues))
        sp = E.parse_emitters(spa([header(interval=0)]))
        self.assertTrue(any("emission_interval" in i for i in ES.check_emitters(sp)[0]))
        self.assertEqual(ES.check_emitters(E.parse_emitters(spa([header()])))[0], [])

    def test_archive_category_and_failure_path(self):
        self.assertEqual(ES.study_archive("x", "x:a", spa([header()]))["category"], "EMITTER_FIELDS_VERIFIED")
        self.assertEqual(ES.study_archive("x", "x:a", spa([header()])[:60])["category"], "DECODED_TEXTURE_ONLY")

    def test_texture_vram_matches_header_bytes(self):
        v = ES.texture_vram(spa([header()], ntex=2))
        self.assertEqual((v["textures"], v["texture_vram_bytes"], v["palette_vram_bytes"]), (2, 128, 8))


# ------------------------------------------------------------------ manifest + candidates
FIXTURE_MANIFEST = {"id": "t", "state": "s", "scope": {}, "moves": (
    [{"move": f"P0m{i}", "tier": "P0_early_frequent", "template": "t", "visual_intent": "v", "status": "design_proposal_unverified", "source_animation": "x"} for i in range(19)] +
    [{"move": f"P1m{i}", "tier": "P1_mid_staples", "template": "t", "visual_intent": "v", "status": "design_proposal_unverified", "source_animation": "x"} for i in range(19)] +
    [{"move": f"P2m{i}", "tier": "P2_status_utility", "template": "t", "visual_intent": "v", "status": "design_proposal_unverified", "source_animation": "x"} for i in range(14)])}


class Manifest(unittest.TestCase):
    def test_sha_pin_and_counts(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.json"
            p.write_text(json.dumps(FIXTURE_MANIFEST))
            with self.assertRaises(M.ManifestError):
                M.load(p)                                                  # not the pinned digest

    def test_slug_aliases(self):
        self.assertEqual((M.slug("ThunderShock"), M.slug("BubbleBeam"), M.slug("Aerial Ace"), M.slug("Double Team")),
                         ("thunder_shock", "bubble_beam", "aerial_ace", "double_team"))

    def test_index_parser(self):
        txt = "## P1 (19)\n- Headbutt — heavy_contact: shoulder/head impact\n## P2 (14)\n- Swords Dance — status_buff: orbiting blades\n"
        self.assertEqual(M.parse_index_md(txt)["P2_status_utility"]["Swords Dance"], ("status_buff", "orbiting blades"))

    def test_bind_reports_missing_script_and_alias(self):
        with tempfile.TemporaryDirectory() as td:
            b = M.bind(FIXTURE_MANIFEST, Path(td))
            self.assertEqual(b["summary"]["p1_p2_scripts_found"], 0)
            self.assertTrue(any(d["kind"] == "MISSING_SCRIPT" for d in b["discrepancies"]))

    def test_all_33_move_queries_exist_and_compile(self):
        import re
        want = {"Headbutt", "Slam", "Wing Attack", "Aerial Ace", "Spark", "Flame Wheel", "Aqua Jet", "BubbleBeam", "Magical Leaf", "Metal Claw", "Rock Tomb",
                "Rock Slide", "Crunch", "Ice Shard", "Icy Wind", "Mud Shot", "Mud Bomb", "Psybeam", "Swift", "Thunder Wave", "Hypnosis", "Confuse Ray",
                "Poison Powder", "Sleep Powder", "Stun Spore", "Swords Dance", "Defense Curl", "Focus Energy", "Sand Attack", "String Shot", "Leech Seed",
                "Supersonic", "Double Team"}
        self.assertEqual(set(MOVE_QUERIES), want)
        for m, comps in MOVE_QUERIES.items():
            self.assertTrue(comps, m)
            for q in comps.values():
                re.compile(q["names"])
                self.assertTrue(q["plat"] and q["feat"]["hues"], m)


def unit(uid, lib, typ, src, vis, tiles=20, frames=3, extra=None):
    ex = {"opal_fx": {"convertible": True, "obj_tiles": tiles, "colours": 8, "max_oams_per_cell": 2, "hue": "red", "translucent_pixels_dropped": 0}}
    ex.update(extra or {})
    return {"id": uid, "library": lib, "source": src, "sha256": "a" * 64, "type": typ, "status": "DECODED", "frame_count": frames, "palette_size": 8,
            "dimensions": {"min": [16, 16], "max": [16, 16]}, "tile_budget": None, "oam_budget": None, "error_reason": None, "members": [],
            "warnings": [], "visual_sha256": vis, "sheet": None, "extra": ex}


FEAT_FIRE = {"usable": True, "bw": 24, "bh": 24, "fill": 0.6, "elong": 1.1, "hollow": 0.0, "components": 1, "dominant_hues": ["orange"], "neutral": None}


class Candidates(unittest.TestCase):
    def test_feature_score_prefers_matching_hue_and_shape(self):
        spec = {"hues": ["red", "orange"], "shape": "orb"}
        self.assertGreater(C.feature_score(FEAT_FIRE, spec), 0.7)
        blue = dict(FEAT_FIRE, dominant_hues=["blue"])
        self.assertLess(C.feature_score(blue, spec), C.feature_score(FEAT_FIRE, spec))
        self.assertEqual(C.feature_score({"usable": False}, spec), 0.0)

    def test_heuristic_scope_excludes_unlabelled_cell_banks(self):
        hg = {"unit": unit("hgss:files/a/0/0/6#12", "hgss", "nitro_cell_bank", "files/a/0/0/6", "v1")}
        pm = {"unit": unit("pmd_sky:files/EFFECT/effect.bin#3", "pmd_sky", "pmd_effect_wan", "files/EFFECT/effect.bin", "v2")}
        self.assertIsNone(C.heuristic_scope(hg))
        self.assertTrue(C.heuristic_scope(pm))

    def _world(self):
        units = [unit("emerald:graphics/battle_anims/sprites/hit.png", "emerald", "gba_indexed_png", "graphics/battle_anims/sprites/hit.png", "e1"),
                 unit("emerald:graphics/battle_anims/sprites/circle_impact.png", "emerald", "gba_indexed_png", "graphics/battle_anims/sprites/circle_impact.png", "e2"),
                 unit("crystal:data/battle_anims/objects.asm#BATTLE_ANIM_OBJ_HIT", "crystal", "gb_recipe_object", "data/battle_anims/objects.asm", "c1"),
                 unit("pmd_sky:files/EFFECT/effect.bin#3", "pmd_sky", "pmd_effect_wan", "files/EFFECT/effect.bin", "p1", extra={"invalid_metaframes": 0, "metaframes": 4}),
                 unit("ranger2:res/prebuilt/data/effect/e1_LZ.bin#4", "ranger2", "nitro_cell_bank", "res/prebuilt/data/effect/e1_LZ.bin", "r1", extra={"pairing": "stem"})]
        plat = [unit("platinum:res/graphics/battle/particles/headbutt.spa", "platinum", "spl_particle_archive", "res/graphics/battle/particles/headbutt.spa", "pl1"),
                unit("platinum:res/graphics/battle/particles/hit_1.spa", "platinum", "spl_particle_archive", "res/graphics/battle/particles/hit_1.spa", "pl2")]
        feats = {u["id"]: dict(FEAT_FIRE) for u in units + plat}
        cat = {"units": units, "sources": [{"library": "emerald", "commit": "abc"}]}
        fd = {"platinum_units": plat, "platinum_order": ["hit_1", "headbutt"], "features": feats, "platinum_revision": "def"}
        binding = {"moves": [{"move": "Headbutt", "tier": "P1_mid_staples", "slug": "headbutt", "template": "heavy_contact",
                              "visual_intent": "x", "anim_script": "res/moves/headbutt/anim.s"}]}
        return cat, fd, binding

    def test_matrix_binds_sources_and_never_approves(self):
        cat, fd, binding = self._world()
        m = C.build_matrix(cat, fd, binding)
        mv = m["moves"][0]
        self.assertEqual(mv["move"], "Headbutt")
        self.assertEqual(mv["visual_decision"], "AWAITING_OWNER_REVIEW")
        bases = {r["evidence_basis"] for r in mv["candidates"]}
        self.assertIn("named_move_particle", bases)
        self.assertIn("named_source", bases)
        self.assertTrue(any(r["evidence"].get("native_same_move") for r in mv["candidates"]))
        for r in mv["candidates"]:
            self.assertEqual(r["visual_review"], {"status": "AWAITING_OWNER_REVIEW", "owner_decision": None, "model_observation": None})
            self.assertIn("redistribution_status", r)
        self.assertEqual(json.dumps(m, sort_keys=True), json.dumps(C.build_matrix(cat, fd, binding), sort_keys=True))   # deterministic

    def test_insufficient_when_too_few_named_renderings(self):
        cat, fd, binding = self._world()
        cat["units"] = [u for u in cat["units"] if u["library"] not in ("emerald", "crystal")]
        fd["platinum_units"] = fd["platinum_units"][:1]
        m = C.build_matrix(cat, fd, binding)
        self.assertEqual(m["moves"][0]["status"], "INSUFFICIENT_VERIFIED_CANDIDATES")
        self.assertTrue(m["moves"][0]["status_reasons"])

    def test_duplicates_collapse_to_the_highest_ranked_library(self):
        cat, fd, binding = self._world()
        cat["units"].append(unit("firered:graphics/battle_anims/sprites/hit.png", "firered", "gba_indexed_png", "graphics/battle_anims/sprites/hit.png", "e1"))
        a = C.build_assets(cat, fd)
        self.assertEqual(a["firered:graphics/battle_anims/sprites/hit.png"]["alias_of"], "emerald:graphics/battle_anims/sprites/hit.png")
        self.assertEqual(a["emerald:graphics/battle_anims/sprites/hit.png"]["also_in"], ["firered:graphics/battle_anims/sprites/hit.png"])

    def test_palette_dependency_reporting(self):
        pm = unit("pmd_sky:x#1", "pmd_sky", "pmd_effect_wan", "x", "v", extra={"invalid_metaframes": 3, "metaframes": 9})
        conf, dep = C.decode_confidence(pm)
        self.assertEqual(conf, "PARTIAL")
        self.assertTrue(dep.startswith("YES"))
        nc = unit("hgss:x#1", "hgss", "nitro_cell_bank", "x", "v", extra={"pairing": "proximity"})
        self.assertEqual(C.decode_confidence(nc)[0], "MEDIUM_PALETTE_PAIRING_HEURISTIC")


class Guards(unittest.TestCase):
    def test_check_gate_rejects_a_tampered_artefact(self):
        import argparse
        import shutil
        from dau2 import cli2
        root = HERE.parents[1]
        src = root / "docs/visual_overhaul/asset_unlock/dau2"
        if not (src / "MOVE_CANDIDATE_MATRIX.json").exists():
            self.skipTest("DAU2 artefacts not generated")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "dau2"
            shutil.copytree(src, out, ignore=shutil.ignore_patterns("*.png", "*.gif"))
            ns = argparse.Namespace(out=out, build=Path(td) / "b", workspace=root.parent, manifest=None, cmd="check")
            self.assertEqual(cli2.cmd_check(ns, root), 0)
            m = json.loads((out / "MOVE_CANDIDATE_MATRIX.json").read_text())
            m["moves"][0]["candidates"][0]["visual_review"]["status"] = "APPROVED"
            (out / "MOVE_CANDIDATE_MATRIX.json").write_text(json.dumps(m))
            self.assertEqual(cli2.cmd_check(ns, root), 1)                    # an approval may not appear anywhere


    def test_tracked_binary_guard_flags_images(self):
        from dau2 import cli2
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "docs/visual_overhaul/asset_unlock/dau2"
            d.mkdir(parents=True)
            (d / "ok.json").write_text("{}")
            self.assertEqual(cli2._tracked_binaries(root, ["docs/visual_overhaul/asset_unlock/dau2"]), [])
            (d / "leak.png").write_bytes(b"\x89PNG")
            self.assertEqual(cli2._tracked_binaries(root, ["docs/visual_overhaul/asset_unlock/dau2"]), ["docs/visual_overhaul/asset_unlock/dau2/leak.png"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
