# GBA/GBC exact mining target map

This file converts the prior deferred findings into concrete source anchors so the mining agent does not spend context rediscovering where to look.

## Emerald

**Field-action choreography** is source-backed at the pinned revision. `src/field_effect.c` explicitly declares task chains for outdoor and indoor Pokémon field-move presentation, Surf, Fly out/in, Waterfall, fall/landing, camera shake, teleport, and related transitions. `data/scripts/field_move_scripts.inc` provides the event/script entry points for Cut, Rock Smash, Strength, Waterfall and other moves.

High-value graphics are already named under `graphics/field_effects/pics/`: field-move streaks, ash puffs/launch, ground-impact dust, bird, Poké Ball glow, ripple, splash, sparkle, sand pillar and water-surfacing frames. This means Emerald should be mined **system first, referenced graphics second**, not as a blind graphics dump.

## FireRed

Three earlier hypotheses are now tied to exact source:

- **Location previews:** `src/map_preview_screen.c` contains `sMapPreviewScreenData`, binding map section, preview type, visited/world-map flag, tiles, tilemap and palette. The graphics live under `graphics/map_preview/`.
- **Timed environmental palette animation:** `src/field_specials.c` contains `DoPokemonLeagueLightingEffect`, `Task_RunPokemonLeagueLightingEffect`, `sEliteFourLightingTimers` and `sChampionRoomLightingTimers`. The task cycles dedicated palettes into BG palette slot 7 with per-step timers.
- **Interactive object states:** `DoDeoxysTriangleInteraction` / `MoveDeoxysObject` plus `data/maps/BirthIsland_Exterior/scripts.inc` combine progress variables, position changes, palette changes, sound, field effects and step-count gating.

These are no longer vague prior-session leads; Claude can begin from the exact functions.

## PMD Red

The status-overlay lead has a concrete render-path anchor.

`src/dungeon_mon_sprite_render.c::UpdateMonsterSprite` calls:

- `EntityGetStatusSprites(entity)`
- `UpdateDungeonPokemonSprite(..., statusSprites, ...)`

This proves status visualization is encoded directly in the monster-render path. The next mining action is narrow: trace those two functions into `src/dungeon_pokemon_sprites.c` and identify the exact status-symbol assets/mapping before looking at the much larger effect archive.

The general effect family is visible under `src/data/effects/` and the `effect_*.c` / `move_orb_effects_*.c` modules, but broad effect mining should wait until the status family is closed.

## Crystal

The prior primitive list is directly supported by `data/battle_anims/object_gfx.asm` and `gfx/battle_anims/`. Explicit families include Web, Rope, Angels, Globe, Noise, Reflect, Shapes, Shine, Wave and Aeroblast.

`engine/battle_anims/anim_commands.asm` shows a per-frame script interpreter updating BG effects, OAM and palettes. That supports Crystal as a **component/choreography donor**, not an engine-backport target.

## Ruby

Ruby exposes the same broad readable script families as Emerald:

- `data/battle_anim_scripts.s`
- `data/field_effect_scripts.s`
- `data/field_move_scripts.inc`

Therefore Ruby starts with a deterministic **delta against Emerald**. Only materially distinct sequences/resources proceed to opportunity mining.

## Yellow

`data/pikachu/pikachu_pic_animation.asm` contains a large dedicated Pikachu presentation system with explicit durations, multiple graphics loads, background animations, cries, and palette cycling (`PikaPicAnimThunderboltPals`).

`engine/battle/battle_transitions.asm` contains context-selected transitions based on trainer/wild battle, enemy level and dungeon context. This is a selective technique/reference source only; later donors remain preferred when they already cover the same presentation concept better.

## Execution rule

For each donor:

1. open the exact source anchors above;
2. trace referenced graphics/tables/functions;
3. inventory only the family actually used by that system;
4. generate representative evidence;
5. classify with the existing eight-class taxonomy;
6. broaden only when a verified family shows enough payoff.

This path-first strategy is specifically intended to reduce agent context use and avoid large exploratory scans.
