# GBA/GBC source target map

This file records exact donor paths already located during preflight so later mining agents do not spend context rediscovering them.

## Emerald — field choreography and environmental effects

Pinned donor: `79cbd8hmgj-wq/pokeemerald@a81cfacbe53bcc229fc4d93cb10b56a58e77a15f`

High-value source targets:

- `src/field_effect.c`
  - field-move presentation state machines
  - `Task_FieldMoveShowMonOutdoors`
  - `FieldMoveShowMonOutdoorsEffect_*`
  - `Task_FieldMoveShowMonIndoors`
  - `FieldMoveShowMonIndoorsEffect_*`
  - `Task_SurfFieldEffect` / `SurfFieldEffect_*`
  - `Task_FlyOut` / `FlyOutFieldEffect_*`
  - `Task_FlyIn` / `FlyInFieldEffect_*`
  - `Task_UseWaterfall` / `WaterfallFieldEffect_*`
  - teleport field-effect state machine
- `data/scripts/field_move_scripts.inc`
  - script-level use of `FLDEFF_USE_STRENGTH`, `FLDEFF_USE_WATERFALL`, Dive and related field effects
- `data/field_effect_scripts.s`
  - effect dispatch table
  - Surf, Fly, Strength, Waterfall, Dive
  - ash puff/launch, bubbles, sparkle, Deoxys rock effects, teleport and other reusable primitives
- `src/field_effect_helpers.c`
  - grass/water/ash/surf support effects and field-effect sprite helpers
- `src/field_weather.c`, `src/field_weather_effect.c`
  - weather/environmental technique follow-up
- `data/battle_anim_scripts.s`, `src/battle_anim_*.c`
  - battle-effect sequencing follow-up only after field pass

Preflight conclusion: the prior field-action hypothesis is strongly source-addressable; bulk graphics inspection should follow these functions rather than precede them.

## FireRed — location previews, palette animation, interactive object states

Pinned donor: `79cbd8hmgj-wq/pokefirered@037335f4c725d7c9aecdac87066f2002b4bd7e14`

### Location previews

Primary code:
- `src/map_preview_screen.c`

Primary graphics:
- `graphics/map_preview/*/tiles.png`
- `graphics/map_preview/*/tilemap.bin`

Verified structure in `sMapPreviewScreenData`:
- map section
- preview type
- world-map/visited flag
- tiles
- tilemap
- palette

Examples include Viridian Forest, Mt. Moon, Rock Tunnel, Power Plant, Pokémon Mansion, Seafoam Islands, Victory Road, Mt. Ember and others.

This directly verifies that the preview-card seed has a source-backed association between location identity, visited-state flag and dedicated visual resources.

### Timed Pokémon League palette animation

Primary code:
- `src/field_specials.c`

Primary assets:
- `graphics/field_specials/elite_four_lighting_*.pal`
- `graphics/field_specials/champion_room_lighting_*.pal`

Verified code/data:
- `sEliteFourLightingPalettes`
- `sChampionRoomLightingPalettes`
- `sEliteFourLightingTimers`
- `sChampionRoomLightingTimers`
- `DoPokemonLeagueLightingEffect`
- `Task_RunPokemonLeagueLightingEffect`

The task cycles one BG palette slot on per-step timers and reapplies global tint. This is a concrete technique donor, not merely an art reference.

### Deoxys interactive-object visual state machine

Primary code:
- `src/field_specials.c`

Primary assets:
- `graphics/field_specials/deoxys_rock_*.pal`
- Deoxys rock field-effect fragments under `graphics/field_effects/pics/`

Verified code/data:
- `sDeoxysObjectPals`
- `sDeoxysCoords`
- `sDeoxysStepCaps`
- `DoDeoxysTriangleInteraction`
- `Task_DoDeoxysTriangleInteraction`
- `MoveDeoxysObject`
- `Task_WaitDeoxysFieldEffect`
- `SetDeoxysTrianglePalette`

The interaction combines progress state, palette changes, object relocation, sound and a field effect.

## PMD Red — status overlays

Pinned donor: `79cbd8hmgj-wq/pmd-red@aefe6a46bcc5df13142225ef673a1ee2ac1b760b`

Primary code:
- `src/dungeon_mon_sprite_render.c`
- `src/dungeon_pokemon_sprites.c`
- `src/status_checks.c`

Primary graphics:
- `graphics/status/*.4bpp`

Verified structure:
- `UpdateMonsterSprite` obtains `EntityGetStatusSprites(entity)` and passes status sprite data into dungeon Pokémon sprite rendering.
- `DungeonPokemonSprite` reserves two status-sprite slots/offsets.
- `sStatusGfxInfo` defines dimensions, frame/tile offsets and related graphics metadata.
- `sStatusSpritesInfo` maps status-symbol IDs to graphics/frame variants.
- Dedicated graphics exist for sleepless, burned, poisoned, frozen, confused, whiffer, taunted, low HP, shield, stat-down, sword, blinker, cross-eyed, eyedrops, muzzled and sleep.
- Distinct mappings include badly poisoned, cursed, Focus Energy, sure-shot and multiple shield states.

Preflight conclusion: the prior PMD Red status-overlay finding is directly supported by source and graphics and should be one of the first formal GBA/GBC verifications.

## Crystal — battle animation primitives and choreography

Pinned donor: `79cbd8hmgj-wq/pokecrystal@3bc8daa4173e96a7f4011dad3922eb6fa5dad5c6`

Primary animation data/code:
- `data/moves/animations.asm`
- `data/battle_anims/framesets.asm`
- `data/battle_anims/oam.asm`
- `data/battle_anims/object_gfx.asm`
- `data/battle_anims/objects.asm`
- `engine/battle_anims/anim_commands.asm`
- `engine/battle_anims/bg_effects.asm`
- `engine/battle_anims/core.asm`
- `engine/battle_anims/functions.asm`
- `engine/battle_anims/helpers.asm`
- `docs/battle_anim_commands.md`

Confirmed primitive graphics include:
- `gfx/battle_anims/aeroblast.png`
- `angels.png`
- `globe.png`
- `noise.png`
- `reflect.png`
- `rope.png`
- `shapes.png`
- `shine.png`
- `wave.png`
- `web.png`

This matches the prior hypothesis closely. The next pass should bind specific move scripts/framesets to those primitives; no engine-backport investigation is needed.

## Yellow — specialized presentation pass

Pinned donor: `79cbd8hmgj-wq/pokeyellow@e89ead154b9968aa50eed9328ff2b38b6c194382`

High-threshold source targets already located:

Battle presentation:
- `engine/battle/animations.asm`
- `engine/battle/battle_transitions.asm`
- `engine/gfx/screen_effects.asm`
- `data/battle_anims/special_effects.asm`
- `data/battle_anims/subanimations.asm`
- `data/battle_anims/frame_blocks.asm`

Pikachu-specific:
- `engine/battle/pikachu_entrance_anim.asm`
- `engine/pikachu/pikachu_emotions.asm`
- `engine/pikachu/pikachu_pic_animation.asm`
- `data/pikachu/pikachu_emotions.asm`
- `data/pikachu/pikachu_pic_animation.asm`
- `data/pikachu/pikachu_pic_objects.asm`
- `data/pikachu/pikachu_pic_tilemaps.asm`
- `gfx/pikachu/*`
- `gfx/sprites/surfing_pikachu.png`

Do not broaden beyond these targets unless they reveal a genuinely distinctive opportunity.

## Ruby — delta-first control

Pinned donor: `79cbd8hmgj-wq/pokeruby@5784633ce4ef7ade1a7f2d2d0c288e3d5e6cdd7f`

The Ruby and Emerald repositories use materially different path layouts, so raw path-set subtraction is not a reliable semantic delta. Do not treat path differences as unique visual findings.

Target only subsystem-level deltas against Emerald:
- field effects
- field-move presentation
- weather
- battle animation scripts
- animated tiles
- unused/debug graphics

Semantic comparison must happen after the Emerald source/system pass establishes the baseline.

## Context rule

Later agents should begin from this file and the seed ledger. Do not rescan donor trees merely to rediscover these paths.
