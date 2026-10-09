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

## Render-state audit (PR #92 follow-up)

Method: traced every 3D command the overlay issues, then read each 3D consumer that can run after it. State that the hardware cannot read back is handled with a source-verified contract, not by guessing a getter (the pinned SDK exposes none for polygon attributes, texture parameters or vertex colour).

### Rendering sequence

Each frame in render mode 0 (`SysTask_DrawSprites`): `ParticleHelper_DrawParticleSystems` (starts with `G3_ResetG3X` → `G3X_Reset`) → `PokemonSpriteManager_DrawSprites` → **`BattleStatusOverlay_Draw`** → `SpriteSystem_DrawSprites` (OAM only) → `SpriteSystem_UpdateTransfer` (cell transfer) → `G3_RequestSwapBuffers` (deferred; the swap is issued later by `sub_020241CC` in the main loop (`main.c`), so the overlay's commands are submitted before it). Mode 3 frames skip the particle call and the overlay but still run the mon pass. No other 3D command issuer exists in `src/battle`, `src/battle_anim` or `src/battle_sub_menus` apart from the one-time `G3X_*` setup in `battle_main.c` (checked by the validator).

### State by state

| State | Overlay action | Restored explicitly? | What later consumers do (source-verified) |
|---|---|---|---|
| Texture image param / texgen | `GX_TEXFMT_NONE`/`GX_TEXGEN_NONE` for the polygons | **Yes**: re-issued with the mon pass's exact argument list (validator compares the two argument lists) | Mon pass sets it once before its loop; SPL sets it per emitter; `G3X_Reset` sets it |
| Texture palette base | never written | n/a (untouched) | Mon pass sets it per quad; SPL per emitter; `G3X_Reset` sets it |
| Texture matrix / matrix mode | never written | n/a (untouched) | – |
| Polygon attribute (ID, alpha, cull, light, mode) | unlit, MODULATE, cull-none, alpha 31, ID `8+battler` | No (write-only register) | Mon pass sets it per quad (shadow quad reuses its own iteration's value); SPL sets it per particle (`SPLDraw_Setup`); `G3X_Reset` sets it at the start of every mode-0 frame |
| Vertex colour | `G3_Color` | No (write-only register) | Mon pass: `G3_MaterialColorDiffAmb(..., TRUE)` sets it per quad; SPL: `G3_Color` per particle |
| Material (diffuse/ambient/specular/emission) | never written; lighting is masked off | n/a (untouched) | – |
| Matrix stack depth / current matrix | one `PushMtx`/`PopMtx(1)` pair plus nested per-star pairs, max depth 3 | **Yes** (balanced on every path) | `G3X_Reset` also clears the stack each mode-0 frame |
| Begin/End | strictly paired; only `Color`/`Vtx` inside | **Yes** | – |
| Command buffer ordering | `NNS_G3dGeFlushBuffer` before the first overlay command, as the mon pass does; all direct-register writes afterwards | n/a | Overlay is the last geometry submitted in the frame |
| Depth / opacity | opaque, depth-tested; fill is ≥ 8 units nearer than the battler quad on every orbit frame, outline 4 units behind the fill (still nearer than the battler) | n/a | Edge marking is off (`G3X_EdgeMarking(FALSE)`), so polygon IDs have no visual effect |

Findings:

* **No unsafe leak was found**, so the overlay's rendering code is unchanged by this follow-up (only its comment was rewritten to state the verified contract). Polygon attribute and vertex colour do leave the overlay's values behind, but every consumer sets them before drawing, and the mon pass already left its last sprite's values behind in the same way before the overlay existed.
* Vertex RAM / polygon RAM: the overlay adds at most 48 polygons / 192 vertices after everything else; if the hardware lists were ever full, the stars would be dropped rather than a battler.
* Teardown: the draw task, `BattleContext_Free` and `SysTask_Done(taskDrawSprites)` all sit in the single synchronous `BattleMain_CopyBattleSysToDTOAndFree`, which cannot yield to the main task manager (the validator rejects task-manager/yield calls there). The capture→naming early free sets render mode 1 in the same call as `BattleSystem_FreeGraphics`. Mode 1/2 are never drawn.
* Link position: `BattleStatusOverlay_Draw` is at `0x02264b38`, inside the battle overlay (`0x0223b3c0–0x02271580`) next to its caller `SysTask_DrawSprites` (`0x0223d1dc`), for both revisions.

### Validator strengthening

`validate_confusion_overlay.py` now parses the overlay's functions with a small C-subset interpreter and executes the command stream on every control-flow path (guards, optional `Identity`, 0/1/2/4 battlers). Per path it enforces: matrix balance/bound, Begin/End pairing and contents, whitelist of G3 commands, flush-first, no `return` after commands, no commands when nothing is drawn, the texture state machine (manager → NONE before the first polygon → manager's exact arguments after the last), PolygonAttr before every Begin and its exact form, and budgets measured from the trace (48 polygons / 192 vertices for four battlers). It also checks the consumer contract in the repo sources (mon pass, `G3_ResetG3X`/`G3X_Reset` — against the pinned SDK source when the subproject is present — SPL, `SysTask_DrawSprites` ordering, the inventory of 3D issuers, edge marking, polygon-ID assumption, teardown shape, meson + `main.lsf`). A built-in mutation suite injects 48 defects (missing restore, wrong restore arguments, restore in the wrong place, unbalanced push/pop, missing Begin/End, extra vertices, missing/translucent/lit PolygonAttr, forbidden commands, misplaced flush, early returns, commands with no battler, wrong call order, missing registration, broken consumer contract, …); each must be rejected, and it runs by default (also in CI).

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
| `make rom ROM_REVISION=0` (Metrowerks, local) | pass; ROM identical to the pre-follow-up build (comment-only source change) |
| `make rom ROM_REVISION=1` (Metrowerks, local) | pass; same |
| `platinum.us/main.lsf` placement | `BattleStatusOverlay_Draw` linked at `0x02264b38` in the battle overlay, both revisions |
| `tools/visual_overhaul/io_status/validate_confusion_overlay.py` | pass: 9 control-flow paths traced (6 emit geometry), SDK `G3X_Reset` source verified, **48/48 mutants rejected** (each for the intended reason) |
| `clang-format` 19.1.1 on new/edited C | clean |
| Existing `g7-visual-validation` validators, pristine `main` vs this branch | identical results |

Findings during implementation:

1. **`platinum.us/main.lsf` lists objects per overlay.** Without an entry the build succeeds but the symbol is unplaced (address 0) and the call would jump to 0. The object is now in the `battle` overlay (symbol at `0x02264b38`); the validator guards this.
2. **Depth:** the back-most star initially landed at exactly the battler's depth and would have been rejected by the LESS depth test. Bias raised to 24; the validator checks fill and outline stay strictly nearer for every orbit frame.

## Historical / pre-existing (not regressions)

* `validate_atlas_write_ranges.py` already fails on pristine `main` (expects `for (i = 0; …` loops that the source declares as `for (int i`). That audit is not used by this path and is untouched.
* Locally `validate_g76_atmosphere`, `validate_g7_core_menus`, `validate_g77_final_cohesion` fail identically on pristine `main` and this branch (shallow clone lacks their baseline commits; CI uses `fetch-depth: 0`).

## Deferred to owner

Runtime check of anchor position (singles/doubles, back vs front sprites), apparent size and colour, depth against the battler and shadow, behaviour through send-out/switch/faint/vanish/substitute, confusion ending, repeat battles, sub-menu hide, and overall art acceptance. Palette-free design means no palette work is needed if the look is adjusted: tune the constants at the top of `battle_status_overlay.c`.

Unresolved risks reserved for that runtime pass (none is a renderer-state hazard):

* **Rotation:** the mon quad can be rotated by move animations (`rotationX/Y/Z` about its pivot); the overlay ignores rotation and follows only centre, offsets, scale and shadow height, so the stars may not follow a spinning sprite. Hiding during rotation is a one-line option if the owner prefers.
* **Partial alpha:** only alpha 0 hides the overlay; during an alpha fade of the battler the stars are drawn fully opaque.
* **Anchor offset:** the vertical anchor assumes the sprite art sits within the 80×80 frame; tall or short species may need a per-sprite offset.
* **Hardware behaviours not exercisable here:** the list-RAM-overflow behaviour and G3X_Reset semantics are taken from SDK source and documentation, not observed.

## Next (not started)

Infatuation via a second glyph in the same pass, only after owner review of this pilot.
