# Pokémon Platinum Overhaul — Trainer Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority: `docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md`.

Claude Code owns implementation. It must not redesign teams or difficulty rules.

## 1. Source reality

Primary editable trainer data lives under:

`res/trainers/data/*.json`

Each trainer JSON exposes, as applicable:

- name/class;
- trainer bag items;
- AI flags;
- double-battle flag;
- party species/form;
- level;
- held item;
- explicit moves;
- `iv_scale`;
- ball seal;
- battle messages.

Trainer resources are integrated under `res/trainers/meson.build`.

Frontier data is separate under `res/trainers/frontier/` and is out of this implementation phase except for shared validation.

## 2. Do not touch yet

Do not redesign or implement:

- Battle Frontier trainer pools;
- economy/EXP;
- encounter availability beyond validation references;
- Legendary/Mythical events;
- breeding;
- unrelated Pokémon/move data.

If a proposed move/species is not yet present in current main, mark the affected trainer entry blocked rather than inventing a replacement.

## 3. Machine-readable authority

Create:

`docs/overhaul/implementation/trainers/trainer_overhaul_manifest.json`

It must enumerate every intentionally changed trainer file with:
- trainer path/id;
- category;
- story gate;
- before party summary;
- target party;
- target levels;
- target held items;
- target moves;
- target AI flags when changed;
- expected party size;
- rationale tag.

Create:

`docs/overhaul/implementation/trainers/trainer_archetypes.json`

for ordinary-trainer transformation rules by trainer class/area.

Create:

`docs/overhaul/implementation/trainers/trainer_validation_rules.json`

encoding:
- level bands;
- party-size caps;
- AI requirements;
- availability-band restrictions;
- duplicate policy;
- boss/item policy.

## 4. Implementation batches

### T0 — Inventory and guard generation
- enumerate all active trainer JSONs;
- separate unused records;
- classify bosses, Rival branches, ordinary trainers, rematches, Frontier;
- generate before-value hashes/guards;
- confirm `iv_scale` semantics before changing it;
- do not normalize `iv_scale` until its runtime/build semantics are verified.

### T1 — Gym Leaders
Implement the eight locked main-story teams exactly.

Validate after each leader:
- JSON parse;
- species/move constants;
- party size;
- level curve.

### T2 — Rival
Update all three starter branches consistently across:
- Route 203;
- Route 209;
- Pastoria;
- Canalave;
- Pokémon League;
- Fight/Survival Area variants.

Preserve branch logic. Use generated comparison to ensure only the intended complementary slots differ.

### T3 — Galactic bosses
Implement:
- Mars;
- Jupiter;
- Saturn;
- Cyrus HQ;
- Cyrus Distortion World;
- later Commander variants according to the locked scaling rules.

### T4 — Elite Four + Cynthia
Implement main-story teams/moves and ensure the resulting sequence maintains the locked ace curve.

### T5 — Ordinary trainers
Apply archetype-driven edits in geographic/progression batches.

Do not mechanically replace every species. Priorities:
1. remove repetitive filler;
2. showcase newly available families;
3. synchronize evolution stage with level;
4. improve obviously useless moves;
5. preserve trainer-class identity.

Batch by story region so encounter availability can be cross-validated.

### T6 — Rematches
Implement Gym, Rival, Elite Four, and Cynthia rematches from the locked spec.

Do not touch Frontier facility opponents.

## 5. Move-generation policy

For ordinary trainers:
- default to legal/natural moves available at their level;
- preserve 2–4 useful moves rather than forcing four optimized moves;
- do not give perfect coverage.

For important trainers:
- explicit locked moves in the spec take priority;
- fill any unspecified fourth slot only from the Pokémon's current legal thematic pool;
- no new created-move recipients may be invented.

Use current move properties from main, not vanilla assumptions.

## 6. Validation tooling

Create a trainer validator under `tools/overhaul/`, preferably:

`tools/overhaul/validate_trainers.py`

It must fail on:
- invalid species/form/move/item;
- empty or over-cap parties;
- boss party-size mismatch;
- level outside declared band;
- illegal duplicate on important teams;
- required boss AI flags missing;
- unresolved/superseded move constants;
- availability violation for ordinary trainers;
- evolution-stage contradiction detectable from the locked evolution manifest;
- manifest/source drift.

Warnings:
- ordinary trainer repeated species;
- suspiciously weak moves;
- large effective-strength spike;
- held items on low-tier trainers;
- unusual `iv_scale`.

Create a report:
`docs/overhaul/implementation/trainers/TRAINER_VALIDATION_REPORT.md`

## 7. Power-curve audit

Do not judge difficulty from levels alone.

Generate a simple per-party diagnostic using:
- level;
- BST from current Pokémon data;
- number of evolved/final forms;
- held item presence;
- explicit high-power STAB/coverage count.

This is an audit heuristic, not a battle simulator.

Flag large unexplained jumps between consecutive mandatory bosses for human review.

## 8. Build and runtime QA

After each major batch:
- run trainer validator;
- run repository data generation/build checks;
- build US Rev 0;
- build US Rev 1.

Runtime smoke tests should include at least:
- Roark;
- Gardenia;
- Fantina;
- Maylene;
- Wake;
- Byron;
- Candice;
- Volkner;
- one Rival branch early;
- same branch at League;
- Mars Windworks;
- Cyrus HQ;
- Cyrus Distortion World;
- each Elite Four member;
- Cynthia;
- one postgame Gym rematch.

Confirm:
- correct party loads;
- moves execute;
- held items behave;
- AI does not stall on malformed sets;
- no script progression issue after victory.

## 9. Commit structure

Recommended:
1. trainer manifests + validator;
2. main-story Gyms;
3. Rival;
4. Galactic;
5. Elite Four/Cynthia;
6. ordinary trainers early/mid;
7. ordinary trainers late;
8. rematches;
9. final validation/status docs.

Keep unrelated systems out of these commits.

## 10. Status updates

Update:
- `docs/overhaul/STATUS.md`;
- `docs/overhaul/DESIGN_PIPELINE.md`.

Use:
- `LOCKED SPEC` before implementation;
- `IMPLEMENTING` once source edits begin;
- `IMPLEMENTED` after source + dual-revision builds;
- `VERIFIED` only after required runtime QA.

## 11. Acceptance criteria

Trainer phase is complete only when:

- all intended main-story boss records match the manifest;
- all Rival branches remain structurally synchronized;
- ordinary trainer pass is complete without encounter/evolution contradictions;
- rematches match the locked spec;
- validator passes with no blocking errors;
- no Frontier data was unintentionally changed;
- both supported US revisions build;
- representative runtime tests pass;
- STATUS documents exact evidence.

Any live-source conflict with the locked spec is reported rather than silently redesigned.
