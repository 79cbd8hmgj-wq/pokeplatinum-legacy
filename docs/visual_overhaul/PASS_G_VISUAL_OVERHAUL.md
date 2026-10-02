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

## Donor-use constraint

Use external repositories primarily to research visual direction and implementation ideas.

Prefer:
- Platinum-native code paths and source-backed assets
- donor-informed palette, timing, staging, camera, particle, and UI decisions
- only trivially compatible donor assets with a proven resource contract

Reject or defer donor assets that require nontrivial format conversion, palette remapping,
animation/cell reconstruction, archive surgery, or speculative binary patching.

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



### G2B implementation checkpoint — native weather enhancement

Implemented in `src/overlay005/ov5_021D5EB8.c`:

- Deep-forest weather ID 23 retains its existing scrolling BG2 mist/parallax and density behavior, but its fog is now a muted green-gray (`GX_RGB(20, 24, 22)`) instead of flat white.
- Light snow fog now uses a cool blue-white (`GX_RGB(22, 26, 31)`).
- Heavy snow fog now uses a colder blue-white (`GX_RGB(20, 24, 31)`).
- Blizzard fog now uses `GX_RGB(20, 24, 31)`.
- Hail fog now uses `GX_RGB(22, 26, 31)`.
- Existing particle counts, movement logic, fog offsets, and transition timing remain unchanged pending runtime validation.

Validation:
- Only 10 intended weather-source lines differ from `main` for this checkpoint.
- Forest weather 23 is exclusive to the three deep-forest maps already sharing `area_data_054`.
- Brand-new leaf particles remain deferred because `weather_sys.narc` and `fldeff.narc` are currently prebuilt binary archives; adding new textures cleanly requires reconstructing one of those resource pipelines or deliberately patching the archive.



### G2B canopy-weather implementation checkpoint

Confirmed from the Diamond decomp:
- Platinum weather ID 23 corresponds to **CANOPY** weather.
- The canopy mode is a native weather-state entry, not an unknown placeholder.
- Platinum's canopy callback is `ov5_021DB144`.
- It already combines a scrolling BG2 layer with hardware fog.
- Its resource-set index is 9; Diamond's unpacked weather archive maps the associated members to raw weather resources 55-57.

Implemented:
- renamed `OVERWORLD_WEATHER_23` to `OVERWORLD_WEATHER_CANOPY`
- updated the forest map headers to use the named canopy constant
- kept the existing canopy state machine and resource layout
- shifted canopy fog slightly closer and changed it from pure white toward a cooler green-gray forest haze

This is intentionally a conservative first visual pass. Runtime validation in Delta should determine whether the fog offset/color can be pushed further before additional canopy motion or leaf elements are added.



### G2B implementation checkpoint — deep-forest mist

Implemented:
- Added `FieldMap_ApplyDeepForestAtmosphere()` in `src/overlay005/fieldmap.c`.
- Applies only to:
  - Eterna Forest
  - Fullmoon Island Forest
  - Newmoon Island Forest
- Runs after Platinum's normal weather initialization and after normal map-zone weather transitions.
- Preserves `OVERWORLD_WEATHER_23`; the patch only overrides fog color/alpha and the 32-entry fog density table.
- Current forest fog target is a muted green-gray with conservative alpha and progressive depth density.
- No opaque `weather_sys.narc` edits were made.

Runtime/build validation remains required before the fog values are locked.



### G2B native forest-effect verification

The deep-forest effect path has now been compared directly against retail Platinum.

Retail weather ID 23 already implements:
- a scrolling BG2 atmosphere layer
- hardware fog through `FogManager`
- fade-in/fade-out handling
- scroll coupling to player/camera movement

The overhaul therefore **enhances** that native path instead of replacing it.

Current branch changes:
- weather ID 23 is named `OVERWORLD_WEATHER_CANOPY`
- mist opacity: 7 -> 8
- fog offset: retail `0x6F6F - 1600` -> `0x6F6F - 1900`
- fog color: white `GX_RGB(31,31,31)` -> cool forest `GX_RGB(20,24,22)`
- existing 0.75 scroll response retained
- Eterna Forest receives a dedicated camera profile:
  - distance 545
  - pitch 58 degrees
  - vertical FOV 10.9 degrees
- Fullmoon/Newmoon forest keep the retail zoomed-in camera while sharing the canopy weather/lighting treatment
- Eterna, Fullmoon, and Newmoon route through the dedicated `sForestFieldEffectRenderers` list

Outdoor-lighting invariant:
- retail lighting sets 0 and 3 used global area model lighting
- new forest set 4 and snow set 5 preserve that behavior
- Galactic 6, Coronet 7, Spear Pillar 8, and Distortion World 9 preserve the non-global-lighting behavior of the retail sets they replace
- this is intentional; do not classify lighting families from map type alone

Leaf reuse finding:
- Platinum already contains editable leaf/petal resources under `res/graphics/trap_effects/`
- the Underground leaf effect uses standard Nitro 2D NCGR/NCLR/NCER/NANR resources
- its runtime is tightly coupled to Underground trap state, microphone input, and its own sprite environment
- reuse the artwork/resource formats, not the Underground runtime wholesale
- implement ambient forest leaves as a dedicated guarded field effect after the mist path is build/runtime validated



### G2B snow-atmosphere checkpoint

Mapped native weather handlers:
- weather 5 = light snow
- weather 6 = heavy snow
- weather 7 = blizzard

The native particle system already ramps density substantially, especially for blizzard. Particle counts were intentionally left unchanged for the first pass to avoid spending DS effect budget where retail is already dense.

Fog separation was strengthened instead:
- light snow: slightly denser/cooler distance haze
- heavy snow: stronger blue-white depth fog
- blizzard: strongest near-field atmospheric fog of the three

Named constants now replace the relevant magic fog values in both initialization and resume paths, ensuring weather transitions use consistent parameters.

Commit implementing this pass: `209b2dc0a0d403e5e159f63cd6f3e1520c8f8c37`.



### G2B forest mist implementation checkpoint

Implemented:
- Added a shared `FieldMap_IsDeepForest()` helper for Eterna Forest, Fullmoon Island Forest, and Newmoon Island Forest.
- The same helper now controls both dedicated forest renderer selection and forest atmosphere activation.
- Added `FieldMap_ApplyDeepForestFog()` using Platinum's native `FogManager`.
- Forest fog is applied **after** stock weather initialization so the custom atmosphere is not immediately overwritten.
- Uses a conservative 32-step density table, color+alpha fog blend, and a muted green-gray fog color.
- No changes were made to `weather_sys.narc`.

Current status:
- source wiring is complete
- runtime/build validation is still required
- next effect target is drifting leaves through the dedicated forest renderer path



### Eterna asset-path audit

Confirmed Eterna/deep-forest resource mapping:
- `area_data_054`
- `mapTextureSet = map_texture_set_053`
- `mapPropSet = prop_model_set_050`
- `prop_model_set_050` contains:
  - `prop_model_147_nsbmd`
  - `mansion_door_nsbmd`

Implication:
- most of the forest's visual identity comes from map geometry + `map_texture_set_053.nsbtx`, not a large standalone prop collection.
- the map/prop texture and model resources are Nitro binaries (`NSBTX` / `NSBMD`).
- `fldeff.narc` is also binary/prebuilt.
- the current GitHub connector exposes these paths and metadata but cannot materialize the binary contents in this environment.

Working rule:
- do not guess at anonymous binary resource IDs.
- continue source-exposed visual work (lighting, fog, renderer routing, camera, UI/code paths) immediately.
- inspect/convert Nitro assets when a binary-capable repository checkout or artifact handoff is available.



### G2C / G5 editable UI surface audit

Platinum exposes a large amount of interface art directly as PNG + animation/cell JSON rather than opaque archives.

Confirmed directly editable groups include:

#### Global windows
`res/graphics/windows/`
- message_box_00 through message_box_19
- standard field/system window graphics
- scroll cursor
- wait dial
- Pokemon preview graphics

#### Party menu
`res/graphics/party_menu/`
- menu tiles
- panels
- cursor
- buttons
- icons
- member-ball graphics
- touch controls
- subscreen resources

#### Pokemon summary
`res/graphics/pokemon_summary_screen/`
- primary/subscreen tiles
- tabs
- cursors
- status icons
- markings
- battle/contest page layouts
- ribbons and condition graphics

#### Start/options
`res/graphics/start_menu/`
`res/graphics/options_menu/`
- menu icons
- cursors
- tiles
- palettes

#### Battle UI
`res/graphics/battle/healthbox/`
`res/graphics/battle/interface/`
- player/enemy healthboxes
- doubles healthbox
- healthbox parts
- arrows
- battle cursor
- stock graphics
- level-up UI

Implementation implication:
- Platinum remains the editable UI base.
- HGSS/PMD should be treated as donor/reference sources for visual language, motion, and selected convertible assets.
- Whole-archive swaps are unnecessary and higher risk.
- G2C/G5 can redesign the UI by replacing source PNG/JSON resources while preserving Platinum's existing layout and runtime code where practical.



### G2B foliage-resource and emitter checkpoint

Binary inspection is now available through a temporary GitHub Actions asset-export artifact.

`fldeff.narc` inventory:
- 201 members total
- 15 NSBTX texture resources
- 145 NSBMD model resources
- 10 NSBTP texture-pattern animations
- 13 NSBCA skeletal animations
- 1 NSBMA material animation
- 5 NSBTA texture-coordinate animations
- 12 small metadata records

Relevant embedded resource names:
- texture member 000: `kusaeff`
- texture members 001-003: `e_kusaeff1`, `e_kusaeff2`, `e_kusaeff3`
- model member 083: `kusaeff`
- model member 084: `e_kusaeff1`
- model members 089/090: `lgrass_ani1` / `ngrass_ani1`

Source-reference mapping confirms `src/overlay005/ov5_021F2D20.c` / `FIELD_EFFECT_RENDERER_13` loads:
- model 83 -> `kusaeff`
- model 84 -> `e_kusaeff1`
- metadata members 170-173
- texture members 0-3
- billboard resource slots 0, 5, 6, 7

This renderer is already present in the normal and deep-forest renderer lists and exposes a standalone billboard path that does not require a map object.

Implemented forest foliage prototype:
- `FieldEffect_StartForestLeaves(FieldSystem *)`
- four recycled billboards controlled by one animation manager
- reuses existing renderer-13 foliage resources 5/6/7
- no new NARC members, textures, or models
- player-relative spawn/reset positions
- deterministic drift
- conservative 3/4 scale
- particles recycle after lifetime/range limits instead of allocating continuously
- cleanup is handled through the existing animation-manager lifecycle
- emitter starts only in the three deep-forest maps

Validation status:
- exact visual character of the reused `e_kusaeff` assets still requires Delta runtime inspection
- source is under US revision 0/1 CI and clang-format validation before being treated as locked



### G2B reconciled atmosphere architecture

Validated implementation state:

- Retail weather ID `23` is the forest/canopy handler backed by `ov5_021DB144`; it is now named `OVERWORLD_WEATHER_CANOPY`.
- Eterna Forest, Fullmoon Island Forest, and Newmoon Island Forest use that canopy weather path.
- Canopy weather owns its native BG2 mist/fog behavior. The visual pass tunes that native handler rather than layering a second forest fog controller over it.
- Snow weather variants likewise retain ownership of their native fog. Their fog colors/offsets are tuned in the existing weather handlers.
- `FieldMap_ApplySpecialAreaFog()` is reserved for lighting families that do not already own an equivalent weather-fog path:
  - Mt. Coronet
  - Spear Pillar
  - Distortion World
- The dedicated `sForestFieldEffectRenderers` path remains available for forest-only ambience.
- `FIELD_EFFECT_RENDERER_FOREST_AMBIENCE` uses the existing berry sparkle system as a sparse ambient mote/glint effect. Its position-only helper was audited and does not require a live `MapObject`.
- A prototype that repurposed `e_kusaeff1/2/3` as drifting leaves was removed after binary asset inspection confirmed those resources are retail one-shot ground-level grass effects.
- `fldeff.narc` has now been successfully exported and inventoried locally: 201 members (15 NSBTX, 145 NSBMD, 10 NSBTP, 13 NSBCA, 1 NSBMA, 5 NSBTA, 12 other/metadata members).
- Proper drifting leaves remain a later asset-authoring task; they should not reuse the grass-burst textures.


#### G2C — Global UI presentation
Improve:
- frames
- panels
- cursors
- transitions
- menu palette hierarchy
- HUD readability
- party/status presentation


### G2C UI source audit checkpoint

Platinum exposes the following UI groups as source-backed build resources:

- `res/graphics/windows/` — message boxes, scroll cursor, frame order
- `res/graphics/start_menu/` — cursor, icons, palettes
- `res/graphics/party_menu/` — menu panels, cursor, icons, buttons, subscreen
- `res/graphics/pokemon_summary_screen/` — tabs, cursors, status icons, tiles, page layouts
- `res/graphics/shop_menu/` — tiles, tilemaps, cursor, arrows
- `res/graphics/bag/` — bag UI tiles, layouts, player sprites
- `res/graphics/battle/healthbox/` — player/enemy healthboxes and parts
- `res/graphics/battle/interface/` — battle cursor/interface assets

Relevant donor/reference findings:

- HGSS exposes directly comparable window/area-window assets, menu code, cursor code, party-menu code, message-printer code, and font/window rendering infrastructure.
- PMD Sky exposes multiple frame variants, cursor assets, page arrows, text palettes, and UI transition graphics; treat these primarily as presentation/style references unless a clean conversion path is proven.

G2C implementation order:

1. Message-box/window frames and scroll cursor
2. Start-menu cursor/icon presentation
3. Party-menu panel/cursor cleanup
4. Pokemon summary-screen tabs/cursors/status presentation
5. Battle healthboxes and battle cursor
6. Bag/shop secondary UI

Reason: these are highly visible, source-backed, and can be upgraded without renderer work.



### G2C UI audit checkpoint

Platinum exposes most major UI surfaces in directly editable formats rather than opaque archives.

Confirmed editable groups:
- `res/graphics/windows/`
  - message-box PNGs
  - standard field/system windows
  - scroll cursor
  - wait dial
- `res/graphics/main_menu/`
  - menu tiles/backgrounds
  - arrows
  - buttons
  - particle sprites
  - animation/cell JSON
- `res/graphics/party_menu/`
  - menu tiles
  - panels
  - cursor
  - icons
  - buttons
  - animation/cell JSON
- `res/graphics/pokemon_summary_screen/`
  - page layouts
  - tabs
  - cursors
  - icons
  - tiles
  - palettes
  - animation/cell JSON
- `res/graphics/bag/`
  - main UI tileset
  - pocket selector
  - highlights
  - borders
  - item-entry icons
- `res/graphics/start_menu/`
  - icons
  - cursor
  - menu palettes
- `res/graphics/battle/healthbox/`
  - player/enemy healthboxes
  - doubles/safari variants
  - arrows and component graphics
- `res/graphics/battle/interface/`
  - cursor
  - stock/player/enemy interface graphics
  - level-up graphics
- `res/graphics/battle/type_icons/`
  - all type/category icons as editable PNGs plus shared palette/cell data

HGSS's `files/graphic/plist_gra/` contains equivalent Nitro UI resources (NANR/NCER/NCGR/NCLR/NSCR) and is the first donor/reference source for a later-Gen-IV interface treatment.

Implementation implication:
- most G2C work can be done as asset/layout replacement without rewriting the UI engine.
- highest-payoff first batch should be message windows, party menu, summary screen, bag, start menu, and battle healthboxes.
- preserve existing cell/animation geometry when possible for low-risk replacements; change layout code only where the redesigned composition requires it.



### G5 battle HUD palette checkpoint

Implemented a resource-contract-safe first battle HUD refresh:

- added `tools/visual_overhaul/generate_battle_ui.py`
- normal player/enemy healthboxes retain their existing indexed pixel geometry, NCGR dimensions, cells, and OAM layout
- changed only shared chrome palette entries used by the normal healthboxes:
  - cool edge highlight
  - deep navy outline
  - steel-blue rail
  - bright cool highlight
  - slate panel fill
- HP-state colors, status colors, white text/highlights, and black remain unchanged
- synchronized embedded preview palettes for:
  - `player_singles.png`
  - `player_doubles.png`
  - `enemy.png`
  - `healthbox_parts.png`
- `primary.NCLR` continues to be generated from `player_singles.png` exactly as before
- Safari healthbox remains untouched because it uses its own `safari.NCLR` and requires a separate design pass

Visual result:
- replaces the retail olive/brown frame language with a cleaner navy/slate/steel presentation
- preserves battle readability and the existing Pokemon HP/status color language

Validation status:
- generated assets have landed on `visual-overhaul-g2a`
- local indexed-palette preview confirms only the intended chrome colors changed
- normal ROM build, PR lint, and exported-binary verification are running against the generated assets before lock.

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

Source-side G4 implementation is complete across the representative environment set:
- G4A: Eterna Forest
- G4B: Snowpoint / Route 217
- G4C: Distortion World
- G4D: Spear Pillar
- G4E: Sinnoh lakes
- G4F: Turnback Cave
- G4G: Team Galactic interiors

The pass preserves map geometry, collision, scripts, progression, texture dimensions,
texel-index maps, and resource naming. Changes are isolated lighting and palette/material
grades, with dedicated area/texture slots created where shared retail resources would
otherwise cause collateral changes.

Objective G4 validation is closed:
- normal US Rev 0 / Rev 1 builds pass
- debug Rev 0 / Rev 1 builds and runtime-symbol export pass
- the area-light archive contract passes
- all G4 runtime probe symbols resolve

The headless DeSmuME autowarp harness remains in-tree as experimental, non-blocking QA.
Rendered-frame sanity review is still useful for subjective palette/lighting tuning, but it
does not block later visual passes.

HGSS is the first donor/reference source.

### G5 — Battle presentation
Status: **active**.

The existing resource-contract-safe battle HUD palette checkpoint is the G5 foundation;
do not restart the battle UI from retail.

Implementation order:
1. battle backgrounds and arena color/staging
2. impact/effect presentation
3. camera motion and screen-shake treatment
4. weather presentation
5. selective move-animation upgrades after the reusable presentation systems are stable

- HUD
- backgrounds
- particle effects
- move animation upgrades
- camera motion
- screen shake/impact treatment
- weather presentation

### G5 battle-terrain palette checkpoint

Implemented the first battle-background pass using source-backed terrain palettes rather than
changing sprite geometry or battle logic.

Added reproducible generator:
- `tools/visual_overhaul/generate_battle_terrain.py`

Current terrain families:
- grass — refreshed day/evening/night palettes with stronger time-of-day separation
- cave — cooler slate/indigo depth and less flat gray
- ice — cleaner cyan/blue-white highlights with stronger cold contrast
- Distortion World — shifted the retail muted rose family toward a more deliberate violet/magenta identity
- path — stronger earth/vegetation separation across day/evening/night
- path puddles — path treatment plus clearer reflected-sky/water color identity
- snow — colder blue-white daytime values, lavender sunset separation, and deeper blue-violet nights
- water — clearer cyan daytime depth, sunset coral-to-wine progression, and a deeper indigo night ramp

Resource-contract invariants:
- all terrain sprite PNG geometry is unchanged
- NCGR pixel indices are unchanged
- cells and animations are unchanged
- archive ordering is unchanged
- only 16-color JASC palette source data changed

This is the opening G5 background/staging sequence. Remaining natural and special arenas
will follow under the same palette-only contract while ordinary ROM build/resource
validation stays green.

### G5 natural-terrain palette completion checkpoint

The common natural battle-terrain palette pass is now synchronized with
`tools/visual_overhaul/generate_battle_terrain.py`.

Completed source-backed families now include:
- grass
- path
- path with puddles
- mud
- rocky
- sand
- snow
- ice
- water
- cave

Day/evening/night variants retain their original sprite geometry, NCGR pixel
indices, cells, animation data, palette counts, and archive ordering. The pass
changes only JASC palette source data and is therefore reproducible from the
generator.

Reproducibility is consolidated on `tools/visual_overhaul/generate_battle_terrain.py`.
The older duplicate `generate_battle_terrain_palettes.py` was removed so there is no stale
second source capable of regenerating conflicting palette values.

The next background work should focus on the remaining facility/special arenas rather than
reopening the already-completed natural terrain set.

### G5 special-arena palette checkpoint

Extended the battle-background palette pass into high-visibility special arenas while preserving
the same resource contract.

Updated families:
- generic indoor arena — cleaner steel/blue neutral hierarchy
- Giratina arena — deeper violet/magenta shadow identity distinct from the broader Distortion World palette
- Elite Four Aaron — brighter mint/teal hierarchy
- Elite Four Bertha — warmer earth/bronze hierarchy
- Elite Four Flint — stronger ember/crimson hierarchy
- Elite Four Lucian — clearer indigo/violet hierarchy
- Champion Cynthia — restrained pearl/lavender/charcoal presentation

All seven remain palette-only changes:
- terrain PNG geometry unchanged
- NCGR pixel indices unchanged
- cell/animation data unchanged
- archive ordering unchanged

The reproducible generator now owns these palettes alongside the common outdoor terrain set.

### G5 Battle Frontier arena palette checkpoint

Completed the first dedicated Battle Frontier arena pass while preserving each facility's
existing 256-entry palette layout and 4bpp sprite/cell contract.

Updated facilities:
- Battle Arcade — sharper magenta/pink presentation
- Battle Castle — cleaner emerald/green hierarchy
- Battle Factory — colder steel/cyan hierarchy
- Battle Hall — brighter white/cyan presentation
- Battle Tower — stronger gold/bronze hierarchy

The terrain generator now supports both 16-entry authored palettes and padded 256-entry
facility palettes, so these changes are reproducible without altering sprite geometry,
NCGR indices, cells, animations, or archive ordering.

### G5 impact-presentation pilot

Implemented a first reusable-impact pass using Platinum's existing battle-animation shake
primitives rather than adding a new renderer or particle subsystem.

Pilot moves:
- Body Slam — defender shake plus a restrained base-background jolt
- Giga Impact — retains its effect-background shake and adds a heavier base-arena jolt
- Explosion — retains the large effect-background shake and adds synchronized arena movement
- Stone Edge — adds a short base-background impact beneath the existing defender shake
- Close Combat — adds a tight horizontal arena jolt to reinforce the repeated hit sequence
- Brave Bird — adds the same base-arena impact in all three attacker-side/contest branches

Implementation rule:
- use `Func_ShakeBg(..., SHAKE_BG_TARGET_BASE)` only at explicit impact frames
- preserve existing particles, sounds, timing, battler movement, and effect-background behavior
- avoid global shake-strength changes until the move-script pilot is visually reviewed
- scale shake strength by move weight instead of making every damaging move equally violent

This establishes G5 screen-impact treatment through existing scriptable presentation systems
with no new runtime allocation or resource format.

### G5 battle staging / camera-language checkpoint

The source audit found that Platinum's battle-animation script surface exposes particle-camera
projection controls, but not a general-purpose full-scene camera dolly/zoom command. Practical
battle "camera" language on this engine is therefore built from battler motion, switched/custom
background scrolling, and selective base/effect-background movement.

A second staging pilot now reinforces moves whose existing animation already implies large
environmental force:

- Earthquake — base arena now moves with the existing battler/effect shake
- Hyper Beam — all normal/friendly-fire/contest branches add a restrained horizontal base-arena jolt at the beam impact
- Dragon Rush — adds a short base-arena impact beneath the existing effect-background shake
- Rock Slide — adds a compact two-axis arena shake beneath the existing defender shake

The pilot does not replace particles, sounds, move timing, or existing battler animation.
It uses the existing `Func_ShakeBg` implementation and explicitly targets
`SHAKE_BG_TARGET_BASE`, keeping the effect-background behavior independent.

### G5 donor-informed elemental-force checkpoint

Cross-repo research is now explicitly technique-first. The implementation basis is documented in
`docs/visual_overhaul/G5_DONOR_TECHNIQUE_AUDIT.md`.

Research takeaways applied here:
- Emerald: keep battler motion, arena/platform reaction, palette treatment, particles, and sound as separate presentation layers
- Yellow: use impact-specific shake/flash beats rather than one uniform global damage effect
- Stadium 1/2: borrow anticipation/recovery and arena-reaction language, not renderer/camera assets
- PMD Sky: borrow layered timing and clear primary-impact-recovery structure, not effect resources

Implemented pilot:
- Fire Blast — short base-arena jolt on the main defender impact
- Hydro Pump — stronger directional base-arena reaction under the pressure hit
- Blizzard — two restrained arena pulses aligned with its existing two defender-shake beats
- Thunder — intentionally unchanged as a control because Platinum already combines a base-background shake with an effect-background flash

No donor graphics, particles, backgrounds, or animation assets were imported.

### G5 donor-control special-attack checkpoint

The next donor comparison was deliberately conservative. Emerald's battle scripts were used to
check presentation structure, not to source assets.

Results:
- Psychic, Ice Beam, Flamethrower, and Thunderbolt already express the same core donor ideas well enough in Platinum and remain unchanged.
- Shadow Ball keeps all native Platinum particles, timing, sound, and defender effects, with only an added restrained dark-purple base-arena grade to supply the missing scene-level ghost atmosphere.

This checkpoint establishes an explicit rule for the remainder of G5: **research can validate no-change decisions**. A donor comparison does not automatically justify editing a move.

### G5 signature scene-grade checkpoint

Cross-game research also supports treating scene atmosphere as a separate layer from particles and
battler motion. Four Platinum moves already had strong black arena fades, so their resource/timing
contracts were preserved and only the existing fade color was specialized:

- Aura Sphere — dark blue
- Energy Ball — teal green
- Flash Cannon — dark gray
- Dragon Pulse — dark purple

No particles, emitters, sounds, timing, cells, backgrounds, or donor assets were replaced.


### G5 legendary-signature staging checkpoint

A signature-move audit applied the existing Platinum-native arena-reaction language only where a
clear impact-layer gap remained:

- Spacial Rend — restrained base-arena jolt beneath the main defender impact
- Roar of Time — stronger base-arena reaction at the white-flash impact
- Seed Flare — restrained base-arena reaction beneath the existing scene/effect shake

Three equally important no-change rulings were retained:

- Shadow Force already has grayscale disappearance/reappearance staging and a clear impact beat
- Dark Void already has a dedicated moving background, projection treatment, particles, and battler motion
- Judgment already combines a full white scene grade with repeated defender-impact shakes

The batch changes only base-arena motion at explicit impact frames. Existing particles, sounds,
backgrounds, timing, battler logic, and donor assets remain untouched.


### G5 heavy physical-collision checkpoint

A second physical-impact audit keeps heavyweight attacks visually distinct from ordinary contact moves.

Updated:
- Flare Blitz — short base-arena jolt on collision
- Wood Hammer — separate base-arena reaction beneath its existing effect-background shake
- Head Smash — strongest base-arena collision in the batch
- Superpower — heavy base-arena reaction under the defender impact
- Hammer Arm — restrained base-arena reaction beneath the existing effect/background motion

Deliberate no-change controls:
- Waterfall retains its moving dedicated background and existing defender treatment
- Aqua Tail remains a cleaner localized mid-power strike
- Outrage already supplies sustained scene motion through its switched background and repeated red pulses
- Dragon Claw, Iron Head, and Poison Jab remain localized impacts

No particle resources, sounds, timing, battler motion, backgrounds, or donor assets were replaced.



### G5 legacy ultimate/signature staging checkpoint

A final high-power signature sweep extends the established base-arena reaction language without
replacing any native animation resources.

Updated:
- Blast Burn — heavy base-arena jolt on the final impact in both side branches
- Hydro Cannon — heavy base-arena response under its sustained defender shake
- Frenzy Plant — heavy arena reaction when the delayed vine strike lands
- Psycho Boost — distinct base-arena impact beneath the switched-background hit
- Sacred Fire — restrained base-arena reaction beneath the existing scene treatment

No-change controls:
- Eruption already supplies a full scene grade, repeated eruptions, effect-background motion, and multi-target impact treatment
- Water Spout retains its broad multi-target burst and long defender shake
- Doom Desire already owns a full white delayed-impact scene
- Aeroblast already supplies a long dedicated-background shake and defender impact

No gameplay logic, particles, backgrounds, sounds, timing, or donor assets were replaced.

### G5 generic-special control checkpoint

A final common-special sweep produced **no additional edits**. Dark Pulse, Earth Power, Power Gem,
Sludge Bomb, Bug Buzz, Surf, Water Pulse, and Signal Beam already have sufficient native staging
through their existing combinations of scene fades/backgrounds, emitters, battler motion, color
treatment, and impact timing.

This is an explicit restraint checkpoint: G5 does not add arena-wide movement or scene grading merely
because a move is strong. Those layers are reserved for attacks whose native presentation has a clear gap.

### G5 weather-presentation checkpoint

Weather presentation is now aligned across both move initiation and the shared end-of-turn
weather animation paths.

Weather-setting moves:
- Rain Dance — black base fade replaced by a deep-blue storm grade
- Sunny Day — existing warm yellow grade strengthened from 10 to 12
- Sandstorm — added a restrained dark-yellow base grade, then restores the arena after the particle sequence
- Hail — black base fade replaced by a cool light-blue grade

Shared weather animations:
- `weather_rain.s` uses the same deep-blue storm grade
- `weather_sun.s` uses the same 12-strength warm grade and removes the prior 10/12 fade mismatch
- `weather_sandstorm.s` now carries the same restrained dark-yellow arena grade
- `weather_hail.s` uses the same cool light-blue grade

Invariants:
- weather mechanics, damage, duration, and turn sequencing are unchanged
- existing particle resources, emitters, sounds, and battle-script ordering are preserved
- no new battle renderer or allocation path was added
- `weather_fog.s` remains unchanged because it is a separate fog presentation path rather than one of the four standard field-weather states

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


### G2C global window foundation checkpoint

Implemented first UI resource upgrade:

- Added reproducible generator: `tools/visual_overhaul/generate_ui_foundation.py`.
- Added CI helper: `.github/workflows/generate-visual-ui.yml` for binary PNG generation.
- Rebuilt:
  - `res/graphics/windows/standard_system.png`
  - `res/graphics/windows/standard_field.png`
- Both assets retain:
  - original 24x24 dimensions
  - 3x3 8-pixel tile semantics
  - shared 4bpp palette architecture
  - palette index 0 behavior
  - original VRAM footprint
- The new system frame uses a cleaner high-contrast navy/slate hierarchy.
- The new field frame uses a teal/aqua Pokemon-style hierarchy with the same shared palette.
- No window-layout code, dimensions, cell data, or archive ordering changed.

Implementation is intentionally conservative at the resource-contract level while making the rendered chrome visibly cleaner.

Next G2C candidates:
1. scroll cursor / wait dial
2. optional message-box frame refresh
3. party menu chrome
4. summary-screen chrome
5. bag chrome




### G2C cursor / wait-dial checkpoint

Implemented through the existing reproducible UI generator:

- `res/graphics/windows/scroll_cursor.png`
  - preserved retail resource contract: 96x8 total
  - preserved 12 horizontal 8x8 animation frames
  - rebuilt as a cleaner bouncing down-chevron
  - uses only the shared window palette indices; no new palette or VRAM allocation

- `res/graphics/windows/wait_dial.png`
  - preserved retail resource contract: 16x128 total
  - preserved 8 vertical 16x16 animation frames
  - rebuilt as an 8-step rotating ring with active/highlight/trailing states
  - uses only the shared window palette indices; no new palette or VRAM allocation

Reproducibility:
- `tools/visual_overhaul/generate_ui_foundation.py` now generates the standard system frame, field frame, scroll cursor, and wait dial.
- `.github/workflows/generate-visual-ui.yml` tracks and commits all four generated assets.

Validation status:
- generated PNGs have landed on `visual-overhaul-g2a`
- binary dimensions/palette-index usage and ROM build are being verified through the visual-asset export and normal CI workflows before this checkpoint is treated as locked.


### G2C start-menu cursor checkpoint

Implemented:
- added `tools/visual_overhaul/generate_start_menu_ui.py`
- regenerated `res/graphics/start_menu/cursor.png` through the shared visual-UI workflow
- preserved the retail 96x32 cursor sprite canvas
- preserved the existing three-OAM 32x32 cell layout and one-frame animation contract
- preserved the colored start-menu palette bank and palette-index usage
- replaced the thick retail rounded rectangle with a thinner cut-corner selection frame plus a small inward focus chevron
- left the existing animated icon art/geometry unchanged because Platinum already supplies swell and wiggle selection animation states

Rationale:
- improves selection-frame clarity and reduces visual bulk without touching menu layout, sprite positions, animation sequencing, or VRAM allocation
- avoids recoloring shared palette index 15, which is also used inside the selected menu icons

Validation status:
- generator output has landed on the branch
- local preview confirms the intended cut-corner geometry
- normal ROM build / PR lint / exported-binary verification is running against the generated asset before lock.

### G2C party-menu palette checkpoint

Implemented a resource-contract-safe party-menu refresh through `res/graphics/party_menu/shared.pal`.

Scope:
- modernized palette banks 0 and 1 used by party-menu buttons/cursors and shared chrome
- preserved the existing 256-color JASC palette structure
- preserved sprite PNGs, OAM cells, animation JSON, dimensions, and VRAM usage
- retained separate cursor-state accents:
  - bank 0: gold accent
  - bank 1: teal accent

Visual direction:
- deep navy outlines
- cleaner royal/clear blue fills
- cool slate neutrals
- softer coral Poké Ball tones
- restrained gold/teal state accents

This provides a visible party-menu modernization without changing layout or sprite geometry.



### G2C Pokemon summary chrome checkpoint

Implemented a resource-contract-safe summary-screen refresh:

- added `tools/visual_overhaul/generate_summary_ui.py`
- updated only shared chrome colors in `tiles_main.pal`
- preserved page-specific accent colors and all tile/tilemap geometry
- updated only the repeated neutral outline/white entries in `sprites.pal`
- left `status_icons.pal`, ball palettes, ribbon palettes, sprite cells, animations, and NSCR layouts untouched
- explicitly preserves the page-specific palette entry used as black in bank 7 and pale yellow in bank 8

The first generator pass exposed why per-bank auditing matters: palette entry 6 is shared chrome in most summary banks but is page-specific in banks 7 and 8. The generator now treats those two banks as exceptions and repairs their original values deterministically.

Visual direction:
- deep navy outlines
- cool steel-blue edge colors
- pale blue-white panel highlights
- existing page identity/accent colors retained


### G2C bag chrome checkpoint

Implemented a conservative bag-interface refresh:

- added `tools/visual_overhaul/generate_bag_ui.py`
- `bag_ui_main.pal` changes only the first shared chrome gradient
- `ui_elements.pal` changes only the existing three-color blue accent ramp
- bag tilemaps, sprite geometry, pocket-specific colors, item icons, player bag sprites, Poké Ball graphics, and animation data remain unchanged

Visual direction:
- cool white highlight
- steel-blue midtones
- deep blue rail/outline
- clearer blue UI accent ramp consistent with the global window/start-menu/party-menu direction

Both summary and bag generators are wired into `generate-visual-ui.yml` so these text-palette changes remain reproducible alongside the PNG-based UI generators.


### G2C shop-menu chrome checkpoint

Implemented the next secondary UI pass:

- added `tools/visual_overhaul/generate_shop_ui.py`
- `default.pal` and `frontier.pal` now share the same refreshed neutral/chrome ramp
- the distinct default-shop and Battle Frontier accent colors at palette entries 9-15 are preserved
- `sprites.pal` changes only the existing three-color blue cursor/arrow ramp
- tilemaps, tiles, cursor/arrow sprite geometry, cells, and animations remain unchanged

This keeps normal shops and Frontier shops visually related while preserving their separate accent identities.


### G2C party-menu geometry checkpoint

The party-menu pass now goes beyond palette-only cleanup while keeping the retail sprite/OAM contracts intact.

Implemented through `generate_party_menu_ui.py`:

- rebuilt all four `cursor.png` states on the existing 128x48 cell geometry
- retained the two retail silhouette families:
  - cut-corner frame
  - rounded-leading-edge frame
- reduced the heavy retail outline into a thinner two-stage frame
- preserved distinct focused and alternate visual states
- rebuilt `button.png` on the existing four-cell packing:
  - two 56x32 large-button states
  - two 56x16 compact-button states
- retained the original NCER/NANR files, OAM counts, dimensions, animation IDs, and VRAM layout

The generated assets therefore change presentation without requiring party-menu layout/code changes.


### G2C summary navigation checkpoint

The summary-screen generator now also owns the two low-risk navigation assets:

- `tab_arrow.png`
  - remains 8x16
  - NCER still provides the mirrored right-facing version
  - existing NANR bounce animation is unchanged
  - art is now a cleaner compact chevron

- `move_cursor.png`
  - remains the retail 8x512 tile-strip source format
  - preserves the two 64x32 half-frame states consumed by the existing mirrored NCER layout
  - rebuilt as a thinner cut-corner frame with a navy inner edge
  - active red and alternate light states remain distinct
  - no cell, animation, OAM, or layout changes

These assets are generated and checked through the same visual-UI pipeline as the other G2C resources.


### G2C/G5 battle-cursor checkpoint

The battle command cursor now has a reproducible geometry refresh in `generate_battle_ui.py`.

- `res/graphics/battle/interface/cursor.png` remains 16x16
- the existing NCER still flips the one source corner into all four orientations
- the existing NANR bounce/offset animation remains unchanged
- the heavy retail L-corner was replaced by a thinner red focus bracket with a white inner highlight
- no command layout, sprite position, cell, animation, palette allocation, or VRAM contract changed

The cursor is now included in the generated-asset workflow alongside the healthbox palette refresh.


### G2C implementation-foundation closure checkpoint

The first global UI foundation is now implemented across the high-visibility source-backed surfaces targeted by G2C:

- global system/field windows
- scroll cursor and wait dial
- start-menu selection cursor
- party-menu palette, selection frames, and button chrome
- Pokemon summary shared chrome, tab arrow, and move-selection cursor
- bag chrome and UI accent ramp
- shop/default + Frontier chrome
- normal battle healthbox chrome
- battle command cursor

All of these changes preserve the existing Platinum resource contracts unless explicitly documented otherwise. No G2C change in this foundation batch requires a UI-engine rewrite.

Remaining UI work is now classified as deeper page-specific art/layout polish rather than a missing global foundation. That work can proceed after runtime inspection instead of blocking the next visual pass.

Runtime status:
- source/export/format/lint validation is being used as the build gate
- final visual tuning still requires Delta inspection because compile success cannot validate readability, spacing, or perceived contrast on-screen


### Visual UI generator concurrency fix

The generated-asset workflow exposed a CI race when multiple UI commits landed close together: a generator run could successfully build and commit an asset, then fail its push because the remote branch had advanced.

`generate-visual-ui.yml` now:

1. commits the generated assets locally
2. fetches the current `visual-overhaul-g2a` head
3. rebases the small generated-asset commit onto that head
4. pushes the rebased result

This keeps generated PNG/palette commits reproducible without losing concurrent documentation/source updates.


### G3 Pokemon-icon donor audit checkpoint

HGSS Pokemon icons are confirmed to be structurally compatible with Platinum at the source/resource level.

Confirmed:

- Platinum stores party/box icons as editable `res/pokemon/**/icon.png` resources and repacks them into `pl_poke_icon.narc`.
- HGSS stores the equivalent archive as editable `files/poketool/icongra/poke_icon/poke_icon_*.png` resources and rebuilds `poke_icon.narc`.
- Both use 32x64 indexed PNG icon sheets.
- The shared 256-color icon palette is byte-for-byte equivalent at the JASC palette level:
  - three populated 16-color banks
  - remaining entries unused/zeroed
- The standard 32x32 two-frame icon cell contract is equivalent:
  - two cells
  - one 32x32 OAM each
  - tile offsets 0 and 16
  - 4bpp/16-color sprite mode
- Runtime selection in both games uses the same basic model:
  - species -> icon archive member
  - form-specific member remapping
  - per-species/form selection of one of the shared palette banks

Archive-layout warning:

- Platinum currently exposes 539 icon PNG resources.
- HGSS exposes 544 icon PNG resources.
- HGSS includes additional late-Gen-IV battle/form icon members, including dedicated Castform battle forms and Cherrim battle presentation.
- Therefore **do not replace Platinum's entire icon archive with the HGSS archive**.

Implementation rule:

1. Keep Platinum's `pl_poke_icon.narc` build pipeline and named species/form ordering.
2. Import HGSS icon art per mapped species/form PNG.
3. Preserve Platinum's existing archive member IDs and `pokemon_icon.c` lookup behavior.
4. Treat HGSS-only members as optional later backports only when Platinum gains matching runtime form handling.

Classification: **Direct asset donor with explicit member remapping**, not whole-archive donor.

This makes Pokemon icons one of the safest G3 donor classes: artwork can be compared/replaced species-by-species without changing VRAM dimensions, shared palette architecture, cell geometry, or the Platinum icon loader.

Tooling:
- added `tools/visual_overhaul/audit_hgss_icons.py`
- accepts a local `pret/pokeheartgold` checkout through `--hgss-root`
- verifies the shared palette and standard cell contract
- maps Platinum base species to HGSS members using the shared `species + 7` convention
- compares indexed pixel data and embedded palettes for all base species through Arceus
- can emit a JSON manifest of identical/different/missing resources through `--write-manifest`

This gives the implementation pass a deterministic way to identify the HGSS icons that actually differ instead of replacing hundreds of pixel-identical assets blindly.


### G3 HGSS Pokemon-icon pilot checkpoint

The first G3 Pokemon-graphics batch now uses HeartGold/SoulSilver as the direct donor source for party/box icons.

Compatibility audit:

- Platinum `res/pokemon/.shared/pl_poke_icon.pal` is byte-for-byte color-equivalent to HGSS `poke_icon_00000000.pal` after newline normalization.
- Both games expose normal Pokemon icons as indexed 4bpp PNGs at 32x64 with 16-color per-image palettes.
- HGSS normal-species icon numbering follows `National Dex + 7`, matching the archive contract used by `GetMonIconNaixEx`.
- Because Platinum already builds its icon archive from named per-species PNG sources, HGSS donor art can replace those source PNGs without changing the Platinum icon archive builder, palette table, cells, animations, or runtime loader.

Pilot batch replaced with HGSS art:

- Pikachu
- Eevee
- Turtwig
- Chimchar
- Piplup
- Staraptor
- Luxray
- Garchomp
- Riolu
- Lucario

The replacements preserve Platinum's existing per-species paths and build wiring. This batch is intentionally limited to normal species first; eggs and alternate-form icon indices remain untouched until their donor-index mapping is audited separately.

Donor source:
- repository: `pret/pokeheartgold`
- audited donor commit: `9d8b7591f09b65804da2fb2dfd56f320633e0d36`

If the pilot build/runtime presentation is clean, the same mapping can be expanded across the normal National Dex without engine changes.


### G3 HGSS battle-sprite donor audit checkpoint

The first full Pokemon battle-sprite donor audit is complete and is recorded in
`docs/visual_overhaul/HGSS_BATTLE_SPRITE_AUDIT.md`.

The audit compares the four base sprite source slots used by Platinum for every
species (female back, male back, female front, male front) against the pinned
HGSS donor.

Results:

- **494 species audited**
- **1,812 overlapping sprite files audited**
- **495 files contain actual rendered-art differences**
- those art differences span **253 species**
- **433 files are fully identical**
- **884 files differ only in palette/color treatment while retaining the same indexed art**
- **0 structural incompatibilities** among overlapping files
- **164 missing target paths** are the expected Platinum omissions for impossible/unused gender slots (genderless or single-gender species), not format failures

Representative inspection confirms that the real differences are meaningful
later-game redraws rather than archive noise: examples such as Pikachu,
Charizard, Gyarados, and Snorlax use visibly different HGSS frames, while some
Sinnoh-era species such as Torterra retain effectively the same underlying art.

This makes HGSS battle sprites a real G3 donor class, unlike Pokemon icons.

However, wholesale replacement is intentionally not being applied yet. Platinum
stores its battle-animation timing/frame-shift data separately in per-species
`sprite_data.json`, while HGSS's corresponding animation data is still carried
in prebuilt animation archives rather than an immediately source-compatible
per-species format. Platinum also compiles normal/shiny palettes from separate
`normal.pal` / `shiny.pal` sources.

The safe backport strategy is therefore:

1. preserve Platinum's normal/shiny palette sources
2. transplant only HGSS indexed sprite art that is an actual art difference
3. preserve Platinum's existing gender/file contract
4. stage the donor set through animation/bounding-box compatibility checks
5. runtime-check the changed animation frames before treating the full 253-species set as locked

This prevents a visually newer static frame from silently regressing a
species-specific Platinum animation.


### G3 HGSS battle-sprite palette-contract checkpoint

The geometry-close set has now passed a second safety gate against Platinum's
actual sprite packing contract.

The Platinum build packs battle-sprite pixel indices separately from each
species' `normal.pal` / `shiny.pal`, so a donor PNG is not safe merely because
its embedded palette looks correct. The donor's used indices must remain
meaningful under Platinum's retained palettes.

Results across the 69 geometry-close species:

- **130** changed sprite views audited
- **53** views are direct-index-safe
- **28** species are fully direct-index-safe across all changed views
- **77** views have palette mismatches
- **41** species therefore remain on the conversion/review path
- **0** species fell into an exact-normal-remap-only middle tier

This reduces the automatic runtime-candidate pool from 69 to **28 species**.

A five-species runtime pilot is now staged:

- Venusaur
- Persian
- Hypno
- Lapras
- Tyranitar

Only their changed HGSS front sprites are imported. Platinum palettes,
`sprite_data.json`, back sprites, archive ordering, and engine behavior remain
untouched.

Runtime checklist: `docs/visual_overhaul/HGSS_BATTLE_SPRITE_RUNTIME_PILOT.md`.

Do not expand the remaining 23 direct-index-safe species until this pilot is
visually checked in Delta.


### G3 HGSS battle-sprite palette-order triage checkpoint

The 41 geometry-close species that failed exact RGB palette matching were split
again by palette-index ordering rather than being treated as one manual-conversion
bucket.

For each changed view, the audit compares the identity index mapping against the
globally minimum-cost one-to-one RGB assignment into Platinum's retained normal
palette.

Results:

- **41** palette-mismatch species examined
- **77** changed views examined
- **30 species** retain identity as the optimal palette-index ordering
- **11 species** show evidence of index reordering and remain explicit conversion cases

The 30 identity-order candidates can later be runtime-tested while still retaining
Platinum's normal/shiny palettes; their RGB palettes differ, but the evidence says
the color roles remain on the same indices.

The 11 reorder-suspected species are:

- Exeggcute
- Feraligatr
- Granbull
- Igglybuff
- Nidorina
- Porygon2
- Slowking
- Snorlax
- Sunflora
- Teddiursa
- Togetic

These must not be imported without a deliberate pixel-index conversion.

Current G3 battle-sprite funnel:

1. **253** species with genuine HGSS art differences
2. **69** pass conservative static frame geometry
3. **28** are exact direct-index-safe
4. **30 more** preserve likely index semantics despite RGB palette drift
5. **11** geometry-close species show likely palette reordering
6. the remaining geometry-review species stay deferred pending animation/frame work

The active implementation gate remains the five-species direct-index-safe runtime
pilot before either safe pool is expanded.


### G4 environment reconstruction completion checkpoint

G4 is now **source-pass complete / runtime QA pending**.

Completed representative environment families:
- Eterna Forest
- Snowpoint / Routes 216–217 / Acuity
- Distortion World
- Spear Pillar
- Sinnoh lake family
- Turnback Cave
- Team Galactic interior review

Implemented work is limited to guarded texture palette changes, dedicated
lighting, and safe resource isolation. Map collision, gameplay geometry,
scripts, encounters, warps, and progression are unchanged.

Selective NSBMD/map-geometry upgrades are deferred: the current source tree has
a reproducible NSBTX texture pipeline but not a proven editable/round-trip model
authoring pipeline. G4 should not cross that boundary through blind binary edits.

Canonical completion record:
`docs/visual_overhaul/G4_ENVIRONMENT_RECONSTRUCTION_COMPLETE.md`.

The next visual implementation phase is **G5 — Battle Presentation**.
