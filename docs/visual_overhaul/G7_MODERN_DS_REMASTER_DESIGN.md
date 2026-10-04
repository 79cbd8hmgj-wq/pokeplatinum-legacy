# G7 — Modern DS Remaster Visual Design

Status: **DESIGN LOCKED FOR IMPLEMENTATION**

## Goal

Push the existing visual overhaul beyond "polished Platinum" into a deliberately more modern, immersive, intense presentation while remaining a real Nintendo DS ROM that runs through DS emulators on iPhone.

The target is not a fake native iOS interface and not strict retail-Platinum authenticity.

The target is:

> **A premium modern DS remaster of Pokémon Platinum, designed to look excellent when emulated on a phone.**

The DS hardware model, 256x192 screens, touch input, dual-screen composition, Nitro resources, and ROM-side rendering remain authoritative constraints.

## Product principles

1. **Modernize composition, hierarchy, motion, and atmosphere — not by pretending the DS is a modern GPU.**
2. **Top screen = dramatic play space. Bottom screen = touch-first command center.**
3. **Every redesign must remain readable in both emulator layouts used in practice:**
   - landscape side-by-side screens;
   - portrait stacked screens.
4. **Avoid important text or controls at extreme edges when possible**, because emulator overlays can partially cover those areas.
5. **Preserve gameplay information density.** Modernization must never hide HP state, status, PP, type, targeting, party state, or item information.
6. **Intensity should be contextual, not constant.** Rival, Gym, Elite Four, Galactic, legendary, low-HP, critical, KO, and major move moments should feel stronger than ordinary encounters.
7. **Use native Platinum systems first.** Donor games inform style and technique; they do not justify risky whole-system swaps.
8. **Keep the pixel-art/Nitro language.** No thin vector-style lines, tiny modern icons, subtle low-contrast gradients, or UI that only looks good at emulator upscales.
9. **Preserve input semantics.** Touch/button hitboxes and menu behavior must stay reliable even when visuals change.
10. **No external texture packs, shaders, or emulator-specific assets.** Everything ships in the ROM.

## Relationship to Pass G

Pass G remains valid and is the foundation.

Do not undo:
- existing G2C UI modernization;
- G4 environment grades;
- G5 battle presentation work;
- G6 showcase integration;
- existing generators and resource contracts.

G7 is an escalation pass. It deliberately goes beyond the conservative visual scope used to close Pass G.

## Visual language

### Global palette direction

Use a coherent high-contrast system:

- deep navy / charcoal for structural outlines;
- cool white / pale blue-white for readable panels;
- saturated but controlled accent colors for actions and states;
- richer environment-specific hues in battle and field scenes;
- stronger local contrast than retail Platinum.

Do not globally desaturate the game. The goal is dramatic separation, not a gray "HD" filter.

### Shape language

Prefer:
- chamfered or cut-corner panels;
- 2-3 pixel structural outlines where resource scale allows;
- layered edge/highlight/shadow treatment;
- compact depth rather than exaggerated retail bevels;
- clear focused/pressed/disabled states.

Avoid:
- huge empty rectangular regions;
- ultra-rounded smartphone cards;
- flat monochrome blocks without depth;
- ornamental clutter that competes with Pokémon sprites or text.

### Motion language

Use motion as feedback:
- short focus pulses;
- cursor bounce;
- compact pressed-state compression;
- selective flash/shake for impact;
- restrained panel entrance/exit motion if existing animation contracts permit.

Do not add constant motion to every UI element.

## Battle presentation design

Battle is the highest-priority G7 surface.

### Top screen

The top screen should feel cinematic without changing the basic battle engine contract.

#### Healthboxes
Target:
- slimmer visual weight while maintaining existing information;
- stronger dark outline;
- cleaner internal separation;
- more modern rail/frame treatment;
- HP bar remains immediately readable;
- status remains visually distinct;
- level/name priority remains strong.

Do not remove:
- species name;
- gender;
- level;
- HP bar;
- numeric player HP where currently present;
- status indicators.

#### Battle text window
Retail-style beige/olive presentation should no longer dominate.

Target:
- darker, cleaner frame;
- cool light text field;
- stronger separation from the arena;
- reduced "2009 dialog box" feel;
- no loss of line capacity or printer timing.

#### Battle backgrounds
Build on G5:
- stronger value separation;
- richer time-of-day grading;
- boss/special arenas should feel more theatrical;
- avoid flattening sprites into the background;
- no geometry changes unless needed for a specific proven visual gain.

#### Encounter hierarchy
Presentation tiers:

**Tier 0 — ordinary wild**
- clean normal intro;
- restrained atmosphere.

**Tier 1 — ordinary trainer**
- slightly stronger transition/focus than wild.

**Tier 2 — Rival / Galactic Commander / Gym**
- stronger palette/transition identity;
- tighter intro pacing;
- more pronounced first-frame presentation.

**Tier 3 — Elite Four / Champion / major legendary**
- strongest legal/intended presentation;
- special arena emphasis;
- more forceful transition, flash, or screen reaction;
- never obscures combat information.

### Bottom battle screen

The bottom screen becomes the visual command center.

#### Command menu
Keep the existing four-command semantics.

Target hierarchy:
- **FIGHT** is dominant;
- BAG / POKÉMON / RUN are secondary;
- focused state must be obvious without relying only on color;
- labels remain readable at native resolution;
- touch targets remain large.

Visual direction:
- deep structural frame;
- richer action colors;
- less empty filler;
- thinner, cleaner inner bevel;
- stronger pressed/focus response.

#### Move-selection screen
This is the most important G7 interaction surface.

Required:
- four move slots preserve their runtime mapping;
- move name;
- type;
- PP;
- disabled/empty state;
- selection state.

Desired if feasible without destabilizing layout:
- physical/special/status category icon;
- clearer PP hierarchy;
- stronger type strip/badge;
- selected move receives frame + brightness change;
- disabled moves visibly muted.

Do not make category icons mandatory if they require invasive engine work. They are a Phase 1B enhancement after the primary redesign is stable.

#### Low-HP intensity
Add stronger visual urgency without altering gameplay:
- pulse or palette-state accent on the player's healthbox;
- optional subtle command-screen accent change;
- no strobing;
- no persistent full-screen red filter.

## Core menu design

### Party menu
Target:
- stronger member-card hierarchy;
- clearer selected state;
- HP/status legibility first;
- party icons and member balls remain visible;
- touch buttons should look intentional, not like leftover DS chrome.

### Pokémon summary
Target:
- tabs read as a modern navigation system;
- page title/section hierarchy clearer;
- move/stat pages emphasize data instead of decorative background;
- selected move cursor stronger;
- preserve all page functions and contest/ribbon content.

### Bag
Target:
- reduce visual clutter;
- stronger pocket identity;
- clearer item-row focus;
- improve quantity/value readability;
- preserve pocket switching and touch behavior.

### Start menu
Target:
- stronger icon identity;
- clearer focus state;
- less "floating DS icon list" appearance;
- retain existing menu topology and keyboard/touch input behavior.

### Shop / secondary menus
Bring them into the same global chrome language after the high-use surfaces are stable.

## Overworld presentation design

G4 remains the base.

G7 field work should focus on *perceived depth and atmosphere* rather than replacing every map asset.

Priorities:
- richer day/evening/night separation;
- darker caves with readable traversal;
- stronger snow/cold identity;
- more threatening Galactic interiors;
- more dreamlike Distortion World;
- improved water/coastal color separation;
- subtle environmental motion where native field-effect systems safely support it.

Do not perform broad blind texture replacements.

## Immersion and intensity rules

### Critical hits
If the battle animation/script surface supports it cleanly:
- add a sharper short flash/shake/audio emphasis path;
- do not lengthen battle pacing significantly.

### Super-effective hits
Prefer a brief extra impact accent rather than a persistent overlay.

### KO
Strengthen the moment through existing fade/motion/sound timing if feasible.
Do not add long cinematic delays to ordinary KOs.

### Boss opening
Use presentation differentiation rather than new gameplay.
Potential tools:
- palette emphasis;
- battle-background state;
- existing fade/transition primitives;
- trainer sprite staging;
- short arena movement.

### Legendary encounters
Use the strongest environmental and battle grade available while keeping sprite readability.

## Emulator-specific design constraints

The ROM must remain emulator-neutral, but the design must be evaluated on phone emulators.

Test every major UI surface in:
- portrait stacked mode;
- landscape side-by-side mode;
- touch overlay enabled;
- standard integer/non-integer scaling where available.

Do not depend on:
- a specific controller skin;
- hidden emulator controls;
- external shaders;
- screen gaps being a specific size;
- one orientation.

## Accessibility/readability floor

At native 256x192 render size:
- all essential text must remain legible;
- selection cannot be color-only;
- HP state must remain recognizable;
- disabled state must remain recognizable;
- no critical labels may overlap;
- no touch target may become smaller than the retail functional hit area.

## Donor/reference policy

Priority:
1. Platinum source/resource path.
2. HGSS for late-Gen-IV UI/resource ideas.
3. Diamond for engine/control comparison.
4. PMD Sky for transition/effect language.
5. Stadium/Stadium 2 for battle staging reference.
6. Ruby/FireRed/Crystal/Yellow for pixel-art/readability references.

Borrow:
- composition;
- palette hierarchy;
- timing;
- selection language;
- transition language;
- impact staging.

Do not blindly transplant:
- incompatible renderers;
- N64 camera systems;
- PMD resource pipelines;
- large archives with unverified contracts.

## Non-goals

G7 does not:
- convert Platinum into a native iPhone app;
- redesign gameplay systems;
- change Pokémon balance;
- replace the battle engine;
- require HD texture packs;
- require 3D camera freedom the engine does not expose;
- remove the dual-screen model.

## Visual acceptance bar

G7 succeeds when a person familiar with base Platinum can immediately say:

> "This is clearly Pokémon Platinum underneath, but it no longer looks like an untouched 2009 DS game."

The result should feel:
- modern;
- deliberate;
- intense;
- readable;
- cohesive;
- premium;
- still unmistakably Pokémon.
