# IO-PAL-CYCLE water pilot — implementation record

Class: `technique_donor` · donor pixels reused: **0** · Platinum is the visual host · water terrain only.
Preflight: `IO_PAL_CYCLE_PREFLIGHT.md` (treated as authoritative).

## Answers to the five remaining questions

1. **Detecting an active fade on `PLTTBUF_MAIN_OBJ`.** `PaletteData_GetSelectedBuffersMask(paletteData) & PLTTBUF_MAIN_OBJ_F`.
   `PaletteData_StartFade()` sets the buffer's bit in `selectedBuffers`, and `UpdateFadeBlendStep()` clears it when `cur == end`.
   The pilot also checks `PLTTBUF_MAIN_BG_F` because it mirrors BG slot 7.
2. **Committing a small OBJ range.** `PaletteData_CommitFadedBuffers()` only uploads (the whole buffer) while a fade has flagged the
   buffer, so there is no "commit a sub-range" API. The supported pattern, used by the Distortion World sky clouds and the Great Marsh
   lookout, is: write the range in the `PaletteData` buffers, `DC_FlushRange`, then `GX_LoadOBJPltt(src, PLTT_OFFSET(idx) + byteOffset, size)` from a SysTask.
   When no fade owns the buffer the pilot writes unfaded **and** faded, then hardware. During a fade it writes nothing (see below).
3. **Shared vs independent palette.** Shared. `SpriteSystem_LoadPlttResObjFromOpenNarc()` returns -1 when resource 20009 is already loaded,
   so the second `Terrain_Init` (enemy side) allocates nothing and `SpriteSystem_LoadPaletteBufferFromOpenNarc()` returns `0xFF` for it
   without touching the buffer. The player-side terrain (initialised first) owns the single OBJ palette allocation; both sprites render with it.
   Resource 20009 is unloaded once (the second unload is a no-op). The cycle is therefore owned by the side whose load returned a valid index.
4. **BG slot 7 consumer.** `BattleSystem_BakeSpritesToBackground()` bakes the terrain sprite pixels into BG tiles with palette 7 (`colorIdx + 0x70`)
   and snapshots the BG *unfaded* palette buffer. Nothing else reads slot 7 as a terrain colour. It is mirrored (see below) so a baked terrain matches the
   phase that was on screen. The mirror has no other effect.
5. **Indices / interval.** Indices **4–7**, step every **16 frames**, shifts `{0, +1, 0, -1}` with clamping (see below).

## Architecture

- `src/battle/terrain.c`: `SysTask_CycleWaterPalette` (SysTask, priority 60001), started from `Terrain_LoadResources()` via
  `Terrain_StartPaletteCycle()` only when `terrainType == TERRAIN_WATER` and the OBJ load returned a valid palette index.
  The index returned by `SpriteSystem_LoadPaletteBufferFromOpenNarc()` is now captured (`Terrain.objPaletteIdx`); previously discarded.
- `Terrain` gained `paletteTask`, `cycleBaseColors[4]` (snapshot of the loaded colours, so day/evening/night identity is inherited),
  `objPaletteIdx`, `cycleTimer`, `cycleStep` (replacing two unused `s16`).
- `Terrain_StopPaletteCycle()` ends the task and restores the base colours if the palette is still in a cycled state.
  Called from `Terrain_Destroy()` (bake path) **and** from the normal battle exit in `battle_main.c` (right after `sub_02015760`, before
  `PaletteData` is freed). `Terrain_Destroy` is not reached on a normal battle exit, so the exit hook is required to avoid a leaked task.
- `BattleSystem_GetRenderMode()` added (the field existed, no getter did).
- No generic framework; the existing `PaletteAnimator` (`unk_0201567C`) is BG-only and was not reused.

## Animated palette indices

Entries **4, 5, 6, 7** of the 16-colour water palette (mid-light highlight bands). Untouched: 0 (transparent), 1–2 (outline/shadow black),
3 (brightest sparkle), 8–15 (body and shadow tones; 8 and 12 are the dominant tones in the sprites). Entries 4–7 cover 815 of 3,048 drawn pixels in `enemy.png` and 1,201 of 4,128 in `player.png` (~27–29%).

## Tick interval

16 frames per step (~0.27 s), 4 phases, loop ≈ 1.07 s. Phase `p` assigns slot `i` the base colour `base[clamp(i + shift[p], 0, 3)]`
with `shift = {0, +1, 0, -1}`: each slot moves at most **one ramp rung** per step and there is no wrap-around jump, which keeps motion subtle and flicker-free.

## Fade and effect behaviour

The task does nothing (and does not advance its phase) when:
- `renderMode != 0` (bag/party/move-forget sub-menus, post-catch screens own the palettes);
- `PLTTBUF_MAIN_OBJ` or `PLTTBUF_MAIN_BG` is selected for a fade (the fade's own blend from the unfaded buffer governs the result);
- the unfaded range is neither the current cycle phase nor the base colours (palette slot is not water-owned, e.g. sub-menu data not yet restored);
- the faded range differs from the unfaded range (another effect tinted the faded buffer directly).

The unfaded buffer is updated whenever a write happens, so a later fade or `savedObjPalettes` restore starts from a valid colour set; a restore
that re-installs the step-0 colours is recognised as base colours and the cycle simply continues from them.

## OBJ palette ownership / reuse

One OBJ palette (resource 20009), allocated by the player-side `Terrain_Init`, shared by both platform sprites. `Terrain.objPaletteIdx` is only
set on the owning side; the enemy-side `Terrain` has `paletteTask == NULL` and is a no-op for start/stop. The state lives in the `Terrain`
struct (inside `BattleSystem`), is zeroed by `Terrain_Init`/`Terrain_Destroy`, and the task is ended on both exit paths, so nothing persists between battles.

## BG slot 7

Mirrored (unfaded + faded buffer + hardware slot, same four entries, same guards). Reason: the bake path snapshots the BG unfaded palette and bakes
terrain pixels with palette 7; mirroring keeps a baked platform on the same phase that was on screen. Without the mirror the baked platform would
step back to base colours (<= one rung change). BG slot 7 is not otherwise visible during the cycle.

## Files changed

- `src/battle/terrain.c`, `include/battle/terrain.h`
- `src/battle/battle_main.c` (exit hook), `src/battle/battle_system.c`, `include/battle/battle_system.h` (render-mode getter)
- `docs/visual_overhaul/implementation/IO_PAL_CYCLE_WATER_PILOT.md`

No palette/tile assets changed; non-water terrains never start the task.

## Validation

See the PR description for the actual results. Runtime scenarios still needing an emulator pass (not executed in the authoring environment):
normal water battle, fade in/out, palette/blend move effects, double battle, day/evening/night, consecutive battles, non-water regression.
