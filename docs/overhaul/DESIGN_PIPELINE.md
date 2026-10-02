# Remaining Design Pipeline — Pokémon Platinum Overhaul

This file tracks design work that still needs exact subsystem-level specification before Claude Code implementation.

## Workflow rule

For every remaining subsystem:

1. ChatGPT and the user design the subsystem interactively from canonical repo authority and relevant Platinum/Emerald source.
2. Draft decisions are revised in chat until the user approves them.
3. Approval is immediately captured in the repository as:
   - a canonical locked design/spec; and
   - a complete Claude-ready implementation plan.
4. Data-heavy systems also receive machine-readable manifests/schemas when practical.
5. Only then may Claude implement.
6. Claude validates/builds/tests and updates `docs/overhaul/STATUS.md`.

Chat-only approval is not sufficient implementation authority.

## Remaining design order

### D1 — Trainer Overhaul
Status: `IMPLEMENTED` and merged (PR #19; source + validator + Rev 0/Rev 1 CI build; `VERIFIED` only after runtime trainer QA)

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

Locked and implemented from `docs/overhaul/trainers/` (level curve, archetype rules, exact Gym/Rival/Galactic/E4/Cynthia teams, moves/items/AI policy, rematch tables, validators, batching). Manifests: `docs/overhaul/implementation/trainers/`. Runtime trainer QA pending.

### D2 — EXP, Money, Shops, and Item Economy
Status: `LOCKED SPEC`

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
Status: `IMPLEMENTED` (PR #17 merged; runtime QA pending)

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
Status: `IMPLEMENTED` and merged (PR #18; source/validator/harness verified; CI build; runtime QA pending, not VERIFIED)

Canonical authority:
- `docs/overhaul/breeding/BREEDING_SPEC.md`
- `docs/overhaul/breeding/BREEDING_IMPLEMENTATION_PLAN.md`

Resolved design includes nature/IV/ability inheritance, Power-item targeting, no-incense babies, egg-move inheritance policy, hatch/egg-generation speed, breeding-supply access, and one-save legality validation.

### D5 — Legendary/Mythical Events
Status: `IMPLEMENTED` (source + validator + Rev 0/Rev 1 builds; runtime event QA pending — not `VERIFIED`)

Authority: `docs/overhaul/events/LEGENDARY_MYTHICAL_SPEC.md` + `LEGENDARY_MYTHICAL_IMPLEMENTATION_PLAN.md`.
Implementation record: `docs/overhaul/implementation/events/` (five manifests + `LEGENDARY_EVENT_VALIDATION_REPORT.md`);
validator `tools/overhaul/validate_legendary_availability.py` (51 checks, 46 mutation cases + baseline in `tools/overhaul/events/`).

Implemented: native Sinnoh retry safety (Uxie, Azelf, Mesprit, Cresselia, Giratina, Dialga, Palkia, Heatran, Regigigas);
Rotom/Darkrai/Shaymin/Arceus distribution gates removed with in-game unlocks (Sailor Eldritch Member Card, Oak's Letter on Route 224,
Rowan's Azure Flute after a #001–#492 caught check); Sailor Eldritch Manaphy Egg gift (Phione via Breeding 2.0); Regi ruins and
Regigigas without the event Regigigas; renewable post-Hall-of-Fame habitats for the 14 Gen I–III legends; Mew/Celebi/Jirachi/Deoxys
retry-safe statics.

Runtime QA remains for the final overhaul playtest (see the validation report).

### D6 — Battle Frontier, Rematches, and Postgame Rewards
Status: `LOCKED SPEC`

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
Status: `LOCKED SPEC`

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

**All currently identified remaining design phases D1–D7 are now LOCKED. The project is ready to proceed through implementation sequencing from canonical repo authority.**

Legendary/Mythical authority:
- `docs/overhaul/events/LEGENDARY_MYTHICAL_EVENT_SPEC.md`
- `docs/overhaul/events/LEGENDARY_MYTHICAL_IMPLEMENTATION_PLAN.md`

D3 authority:
- `docs/overhaul/pokeballs/POKE_BALL_REBALANCE_SPEC.md`
- `docs/overhaul/pokeballs/POKE_BALL_IMPLEMENTATION_PLAN.md`

Economy authority:
- `docs/overhaul/economy/EXP_ECONOMY_SPEC.md`
- `docs/overhaul/economy/EXP_ECONOMY_IMPLEMENTATION_PLAN.md`

Trainer authority:
- `docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md`
- `docs/overhaul/trainers/TRAINER_IMPLEMENTATION_PLAN.md`

D4 authority:
- `docs/overhaul/breeding/BREEDING_SPEC.md`
- `docs/overhaul/breeding/BREEDING_IMPLEMENTATION_PLAN.md`


D6 authority:
- `docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md`
- `docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_IMPLEMENTATION_PLAN.md`


D7 authority:
- `docs/overhaul/qa/FINAL_INTEGRATION_QA_SPEC.md`
- `docs/overhaul/qa/FINAL_INTEGRATION_QA_IMPLEMENTATION_PLAN.md`


D5 authority:
- `docs/overhaul/events/LEGENDARY_MYTHICAL_EVENT_SPEC.md`
- `docs/overhaul/events/LEGENDARY_MYTHICAL_IMPLEMENTATION_PLAN.md`
