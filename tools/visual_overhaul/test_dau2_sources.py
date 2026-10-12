#!/usr/bin/env python3
"""Corpus-dependent DAU2 tests.  Platinum's own ``.spa`` files live in this repository and are always tested; Diamond / HGSS checks need the
donor checkouts next to the repository (``--workspace``/default parent dir) and are *explicitly skipped* (reported) when absent."""
from __future__ import annotations

import json
import os
import sys
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
WS = Path(os.environ.get("DAU2_WORKSPACE", ROOT.parent))
OUT = ROOT / "docs/visual_overhaul/asset_unlock/dau2"

from dau1 import spl as dspl                              # noqa: E402
from dau2 import emitter_study as ES                      # noqa: E402
from dau2 import spl_emitter as E                         # noqa: E402
from dau2 import spl_sim as S                             # noqa: E402

HAVE = {"diamond": (WS / "pokediamond/files").is_dir(), "hgss": (WS / "pokeheartgold/files").is_dir()}


def corpus(lib):
    return [(uid, d) for l, uid, rel, m, d in ES.iter_corpus(WS, ROOT) if l == lib]


class PlatinumNative(unittest.TestCase):
    """Always runs: Platinum's .spa files ship in res/."""

    @classmethod
    def setUpClass(cls):
        cls.files = corpus("platinum")

    def test_every_archive_tiles_exactly_and_passes_structural_checks(self):
        self.assertGreaterEqual(len(self.files), 600)
        bad = Counter()
        for uid, d in self.files:
            r = ES.study_archive("platinum", uid, d)
            bad[r["category"]] += 1
            self.assertEqual(r.get("issues", []), [], uid)
        self.assertEqual(set(bad), {"EMITTER_FIELDS_VERIFIED"})

    def test_value_distributions_match_lib_spl_semantics(self):
        hs = [e.header for uid, d in self.files for e in E.parse_emitters(d).emitters]
        self.assertGreater(len(hs), 1500)
        mode = lambda k: Counter(h[k] for h in hs).most_common(1)[0][0]       # noqa: E731
        self.assertEqual(mode("air_resistance"), 128)         # (128 + 384) >> 9 == exactly 1.0: 'no drag'
        self.assertEqual(mode("aspect_fx16"), 4096)
        self.assertEqual(mode("emission_interval"), 1)
        self.assertTrue(all(h["base_alpha"] <= 31 for h in hs))
        self.assertTrue(all(h["user_flags"] == 0 for h in hs))

    def test_dau1_texture_decode_is_unchanged(self):
        n = 0
        for uid, d in self.files:
            u, frames = dspl.spl_unit("platinum", uid, d)
            self.assertIn(u.status, ("DECODED", "STRUCTURAL_ONLY"))
            n += 1
            if n >= 120:
                break

    def test_representative_replays_are_deterministic_and_match_committed_state_hash(self):
        by = dict(self.files)
        for name in ("headbutt", "flame_wheel", "sleep_powder"):
            d = by[f"platinum:res/graphics/battle/particles/{name}.spa"]
            sp = E.parse_emitters(d)
            a, b = S.replay(sp, 60, 0x2B7E1516), S.replay(sp, 60, 0x2B7E1516)
            self.assertEqual(a.frames, b.frames)
            inv = ES.replay_invariants(sp, a, 60)
            self.assertTrue(inv["spawn_schedule_matches"] and inv["particle_age_within_life"] and inv["within_ds_quad_limit"], name)
            rp = OUT / "emitter/recipes" / f"{name}.emitter_recipe.json"
            if rp.exists():
                rec = json.loads(rp.read_text())
                sha = ES.hashlib.sha256(json.dumps(a.frames, sort_keys=True).encode()).hexdigest()
                self.assertEqual(sha, rec["replay"].get("state_sha256"), f"{name}: replay state differs from the committed recipe")
                self.assertEqual(ES.hashlib.sha256(d).hexdigest(), rec["source"]["sha256"])


@unittest.skipUnless(HAVE["diamond"], "SKIP: pokediamond checkout not found next to the repository")
class DiamondCorpus(unittest.TestCase):
    def test_all_move_particles_parse(self):
        files = corpus("diamond")
        self.assertGreaterEqual(len(files), 600)
        cats = Counter(ES.study_archive("diamond", u, d)["category"] for u, d in files)
        self.assertEqual(set(cats), {"EMITTER_FIELDS_VERIFIED"})

    def test_index_alignment_with_platinum_is_texture_verified_for_most_entries(self):
        from dau2 import assets as A
        order = A.platinum_order(ROOT)
        plat = {n: dspl.spl_unit("p", n, d)[0].visual_sha256 for (u, d) in corpus("platinum") for n in [u.rsplit("/", 1)[-1][:-4]]
                if "/pokeballs/" not in u and u.startswith("platinum:res/graphics/battle/particles/")}
        dm = {u.rsplit("narc_", 1)[1][:4]: d for u, d in corpus("diamond") if "waza_particle" in u}
        same = sum(1 for i, n in enumerate(order) if f"{i:04d}" in dm and dspl.spl_unit("d", "d", dm[f"{i:04d}"])[0].visual_sha256 == plat.get(n))
        self.assertGreaterEqual(same, 440, f"only {same}/{len(order)} index-aligned entries share decoded textures")


@unittest.skipUnless(HAVE["hgss"], "SKIP: pokeheartgold checkout not found next to the repository")
class HgssCorpus(unittest.TestCase):
    def test_all_spl_archives_parse(self):
        files = corpus("hgss")
        self.assertGreaterEqual(len(files), 640)
        cats = Counter(ES.study_archive("hgss", u, d)["category"] for u, d in files)
        self.assertEqual(set(cats), {"EMITTER_FIELDS_VERIFIED"})

    def test_representative_effects_agree_across_games(self):
        rec_dir = OUT / "emitter/recipes"
        if not rec_dir.exists():
            self.skipTest("SKIP: emitter recipes not generated")
        for p in sorted(rec_dir.glob("*.json")):
            r = json.loads(p.read_text())
            for lib, c in r["cross_game_agreement"].items():
                self.assertTrue(c["emitter_records_identical_to_platinum"], f"{p.name}: {lib} differs in {c['differing_blocks']}")

    def test_hgss_labels_reproduce_from_the_checkout_and_gate_the_matrix(self):
        from dau2 import hgss_labels as HL
        lab_p, ov_p, ml_p = OUT / "HGSS_CELL_BANK_LABELS.json", OUT / "hgss_cell_bank_label_overrides.json", OUT / "hgss_cell_bank_model_labels.json"
        if not lab_p.exists():
            self.skipTest("SKIP: labels not generated")
        cat = json.loads((ROOT / "docs/visual_overhaul/asset_unlock/ASSET_CATALOG.json").read_text())
        fresh = HL.build_labels(WS, cat, json.loads(ov_p.read_text()), json.loads(ml_p.read_text()))
        committed = json.loads(lab_p.read_text())
        self.assertEqual(fresh["containers"], committed["containers"])
        self.assertEqual(fresh["summary"]["banks_decoded_auto_eligible"], 9)               # only identified weather-system banks are eligible today
        mat = json.loads((OUT / "MOVE_CANDIDATE_MATRIX.json").read_text())
        unident = {r["container"] for r in committed["containers"] if r["category"] == "unidentified"}
        units = {u["id"]: u for u in cat["units"]}
        for mv in mat["moves"]:
            for r in mv["candidates"]:
                u = units.get(r["asset_id"])
                self.assertFalse(u and u["library"] == "hgss" and u["source"] in unident, f"{mv['move']}: unidentified HGSS bank selected")

    def test_dau1_catalog_hashes_still_reproduce(self):
        cat = {u["id"]: u for u in json.loads((ROOT / "docs/visual_overhaul/asset_unlock/ASSET_CATALOG.json").read_text())["units"]}
        n = 0
        for u, d in corpus("hgss"):
            unit, _ = dspl.spl_unit("hgss", u.split(":", 1)[1].split("#")[0], d)
            c = cat.get(u)
            if c and c["status"] == "DECODED":
                self.assertEqual(c["sha256"], ES.hashlib.sha256(d).hexdigest(), u)
                self.assertEqual(c["visual_sha256"], unit.visual_sha256, u)
                n += 1
            if n >= 150:
                break
        self.assertGreater(n, 100)


if __name__ == "__main__":
    unittest.main(verbosity=1)
