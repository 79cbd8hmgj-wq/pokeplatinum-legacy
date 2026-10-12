#!/usr/bin/env python3
"""Donor-dependent DAU1 checks.  Each test skips when its checkout is not next to this repository.

  python3 tools/visual_overhaul/test_dau1_sources.py [--workspace DIR]

Not run in source-only CI (no donor bytes are available there); run locally / in the donor workflow.
"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from dau1 import bundle as bd, common, nitro2d as n2, nitro_library as nl, pipeline, pmd_effect as pe, spl  # noqa: E402

WS = ROOT.parent


def root(lib):
    return pipeline.find_root(WS, pipeline.LIBRARIES[lib][1])


def need(lib):
    r = root(lib)
    return unittest.skipIf(r is None, f"{lib} checkout absent")


class B1RangerFixtureStaysIdentical(unittest.TestCase):
    """The three original B1 Ranger outputs: committed cell hashes reproduce, and the DAU1 decoder is pixel-identical."""

    @need("ranger2")
    def test_b1_cells(self):
        from PIL import Image
        from render_ranger_pokemon_package import render_package
        prov_dir = ROOT / "docs/visual_overhaul/b1_installed_donors"
        total = 0
        for name, pkg in (("ranger_fire_bloom", "e010"), ("ranger_ice_bloom", "e009"), ("ranger_rock_burst", "e002")):
            prov = json.loads((prov_dir / f"{name}.provenance.json").read_text())
            src = root("ranger2") / f"res/prebuilt/data/effect/{pkg}_LZ.bin"
            payload = common.lz_decompress(src.read_bytes())
            banks = {ncer.name.rsplit(".", 1)[0]: bd.decode_cell_bundle(ncer.data, g.data, p.data, a.data if a else None,
                                                                        trust_scan_header=False)
                     for ncer, g, p, a, _ in bd.pair_bundles(bd.classify_members(n2.parse_narc(payload)))}
            with tempfile.TemporaryDirectory() as t, contextlib.redirect_stdout(io.StringIO()):
                render_package(src, Path(t), 32)
                for fr in prov["frames"]:
                    hits = list(Path(t).rglob(fr["cell"]))
                    self.assertTrue(hits, fr["cell"])
                    match = [h for h in hits if hashlib.sha256(h.read_bytes()).hexdigest() == fr["cell_sha256"]]
                    self.assertTrue(match, f"{name} {fr['cell']}: existing tool no longer reproduces the committed hash")
                    im = Image.open(match[0]).convert("RGBA")
                    raw = bytearray(im.tobytes())
                    for i in range(0, len(raw), 4):
                        if raw[i + 3] == 0:
                            raw[i:i + 3] = b"\0\0\0"
                    nb = banks[match[0].parent.name].frames[int(fr["cell"][5:8])]
                    self.assertEqual((im.width, im.height), (nb.width, nb.height))
                    self.assertEqual(bytes(raw), nb.rgba, f"{name} {fr['cell']}: DAU1 decoder differs from the B1 renderer")
                    total += 1
        self.assertEqual(total, 25)


class Hgss(unittest.TestCase):
    @need("hgss")
    def test_move_particle_archive_decodes(self):
        r = root("hgss")
        data = (r / "files/a/0/2/9").read_bytes()
        units, sheets, _ = nl.scan_container("hgss", "files/a/0/2/9", data)
        spa = [u for u in units if u.type == "spl_particle_archive"]
        self.assertGreaterEqual(len(spa), 480)
        self.assertGreaterEqual(sum(u.status == common.DECODED for u in spa), 440)

    @need("hgss")
    def test_filesystem_manifest_hashes(self):
        import hashlib
        r = root("hgss")
        bad = 0
        for line in (r / "heartgold.us/filesystem.sha1").read_text().splitlines()[:40]:
            h, rel = line.split(" *", 1)
            if (r / rel).exists():
                bad += hashlib.sha1((r / rel).read_bytes()).hexdigest() != h
        self.assertEqual(bad, 0)


class PmdSky(unittest.TestCase):
    @need("pmd_sky")
    def test_effect_bin_frame_level(self):
        d = (root("pmd_sky") / "files/EFFECT/effect.bin").read_bytes()
        ents = pe.parse_pack(d)
        self.assertEqual(len(ents), 293)
        results = [pe.decode_effect_entry(d[o:o + l]) for o, l in ents]
        decoded = [r for r in results if r.status == common.DECODED]
        self.assertGreaterEqual(len(decoded), 180)
        self.assertTrue(all(r.frames and r.palette_rows >= 1 for r in decoded))
        # entry 1 is a known 4bpp 81-frame sprite
        self.assertEqual(len(results[1].frames), 81)
        # deterministic
        again = pe.decode_effect_entry(d[ents[1][0]:ents[1][0] + ents[1][1]])
        from dau1.render import frames_hash
        self.assertEqual(frames_hash(again.frames), frames_hash(results[1].frames))


class Diamond(unittest.TestCase):
    @need("diamond")
    def test_waza_particles_and_cells(self):
        r = root("diamond")
        sp = sorted((r / "files/wazaeffect/effectdata/waza_particle").glob("*.bin"))
        self.assertGreaterEqual(len(sp), 485)
        ok = sum(spl.spl_unit("diamond", p.name, p.read_bytes())[0].status == common.DECODED for p in sp)
        self.assertGreaterEqual(ok, 450)


class RubyVsEmerald(unittest.TestCase):
    @need("ruby")
    def test_ruby_art_is_present_elsewhere(self):
        doc, _, _ = pipeline.run(WS, ["ruby", "emerald", "firered"])
        ruby = [u for u in doc["units"] if u["library"] == "ruby"]
        self.assertGreater(len(ruby), 250)
        self.assertTrue(all(u["extra"]["cross_library"] in ("identical", "same_pixels", "same_indices_other_palette", "unique")
                            for u in ruby))


class WholeCatalog(unittest.TestCase):
    def test_pipeline_reports_absent_sources_without_failing(self):
        with tempfile.TemporaryDirectory() as t:
            doc, sheets, _ = pipeline.run(Path(t))
            self.assertEqual(doc["units"], [])
            self.assertTrue(all(not s["present"] and s["status"] == "BLOCKED_INPUT" for s in doc["sources"]))


if __name__ == "__main__":
    if "--workspace" in sys.argv:
        i = sys.argv.index("--workspace")
        WS = Path(sys.argv[i + 1])
        del sys.argv[i:i + 2]
    unittest.main(verbosity=1)
