# V01 — Forest ambient foliage: feasibility result

Opportunity: V01 (`OPAL_POST_S2_DONOR_ROADMAP.md`). Result: **NO-GO (blocked); no runtime code changed.**
Static source inspection only. No emulator, runtime or visual testing was performed or is claimed.
Base: `85304fdc` (PR #98 merge).

## Existing host (confirmed in source)

- `ForestAmbienceRenderer` (`src/overlay005/field_effect_renderer.c`): one `SysTask` (priority 255); every 90 frames it calls `BerryPatchGraphics_NewSparkleEffectAt` at one of six rotating offsets around the player. `_Free` ends the task and frees the heap block. It is registered as `FIELD_EFFECT_RENDERER_FOREST_AMBIENCE` in `sFieldEffectRendererHandlers` and listed in `sForestFieldEffectRenderers`.
- `fieldmap.c` selects `sForestFieldEffectRenderers` via `FieldMap_IsDeepForest`, which matches Eterna, Fullmoon and Newmoon forests. Eterna's dedicated area-data 075 does not give it a separate renderer list, so any change to this renderer is shared by all three maps unless explicitly gated.
- The task, lifecycle and cleanup are sound and should be reused rather than duplicated.

## Why the trap-effect leaf cannot be used

1. **Format mismatch.** `res/graphics/trap_effects/leaf.png` + `leaf_cell.json` + `leaf_anim.json` build (via `trap_effects/meson.build`) to NCGR/NCLR/NCER/NANR in `trap_effects.narc`. These are 2D OAM sprite resources: one 16×16, 16-colour OBJ cell, a single animation frame (delay 4), no motion of its own.
2. **Field effects are 3D billboards, not OAM sprites.** The sparkle path (`BerryPatchEffectCounter_EnableEffects` → `ov5_021DF9E0/ov5_021DFA14/ov5_021DFA3C/ov5_021DF864`, `Billboard_*`) loads NSBMD/NSBTX/animation members only from the field-effect manager's `fldeff.narc` (`NARC_INDEX_DATA__MMODEL__FLDEFF`, opened in `field_effect_manager.c`) by numeric member index.
3. **`fldeff.narc` is opaque.** It exists only as `res/prebuilt/data/mmodel/fldeff.narc`; there is no source-controlled input or build rule. Adding a leaf billboard model/texture would require patching a binary archive and guessing member IDs, both prohibited by the V01 protocol.
4. **The only other consumer of the leaf resource is the Underground** (`src/underground/{traps,manager,mining,secret_bases,top_screen}.c`), which is trap/input-coupled and was ruled out as a runtime to borrow.
5. **A new 2D-OBJ-over-3D path would be new infrastructure.** The field does initialise `CharTransfer`/`PlttTransfer` (`ov5_021D15B4`) and maps `GX_VRAM_OBJ_32_FG`, and `trap_effects.narc` is a normal NARC index, so a bespoke path is theoretically possible. It would need its own sprite list/render-OAM setup, char and palette VRAM allocation against the field's shared OBJ allocator, world-to-screen projection against the field camera, per-leaf software drift (the NANR has one frame), teardown on map change/battle/menu transitions, and interaction with fog, weather and the fade, with no way to check OBJ VRAM/OAM conflicts without runtime testing. That is the "substantial new infrastructure" condition in the task, not a small change.

## Go/no-go

| Route | Verdict |
|---|---|
| Add leaf billboard to `fldeff.narc` | Blocked: opaque prebuilt archive |
| Reuse Underground leaf runtime | Rejected: trap/input coupled |
| New 2D OBJ leaf system in the field renderer | Not attempted: new infrastructure, unverifiable statically |
| Re-skin existing sparkle | Not attempted: also needs `fldeff.narc` edits and would still change Fullmoon/Newmoon |

## Prerequisite for a future retry

A source-controlled way to build or extend a field-effect billboard archive (e.g. unpacking `fldeff.narc` into `res/` with a Meson rule and verified member order), or an explicitly approved scope for a field 2D OBJ particle subsystem. If implemented, gate it to Eterna (area-data 075) so Fullmoon/Newmoon stay unchanged; design recipe: low density, slow drift, small, no overlap of player/UI, reuse the 90-frame task.

## Recommendation

Proceed to **V02** (HGSS-to-Eterna texture comparison). Donor findings (HGSS/Ranger/PMD Sky) were not re-mined.

## Checks / builds

No source or resource files changed, so no ROM build was needed or run for this result. Runtime behaviour untested (owner-run).
