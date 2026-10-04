# Pass H — Modern DS Remaster Implementation Plan

Status: **implementation-ready**

Companion design authority:
- `docs/visual_overhaul/PASS_H_MODERN_DS_REMASTER_DESIGN.md`

Starting authority:
- current `main` after post-recovery static validation
- Pass G source-side visual work already present on `main`
- do **not** restart from retail assets
- do **not** use historical `visual-overhaul-g2a` as the implementation base

---

# 0. Implementation contract

The implementer must treat this as a ROM-side Nintendo DS overhaul.

Primary runtime target is a DS emulator on iPhone, but:
- no emulator-specific code;
- no external skin dependency;
- no texture pack;
- no shader dependency;
- no post-processing dependency.

Every phase must preserve:
- gameplay behavior;
- script progression;
- save format;
- battle mechanics;
- resource ordering unless a deliberate audited expansion is required;
- US Rev 0 + US Rev 1 buildability.

The user owns runtime QA. Claude should complete source work, source audits, generators, static validation, and dual-revision build evidence. Do not mark subjective runtime appearance as verified without user evidence.

---

# 1. Existing foundation — retain and extend

Before changing anything, read:

- `docs/visual_overhaul/PASS_G_VISUAL_OVERHAUL.md`
- `docs/visual_overhaul/G5_BATTLE_PRESENTATION_COMPLETE.md`
- `docs/visual_overhaul/G6_SHOWCASE_INTEGRATION_COMPLETE.md`
- `docs/visual_overhaul/PASS_G_DELTA_REVIEW_CHECKLIST.md`
- `docs/visual_overhaul/PASS_H_MODERN_DS_REMASTER_DESIGN.md`

Existing generators to retain:
- `tools/visual_overhaul/generate_ui_foundation.py`
- `tools/visual_overhaul/generate_start_menu_ui.py`
- `tools/visual_overhaul/generate_battle_ui.py`
- `tools/visual_overhaul/generate_party_menu_ui.py`
- `tools/visual_overhaul/generate_summary_ui.py`
- `tools/visual_overhaul/generate_bag_ui.py`
- `tools/visual_overhaul/generate_shop_ui.py`
- `tools/visual_overhaul/generate_battle_terrain.py`

Existing battle-presentation work to retain:
- G5 battle terrain palettes;
- G5 special arena palettes;
- G5 Frontier arena palettes;
- existing move-impact `Func_ShakeBg(..., SHAKE_BG_TARGET_BASE)` edits;
- existing scene-grade color specialization;
- existing weather-presentation alignment.

Existing environment work to retain:
- G4 lighting families;
- fog/weather tuning;
- Eterna Forest camera and atmosphere;
- Snowpoint / Route 217;
- Distortion World;
- Spear Pillar;
- lakes;
- Turnback Cave;
- Galactic interiors;
- G6 showcase validators.

Do not undo those systems merely to establish a new visual identity.

---

# 2. Branch / PR strategy

Use current `main` as the base.

Recommended branch sequence:

1. `visual/pass-h-h0-surface-audit`
2. `visual/pass-h-h1-battle-ui`
3. `visual/pass-h-h1-battle-intensity`
4. `visual/pass-h-h2-core-menus`
5. `visual/pass-h-h3-overworld-atmosphere`
6. `visual/pass-h-h4-encounter-presentation`
7. `visual/pass-h-h5-integration-polish`

If implementation is kept on one long-lived branch, commits must still be phase-separated so regressions can be bisected.

Do not mix gameplay-balance changes into Pass H PRs.

---

# 3. H0 — Source/resource ownership audit

## Goal

Map the exact source/resource owner of every target screen before layout changes.

This is required because Pass G confirmed many editable UI resources but did not fully map all lower-screen battle-command artwork and state logic.

## H0.1 Battle UI ownership

Audit:
- `res/graphics/battle/healthbox/`
- `res/graphics/battle/interface/`
- `res/graphics/battle/type_icons/`
- battle UI loading code;
- lower-screen command menu resource loading;
- lower-screen move menu resource loading;
- command selection state;
- move selection state;
- touch hitboxes;
- cursor state;
- Cancel button;
- category/type icon capabilities;
- Safari/double-battle variants.

Find the exact source for:
- FIGHT panel;
- BAG panel;
- RUN panel;
- POKÉMON panel;
- lower-screen neutral background;
- move cards;
- move type badge;
- PP display;
- selected/pressed state;
- empty move slots.

Do not assume these live in `res/graphics/battle/interface/` until verified.

### H0 battle audit deliverable

Create:
- `docs/visual_overhaul/PASS_H_H0_BATTLE_UI_SURFACE_AUDIT.md`

For each resource:
- path;
- compiled format;
- dimensions;
- palette bank;
- cell/animation relationship;
- owning source function;
- touch geometry owner;
- safe edit class:
  - palette-only;
  - pixel-safe;
  - cell-safe;
  - layout-code required;
  - opaque / defer.

## H0.2 Battle top-screen ownership

Map:
- healthbox resources and palette banks;
- battle message window/frame;
- battle text printer;
- HP bar graphics/state colors;
- status display;
- trainer/Pokémon entrance code;
- faint/KO display sequence;
- critical/super-effective/resisted presentation code;
- battle transition routing by encounter type.

Deliverable:
- same H0 audit, top-screen section.

## H0.3 Core menu ownership

Audit exact resource + code ownership for:
- Start menu;
- Party menu;
- Summary;
- Bag;
- Shop;
- Pokédex;
- PC boxes if source-backed and practical.

Known source-backed directories:
- `res/graphics/start_menu/`
- `res/graphics/party_menu/`
- `res/graphics/pokemon_summary_screen/`
- `res/graphics/bag/`
- `res/graphics/shop_menu/`
- `res/graphics/windows/`

Deliverable:
- `docs/visual_overhaul/PASS_H_H0_MENU_SURFACE_AUDIT.md`

## H0.4 Transition/encounter audit

Map:
- wild battle transition;
- ordinary trainer transition;
- Rival;
- Gym Leader;
- Galactic Commander/Cyrus;
- Elite Four;
- Champion;
- Legendary/Mythical encounters;
- any encounter-type enum or transition dispatch table.

Document what can be varied by class without invasive story scripting.

Deliverable:
- `docs/visual_overhaul/PASS_H_H0_ENCOUNTER_PRESENTATION_AUDIT.md`

## H0 gate

Do not begin layout-changing H1 work until:
- battle command resources are identified;
- touch geometry is identified;
- move-card resource/state ownership is identified;
- build path for edited assets is known.

Palette-only research may occur in parallel.

---

# 4. H1 — Battle UI redesign

This is the highest-priority implementation phase.

## H1A — reusable visual token generator

Create a shared module such as:

- `tools/visual_overhaul/pass_h_style.py`

It should define reusable authored colors/ramps:
- deep navy/near-black;
- graphite;
- steel/slate;
- cool white;
- silver highlight;
- electric-blue focus;
- gold focus/important state;
- command accents;
- disabled ramp.

Generators should import these shared values rather than duplicating RGB constants.

Keep resource-specific palette constraints explicit.

## H1B — battle healthboxes

Extend:
- `tools/visual_overhaul/generate_battle_ui.py`

Targets:
- player singles;
- player doubles;
- enemy;
- healthbox parts;
- Safari;
- battle cursor;
- arrow/focus assets where compatible.

### Required behavior

Preserve:
- HP green/yellow/red;
- status colors;
- text contrast;
- HP depletion behavior;
- OAM/cell contract unless H0 proves safe changes.

Design result:
- cleaner silhouette;
- more authored frame;
- reduced “retail recolor” feel;
- stronger name/level grouping;
- visually consistent doubles and Safari variants.

If pixel geometry must change, regenerate only within existing NCGR dimensions first.

## H1C — battle message window

Audit whether the battle message frame uses:
- global windows;
- a battle-specific window;
- frame selection logic.

Implement a modern dark/cool-neutral battle frame while preserving:
- printable region;
- line count;
- text width;
- printer behavior;
- wait cursor.

Do not shrink the text area without a full text-overflow audit.

## H1D — command deck

After H0 identifies the exact assets/code:

Redesign:
- FIGHT;
- BAG;
- RUN;
- POKÉMON;
- neutral bottom-screen background.

### Art direction

- dark-neutral command deck background;
- FIGHT = crimson accent;
- BAG = amber/gold;
- RUN = cyan/blue;
- POKÉMON = green;
- reduce thick black retail bevel;
- add crisp inner highlight;
- selected state = bright edge/value lift;
- pressed state = brief compression/darker inset if state exists;
- labels centered well inside emulator-safe region.

### Geometry

First implementation preference:
1. preserve touch rectangles;
2. preserve button footprints;
3. replace art/palette;
4. only change geometry if H0 proves source-controlled layout and touch coordinates can be updated together.

Never move visible button art without moving its touch target.

## H1E — move-card deck

Redesign the move menu into four modern action cards.

Required display:
- name;
- type;
- current/max PP;
- empty-state;
- selected-state.

Optional, only if H0 proves a clean path:
- physical/special/status category icon.

### Category icon rule

Do not implement category icons by:
- stealing text glyph positions;
- reducing move-name capacity;
- hardcoding per-move labels in art.

Only add them if there is a proper runtime value-to-icon path.

### Move-card palette rule

Do not fill the full card with saturated type color.

Use:
- dark-neutral base;
- type-colored badge/accent rail;
- selected bright frame;
- high-contrast text.

## H1F — battle static validator

Create:
- `tools/visual_overhaul/validate_pass_h_battle_ui.py`

Check at minimum:
- edited PNG dimensions unchanged unless manifest says otherwise;
- indexed mode retained where required;
- palette count/bank size valid;
- required transparent index preserved;
- healthbox HP/status palette entries preserved;
- animation/cell JSON references remain valid;
- command/move touch geometry matches visual geometry if layout changed;
- resource order unchanged unless explicitly manifested.

Create manifest:
- `docs/visual_overhaul/pass_h_battle_ui_manifest.json`

---

# 5. H1.5 — Battle intensity expansion

This phase enhances encounter feel without changing mechanics.

## H1.5A — critical hit presentation

Audit the battle script/event path for critical-hit message/effect timing.

Desired:
- one short, distinct visual punctuation;
- stronger than ordinary hit;
- less than boss transition;
- no added gameplay delay if avoidable.

Possible source-safe tools:
- short palette flash;
- existing screen shake;
- existing hit effect;
- message-frame accent.

Do not add a generic long animation.

## H1.5B — super-effective / resisted feedback

Goal:
- make effectiveness readable visually before/with text;
- preserve existing battle messaging.

Preferred:
- subtle short accent;
- no giant UI banner;
- no mechanics change.

## H1.5C — faint / KO punctuation

Audit current faint sequence.

Possible improvement:
- stronger brief fade/grade;
- better timing around existing cry/sprite drop;
- restrained arena reaction for important encounters only.

Keep ordinary battles fast.

## H1.5D — battle entry hierarchy

Implement encounter-class tiers only after H0 transition audit.

Order:
1. Rival;
2. Gym Leader;
3. Galactic Commander/Cyrus;
4. Elite Four;
5. Champion;
6. flagship Legendary encounters.

Ordinary wild/trainer transitions remain fast controls.

## H1.5E — static validator

Add source assertions for:
- encounter class routing;
- no gameplay-script changes outside approved visual hooks;
- no global effect accidentally applied to ordinary encounters.

---

# 6. H2 — Core menu modernization

Do this only after H1 visual tokens are stable.

## H2A — global windows

Extend:
- `generate_ui_foundation.py`

Targets:
- standard system;
- standard field;
- scroll cursor;
- wait dial;
- selected message-box families where safe.

Goal:
- coherent dark-neutral/cool-white system language;
- field/dialogue windows may retain contextual lighter treatment;
- remove remaining beige/brown retail feel.

Do not blindly overwrite all `message_box_00..19`; first identify purpose and palette sharing.

## H2B — Start menu

Extend:
- `generate_start_menu_ui.py`

Targets:
- cursor;
- menu palette;
- icons if a modern silhouette can be achieved without losing recognition.

Preserve:
- menu ordering;
- interaction logic;
- icon cell/animation contracts unless audited.

## H2C — Party menu

Extend:
- `generate_party_menu_ui.py`

Go beyond cursor/button cleanup:
- member-card panels;
- selected-card hierarchy;
- HP/status scanability;
- empty slots;
- touch button presentation;
- held-item/status clarity.

Potential files:
- `menu_tiles.png`;
- `menu.pal`;
- `menu.NSCR`;
- `menu_panels.NSCR`;
- `subscreen_tiles.png`;
- `subscreen.pal`;
- `touch_button.png`;
- existing cursor/button resources.

Any NSCR layout edit must be explicit and validated.

## H2D — Summary screen

Extend:
- `generate_summary_ui.py`

This is a showcase screen.

Targets:
- tabs;
- page chrome;
- status/skills/moves grouping;
- move cursor;
- move display consistency with battle;
- cleaner stat hierarchy;
- type/ability emphasis.

Preserve every existing data field.

Potential files:
- `tiles_main.png`;
- `tiles_main.pal`;
- `tiles_sub.png`;
- `tiles_sub.pal`;
- `tabs.png`;
- `tab_arrow.png`;
- page NSCR files;
- cursor resources.

## H2E — Bag

Extend:
- `generate_bag_ui.py`

Targets:
- main tileset;
- pocket header;
- item row;
- selected item;
- pocket selector;
- action buttons;
- counts/money hierarchy where applicable.

## H2F — Shop

Extend:
- `generate_shop_ui.py`

Match Bag visual language.

## H2G — menu validator

Create:
- `tools/visual_overhaul/validate_pass_h_core_ui.py`

Check:
- dimensions;
- indexed palette contracts;
- palette bank counts;
- NSCR file sizes where unchanged;
- animation/cell references;
- generator idempotence;
- no unexpected resource-order diffs.

---

# 7. H3 — Overworld atmosphere expansion

Pass G showcase scenes are the benchmark, not the entire target.

## H3A — environment-family audit

Build a map-family manifest:
- temperate;
- forest;
- cave;
- snow;
- coast;
- urban;
- industrial/Galactic;
- mountain;
- ancient/legendary;
- Distortion.

Create:
- `docs/visual_overhaul/pass_h_environment_family_manifest.json`

Each area should record:
- area-data;
- texture set;
- lighting set;
- weather;
- camera;
- special renderer/fog;
- proposed Pass H treatment;
- shared-resource risk.

## H3B — time-of-day strengthening

Use area-light architecture first.

Do not globally darken all nights.

Tune by family:
- dawn hue;
- day contrast;
- evening warmth/cool shadow;
- night depth.

New lighting sets are allowed when shared retail sets would cause unrelated maps to change.

## H3C — selective texture/material grade

Use existing reproducible tooling patterns.

Rules:
- never blind-recolor unknown key/material colors;
- preserve texel indices unless deliberately rebuilding a resource;
- isolate shared texture sets before applying location-specific grades;
- validate resource ordering.

## H3D — ambient effects

Use bounded native systems.

Candidate effects:
- forest motes/leaves;
- summit wind/snow;
- cave dust;
- coastal shimmer;
- Galactic energy accents;
- Distortion ambient particles.

Every effect needs:
- bounded actor/resource count;
- cleanup path;
- map guard;
- no unbounded allocations;
- source/static validation.

## H3E — camera accents

Only for showcase or arrival moments.

No global field-camera overhaul.

---

# 8. H4 — Special encounter presentation

## H4A — class-based intro manifest

Create:
- `docs/visual_overhaul/pass_h_encounter_presentation_manifest.json`

Entries:
- ordinary wild;
- ordinary trainer;
- Rival;
- Gym Leader;
- Galactic Commander;
- Cyrus;
- Elite Four;
- Champion;
- Legendary/Mythical flagship groups.

For each:
- transition;
- palette/grade;
- intro duration;
- sound dependency if any;
- source path;
- fallback behavior.

## H4B — Rival

Direction:
- fast;
- energetic;
- strong contrast;
- no excessive ceremony.

## H4C — Gym

Direction:
- stronger start beat;
- Gym/badge progression feel;
- can share a base transition with leader-specific palette accent.

## H4D — Galactic

Direction:
- steel/cyan/violet;
- sharper, more threatening;
- preserve Galactic identity already present in environment grading.

## H4E — Elite / Champion

Build on G5 arena-specific palettes.

Champion should be the strongest non-Legendary trainer presentation.

## H4F — Legendary

Prioritize:
- Dialga;
- Palkia;
- Giratina;
- Arceus;
- Darkrai;
- Shaymin;
- major static Legendary encounters.

Do not make every legacy habitat encounter use the same expensive flagship transition unless routing makes it appropriate.

---

# 9. H5 — Transitions and final integration

## H5A — menu transitions

Audit first.

If source-safe:
- brief panel slide/fade;
- focus transition;
- no slow animation tax.

## H5B — battle/menu cohesion

Verify:
- healthbox chrome;
- global windows;
- party;
- summary;
- bag/shop;
- battle command deck

all use the same Pass H token language without becoming monochrome.

## H5C — special-area cohesion

Verify G6 showcases still read correctly against the stronger Pass H UI.

## H5D — no-holdout audit

Create a visual holdout report:
- retail beige/brown frames still visible;
- old olive healthbox variants;
- inconsistent cursor styles;
- screens with obviously untouched retail chrome;
- special modes such as Safari/doubles;
- secondary menus.

Classify each:
- fix in H5;
- intentionally retained;
- deferred due resource risk.

Deliverable:
- `docs/visual_overhaul/PASS_H_HOLDOUT_AUDIT.md`

---

# 10. Reproducibility requirements

Every authored asset change should have one of:

1. source PNG/PAL/JSON committed directly and intentionally edited; or
2. deterministic generator script that reproduces it.

Prefer generator ownership when:
- a palette is shared across multiple previews/resources;
- multiple assets must stay synchronized;
- a style token is reused;
- a resource is likely to need later tuning.

Generators must be idempotent:
- run twice;
- second run produces no diff.

Do not create overlapping generators that both own the same file.

---

# 11. Validation plan

## Per-phase static checks

At minimum:
- Python syntax for new tools;
- generator execution;
- generator idempotence;
- resource-format validation;
- targeted validators;
- existing visual validators where affected.

## Integration checks

Run:
- existing Pass G/G6 validators;
- Pass H validators;
- main project master validation where practical;
- normal US Rev 0 build;
- normal US Rev 1 build.

If a visual change touches source code used by runtime-symbol QA:
- run corresponding debug/runtime-symbol workflow too.

## Required no-regression checks

Pass H must not break:
- 33/33 overhaul master static validation;
- species/moves/evolution;
- C1/C2/C2.5/C3;
- D1-D8 source contracts;
- availability;
- breeding;
- events;
- postgame;
- Mystery Starter;
- save format.

---

# 12. Runtime handoff package

The user will perform runtime visual QA.

Claude should provide a concise test matrix after each major phase.

For H1:
- ordinary wild day/night;
- ordinary trainer;
- Rival;
- doubles;
- Safari if accessible;
- move menu with 1/2/4 populated moves;
- low HP;
- status;
- long move names;
- portrait emulator layout;
- landscape emulator layout.

For H2:
- full party;
- one Pokémon party;
- statused Pokémon;
- summary pages;
- bag with long item names;
- shop;
- start menu.

For H3/H4:
- Eterna Forest;
- Snowpoint;
- Route 217;
- Distortion World;
- Spear Pillar;
- Galactic interior;
- Gym Leader;
- Elite Four;
- Champion;
- flagship Legendary.

Claude must not mark runtime appearance PASS from static evidence.

---

# 13. Implementation order and stop conditions

## Recommended order

### H0
Audit exact ownership.

### H1.1
Battle visual tokens + healthboxes + battle message frame.

### H1.2
Command deck.

### H1.3
Move-card deck.

### H1.4
Battle-state static validator.

### H1.5
Critical/effectiveness/faint/encounter intensity.

### H2
Core menus.

### H3
Overworld atmosphere expansion.

### H4
Special encounter presentation.

### H5
Holdout cleanup + integration.

Do not begin H3/H4 while H1/H2 generators have overlapping ownership or unresolved resource-contract failures.

## Real blockers

Stop and report only when:
- resource ownership cannot be identified;
- an archive is opaque and cannot be safely reconstructed;
- a layout change requires unknown touch geometry;
- a required asset conversion cannot be reproduced;
- build/resource limits are exceeded;
- runtime evidence is necessary to choose between two visually plausible values.

Do not stop for:
- routine palette decisions;
- obvious generator refactors;
- formatting;
- straightforward validator updates;
- minor implementation details covered by the design spec.

---

# 14. Definition of source-side complete

Pass H is source-side complete when:

- H0 audits exist;
- H1 battle UI is implemented;
- H1 battle intensity hooks are implemented where source-safe;
- H2 core menus share the Pass H language;
- H3 environment-family pass is implemented for approved targets;
- H4 encounter hierarchy is implemented for approved classes;
- H5 holdout audit is resolved;
- generators are deterministic;
- Pass H validators pass;
- existing visual validators pass;
- overhaul master validation remains green;
- US Rev 0 builds;
- US Rev 1 builds;
- no runtime claim is made beyond available evidence.

At that point the project status becomes:

> **PASS H SOURCE-COMPLETE — USER RUNTIME VISUAL QA PENDING.**

---

# 15. First Claude execution batch

The first implementation session should **not** attempt all of Pass H.

It should complete:

1. H0 battle UI ownership audit;
2. H0 top-screen battle ownership audit;
3. shared Pass H style-token module;
4. H1B healthbox/Safari modernization;
5. H1C battle message-frame modernization if ownership is confirmed;
6. H1D command-deck implementation if ownership/touch geometry is confirmed;
7. H1E move-card implementation if ownership is confirmed;
8. Pass H battle UI validator;
9. Rev 0 + Rev 1 builds;
10. implementation report.

If command/move resources prove opaque, complete the audited safe H1 subset and document the exact blocker instead of guessing.

### First-batch deliverables

Create:
- `docs/visual_overhaul/PASS_H_H0_BATTLE_UI_SURFACE_AUDIT.md`
- `docs/visual_overhaul/PASS_H_H1_BATTLE_UI_IMPLEMENTATION_REPORT.md`
- `docs/visual_overhaul/pass_h_battle_ui_manifest.json`
- `tools/visual_overhaul/pass_h_style.py`
- `tools/visual_overhaul/validate_pass_h_battle_ui.py`

Update existing generators rather than creating redundant owners where possible.

---

# 16. Design authority

If implementation discovers that a requested effect is not technically viable on the current Platinum resource path:

1. preserve the visual goal;
2. use the nearest native Platinum technique;
3. document the deviation;
4. do not silently substitute a different aesthetic;
5. do not weaken the entire Pass H direction to preserve retail authenticity.

Technical constraints may change the implementation.

They do **not** change the target:
**modern, intense, immersive, premium DS presentation for iPhone emulator play.**
