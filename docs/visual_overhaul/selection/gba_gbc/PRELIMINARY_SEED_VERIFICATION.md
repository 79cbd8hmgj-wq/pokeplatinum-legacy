# Preliminary GBA/GBC seed verification

This checkpoint records only facts already confirmed against the pinned donor revisions. It does **not** activate the deferred findings or change the DS ranking.

## Confirmed now

### Emerald field-action choreography

The Emerald source directly exposes separate state-machine functions for:

- field-move Pokémon presentation outdoors
- field-move Pokémon presentation indoors
- Surf
- Fly out
- Fly in
- Waterfall
- Teleport

The field-effect table also explicitly registers Surf, Fly, Fly-in, Strength and Waterfall field effects. This upgrades the old "prior-session" lead from vague memory to a concrete source target. The next pass should recover state order, referenced graphics and exact timing rather than rediscovering file locations.

### Emerald environmental effect families

The same source exposes camera shake, ash-puff/launch, teleport spin, fall/landing and Deoxys-rock field-effect families. These are now concrete candidates for splitting into technique versus component findings.

### FireRed map previews

`src/map_preview_screen.c` exists and directly embeds per-location palette, tiles and tilemap resources under `graphics/map_preview/`. It also tracks whether the map has been visited. This strongly supports the existing location-preview hypothesis; the remaining work is the trigger/lookup/gating trace and complete family count.

### FireRed Pokémon League palette lighting

`src/field_specials.c` contains explicit Pokémon League lighting tasks and an `sEliteFourLightingPalettes` table, backed by dedicated Elite Four and Champion palette files. The remaining work is to recover timer progression and palette-slot writes.

### FireRed Deoxys object-state presentation

`src/field_specials.c` contains dedicated Deoxys triangle interaction/object-movement tasks, with a family of Deoxys-rock palettes and fragment graphics. The prior interactive-object-state idea now has concrete source and asset anchors.

### PMD Red status art

A dedicated `graphics/status/` family exists with burned, confused, frozen, poisoned, shield, sleep, stat-down, taunted and other symbols. The remaining blocker is not asset existence; it is locating the exact dungeon render/cycling path.

### Crystal battle-animation primitives

The previously remembered primitive family is present at the pinned revision: Aeroblast, angels, globe, noise, reflect, rope, shapes, shine, wave, web and related graphics. Crystal's battle-animation command/data paths are also present. This supports keeping Crystal as a component/choreography donor rather than an engine donor.

## Still intentionally unresolved

- PMD Red status-symbol positioning/cycling logic
- exact FireRed preview lookup/gating behavior
- exact FireRed palette-cycle timing
- per-move mapping of Crystal primitives
- Yellow's genuinely useful visual Pikachu-only material
- Ruby-only deltas versus Emerald
- any LeafGreen-only material

These are now narrow verification tasks, not broad donor-discovery tasks.
