# Pokémon Platinum Overhaul — Breeding 2.0 Spec

Status: **LOCKED SPEC**

## 1. Design target

Breeding should be a practical midgame team-building system, not postgame paperwork.

Core principles:
- breeding refines Pokémon; it does not repair basic campaign functionality;
- level-up learnsets remain the primary source of ordinary STAB and role-defining moves;
- egg moves provide optional inherited techniques, early access, utility, and specialization;
- no external game/trade requirement may be needed to create a legal inheritance chain;
- the locked no-incense baby rule applies to all affected baby species;
- cross-type offspring/variant breeding remains deferred beyond Core 1.0.

## 2. Platinum source baseline

Breeding is centrally implemented in:
- `src/overlay005/daycare.c`;
- `include/constants/daycare.h`;
- species egg-group and egg-move resources;
- daycare field scripts.

Current Platinum behavior includes:
- 50% Everstone nature inheritance from the selected eligible parent;
- 3 inherited IV stats;
- father-only egg-move inheritance;
- father TM/HM inheritance;
- shared level-up move inheritance when both parents know the move;
- incense-gated baby species;
- compatibility checks every 255 parent steps;
- hatch-cycle decrement every 255 field steps, with Flame Body/Magma Armor doubling decrement.

## 3. Nature inheritance

Everstone nature inheritance becomes **100%**.

Rules:
- if exactly one eligible parent holds Everstone, inherit that parent's nature;
- if both eligible parents hold Everstone and have different natures, choose either parent 50/50;
- if both have the same nature, inherit it;
- Ditto follows the same rule and does not receive a special penalty;
- without Everstone, nature remains random.

Do not add Destiny Knot or later-generation mechanics.

## 4. IV inheritance

Increase inherited IV count:

**3 → 4 distinct stats**

Rules:
- choose four unique stats;
- each chosen stat independently selects one of the two parents 50/50;
- no inherited stat may be selected twice;
- remaining two IVs stay randomly generated;
- Ditto is treated as an ordinary parent for IV inheritance;
- do not guarantee perfect IVs.

This improves predictability without making breeding trivial.

## 5. Ability inheritance

Do **not** add new ability-slot inheritance logic in Core 1.0.

Platinum ability selection remains governed by its existing personality/species behavior.

Reason:
- the source audit confirms nature and IV inheritance are cleanly separable;
- forcing ability-slot inheritance would require personality-generation constraints and risks interacting with gender, nature, form, and shiny logic;
- the project does not need hidden-ability or modern breeding behavior.

This may be revisited only after runtime evidence shows a meaningful breeding usability problem.

## 6. Baby Pokémon — no incense requirement

Remove incense as a requirement for producing:

- Wynaut
- Azurill
- Mime Jr.
- Bonsly
- Munchlax
- Mantyke
- Budew
- Happiny
- Chingling

Breeding their family always produces the baby-stage species when that family normally has one.

Incense items remain obtainable for their independent held-item effects.

## 7. Egg-move inheritance

### 7.1 Either parent may pass egg moves

If either biological parent knows a move listed in the offspring species' egg-move pool, the offspring may inherit it.

This replaces the father-only restriction.

Ditto itself does not contribute species egg moves unless the non-Ditto species' normal rules make that move available through the other parent.

### 7.2 Shared level-up moves

Keep the current rule that a move in the offspring's level-up pool is inherited when both parents know it.

### 7.3 TM/HM inheritance

Retain Platinum's existing TM/HM inheritance behavior for compatibility, but do not expand it.

Because TMs are reusable in the overhaul, TM inheritance is no longer a major progression requirement.

### 7.4 Created moves

Created identity moves must not be broadly added to egg pools.

Do not add:
- Resonant Slash
- Solar Petal
- Vine Snare
- Luminous Current
- Soul Siphon
- Pollen Pulse
- Earthen Bash
- Scrap Guard
- Magnet Volley
- Soul Grip
- Stalk Slash
- Cursed Stitch
- Star Jab

Generic created moves are also not automatically egg moves.

## 8. Egg-move pool policy

Preserve vanilla Platinum egg pools by default.

Only add or remove entries when one of these conditions applies:
- a locked redesign creates an obvious inherited specialization;
- a family has an unnecessary one-save inheritance dead end;
- a move remains thematically valuable as early inherited access even after becoming a natural move;
- an evolved-anatomy/signature move would be inappropriate and should remain excluded.

Do not perform blanket movepool inflation.

A duplicate between level-up and egg move is allowed when breeding provides meaningful earlier access.

## 9. One-save inheritance rule

Every egg move retained or added in the overhaul must have at least one legal inheritance path using species obtainable in the same Platinum save.

Validator must prove:
- compatible egg groups;
- appropriate parent sex/role or Ditto path;
- source Pokémon can legally know the move;
- no external generation/game transfer is required.

If a vanilla egg move has no valid one-save path after the overhaul's final availability/learnset rules, either:
1. add a legal in-save parent path; or
2. remove the dead entry.

## 10. Egg groups

Core 1.0 uses a **conservative egg-group cleanup**, not a wholesale redesign.

Rules:
- preserve vanilla groups unless a clear inheritance/accessibility problem exists;
- add a second egg group only when anatomy/ecology and inheritance utility both strongly support it;
- do not change Undiscovered/Legendary breeding restrictions except already-established baby/family rules;
- Ditto remains Ditto;
- genderless non-Ditto species still require Ditto where vanilla structure requires it.

The implementation manifest must list every egg-group change explicitly with rationale.

No automatic type-to-egg-group mapping.

## 11. Egg generation speed

Keep existing compatibility percentages:
- low: 20%;
- medium: 50%;
- high: 70%.

Increase check frequency:

**255 parent steps → 128 parent steps**

This roughly doubles egg-production opportunities without removing compatibility differences.

Special-date behavior may remain, but it must not make ordinary days worse than the new 128-step baseline.

## 12. Hatching speed

Reduce every species' hatch-cycle requirement to:

**ceil(vanilla_hatch_cycles / 2)**

Minimum: **1 cycle**.

Keep Flame Body / Magma Armor as meaningful acceleration:
- normal party: subtract 1 cycle per hatch tick;
- Flame Body/Magma Armor present: subtract 2 cycles.

Result:
- ordinary hatching is roughly twice as fast as vanilla;
- dedicated hatch teams remain roughly twice as fast again.

Do not remove walking/hatching gameplay entirely.

## 13. Day Care availability

Keep the Solaceon Day Care location.

Do not relocate the facility or create a second full Day Care in Core 1.0.

Its usefulness improves through:
- expanded pre-E4 species availability;
- no-incense babies;
- faster egg generation;
- faster hatching;
- better inheritance;
- broader legal one-save egg-move chains.

This is sufficient to make breeding useful during the main story once Solaceon is reached.

## 14. Day Care leveling

Keep passive Day Care level gain and withdrawal-cost behavior unless implementation audit uncovers a concrete conflict.

Breeding changes should not become a hidden EXP/economy rewrite.

## 15. Shiny/Masuda behavior

Preserve Platinum's existing different-language parent shiny logic.

Do not increase shiny odds as part of Breeding 2.0.

Nature/IV changes must not accidentally bypass or multiply the existing Masuda personality attempts.

## 16. Form/species special cases

Preserve existing special logic unless explicitly changed:
- Manaphy → Phione breeding;
- Nidoran male/female outcome handling;
- Volbeat/Illumise outcome handling;
- Rotom/form handling;
- Ditto restrictions;
- Undiscovered group restrictions.

No new legendary breeding beyond existing Phione behavior.

## 17. Egg-move design scope

The C3 rule remains authoritative:

> Egg moves refine; they do not repair.

Therefore D4 does not reopen locked C3 level-up/TM/tutor decisions.

The final egg-move sweep should prioritize:
- utility;
- alternative coverage;
- setup;
- support;
- early access to a later natural move;
- thematic inherited techniques.

It should not give strong Pokémon gratuitous extra coverage.

## 18. Validation requirements

Breeding implementation must validate:
- 100% Everstone nature inheritance;
- four unique inherited IV stats;
- no duplicate IV-stat selection;
- either-parent egg-move inheritance;
- no-incense baby output;
- one-save legality of every egg move;
- egg generation at the new cadence;
- hatch-cycle halving;
- Flame Body/Magma Armor acceleration;
- Masuda logic preserved;
- Manaphy/Phione preserved;
- all changed egg groups explicitly manifested;
- no created identity move leaks into egg pools.

## 19. Deferred

Not Core 1.0:
- cross-type offspring;
- regional/variant breeding;
- hidden abilities;
- Destiny Knot mechanics;
- Power-item IV targeting;
- Poké Ball inheritance;
- guaranteed ability-slot inheritance;
- nursery UI redesign.

This spec is approved authority for Breeding 2.0.
