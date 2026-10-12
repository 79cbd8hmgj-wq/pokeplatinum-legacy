# DAU1 -> B9 P1/P2 readiness gate

**Verdict: the asset side of the gate is met; P1/P2 itself must not start until the two input items below are resolved by the owner.** Nothing in P1/P2 has been started or edited.

## Gate checklist

| Gate (DAU1_SPEC acceptance) | State |
|---|---|
| 1. One reproducible command generates the catalog from present sources and reports absent ones | **met** - `dau1_unlock.py catalog`; absent sources are listed in `sources[*].present` / blockers (none absent in the DAU1 workspace). |
| 2. F1-F3 each have genuine frame-level output or an evidence-rich blocker | **met, with explicit partials** - HGSS (SPL textures + 2D cells), PMD (effect WAN frames), Ranger 2 (cells + textures) all produce frames; none is claimed *complete* (see `DECODER_COVERAGE.md`: SPL motion, run-time palette banks, external palette pairings, 72 base-ROM files). |
| 3. Ranger B1 fixture stays identical | **met** - 25/25 B1 cell hashes reproduce and match the new decoder pixel-for-pixel (`test_dau1_sources.py`). |
| 4. Conversion path to Opal FX with transparency / palette / tile / OAM checks | **met** - `dau1_unlock.py convert` -> `fx_convert.py` -> unchanged `opal_fx/build_opal_fx_sheet.py`; reports index-0 transparency, dropped translucent pixels, <= 15 colours, tile budget (192) and OAM count; fails closed over budget. Demonstrated on `pmd_sky:files/EFFECT/effect.bin#1` (12 frames -> 24 OBJ tiles, 5 colours, 1 OAM/cell). |
| 5. Cross-library candidate matrix refreshed from decoded assets before editing P1 | **met** - `CANDIDATE_MATRIX.{json,md}` (3,198 decoded, convertible rows evaluated; 42 shortlisted over 14 effect roles, hue-hint provisional list for anonymous donors). |
| 6. No gameplay / battle-animation script / B9 P0 changes; PR #111 untouched | **met** - diff is `tools/visual_overhaul/dau1*`, `tools/visual_overhaul/test_dau1*.py`, `docs/visual_overhaul/asset_unlock/**`, one workflow. |
| 7. CI/tests honest, missing archives do not stall independent pools | **met** - source-only CI runs 48 host tests + the committed-catalog check; donor tests skip when a donor is absent. |

## Inputs still required from the owner (blocking P1/P2 planning, not the tooling)

1. **The B9 everyday-moves manifest** (`pokemon_opal_everyday_moves_b9_manifest_v2`, which names the 19 P1 and 14 P2 moves) - not in the repo or the DAU1 package. Until it is supplied the matrix is keyed by *effect role* (fire, water, ice, ...) instead of by move.
2. **A visual pass** over the anonymous decoded donors (PMD / HGSS / Ranger / Diamond have no names; only a dominant-hue hint exists). The matrix marks them `needs_visual_review`.
3. **Licence / release decision** for every donor pool (`PROVENANCE.md`), including whether the committed excerpt PNGs may stay.

## Optional follow-ups the evidence now justifies (not required for the gate)

* SPL **emitter** decoding (HGSS `a/0/2/9`, Diamond `waza_particle`) - would turn textures into playable particle behaviour; the largest remaining F1 gap.
* HGSS palette-pairing tables from the overlays (593 banks/sheets are held at STRUCTURAL_ONLY only because their NCLR is not adjacent).
* PMD run-time palette banks (82 effect sprites) - needs engine-side palette-load semantics.
* Yellow subanimation tables; Crystal's remaining 33 objects.
* Base-ROM-extracted HGSS files (72 MISSING) if the owner can legally supply an extraction.

## DAU2 update

Input 1 above (the B9 manifest naming the 19 P1 + 14 P2 moves) is **resolved**: the original manifest is imported unchanged and SHA-pinned in `dau2/source/`, and `dau2/MOVE_CANDIDATE_MATRIX.*` keys candidates per move. Inputs 2 and 3 remain with the owner:
the visual pass now has indexed boards to work from (`dau2/OWNER_REVIEW_GALLERY.md`, previews generated locally), and licensing is still undecided. SPL emitter decoding (optional follow-up above) is done for field structure and offline replay (`dau2/EMITTER_RESEARCH.md`);
it is not runtime-validated. P1/P2 still must not start until the owner has made the visual and licensing decisions listed in `dau2/GAP_REPORT.md`.
