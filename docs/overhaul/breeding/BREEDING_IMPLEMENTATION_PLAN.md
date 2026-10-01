# Pokémon Platinum Overhaul — Breeding 2.0 Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority:
- `docs/overhaul/breeding/BREEDING_SPEC.md`
- locked C3 learnset/egg-move principles
- locked evolution/species rules

Claude Code implements; it must not redesign breeding behavior.

## 1. Source targets

Primary engine:
- `src/overlay005/daycare.c`
- `include/constants/daycare.h`
- `src/daycare_save.c`
- relevant Day Care scripts/text

Data:
- species egg-group fields under `res/pokemon/*/data.json`;
- generated egg-group constants;
- species egg-move resources generated from `res/pokemon/species_egg_moves.h` / source templates;
- species hatch-cycle values in Pokémon data.

Known functions requiring audit/edits:
- `Daycare_GetParentToInheritNature`
- `Daycare_SetInheritedNature`
- `Egg_InheritIVs`
- `Egg_BuildMoveset`
- `Daycare_AlterEggSpeciesWithIncenseItem`
- `Daycare_Update`
- egg hatch-cycle decrement path
- compatibility helpers

## 2. B0 — Baseline manifest

Create:

`docs/overhaul/implementation/breeding/breeding_rules.json`

Encode:
- Everstone rate = 100%;
- inherited IV count = 4;
- IV stats unique = true;
- either-parent egg moves = true;
- no-incense babies = true;
- egg check cadence = 128;
- hatch-cycle transform = ceil(vanilla/2);
- Flame Body/Magma Armor multiplier preserved;
- ability inheritance = vanilla;
- Masuda behavior = vanilla.

Create before-value/source guards.

## 3. B1 — Nature inheritance

Refactor current Everstone selection so:
- one holder always passes nature;
- two holders use a 50/50 parent choice when appropriate;
- same-nature holders remain deterministic;
- Ditto works consistently.

Do not change random nature behavior when no Everstone is held.

Test gendered pair, Ditto pair, two Everstones, and no Everstone.

## 4. B2 — IV inheritance

Change `NUM_INHERITED_IVS` from 3 to 4.

Audit and correct the unique-stat selection routine.

Important:
the current function must be checked carefully because the removal helper is index-sensitive. Validator/unit tests must prove four distinct stat indices are selected every time.

For each selected stat:
- randomly select parent 0/1;
- copy that parent's IV;
- leave the other two random.

No stat may be inherited twice.

## 5. B3 — No-incense babies

Remove the incense gate for the nine baby families.

Preferred implementation:
- make the egg-species resolution directly retain the baby species;
- do not require held incense checks.

Do not delete incense items or their battle effects.

Regression-test all nine families.

## 6. B4 — Either-parent egg moves

Refactor `Egg_BuildMoveset` so listed egg moves can come from either parent.

Requirements:
- avoid duplicate moves;
- retain four-move capacity behavior;
- preserve shared level-up inheritance;
- preserve existing TM/HM inheritance unless a direct code conflict requires a documented minimal adaptation;
- Ditto must not accidentally inject unrelated moves.

Do not add created identity moves.

## 7. B5 — Egg generation cadence

Change the ordinary egg-generation compatibility check cadence from 255 to 128 parent steps.

Preserve compatibility probabilities 20/50/70.

Audit special-date logic:
- ordinary cadence must never become slower than 128 because of a calendar date;
- preserve harmless flavor only if behavior remains consistent.

## 8. B6 — Hatch-cycle transform

Create a generated manifest:

`docs/overhaul/implementation/breeding/hatch_cycles.json`

For every breedable species:
- record vanilla hatch cycles;
- target = max(1, ceil(vanilla / 2)).

Apply target values to species data.

Do not change hatch-cycle values for special pseudo-species such as Egg/Bad Egg unless source semantics explicitly require it.

Preserve Flame Body/Magma Armor decrement of 2.

## 9. B7 — Egg-move legality audit

Create:

`tools/overhaul/validate_egg_moves.py`

For every species egg move:
- identify at least one legal parent in the final #001–#493 same-save roster;
- validate overlapping egg group;
- validate parent can know the move through locked level-up/TM/tutor/egg inheritance rules;
- validate sex/compatibility constraints;
- permit legal chain breeding;
- reject paths requiring external games/trading/transfers.

Output:

`docs/overhaul/implementation/breeding/EGG_MOVE_LEGALITY_REPORT.md`

Do not automatically add moves merely because a path is missing.

For dead vanilla entries:
- produce a compact proposed-fix table;
- use the smallest fix consistent with the locked spec;
- if it requires a subjective new egg-group or egg-move design decision, flag it rather than silently inventing one.

## 10. B8 — Egg-group cleanup manifest

Create:

`docs/overhaul/implementation/breeding/egg_group_changes.json`

Default: no change.

Only include a species when:
- one-save inheritance validation proves a practical blocker; and
- a second group is anatomically/ecologically defensible.

Every entry must include:
- species/family;
- vanilla groups;
- target groups;
- inheritance problem fixed;
- rationale.

Do not bulk-map groups from typings.

If no changes are required, commit an empty manifest and state that vanilla egg groups were sufficient.

## 11. B9 — Final egg-move sweep

Use locked C3 authority.

Preserve vanilla pools by default.

For each actual change create:
`docs/overhaul/implementation/breeding/egg_move_changes.json`

Fields:
- species;
- move;
- add/remove;
- source parent path;
- rationale category;
- one-save legality.

Reject:
- created identity moves;
- basic STAB repair;
- gratuitous elite-Pokémon coverage.

## 12. Ability safety

Do not implement ability inheritance.

Add regression tests proving breeding still produces valid ability slots under current Platinum personality logic.

Nature inheritance changes must not corrupt:
- gender;
- ability slot;
- shiny checks;
- form/personality-sensitive cases.

## 13. Masuda/shiny regression

Test:
- same-language parents;
- different-language parents;
- Everstone + different-language parents;
- two Everstones + different languages.

Preserve the existing number/behavior of shiny personality attempts.

No shiny-rate buff.

## 14. Runtime test matrix

At minimum:
- one normal compatible pair;
- high/medium/low compatibility;
- Ditto + male;
- Ditto + female;
- Ditto + genderless;
- two Everstones;
- four-IV inheritance across repeated eggs;
- either-parent egg move;
- shared level-up move;
- father TM/HM move;
- each of nine no-incense babies;
- Pichu + Light Ball Volt Tackle;
- Nidoran outcome;
- Volbeat/Illumise outcome;
- Manaphy → Phione;
- Flame Body/Magma Armor hatch acceleration;
- ordinary hatch timing;
- Masuda pair.

## 15. Build sequence

Recommended commits:
1. breeding manifests + validators;
2. nature + IV inheritance;
3. no-incense babies + egg moves;
4. egg generation/hatch speed;
5. egg legality audit + minimal data cleanup;
6. final runtime tests + status update.

Build US Rev 0 and Rev 1 after every engine-affecting batch and final integration.

## 16. Status updates

Update:
- `docs/overhaul/STATUS.md`
- `docs/overhaul/DESIGN_PIPELINE.md`

Lifecycle:
- LOCKED SPEC
- IMPLEMENTING
- IMPLEMENTED
- VERIFIED

VERIFIED requires:
- dual-revision builds;
- exact inheritance tests;
- hatch/generation timing tests;
- one-save egg-move legality report;
- no-incense baby tests;
- Masuda/special-case regression tests.

## 17. Acceptance criteria

D4 is complete when:
- Everstone nature inheritance is deterministic at 100%;
- exactly four distinct IV stats inherit;
- either parent can pass listed egg moves;
- all incense babies breed directly;
- egg generation checks at 128 steps;
- hatch cycles are halved;
- Flame Body/Magma Armor remain useful;
- all retained egg moves have legal one-save inheritance paths;
- no unintended ability/shiny/form regressions occur;
- both supported US revisions build and runtime tests pass.
