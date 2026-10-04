# G7 — Modern DS Remaster Implementation Plan

Status: **IMPLEMENTATION-READY**

Canonical design:
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md`

This plan is written for implementation by Claude Code or another repository-capable coding agent. It assumes current `main` already contains the completed gameplay overhaul, Pass G source-side visual work, and the visual-generation tooling under `tools/visual_overhaul/`.

## 0. Ground rules

Do not restart from retail assets.

Start from current `main`, preserving:
- G2C global UI foundation;
- G4 environment work;
- G5 battle presentation;
- G6 showcase integration;
- the current generated-asset pipeline;
- all gameplay-overhaul source.

The implementation must remain:
- ROM-side;
- DS-native;
- compatible with both US Rev 0 and US Rev 1;
- emulator-neutral;
- visually tested with phone-emulator layouts.

Do not modify gameplay balance, moves, species data, trainers, encounters, economy, or progression unless a visual feature absolutely requires a code-side presentation hook.

## 1. Branch strategy

Create:
`visual-overhaul-g7-modern-ds-remaster`

Base it on the latest `main`.

Use incremental commits by subsystem. Recommended order:

1. G7A battle UI audit + foundation
2. G7B command/move selector redesign
3. G7C battle top-screen HUD/text
4. G7D battle intensity hooks
5. G7E party/summary/bag/start-menu refresh
6. G7F overworld atmosphere escalation
7. G7G validation and integration

Do not mix unrelated gameplay fixes into this branch.

## 2. Mandatory discovery pass

Before editing, map the exact runtime/resource ownership of each target.

### Battle resource surfaces already confirmed

Assets:
- `res/graphics/battle/healthbox/`
- `res/graphics/battle/interface/`
- `res/graphics/battle/type_icons/`
- `res/graphics/windows/`
- `res/graphics/battle/terrain/`

Code:
- `src/battle/battle_controller.c`
- `src/battle/battle_controller_player.c`
- `src/battle/battle_system.c`
- `include/battle/`
- `src/battle_sub_menus/`
- `include/battle_sub_menus/`

Existing generator:
- `tools/visual_overhaul/generate_battle_ui.py`

### Core menu surfaces already confirmed

Party:
- `res/graphics/party_menu/`
- `tools/visual_overhaul/generate_party_menu_ui.py`
- `src/battle_sub_menus/battle_party*.c` for battle-party presentation/input
- locate non-battle party-menu owner before changing layout code

Summary:
- `res/graphics/pokemon_summary_screen/`
- `tools/visual_overhaul/generate_summary_ui.py`

Bag:
- `res/graphics/bag/`
- `tools/visual_overhaul/generate_bag_ui.py`

Start:
- `res/graphics/start_menu/`
- existing start-menu generator if present

Windows:
- `res/graphics/windows/`
- `tools/visual_overhaul/generate_ui_foundation.py`

### Discovery deliverable

Create:
`docs/visual_overhaul/G7_RESOURCE_AND_RUNTIME_AUDIT.md`

For each screen, record:
- source code owner;
- graphics archive/resource path;
- palette source;
- NCER/NANR/NSCR ownership;
- touch hitbox owner;
- text/window owner;
- whether layout is asset-only, data-driven, or code-positioned;
- safe edit class: palette-only / art-only / cell-animation / layout / runtime code.

Do not begin invasive layout edits until this audit exists.

## 3. G7A — Battle UI foundation

### Objective

Move the current battle HUD from "recolored Platinum" to a cohesive modern DS remaster interface.

### Healthboxes

Extend `generate_battle_ui.py`.

Required:
- retain resource dimensions and OAM contracts unless the audit proves a safe alternative;
- redesign pixel geometry, not only palette;
- cleaner outer silhouette;
- stronger inner rail separation;
- more compact empty chrome;
- preserve HP/status color semantics;
- preserve player numeric HP;
- preserve doubles behavior;
- separately design Safari if it remains on an independent palette contract.

Acceptance:
- no text overlap at longest practical species names;
- gender/level/status readable;
- HP bar unobstructed;
- singles/doubles/safari render correctly;
- no cell clipping.

### Battle cursor

Replace the current minimal corner treatment with a clearer focused-state language.

Target:
- visible at native resolution;
- not dependent on red alone;
- animation remains within current cell bounds unless deliberately re-authored and validated.

### Global battle text box

Audit which `res/graphics/windows/message_box_XX.png` style the battle system uses.

Create a dedicated G7 battle-frame treatment if the resource contract permits without unintended global dialog changes.

If battle and field share the same frame resource:
- either intentionally redesign the shared global frame coherently;
- or isolate the battle frame through a safe resource-selection change.

Do not silently change every message box because battle needs a new look.

## 4. G7B — Bottom-screen command center

This is the highest-impact work item.

### 4.1 Command menu

Locate:
- command button geometry;
- label rendering;
- touch rectangles;
- selected-state behavior;
- any sprite/tilemap resources.

Target composition:
- FIGHT visually dominant;
- BAG / RUN / POKÉMON secondary;
- preserve the four-command input semantics exactly.

Design requirements:
- larger-looking touch surfaces without shrinking functional hitboxes;
- stronger focus/pressed state;
- reduced dead space;
- dark structural frame with saturated action accents;
- crisp label readability at native resolution.

Input requirement:
- touch rectangles remain at least as forgiving as retail;
- D-pad/A/B navigation remains unchanged.

### 4.2 Move selector

Map the four move-slot render path.

Required visual content:
- move name;
- type;
- PP current/max;
- empty/disabled state;
- focus state.

Phase 1 target:
- stronger card silhouette;
- compact type badge/strip;
- clearer PP hierarchy;
- selected frame + luminance change;
- disabled move muted but legible.

Phase 1B optional enhancement:
- physical/special/status category icon.

Only implement category icons if:
- the move category is already available in the menu render state or can be obtained with a trivial lookup;
- no battle logic change is required;
- sprite/tile budget is safe;
- no text collision occurs.

If any of these fail, defer category icons and document why.

### 4.3 Battle target selector

Audit doubles target selection and ensure the new visual language does not obscure:
- ally/enemy target choice;
- fainted targets;
- invalid targets;
- multi-target moves.

## 5. G7C — Top-screen battle presentation

### 5.1 HUD hierarchy

After healthbox art is stable, tune position only if needed.

Do not move healthboxes merely for novelty.

Any position change must be checked against:
- large sprites;
- doubles;
- status icons;
- weather;
- long names;
- trainer battles.

### 5.2 Battle text treatment

Goal:
- cleaner, less beige/retail feel;
- preserve exact text capacity;
- preserve printer behavior and pacing.

Prefer art/palette changes over text engine changes.

### 5.3 Arena/background escalation

Build on `tools/visual_overhaul/generate_battle_terrain.py`.

Do not redo already-finished G5 families unless a G7 composition requires it.

Add only evidence-based stronger grades:
- rival/gym/elite/champion arena emphasis where resources allow;
- legendary/special arena contrast;
- nighttime depth;
- indoor/Galactic mood.

Keep sprite silhouettes readable.

## 6. G7D — Intensity systems

This phase adds contextual drama.

### 6.1 Low HP

Implement the least invasive readable effect.

Preferred order:
1. healthbox accent/palette pulse using existing palette animation capability;
2. subtle battle-interface accent;
3. only then consider code-driven palette cycling.

Constraints:
- no flashing faster than safe/readable cadence;
- do not obscure HP color;
- do not affect enemy HUD unless intentionally designed;
- easy to disable/revert if runtime behavior is unstable.

### 6.2 Critical hit / super-effective impact

Audit existing battle scripts and effect commands first.

Prefer:
- one-frame or short flash;
- selective base-background shake;
- existing sound timing;
- no global generic shake added to all hits.

Preserve G5's rule that move-specific staging remains selective.

### 6.3 KO

Use existing fade/motion/audio timing if a safe stronger presentation is possible.

Do not materially slow ordinary battles.

### 6.4 Battle-intro tiers

Implement only if the source already exposes a clean discriminator for battle class/trainer class/event type.

Desired hierarchy:
- ordinary wild;
- ordinary trainer;
- Rival / Commander / Gym;
- Elite Four / Champion / major legendary.

Possible implementation tools:
- alternate transition palette;
- existing transition effect selection;
- short fade color difference;
- arena emphasis;
- trainer-intro timing.

Do not add a large new transition subsystem unless the existing one is insufficient.

## 7. G7E — Core menus

Implement after battle UI is stable so the battle style becomes the visual reference.

### Party

Extend `generate_party_menu_ui.py`.

Targets:
- stronger card hierarchy;
- cleaner selected state;
- clearer HP/status separation;
- modernized touch buttons;
- preserve member order, touch layout, switch/use behavior.

### Summary

Extend `generate_summary_ui.py`.

Targets:
- stronger tab hierarchy;
- cleaner page chrome;
- move/stat data first;
- stronger move-selection cursor;
- preserve all pages, ribbons, contest data, status, markings, ball display.

Do not delete "old" systems merely because they are less important to the user.

### Bag

Extend `generate_bag_ui.py`.

Targets:
- stronger current-pocket identity;
- clearer item-row highlight;
- cleaner quantity/value hierarchy;
- more consistent chrome with battle/party/summary.

### Start menu

Modernize:
- cursor;
- icon treatment;
- selected state;
- frame/chrome.

Preserve menu order and touch behavior.

## 8. G7F — Overworld atmosphere escalation

Pass G already contains substantial environment work. G7 should not turn into a full map-art rewrite.

Prioritized targets:
1. Eterna/deep forest atmosphere;
2. Route 217/Snowpoint;
3. Galactic interiors;
4. Mt. Coronet/Spear Pillar;
5. Distortion World;
6. lakes/coastal routes;
7. caves.

Allowed changes:
- lighting;
- fog;
- palette/material grade;
- safe native field effects;
- camera tuning where already supported;
- selective texture polish with known resource ownership.

Avoid:
- blind NSBTX replacements;
- broad map geometry changes;
- collision-affecting edits;
- expensive effect density that risks DS performance.

## 9. G7G — Tooling and reproducibility

Every authored visual change must be reproducible.

Rules:
- generators remain source of truth for generated PNG/palette assets;
- do not hand-edit a generated asset without updating its generator;
- if a new generator is needed, place it under `tools/visual_overhaul/`;
- document palette-bank ownership and exceptions;
- preserve indexed PNG mode where required;
- preserve palette counts;
- preserve NCER/NANR contracts unless the implementation deliberately changes them.

Update `.github/workflows/generate-visual-ui.yml` to include any new generator outputs.

If the old workflow is branch-hardcoded, generalize it so it can run safely on the G7 branch or via manual dispatch without accidentally writing to the wrong branch.

## 10. Validation

### Static

Create:
`tools/visual_overhaul/validate_g7_modern_ds_remaster.py`

It should validate:
- expected assets exist;
- generated files are reproducible;
- indexed PNGs remain indexed;
- expected dimensions unchanged where contract-locked;
- palette sizes/banks intact;
- critical cell/animation JSON references remain valid;
- no missing order/meson entries;
- battle UI resources remain within expected geometry contracts;
- touch-coordinate tables are unchanged unless explicitly approved;
- G4/G5/G6 validators still pass.

### Build

Mandatory before merge:
- US Rev 0 build PASS;
- US Rev 1 build PASS;
- existing visual format check PASS;
- visual asset export PASS;
- master overhaul static validation still PASS 33/33.

### Runtime / visual review

User owns final runtime review.

Provide a short checklist with exact captures:
- wild battle command menu;
- wild move selector;
- trainer battle;
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
- portrait emulator layout;
- landscape emulator layout.

## 11. Rollout order and stop gates

### Stage 1 — Battle UI
Ship nothing else until:
- command menu works;
- move selector works;
- healthboxes work;
- battle text works;
- dual-revision builds pass.

### Stage 2 — Battle intensity
Proceed only after Stage 1 is visually approved.

### Stage 3 — Core menus
Party/summary/bag/start.

### Stage 4 — Overworld escalation
Only after UI language is coherent.

This prevents a large visual branch from becoming impossible to review.

## 12. Required implementation records

Create and maintain:
- `docs/visual_overhaul/G7_RESOURCE_AND_RUNTIME_AUDIT.md`
- `docs/visual_overhaul/G7_IMPLEMENTATION_LOG.md`
- `docs/visual_overhaul/G7_RUNTIME_REVIEW_CHECKLIST.md`

The implementation log must record:
- each changed resource;
- generator owning it;
- runtime owner;
- why it changed;
- contract preserved/changed;
- build result;
- visual-review status.

## 13. Explicit preservation rules

Do not regress:
- Pass B restored species data;
- C1/C2/C2.5/C3;
- D1-D8 gameplay work;
- reusable TMs/HMs;
- breeding;
- trainer/postgame changes;
- Mystery Starter;
- Pass G environment and battle work.

Before merge run:
`python3 tools/overhaul/validate_overhaul.py --no-write`

Expected:
`MASTER VALIDATION: PASS (33/33 children passed)`

## 14. Definition of done

G7 source work is complete when:

- battle command/move UI is visibly redesigned, not merely recolored;
- healthboxes/text/windows use the new cohesive language;
- at least one contextual intensity system is implemented safely;
- party/summary/bag/start menu share the same language;
- Pass G environments remain intact and selected atmosphere targets are strengthened;
- all generators are reproducible;
- G7 validator passes;
- Rev 0 and Rev 1 builds pass;
- master gameplay static validation remains 33/33;
- the runtime checklist is ready for the user.

Runtime screenshots can then drive subjective polish without reopening the architecture.
