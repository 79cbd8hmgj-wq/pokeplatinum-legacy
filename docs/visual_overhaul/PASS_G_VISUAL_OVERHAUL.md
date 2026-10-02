# Pass G — Visual Overhaul

## Goal

Build the most visually advanced Pokemon experience the Platinum Nintendo DS base can realistically support while preserving clear Pokemon visual language.

The project does **not** preserve Platinum's retail visual identity as a constraint. Platinum is the engine/content base; the target is maximum visual improvement within the emulated DS hardware behavior used by Delta.

## Runtime target

- Primary runtime: Delta Nintendo DS emulation.
- Design to DS hardware behavior/limits as enforced by the emulator.
- No separate emulator-specific cosmetic track.
- Visual changes must remain ROM-side and must not depend on external texture packs, shaders, skins, or post-processing.

## Donor/reference pool

### Pokemon HeartGold/SoulSilver
Primary technical donor because it is the closest later Gen IV code/resource base.

Use for:
- field graphics and props
- buildings/models/textures
- Pokemon/icon resources
- UI
- late-Gen-IV rendering behavior
- engine feature backports where the payoff is high

### Pokemon Mystery Dungeon: Explorers of Sky
Secondary presentation/effects donor.

Confirmed useful systems/resources:
- dedicated `EFFECT/` resource family
- `effect.bin`
- `.wan` animated sprite assets
- layered map/background formats (`.bma`, `.bpc`, `.bpl`, `.bpa`)
- `.wte` UI/background assets
- explicit graphics conversion rules for Nitro NCGR/NCLR resources
- source modules for dungeon camera, dungeon effects, and weather

Use primarily for:
- particles
- weather
- animated overlays
- transitions
- screen-space effects
- UI presentation
- environmental animation ideas

### Pokemon Mystery Dungeon: Red Rescue Team
Art/presentation reference only. It is a GBA title and should not define Platinum's DS technical ceiling.

Use for:
- sprite/palette ideas
- UI motifs
- effect design
- background art reference


### Additional Pokemon decomps in donor pool

The user also has decomps/forks for:
- Pokemon Stadium
- Pokemon Stadium 2
- Pokemon Diamond
- Pokemon Yellow
- Pokemon FireRed
- Pokemon Crystal
- Pokemon Ruby

These must be considered before finalizing any visual subsystem. They are not assumed to be equally portable.

#### Technical priority by platform/generation
- **Diamond**: extremely high-value control/reference source because it shares the Gen IV DS engine lineage with Platinum. Use to identify alternate or unused field assets, rendering behavior, UI resources, battle presentation, effects, and content that Platinum changed or removed.
- **FireRed / Ruby**: strong 2D donor/reference sources for sprites, tiles, palettes, UI motifs, battle effects, and readability. Use primarily for art direction and convertible 2D assets rather than DS engine code.
- **Crystal / Yellow**: historical/reference sources for iconic Pokemon visual language, palette identity, tiles, UI motifs, and simplified effects. Use selectively where clarity or style is stronger than later assets.
- **Pokemon Stadium / Stadium 2**: high-value visual reference sources for 3D Pokemon presentation, battle staging, camera language, animation timing, effects, stadium/battle environments, lighting direction, and model-material ideas. N64 code/assets are not assumed to be directly portable to DS; treat them primarily as reference/technique donors unless a specific asset conversion proves practical.

#### Rule
For each visual subsystem, compare all relevant donor/reference games before choosing a direction. Prefer the strongest result that can be implemented efficiently on Platinum's DS base rather than favoring a game merely because it is newer.


## Cross-game visual subsystem matrix

This matrix is the default source-selection order for Pass G. It is a working implementation guide, not a requirement to copy a donor wholesale.

| Subsystem | Primary source | Secondary source(s) | Intended use |
|---|---|---|---|
| Field lighting | Platinum | HGSS, Stadium 1/2 reference | Modify Platinum's native area-light system; use other games for color/lighting direction |
| Field weather | Platinum | HGSS, PMD Sky | Prefer native Platinum weather; study HGSS/PMD behavior for richer layering and timing |
| Environmental particles/overlays | Platinum + PMD Sky | HGSS, Ruby | Rebuild effects through Platinum field-effect/particle systems; PMD is the main presentation reference |
| Field camera | Platinum | Diamond, HGSS, Stadium reference | Preserve Platinum compatibility; borrow camera behaviors only where visually meaningful |
| Map props/3D environment | HGSS | Platinum, Diamond | HGSS is the first donor for compatible late-Gen-IV models/textures; convert selectively |
| Environment textures | HGSS | Diamond, Ruby | Prefer DS-native compatible art; Ruby is useful for color/pattern inspiration rather than direct 3D texture replacement |
| Animated environmental props | Platinum/HGSS | Diamond, PMD Sky | Use native map-prop animation where possible; PMD contributes animation concepts |
| Player/NPC field sprites | HGSS | Platinum, Diamond | Compare dimensions/palette/resource assumptions and use the strongest compatible rendition |
| Pokemon icons | HGSS | Platinum, Diamond | High-priority direct/convertible asset class |
| Pokemon battle sprites | Platinum/HGSS | Diamond, Ruby/Yellow reference | Favor Gen-IV-compatible assets; older games only where they provide superior pose/readability ideas |
| Trainer sprites | HGSS/Platinum | Diamond, Ruby | Direct/convertible DS assets first; Ruby as 2D reference |
| UI frames/panels | Platinum | HGSS, PMD Sky, Ruby/Yellow | Rebuild within Platinum UI resource formats using strongest Pokemon-style visual language |
| UI animation/transitions | Platinum | PMD Sky, HGSS, Yellow | PMD is the strongest presentation reference; implement through Platinum-native systems |
| Battle backgrounds | Platinum | Stadium 1/2, HGSS, Diamond | Stadium games define staging/composition ideas; final assets must be rebuilt for DS constraints |
| Battle camera/staging | Platinum | Stadium 1/2, Diamond | Stadium is the primary visual reference; implementation remains Platinum-native |
| Battle move effects | Platinum | PMD Sky, Stadium 1/2, Ruby/Yellow | Use Platinum's script/particle system; mine other games for effect design, timing and impact |
| Pokemon battle animation | Platinum | Stadium 1/2, Diamond | Stadium supplies animation/camera language, not direct N64 animation transplantation |
| Palette/color identity | Platinum/HGSS | Ruby, Yellow, PMD | Use older games selectively when their color separation/readability is stronger |
| Special-area presentation | Platinum | PMD Sky, Stadium 1/2, HGSS | Distortion World, Galactic areas and legendary scenes can combine native 3D with layered effects |
| Technical DS ceiling/control | Platinum | HGSS, Diamond | These three determine what is realistically portable without unnecessary engine replacement |

### Donor classification rules

Every candidate resource or technique must be labeled as one of:

1. **Direct** — usable with little or no structural conversion.
2. **Convertible** — useful asset/data, but requires format/palette/dimension/remapping work.
3. **Technique** — implementation concept worth reproducing in Platinum code.
4. **Reference** — visual/art-direction reference only.
5. **Reject** — cost, incompatibility, or visual mismatch exceeds the payoff.

### Current repo-specific findings

#### Diamond
Confirmed useful material includes:
- camera source
- RTC/weather field code
- palette code
- graphics loaders
- NNS G2D/G3D routines
- extensive field-model animation resources in NSBTA/NSBCA/NSBTP formats

**Classification:** high-value technical control/reference; some assets may be directly compatible or cheaply convertible.

#### Ruby
Confirmed useful material includes:
- editable tilesets and metatiles
- explicit palette files
- animated tiles
- battle animation scripts
- field-effect scripts
- Pokemon/trainer graphics
- map/layout resources

**Classification:** strong 2D art/effect donor and reference source; weak direct DS-engine donor.

#### Yellow
Confirmed useful material includes:
- battle animation data
- battle transitions
- screen effects
- sprite animation systems
- battle HUD graphics
- tilesets
- emotes
- Pikachu-specific animation resources

**Classification:** selective style/readability/effect reference.

#### Stadium 1 / Stadium 2
Confirmed Stadium material includes graphics/animation tooling and battle/presentation resources; Stadium 2 remains primarily an N64 presentation reference.

Best targets:
- battle framing
- camera motion
- Pokemon animation timing
- move-impact staging
- arena composition
- lighting/material direction

**Classification:** high-value presentation/animation reference; low direct portability to DS.

## Implementation-selection rule

Before modifying a visual subsystem, inspect the primary source named above and only inspect secondary sources when they can plausibly improve that subsystem. This prevents donor research from becoming open-ended while still using the full available resource pool.


## Confirmed Platinum visual systems

The current decomp exposes substantially more than simple asset replacement.

### Field lighting
`res/field/lighting/` contains four editable lighting sets.

Each lighting template exposes:
- up to four lights
- per-light enable state
- RGB color
- XYZ direction
- diffuse color
- ambient color
- specular color
- emission color
- time boundaries

`src/overlay005/area_light.c` applies these values to global model attributes.

`res/field/area_data/*.json` selects the lighting set per area through `lightingSet`.

This makes environment-specific lighting possible without replacing the renderer.

### Other exposed visual systems
Confirmed in source/resource tree:
- fog manager
- field effect manager and renderer
- overworld weather
- particle system
- texture resource manager
- model attributes
- field camera
- map prop animation
- sprite resource manager
- battle particle utilities
- battle animation system
- battle animation scripts
- weather battle animations
- battle backgrounds
- Pokemon animation data
- field sprite resources
- map textures/models/props

## Visual strategy

The preferred approach is not "more polygons everywhere."

Target:
- stronger textures
- richer lighting
- better palettes
- layered environmental effects
- selective geometry improvements
- animated props/overlays
- cleaner sprites/UI
- stronger battle presentation

This should provide a larger perceived improvement per DS resource cost.

## Pass structure

### G1 — Rendering & Visual Capability Audit
Status: substantially complete.

Purpose:
- identify editable Platinum systems
- classify donor assets/techniques
- establish safe vs source-level vs advanced work
- avoid designing around assumed limitations

### G2 — Global Visual Foundation
Active.

#### G2A — Lighting and environment foundation
1. Audit all four existing lighting sets and area assignments.
2. Define environment lighting families:
   - temperate outdoor
   - forest
   - cave
   - snow
   - coastal
   - urban
   - industrial/Galactic
   - Mt. Coronet
   - Distortion World
3. Build stronger dawn/day/sunset/night templates.
4. Reassign areas where the retail four-set grouping is too coarse.
5. Add new lighting-set entries only when existing four-set reuse cannot deliver the desired result.


### G2A implementation checkpoint

Implemented on `visual-overhaul-g2a`:

- Expanded area-light archive support from 4 to 10 files.
- Added lighting families:
  - `lighting_set_004` — Eterna Forest / deep forest
  - `lighting_set_005` — Snowpoint / Route 217 snow
  - `lighting_set_006` — Galactic interiors
  - `lighting_set_007` — Mt. Coronet interior
  - `lighting_set_008` — Spear Pillar
  - `lighting_set_009` — Distortion World
- Registered all new sets in `lighting_sets.order` and `meson.build`.
- Reassigned:
  - `area_data_054` -> forest
  - `area_data_014` -> snow
  - `area_data_058` -> Galactic
  - `area_data_069` -> Coronet
  - `area_data_060` -> Spear Pillar
  - `area_data_074` -> Distortion World

The retail lighting sets 000-003 remain unchanged.

Current validation status:
- repository structure and references are internally consistent
- branch is based cleanly on current `main`
- runtime/build validation still required before these values are treated as locked


#### G2B — Environmental effects
Use Platinum's native field-effect/particle/weather systems first.

Targets:
- drifting leaves
- mist
- layered snow
- dust/pollen
- water shimmer
- atmospheric particles
- Galactic energy accents
- Distortion World particles/overlays

Mystery Dungeon effects are references/donors, not a wholesale engine transplant.


### G2B deep-forest atmosphere checkpoint

Current findings:
- `OVERWORLD_WEATHER_23` is used by Eterna Forest, Fullmoon Island Forest, and Newmoon Island Forest.
- Those maps also share `area_data_054`, now assigned to the new deep-forest lighting family `lighting_set_004`.
- Platinum's exposed field-effect manager already supports billboarded 3D effects, texture VRAM upload, fog participation, global model lighting, animation managers, and per-map renderer sets.
- `weather_sys.narc` is still prebuilt/opaque, so Pass G will not blindly patch that archive.

Implementation rule:
- Deep-forest atmosphere is a shared forest treatment, not an Eterna-only weather hack.
- Prefer exposed fog and field-effect APIs over modifying opaque weather internals.
- First forest atmosphere target: subtle mist + drifting leaf billboards at conservative density.
- Preserve the existing `OVERWORLD_WEATHER_23` behavior until its internals are fully identified.



### G2B implementation checkpoint

Implemented source-side presentation work:

- Added `CAMERA_TYPE_ETERNA_FOREST`.
- Eterna Forest now uses a dedicated perspective profile rather than the generic `CAMERA_TYPE_ZOOMED_IN`.
- Fullmoon Island Forest and Newmoon Island Forest retain the retail zoomed-in camera.
- The new Eterna profile uses:
  - distance: 545.0
  - pitch: 58.0 degrees
  - vertical FOV: 10.9 degrees
  - standard near/far clipping
- Purpose: expose more canopy/terrain depth and improve spatial presentation without changing map geometry.

Environmental-effects audit findings:

- Platinum's field-effect manager supports billboards, animated resources, fog participation, texture VRAM upload, and per-map renderer sets.
- Most exposed renderer implementations are object-attached effects rather than free ambient emitters.
- The primary field-effect asset archive `res/prebuilt/data/mmodel/fldeff.narc` is currently prebuilt/opaque in this decomp.
- `weather_sys.narc` is also prebuilt.
- Therefore, new leaf/mist texture effects should not be wired by blindly editing opaque archive members.
- Preferred next path: recover/extract the relevant prebuilt archives into reproducible source assets or reuse a known-compatible existing effect resource after exact identification.

Additional mapping note:

- `area_data_054` is shared by Eterna Forest, Fullmoon Island Forest, and Newmoon Island Forest.
- `lighting_set_004` should therefore be treated as a shared deep-forest lighting family unless those maps are split into separate area-data entries later.


#### G2C — Global UI presentation
Improve:
- frames
- panels
- cursors
- transitions
- menu palette hierarchy
- HUD readability
- party/status presentation

### G3 — Character and Pokemon graphics
- player sprites
- NPC sprites
- trainer sprites
- Pokemon icons
- Pokemon battle sprites/animation where worthwhile

### G4 — Environment reconstruction
- textures
- foliage
- water
- rocks
- roads
- buildings
- props
- interiors
- selective model upgrades

HGSS is the first donor/reference source.

### G5 — Battle presentation
- HUD
- backgrounds
- particle effects
- move animation upgrades
- camera motion
- screen shake/impact treatment
- weather presentation

### G6 — Showcase areas
Primary quality benchmarks:
- Eterna Forest
- Snowpoint / Route 217
- Distortion World

Additional showcase targets:
- Spear Pillar
- Team Galactic interiors
- lakes
- Turnback Cave

## First implementation target

Eterna Forest is the first quality benchmark because it exercises:
- foliage
- ground textures
- directional lighting
- ambient light
- fog/mist
- particles
- animated environmental elements
- field sprites

Before Eterna-specific asset work, G2A should establish the upgraded lighting vocabulary and identify which existing areas share each retail lighting set.

## Guardrails

- Keep Pokemon silhouettes/readability intact.
- Avoid visually incompatible assets even if technically portable.
- Prefer native Platinum systems before writing new rendering code.
- Backport HGSS behavior when it is clearly better and technically justified.
- Use Mystery Dungeon effects as inspiration/reference unless a clean conversion path exists.
- Do not spend work preserving original DS LCD artifacts or Platinum nostalgia.
- Do not add Delta-only visual dependencies.
