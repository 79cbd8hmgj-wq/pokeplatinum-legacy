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
