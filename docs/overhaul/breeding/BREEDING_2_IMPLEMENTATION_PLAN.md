# Pokémon Platinum Overhaul — Breeding 2.0 Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority:
- `docs/overhaul/breeding/BREEDING_2_SPEC.md`
- locked evolution/species/learnset authority

Claude Code implements; it must not redesign breeding rules.

## 1. Confirmed source targets

Primary breeding engine:
- `src/overlay005/daycare.c`
- `include/constants/daycare.h`

Relevant behavior already exposed there:
- Everstone nature inheritance;
- IV inheritance;
- egg-move construction;
- Ditto handling;
- incense-baby conversion;
- compatibility;
- egg generation;
- hatch-cycle decrement;
- Flame Body/Magma Armor.

Additional sources:
- `res/pokemon/*/data.json` for hatch cycles / egg groups;
- generated egg-move data and source templates;
- Day Care field scripts/text;
- item data for Everstone/Power items;
- mart stock for breeding supplies.

## 2. Breeding manifests

Create:
- `docs/overhaul/implementation/breeding/breeding_rules.json`
- `docs/overhaul/implementation/breeding/egg_group_changes.json`
- `docs/overhaul/implementation/breeding/egg_move_changes.json`
- `docs/overhaul/implementation/breeding/hatch_cycle_changes.json`
- `docs/overhaul/implementation/breeding/breeder_shop_changes.json`

Every non-empty change entry must include:
- before value;
- target value;
- source path;
- rationale;
- locked authority reference.

The egg-group and egg-move manifests may legitimately be empty if the audit proves no Core 1.0 changes are required.

## 3. B0 — Guard current behavior

Before edits, add or script deterministic tests for:
- single-Everstone 50% behavior;
- current female/Ditto restriction;
- 3-IV inheritance;
- current father-only egg moves;
- incense babies;
- 255-step generation cycle;
- hatch-cycle decrement;
- Flame Body/Magma Armor;
- Masuda personality rerolls.

Capture source hashes/guards.

## 4. B1 — Everstone rewrite

Update nature-parent selection:

- gather parents holding Everstone;
- none → random nature as vanilla;
- one → inherit that parent's nature 100%;
- two → randomly choose one of the two parents, then inherit 100%.

Remove gender/female/Ditto restriction.

Keep personality generation compatible with:
- target nature;
- gender;
- shiny handling;
- later ability-slot selection.

## 5. B2 — Four-IV inheritance

Change `NUM_INHERITED_IVS` from 3 to 4.

Fix/verify distinct-stat selection so the selected stat index, not merely the loop index, is removed from the candidate list.

Add Power-item forced-stat handling before random selection:
- identify relevant held Power items;
- choose one guarantee if one/both parents qualify;
- reserve that stat index;
- copy it from the correct holder;
- select remaining inherited stats distinctly;
- randomize parent source for unforced inherited stats.

Do not implement Destiny Knot inheritance.

## 6. B3 — Ability-slot inheritance

Implement 80/20 inheritance from the non-Ditto species parent for species with two distinct normal abilities.

Do not create a new hidden-ability field/system.

Preserve legal personality-derived semantics:
- if ability slot is personality-linked in live source, generate/adjust personality under the already-selected nature/gender/shiny constraints rather than writing a contradictory ability value;
- if the engine stores a stable ability slot independently, use the smallest safe source change.

Add deterministic tests for:
- female + male;
- male + Ditto;
- female + Ditto;
- genderless + Ditto;
- one-ability species;
- two-ability species.

## 7. B4 — Either-parent egg moves

Refactor egg-move collection so listed egg moves may come from either parent.

Rules:
- gather eligible listed egg moves from both;
- deduplicate;
- preserve deterministic order;
- preserve four-move cap/replace semantics.

Do not broaden the species egg-move list during this engine step.

Preserve:
- father TM/HM inheritance;
- both-parent shared level-up inheritance;
- Volt Tackle special behavior.

## 8. B5 — No-incense babies

Remove incense gating from:
- Wynaut
- Azurill
- Mime Jr.
- Bonsly
- Munchlax
- Mantyke
- Budew
- Happiny
- Chingling

Prefer simplifying/bypassing `Daycare_AlterEggSpeciesWithIncenseItem` while retaining the correct family base species.

Regression-test each family.

## 9. B6 — Egg production interval

Change the normal Day Care generation interval from 255 to 128 steps.

Preserve compatibility percentages 20/50/70.

Audit special-date handling:
- either scale special dates proportionally to the new interval;
- or remove the special-date micro-bonus if that is cleaner.

Do not let the date behavior produce a slower interval than ordinary overhaul breeding.

Document the chosen equivalent in the manifest; this is implementation normalization, not a new design choice.

## 10. B7 — Hatch cycles

Generate the hatch-cycle manifest from current breedable species:

`target = max(5, ceil(vanilla / 2))`

Do not modify Undiscovered-only species unless they participate in a legitimate egg result.

Apply data edits with before-value guards.

Preserve Flame Body/Magma Armor cycle subtraction.

## 11. B8 — Egg-group and egg-move audit

Run a one-save inheritance audit against:
- all species #001–#493;
- final encounter availability;
- final egg groups;
- existing egg moves;
- either-parent inheritance;
- no-incense babies.

For every egg move, prove at least one legal same-save parent chain or mark it unreachable.

Only propose a data change if:
- the chain is impossible; or
- a previously locked breeding refinement explicitly requires it.

Do not invent broad new egg-group/egg-move content.

If a genuine design decision is needed, stop only that affected entry and report it.

## 12. B9 — Breeder supply access

Add renewable midgame purchase access for:
- Everstone at ₽200;
- Power Weight/Bracer/Belt/Lens/Band/Anklet at ₽3,000 each.

Prefer Veilstone Department Store or a Solaceon-area existing vendor.

Do not make these Frontier-only.

Validate Ditto availability separately against the availability manifest; do not add a gift unless already approved.

## 13. Validator

Create:
`tools/overhaul/validate_breeding.py`

Fail on:
- Everstone not 100%;
- gender restriction still present;
- inherited IV count != 4;
- duplicate inherited IV stat indices;
- incorrect Power-item mapping/source;
- ability-slot probability/config mismatch;
- father-only egg-move restriction remaining;
- incense-required baby family;
- wrong generation interval;
- wrong hatch-cycle target;
- broken Flame Body/Magma Armor behavior;
- broken Manaphy→Phione/Nidoran/Volbeat-Illumise special cases;
- unreachable egg moves in the final one-save graph;
- unapproved egg-group/egg-move expansion.

Generate:
`docs/overhaul/implementation/breeding/BREEDING_VALIDATION_REPORT.md`

## 14. Runtime tests

At minimum:
- one parent Everstone;
- both parent Everstones;
- four-IV inheritance over deterministic seeded runs;
- each Power item;
- both parents holding different Power items;
- ability-slot inheritance sample distribution;
- mother-only listed egg move;
- father-only listed egg move;
- duplicate move from both parents;
- all nine no-incense babies;
- Ditto + male/female/genderless cases;
- 128-step egg-generation check;
- standard hatch cycle;
- Flame Body/Magma Armor accelerated hatch;
- Masuda-language shiny-path regression;
- Manaphy→Phione;
- Nidoran;
- Volbeat/Illumise.

## 15. Build order

Recommended commits:
1. manifests + baseline validator;
2. Everstone + IV inheritance;
3. Power-item + ability inheritance;
4. either-parent egg moves;
5. no-incense babies;
6. generation/hatch speed;
7. breeding supply shop;
8. one-save legality audit;
9. final validation/status.

Build US Rev 0 and Rev 1 after each engine-affecting batch and at final integration.

## 16. Status

Update:
- `docs/overhaul/STATUS.md`
- `docs/overhaul/DESIGN_PIPELINE.md`

Use:
- LOCKED SPEC
- IMPLEMENTING
- IMPLEMENTED
- VERIFIED

Do not claim VERIFIED until dual-revision builds and runtime inheritance/hatch tests pass.

## 17. Acceptance

D4 is complete when:
- all locked breeding mechanics are implemented exactly;
- breeding is materially faster and more predictable;
- no-incense babies work;
- inheritance is one-save legal;
- no broad unapproved egg-group/move redesign slipped in;
- breeder supplies are reasonably available;
- both supported revisions build;
- runtime tests pass.
