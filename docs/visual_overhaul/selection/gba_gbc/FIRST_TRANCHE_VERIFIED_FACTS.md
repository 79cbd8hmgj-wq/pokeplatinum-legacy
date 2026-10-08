# First-tranche verified source facts

This file records only source facts already verified at the pinned donor revisions. It is not an opportunity ranking.

## Emerald — field-action choreography

Pinned revision: `a81cfacbe53bcc229fc4d93cb10b56a58e77a15f`

`src/field_effect.c` exposes:
- separate indoor and outdoor Pokemon-show state machines;
- an outdoor window/banner setup with dedicated field-move streak graphics;
- dedicated Surf state flow;
- dedicated Fly-out and Fly-in state flows;
- dedicated Waterfall state flow;
- teleport and related travel effects.

Representative verified symbols:
- `Task_FieldMoveShowMonOutdoors`
- `FieldMoveShowMonOutdoorsEffect_LoadGfx`
- `Task_FieldMoveShowMonIndoors`
- `Task_SurfFieldEffect`
- `Task_FlyOut`
- `Task_FlyIn`
- `Task_UseWaterfall`

The Surf sequence explicitly locks controls, freezes object events, sets the surfing avatar state, performs a field-move pose, and advances through a task-state table.

The Fly-out sequence performs the player's field-move pose and then starts `FLDEFF_FIELD_MOVE_SHOW_MON_INIT` before the bird sequence.

The Waterfall sequence explicitly shows the selected Pokemon via `FLDEFF_FIELD_MOVE_SHOW_MON_INIT` before the ride-up sequence.

`data/field_effect_scripts.s` also confirms many compact field-effect families, including ash puff/launch, dust, splashes, bubbles, sparkle, sand pillar, Pokeball trail, teleport, and Rayquaza spotlight.

**Preflight conclusion:** both Emerald seeds survive source verification. Claude does not need to rediscover the field-action architecture.

## FireRed — map previews

Pinned revision: `037335f4c725d7c9aecdac87066f2002b4bd7e14`

`src/map_preview_screen.c` contains dedicated preview resources and a `sMapPreviewScreenData` table.

Verified record fields bind:
- map section;
- preview type;
- world-map/visited flag;
- tiles;
- tilemap;
- palette.

Dedicated preview art exists under `graphics/map_preview/` for many important locations.

**Preflight conclusion:** the map-preview capability is source-backed and should enter formal GBA/GBC opportunity classification without another repository search.

## FireRed — timed Pokemon League palette animation

`src/field_specials.c` contains:
- `sEliteFourLightingPalettes`;
- `sChampionRoomLightingPalettes`;
- timer arrays for both;
- `DoPokemonLeagueLightingEffect`;
- `Task_RunPokemonLeagueLightingEffect`;
- cancellation/final-state handling.

The runtime repeatedly loads the selected palette into **BG palette slot 7**, using explicit per-step timers, and reapplies the global field tint.

**Preflight conclusion:** this is a concrete timer-driven palette-animation technique, not merely an inferred art difference.

## FireRed — Deoxys triangle visual state machine

The same source file contains:
- `sDeoxysObjectPals`;
- `sDeoxysCoords`;
- `sDeoxysStepCaps`;
- persistent interaction variables;
- `DoDeoxysTriangleInteraction`;
- `MoveDeoxysObject`;
- sound playback;
- `FLDEFF_MOVE_DEOXYS_ROCK`;
- coordinate updates;
- awakened-state flag handling.

**Preflight conclusion:** the remembered "interactive object visual states" hypothesis is source-backed.

## PMD Red — battler status overlays

Pinned revision: `aefe6a46bcc5df13142225ef673a1ee2ac1b760b`

`graphics/status/` contains dedicated art for conditions including burn, poison, frozen, confusion, taunt, shields, sleep, stat-down and others.

`src/dungeon_pokemon_sprites.c` contains:
- `sStatusGfxInfo`;
- `sStatusGfx`;
- `sStatusSpritesInfo`;
- `GetNextStatusSymbol`;
- `UpdateStatusSprite`.

The status table maps several logical conditions onto shared graphics/palette variants. `GetNextStatusSymbol` iterates active status bits so multiple conditions can be represented over time.

`src/dungeon_mon_sprite_render.c` obtains the entity's status-sprite mask and passes it into the dungeon Pokemon sprite renderer.

**Preflight conclusion:** the PMD Red status-overlay seed survives source verification, including the previously remembered cycling behavior.

## Remaining bounded work

Crystal, Ruby and Yellow still require the checklist pass, but their exact source areas are already mapped in `DONOR_PATH_TARGETS.json`. No broad donor orientation is required.
