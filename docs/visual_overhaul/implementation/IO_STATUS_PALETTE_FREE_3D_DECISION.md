# IO-STATUS — Palette-free 3D pilot architecture decision

**Baseline:** main `0bd2f79d60ae980cf1fcbb546b5c16a73e59a64c`. **Scope:** targeted technical decision; no status glyphs shipped in this PR.

## Important correction from call-site audit

`PokemonSpriteManager_New` defaults to four 16-colour banks, **but battles explicitly override that** in `src/battle/battle_main.c:587`:

```c
PokemonSpriteManager_SetPlttBaseAddrAndSize(battleSys->monSpriteMan, 0, PALETTE_SIZE_BYTES * 6);
```

The battle therefore uploads all six configured battler/shadow banks. Neither the default four-bank setting nor the six-bank CPU buffer supplies an unused palette slot. The previous audit's warning *not to borrow an unowned palette* remains correct, but any description of actual battle uploads as four banks must be read in light of this call site.

## Renderer integration point

`src/battle/battle_main.c` creates `SysTask_DrawSprites` at priority 60000 (line 620). This task draws particles only in normal render mode 0, then calls `PokemonSpriteManager_DrawSprites`, `SpriteSystem_DrawSprites`, `SpriteSystem_UpdateTransfer`, and finally `G3_RequestSwapBuffers`. It runs in mode 0 or 3, so overlays should be strictly disabled in mode 3.

**Preferred integration:** draw the glyphs within the existing `SysTask_DrawSprites` frame, immediately after the Pokémon quad draw and before swap, with no new persistent SysTask and no direct pointer caching. Access the current battle context only while it is live. Gate the effect on normal render mode and existing battle-type exclusions documented in `IO_STATUS_COMPOSITE_PREFLIGHT.md`.

## Chosen first implementation candidate: untextured 3D primitives

Investigate an untextured polygon glyph implementation using the Nitro 3D direct-geometry API. The goal is to make **both the main-OBJ capacity and battler texture/palette slots irrelevant**: symbols would be composed from a small number of coloured opaque/alpha polygons rather than sprite textures.

A source-only candidate is **not yet API-verified or built**. In particular:

- Prove the exact SDK sequence for disabling texture sampling (e.g. the supported texture-format-none state), vertex colours/material behaviour, polygon alpha and screen projection in this repository's Nitro SDK.
- Prove restoring `G3_TexImageParam`, `G3_TexPlttBase`, polygon/material state and matrix stack does not disrupt the next 3D consumer. Merely drawing shapes between `PokemonSpriteManager_DrawSprites` and `SpriteSystem_DrawSprites` is insufficient without state ownership proof.
- Respect per-battler visible/position/vanish/substitute/scale lifecycle. Preserve render mode and link/recording/Safari/Pal Park/tutorial exclusions.
- Limit to confusion and infatuation, singles first and doubles after static screen-position checks.
- No animation task or new heap state necessary for a two-phase pulse: derive phase from an existing safely read frame counter only if source verified; otherwise use bounded state held by the battle system with explicit initialization and no dangling context pointers.
- Gate geometry command budget; use conservative per-battler polygon count; do not assert visual acceptance before owner tests.

**Fallback** if untextured geometry cannot produce legible symbols or introduces unsafe state: the existing atlas write-range proof found four candidate 16×16 rectangles at y=240, but that route still requires an explicitly owned palette strategy. A texture atlas region alone does not solve palette ownership.

## Implementation acceptance (before merge)

1. Native ROM builds for applicable revisions pass CI.
2. Deterministic checks for glyph geometry, batch count/limits and fade/visibility gating.
3. Source audit of all palette/texture state restoration and lifecycle.
4. Only after that, mark **source implemented — owner runtime QA deferred**; the owner will perform emulator/hardware testing after the visual implementation phase.

## Status

**Gate C original OBJ capacity issue can be sidestepped architecturally; it has not been proven for a shipped alternative renderer.** Gate D becomes *geometry definitions + visual specification* for an untextured pilot rather than required NCGR/NCER/NANR/NCLR assets. Do not call the feature complete until code and build evidence exist.
