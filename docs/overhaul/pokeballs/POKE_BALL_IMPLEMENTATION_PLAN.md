# Pokémon Platinum Overhaul — Poké Ball Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority: `docs/overhaul/pokeballs/POKE_BALL_REBALANCE_SPEC.md`.

Claude Code implements this spec; it does not redesign capture balance.

## 1. Confirmed source target

Primary capture logic:
- `src/battle/battle_script.c`
- function: `BattleScript_CalcCatchShakes`

Current source already handles:
- Net Ball;
- Dive Ball;
- Nest Ball;
- Repeat Ball;
- Timer Ball;
- Dusk Ball;
- Quick Ball;
- standard ball multipliers;
- Safari handling;
- Master Ball guarantee.

This phase should remain a small source-level capture-formula change.

## 2. Manifest

Create:

`docs/overhaul/implementation/pokeballs/pokeball_manifest.json`

Fields:
- ball;
- trigger;
- vanilla modifier/formula;
- target modifier/formula;
- item price;
- earliest shop gate;
- source location;
- before guard.

Create:

`docs/overhaul/implementation/pokeballs/pokeball_shop_manifest.json`

for vendor/badge availability.

## 3. Formula edits

Implement exact locked values:

- Net qualifying: 35 / 10.
- Dive qualifying: 40 / 10.
- Repeat qualifying: 35 / 10.
- Dusk qualifying: 30 / 10.
- Quick first turn: 50 / 10.
- Heal: 15 / 10 universally.
- Timer: `10 + 3 * totalTurns`, cap 40.
- Nest: level-ratio thresholds:
  - < target: 10;
  - >= target: 20;
  - >= 2x: 35;
  - >= 4x: 50.

Use integer modifier units consistent with current source.

Do not modify:
- Poke;
- Great;
- Ultra;
- Safari;
- Master;
- status catch bonuses;
- HP catch factor.

## 4. Heal Ball handling

Because Heal Ball currently has no special catch-rate branch in the central switch, add the 1.5x modifier there.

Audit the existing post-capture Heal Ball effect and preserve it exactly.

If healing behavior is implemented elsewhere, do not duplicate it.

## 5. Dive Ball environment

Use existing water-terrain trigger as the required implementation.

Optionally inspect whether a stable fishing encounter flag is already available in battle context.

Only add fishing as an extra trigger if:
- the flag is explicit and reliable;
- no new encounter plumbing is required.

Do not broaden scope to build fishing-state transport just for Dive Ball.

## 6. Nest Ball implementation

Replace the current target-level formula with active-player-level comparison.

Use the actual active battler selected at throw time.

Test:
- equal level;
- 2x threshold;
- 4x threshold;
- lower-level player;
- doubles if Poké Ball throwing can occur there.

## 7. Shop availability

Use existing common/specialty mart infrastructure.

Implement:
- Poké Ball + Great Ball + Heal Ball in the opening common-Mart tier;
- Quick Ball in Jubilife, before Badge 1;
- Timer Ball in Oreburgh, around the first badge;
- preserve Net Ball as the Water/Bug target specialist from Oreburgh/Floaroma onward;
- introduce Nest Ball (Level Ball role) and Dive Ball (Lure/water-environment role) by Eterna;
- introduce Dusk Ball after the earliest specialist wave, around Hearthome/Solaceon;
- introduce Repeat Ball by Solaceon/early-midgame;
- keep Quick/Timer and other earlier specialist tools available in later regional marts rather than removing them as the story advances;
- Ultra Ball by roughly the third-to-fourth badge tier;
- keep Luxury Ball as a later flavor/friendship option;
- ensure League shop sells the broad specialist set.

Avoid replacing each city's specialty identity with a universal list; the goal is overlapping, progressively richer specialist access.

## 8. Prices

Validator must confirm no D3 price changes beyond canonical values:
- Poke 200
- Great 600
- Ultra 1200
- Heal 300
- Net/Nest/Dusk/Quick/Timer/Repeat/Dive/Luxury 1000

Premier pricing is not gameplay-significant unless directly sold.

## 9. Descriptions

Update item descriptions only where mechanics materially changed:

- Heal Ball: mention improved catch performance only if text space permits naturally.
- Nest Ball: retain "weaker Pokémon" language; exact thresholds need not be printed.
- Timer Ball: current wording remains accurate.
- Repeat/Net/Dive/Dusk/Quick: existing descriptions remain semantically accurate.

Do not clutter descriptions with raw multipliers unless project style requires it.

## 10. Validator

Create:

`tools/overhaul/validate_pokeballs.py`

It must verify:
- source modifier constants/formulas;
- shop availability;
- prices;
- no changes to base catch formula/status bonuses;
- no accidental changes to Safari/Master;
- manifest/source agreement.

Generate:
`docs/overhaul/implementation/pokeballs/POKEBALL_VALIDATION_REPORT.md`.

## 11. Deterministic tests

Add unit/harness tests where feasible for calculated modifier values independent of RNG.

Required cases:
- Net Water;
- Net Bug;
- Net unrelated;
- Dive water/non-water;
- Nest ratios 0.5x, 1x, 2x, 4x;
- Repeat caught/uncaught;
- Timer turns 0/1/5/10/30;
- Dusk day/night/cave;
- Quick first/later;
- Heal;
- Great/Ultra unchanged.

For full catch-shake tests, use controlled RNG or compare computed catch-rate intermediates if the repo test framework permits.

## 12. Runtime smoke tests

At minimum:
- first-turn Quick catch attempt;
- long Timer attempt;
- day and cave Dusk;
- caught-species Repeat;
- low-level target Nest;
- water-terrain Dive;
- Heal Ball capture followed by checking HP/status;
- standard Great/Ultra comparison.

## 13. Build and commits

Recommended:
1. manifest + validator;
2. capture modifiers;
3. Nest/Heal special logic;
4. shop availability;
5. descriptions;
6. tests + validation report;
7. Rev 0 / Rev 1 builds + STATUS update.

## 14. Acceptance

D3 reaches VERIFIED only when:
- formula validator passes;
- shop validator passes;
- standard catch formula remains unchanged outside ball modifiers;
- both US revisions build;
- runtime smoke tests pass;
- STATUS records evidence.

Any engine ambiguity must be reported rather than silently changing the spec.
