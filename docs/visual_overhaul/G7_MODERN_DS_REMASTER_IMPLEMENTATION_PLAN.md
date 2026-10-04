# G7 — Modern DS Remaster Implementation Plan

Status: **READY FOR IMPLEMENTATION**

Canonical design:
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md`

Foundation that must be preserved:
- `docs/visual_overhaul/PASS_G_VISUAL_OVERHAUL.md`
- `docs/visual_overhaul/G5_BATTLE_PRESENTATION_COMPLETE.md`
- `docs/visual_overhaul/G6_SHOWCASE_INTEGRATION_COMPLETE.md`
- existing visual generators under `tools/visual_overhaul/`

## Objective

Implement the G7 design as a staged visual escalation on top of current `main`, keeping the game a normal DS ROM while making the presentation feel intentionally modern on iPhone DS emulators.

Do **not** restart the visual overhaul from retail assets. G7 extends the existing Pass G work.

## Branch / integration policy

Use a dedicated implementation branch from current `main`:

`visual/g7-modern-ds-remaster`

Rules:
1. Rebase/refresh from current `main` before implementation.
2. Do not implement on the historical `visual-overhaul-g2a` branch.
3. Preserve all gameplay-overhaul changes already merged to `main`.
4. Keep generated asset changes reproducible through scripts in `tools/visual_overhaul/`.
5. Commit each G7 batch separately so visual regressions are bisectable.
6. Do not bundle unrelated gameplay fixes into the visual PR.
7. Build both US Rev 0 and US Rev 1 before declaring a batch complete.

## Phase order

G7 is intentionally front-loaded toward high-visibility battle/UI work.

### G7.1 — Battle command-center redesign
**Priority: highest**

Goal: make the battle bottom screen look purpose-built for touch/emulator play rather than like a polished 2009 menu.

Primary source surfaces:
- `res/graphics/battle/interface/`
- `res/graphics/battle/healthbox/`
- battle command/move-menu code in `src/battle/battle_controller_player.c`
- supporting battle controller/system code only where layout/state wiring requires it
- `tools/visual_overhaul/generate_battle_ui.py`

Required implementation:
- preserve four-command semantics: Fight / Bag / Pokémon / Run;
- preserve current touch/button behavior;
- preserve all battle states and controller flow;
- redesign visible command chrome with stronger hierarchy;
- make Fight the dominant visual action;
- add visually distinct focus and pressed states;
- reduce empty/filler look;
- keep action labels legible at native 256×192.

Move-selection redesign:
- preserve four move-slot mapping;
- preserve name/type/PP;
- preserve empty/disabled slots;
- strengthen selected-state frame and brightness contrast;
- strengthen type strip/badge readability;
- improve PP hierarchy;
- keep slot geometry compatible with touch hitboxes.

Optional Phase 1B enhancement:
- display physical/special/status category icon **only if** the existing battle data path exposes category cheaply and the UI can display it without invasive controller changes.
- If this requires risky battle-engine refactoring, defer and document.

Acceptance:
- command and move screens remain fully functional with D-pad/buttons and touch;
- no label clipping;
- no hitbox mismatch;
- readable in portrait and landscape emulator layouts;
- resource contracts and archive order remain valid.

### G7.2 — Battle top-screen HUD + dialog modernization

Primary surfaces:
- `res/graphics/battle/healthbox/`
- `res/graphics/windows/`
- `tools/visual_overhaul/generate_battle_ui.py`
- `tools/visual_overhaul/generate_ui_foundation.py`
- battle message/window call sites only if layout changes require source edits.

Required:
- rebuild normal player/enemy healthbox chrome with slimmer, cleaner visual weight;
- preserve HP/status colors and information;
- preserve player numeric HP;
- modernize battle text-window frame away from beige/olive retail feel;
- maintain original line capacity and text-printer behavior;
- retain Safari/special variants unless separately audited before modification.

Low-HP enhancement:
- audit whether a palette/state pulse can be implemented through existing healthbox update state;
- if safe, add a restrained non-strobing urgency pulse;
- if not safe, ship static visual improvement and defer pulse.

Acceptance:
- all single/double battle healthbox variants render;
- no HP/status/name/level overlap;
- message printer unchanged functionally;
- status colors remain distinguishable.

### G7.3 — Battle intensity hierarchy

Build on G5; do not rewrite its move-animation work.

Primary surfaces:
- battle transition code/resources;
- battle animation scripts;
- battle terrain/background resources;
- existing `Func_ShakeBg`, `Func_FadeBg`, battler motion and background-motion primitives;
- `tools/visual_overhaul/generate_battle_terrain.py`.

Create four presentation tiers:
- Tier 0 ordinary wild;
- Tier 1 ordinary trainer;
- Tier 2 Rival / Gym / Galactic Commander;
- Tier 3 Elite Four / Champion / major legendary.

Implementation strategy:
- identify the existing battle-type/trainer/event flags available at transition time;
- prefer palette/transition/background/staging differentiation over new renderer systems;
- keep ordinary fights restrained;
- reserve stronger flash/shake/grade treatment for Tier 2/3;
- do not globally increase shake on all damage;
- do not alter battle mechanics or AI.

Critical/super-effective/KO investigation:
- locate shared presentation hooks;
- add only short, bounded feedback if it can be isolated from damage calculation;
- do not modify damage, crit probability, type effectiveness, turn timing, or script branching;
- if no clean shared hook exists, document as deferred rather than hacking per-move behavior.

Acceptance:
- no change to battle results;
- no persistent background offset;
- no grade state leaks after animations;
- no unreadable flashes;
- normal battles remain less intense than bosses.

### G7.4 — Core menu modernization

Order:
1. Party
2. Summary
3. Bag
4. Start menu
5. Shop / secondary menus

Existing generators:
- `generate_party_menu_ui.py`
- `generate_summary_ui.py`
- `generate_bag_ui.py`
- `generate_start_menu_ui.py`
- `generate_shop_ui.py`
- `generate_ui_foundation.py`

#### Party
- strengthen selected member card;
- improve HP/status hierarchy;
- preserve member-ball/icon/touch semantics;
- keep existing cell/OAM geometry unless a layout change is demonstrably needed.

#### Summary
- modernize tab hierarchy;
- strengthen page section separation;
- make move/stat information dominant;
- keep contest/ribbon pages complete;
- strengthen move selection cursor.

#### Bag
- cleaner pocket identity;
- stronger item focus;
- clearer quantity/value hierarchy;
- preserve touch/pocket switching.

#### Start
- stronger icon focus state;
- more deliberate panel hierarchy;
- preserve all menu topology.

Acceptance:
- every touched menu works by buttons and touch;
- no page/function is removed;
- no text clipping at native scale;
- palette-bank exceptions remain respected.

### G7.5 — Global window / typography-adjacent polish

This is **not** a font replacement unless the font pipeline is first proven safe.

Work:
- message-box frame family audit;
- standard field/system frames;
- scroll cursor/wait dial;
- consistent panel outline/highlight language;
- optional per-context frame variants if current resource contract supports them cleanly.

Do not:
- shrink text for aesthetics;
- replace core font encoding blindly;
- change message speed/timing as part of visual work.

### G7.6 — Overworld atmosphere escalation

Foundation:
- existing G4/G6 lighting, fog, texture grades and camera work.

Priority environments:
1. Eterna/deep forest
2. Route 217/Snowpoint
3. Galactic interiors
4. Mt. Coronet/Spear Pillar
5. Distortion World
6. lakes/coastal routes
7. caves/Turnback

Allowed:
- stronger authored palette separation;
- safe fog tuning;
- existing field-effect reuse;
- selective dedicated resource slots where shared retail resources cause collateral recolors;
- small atmosphere emitters using proven resource paths.

Avoid:
- blind whole-map texture replacement;
- geometry churn;
- opaque NARC patching without a verified pipeline;
- making navigation harder.

Acceptance:
- player/NPC silhouettes remain readable;
- terrain/collision boundaries remain obvious;
- no map family accidentally inherits another area's grade;
- weather + fog remain coherent.

### G7.7 — Special encounter / boss polish

After ordinary battle and menu systems are stable:
- Rival;
- Gym Leaders;
- Galactic Commanders/Cyrus;
- Elite Four;
- Cynthia;
- major legendary encounters.

Use existing transition/background/grade/staging systems.
No gameplay changes.

Create a small matrix documenting:
- encounter class;
- visual tier;
- transition treatment;
- arena/background treatment;
- any special intro/impact treatment.

### G7.8 — Cohesion pass

Audit the game for remaining obvious retail-2009 visual islands:
- old beige/olive frames;
- inconsistent cursor language;
- unmodernized high-frequency menu chrome;
- palette mismatches between overworld, battle, and menus.

Only fix high-frequency or high-visibility inconsistencies. Do not churn obscure one-off screens without evidence.

## Reproducible asset policy

Every authored PNG/palette transformation that can be scripted should be generated from a deterministic tool under `tools/visual_overhaul/`.

For generator-backed assets:
- script is authority;
- generated output must be committed;
- rerunning the generator must produce no diff;
- do not hand-edit generated output without updating the generator.

Extend `.github/workflows/generate-visual-ui.yml` only when the new generator/output set is stable and safe for automatic regeneration.

## Resource safety rules

Before changing any Nitro visual resource, record:
- source path;
- dimensions;
- indexed palette size/bank;
- NCER/NANR relationship if present;
- whether geometry/cells/animation stay unchanged;
- archive/order contract;
- shared consumers.

For shared palettes, audit every consumer before changing an index.

For NSCR/cell/layout changes:
- preserve resource dimensions unless source code and build pipeline are updated together;
- preserve touch target semantics;
- verify both orientations via emulator screenshots.

## Source-code safety rules

When visual changes require C code:
- isolate them behind presentation helpers;
- never alter battle calculation state to drive cosmetics when a read-only state is available;
- never change save data structures for cosmetics;
- avoid new allocations in hot battle/field loops unless required;
- clean up any new animation/effect manager lifecycle explicitly;
- keep changes revision-agnostic.

## Validation plan

### Static/resource validation
For every batch:
- run relevant existing visual validators;
- run generator reproducibility checks;
- verify PNG/palette dimensions;
- verify JSON/cell/animation syntax;
- run `python3 tools/overhaul/validate_overhaul.py --no-write` after any code/resource integration that could affect the core tree.

### Build validation
Required:
- US Rev 0 ROM build;
- US Rev 1 ROM build;
- existing visual-format checks;
- visual asset export where applicable.

### Runtime review — owner
Runtime visual approval remains the owner's responsibility in a DS emulator on iPhone.

Capture both:
- portrait stacked;
- landscape side-by-side.

For each major screen, inspect:
- readability;
- touch accuracy;
- clipping;
- contrast;
- emulator-overlay conflict;
- animation state restoration.

Runtime review should report concrete defects with screenshots. Do not reopen stable source work for vague taste churn.

## Phase-specific QA checklist

Battle command:
- Fight/Bag/Pokémon/Run all selectable by touch and buttons.
- Cursor/focus follows actual selected action.
- Disabled states remain clear.

Moves:
- 1/2/3/4 move configurations.
- 0 PP.
- disabled move.
- long move names.
- type labels.
- optional category icon if implemented.

Healthboxes:
- player/enemy;
- singles/doubles;
- status condition;
- low HP;
- faint;
- level 100;
- long species names;
- genderless/gender markers.

Menus:
- full party / one Pokémon;
- fainted/statused party members;
- Bag pockets with long names/large quantities;
- every Summary page;
- Start menu with all unlocked entries.

Battle tiers:
- ordinary wild;
- ordinary trainer;
- Rival;
- Gym;
- Galactic;
- Elite Four/Champion;
- legendary.

## Deliverables

G7 implementation is complete only when the repo contains:

1. implemented source/assets;
2. deterministic generators for generated assets;
3. updated CI/generator wiring where needed;
4. `docs/visual_overhaul/G7_IMPLEMENTATION_REPORT.md`;
5. `docs/visual_overhaul/G7_RUNTIME_REVIEW_CHECKLIST.md`;
6. screenshots supplied by owner for any accepted runtime defects/fixes;
7. dual-revision build evidence;
8. no regression in core overhaul master validation.

## Implementation report requirements

The final report must state:
- exact files/systems changed;
- which changes are asset-only vs source-level;
- generator ownership;
- deferred ideas and why;
- build/run IDs;
- known runtime-only review items;
- explicit statement that gameplay mechanics were not intentionally changed.

## Stop / escalation conditions

Claude should stop and report a blocker only if:
- required visual asset/resource cannot be traced safely;
- a desired design requires changing battle mechanics or save format;
- a palette/resource is shared in a way that makes safe isolation unclear;
- a build fails for a reason that cannot be localized;
- the only way forward is opaque binary patching without a verified contract.

Do **not** stop for ordinary design choices already answered by the canonical design. Use the design document and this plan as authority.

## Recommended implementation sequencing

Execute in separate commits:

1. **G7.1A** command-menu audit + redesign
2. **G7.1B** move-selection redesign
3. **G7.2A** healthbox redesign
4. **G7.2B** battle text-window redesign
5. **G7.3** battle intensity hierarchy
6. **G7.4A** party + summary
7. **G7.4B** bag + start + shop
8. **G7.5** global window consistency
9. **G7.6** overworld atmosphere escalation
10. **G7.7** special encounter/boss pass
11. **G7.8** cohesion audit + documentation

Each commit must build or at minimum keep the tree in a buildable state. Do not accumulate a giant unvalidated asset dump.

## First implementation task

Begin with **G7.1A — battle command menu**.

Before editing:
1. trace the exact resources/code that draw the current Fight/Bag/Pokémon/Run interface;
2. document touch hitboxes and visual resource ownership;
3. identify whether the visible command panels are BG tilemaps, sprites, or a mixture;
4. compare current implementation against G7 design;
5. implement the redesign through the lowest-risk resource path;
6. preserve input semantics;
7. build Rev 0/Rev 1;
8. record the result before moving to G7.1B.

The existing screenshot-driven goal is clear: retain the large touch-friendly command surfaces, but make them look less like enlarged DS-era boxes and more like a deliberate modern command console.
