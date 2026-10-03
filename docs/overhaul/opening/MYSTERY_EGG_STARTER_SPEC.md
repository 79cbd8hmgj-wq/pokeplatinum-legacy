# Pokémon Platinum Overhaul — Mystery Egg Starter Spec

Status: **LOCKED SPEC**

Authority: user-approved design, 2026-10-02.

This phase replaces the traditional three-species starter choice with a hidden weighted draw from Generation I–IV starter Pokémon plus Pikachu.

## 1. Design goal

The opening starter choice should feel uncertain and replayable without becoming arbitrary or unfair.

The player still makes a visible choice among three options, but all three options are mechanically identical **Mystery Eggs**. The selected position does not correspond to a type, species, rarity tier, or predetermined result.

The player's actual starter is determined only after an egg is confirmed.

## 2. Starter pool

The draw contains exactly these 13 species:

### Generation I
- Bulbasaur
- Charmander
- Squirtle

### Special
- Pikachu

### Generation II
- Chikorita
- Cyndaquil
- Totodile

### Generation III
- Treecko
- Torchic
- Mudkip

### Generation IV
- Turtwig
- Chimchar
- Piplup

No Eevee or other non-listed Pokémon are part of this starter draw.

Pikachu is the direct hatch result. It does **not** become Pichu for this special scripted starter event.

## 3. Locked probabilities

| Species | Probability |
|---|---:|
| Bulbasaur | 3% |
| Charmander | 3% |
| Squirtle | 3% |
| Pikachu | 1% |
| Chikorita | 10% |
| Cyndaquil | 10% |
| Totodile | 10% |
| Treecko | 10% |
| Torchic | 10% |
| Mudkip | 10% |
| Turtwig | 10% |
| Chimchar | 10% |
| Piplup | 10% |

Total: **100%**.

Group totals:
- Generation I starters: **9%**
- Pikachu: **1%**
- Generations II–IV starters: **90%**

Interpretation:
- any Gen I starter is roughly a 1-in-11 result;
- Pikachu is a 1-in-100 result;
- every Gen II–IV starter is individually 10%.

These values are locked.

## 4. Three identical eggs

The starter-selection scene must present **three visually identical Mystery Eggs**.

Rules:
- left, center, and right use the same visual;
- all three use the same weighted table;
- no slot has a hidden type or rarity bias;
- no species is preassigned to an egg before the player confirms one;
- moving the cursor between eggs must reveal no species preview;
- confirmation text must not disclose the result.

The species RNG roll occurs **once**, after the player confirms an egg.

## 5. RNG and save resetting

The selected starter is rolled once and then permanently bound to that selection.

Do not reroll:
- during the hatch scene;
- when returning to the field;
- when entering battle;
- when saving after selection.

Resetting the game to a save made **before** the egg is selected is allowed to produce a new draw. No anti-save-scumming system is required.

## 6. Opening-flow integration

Current Platinum source awards a level-5 starter from the Route 201 briefcase and then immediately proceeds into Barry's first battle.

Canonical source:
- res/field/scripts/scripts_route_201.s
- src/choose_starter/choose_starter_app.c

Because the first Rival battle occurs immediately after the selection sequence, the Mystery Egg must hatch **before that battle begins**.

Locked flow:

1. Rowan offers the briefcase.
2. The choice interface presents three identical Mystery Eggs.
3. Player confirms one egg.
4. The weighted 13-species draw runs exactly once.
5. The selected species is bound to the special starter egg.
6. The scene returns to Route 201.
7. The special egg immediately enters a scripted/native hatch reveal.
8. The resulting Pokémon is made battle-ready at **level 5**.
9. Rowan/counterpart departure proceeds.
10. Barry challenges the player as normal.
11. The first battle and all later story progression continue without requiring an unhatched egg.

This special scripted starter egg is exempt from ordinary breeding hatch-cycle rules. Breeding 2.0 remains unchanged.

## 7. Starter Pokémon state

The Mystery Egg result must produce a normal legal Pokémon of the rolled species, with the special opening adjustment that it enters play at **level 5**.

Preserve normal engine generation behavior wherever practical for:
- personality;
- nature;
- gender;
- IVs;
- shiny legality;
- ability slot;
- language/OT/met data.

Do not introduce:
- guaranteed IVs;
- forced nature;
- forced gender;
- guaranteed shiny;
- hidden abilities;
- special moves not already legal for the species.

The starter must be fully usable in the first Rival battle.

## 8. Rival branch mapping

The merged Trainer Overhaul contains three persistent Rival progression branches built around the original Sinnoh starter relationship. This feature must preserve those branches rather than creating 13 new Rival campaigns.

Map the player's random starter to the existing branch key by elemental family:

### Grass results → Turtwig branch
- Bulbasaur
- Chikorita
- Treecko
- Turtwig

Barry therefore follows the existing branch in which his starter is Chimchar.

### Fire results → Chimchar branch
- Charmander
- Cyndaquil
- Torchic
- Chimchar

Barry follows the existing branch in which his starter is Piplup.

### Water results → Piplup branch
- Squirtle
- Totodile
- Mudkip
- Piplup

Barry follows the existing branch in which his starter is Turtwig.

### Pikachu → Piplup branch

Pikachu maps to the Piplup branch so Barry receives Turtwig, giving the special result a sensible early defensive matchup without creating a fourth Rival branch.

The egg's screen position must not control Rival branch selection.

## 9. Player starter identity

The game must retain both concepts where needed:

1. **actual starter species** — the Pokémon the player hatched;
2. **Rival branch key** — Turtwig / Chimchar / Piplup compatibility branch used by existing story/trainer logic.

Do not overwrite the actual starter identity with the branch representative if doing so would make scripts, records, dialogue, Pokédex state, or later logic believe the player actually received a different Pokémon.

Implementation should use the smallest safe separation between actual species and branch key.

## 10. UI and text

The existing starter app currently shows three Poké Ball choices and species previews.

Target presentation:
- replace the three visible choices with identical egg presentation;
- suppress species previews;
- use neutral Mystery Egg wording;
- preserve cursor movement and confirmation UX where practical;
- do not imply Grass / Fire / Water;
- reveal the species only at hatch.

Prefer existing Pokémon Egg art/assets already present in Platinum rather than introducing new custom art.

New text should be short and in Platinum's tone.

## 11. Compatibility requirements

This feature must preserve:
- the Route 201 opening sequence;
- Barry's first battle;
- all three existing Rival progression branches;
- Trainer Overhaul teams;
- all #001–#493 availability guarantees;
- breeding rules;
- starter-family availability elsewhere in the game;
- Pokédex completion;
- save integrity;
- US Rev 0 and Rev 1 builds.

It must not remove later acquisition paths for the other starter families.

## 12. Validation requirements

At minimum, prove:

- probability table totals 100%;
- all 13 species are reachable;
- exact weights are 3/3/3/1/10×9;
- all three egg positions call the same draw;
- one confirmed choice triggers exactly one RNG draw;
- result persists after the draw;
- species is not previewed before hatch;
- hatch completes before Barry's first battle;
- result is level 5;
- Grass results select Turtwig Rival branch;
- Fire results select Chimchar Rival branch;
- Water results select Piplup Rival branch;
- Pikachu selects Piplup Rival branch;
- no 13-way Rival duplication is introduced;
- ordinary breeding egg behavior is unchanged;
- all previous overhaul validators continue to pass.

## 13. Runtime QA

Required representative runtime cases:

- left egg;
- center egg;
- right egg;
- one Gen II–IV result;
- one Gen I result;
- Pikachu result using deterministic/debug RNG support;
- immediate hatch scene;
- first Barry battle;
- one later Barry encounter for each of the three branch categories;
- save/reset before selection produces a new eligible roll;
- save after selection does not reroll the bound result.

Runtime probability testing may use a deterministic host/model harness rather than manually resetting hundreds of times.

## 14. Scope boundary

This phase is an opening-system overhaul only.

Do not use it to redesign:
- later starter gifts;
- ordinary egg mechanics;
- Rival teams;
- trainer level curves;
- starter learnsets;
- starter stats/abilities;
- general RNG.

Any defect discovered in those systems should be reported to its owning subsystem rather than silently redesigned here.
