# Claude Code Prompt — G7.6 Overworld Atmosphere Escalation

Work on exactly one complete numbered section: **G7.6 — Overworld Atmosphere Escalation** in `pokeplatinum-legacy`.

Start from current `main`.

Before implementation, read only:
- `docs/visual_overhaul/G7_CLAUDE_EXECUTION_PROTOCOL.md`
- `docs/visual_overhaul/G7_MODERN_DS_REMASTER_DESIGN.md`
- only the **G7.6** section of `docs/visual_overhaul/G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md`
- `docs/visual_overhaul/G7_CLAUDE_HANDOFF.md`
- `docs/visual_overhaul/G4_ENVIRONMENT_RECONSTRUCTION_COMPLETE.md`
- `docs/visual_overhaul/G6_SHOWCASE_INTEGRATION_COMPLETE.md`

Then read the specific G4 environment report only when you reach that environment:
- Eterna: `G4A_ETERNA_FOREST.md`
- Snow: `G4B_SNOW_ENVIRONMENT.md` and/or `G4B_SNOW_REGION.md`
- Distortion: `G4C_DISTORTION_WORLD.md`
- Coronet/Spear/lakes/caves remainder: `G4D_G4F_SHOWCASE_ENVIRONMENTS.md`
- Galactic interiors: `G4G_GALACTIC_INTERIORS.md`

Treat these documents and the current source tree as authority. Do not reconstruct old G4/G6 work from chat history or broad repository archaeology.

## Scope

Complete **all of G7.6** in this session.

Priority environment groups, in this order:
1. Eterna / deep forest
2. Route 217 / Snowpoint
3. Galactic interiors
4. Mt. Coronet / Spear Pillar
5. Distortion World
6. lakes / coastal routes
7. caves / Turnback Cave

Do **not** continue to G7.7 after G7.6 is complete.

Use/create:
`visual/g7-modern-ds-remaster`

If that branch exists, verify it is clean and based on current `main` before editing.

## Token and time discipline

Use targeted searches:
- `rg`
- `git grep`
- `find`
- narrow `sed -n`, `head`, `tail`

Do not:
- recursively dump large resource trees;
- read large unrelated source files in full;
- rerun old archaeology already documented in G4/G6 reports;
- narrate routine shell commands;
- repeatedly open the same reports;
- run full ROM builds between environment groups.

Before deep implementation, spend one focused audit pass identifying ownership and shared-resource risk for all seven environment groups.

If one environment remains unclear, isolate that investigation instead of restarting the whole audit.

## Foundation to preserve

G7.6 is an **escalation of the existing G4/G6 environment work**, not a replacement.

Preserve:
- existing G4 lighting grades;
- existing fog decisions;
- existing texture recolors;
- existing dedicated resource-slot decisions;
- existing G6 showcase integration;
- map geometry;
- collision;
- event/script behavior;
- weather logic unless a purely visual parameter is explicitly safe.

Primary existing tools/contracts include:
- `tools/visual_overhaul/apply_g4_showcase_passes.py`
- `tools/visual_overhaul/recolor_g4a_eterna.c`
- `tools/visual_overhaul/recolor_g4b_snow.c`
- `tools/visual_overhaul/recolor_g4c_distortion.c`
- `tools/visual_overhaul/recolor_g4_remainder.c`
- `tools/visual_overhaul/recolor_g4_showcase.c`
- `tools/visual_overhaul/recolor_g4g_galactic.c`
- existing `validate_g4*.py` validators
- `tools/visual_overhaul/validate_area_light_contract.py`
- `src/overlay005/area_light.c`
- `src/overlay005/fieldmap.c`
- `res/field/lighting/`
- `res/field/area_data/`

Do not invent a new pipeline if the current G4/G6 pipeline can express the change safely.

## Overall visual target

The overworld should feel less like untouched 2009 Platinum and more like a premium modern DS remaster while remaining native DS rendering.

Modernization should come from:
- stronger authored regional palette identity;
- better light/dark separation;
- stronger depth cues;
- coherent fog/weather;
- selective atmospheric accents;
- improved contrast between interactable characters and environment;
- more cinematic landmark areas.

Do not solve this through arbitrary darkness or excessive saturation.

At native 256×192:
- player and NPC silhouettes must remain readable;
- doors, paths, ledges, stairs, water edges and collision-relevant boundaries must remain clear;
- weather/fog must not hide navigation information.

## Environment requirements

### 1. Eterna / deep forest

Goal: deeper, denser, more atmospheric forest without crushing sprite visibility.

Audit and improve where justified:
- canopy/deep-green separation;
- cool shadow depth;
- selective warm/cool landmark contrast;
- fog/light coherence;
- texture grades already owned by G4A.

Do not turn the forest into uniformly dark green.

Use the existing Eterna recolor/dump/report pipeline first.

### 2. Route 217 / Snowpoint

Goal: stronger cold, exposed, high-altitude atmosphere.

Audit and improve:
- snow/ice luminance hierarchy;
- blue/cyan cold shadows;
- storm/fog readability;
- building/player/NPC separation against snow;
- coherence between Route 217, Acuity approaches and Snowpoint.

Avoid white clipping and low-contrast characters on snow.

Use the existing G4B snow pipeline first.

### 3. Galactic interiors

Goal: make Galactic spaces more deliberate, synthetic and threatening.

Audit and improve:
- steel/navy structure;
- controlled cyan/teal technological accents;
- selective red/magenta danger accents where already appropriate;
- stronger room depth without obscuring doors/consoles/NPCs.

Preserve existing G4G resource isolation. Do not recolor shared interior resources if that would contaminate ordinary buildings.

### 4. Mt. Coronet / Spear Pillar

Goal: build a stronger progression from cave ascent to exposed mythic summit.

Coronet:
- cooler stone depth;
- clearer cave layers;
- restrained atmospheric haze.

Spear Pillar:
- stronger ancient/high-altitude separation;
- colder open-air grade;
- make the summit feel visually distinct from ordinary mountain interiors.

Do not alter collision or map geometry.

### 5. Distortion World

Goal: most surreal regular-field environment in the game without sacrificing navigation.

Audit and improve:
- separation between void, traversable platforms and interactable objects;
- purple/blue/teal spectral hierarchy;
- selective contrast around paths and platforms;
- existing G4C grade/fog behavior.

Do not make the entire scene uniformly dark or uniformly saturated.

### 6. Lakes / coastal routes

Goal: stronger water/sky/shore identity and clearer regional atmosphere.

Audit:
- lake water vs shoreline separation;
- coastal cool light;
- reflections/highlights where already resource-backed;
- fog/weather consistency;
- silhouettes against water.

Avoid making every water map use one identical blue grade.

### 7. Caves / Turnback Cave

Goal: deeper subterranean atmosphere with readable navigation.

Audit:
- dark stone depth;
- restrained cool/neutral haze;
- clear ladders, doors, paths, ledges and NPC silhouettes;
- Turnback Cave distinction from ordinary caves.

Do not reduce visibility enough to make navigation tedious.

## Allowed implementation techniques

Prefer, in order:
1. existing deterministic G4/G6 generators/recolor/apply tools;
2. palette/light/fog parameter changes through verified source paths;
3. selective existing field-effect reuse;
4. dedicated resource isolation where shared retail resources cause collateral recolors;
5. very small atmosphere emitters only through already-proven resource paths.

Any new deterministic transformation should be scriptable/reproducible.

If an asset is generator-owned, change the generator/tool, regenerate, then verify a second run produces no diff.

## Avoid

Do not:
- blindly replace whole map texture families;
- change geometry;
- change collision;
- alter encounter/gameplay logic;
- change map scripts for aesthetics unless a proven presentation-only hook is required;
- patch opaque NARCs without a verified contract;
- create new renderer systems;
- add expensive per-frame allocations/effects;
- make navigation harder;
- reopen G7.1–G7.5 without a concrete regression.

## Shared-resource safety

For every changed shared resource, establish:
- exact consumers;
- whether the resource is reused by maps outside the intended environment group;
- whether a dedicated slot already exists;
- whether isolation is needed before recoloring.

If isolation is unclear, do not guess.

If only one environment is blocked:
- document the blocker precisely;
- continue the remaining G7.6 environment groups;
- do not stop the whole session unless the blocker affects the entire section.

## Implementation checkpoints

Use these as internal checkpoints, not separate sessions:

Checkpoint A:
- Eterna
- Route 217 / Snowpoint

Checkpoint B:
- Galactic interiors
- Mt. Coronet / Spear Pillar

Checkpoint C:
- Distortion World
- lakes / coastal
- caves / Turnback

Target coherent commits around these groups if useful.

Do not run full Rev 0/Rev 1 builds after A or B.

## Validation

During implementation, use only the relevant environment validator/recolor check for the group you are editing.

After **all G7.6 groups are complete**:

1. rerun every touched deterministic apply/recolor/generator step and confirm reproducibility / no unexpected diff;
2. run all relevant existing G4/G6 environment validators;
3. run `tools/visual_overhaul/validate_area_light_contract.py`;
4. add or extend a focused G7.6 validator only where an existing validator does not protect a new contract;
5. run `python3 tools/overhaul/validate_overhaul.py --no-write` if shared code/resource plumbing changed;
6. build US Rev 0 once;
7. if Rev 0 succeeds, build US Rev 1 once;
8. if a build fails, fix the first localized cause and rerun only the failed build before final evidence.

Do not repeatedly run dual-revision builds after cosmetic edits.

## Runtime boundary

Do not create:
- DeSmuME automation;
- gameplay bots;
- headless campaign harnesses;
- long-running runtime probes beyond existing quick/static tooling.

Runtime visual approval belongs to the owner on iPhone DS emulators.

Static texture/palette sheets or quick exports are allowed if they take minutes and help verify the authored resources.

## Documentation

Create/update:
`docs/visual_overhaul/G7_6_OVERWORLD_ATMOSPHERE.md`

Keep it concise but cover **all seven priority groups**.

For each group record:
- ownership/resources;
- exact changes;
- shared-resource/isolation decisions;
- functionality/navigation preserved;
- relevant validator result;
- deferred item if any.

Also record:
- final generator/recolor reproducibility;
- area-light validation;
- Rev 0 / Rev 1 results;
- owner runtime checklist.

## Owner runtime checklist

Prepare a concise checklist for portrait stacked and landscape side-by-side play.

At minimum include representative captures from:
- Eterna Forest;
- Route 217 during weather and Snowpoint;
- one ordinary Galactic interior and a major Galactic room;
- Mt. Coronet interior and Spear Pillar;
- Distortion World;
- one lake and one coastal route;
- ordinary cave and Turnback Cave.

Verify:
- player/NPC silhouette readability;
- path/door/ledge/stair/water-edge clarity;
- fog/weather coherence;
- no shared-resource leakage;
- no palette popping between adjacent maps;
- landmark areas feel stronger than ordinary routes without looking like different games.

## Commit / finish rules

Use a small number of coherent commits, preferably aligned with Checkpoints A/B/C plus documentation/validation if needed.

Avoid micro-commits.

Before finishing:
- `git status` clean;
- no temporary QA files;
- generated/recolored outputs match their authoritative tools;
- no unrelated files staged.

## Stop rule

Once **all of G7.6** is audited, safely implemented where supported, validated, built, committed and documented:

**STOP.**

Do not begin G7.7.

Return only:
- G7.6 completion status;
- environment groups completed;
- commit SHA(s);
- validator results;
- Rev 0 result;
- Rev 1 result;
- deferred/blocker items by environment, if any;
- owner runtime checks;
- PR readiness.
