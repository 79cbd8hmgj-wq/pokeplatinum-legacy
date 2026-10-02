# Pass G — Cross-Game Visual Donor Matrix

## Purpose

Choose the strongest available Pokemon source/reference for each visual subsystem before implementation. Categories:

- **Direct donor**: close enough to Platinum/DS formats or engine lineage to justify direct comparison/backport attempts.
- **Convertible donor**: assets/logic can be translated into Platinum's systems with adaptation.
- **Technique donor**: implementation or presentation pattern is useful, but not directly portable.
- **Reference**: visual/art direction only.

## Source pool audited

- Pokemon Platinum — target engine
- Pokemon HeartGold/SoulSilver
- Pokemon Diamond/Pearl
- Pokemon Mystery Dungeon: Explorers of Sky
- Pokemon Mystery Dungeon: Red Rescue Team
- Pokemon Ruby/Sapphire
- Pokemon Yellow
- Pokemon Stadium
- Pokemon Stadium 2

## Matrix

| Visual subsystem | Primary source | Secondary source(s) | Donor class | Planned use |
|---|---|---|---|---|
| Field lighting | Platinum | HGSS, Stadium | Native + reference | Expand Platinum's editable area-light families; use external games only for visual direction |
| Day/night atmosphere | Platinum | HGSS, Diamond | Direct comparison | Stronger time-of-day templates using Platinum's existing light vectors and material colors |
| Weather behavior | Platinum | Diamond, PMD Sky, Ruby | Direct comparison + technique | Compare DS weather implementations first; borrow density/timing ideas from PMD/Ruby |
| Fog/mist | Platinum | PMD Sky, Stadium | Native + technique | Use Platinum fog manager; design richer mist/atmosphere from PMD/Stadium references |
| Field particles | Platinum | PMD Sky, Ruby | Native + technique/convertible | Prefer Platinum field effect/particle system; rebuild PMD/Ruby concepts natively |
| Animated environmental overlays | PMD Sky | Ruby, Platinum | Technique/convertible | Leaves, pollen, shimmer, dust, supernatural overlays |
| Map/prop animation | Platinum | Diamond, HGSS, Ruby | Direct comparison | Reuse/extend Platinum prop animation; inspect Diamond/HGSS animation resources |
| 3D field models | HGSS | Diamond, Platinum | Direct/convertible | Compare late Gen IV models; convert selectively into Platinum's model/texture pipeline |
| Field textures | HGSS | Diamond, Ruby | Convertible/reference | Prefer late Gen IV assets; use Ruby for palette/tile motifs when stronger |
| Foliage | HGSS | PMD Sky, Ruby | Convertible/reference | Improve trees/grass textures and add cheap layered motion/effects |
| Water | HGSS/Platinum | PMD Sky, Ruby | Direct/technique | Improve texture/animation/shimmer without wasting geometry |
| Snow environments | Platinum | Diamond, HGSS, PMD Sky | Direct/technique | Combine Platinum snow systems with stronger density/layering and cold lighting |
| Urban environments | HGSS | Diamond, Platinum | Convertible/direct | Stronger building surfaces, props, lighting separation |
| Galactic/industrial environments | Platinum | Stadium, PMD Sky | Native/reference | More sterile lighting, animated energy accents, stronger contrast |
| Distortion World | Platinum | PMD Sky, Stadium | Native/technique/reference | Push particles, overlays, camera, unusual lighting/material treatment |
| NPC/player field sprites | HGSS | Platinum, Diamond | Direct/convertible | Prefer best late-Gen-IV sprite quality compatible with Platinum pipeline |
| Pokemon icons | HGSS | Platinum | Direct/convertible | Compare icon resources and replace where HGSS is stronger |
| Pokemon battle sprites | Platinum/HGSS | Stadium 1/2, Yellow/Ruby | Direct + reference | Keep DS sprite pipeline; improve animation/staging using Stadium references |
| Trainer battle sprites | HGSS | Platinum, Ruby | Direct/convertible | Use strongest compatible trainer art; convert only when necessary |
| Battle backgrounds | Platinum | Stadium 1/2, Diamond | Native/reference | Redesign composition/material treatment while keeping DS-native format |
| Battle camera | Platinum | Stadium 1/2 | Native + technique | Add stronger framing, anticipation, impact motion, and restrained camera movement |
| Move animation scripting | Platinum | Diamond, Ruby, Yellow | Native/direct/reference | Platinum remains implementation target; Ruby/Yellow offer clear timing/composition examples |
| Battle particles | Platinum | PMD Sky, Ruby | Native + technique | Improve density, layering, motion, and timing within Platinum's particle system |
| Hit impacts/screen shake | Platinum | Stadium 1/2, Ruby | Native + technique | Stronger physicality without excessive visual noise |
| Pokemon animation timing | Stadium 1/2 | Platinum/HGSS | Reference | Use Stadium's anticipation/recovery/staging ideas, adapted to sprite battles |
| Battle HUD | Platinum | HGSS, Ruby, Yellow | Direct/convertible/reference | Cleaner hierarchy, stronger readability, less dead visual space |
| Menus/UI frames | HGSS/Platinum | PMD Sky, Ruby | Direct/convertible | Modernize panels, cursors, transitions while retaining Pokemon visual grammar |
| Screen transitions | Platinum | PMD Sky, Ruby, Yellow | Native + technique | Replace weak transitions with better layered wipes/fades using native systems |
| Palette design | Platinum/HGSS | Ruby, Yellow | Convertible/reference | Use richer hue separation and environmental palettes; avoid unnecessary nostalgia constraints |
| 2D tiles | Ruby | Yellow, Platinum | Convertible/reference | Source readable motifs/patterns, then redraw/convert for DS use |
| Historic Pokemon visual grammar | Yellow | Ruby, Stadium | Reference | Use only when an older design communicates Pokemon identity better than later art |

## Strict donor-use policy

Cross-game repositories are primarily **research sources**, not asset banks.

Default behavior:
- borrow **ideas, timing, staging, composition, palette logic, animation structure, and presentation techniques**
- reimplement those ideas through Platinum's native systems and source-backed resources
- do **not** import an external asset merely because it looks better

An external asset may be transferred only when all of the following are true:
- the format and resource contract are already compatible or require only trivial deterministic conversion
- dimensions, palette/index assumptions, animation/cell structure, and archive placement are known
- the transfer does not require speculative binary editing or broad remapping
- the result can be reproduced from source and validated by normal build/resource checks
- the visual gain clearly justifies even that small integration cost

If any of those conditions are uncertain, classify the candidate as **Technique** or **Reference**, not Direct/Convertible.

This policy intentionally favors Platinum-native reconstruction over donor transplantation.

## Key findings

### Platinum is more capable than a simple asset swap project
The target decomp already exposes:
- area lighting
- fog
- weather
- field effects
- particles
- texture and model resource managers
- map prop animation
- camera
- battle particles
- battle animation scripting
- battle backgrounds
- Pokemon animation systems

Therefore, new engine code should be a last resort rather than the default.

### Diamond is a control/reference build, not merely another donor
Diamond shares the closest engine lineage with Platinum and exposes:
- field RTC/weather code
- camera code
- palette/render-window code
- NNS G2D/G3D systems
- extensive NSBTA/NSBCA/NSBTP field animation resources
- extensive battle/effect/model data

Use it to answer: **Did Platinum remove, change, or simplify something that Diamond already had?**

### HGSS is the strongest external DS technical donor
Use first for:
- field graphics
- 3D models
- textures
- field sprites
- Pokemon icons
- UI
- late Gen-IV rendering/animation behavior

### PMD Sky is the strongest effects reference
Confirmed:
- dedicated effect resource family
- effect animation source
- weather source
- dungeon camera source
- large animated sprite/background resource sets

Do not transplant the PMD engine wholesale. Recreate useful effects through Platinum's native systems.

### Ruby is a high-value 2D/effects donor
The decomp exposes:
- many editable tiles and palettes
- animated tiles
- field effect scripts
- battle animation scripts
- sprite resources
- weather/effect logic

Its battle animation scripts are especially useful because they clearly compose:
- sprite creation
- delays
- alpha blending
- sound timing
- battler movement
- screen/battler shake
- multi-layer particles

The exact GBA implementation is not portable, but the timing/composition language is valuable.

### Stadium 1/2 are presentation references, not renderer donors
The Stadium repo includes tooling that reconstructs animation scripts and display-list/texture data. The useful information is:
- animation sequencing
- battle staging
- camera/framing
- lighting/material choices
- attack anticipation and recovery
- arena visual composition

Do not attempt to port N64 rendering code into Platinum.

### Yellow is a selective style/reference source
Useful for:
- iconic UI/visual language
- battle transition concepts
- sprite animation readability
- simple, strong move-effect silhouettes
- Pikachu animation ideas

Low priority for direct implementation.

## Implementation priority after audit

1. Platinum native lighting/environment foundation
2. Diamond/HGSS comparison for field animation and environmental resources
3. Eterna Forest proof using improved lighting + native particles/overlays
4. Snowpoint/Route 217 proof using weather + layered effects
5. Battle presentation proof using Platinum implementation + Stadium/Ruby timing references
6. UI pass using Platinum/HGSS as base and PMD/Ruby for presentation ideas
7. Only then consider source-level renderer extensions

## Runtime constraint

Primary runtime is Delta DS emulation. Validate against the DS behavior/specification actually enforced by the emulator. No external shaders, texture packs, emulator skins, or Delta-only visual dependencies are part of Pass G.
