# Pokémon Platinum Overhaul — Breeding 2.0 Spec

Status: **LOCKED SPEC**

## 1. Design target

Breeding should be a practical team-building system during the campaign and postgame, not repetitive postgame paperwork.

Core principles:
- breeding refines a Pokémon's role; it does not repair a broken species;
- level-up/TM/tutor access remains the primary way a species becomes functional;
- no flat BST rewards for bred Pokémon;
- no cross-type offspring, variant offspring, or other experimental breeding forms in Core 1.0;
- preserve Gen IV identity where it remains useful;
- reduce repetition in nature, IV, ability, egg production, and hatching;
- all inheritance chains must be possible in one save.

## 2. Platinum source baseline

Current Platinum behavior includes:
- 50% Everstone nature inheritance from the eligible female/Ditto parent;
- three inherited IVs;
- egg moves from the father;
- father TM/HM inheritance;
- shared level-up moves known by both parents;
- incense-gated babies;
- egg creation checks based on compatibility;
- species hatch-cycle values;
- Flame Body/Magma Armor doubling hatch-cycle reduction;
- standard Ditto compatibility;
- Masuda-language shiny rerolls;
- eggs hatch at Lv1.

Those are the baseline mechanics this spec modifies.

## 3. Nature inheritance

Everstone becomes **100% nature inheritance**.

Rules:
- if exactly one parent holds Everstone, inherit that parent's nature;
- if both parents hold Everstone, randomly choose one parent and inherit that nature;
- Ditto is treated exactly like any other parent for this purpose;
- gender does not restrict Everstone inheritance.

This supersedes Platinum's 50% female/Ditto-only rule.

Masuda-method shiny handling must remain compatible with the inherited nature.

## 4. IV inheritance

Increase inherited IV count from **3 to 4**.

Rules:
- inherit four distinct stat indices;
- never select the same stat twice;
- for each selected stat, choose one of the two parents at random unless a Power item forces the source;
- the remaining two stats are generated normally.

### Power-item inheritance

Power items gain their later-generation breeding utility:

- Power Weight → HP
- Power Bracer → Attack
- Power Belt → Defense
- Power Lens → Sp. Atk
- Power Band → Sp. Def
- Power Anklet → Speed

If exactly one parent holds a relevant Power item:
- that stat is guaranteed among the four inherited stats;
- it is inherited from that holder.

If both parents hold Power items:
- randomly choose one holder's forced stat/source;
- only one Power-item guarantee applies;
- choose the other three inherited stats distinctly from the remaining five.

Destiny Knot does **not** gain later-generation five-IV inheritance in Core 1.0.

## 5. Ability-slot inheritance

No Hidden Abilities exist in this project.

For species with two distinct normal ability slots:

- the non-Ditto species parent passes its current ability slot with **80% probability**;
- the other normal ability slot occurs 20% of the time;
- in a standard male/female pairing, the female is the species parent;
- with Ditto, the non-Ditto parent is the species parent;
- species with only one effective ability remain unchanged.

Implementation must preserve valid Gen IV personality/gender/nature behavior. Do not create impossible personality/ability combinations merely to force the slot.

## 6. Egg-move inheritance

Egg moves may be inherited from **either parent**, not only the father.

Rules:
- if either parent knows a move listed in the offspring species' egg-move list, the offspring may inherit it;
- duplicate inherited moves collapse to one;
- preserve the four-move cap and deterministic move replacement behavior;
- shared level-up move inheritance remains available;
- father TM/HM inheritance remains unchanged for Gen IV identity, although reusable TMs make it less important.

This broadens legal one-save breeding chains without turning egg moves into mandatory role repair.

## 7. Egg-move content policy

Keep Platinum's existing egg-move lists as the baseline.

Do **not** perform a broad "give every species more egg moves" expansion.

Additions are permitted only when all are true:
1. they refine a locked species role;
2. the move is not required for basic STAB/functionality;
3. the move is thematically appropriate;
4. a legal one-save inheritance chain exists under the final egg groups;
5. the addition does not obsolete a level-up/TM/tutor identity decision.

The C3 rule remains authoritative:

> Egg moves refine; they do not repair.

The bespoke Emerald conditional hatch-reward concepts are **DEFERRED** from Platinum Core 1.0. Platinum already has a larger move pool and stronger species-level redesign, while conditional hatch packages would create an additional mechanic beyond the native breeding hooks.

## 8. Egg groups

Retain vanilla Platinum egg groups as the default.

Do **not** broadly rewrite egg groups based merely on type changes.

Only change an egg group when one of these is demonstrated:
- the current group contradicts the species' locked biological identity;
- a locked egg-move refinement would otherwise have no legal one-save chain;
- a cross-generation family has an internal breeding inconsistency.

All egg-group changes require a machine-readable manifest and validator.

Core 1.0 should prefer **minimal egg-group edits** over wholesale expansion.

## 9. No-incense baby breeding

The already-locked no-incense rule is mandatory.

The following babies hatch directly from their family without requiring incense:
- Wynaut
- Azurill
- Mime Jr.
- Bonsly
- Munchlax
- Mantyke
- Budew
- Happiny
- Chingling

Incense items may remain for their independent battle effects or collection identity. They no longer determine whether the baby species hatches.

## 10. Egg production speed

Keep Platinum's compatibility score identities:
- incompatible = 0
- low = 20
- medium = 50
- high = 70

Change the Day Care egg-generation check interval from roughly **255 steps to 128 steps**.

Do not increase the compatibility percentages themselves.

This approximately doubles egg-generation opportunities while preserving the difference between poor and strong pairings.

## 11. Hatch-speed policy

Reduce every breedable species' hatch-cycle requirement to:

**ceil(vanilla_hatch_cycles / 2)**

with a minimum of **5 cycles**.

Flame Body and Magma Armor retain their current effect of subtracting two hatch cycles per cycle event.

Result:
- ordinary eggs hatch in roughly half the vanilla walking requirement;
- a Flame Body/Magma Armor helper remains meaningfully faster;
- extremely fast species do not collapse to near-zero hatch time.

Do not alter legendary/Undiscovered species merely because they have hatch-cycle data.

## 12. Day Care access and breeder supplies

Keep the Day Care in Solaceon rather than creating a redundant earlier facility.

Its usefulness improves through:
- faster egg production;
- faster hatching;
- stronger inheritance;
- no-incense babies;
- deterministic Ditto availability from the world/availability phase.

By the Veilstone/Solaceon midgame window, provide renewable access to:
- Everstone;
- all six Power items.

Locked shop values:
- Everstone: keep current ₽200;
- Power items: keep current ₽3,000 each.

Prefer an existing Veilstone/Solaceon vendor rather than a new shop system.

Destiny Knot remains a normal battle/utility item and is not required.

## 13. Ditto

Ditto must have a deterministic normal acquisition path by the time breeding becomes a meaningful midgame option.

The availability phase should ensure this no later than the Hearthome/Solaceon portion of M1.

Ditto must not remain dependent on Trophy Garden rotation or other daily RNG.

Breeding implementation does not create a separate Ditto gift unless the availability spec later explicitly chooses one.

## 14. Form/species special cases

Preserve and test:
- Manaphy → Phione;
- Nidoran male/female offspring behavior;
- Volbeat/Illumise paired offspring behavior;
- Burmy/Wormadam/Mothim form behavior;
- Shellos/Gastrodon form inheritance where current source supports it;
- Rotom breeding restrictions/forms;
- Ditto incompatibility with Ditto;
- Undiscovered egg group restrictions;
- genderless + Ditto rules.

Do not broaden legendary breeding.

## 15. Ball inheritance

Retain Platinum's default Poké Ball result for bred offspring.

Do not import later-generation Poké Ball inheritance in Core 1.0.

This keeps D3 capture-ball identity separate from breeding.

## 16. Shiny breeding

Preserve Platinum's different-language/Masuda behavior.

Nature, ability-slot, and IV improvements must not remove or weaken the existing shiny reroll behavior.

No additional shiny-rate increase is introduced in D4.

## 17. Validation requirements

Breeding implementation must prove:
- Everstone 100% inheritance works for either parent and Ditto;
- both Everstones choose one parent's nature;
- exactly four distinct IV stats are inherited;
- Power-item forced inheritance works and never creates duplicate inherited stat indices;
- ability-slot inheritance follows 80/20 where applicable;
- either parent can pass listed egg moves;
- vanilla TM/HM/shared-level inheritance remains valid;
- no incense is needed for all nine baby families;
- egg-generation interval is 128 steps;
- hatch-cycle tables are halved with minimum 5;
- Flame Body/Magma Armor still accelerate hatching;
- Masuda shiny logic remains intact;
- every legal egg-move chain is achievable in one save;
- no invalid egg-group or species/form result is introduced.

This spec is the canonical D4 breeding authority.
