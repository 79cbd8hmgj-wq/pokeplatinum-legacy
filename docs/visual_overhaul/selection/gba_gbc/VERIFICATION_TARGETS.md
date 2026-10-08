# GBA/GBC verification target map

This map converts the deferred hypotheses into exact source paths and symbols at the pinned donor revisions. It is intended to prevent future agents from spending context rediscovering the donor code layout.

## Strongest preflight confirmations

- **Emerald field actions:** `src/field_effect.c` contains dedicated indoor/outdoor field-move presentation state machines plus explicit Surf, Fly and Waterfall sequences.
- **FireRed location previews:** `src/map_preview_screen.c` directly binds each preview to map section, visited flag, tiles, tilemap and palette.
- **FireRed palette animation:** `src/field_specials.c` contains Elite Four/Champion palette arrays, timer arrays and a task that reloads BG palette slot 7 over time.
- **FireRed interactive object state:** the Birth Island Deoxys triangle uses state-indexed palettes and coordinates plus progress variables, sound and field effects.
- **PMD Red status overlays:** `src/dungeon_pokemon_sprites.c` implements two status-symbol slots, active-status cycling and a status-to-graphics mapping; `src/dungeon_mon_sprite_render.c` supplies the active status mask.
- **Crystal:** distinctive battle primitives are directly present under `gfx/battle_anims/`, with engine/data tables under `engine/battle_anims/` and `data/battle_anims/`.
- **Ruby:** source families overlap Emerald strongly, supporting a delta-first pass.
- **Yellow:** Pikachu-specific presentation has dedicated data, engine and graphics trees; battle transitions/effects are also source-visible.

## Next mining order

1. Finish seed verification for Emerald/FireRed/PMD Red using the exact paths above.
2. Trace only referenced graphics/resources.
3. Sample Crystal distinctive primitives and choreography.
4. Compute Ruby-vs-Emerald deltas.
5. Run Yellow high-threshold specialized pass.
6. Only after seed verification, broaden into uncovered high-value subsystems.

The full machine-readable target list is in `VERIFICATION_TARGETS.json`.
