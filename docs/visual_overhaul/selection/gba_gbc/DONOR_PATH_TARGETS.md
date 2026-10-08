# GBA/GBC donor path target map

This file is the human-readable companion to `DONOR_PATH_TARGETS.json`.

The preflight pass has now narrowed the first mining run to exact source areas rather than broad donor repositories.

## Emerald
Field-action choreography is concentrated in `src/field_effect.c`, `data/scripts/field_move_scripts.inc`, and `data/field_effect_scripts.s`. The source explicitly exposes separate indoor/outdoor field-move presentation, Pokémon display/cry staging, and dedicated Surf/Fly/Waterfall task sequences.

Environmental effect primitives should be traced from the field-effect registry into `src/field_effect_helpers.c` and related handlers. The registry already identifies ash puffs/launch, dust, splashes, sparkle, Poké Ball trails, teleport, and similar families.

## FireRed
The location-preview hypothesis is now source-backed at `src/map_preview_screen.c`. Preview records bind map section + visited flag + tiles + tilemap + palette.

The timed environmental-lighting hypothesis is source-backed at `src/field_specials.c`: Elite Four and Champion rooms use palette arrays plus timer arrays, repeatedly loading BG palette slot 7.

The interactive-object hypothesis is narrowed to the Deoxys triangle state machine in the same file, with explicit palette states, coordinates, step caps, movement, and task sequencing.

## PMD Red
The status-overlay hypothesis is source-backed at `src/dungeon_pokemon_sprites.c`, `src/dungeon_mon_sprite_render.c`, and `graphics/status/`. The implementation has dedicated status artwork, mappings for many condition types, entity-derived status sprite masks, and support for multiple status sprite slots/cycling.

## Crystal
The previously remembered unusual primitive families are present directly under `gfx/battle_anims/`, including web, rope, angels, globe, noise, reflect, shine, shapes, wave, and Aeroblast artwork. Choreography lives under `engine/battle_anims/` and should be mined as technique only.

## Yellow
Pikachu-specific presentation is concentrated in `data/pikachu/`, `engine/pikachu/`, `engine/battle/pikachu_entrance_anim.asm`, and `gfx/pikachu/`. Generic battle animation/transition material remains high-threshold.

## Ruby
Ruby remains delta-only against Emerald. Compare corresponding source/resource families first; do not perform a second full Gen III mining pass.

## Next pre-Claude setup
The remaining useful setup work is to turn these exact paths into a small verification checklist per seed: exact functions/tables to inspect, evidence fields to record, and a deterministic accept/reject rule. After that, Claude can start by resolving a bounded seed queue instead of rediscovering donor structure.
