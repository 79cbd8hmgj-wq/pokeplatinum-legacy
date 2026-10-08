# IO-PAL-CYCLE implementation preflight

Status: source-level preflight only. No Platinum source/assets modified.

Target: `IO-PAL-CYCLE` — battle terrain palette/tile-cycle service, water platform pilot.

## Implementation philosophy

This is a **technique donor** implementation, not an asset replacement.

- PMD Sky supplies the palette/tile-cycling idea.
- FireRed only corroborates timing/sequence behavior.
- Donor pixels reused: **0**.
- Platinum remains the host and visual identity.
- The first pilot is water only.

## Verified Platinum terrain resource path

`src/battle/terrain.c` owns the circular battler platforms.

`Terrain_LoadResources()`:
- selects the player/enemy platform NCGR from `sTerrainSpriteSource_PlayerSide` / `sTerrainSpriteSource_EnemySide`.
- selects day/evening/night palette through `sTerrainPaletteSource[terrainType][bgTimeOffset]`.
- loads the visible platform palette through `SpriteSystem_LoadPaletteBufferFromOpenNarc(..., PLTTBUF_MAIN_OBJ, ..., resourceID=20009)`.
- also loads the same NCLR into `PLTTBUF_MAIN_BG` at `PLTT_DEST(7)`.

For `TERRAIN_WATER`, the three palette resources are:
- `terrain_water_day_NCLR`
- `terrain_water_evening_NCLR`
- `terrain_water_night_NCLR`

Source palettes:
- `res/graphics/battle/terrain/water/day.pal`
- `res/graphics/battle/terrain/water/evening.pal`
- `res/graphics/battle/terrain/water/night.pal`

The current G5 palette generator authors all three in:
`tools/visual_overhaul/generate_battle_terrain.py`.

## Important correction: BG slot 7 is not the whole visible platform path

The visible battle platform is an OBJ sprite.

`SpriteSystem_LoadPaletteBufferFromOpenNarc()` calls
`SpriteSystem_LoadPlttResObjFromOpenNarc()`, requests OBJ palette VRAM,
returns the dynamically allocated palette offset, then mirrors the hardware
palette into the requested `PaletteData` buffer.

Therefore:
- the terrain's visible palette lives in **MAIN OBJ palette memory** at the offset returned by the sprite transfer system;
- `PLTTBUF_MAIN_BG` slot 7 is a separate copy loaded by `Terrain_LoadResources()`;
- animating only BG slot 7 is insufficient to prove that the visible platform will animate.

Claude should not spend time rediscovering this distinction.

## Existing PaletteAnimator is useful evidence but is BG-only

`src/unk_0201567C.c` / `include/unk_0201567C.h` already implement a small SysTask palette animator.

Construction:
`sub_0201567C(PaletteData *paletteData, u16 screen, u16 paletteSlot, heapID)`

Behavior:
- if `PaletteData` is supplied, screen 0 selects `PLTTBUF_MAIN_BG`, screen 1 selects `PLTTBUF_SUB_BG`;
- if no `PaletteData` is supplied, it targets raw main/sub BG hardware palettes;
- it snapshots one 16-color palette;
- its SysTask runs continuously;
- state 2 pauses;
- state 3 restores the original palette and frees the task;
- the built-in animation touches mask `0x7800` (indices 11-14), changing them at counter 0 / 24 in a 32-tick loop.

This confirms:
- Platinum already has a SysTask-based palette-animation pattern;
- pause/restore semantics already exist;
- but this helper does **not** directly target `PLTTBUF_MAIN_OBJ`, so it should not be blindly reused for the terrain sprite.

Prefer adapting the pattern or a minimal generic helper over inventing a large new framework.

## Fade interaction verified

`src/palette.c` keeps separate unfaded and faded buffers.

`PaletteData_StartFade()`:
- configures selected palette buffers/masks;
- blends from the **unfaded** buffer into the faded buffer.

`PaletteData_CommitFadedBuffers()` then uploads the faded buffers to hardware.

Implication for IO-PAL-CYCLE:
- terrain animation should update the authoritative `PaletteData` unfaded OBJ palette range, not only hardware VRAM;
- otherwise a fade or later palette commit can overwrite the animation;
- if a fade is active, either update unfaded state and let fade recompute, or suspend visible cycling until the fade finishes;
- directly writing hardware-only colors is the fragile option.

## Sprite palette allocation path

`src/sprite_system.c` confirms:
- `SpriteSystem_LoadPlttResObjFromOpenNarc()` requests free palette VRAM;
- `SpriteTransfer_GetPlttOffset(resource, vramType)` returns the allocated palette index;
- `SpriteSystem_LoadPaletteBufferFromOpenNarc()` then mirrors that hardware palette into `PaletteData` using `PLTT_DEST(paletteOffset)`.

The existing `Terrain` struct does **not** store that returned offset.

Current struct:
- `ManagedSprite *managedSprite`
- `BattleSystem *battleSys`
- `u8 side`
- `u8 terrainType`
- two unused `s16` fields

Likely minimal implementation choices:
1. store the returned OBJ palette offset in one of the currently-unused terrain fields or a newly named field; or
2. query the sprite resource manager by resource ID 20009 if a clean API exists.

Option 1 is likely simpler and more deterministic for the pilot.

## Water palette shape

The current authored water palettes are 16-color ramps.

For all day/evening/night variants:
- indexes 1-2 are black;
- indexes 3-15 form the main water gradient/ramp;
- index 0 is a bright/light contextual color.

Do not rotate the entire 16-color palette.

A pilot should limit motion to a deliberately chosen subset of the water ramp and preserve:
- transparent/unused assumptions,
- outline/shadow entries,
- time-of-day identity.

Exact animated indices and tick interval should be chosen by implementation/testing, not donor copying.

## Minimal implementation direction

Recommended architecture:

1. In `Terrain_LoadResources()`, capture the returned MAIN OBJ palette offset when resource 20009 is loaded.
2. Add a tiny terrain-animation state to `Terrain` (or a battle-owned task) only when `terrainType == TERRAIN_WATER`.
3. Keep a pristine copy of the selected 16-color water palette or the animated subset.
4. On a low-frequency tick, produce the next Platinum-native ramp state.
5. Write the changed colors into the relevant `PLTTBUF_MAIN_OBJ` **unfaded** buffer at the terrain's allocated OBJ palette offset.
6. Ensure the faded buffer/hardware update follows existing PaletteData semantics.
7. Pause or safely coexist while a fade owns that buffer.
8. Restore original colors on `Terrain_Destroy()`.
9. Do not enable other terrains yet.

Avoid a general-purpose terrain animation framework unless the minimal pilot clearly needs one.

## Remaining implementation questions for Claude

Only these should require source work before coding:

1. What API/state should be used to detect an active fade for `PLTTBUF_MAIN_OBJ`?
2. What is the cleanest supported way to commit a small changed OBJ palette range after updating the unfaded buffer?
3. Are both player and enemy terrain sprites guaranteed to share resource ID 20009 / one palette allocation at a time, or does resource lifetime make the second load a no-op/reuse?
4. Is the BG slot-7 mirror consumed by any battle effect that expects the terrain colors? If so, mirror the same animated state there too.
5. Which water ramp indices and interval give subtle motion without flicker?

These are bounded implementation questions. Broad donor or terrain-system rediscovery is unnecessary.

## Known files

Primary:
- `src/battle/terrain.c`
- `include/battle/terrain.h`
- `src/palette.c`
- `src/sprite_system.c`
- `src/unk_0201567C.c`
- `include/unk_0201567C.h`
- `res/graphics/battle/terrain/water/day.pal`
- `res/graphics/battle/terrain/water/evening.pal`
- `res/graphics/battle/terrain/water/night.pal`
- `res/graphics/battle/terrain/water/meson.build`
- `tools/visual_overhaul/generate_battle_terrain.py`

## Boundaries

Do not:
- import PMD/FireRed pixels;
- touch non-water terrain in the pilot;
- restart donor mining;
- implement IO-CARD / IO-STATUS / IO-PREVIEW in this branch;
- treat BG slot 7 as the visible platform without proving the OBJ path.

