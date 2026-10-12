#!/usr/bin/env python3
"""Host-side, ROM-free tests for the DAU1 donor-asset toolkit.

Every fixture is synthesised in this file (no donor bytes).  Covers malformed / truncated input at every prefix length,
invalid offsets and palette indices, determinism, duplicate detection, catalog schema rules, the Opal-FX conversion gate
and the candidate matrix.  Source-dependent checks live in ``test_dau1_sources.py`` and skip when donors are absent.

  python3 tools/visual_overhaul/test_dau1.py
"""
import json
import struct
import warnings
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from dau1 import bundle as bd                                  # noqa: E402
from dau1 import catalog as cat                                # noqa: E402
from dau1 import common, fx_convert, gb, matrix, nitro2d as n2, nitro_library as nl, pmd_effect as pe, spl  # noqa: E402
from dau1.render import Frame, frames_hash                     # noqa: E402
from nitro_narc import lz10_compress                           # noqa: E402


# ------------------------------------------------------------------------------------ builders
def u16(v): return struct.pack("<H", v)
def u32(v): return struct.pack("<I", v)


def nitro_file(magic: bytes, blocks: list[bytes], declared_size: int | None = None) -> bytes:
    body = b"".join(blocks)
    size = 16 + len(body) if declared_size is None else declared_size
    return magic + b"\xff\xfe\x00\x01" + u32(size) + u16(16) + u16(len(blocks)) + body


def bgr(r, g, b): return (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10


def nclr(colors: list[int], declared_size=None, depth=3, trunc=0) -> bytes:
    data = b"".join(u16(c) for c in colors)
    blk = b"TTLP" + u32(0x18 + len(data)) + u32(depth) + u32(0) + u32(len(data) + trunc) + u32(0x10) + data
    return nitro_file(b"RLCN", [blk], declared_size)


def ncgr(tiles: list[bytes], tiles_x=0xFFFF, tiles_y=0xFFFF, mapping=0, scan=0, fmt=3, size_override=None) -> bytes:
    """tiles: 64 palette indices each (4bpp packed here)."""
    body = b""
    for t in tiles:
        for i in range(0, 64, 2):
            body += bytes([t[i] | t[i + 1] << 4])
    blk = b"RAHC" + u32(0x20 + len(body)) + u16(tiles_y) + u16(tiles_x) + u32(fmt) + u32(mapping) + u32(scan) \
        + u32(len(body) if size_override is None else size_override) + u32(0x18) + body
    return nitro_file(b"RGCN", [blk])


def ncer(cells: list[list[tuple[int, int, int]]], mapping=0) -> bytes:
    table, oams = b"", b""
    for c in cells:
        table += u16(len(c)) + u16(0) + u32(len(oams))
        for a in c:
            oams += u16(a[0]) + u16(a[1]) + u16(a[2])
    hdr = u16(len(cells)) + u16(0) + u32(0x18) + u32(mapping) + u32(0) + u32(0) + u32(0)
    blk = b"KBEC" + u32(8 + len(hdr) + len(table) + len(oams)) + hdr + table + oams
    return nitro_file(b"RECN", [blk])


def nanr(seqs: list[list[tuple[int, int]]]) -> bytes:
    sq, fr, dat = b"", b"", b""
    for s in seqs:
        sq += u16(len(s)) + u16(0) + u32(1) + u32(1) + u32(len(fr))
        for cell, dur in s:
            fr += u32(len(dat)) + u16(dur) + u16(0xBEEF)
            dat += u16(cell) + u16(0)
    off_s = 0x18
    off_f = off_s + len(sq)
    off_d = off_f + len(fr)
    blk = b"KNBA" + u32(0x20 + len(sq) + len(fr) + len(dat)) + u16(len(seqs)) + u16(sum(len(s) for s in seqs)) \
        + u32(off_s) + u32(off_f) + u32(off_d) + u32(0) + u32(0) + sq + fr + dat
    return nitro_file(b"RNAN", [blk])


def narc(members: list[bytes], names: list[str] | None = None) -> bytes:
    fatb = b"BTAF" + u32(12 + 8 * len(members)) + u32(len(members))
    img = b""
    for m in members:
        while len(img) % 4:
            img += b"\xff"
        fatb += u32(len(img)) + u32(len(img) + len(m))
        img += m
    if names:
        sub = b"".join(bytes([len(n)]) + n.encode() for n in names) + b"\x00"
        fnt_body = u32(8) + u16(0) + u16(1) + sub
    else:
        fnt_body = u32(4) + u16(0) + u16(1)
    fnt = b"BTNF" + u32(8 + len(fnt_body)) + fnt_body
    gm = b"GMIF" + u32(8 + len(img)) + img
    total = 16 + len(fatb) + len(fnt) + len(gm)
    return b"NARC" + b"\xfe\xff\x00\x01" + u32(total) + u16(16) + u16(3) + fatb + fnt + gm


def solid_tile(v): return bytes([v]) * 64
def ramp_tile(): return bytes((i % 15) + 1 for i in range(64))


def blob():
    """A coherent synthetic bank: 2 cells over 4 tiles, 16-colour palette."""
    pal = [0] + [bgr(10 * i, 255 - 10 * i, 128) for i in range(1, 16)]
    tiles = [solid_tile(1), solid_tile(2), ramp_tile(), solid_tile(3)]
    cells = [[(0x0000, 0x0000, 0x0000)],                                    # 8x8 at (0,0) tile 0
             [(0x0000, 0x0000, 0x0001), (0x0008, 0x0008, 0x0002)]]          # two 8x8
    return ncer(cells), ncgr(tiles, tiles_x=4, tiles_y=1, mapping=0x10), nclr(pal), nanr([[(0, 4), (1, 4)]])


# ------------------------------------------------------------------------------------ tests
class Lz(unittest.TestCase):
    def test_roundtrip_and_determinism(self):
        data = bytes(range(200)) * 5 + b"abcabcabc" * 50
        c = lz10_compress(data)
        self.assertEqual(common.lz_decompress(c), data)
        self.assertEqual(lz10_compress(data), c)

    def test_every_truncation_is_a_decode_error(self):
        c = lz10_compress(bytes(range(256)) * 4)
        for n in range(len(c) - 1):
            with self.assertRaises(common.DecodeError) as cm:
                common.lz_decompress(c[:n])
            self.assertIn(cm.exception.code, ("TRUNCATED", "BAD_MAGIC"))

    def test_bad_backreference_and_limit(self):
        bad = bytes([0x10, 4, 0, 0, 0x80, 0x00, 0x05])          # copy 3 bytes from distance 6 with empty output
        with self.assertRaises(common.DecodeError) as cm:
            common.lz_decompress(bad)
        self.assertEqual(cm.exception.code, "BAD_OFFSET")
        with self.assertRaises(common.DecodeError) as cm:
            common.lz_decompress(bytes([0x10, 0xFF, 0xFF, 0xFF]) + b"\0" * 8, limit=1000)
        self.assertEqual(cm.exception.code, "LIMIT")

    def test_lz11(self):
        # flag byte 0x40: literal 'A', then copy len 3 (nibble 2) dist 1 -> "AAAA"
        stream = bytes([0x11, 4, 0, 0, 0x40, 0x41, 0x20, 0x00])
        self.assertEqual(common.lz_decompress(stream), b"AAAA")


class Narc(unittest.TestCase):
    def test_parse_and_names(self):
        n = narc([b"hello", b"world!!!"], ["a.bin", "b.bin"])
        ms = n2.parse_narc(n)
        self.assertEqual([m.data for m in ms], [b"hello", b"world!!!"])
        self.assertEqual([m.name for m in ms], ["a.bin", "b.bin"])
        self.assertTrue(all(m.name is None for m in n2.parse_narc(narc([b"x"]))))

    def test_every_prefix_fails_cleanly(self):
        n = narc([b"abcdefgh", b"ijkl"])
        for k in range(len(n)):
            try:
                n2.parse_narc(n[:k])
            except common.DecodeError:
                pass                                              # expected; anything else (IndexError, struct.error) fails

    def test_member_outside_fimg(self):
        n = bytearray(narc([b"abcdefgh"]))
        n[16 + 12 + 4:16 + 12 + 8] = u32(0x1000)                  # member end beyond the image block
        with self.assertRaises(common.DecodeError) as cm:
            n2.parse_narc(bytes(n))
        self.assertEqual(cm.exception.code, "BAD_OFFSET")


class Nitro2D(unittest.TestCase):
    def test_nclr_quirks(self):
        pal = [bgr(255, 0, 0), bgr(0, 255, 0)]
        p = n2.parse_nclr(nclr(pal, declared_size=32))           # Ranger quirk: wrong declared size
        self.assertEqual(p.colors, pal)
        self.assertTrue(p.warnings)
        t = n2.parse_nclr(nclr(pal, trunc=8))                     # header over-states the data
        self.assertEqual(t.colors, pal)
        self.assertTrue(any("truncated" in w for w in t.warnings))
        with self.assertRaises(common.DecodeError):
            n2.parse_nclr(nclr([], declared_size=None))

    def test_ncgr_decode_and_rejections(self):
        cd = n2.parse_ncgr(ncgr([ramp_tile(), solid_tile(5)], tiles_x=2, tiles_y=1))
        self.assertEqual(cd.tile_count, 2)
        _, tiles = cd.tiles()
        self.assertEqual(tiles[1], solid_tile(5))
        self.assertEqual(tiles[0][:3], bytes([1, 2, 3]))
        with self.assertRaises(common.DecodeError) as cm:
            n2.parse_ncgr(ncgr([solid_tile(1)], fmt=5))
        self.assertEqual(cm.exception.code, "UNSUPPORTED")
        with self.assertRaises(common.DecodeError) as cm:
            n2.parse_ncgr(ncgr([solid_tile(1)], tiles_x=3, tiles_y=3))
        self.assertEqual(cm.exception.code, "BAD_HEADER")
        with self.assertRaises(common.DecodeError):
            n2.parse_ncgr(ncgr([solid_tile(1)], size_override=4000))

    def test_ncer_bad_oam_range(self):
        data = bytearray(ncer([[(0, 0, 0)]]))
        # corrupt the cell's OAM count so its OAM run exceeds the block
        cell_table = 16 + 8 + 0x18
        data[cell_table:cell_table + 2] = u16(500)
        with self.assertRaises(common.DecodeError) as cm:
            n2.parse_ncer(bytes(data))
        self.assertEqual(cm.exception.code, "BAD_OFFSET")

    def test_all_prefixes_of_every_format_fail_cleanly(self):
        for blobdata, fn in zip(blob(), (n2.parse_ncer, n2.parse_ncgr, n2.parse_nclr, n2.parse_nanr)):
            for k in range(len(blobdata)):
                try:
                    fn(blobdata[:k])
                except common.DecodeError:
                    pass

    def test_nanr(self):
        a = n2.parse_nanr(nanr([[(0, 3), (2, 5)], [(1, 1)]]))
        self.assertEqual(a.sequences, [[(0, 3), (2, 5)], [(1, 1)]])

    def test_render_1d_flip_and_unmapped(self):
        chars = [solid_tile(1), solid_tile(2)] + [bytes(64)] * 2
        rc = n2.render_cell([(0x0000, 0x1000, 0x0000)], chars, 4, 0x10, 4)       # hflip, tile 0
        self.assertEqual(rc.width, 8)
        self.assertEqual(set(rc.pixels), {1})
        far = n2.render_cell([(0x0000, 0x0000, 0x0050)], chars, 4, 0x10, 4)
        self.assertEqual(far.unmapped_tiles, 1)
        self.assertTrue(far.blank)

    def test_2d_mapping_uses_32_tile_rows(self):
        chars = [bytes(64)] * 40
        chars[32] = solid_tile(7)                                  # row 1, col 0 in a 32-wide sheet
        rc = n2.render_cell([(0, 0, 32)], chars, 32, 0, 4)
        self.assertEqual(set(rc.pixels), {7})


class Bundles(unittest.TestCase):
    def test_decoded_bundle(self):
        r = bd.decode_cell_bundle(*blob())
        self.assertEqual(r.status, common.DECODED)
        self.assertEqual(r.valid_frames, 2)
        self.assertEqual(r.oam_budget, 2)
        self.assertEqual(r.tile_budget, 3)
        self.assertEqual(r.anim_sequences, 1)
        self.assertTrue(r.visual_sha256)

    def test_invalid_palette_index_is_reported_not_hidden(self):
        ce, ch, _, an = blob()
        r = bd.decode_cell_bundle(ce, ch, nclr([0]), an)             # 1 colour: every visible pixel is out of range
        self.assertEqual(r.status, common.STRUCTURAL_ONLY)
        self.assertIn("palette", r.reason)
        r2 = bd.decode_cell_bundle(ce, ch, nclr([0, bgr(255, 0, 0)]), an)   # 2 colours: cell 1 overflows, cell 0 is fine
        self.assertEqual(r2.status, common.DECODED)
        self.assertEqual(r2.invalid_cells, [1])
        self.assertTrue(any("outside" in w for w in r2.warnings))

    def test_out_of_range_tiles_make_cells_invalid(self):
        ce = ncer([[(0, 0, 0)], [(0, 0, 0x30)]])                   # second cell points far outside 4 tiles
        _, ch, pal, _ = blob()
        r = bd.decode_cell_bundle(ce, ch, pal)
        self.assertEqual(r.status, common.DECODED)
        self.assertEqual(r.invalid_cells, [1])
        self.assertEqual(r.valid_frames, 1)

    def test_all_blank_is_not_decoded(self):
        ce, _, pal, _ = blob()
        ch = ncgr([bytes(64)] * 4, tiles_x=4, tiles_y=1, mapping=0x10)
        r = bd.decode_cell_bundle(ce, ch, pal)
        self.assertEqual(r.status, common.STRUCTURAL_ONLY)

    def test_garbage_inputs(self):
        r = bd.decode_cell_bundle(b"junk", b"junk", b"junk")
        self.assertEqual(r.status, common.UNSUPPORTED)


class Library(unittest.TestCase):
    def archive(self, pal_index_gap=0):
        ce, ch, pal, an = blob()
        members = [ch, pal, ce, an]
        if pal_index_gap:
            members = [ch] + [nclr([0, 1])] * pal_index_gap + [ce, an]       # palette(s) far from the bank
        return narc(members)

    def test_adjacent_pairing_decodes(self):
        units, sheets, previews = nl.scan_container("hgss", "x.narc", self.archive())
        banks = [u for u in units if u.type == "nitro_cell_bank"]
        self.assertEqual(len(banks), 1)
        self.assertEqual(banks[0].status, common.DECODED)
        self.assertEqual(banks[0].frame_count, 2)
        self.assertEqual(len(sheets[banks[0].id]), 2)

    def test_distant_palette_is_not_counted_as_decoded(self):
        ce, ch, pal, an = blob()
        far = narc([pal, nclr([0, 1])] + [ch] * 8 + [ce, an])         # two palettes, both >4 members from the bank
        units, sheets, previews = nl.scan_container("hgss", "far.narc", far)
        bank = [u for u in units if u.type == "nitro_cell_bank"][0]
        self.assertEqual(bank.status, common.STRUCTURAL_ONLY)
        self.assertIn("outside the archive", bank.error_reason)
        self.assertNotIn(bank.id, sheets)
        self.assertIn(bank.id, previews)

    def test_determinism_and_duplicates(self):
        a = self.archive()
        u1, _, _ = nl.scan_container("hgss", "x.narc", a)
        u2, _, _ = nl.scan_container("hgss", "x.narc", a)
        self.assertEqual([u.to_json() for u in u1], [u.to_json() for u in u2])
        ua, _, _ = nl.scan_container("hgss", "a.narc", a)
        ub, _, _ = nl.scan_container("diamond", "b.narc", a)
        dup = cat.find_duplicates([u.to_json() for u in ua + ub])
        self.assertTrue(any(k.startswith("visual_sha256:") for k in dup["cross_library_groups"]))

    def test_lz_wrapped_members_and_screens_aggregate(self):
        ce, ch, pal, an = blob()
        wrapped = narc([lz10_compress(ch), pal, lz10_compress(ce), lz10_compress(an)])
        units, _, _ = nl.scan_container("hgss", "lz.narc", wrapped)
        self.assertEqual([u.status for u in units if u.type == "nitro_cell_bank"], [common.DECODED])

    def test_corrupt_container_reports_unsupported(self):
        units, _, _ = nl.scan_container("hgss", "bad.narc", b"NARC" + b"\0" * 40)
        self.assertEqual(units[0].status, common.UNSUPPORTED)
        self.assertTrue(units[0].error_reason)


# ---- PMD effect WAN synthetic ------------------------------------------------------------------
def sir0(content: bytes, content_off_in_body: int, reloc_offsets: list[int]) -> bytes:
    """Wrap ``content`` (placed at file offset 16) into a SIR0 with a relocation list for the given file offsets."""
    body = content
    plist_off = 16 + len(body)
    enc, prev = b"", 0
    for off in sorted(reloc_offsets):
        d, chunks = off - prev, []
        prev = off
        chunks.append(d & 0x7F)
        d >>= 7
        while d:
            chunks.append((d & 0x7F) | 0x80)
            d >>= 7
        enc += bytes(reversed(chunks))
    enc += b"\x00"
    return b"SIR0" + u32(16 + content_off_in_body) + u32(plist_off) + u32(0) + body + enc


def synthetic_effect_wan(is256=0, pal_selector=0, bad_pixel=False, pieces=1):
    """4bpp type-2 sprite: one 8x8 image, one metaframe of `pieces` 1x1-tile pieces, one 3-colour palette row."""
    img = bytes([0x21, 0x43, 0x65, 0x07] * 8)                   # 64 px (4bpp) = 32 bytes; values 1..7 (0x07 hi nibble 0)
    if is256:
        img = bytes(range(16, 32)) * 4                          # 64 px values 16..31 (8bpp)
        if bad_pixel:
            img = bytes([40] * 64)                              # 256-colour sprites may only use values 16..31
    body = bytearray()
    base = 16
    ptr_pixels = base + len(body); body += img + bytes(-len(img) % 4)
    pal_off = base + len(body); body += b"".join(bytes([r, g, b, 0]) for r, g, b in [(0, 0, 0), (248, 0, 0), (0, 248, 0), (0, 0, 248)] + [(8, 8, 8)] * 12)
    strip_off = base + len(body); body += u32(ptr_pixels) + u16(len(img)) + u16(0) + u32(0) + u32(0) + u32(0)
    imgtab = base + len(body); body += u32(strip_off)
    pal_info = base + len(body); body += u32(pal_off) + u16(1) + u16(16) + u16(1) + u16(0xFF)
    img_info = base + len(body); body += u32(imgtab) + u32(pal_info) + u16(1) + u16(is256) + u16(1) + u16(1)
    piece = bytearray()
    for k in range(pieces):
        last = 1 if k == pieces - 1 else 0
        piece += b"\xff\xff\x00\x00" + u16(252 + 0) + u16(256 + 8 * k + (last << 11)) + bytes([0, pal_selector << 4])
    mf = base + len(body); body += bytes(piece)
    frame = base + len(body); body += u16(4) + u16(0) + u16(0) + u16(0) + u16(0) + u16(0) + bytes(12)      # duration 4 + terminator (dur 0)
    mf_tab = base + len(body); body += u32(mf)
    seq_tab = base + len(body); body += u32(frame)
    grp_tab = base + len(body); body += u32(seq_tab) + u16(1) + u16(0)
    anim_info = base + len(body); body += u32(mf_tab) + u32(0) + u32(grp_tab) + u16(1) + u16(0)
    hdr = base + len(body); body += u32(anim_info) + u32(img_info) + u16(2) + u16(1)
    relocs = [4, 8, strip_off, imgtab, pal_info, img_info, mf_tab, seq_tab, grp_tab, anim_info, hdr, hdr + 4]
    return sir0(bytes(body), hdr - base, relocs)


class PmdEffect(unittest.TestCase):
    def test_synthetic_sprite_decodes(self):
        r = pe.decode_effect_entry(synthetic_effect_wan())
        self.assertEqual(r.status, common.DECODED, r.reason)
        self.assertEqual(len(r.frames), 1)
        self.assertGreater(r.frames[0].opaque_pixels, 0)
        self.assertEqual(r.palette_rows, 1)

    def test_unresolvable_palette_row_is_never_guessed(self):
        r = pe.decode_effect_entry(synthetic_effect_wan(pal_selector=9))
        self.assertEqual(r.status, common.UNSUPPORTED)
        self.assertIn("palette", r.reason)

    def test_pixel_outside_palette_row(self):
        ok = pe.decode_effect_entry(synthetic_effect_wan(is256=1))
        self.assertEqual(ok.status, common.DECODED, ok.reason)
        r = pe.decode_effect_entry(synthetic_effect_wan(is256=1, bad_pixel=True))
        self.assertEqual(r.status, common.UNSUPPORTED)
        self.assertFalse(r.frames)

    def test_every_prefix_fails_cleanly_and_deterministically(self):
        data = synthetic_effect_wan(pieces=2)
        a = pe.decode_effect_entry(data)
        self.assertEqual(a.status, common.DECODED, a.reason)
        for k in range(len(data)):
            r = pe.decode_effect_entry(data[:k])               # must not raise
            self.assertNotEqual(r.status, common.DECODED, k)
        self.assertEqual(frames_hash(a.frames), frames_hash(pe.decode_effect_entry(data).frames))

    def test_pack_validation(self):
        good = u32(0) + u32(1) + u32(16) + u32(4) + b"SIR0"
        self.assertEqual(pe.parse_pack(good), [(16, 4)])
        for bad in (u32(1) + u32(1) + u32(16) + u32(4) + b"SIR0",       # first word must be 0
                    u32(0) + u32(0) + b"\0" * 8,                          # no entries
                    u32(0) + u32(1) + u32(16) + u32(99) + b"SIR0",        # entry beyond file
                    u32(0) + u32(1000)):                                  # table beyond file
            with self.assertRaises(common.DecodeError):
                pe.parse_pack(bad)

    def test_sir0_rejects_bad_pointers(self):
        with self.assertRaises(common.DecodeError):
            pe.parse_sir0(b"SIR0" + u32(9999) + u32(9999) + u32(0))
        with self.assertRaises(common.DecodeError):
            pe.parse_sir0(b"NOPE" + b"\0" * 12)

    def test_non_sir0_entry_is_structural_only(self):
        self.assertEqual(pe.decode_effect_entry(b"\x02\0\0\0" + b"\0" * 20).status, common.STRUCTURAL_ONLY)


# ---- SPL synthetic ------------------------------------------------------------------------------
def synthetic_spa(fmt=6, s=1, t=1, bad_pal_index=False, wrong_size=False, textures=1):
    w, h = 8 << s, 8 << t
    bits = {1: 8, 2: 2, 3: 4, 4: 8, 6: 8, 7: 16}[fmt]
    px = bytearray(w * h * bits // 8)
    for i in range(len(px)):
        if fmt == 6:
            px[i] = 0xF8 if i % 3 == 0 else 0x08
        elif fmt == 1:
            px[i] = 0xE1 if i % 3 == 0 else 0x21
        else:
            px[i] = 7 if bad_pal_index else 1
    pal = u16(0x7FFF) + u16(0x001F)
    param = fmt | s << 4 | t << 8 | 3 << 12 | 3 << 14 | 1 << 16
    pix = len(px) + (4 if wrong_size else 0)
    rec = b" TPS" + u32(param) + u32(pix) + u32(0x20 + len(px)) + u32(len(pal)) + u32(0x20 + len(px) + len(pal)) + u32(0) * 2 + bytes(px) + pal
    res = b"\0" * 0x30
    tex = rec * textures
    return b" APS" + b"12_1" + u16(1) + u16(textures) + u32(0) + u32(len(res)) + u32(len(tex)) + u32(0x20 + len(res)) + u32(0) + res + tex


class Spl(unittest.TestCase):
    def test_decodes_a5i3_with_alpha(self):
        u, frames = spl.spl_unit("x", "a.spa", synthetic_spa())
        self.assertEqual(u.status, common.DECODED, u.error_reason)
        self.assertEqual((frames[0].width, frames[0].height), (16, 16))
        alphas = {frames[0].rgba[i] for i in range(3, len(frames[0].rgba), 4)}
        self.assertTrue(len(alphas) > 1)
        self.assertEqual(u.extra["emitters"], 1)
        self.assertIsNone(u.oam_budget)

    def test_palette_formats(self):
        for fmt in (2, 3, 4, 1):
            u, _ = spl.spl_unit("x", "a.spa", synthetic_spa(fmt=fmt))
            self.assertEqual(u.status, common.DECODED, (fmt, u.error_reason))

    def test_index_outside_palette(self):
        u, frames = spl.spl_unit("x", "a.spa", synthetic_spa(fmt=3, bad_pal_index=True))
        self.assertEqual(u.status, common.UNSUPPORTED)
        self.assertIn("BAD_PALETTE_INDEX", u.error_reason)
        self.assertFalse(frames)

    def test_size_mismatch_and_bad_magic(self):
        self.assertEqual(spl.spl_unit("x", "a", synthetic_spa(wrong_size=True))[0].status, common.UNSUPPORTED)
        self.assertEqual(spl.spl_unit("x", "a", b"NOPE" + b"\0" * 40)[0].status, common.UNSUPPORTED)

    def test_every_prefix_fails_cleanly(self):
        data = synthetic_spa(textures=2)
        for k in range(len(data)):
            self.assertNotEqual(spl.spl_unit("x", "a", data[:k])[0].status, common.DECODED, k)

    def test_blocks_must_tile_the_file(self):
        self.assertEqual(spl.spl_unit("x", "a", synthetic_spa() + b"\0\0")[0].status, common.UNSUPPORTED)


# ---- Game Boy recipes ---------------------------------------------------------------------------
class GameBoy(unittest.TestCase):
    def test_crystal_recipe_roundtrip(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as t:
            r = Path(t)
            (r / "data/battle_anims").mkdir(parents=True)
            (r / "gfx/battle_anims").mkdir(parents=True)
            (r / "constants").mkdir()
            im = Image.new("L", (8, 16), 255)
            im.putpixel((0, 0), 0)
            im.putpixel((1, 0), 85)
            im.save(r / "gfx/battle_anims/fire.png")
            (r / "gfx/battle_anims.asm").write_text('AnimObj00GFX:\nAnimObjFireGFX:      INCBIN "gfx/battle_anims/fire.2bpp.lz"\n')
            (r / "constants/battle_anim_constants.asm").write_text("\tconst BATTLE_ANIM_GFX_NONE\n\tconst BATTLE_ANIM_GFX_FIRE\n")
            (r / "gfx/battle_anims/battle_anims.pal").write_text(
                "; gray\n" + "\tRGB 31, 31, 31\n" * 3 + "\tRGB 00, 00, 00\n; red\n\tRGB 31, 31, 31\n\tRGB 31, 00, 00\n\tRGB 15, 00, 00\n\tRGB 00, 00, 00\n")
            D = r / "data/battle_anims"
            (D / "object_gfx.asm").write_text("AnimObjGFX:\n\tanim_obj_gfx  0, AnimObj00GFX\n\tanim_obj_gfx  2, AnimObjFireGFX\n")
            (D / "objects.asm").write_text("; BATTLE_ANIM_OBJ_EMBER\n\tbattleanimobj RELATIVE_X, $aa, BATTLE_ANIM_FRAMESET_EMBER, BATTLE_ANIM_FUNC_EMBER, PAL_BATTLE_OB_RED, BATTLE_ANIM_GFX_FIRE\n"
                                           "; BATTLE_ANIM_OBJ_BAD\n\tbattleanimobj RELATIVE_X, $aa, BATTLE_ANIM_FRAMESET_EMBER, BATTLE_ANIM_FUNC_EMBER, PAL_BATTLE_OB_PLAYER, BATTLE_ANIM_GFX_FIRE\n")
            (D / "framesets.asm").write_text("\tdw .Frameset_Ember               ; BATTLE_ANIM_FRAMESET_EMBER\n.Frameset_Ember:\n\toamframe BATTLE_ANIM_OAMSET_0F,  4\n\toamframe BATTLE_ANIM_OAMSET_10,  4\n\toamrestart\n")
            (D / "oam.asm").write_text("\tbattleanimoam $00,  1, .OAMData_0f ; BATTLE_ANIM_OAMSET_0F\n\tbattleanimoam $01,  1, .OAMData_0f ; BATTLE_ANIM_OAMSET_10\n"
                                       ".OAMData_0f:\n\tdbsprite  -1,  -1, 4, 4, $00, $0\n")
            units, sheets = gb.scan_crystal(r)
            good = [u for u in units if u.id.endswith("EMBER")][0]
            bad = [u for u in units if u.id.endswith("BAD")][0]
            self.assertEqual(good.status, common.DECODED, good.error_reason)
            self.assertEqual(good.frame_count, 2)
            self.assertEqual(bad.status, common.UNSUPPORTED)
            self.assertIn("run-time", bad.error_reason)
            f0 = sheets[good.id][0]
            self.assertEqual(f0.rgba[3], 255)                    # tile 0 pixel (0,0) = grey 0 -> colour 3 (black), opaque
            self.assertEqual(f0.rgba[0:3], bytes((0, 0, 0)))


# ---- catalog / matrix / conversion --------------------------------------------------------------
def good_unit(**kw):
    u = dict(id="lib:a#0", library="lib", source="a", sha256="a" * 64, type="t", frame_count=2, palette_size=4,
             dimensions={"min": [8, 8], "max": [8, 8]}, tile_budget=2, oam_budget=1, status="DECODED", error_reason=None,
             visual_sha256="b" * 64)
    u.update(kw)
    return u


class CatalogSchema(unittest.TestCase):
    def test_valid_and_invalid_units(self):
        self.assertEqual(cat.validate_unit(good_unit()), [])
        self.assertTrue(cat.validate_unit(good_unit(visual_sha256=None)))
        self.assertTrue(cat.validate_unit(good_unit(frame_count=0)))
        self.assertTrue(cat.validate_unit(good_unit(status="DONE")))
        self.assertTrue(cat.validate_unit(good_unit(status="UNSUPPORTED", error_reason=None)))
        self.assertTrue(cat.validate_unit(good_unit(status="MISSING", error_reason="gone")))           # MISSING must not carry a sha256
        self.assertEqual(cat.validate_unit(good_unit(status="MISSING", sha256=None, frame_count=None, dimensions=None,
                                                     visual_sha256=None, error_reason="absent")), [])
        self.assertTrue(cat.validate_unit(good_unit(tile_budget=-1)))
        self.assertTrue(cat.validate_unit(good_unit(sha256="xyz")))
        bad = good_unit()
        del bad["oam_budget"]
        self.assertTrue(cat.validate_unit(bad))

    def test_catalog_level_rules(self):
        units = [good_unit(), good_unit(id="lib:b#0", sha256="c" * 64)]
        doc = {"schema_version": 1, "units": units, "coverage": cat.coverage(units)}
        self.assertEqual(cat.validate_catalog(doc), [])
        doc["units"].append(good_unit())                                   # duplicate id
        doc["coverage"] = cat.coverage(doc["units"])
        self.assertTrue(any("duplicate unit id" in e for e in cat.validate_catalog(doc)))
        doc2 = {"schema_version": 1, "units": units, "coverage": {"lib": {"units": 5, "by_status": {"DECODED": 5}}}}
        self.assertTrue(cat.validate_catalog(doc2))

    def test_dump_is_deterministic(self):
        units = [good_unit(id=f"lib:{i}") for i in range(3)]
        doc = {"schema_version": 1, "units": units, "coverage": cat.coverage(units), "sources": [], "blockers": []}
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t) / "a.json", Path(t) / "b.json"
            cat.dump_catalog(doc, a)
            cat.dump_catalog(json.loads(json.dumps(doc)), b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(json.loads(a.read_text())["units"], units)


def frame(rgba_pixels, w, h):
    out = bytearray()
    for p in rgba_pixels:
        out += bytes(p)
    return Frame(w, h, bytes(out))


class FxConversion(unittest.TestCase):
    def frames(self, n=3, colours=4, alpha=255):
        out = []
        for k in range(n):
            px = [((i * 30 + k * 20) % 256, (i * 60) % 256, 40 * (i % colours), alpha if (i % 5) else 0) for i in range(16 * 16)]
            out.append(frame(px, 16, 16))
        return out

    def test_estimate(self):
        e = fx_convert.estimate(self.frames())
        self.assertTrue(e["convertible"])
        self.assertEqual(e["translucent_pixels_dropped"], 0)
        self.assertLessEqual(e["max_oams_per_cell"], 4)
        self.assertFalse(fx_convert.estimate([frame([(0, 0, 0, 0)] * 64, 8, 8)])["convertible"])
        mixed = frame([(200, 10, 10, 255) if i % 2 else (10, 200, 10, 100) for i in range(64)], 8, 8)
        self.assertGreater(fx_convert.estimate([mixed])["translucent_pixels_dropped"], 0)

    def test_convert_runs_builder_and_checks_costs(self):
        with tempfile.TemporaryDirectory() as t:
            rep = fx_convert.convert("dau1_test", self.frames(), Path(t))
            self.assertTrue(rep["ok"], rep)
            self.assertLessEqual(rep["checks"]["palette"]["colours"], 15)
            self.assertTrue((Path(t) / "dau1_test_cell.json").exists())
            self.assertTrue((Path(t) / "dau1_test_anim.json").exists())
            again = fx_convert.convert("dau1_test2", self.frames(), Path(t) / "x")
            self.assertEqual(rep["checks"]["tiles"], again["checks"]["tiles"])

    def test_budget_gate_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            rep = fx_convert.convert("dau1_big", self.frames(n=12), Path(t), max_tiles=4)
            self.assertFalse(rep["ok"])
            self.assertIn("budget", rep["error"])

    def test_many_colours_are_folded_to_the_limit(self):
        px = [((i * 7) % 256, (i * 13) % 256, (i * 29) % 256, 255) for i in range(16 * 16)]
        with tempfile.TemporaryDirectory() as t:
            rep = fx_convert.convert("dau1_col", [frame(px, 16, 16)], Path(t))
            self.assertTrue(rep["ok"])
            self.assertLessEqual(rep["checks"]["palette"]["colours"], 15)


class Matrix(unittest.TestCase):
    def doc(self):
        def unit(i, lib, src, tiles, colours, frames=4, hue="red", vis=None, sha=None, translucent=0):
            return good_unit(id=f"{lib}:{i}", library=lib, source=src, sha256=sha or (i[:1] * 64).ljust(64, "0"), type="t",
                             visual_sha256=vis or (i * 8).ljust(64, "1")[:64], frame_count=frames,
                             extra={"opal_fx": {"convertible": True, "obj_tiles": tiles, "colours": colours,
                                                "translucent_pixels_dropped": translucent, "hue": hue,
                                                "max_oams_per_cell": 3, "largest_frame": [16, 16]}})
        units = [unit("e1", "emerald", "graphics/small_ember.png", 24, 5, vis="1" * 64),
                 unit("e2", "emerald", "graphics/huge_fire.png", 400, 5, vis="2" * 64),
                 unit("e3", "emerald", "graphics/ember_many.png", 20, 40, vis="3" * 64),
                 unit("p1", "pmd_sky", "files/EFFECT/effect.bin", 20, 5, vis="4" * 64, hue="blue"),
                 unit("e4", "emerald", "graphics/small_ember_copy.png", 24, 5, vis="1" * 64)]
        return {"units": units}

    def test_roles_budgets_duplicates_and_anonymous(self):
        m = matrix.build_matrix(self.doc())
        by = {c["id"]: c for c in m["candidates"]}
        self.assertEqual(by["emerald:e1"]["decision"], "shortlisted")
        self.assertIn("fire", m["summary"]["shortlist_by_role"])
        self.assertIn("budget", by["emerald:e2"]["rationale"])
        self.assertEqual(by["emerald:e2"]["decision"], "rejected")
        self.assertIn("colours must be folded", by["emerald:e3"]["rationale"])
        self.assertEqual(by["pmd_sky:p1"]["decision"], "needs_visual_review")
        self.assertEqual(by["emerald:e4"]["decision"], "duplicate_alias")
        self.assertIn("identical rendering of emerald:e1", by["emerald:e4"]["rationale"])
        self.assertNotIn("emerald:e4", m["summary"]["shortlist_by_role"]["fire"])
        self.assertEqual(m["p1_p2_binding"]["status"], "BLOCKED_INPUT")
        self.assertEqual(matrix.build_matrix(self.doc()), m)                 # deterministic

    def test_markdown_renders(self):
        md = matrix.matrix_markdown(matrix.build_matrix(self.doc()))
        self.assertIn("BLOCKED_INPUT", md)
        self.assertIn("small_ember.png", md)


class CommittedDocs(unittest.TestCase):
    """Source-free CI gate: the committed catalog + matrix must validate and be self-consistent."""

    def test_check_command(self):
        import subprocess
        r = subprocess.run([sys.executable, str(HERE / "dau1_unlock.py"), "check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)


if __name__ == "__main__":
    warnings.simplefilter("ignore", ResourceWarning)     # the PR #110 builder leaves PNG handles to the GC
    unittest.main(verbosity=1)
