# G3 Character and Pokemon Graphics Implementation Spec

Status: implementation-ready audit/spec
Primary target: Pokemon Platinum visual overhaul
Primary donor/reference: pret/pokeheartgold at commit 9d8b7591f09b65804da2fb2dfd56f320633e0d36

## Scope

G3 covers:
- player sprites
- NPC sprites
- trainer sprites
- Pokemon party/box icons
- Pokemon battle sprites/animation where a donor change is visually worthwhile

This pass follows the completed G2C global UI foundation. G3 must preserve gameplay data and sprite/resource contracts unless a change is explicitly isolated and validated.

## G3A — Pokemon icon donor path

### Platinum source layout

Platinum exposes:
- `res/pokemon/<species>/icon.png`
- form-specific `icon.png` files
- `res/pokemon/.shared/pl_poke_icon.pal`
- shared NCER/NANR data
- `res/pokemon/species_icons.order`
- per-species/form palette selection through `.icon_palette` in species data
- runtime lookup through `src/pokemon_icon.c`

The archive is rebuilt by `res/pokemon/meson.build`; no binary NARC patching is required.

### HGSS donor layout

HGSS exposes:
- `files/poketool/icongra/poke_icon/poke_icon_XXXXXXXX.png`
- `poke_icon_00000000.pal`
- shared cell/animation JSON resources
- icon archive generation through `poke_icon.mk`

Normal species use the same base archive convention:

`HGSS icon file index = National Dex species ID + 7`

Confirmed examples:
- Bulbasaur #001 -> file 8
- Charizard #006 -> file 13
- Pikachu #025 -> file 32
- Turtwig #387 -> file 394
- Chimchar #390 -> file 397
- Piplup #393 -> file 400
- Starly #396 -> file 403
- Lucario #448 -> file 455

### Geometry compatibility

Representative Platinum and HGSS icons are both:
- 32 x 64 pixels
- indexed PNG
- 4-bit color
- 16 palette entries
- two-frame source art compatible with the existing icon NCER/NANR model

Therefore icon geometry is directly compatible.

### Palette compatibility

The shared icon palette is NOT byte/color compatible.

Platinum:
`res/pokemon/.shared/pl_poke_icon.pal`

HGSS:
`files/poketool/icongra/poke_icon/poke_icon_00000000.pal`

Both provide three populated 16-color banks, but their RGB ramps differ.

Representative species palette-bank mappings were checked and match between the games:
- Bulbasaur: bank 1
- Pikachu: bank 2
- Turtwig: bank 1
- Lucario: bank 2
- Rotom: bank 0

Do not generalize this sample to every form until the complete table is checked.

### Required import strategy

Raw HGSS PNG replacement while retaining the Platinum shared palette is prohibited.

Likewise, replacing only the shared palette while retaining Platinum icon PNGs is prohibited.

Approved implementations are:

#### Strategy A — Atomic HGSS icon subsystem port

Port as one unit:
1. all base-species icon PNGs
2. all supported form icon PNGs
3. HGSS shared three-bank icon palette
4. species/form palette-bank mapping after a complete table comparison
5. retain Platinum's archive order/API only if the resulting mapping is proven equivalent

This is the preferred route if the HGSS mapping table is fully compatible.

#### Strategy B — Per-icon palette remap

For each HGSS donor icon:
1. determine its HGSS palette bank
2. decode indexed pixels against the HGSS bank
3. map each used donor color to the nearest/approved color in the equivalent Platinum bank
4. write a Platinum-palette-compatible indexed PNG
5. leave Platinum shared palette and runtime palette mapping untouched

This has lower global risk but requires more transformation work.

## G3A pilot gate

Before a National Dex-wide import, build a runtime pilot containing:
- Turtwig
- Chimchar
- Piplup
- Starly
- Pikachu
- Lucario

Pilot acceptance:
- correct colors in party menu
- correct colors in Pokemon summary
- correct colors in PC/box UI
- both icon animation frames intact
- no palette bleed between adjacent icons
- eggs and forms unchanged
- ROM builds for both supported revisions
- visual-asset export passes

Do not expand to all species until the pilot is inspected in Delta.

## G3B — Player/NPC/trainer sprites

Rules:
- preserve Platinum character identity; HGSS protagonist/NPC art is reference, not a blind replacement source
- prefer palette/line-cleanup and animation refinement over replacing Sinnoh-specific designs
- use HGSS donor art only where the character/object is genuinely shared and silhouette/animation contracts align
- preserve sprite dimensions, frame packing, palette count, and field animation sequences unless a dedicated runtime test accompanies the change

Priority:
1. player field sprites
2. common overworld NPC classes
3. major trainers
4. battle trainer portraits
5. one-off NPCs

## G3C — Pokemon battle sprites

Platinum's battle sprites already carry game-specific animation metadata. Any donor art change must preserve:
- gender differences
- front/back orientation
- frame count/layout
- y offsets
- shadow offsets/sizes
- cry/start delays
- form routing

HGSS battle sprites should therefore be treated as a selective donor/reference class rather than a bulk blind import.

## Validation

Every G3 batch requires:
- source-format validation
- archive export validation
- both supported ROM builds
- runtime inspection in Delta

Compile success alone is not sufficient for palette, sprite alignment, animation timing, or readability.
