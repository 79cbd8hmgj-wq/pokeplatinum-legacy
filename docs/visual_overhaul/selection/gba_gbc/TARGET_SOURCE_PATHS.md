# GBA/GBC targeted source-path map

This map narrows the next mining pass to verified code/data entry points. It is intentionally source-first: later agents should trace these systems to their referenced assets before considering broad extraction.

## Emerald — pinned `a81cfacbe53bcc229fc4d93cb10b56a58e77a15f`

### Field-action choreography
Primary source:
- `src/field_effect.c`
- `data/scripts/field_move_scripts.inc`
- `data/field_effect_scripts.s`

Verified function/state-machine anchors in `src/field_effect.c`:
- `Task_FieldMoveShowMonOutdoors`
- `FieldMoveShowMonOutdoorsEffect_Init`
- `FieldMoveShowMonOutdoorsEffect_LoadGfx`
- `FieldMoveShowMonOutdoorsEffect_CreateBanner`
- `FieldMoveShowMonOutdoorsEffect_WaitForMon`
- `FieldMoveShowMonOutdoorsEffect_ShrinkBanner`
- `FieldMoveShowMonOutdoorsEffect_RestoreBg`
- `Task_FieldMoveShowMonIndoors`
- `FieldMoveShowMonIndoorsEffect_LoadGfx`
- `FieldMoveShowMonIndoorsEffect_SlideBannerOn`
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
- `Task_FlyIn`
- `Task_UseWaterfall`
- `WaterfallFieldEffect_ShowMon`
- `WaterfallFieldEffect_RideUp`

`data/scripts/field_move_scripts.inc` directly connects gameplay scripts to `FLDEFF_USE_STRENGTH`, `FLDEFF_USE_WATERFALL`, and other field effects.

`data/field_effect_scripts.s` contains the central field-effect dispatch table and explicit entries for:
- field-move show-mon
- surf
- fly out/in
- rock smash
- strength
- waterfall
- dive
- teleport
- ash puff / ash launch
- bubbles / sparkle
- Deoxys rock move/destroy effects

### Environmental effect primitives
Primary source:
- `src/field_effect_helpers.c`
- `src/field_weather.c`
- `src/field_weather_effect.c`
- `data/field_effect_scripts.s`

Start by tracing effect object templates and sprite callbacks for dust, ash, splashes, flowing water, sparkles, bubbles, launch effects and rock-destruction fragments. Avoid cataloging every field sprite until those references are known.

### Battle-effect technique reference
Primary source:
- `data/battle_anim_scripts.s`
- `src/battle_anim_*.c`
- `src/battle_anim_effects_1.c`
- `src/battle_anim_effects_2.c`
- `src/battle_anim_effects_3.c`

Use primarily for sequencing/timing/component discovery, not engine transfer.

---

## FireRed — pinned `037335f4c725d7c9aecdac87066f2002b4bd7e14`

### Location/map preview system
Primary source:
- `src/map_preview_screen.c`

Verified asset family:
- `graphics/map_preview/<location>/tiles.png`
- `graphics/map_preview/<location>/tilemap.bin`

The repository contains dedicated preview families for locations including Viridian Forest, Rock Tunnel, Power Plant, Pokémon Mansion, Seafoam Islands, Victory Road, Mt. Ember, Cerulean Cave, Safari Zone and others.

Mining task:
1. trace the preview lookup table and map association;
2. identify palette source;
3. identify visited/first-entry gating;
4. identify transition/trigger path;
5. record dimensions and resource contract.

Do not treat Kanto artwork as a Platinum replacement asset. This remains a capability/layout donor.

### Timed Elite Four / Champion lighting
Verified asset family:
- `graphics/field_specials/elite_four_lighting_0.pal` ... `elite_four_lighting_11.pal`
- `graphics/field_specials/champion_room_lighting_0.pal` ... `champion_room_lighting_8.pal`

Primary code candidates:
- `src/field_special_scene.c`
- `src/field_specials.c`
- `src/palette.c`
- `src/palette_util.c`

Mining task:
- locate the palette-sequence tables/state machine;
- record per-step timing;
- identify destination palette slot/range;
- identify event start/stop conditions.

This is a technique donor, not a palette transplant.

### Interactive object state machine
Verified asset evidence:
- `graphics/field_specials/deoxys_rock_0.pal` ... `deoxys_rock_10.pal`
- Deoxys rock fragment graphics under `graphics/field_effects/pics/`

Primary code candidates:
- `src/field_special_scene.c`
- `src/field_specials.c`
- related Birth Island map scripts

Mining task:
trace position, palette, sound, field-effect and progression-state changes as one event-presentation system.

---

## PMD Red — pinned `aefe6a46bcc5df13142225ef673a1ee2ac1b760b`

### Status-overlay graphics
Verified asset directory:
- `graphics/status/`

Verified files include:
- `blinker.png`
- `burned.png`
- `confused.png`
- `cross_eyed.png`
- `eyedrops.png`
- `frozen.png`
- `lowhp.png`
- `muzzled.png`
- `poisoned.png`
- `shield.png`
- `sleep.png`
- `sleepless.png`
- `statdown.png`
- `sword.png`
- `taunted.png`
- `whiffer.png`

Primary render path:
- `src/dungeon_mon_sprite_render.c`

Verified anchors:
- `UpdateMonsterSprite`
- `EntityGetStatusSprites(entity)`
- `UpdateDungeonPokemonSprite(..., statusSprites, ...)`

This proves the status symbols are integrated into per-entity dungeon sprite rendering, not merely unused art.

Status logic support:
- `src/status_checks.c`
- `include/status_checks.h`
- `include/constants/status.h`

Next mining step:
trace `EntityGetStatusSprites` and `UpdateDungeonPokemonSprite` to establish:
- bit mapping from condition to symbol;
- simultaneous-status behavior;
- cycling/priority rules;
- draw position/offset;
- animation timing;
- palette/resource ownership.

### General effect-system entry points
Already present and worth targeted follow-up:
- `src/effect_main.c`
- `src/effect_data.c`
- `src/effect_anim_file.c`
- `src/effect_sbin.c`
- `src/effect_sub_1.c`
- `src/effect_sub_2.c`
- `dump_effect_sbin.py`

Do not mine the full effect corpus until status-overlay verification is complete.

---

## Crystal — pending exact-path pass

Scope is already constrained to battle-animation graphic primitives and choreography. Do not investigate engine transplantation.

## Ruby — pending delta pass

Do not broad-mine Ruby. Build a source/resource delta against the Emerald target paths above first.

## Yellow — pending exact-path pass

Use a high threshold. Limit initial search to battle transitions/effect timing and Pikachu-specific presentation resources.

## Handoff rule

Later agents should begin at the exact paths in this document, not with repository-wide exploration. Any newly discovered high-value path should be added here before broadening the mining scope.
