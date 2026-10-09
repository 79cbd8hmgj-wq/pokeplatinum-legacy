# IO-STATUS — confusion overlay pilot (implementation record)

**Baseline:** `main` `b3a4f8a7` (includes PRs #88–91). **Status: source implemented, both US revisions build; owner runtime and art QA deferred.** Confusion only; infatuation is intentionally not started.

## What it does

Three yellow four-point stars (dark outline) orbit above any battler whose `BATTLEMON_VOLATILE_STATUS & VOLATILE_CONDITION_CONFUSION` is non-zero. The orbit is a 64-frame loop; stars swell and move nearer as they swing to the front.

Files: `src/battle/battle_status_overlay.c`, `include/battle/battle_status_overlay.h`; one call added to `SysTask_DrawSprites` (`src/battle/battle_main.c`); registrations in `src/meson.build` and `platinum.us/main.lsf`.

## API verification (before committing to the approach)

Checked against the repository's pinned SDKs (`NitroSDK` `e6fbeba6`, `NitroSystem` `21c8fd07`) and by compiling with the project's Metrowerks toolchain:

| Need | Evidence |
|---|---|
| Untextured polygons | `GX_TEXFMT_NONE = 0` is accepted by `G3_TexImageParam` (`GX_TEXFMT_ASSERT` range starts at `GX_TEXFMT_NONE`); only `G3_TexPlttBase`/`G3_MakeTexPlttBaseParam` assert against it, and the overlay never calls those. |
| Vertex colour only | `G3_Color` + `G3_Begin(GX_BEGIN_QUADS)` + `G3_Vtx`, polygon mode MODULATE, `GX_LIGHTMASK_NONE`; the material registers are never written. |
| Pixel-space projection | `NNS_G2dSetupSoftwareSpriteCamera` (called by `PokemonSpriteManager_New`) sets an ortho camera where 1 unit = 1 pixel; the battler quad is placed by `Translate/Scale`, and the overlay uses the same convention. |
| Vertex range | `G3_Vtx` takes 4.12 `fx16` (±8.0). Stars are unit-sized and positioned/scaled with `G3_Translate`/`G3_Scale`. |

## Render-state handling

* Runs inside the existing `SysTask_DrawSprites`, after `PokemonSpriteManager_DrawSprites`, before `SpriteSystem_DrawSprites` and the buffer swap. **No new task.**
* `NNS_G3dGeFlushBuffer` first (as the mon pass does); every command is inside one `G3_PushMtx`/`G3_PopMtx(1)` pair (per-star pairs nested inside), so the matrix stack/current matrix are unchanged.
* `G3_TexImageParam` is switched to `GX_TEXFMT_NONE` for the overlay and re-issued with the same `imageProxy` values the mon pass used. `G3_TexPlttBase`, polygon attributes and the current vertex colour are write-only registers that every later 3D consumer (particles, next frame's mon pass) re-issues before drawing; the overlay does not rely on or alter palette ownership. Material colour is never written.
* No commands are issued at all unless at least one battler qualifies.
* Opaque only (alpha 31); polygon IDs `8 + battler` (battler quads use 0–3). Fill is drawn nearer than the battler quad and the outline is 4 units behind the fill.

## Lifecycle / mechanics safety

* Strictly read-only: `BattleMon_Get` for HP and volatile status; `PokemonSprite_GetAttribute` for geometry. No battle state, RNG, or sprite attribute is written.
* The sprite pointer is re-read every frame via `BattlerData_GetPokemonSprite` and gated by NULL check → `PokemonSprite_IsActive` (deleted sprites only clear `active`; `BattlerData` is not NULLed). Never cached.
* The battle context is fetched per call; the draw task exists before the context does, so `BattleSystem_IsInitialized` gates the pass. Teardown frees the context and `SysTask_DrawSprites` in the same call, and modes 1/2 skip drawing entirely.
* Hidden when: mode ≠ 0 (sub-menu mode 3 included), HP = 0, `HIDE`/`HIDE_2`, partial draw (move-animation clipping), alpha 0, scale ≤ 0, inactive sprite.
* Disabled for `BATTLE_TYPE_LINK`, `SAFARI`, `PAL_PARK`, `CATCH_TUTORIAL`, and `BATTLE_STATUS_RECORDING`.
* Singles first; the loop already iterates `BattleSystem_GetMaxBattlers`, with per-battler anchors, so doubles use the same path (position needs owner verification).
* No file-scope state. The orbit phase derives from `gSystem.frameCounter`.
* No allocation, no OAM, no texture/palette/atlas write.

Budget: 12 polygons / 48 vertices per battler (48 / 192 for four) — far below the 2048 / 6144 hardware limits.

## Validation performed

| Check | Result |
|---|---|
| `make rom ROM_REVISION=0` (Metrowerks, local) | pass |
| `make rom ROM_REVISION=1` (Metrowerks, local) | pass |
| `tools/visual_overhaul/io_status/validate_confusion_overlay.py` (new; gating, read-only, no-alloc, state balance, call-site order, meson + lsf registration, orbit/depth/budget math). Mutation-tested: 5 injected defects all rejected | pass |
| `clang-format` 19.1.1 on new/edited C | clean |
| Existing `g7-visual-validation` validators, run locally on pristine `main` and this branch | identical results |

Findings during implementation:

1. **`platinum.us/main.lsf` lists objects per overlay.** Without an entry the build succeeds but the symbol is unplaced (address 0) and the call would jump to 0. The object is now in the `battle` overlay (symbol at `0x02264b38`); the validator guards this.
2. **Depth:** the back-most star initially landed at exactly the battler's depth and would have been rejected by the LESS depth test. Bias raised to 24; the validator checks fill and outline stay strictly nearer for every orbit frame.

## Historical / pre-existing (not regressions)

* `validate_atlas_write_ranges.py` already fails on pristine `main` (expects `for (i = 0; …` loops that the source declares as `for (int i`). That audit is not used by this path and is untouched.
* Locally `validate_g76_atmosphere`, `validate_g7_core_menus`, `validate_g77_final_cohesion` fail identically on pristine `main` and this branch (shallow clone lacks their baseline commits; CI uses `fetch-depth: 0`).

## Deferred to owner

Runtime check of anchor position (singles/doubles, back vs front sprites), apparent size and colour, depth against the battler and shadow, behaviour through send-out/switch/faint/vanish/substitute, confusion ending, repeat battles, sub-menu hide, and overall art acceptance. Palette-free design means no palette work is needed if the look is adjusted: tune the constants at the top of `battle_status_overlay.c`.

## Next (not started)

Infatuation via a second glyph in the same pass, only after owner review of this pilot.
