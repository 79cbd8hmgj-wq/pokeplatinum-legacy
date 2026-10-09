# IO-STATUS — 3D palette ownership audit

Baseline: `main` `089cfc0f2a0dfd4466c964fcd13ae4406681cabf`. Source findings only, no battle source/assets modified.

## Direct source evidence

- `src/pokemon_sprite.c` defines `MAX_MON_SPRITE_PALETTES = MAX_MON_SPRITES + MAX_MON_SHADOWS`, and allocates CPU palette buffers accordingly in `PokemonSpriteManager_New`.
- The same constructor initially sets `plttSize = PALETTE_SIZE_BYTES * MAX_MON_SPRITES`; `PokemonSpriteManager_SetPlttBaseAddrAndSize` may change that size. GPU upload uses the *current configured* `plttSize` in `PokemonSpriteManager_UpdateCharAndPltt` when `needLoadPltt` is set.
- Each active battler reload writes a 16-colour palette at bank index `i`; the 3D draw loop binds bank `i` with `G3_TexPlttBase`.
- A shadow may write or fade bank `MON_SHADOW_BASE_PLTT_SLOT + shadow.plttSlot` (base = 3); that bank is also rebound by the 3D draw loop. Do not assume that higher indices are free, including bank 4 or 5.
- Switching, fading and other updates modify palette data, and `needLoadPltt` controls GPU reupload. Writing glyph colours directly to CPU slots alone is insufficient unless upload size and refresh semantics are proven.

## Decision

**Do not use purportedly spare battler/shadow palette slots for the glyphs.** The six-bank CPU allocation and initial four-bank upload setting are not evidence of two unused dedicated GPU palette banks. A safe implementation must prove *current battle-specific* palette ownership including all calls to the size/address setters and shadow-bank bounds, or instead use a renderer treatment that requires no new palette slot.

## Bounded candidate strategies

1. **Palette-independent polygon colours:** Investigate a flat-colour/texture-free status-symbol composition in the same 3D draw pass, with no borrowed palette indices. Must verify how opaque/masked symbols and geometry state can be drawn, preserving other 3D draws. This would make atlas glyph texels unnecessary and would replace the preferred atlas plan.
2. **Shared atlas + explicitly owned palette:** Only if the battle renderer can reserve an actual 3D palette bank with audited VRAM extent and upload/teardown, *not* a visually unused bank; the 16x16 glyph rectangles verified in the atlas audit remain candidate texel space.
3. **Separate texture and palette:** Verify the battle 3D VRAM allocator before choosing; fail closed on exhaustion.

**Do not start drawing overlays until one of these three paths has a source-grounded resource and render-state proof.** The work remaining is focused setter call-site ownership and, preferably, palette-free 3D primitive feasibility. OAM capacity is not needed for option 1 or 2. User retains final emulator testing; compile/static/integration validation continues throughout development.

## Existing source checks

- `src/pokemon_sprite.c` around the constructor `PokemonSpriteManager_New`, `PokemonSpriteManager_SetPlttBaseAddrAndSize`, `PokemonSpriteManager_UpdateCharAndPltt`, `BufferPokemonSpritePlttData` and `PokemonSpriteManager_DrawSprites`.
- `docs/visual_overhaul/implementation/IO_STATUS_ATLAS_WRITE_RANGE_AUDIT.md`
- `docs/visual_overhaul/implementation/IO_STATUS_RENDERER_ALTERNATIVES_AUDIT.md`

## Next executable work

Perform targeted call-site audit of texture and palette base/size setters, then prototype *one glyph* as a source-verified untextured/flat-colour primitive in the existing 3D projection without a new palette or texture allocation, if possible. Confirm status ownership and draw-pass ordering, then two effects and animation. If primitive drawing is infeasible, revisit explicitly-owned atlas palette strategy.
