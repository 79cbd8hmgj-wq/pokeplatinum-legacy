# Opal DAU1 - universal donor asset unlock (tooling only)

Reusable discovery / decode / render / hash / catalog / convert tooling for every accessible donor animation library. **Tooling and evidence only:**
no gameplay, battle-animation script, B9 P0 file or `res/` resource is touched, B9 P1/P2 are not started, and no ROM or donor binary is committed.

Baseline: branch cut from `main` @ `c5a9cdb8`. PR #110 is preserved. **Note:** PR #111 (B9 P0) is *already merged* into that `main` (merge commit `c5a9cdb8`, B9 P0 commits
`12aa97eb` and earlier), contrary to the handoff text that calls it unmerged; nothing in this PR modifies it.

## One command

```sh
python3 tools/visual_overhaul/dau1_unlock.py catalog          # decode every donor present next to the repo; absent donors are reported
python3 tools/visual_overhaul/dau1_unlock.py check            # source-free: validates the committed catalog + matrix (CI)
python3 tools/visual_overhaul/dau1_unlock.py matrix           # rebuild CANDIDATE_MATRIX.* from the committed catalog
python3 tools/visual_overhaul/dau1_unlock.py convert --unit 'pmd_sky:files/EFFECT/effect.bin#1'   # -> Opal FX sheet/cell/anim in build/dau1_fx
python3 tools/visual_overhaul/test_dau1.py                    # 48 host tests, no donor bytes
python3 tools/visual_overhaul/test_dau1_sources.py            # donor-dependent checks (skip when a donor is absent)
```

`catalog` takes about a minute, is deterministic (byte-identical output on re-run), and writes `ASSET_CATALOG.json`, `CANDIDATE_MATRIX.{json,md}`,
`DECODER_COVERAGE.md`, `PROVENANCE.md`, a gallery index and small evidence excerpts under `gallery/`. Full contact-sheet galleries (`--gallery-dir`, default `build/dau1_gallery`) stay out of Git.

## Deliverables

| File | What |
|---|---|
| `ASSET_CATALOG.json` | one record per decodable unit: source, sha256, type, frame count, palette size, dimensions, tile / OAM budget estimates (null if unknown), status, error reason, member hashes, `visual_sha256`; plus per-library coverage, source pins, blockers, cross-library duplicates, gallery index |
| `DECODER_COVERAGE.md` | generated: which libraries are decoded / partial / blocked, by unit type, with the measured reasons |
| `PROVENANCE.md` | generated: pinned commits, licence status, legal release gate, third-party references |
| `CANDIDATE_MATRIX.{json,md}` | refreshed cross-library candidate matrix (selected / rejected / needs-review with rationales) |
| `P1_READY.md` | gate checklist before B9 P1/P2 may start |
| `gallery/*_excerpt.png` | real decoded frames from each priority library (excerpts only; release status: owner review) |

Code: `tools/visual_overhaul/dau1/` (`common`, `nitro2d`, `bundle`, `nitro_library`, `pmd_effect`, `spl`, `ranger_tex`, `gba`, `gb`, `fx_convert`, `matrix`, `pipeline`, `gallery`, `report`, `catalog`) and `dau1_unlock.py`.
Existing B1/B2 tools were reused, not replaced: the Ranger renderer (`render_ranger_ncer_preview.py`) is the pixel oracle for the new Nitro cell renderer and `opal_fx/build_opal_fx_sheet.py` (PR #110) is the conversion back end.

## Status vocabulary

`DECODED` real pixels produced and validated (tiles in range, palette indices in range, >= 1 visible frame) - `STRUCTURAL_ONLY` headers parse, or frames render but a validation (e.g. an unverifiable palette pairing) fails -
`UNSUPPORTED` input present, variant not decodable (evidence recorded) - `MISSING` an input the project lists is absent - `BLOCKED_INPUT` a whole source or required document is inaccessible.
Frames rendered with a *guessed* palette are never counted as decoded; they are kept as local previews only.

## Gap ledger (`FOLLOW_UP_ASSET_DECODING.md`) - what the evidence says now

| # | Pool | P0 ledger claim | Measured outcome |
|---|---|---|---|
| F1 | HGSS | no SPL archives in the checkout; `files/pbr/*.narc` opaque | **The claim was wrong.** The move-particle archives are present as extension-less NARCs: `files/a/0/2/9` holds 486 `.spa` (452 decoded), `files/a/0/9/5` 133 ball-particle `.spa` (all decoded) - 611 of 645 SPL archives decode to their particle textures (34 are fully transparent). `files/pbr/*` is Pokemon Battle Revolution interface data, not move particles (confirmed: `pbr_file.inc`). Search by file name/extension had missed them; the magic is `" APS"`. 513 of 942 Nitro cell banks also decode. **Not decoded:** SPL *emitter motion* (inventoried only), NSCR screens, 593 banks/sheets whose palette pairing lives in overlay code, 72 base-ROM-extracted files (MISSING). |
| F2 | PMD Sky | container-level only | `effect.bin` -> pack -> SIR0 -> effect-WAN decoded to **5,128 real frames in 184 of 293 entries**, validated against an independent reference (29,365 pieces, 0 differences). The other 109: 82 select run-time palette banks the file does not define (reported, never guessed), 23 are screen-effect tables / non-sprite entries, 4 structural. |
| F3 | Ranger 2 | only e002/e009/e010 decoded | all 214 effect packages scanned (211 hold cell banks): 294 of 309 cell banks decoded, 8 of 10 `.ntft` textures decoded (2 have an ambiguous width). B1 fixture: 25/25 cells reproduce the committed hashes and are pixel-identical in the new decoder. |
| F4 | Ruby/Sapphire | no checkout | `79cbd8hmgj-wq/pokeruby` was accessible and is now catalogued: **all 278 battle-anim sprites have a byte-identical counterpart in Emerald/FireRed**, so Ruby adds no unique art in that pool (the decision the ledger asked for - now evidence-backed rather than assumed). |
| F5 | Crystal / Yellow | tile strips only | Crystal: 64 of 97 battle objects reconstructed *exactly* from the assembly tables (frameset + OAM + palette), e.g. `BATTLE_ANIM_OBJ_EMBER`; the rest need run-time data. Yellow: tile sheets decode, layout tables not reconstructed. |
| F6 | Licence | unverified | still unverified - see `PROVENANCE.md`; flagged for owner review. |

Additional pool found: **pokediamond** (accessible, DP lineage = closest to Platinum) carries 485 move-particle `.spa`, 117 ball-particle `.spa` and 36 `wazaeffect` move-effect cell banks (spoon, bone, horn, claw marks, vines, ...); 580 SPL archives and 108 cell banks decode.

## Limits (honest)

* SPL archives are decoded to **textures only**; the particle behaviour (emitters) is not, so an SPL texture is art for a recipe, not a playable effect.
* HGSS and PMD palette semantics that depend on engine code are reported as limits, not guessed (see `DECODER_COVERAGE.md` blockers).
* The Opal-FX conversion path is demonstrated end-to-end on a decoded PMD sprite (see `P1_READY.md`) and cost-estimated for every decoded unit, but nothing is installed into `res/`.
* Nothing here is a visual approval; no emulator or hardware run was performed.
