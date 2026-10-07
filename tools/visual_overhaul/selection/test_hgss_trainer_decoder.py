#!/usr/bin/env python3
"""Regression tests pinning the HGSS trainer NCER per-cell VRAM-transfer decoding (decoder lock).

The pre-fix decoder drew every cell from the first chunk, so multi-frame sets showed frame 0 repeated and
produced false "later frames differ" results. These tests use synthetic data plus committed catalog/render artifacts
(no donor checkout needed, so they run in CI).
"""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image  # noqa: E402

import hgss_trainer_sprite_lib as lib  # noqa: E402
from common import *  # noqa: E402,F401,F403


def tile(v):
    return [v] * 64


def make_ncer(n_cells: int, with_transfer: bool, transfers):
    """Minimal extended NCER: each cell = one 8x8 OBJ at (0,0), char name 0."""
    ent = 16
    cells = b"".join(struct.pack("<HHI", 1, 0, 6 * i) + struct.pack("<hhhh", 8, 8, 0, 0) for i in range(n_cells))
    oams = b"".join(struct.pack("<HHH", 0x0000, 0x0000, 0x0000) for _ in range(n_cells))
    vt = b""
    off = 0
    if with_transfer:
        vt = struct.pack("<II", 0x100, 8) + b"".join(struct.pack("<II", s, z) for s, z in transfers)
    body = struct.pack("<HHIIIII", n_cells, 1, 0x18, 1, 0, 0, 0)  # cellCount, attr, cellOff, mapping, vramOff(patched), stringBank, ucat
    blk = bytearray(b"KBEC" + b"\0\0\0\0" + body + cells + oams)
    if with_transfer:
        off = len(blk) - 8
        blk += vt
    struct.pack_into("<H", blk, 0x14, off)  # vramTransferOffset: block+0x14
    blk[4:8] = struct.pack("<I", len(blk))
    return bytearray(b"RECN" + b"\xff\xfe\x00\x01" + struct.pack("<IHH", 0x10 + len(blk), 0x10, 1)) + blk


class SyntheticDecoder(unittest.TestCase):
    def setUp(self):
        self.tiles = [tile(1), tile(2), tile(3)]  # chunk A = tile0, chunk B = tile1, chunk C = tile2
        self.cells = [[(0x0000, 0x0000, 0x0000)]] * 3
        self.transfers = [(0, 32), (32, 32), (64, 32)]

    def test_each_cell_uses_its_own_chunk(self):
        w, h, px, oob, dims = lib.render_sheet(self.cells, self.tiles, gap=0, transfers=self.transfers)
        frames = [px[i * 64:(i + 1) * 64] for i in range(3)]
        self.assertEqual([set(f) for f in frames], [{1}, {2}, {3}])
        self.assertEqual(oob, 0)

    def test_first_chunk_for_every_frame_bug_is_detectable(self):
        # Pre-fix behaviour: no transfers -> all frames identical copies of chunk 0. Must never be what decode_sheet does.
        _, _, px, _, _ = lib.render_sheet(self.cells, self.tiles, gap=0, transfers=None)
        frames = {tuple(px[i * 64:(i + 1) * 64]) for i in range(3)}
        self.assertEqual(len(frames), 1, "sanity: the buggy path repeats frame 0")

    def test_parse_transfer_table_layout(self):
        raw = bytes(make_ncer(3, True, self.transfers))
        self.assertEqual(lib.parse_ncer_transfers(raw, 3), self.transfers)
        self.assertEqual(len(lib.parse_ncer(raw)), 3)

    def test_multi_cell_without_table_is_rejected(self):
        raw = bytes(make_ncer(2, False, []))
        self.assertIsNone(lib.parse_ncer_transfers(raw, 2))
        ncgr = b"RGCN" + b"\xff\xfe\x00\x01\0\0\0\0\x10\0\x01\0" + b"RAHC" + struct.pack("<IHHIIIII", 0x30, 0xFFFF, 0xFFFF, 3, 0x100010, 0, 0, 64)
        # (structure only needs to fail before rendering; a full NCGR is not required to prove fail-closed behaviour)
        with self.assertRaises(ValueError):
            lib.decode_sheet(bytes(ncgr) + b"\0" * 64, b"RLCN", raw)


class CommittedArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = jload(EXT_DIR / "hgss_trainer_sprites" / "CATALOG.json")["assets"]

    def test_decoder_version_pinned(self):
        for a in self.cat:
            self.assertEqual(a["source_metadata"]["decoder_version"], lib.DECODER_VERSION, a["asset_id"])

    def test_multi_cell_assets_have_transfer_tables(self):
        multi = [a for a in self.cat if a["source_metadata"]["cell_count"] > 1]
        self.assertGreater(len(multi), 0)
        for a in multi:
            m = a["source_metadata"]
            self.assertTrue(m["vram_transfer"] and len(m["vram_transfer"]) == m["cell_count"], a["asset_id"])

    def test_distinct_chunks_yield_distinct_frames(self):
        """If a set's cells draw from >1 distinct NCGR chunk, its render must not be a single repeated frame."""
        for a in self.cat:
            m = a["source_metadata"]
            if m["cell_count"] < 2 or len({t[0] for t in m["vram_transfer"]}) < 2:
                continue
            im = Image.open(ROOT / a["render_path"])
            fh = m["cell_dims"][0][1]
            frames = {im.crop((0, k * (fh + 1), im.width, k * (fh + 1) + fh)).tobytes() for k in range(m["cell_count"])}
            self.assertGreater(len(frames), 1, f"{a['asset_id']}: all frames identical despite distinct VRAM chunks (first-chunk bug)")


if __name__ == "__main__":
    unittest.main()
