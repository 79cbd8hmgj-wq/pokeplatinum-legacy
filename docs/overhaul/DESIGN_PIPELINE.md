# Remaining Design Pipeline — Pokémon Platinum Overhaul

This file tracks design work that still needs exact subsystem-level specification before Claude Code implementation.

## Workflow rule

For every remaining subsystem:

1. Codex `/plan` reads canonical repo authority and relevant Platinum/Emerald source.
2. Codex produces a `DRAFT PLAN` containing only genuinely unresolved decisions.
3. User approves/rejects the decisions.
4. Approval is immediately captured in the repository as:
   - a canonical locked design/spec; and
   - a complete Claude-ready implementation plan.
5. Data-heavy systems also receive machine-readable manifests/schemas when practical.
6. Only then may Claude implement.
7. Claude validates/builds/tests and updates `docs/overhaul/STATUS.md`.

Chat-only approval is not sufficient implementation authority.

## Remaining design order

### D1 — Trainer Overhaul
Status: `LOCKED SPEC`

Existing authority:
- stronger, coherent teams without becoming a hardcore-only hack;
- important trainers use held items and sensible coverage;
- levels follow a reasonably exploring, low-grind player;
- Rival develops around starter choice;
- Galactic commanders/bosses receive stronger identities;
- Elite Four use broader legal species/type coverage;
- Cynthia remains the main-story benchmark;
- rematches use stronger National Dex teams;
- ordinary trainers should showcase expanded species/mechanics.

Still needed:
- level curve;
- ordinary-trainer archetype rules;
- exact Gym/Rival/Galactic/E4/Cynthia teams;
- moves/items/AI policy;
- rematch tables;
- legality/progression validators;
- implementation batching.

### D2 — EXP, Money, Shops, and Item Economy
Status: `NEEDS EXACT VALUES`

Existing authority:
- Platinum's own level/EXP progression is the baseline; Emerald is precedent for philosophy/mechanics, not a source of Platinum trainer level values;
- final scaling must explicitly model team-wide EXP sharing and a normally rotating party rather than single-recipient vanilla EXP assumptions;
- reduce grind without trivializing progression;
- earlier/additional Exp. Share access;
- improved trainer payouts;
- lower-cost basic healing/evolution supplies;
- vitamins substantially cheaper;
- practical move relearning/tutoring;
- controlled repeatable money;
- exploration/late-game Rare Candy access;
- improved BP economy.

Still needed:
- exact EXP behavior/multipliers;
- trainer payout curve;
- shop inventories and price tables;
- field/reward redistribution;
- money-source limits;
- Rare Candy/vitamin/tutor pricing and timing;
- machine-readable economy manifests.

### D3 — Poké Ball Rebalance
Status: `NEEDS PLATINUM FINAL TABLE`

Existing authority:
- Quick Ball strong turn-one identity;
- Timer Ball reaches strong value sooner;
- Repeat Ball improved for caught species;
- Heal Ball improved;
- fishing/water ball identity;
- Dusk Ball checked for over-dominance;
- Great/specialist balls earlier;
- Ultra Ball remains dependable late default.

Still needed:
- exact multipliers/effect formulas;
- exact item identities/slots;
- availability/pricing;
- Gen IV engine feasibility;
- capture-regression tests.

### D4 — Breeding 2.0
Status: `NEEDS GEN-IV FINALIZATION`

Existing authority:
- breeding should be meaningful rather than postgame paperwork;
- no-incense baby breeding rule is part of locked evolution/species work;
- reduced hatch friction;
- egg-group cleanup/expansion;
- broader useful inheritance;
- improved parent access;
- earlier Day Care usefulness;
- egg moves refine rather than repair;
- experimental cross-type/variant offspring are deferred.

Still needed:
- exact hatch-cycle policy;
- exact IV/nature/ability inheritance rules to port/adapt from Emerald;
- egg-group changes;
- final egg-move framework;
- Day Care access/reward changes;
- legality validator and one-save inheritance audit.

### D5 — Legendary/Mythical Events
Status: `ARCHITECTURE EXISTS; NEEDS EXACT EVENT SPECS`

Existing authority:
- Darkrai via Member Card/Newmoon Island;
- Shaymin via Oak's Letter/Seabreak Path;
- Arceus via Azure Flute/Hall of Origin;
- Rotom room/form access restored in-game;
- Regis obtainable without external event Regigigas;
- Regigigas after Regis;
- Manaphy receives an in-save path;
- Phione through breeding;
- Dialga/Palkia use Platinum postgame infrastructure;
- birds retain/improve native roaming;
- migration/version/event-only legends become proper in-save quests;
- no external distribution/hardware/network required.

Still needed:
- per-event prerequisites;
- exact flags/scripts/items/NPCs;
- retry/respawn behavior;
- ordering and level scaling;
- completion validation.

### D6 — Battle Frontier, Rematches, and Postgame Rewards
Status: `NEEDS DETAILED DESIGN`

Existing authority:
- better BP rewards;
- stronger National Dex rematches;
- postgame encounter cleanup/convenience;
- completion rewards;
- preserve Frontier identity rather than bypassing it.

Still needed:
- BP payout curve;
- complete Frontier shop/reward table;
- rematch schedule/team structure;
- postgame shops/items;
- completion rewards;
- optional convenience systems.

### D7 — Final Integration / QA
Status: `NEEDS FINAL SPEC AFTER SYSTEMS LOCK`

Must validate:
- all 493 eventual availability;
- all nonlegendary family pre-E4 access;
- every evolution achievable in one save;
- no external hardware/network/multiplayer dependency;
- no progression softlocks;
- trainer legality;
- moveset compatibility;
- encounter rates/density;
- economy progression;
- event retries;
- save compatibility where supported;
- US Rev 0 / Rev 1 builds;
- focused runtime QA.

## Current next design

**D2 — EXP, Money, Shops, and Item Economy** is the next design phase.

Trainer authority:
- `docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md`
- `docs/overhaul/trainers/TRAINER_IMPLEMENTATION_PLAN.md`