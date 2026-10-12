# B1 installed donor battle resources

Resources here are **installed in the ROM build** through `res/graphics/battle/moves` (NCGR/NCLR/NCER/NANR
NARCs, appended to the end of the `.order` files so existing NAIX indices are unchanged) and drawn by the
existing `SPRITE_FUNC_OFFSET_AND_ANIMATE` battle-script function. No new C code, no battle mechanics changes.

Pipeline: `export_b1_ranger_effect_cells.py` (donor Nitro cells -> PNG) ->
`build_b1_donor_battle_sprite.py <recipe>` (4bpp cell-scan PNG + cell/anim JSON) ->
`install_b1_donor_battle_sprite.py` (register in NARC orders + meson) -> `nitrogfx` in the normal build.
Recipes: `tools/visual_overhaul/b1_recipes/`. Per-sprite provenance (donor package, per-cell sha256, palette): `*.provenance.json`.
Validator: `tools/visual_overhaul/validate_b1_installed_donor_sprites.py`.

| Sprite | Donor (Ranger 2) | Frames / OBJ tiles / colours | Used by (defender-anchored impact) |
|---|---|---|---|
| `ranger_fire_bloom` | `effect/e010` fireball + flame-crown cells | 8 / 236 / 7 | Flamethrower, Ember, Fire Blast, Flame Wheel |
| `ranger_ice_bloom` | `effect/e009` (same cells, cyan palette) | 8 / 236 / 7 | Ice Beam, Aurora Beam |
| `ranger_rock_burst` | `effect/e002` rock shatter cells | 9 / 219 / 6 | Stone Edge, Rock Blast (both branches), Ancient Power (both branches) |

Budget rule: <= 256 OBJ tiles (8 KiB) and <= 15 opaque colours per sprite; each script owns sprite manager 0
for the duration of the sprite and frees it before unloading its particle system.

Not verified here (owner runtime QA): on-screen placement offsets, palette/OAM collision with healthboxes in
doubles, and visual timing against each move's particle emitters.
