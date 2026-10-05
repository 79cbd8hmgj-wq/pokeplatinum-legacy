# Ranger Visual Bundle Classification

Package-level classification derived from the deep Ranger structural inventory.
No Platinum resources are modified or selected.

## Bundle profiles

| Profile | Packages |
|---|---:|
| cell_sprite_bundle | 1157 |
| opaque_narc_bundle | 606 |
| ranger_texture_payload | 441 |
| standalone_screen_map | 441 |
| animated_cell_sprite_bundle | 252 |
| tiled_background_bundle | 158 |
| graphics_palette_bundle | 2 |

## Categories

| Category | Profile | Packages |
|---|---|---:|
| _root | animated_cell_sprite_bundle | 4 |
| battle | cell_sprite_bundle | 65 |
| battle | animated_cell_sprite_bundle | 3 |
| effect | animated_cell_sprite_bundle | 200 |
| ending | tiled_background_bundle | 31 |
| ending | cell_sprite_bundle | 1 |
| event | tiled_background_bundle | 76 |
| eventicon | cell_sprite_bundle | 1 |
| field | opaque_narc_bundle | 446 |
| field | ranger_texture_payload | 441 |
| field | cell_sprite_bundle | 8 |
| field | animated_cell_sprite_bundle | 3 |
| interface | cell_sprite_bundle | 63 |
| interface | animated_cell_sprite_bundle | 7 |
| interface | graphics_palette_bundle | 1 |
| interface | tiled_background_bundle | 1 |
| menu | standalone_screen_map | 441 |
| menu | cell_sprite_bundle | 172 |
| menu | opaque_narc_bundle | 158 |
| menu | tiled_background_bundle | 37 |
| menu | graphics_palette_bundle | 1 |
| npc | cell_sprite_bundle | 155 |
| npc | animated_cell_sprite_bundle | 2 |
| opening | opaque_narc_bundle | 1 |
| player | cell_sprite_bundle | 6 |
| pokeOBJ | cell_sprite_bundle | 282 |
| system | opaque_narc_bundle | 1 |
| target | cell_sprite_bundle | 302 |
| target | animated_cell_sprite_bundle | 33 |
| targetOBJ | cell_sprite_bundle | 101 |
| title | tiled_background_bundle | 11 |
| title | cell_sprite_bundle | 1 |
| uppict | tiled_background_bundle | 2 |

## Notes

- animated_cell_sprite_bundle: NCGR + NCLR + NCER + NANR present.
- cell_sprite_bundle: NCGR + NCLR + NCER present.
- tiled_background_bundle: NCGR + NCLR + NSCR present.
- graphics_palette_bundle: NCGR + NCLR present without a complete cell/tilemap contract.
- ranger_texture_payload: decompressed payload begins with TEX\0 and source naming identifies a texture payload.
- opaque_narc_bundle: NARC members exist but the package lacks a recognized complete standard visual bundle.
- Classification is structural, not a usability decision.
