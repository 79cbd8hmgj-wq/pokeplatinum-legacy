# AV2 — Animated Environmental Presentation (overworld)

Opportunity IDs: **V04** (other overworld atmospheres), **V05** (animated field detail).
Baseline: `main` @ `e91ee103` (merge of PR #101). No C, no gameplay, no encounter, progression, trainer or Pokémon-system change.
Not repeated: G2/G4/G6 atmosphere and texture work, S2 battle-terrain palette cycling (`IO_PAL_CYCLE_*`), static forest material work.

## Method in one paragraph

Platinum already animates field props through **NSBTA** (texture SRT), **NSBTP** and **NSBCA** files that
`MapPropAnimationManager` loads per area from `prop_animations.narc`, bound to prop models by the prebuilt
`bm_anime_list.narc` (20-byte record per prop model, up to 4 animation IDs). AV2 stays inside that native path:
it re-authors NSBTA sample tracks with a small, round-trip-verified Python reader/writer
(`tools/visual_overhaul/av2/nitro_anim.py`) and registers two new NSBTA files. No new field particle system, no
palette writes, no model/texture edits, no guessed IDs (every ID is derived from
`map_prop_models.order` and the `prop_animation_*` list in `meson.build`).

Two techniques:

* **Surge re-timing** — retail tracks are linear scrolls. AV2 applies a monotone progress warp `g(p)` with
  `g(0)=0`, `g(1)=1` (speed = 1 + Σ aₖ·cos 2πk(p−φₖ), Σ|aₖ| < 0.95) to the existing samples. Frame count, total travel,
  first/last sample and the loop seam are identical to retail; only the in-loop speed changes, so water gets layered ripples,
  waterfalls get gusts and machine strips get pulses instead of constant belts.
* **Breath** — two new closed-loop sinusoidal texture-T tracks (new files) for Distortion World cliff materials.

## A. Source preflight (exact host resources)

| Target | Prop model(s) (`map_prop_models.order`) | Animation hook (before AV2) | Material | Source-editable? | Result |
|---|---|---|---|---|---|
| Lake water (A) | `prop_model_074`, `prop_model_311` | `bm_anime_list` → `prop_animation_019.nsbta` (61 f, S+T diagonal linear scroll −1 tile) | `l_lake` (32×32, repeat S+T) | Yes (NSBTA samples) | **Done** |
| Waterfalls (D) | `prop_model_305`–`310` | `prop_animation_018.nsbta` (3 materials) | `taki`, `taki_top` (flow T −2 tiles); `kemuri` (mist) left alone | Yes (in-place same-length samples) | **Done** |
| Galactic machinery (C) | `prop_model_158` (`machine_l03`) | `prop_animation_022.nsbta` | `ma_l03_2` (16×16 green LED strip, S +2 tiles) | Yes | **Done** |
| | `prop_model_314` | `prop_animation_044.nsbta` | `m_l04b` (32×8 green gradient conduit, S −1 tile) | Yes | **Done** |
| | `prop_model_114` (`machine_l02`) | `prop_animation_004.nsbta` (91 f, 2 materials) | `lab_01_2`, `lab_01_3` | Yes | **Done** (counter-phase panels) |
| | `prop_model_495`, `prop_model_497`, `lake_guardian_containment_unit` | `prop_animation_046/047/048.nsbta` | `d26_o01b`, `d26_o03b`, `d26_o02c_lm1` (containment-room energy) | Yes | **Done** |
| Distortion World (B) | `prop_model_583` (`d33_step02`) | none (list record all `0xFF`) | `criffp_lm5`, `file1Material` (cliff faces, repeat S+T) | Yes: 2 new NSBTA + one guarded 20-byte record in `bm_anime_list.narc` | **Done (restrained)** |
| | `prop_model_582` (`d33_step01`) | none | `criffp_lm3` has **repeat S only** (T clamps) | Not safe | **Left static** (see blockers) |
| Distortion World map tiles | land models | none — map geometry has no animation hook | — | No | Not feasible natively |

Preflight facts used: Distortion World = `area_data_074` / `prop_model_set_070` (only models 582/583); lakes = `area_data_062`
(also `area_data_014` Snowpoint uses 311); Galactic HQ/labs = `area_data_058`, `068`, `077`, generic interior `031`.
Animation slot budget (`MAP_PROP_ANIMATION_MANAGER_MAX_ANIMATIONS = 16`): worst area before **and** after = 11 (`area_data_019`);
Distortion World goes 0 → 2.

## B. Change ledger

Generator: `tools/visual_overhaul/av2/apply_av2_env_anim.py` (idempotent, fail-closed on unexpected SHA-256; `--check`).
Pinned digests: `tools/visual_overhaul/av2/av2_pinned.json`.

### Existing NSBTA files re-timed (same frame count, same travel, same seam)

| File | Environment / host | Track(s) | Surge harmonics (amplitude, phase) | Visible effect |
|---|---|---|---|---|
| `prop_animation_019.nsbta` | Sinnoh lakes (`area_data_062`), Snowpoint (`014`) water | `l_lake` S and T | S: k1 (0.30, 0.00) + k2 (0.10, 0.25); T: k1 (0.15, 0.50) + k2 (0.35, 0.15) | diagonal drift now swells and eases with different rhythms on the two axes (rolling ripples; per-frame speed 0.52–1.43× retail) |
| `prop_animation_018.nsbta` | waterfalls on routes (areas 009, 010, 013, 016, 053, 069–071) | `taki`, `taki_top` T | k1 (0.35, 0.00) + k2 (0.20, 0.30) | flow gusts instead of a constant belt |
| `prop_animation_022.nsbta` | `machine_l03` | `ma_l03_2` S | k1 (0.60, 0.00) + k2 (0.25, 0.20) | LED strip surges and stalls |
| `prop_animation_044.nsbta` | `m_l04b` conduit | S | k1 (0.55, 0.50) + k2 (0.25, 0.00) | glow travels in pulses |
| `prop_animation_004.nsbta` | `machine_l02` | `lab_01_2` / `lab_01_3` S | k1 0.55 with φ 0.0 vs 0.5 | two panels pulse in counter-phase |
| `prop_animation_046/047/048.nsbta` | Galactic containment room | T / S / T | k1 0.60/0.60/0.50 at distinct phases | three energy columns no longer in lockstep |

Retail endpoints are preserved exactly. Per-frame speed relative to retail stays within 0.17–1.78× (slowest dwell 022 at 0.17×, fastest 044 at 1.78×); the validator ceiling is 3.2×.

### New NSBTA files

| File | Bound to | Material | Track |
|---|---|---|---|
| `prop_animation_098.nsbta` | `prop_model_583` | `criffp_lm5` | 121-frame closed loop, texture T ≈ ±0.078 tile (≈2.5 texels of 32), `sin + 0.3·sin 2×` |
| `prop_animation_099.nsbta` | `prop_model_583` | `file1Material` | same loop, opposite polarity (two cliff layers breathe against each other) |

Built from retail `prop_animation_046.nsbta` as container template; both appended to `meson.build` list and
`prop_animations.order` (IDs 98/99 follow 97 contiguously). `bm_anime_list.narc` record 583 changes from
`ff ff 00 00 ff…` to `01 00 00 00 | 62 00 00 00 | 63 00 00 00 | ff…` (record 311 is the retail reference layout) through a guarded
in-place patch; no other record changes (validator-enforced).

### Preserved

G6 lighting/fog configuration (`lighting_set_009`), camera, platform geometry, collision, scripts and every gameplay interaction;
no model, texture, palette, area-data or C file changed.

## C. Donor provenance

| Ingredient | Kind | Source | Actual asset reuse |
|---|---|---|---|
| Phase-offset layered motion on one surface | technique inspiration | PMD Sky palette-cycle phasing (IO-PAL-CYCLE lineage) | none |
| Slow multi-rhythm water drift (water category of the donor matrix) | technique inspiration | HGSS/Platinum water row of `CROSS_GAME_DONOR_MATRIX.md` | none |
| Surge-and-ebb energy pulse | technique inspiration | Ranger 2 effect sequencing (IO-FX-SEQ launch → surge → ebb) | none |
| All timings, harmonics, amplitudes | authored for Opal | this PR | n/a |

**Donor pixels or tracks reused: 0.** The in-tree `pokeheartgold` and `pmd-sky` clones are decompilation sources without extracted
visual assets, and the catalogs contain no measured HGSS water timing records, so no HGSS number was copied; HGSS and PMD Sky
contributed only the layering/phase idea.

## D. Resource ownership and cleanup

* Animations are owned by `MapPropAnimationManager` (allocated at area load, released by `MapPropAnimationManager_UnloadAllAnimations` /
  `_Free`); AV2 adds no allocations, no tasks, no VRAM, no OAM.
* New files add 2 manager slots only in `area_data_074`; global worst case unchanged at 11/16.
* `prop_animations.narc` grows from 98 to 100 members; `bm_anime_list.narc` size unchanged (590 × 20-byte records).
* Cleanup path is the existing one; nothing to unregister on area exit.

## E. Validation

* `python3 -I tools/visual_overhaul/av2/apply_av2_env_anim.py --check` — tree equals the pinned AV2 output.
* `python3 -I tools/visual_overhaul/validate_av2_env_anim.py` — structure, bit-exact serializer round trip, material/repeat-flag
  bindings against the real NSBMD materials, monotonicity and seam/endpoint preservation vs the baseline commit, closed-loop and
  amplitude limits, contiguous animation IDs, meson/order agreement, slot budget, scope containment (no `src/`, `include/`,
  `asm/`, area-data, map, model, texture, lighting, script, encounter or Pokémon file changed), and a 9-mutant self-test.
* CI: `.github/workflows/validate-av2-env-anim.yml` plus the existing US Rev 0 / Rev 1 build matrix.
* Regression validators run unchanged-green: `validate_area_light_contract`, `validate_g6_showcase_integration`, `validate_g76_atmosphere`,
  `validate_g77_final_cohesion`, `validate_g7_*` (five), `validate_av1_battle_presentation`, `io_pal_cycle/validate_terrain_cycle`,
  `io_status/validate_confusion_overlay`. The `validate_g4*` scripts need workflow-dumped texture inputs and exit 1 on `main` as well
  (identical on the baseline commit; no texture was touched).

Results (authoring environment, `git fetch --unshallow` for history-dependent validators):

* `apply_av2_env_anim.py --check`: pass. `validate_av2_env_anim.py`: pass, mutation self-test 9/9 rejected, worst-case slots 11/16.
* Regression validators listed above: pass (the six `validate_g4*` scripts exit 1 identically on `e91ee103`).
* `make rom ROM_REVISION=0`: success, sha256 `1830ec74e73bf4d904fd280f80290301cca1de0255e7ad8471d082e1c36cd812`; built `prop_animations.narc` has 100 members and members 4/19/98/99 equal the committed files; the new `bm_anime_list.narc` bytes are present in the ROM.
* `make rom ROM_REVISION=1` (separate build dir): success, sha256 `ded41da824a29bc615a8224272f6ea40a6ef1a2bd03aedf143481f495a36f9b3`.
* Build tooling note: the sandbox blocks WrapDB, so rapidjson/yyjson wrap patches were reproduced locally from `subprojects/packagefiles` (ignored dirs, not committed); CI is unaffected.

## F. Not verified (owner-only)

Emulator/runtime/visual QA was **not performed** and is not claimed. Owner checks: lake drift reads as water rather than wobble;
Snowpoint lake (same prop); waterfall gust amplitude; machine pulse cadence in Galactic HQ and other interiors that share the props;
Distortion World cliff breathing on `prop_model_583` (texel steps visible? any rim shimmer objectionable?).
All values are first-pass and tunable in the `SURGE` / `BREATH_*` tables only; re-pin with `--pin` from retail sources.

## G. Deferred blockers and what remains possible

* **Distortion World palette pulse (vein glow)** — needs a new brighter palette in `prop_texture_set_070.nsbtx` plus an NSBTP; the repo has no
  NSBTX palette-add writer and the blast radius of a bad TEX0 is the whole area. Remains V04/V05 follow-up.
* **`prop_model_582` cliffs** — material `criffp_lm3` clamps T; only an S scroll is safe and the horizontal-band texture shows almost nothing.
  Needs a model material flag edit (outside AV2's no-model-edit rule).
* **Multi-material new NSBTA authoring** — the writer is bit-exact for single-material files; retail multi-material files carry an
  unexplained 16-byte per-material block between sample arrays, so AV2 patches those in place and does not synthesize new ones
  (e.g. waterfall mist `kemuri`, left untouched).
* **Shared props** — machine props (`158`, `114`, `314`) are catalogue members of many generic interior prop sets, so the
  re-timing is global to those props. Isolating Galactic-only copies means cloning models/area data (not done).
* **Distortion World map tiles / floor** have no animation hook; truly animating them needs engine work.
* Other candidates seen but not touched: Pastoria gym water floor (`014`, puzzle-coupled), ship/pool water (`037/038/043/045/068/086`),
  fountain (`000`).

## H. Rollback

Revert the PR. Partial: restore any single `prop_animation_0xx.nsbta` from `e91ee103`; to drop Distortion World, restore record 583 of
`bm_anime_list.narc` to the retail bytes (documented above) and delete files 098/099 with their list entries.
