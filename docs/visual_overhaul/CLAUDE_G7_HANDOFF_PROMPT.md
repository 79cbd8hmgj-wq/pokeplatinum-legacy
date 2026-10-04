# Claude Code Handoff — G7 Modern DS Remaster

Use this prompt verbatim or with only repository-path adjustments.

---

You are implementing **G7 — Modern DS Remaster** in:

`79cbd8hmgj-wq/pokeplatinum-legacy`

Start from the latest `main`.

Read these files first and treat them as canonical:

1. `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md`
2. `docs/visual_overhaul/G7_IMPLEMENTATION_PLAN.md`
3. `docs/visual_overhaul/PASS_G_VISUAL_OVERHAUL.md`
4. `docs/visual_overhaul/G5_BATTLE_PRESENTATION_COMPLETE.md`
5. `docs/visual_overhaul/G6_SHOWCASE_INTEGRATION_COMPLETE.md`
6. `docs/overhaul/STATUS.md`

Also inspect the existing visual generators under:

`tools/visual_overhaul/`

especially:
- `generate_battle_ui.py`
- `generate_ui_foundation.py`
- `generate_party_menu_ui.py`
- `generate_summary_ui.py`
- `generate_bag_ui.py`
- `generate_battle_terrain.py`

## Goal

Push the current source-side visual overhaul beyond conservative Platinum polish into a **premium modern DS remaster** that looks and feels substantially more modern, immersive, and intense when played through a Nintendo DS emulator on iPhone.

Do **not** build a fake native iOS UI.

The ROM must remain:
- Nintendo DS-native;
- dual-screen;
- touch-capable;
- emulator-neutral;
- entirely ROM-side;
- compatible with US Rev 0 and US Rev 1.

The intended visual philosophy is:

> Top screen = cinematic play space. Bottom screen = touch-first command center.

The game should still be recognizable as Platinum, but it should no longer look like an untouched 2009 DS game.

## Non-negotiable constraints

Do not regress or reopen gameplay-overhaul design.

Preserve:
- Pass A/B Pokémon changes;
- C1/C2/C2.5/C3;
- D1-D8 gameplay work;
- Mystery Starter behavior;
- current availability/economy/breeding/trainer/postgame systems;
- existing Pass G environment and battle work.

Do not change gameplay values as part of this task.

Do not overwrite current visual work with retail assets.

Do not use:
- external texture packs;
- emulator shaders;
- iPhone-specific assets;
- assumptions about one emulator skin or one screen orientation.

Design must hold up in:
- portrait stacked layout;
- landscape side-by-side layout;
- native-resolution readability;
- touch-overlay conditions.

## First task: discovery, not redesign

Create a branch:

`visual-overhaul-g7-modern-ds-remaster`

Then perform the mandatory audit from the plan and create:

`docs/visual_overhaul/G7_RESOURCE_AND_RUNTIME_AUDIT.md`

For battle command UI, move selection, healthboxes, battle text, party, summary, bag, start menu, and target selection, identify:

- source-code owner;
- graphics resource path;
- palette owner;
- NCER/NANR/NSCR owner;
- touch hitbox owner;
- label/text owner;
- layout owner;
- safe edit class:
  - palette-only
  - art-only
  - cell/animation
  - layout
  - runtime code

Do not guess. Trace actual call/resource ownership.

## Implementation order

Follow this exact sequence unless a real technical blocker requires reordering:

### G7A — Battle UI foundation
- redesign healthbox pixel geometry, not just colors;
- preserve all HP/status/name/level information;
- redesign battle cursor/focus language;
- isolate or intentionally redesign the battle text-frame treatment.

### G7B — Bottom-screen command center
This is the highest-priority visual work.

Command menu:
- FIGHT remains dominant;
- BAG / RUN / POKÉMON secondary;
- stronger focus and pressed states;
- less dead space;
- preserve D-pad and touch semantics.

Move selector:
- visibly redesign four move cards;
- preserve move name, type, PP, empty/disabled state;
- stronger selected state;
- clearer type/PP hierarchy.

Optional:
- add physical/special/status icon only if move category is trivially available and the resource budget is safe.

Do not destabilize the menu to force that icon.

### G7C — Top-screen battle presentation
- modernize healthbox/text-window composition;
- strengthen arena contrast only where needed;
- retain G5 battle-terrain and move-staging work.

### G7D — Contextual intensity
Implement at least one safe contextual intensity feature.

Preferred order:
1. low-HP HUD accent/pulse;
2. critical/super-effective impact accent;
3. KO presentation;
4. battle-intro tiering.

Use existing battle systems and scripts where possible.
Do not add generic global shake to every hit.

### G7E — Core menus
Use the battle UI as the visual reference language.

Refresh:
- party;
- summary;
- bag;
- start menu.

Do not delete legacy functions/pages.

### G7F — Overworld atmosphere escalation
Build on Pass G rather than replacing it.

Prioritize:
- Eterna/deep forest;
- Route 217/Snowpoint;
- Galactic interiors;
- Mt. Coronet/Spear Pillar;
- Distortion World.

Prefer:
- lighting;
- fog;
- palette/material grade;
- safe field effects;
- camera tuning already supported by the engine.

Avoid broad blind binary resource replacement.

### G7G — Validation
Create:

`tools/visual_overhaul/validate_g7_modern_ds_remaster.py`

Validate contracts, dimensions, indexed resources, palette structure, generator reproducibility, resource references, and relevant touch-layout invariants.

## Generator rule

Every generated visual asset must remain reproducible.

If you change a generated PNG/palette:
- update the generator;
- regenerate the asset;
- do not leave a manual asset edit with stale generator output.

If needed, update:
`.github/workflows/generate-visual-ui.yml`

Be careful: the old workflow may be branch-hardcoded. Generalize it safely instead of making it write to the wrong branch.

## Validation gates

Before asking for review:

Run all relevant visual validators, plus:

`python3 tools/overhaul/validate_overhaul.py --no-write`

The gameplay master validator must remain:

`MASTER VALIDATION: PASS (33/33 children passed)`

Also require:
- US Rev 0 build PASS;
- US Rev 1 build PASS;
- format-visual-overhaul PASS;
- visual-asset-export PASS;
- G7 validator PASS.

## Runtime handoff

The user is handling runtime testing.

Create:

`docs/visual_overhaul/G7_RUNTIME_REVIEW_CHECKLIST.md`

Include exact screenshot/test cases for:
- wild command menu;
- wild move selector;
- trainer;
- doubles;
- low HP;
- status;
- long species name;
- Rival;
- Gym;
- Elite Four/Champion;
- legendary;
- party;
- summary;
- bag;
- start menu;
- Eterna;
- Route 217;
- Galactic interior;
- Distortion World;
- portrait layout;
- landscape layout.

## Work style

Do not stop for minor confirmations.

Use your technical judgment and continue through the implementation plan unless you hit a **real blocker** requiring user choice.

When you encounter a visual decision with multiple equally valid options, choose the option that best satisfies:

1. readability on iPhone emulator;
2. stronger modern hierarchy;
3. immersive/intense feel;
4. DS-native feasibility;
5. preservation of gameplay/input semantics.

Commit incrementally.

At the end, report:
- what changed;
- files/resources touched;
- generator changes;
- validation results;
- any deferred items;
- what the user should test first in the emulator.
