# GBA/GBC seed target map

This map narrows the first mining pass to exact source paths and symbols at the pinned donor revisions in `SOURCE_AVAILABILITY.json`. It is a pre-verification artifact, not an active opportunity ranking.

## Emerald — field-action choreography and field-effect primitives

Pinned repo: `79cbd8hmgj-wq/pokeemerald@a81cfacbe53bcc229fc4d93cb10b56a58e77a15f`

Primary code:
- `src/field_effect.c`
- `src/field_effect_helpers.c`
- `data/field_effect_scripts.s`
- `data/scripts/field_move_scripts.inc`

Exact high-value symbols in `src/field_effect.c`:
- `Task_FieldMoveShowMonOutdoors`
- `FieldMoveShowMonOutdoorsEffect_LoadGfx`
- `FieldMoveShowMonOutdoorsEffect_CreateBanner`
- `FieldMoveShowMonOutdoorsEffect_WaitForMon`
- `FieldMoveShowMonOutdoorsEffect_RestoreBg`
- `Task_FieldMoveShowMonIndoors`
- `FieldMoveShowMonIndoorsEffect_LoadGfx`
- `FieldMoveShowMonIndoorsEffect_SlideBannerOn`
- `FieldMoveShowMonIndoorsEffect_WaitForMon`
- `FieldMoveShowMonIndoorsEffect_RestoreBg`
- `InitFieldMoveMonSprite`
- `SpriteCB_FieldMoveMonSlideOnscreen`
- `SpriteCB_FieldMoveMonWaitAfterCry`
- `SpriteCB_FieldMoveMonSlideOffscreen`
- `Task_SurfFieldEffect`
- `SurfFieldEffect_FieldMovePose`
- `SurfFieldEffect_ShowMon`
- `SurfFieldEffect_JumpOnSurfBlob`
- `Task_FlyOut`
- `FlyOutFieldEffect_ShowMon`
- `FlyOutFieldEffect_BirdLeaveBall`
- `FlyOutFieldEffect_BirdSwoopDown`
- `FlyOutFieldEffect_JumpOnBird`
- `FlyOutFieldEffect_FlyOffWithBird`
- `Task_FlyIn`
- `FlyInFieldEffect_BirdSwoopDown`
- `FlyInFieldEffect_FlyInWithBird`
- `FlyInFieldEffect_JumpOffBird`
- `Task_UseWaterfall`
- `WaterfallFieldEffect_ShowMon`
- `WaterfallFieldEffect_RideUp`

`data/field_effect_scripts.s` directly enumerates field effects including:
- `FLDEFF_FIELD_MOVE_SHOW_MON`
- `FLDEFF_USE_SURF`
- `FLDEFF_USE_FLY`
- `FLDEFF_FLY_IN`
- `FLDEFF_USE_ROCK_SMASH`
- `FLDEFF_USE_STRENGTH`
- `FLDEFF_USE_WATERFALL`
- `FLDEFF_USE_DIVE`
- `FLDEFF_ASH_PUFF`
- `FLDEFF_ASH_LAUNCH`
- `FLDEFF_USE_TELEPORT`

First mining action: trace these state machines and only then enumerate the graphics/palettes they reference.

## FireRed — map previews

Pinned repo: `79cbd8hmgj-wq/pokefirered@037335f4c725d7c9aecdac87066f2002b4bd7e14`

Primary code:
- `src/map_preview_screen.c`

Primary assets:
- `graphics/map_preview/*/tiles.png`
- `graphics/map_preview/*/tilemap.bin`
- generated palette/4bpp resources referenced by `map_preview_screen.c`

Confirmed data structure:
- each `MapPreviewScreen` entry binds a map section, preview type, world-map visit flag, tiles, tilemap and palette
- `sHasVisitedMapBefore` tracks prior visitation state in the preview flow
- at least 20 named preview families are directly represented, including Viridian Forest, Rock Tunnel, Power Plant, Pokemon Mansion, Seafoam Islands, Mt. Ember and Victory Road

First mining action: characterize trigger/visited behavior and preview transition types. Do not spend time cataloging Kanto art beyond representative evidence.

## FireRed — timed Pokemon League lighting

Primary code:
- `src/field_specials.c`

Primary assets:
- `graphics/field_specials/elite_four_lighting_*.pal`
- `graphics/field_specials/champion_room_lighting_*.pal`

Exact symbol:
- `Task_RunPokemonLeagueLightingEffect`

Confirmed behavior:
- timer-indexed palette sequence
- Champion Room and Elite Four use separate timer/palette arrays
- each step loads BG palette slot 7
- global tint is applied after each load
- task is gated by field flags/palette-fade state

This is direct source confirmation of the prior `animated_palette_sequences` hypothesis.

## FireRed — interactive Deoxys triangle state machine

Primary code:
- `src/field_specials.c`

Exact symbols:
- `DoDeoxysTriangleInteraction`
- `Task_DoDeoxysTriangleInteraction`
- `MoveDeoxysObject`
- `Task_WaitDeoxysFieldEffect`
- `IncrementBirthIslandRockStepCount`
- `SetDeoxysTrianglePalette`

Primary assets:
- `graphics/field_specials/deoxys_rock_*.pal`
- `graphics/field_effects/pics/deoxys_rock_fragment_*.png`

Confirmed behavior combines:
- interaction-progress variable
- step-counter gate/reset
- palette change
- object movement to table-driven coordinates
- sound changes
- field effect `FLDEFF_MOVE_DEOXYS_ROCK`
- persistent object coordinates
- awakened completion flag

This directly supports treating the donor as a visual-state-machine technique/detail source rather than as a rock asset transplant.

## PMD Red — battler status overlays

Pinned repo: `79cbd8hmgj-wq/pmd-red@aefe6a46bcc5df13142225ef673a1ee2ac1b760b`

Primary code:
- `src/dungeon_mon_sprite_render.c`
- `src/dungeon_pokemon_sprites.c`

Exact call path:
- `UpdateMonsterSprite`
- `EntityGetStatusSprites`
- `UpdateDungeonPokemonSprite`
- `UpdateStatusSprite`
- `GetNextStatusSymbol`
- `StatusSymbolBitToIndex`
- `DrawStatusSprite`

Primary assets:
- `graphics/status/sleepless.4bpp`
- `graphics/status/burned.4bpp`
- `graphics/status/poisoned.4bpp`
- `graphics/status/frozen.4bpp`
- `graphics/status/confused.4bpp`
- `graphics/status/whiffer.4bpp`
- `graphics/status/taunted.4bpp`
- `graphics/status/lowhp.4bpp`
- `graphics/status/shield.4bpp`
- `graphics/status/statdown.4bpp`
- `graphics/status/sword.4bpp`
- `graphics/status/blinker.4bpp`
- `graphics/status/cross_eyed.4bpp`
- `graphics/status/eyedrops.4bpp`
- `graphics/status/muzzled.4bpp`
- `graphics/status/sleep.4bpp`

Confirmed behavior:
- status bits map into a compact status-graphics table
- badly poisoned and ordinary poison share art with different palette/index treatment
- multiple shield/state variants share primitives
- `GetNextStatusSymbol` and two status-sprite slots support rotating/cycling active conditions
- status sprites are positioned and drawn with the Pokemon sprite

This upgrades the old PMD Red status-overlay lead from vague memory to a tightly scoped source-verification target.

## Crystal — battle-animation primitives/choreography

Pinned repo: `79cbd8hmgj-wq/pokecrystal@3bc8daa4173e96a7f4011dad3922eb6fa5dad5c6`

Primary data/code:
- `data/battle_anims/framesets.asm`
- `data/battle_anims/oam.asm`
- `data/battle_anims/object_gfx.asm`
- `data/battle_anims/objects.asm`
- `engine/battle_anims/anim_commands.asm`
- `engine/battle_anims/bg_effects.asm`
- `engine/battle_anims/core.asm`
- `engine/battle_anims/functions.asm`
- `engine/battle_anims/helpers.asm`
- `macros/scripts/battle_anims.asm`

High-value graphics are already isolated under `gfx/battle_anims/`, including:
- `aeroblast.png`
- `angels.png`
- `globe.png`
- `noise.png`
- `reflect.png`
- `rope.png`
- `shapes.png`
- `shine.png`
- `wave.png`
- `web.png`

First mining action: map each distinctive primitive to its animation commands/frameset and classify component vs technique value. Do not evaluate engine transplantation.

## Ruby — Emerald delta pass only

Pinned repo: `79cbd8hmgj-wq/pokeruby@5784633ce4ef7ade1a7f2d2d0c288e3d5e6cdd7f`

Do not start with independent broad mining. First compare target paths against Emerald for:
- field effect scripts/state machines
- battle animation scripts
- weather/environment logic
- palette/tile animation

Only materially distinct Ruby behavior or assets proceed.

## Yellow — specialized/high-threshold pass

Pinned repo: `79cbd8hmgj-wq/pokeyellow@e89ead154b9968aa50eed9328ff2b38b6c194382`

Primary battle presentation paths:
- `engine/battle/animations.asm`
- `engine/battle/battle_transitions.asm`
- `engine/gfx/screen_effects.asm`
- `data/battle_anims/special_effects.asm`
- `data/battle_anims/subanimations.asm`

Pikachu-specific paths:
- `data/pikachu/pikachu_emotions.asm`
- `data/pikachu/pikachu_pic_animation.asm`
- `data/pikachu/pikachu_pic_objects.asm`
- `data/pikachu/pikachu_pic_tilemaps.asm`
- `engine/battle/pikachu_entrance_anim.asm`
- `engine/pikachu/pikachu_emotions.asm`
- `engine/pikachu/pikachu_follow.asm`
- `engine/pikachu/pikachu_movement.asm`
- `engine/pikachu/pikachu_pic_animation.asm`
- `engine/pikachu/pikachu_status.asm`
- `gfx/pikachu/*`

First mining action: retain only presentation/primitive ideas that are not already superseded by Emerald, Crystal or Platinum-native systems.

## What this preflight removes from the future agent workload

The next mining agent should not:
- rediscover donor repositories or revisions
- rediscover the canonical taxonomy
- search entire donor trees blindly
- re-derive the nine preserved seed hypotheses
- search PMD Red broadly for the status system
- search FireRed broadly for preview, lighting or Deoxys state logic
- search Emerald broadly for field-move choreography
- search Crystal broadly for the distinctive primitive library
- search Yellow broadly for Pikachu presentation files

The remaining work is verification depth, family enumeration, representative evidence, grouping and opportunity generation.
