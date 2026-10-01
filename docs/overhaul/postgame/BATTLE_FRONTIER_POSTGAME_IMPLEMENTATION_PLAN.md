# Pokémon Platinum Overhaul — Battle Frontier & Postgame Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority:
- `docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md`
- `docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md`
- D2 economy authority
- TM/HM BP-price authority

Claude Code implements; it must not redesign Frontier streaks, rewards, or rematch teams.

## 1. Source audit

Map exact source/data for:
- BP award calculations for Tower/Factory/Castle/Arcade/Hall;
- Frontier Brain milestone checks;
- Frontier marts;
- Frontier trainer/Pokémon sets;
- Hall type pools;
- Arcade BP roulette outcomes;
- Castle internal currency;
- Silver/Gold Print save flags;
- Battleground random-trainer selection/reset;
- Rival postgame day-of-week/daily flags;
- League rematch selection;
- Fight Area tag battle.

Known resources include:
- `include/constants/battle_frontier.h`
- `res/field/frontier_scripts/*`
- `res/field/scripts/scripts_battle_frontier.s`
- `res/field/scripts/scripts_battleground.s`
- `res/field/scripts/scripts_fight_area.s`
- `res/trainers/frontier/*`
- ordinary rematch trainer JSONs under `res/trainers/data/`.

## 2. Manifests

Create:
- `docs/overhaul/implementation/postgame/frontier_rewards.json`
- `docs/overhaul/implementation/postgame/frontier_shop_prices.json`
- `docs/overhaul/implementation/postgame/frontier_set_changes.json`
- `docs/overhaul/implementation/postgame/rematch_access.json`
- `docs/overhaul/implementation/postgame/print_rewards.json`

Every changed record includes:
- source path;
- before value;
- target value;
- authority;
- guard.

## 3. F1 — BP payout multiplier

Locate the final BP-credit path for each facility.

Implement **exactly one 2x multiplication** at the latest common safe payout point if possible.

If facilities use separate payout paths, apply equivalent 2x logic individually.

Tests must cover:
- ordinary completed round;
- Silver Brain round;
- Gold Brain round;
- Hall round;
- Arcade 1-BP and 3-BP roulette awards;
- losses/abandoned streaks;
- Castle Point usage.

Do not double Castle Points or any non-BP score.

## 4. F2 — Frontier shops

Apply previously locked TM BP prices exactly.

Keep all other Frontier prices at live-source values unless:
- an item is explicitly duplicated by another locked economy source and the spec authorizes a manifest change.

Validator must diff the full shop table and fail unexpected non-TM edits.

## 5. F3 — Frontier set audit

Generate an audit over all Frontier Pokémon definitions.

Cross-reference:
- current type;
- current base stats;
- current abilities;
- move existence/properties;
- custom-move IDs;
- TM/learnset compatibility only where Frontier legality policy requires it.

Flag:
- wrong-type STAB identity after retype;
- move removed/renamed;
- set made nonsensical by stat redistribution;
- impossible/invalid move constants;
- duplicate/degenerate sets.

Apply targeted fixes only.

Do not regenerate the entire Frontier metagame.

Create a human-readable audit report:
`docs/overhaul/implementation/postgame/FRONTIER_SET_AUDIT.md`.

## 6. F4 — Frontier Brain audit

Review Silver/Gold Brain sets separately.

Make only canonical-overhaul alignment edits.

Preserve:
- encounter numbers;
- facility gimmick;
- overall vanilla difficulty relationship.

## 7. F5 — Battleground reshuffle

Current Battleground uses four slots and daily-generated trainers.

Modify flow so:
- initial visit still produces up to four eligible trainers;
- after current set is resolved, proprietor interaction can request a new group;
- new group can be generated immediately;
- current defeated/declined local state clears safely;
- all eligible trainers can appear without waiting for next date;
- partner prerequisites remain respected.

Prefer extending existing four-slot random-selection code rather than redesigning the map.

Add duplicate-avoidance where source permits cheaply; correctness does not depend on perfect no-repeat randomization.

## 8. F6 — Rival daily rematch

Find postgame Rival scripts, including unused weekend logic where relevant.

Replace Saturday/Sunday requirement with:
- postgame progression prerequisite;
- daily-defeated flag.

Expected:
- available any weekday if not defeated that day;
- after victory, unavailable until normal daily reset;
- starter branch selection preserved.

## 9. F7 — League and Gym rematches

Apply/access already-locked rematch trainer JSONs.

Do not redesign teams.

Validate:
- all 8 leaders reachable through Battleground cycling;
- rematch teams correspond to spec;
- E4/Cynthia rematch state triggers correctly;
- no accidental main-story team replacement before postgame state.

## 10. F8 — Print milestone rewards

Hook first-time Silver/Gold Print acquisition.

Per facility:
- Silver first award: add 10 BP once;
- Gold first award: add 30 BP once.

After all Silver Prints:
- add 50 BP;
- give PP Max;
- set all-Silver reward flag only after successful grant.

After all Gold Prints:
- add 100 BP;
- give Master Ball;
- set all-Gold reward flag only after successful grant.

If bag is full:
- BP portion may be awarded;
- item claim must remain pending/retry-safe.

Do not allow duplicate item claims.

## 11. F9 — Fight Area integration

Audit the Rival/player vs Volkner/Flint tag battle.

Synchronize its trainer references/teams with trainer authority.

Preserve narrative/script flow, Palmer introduction, and route unblock.

## 12. Validator

Create:
`tools/overhaul/validate_postgame.py`

Fail on:
- changed Frontier milestone count;
- BP multiplier not exactly 2x;
- accidental 4x/double application;
- Castle Points altered;
- locked TM BP price mismatch;
- unexpected non-TM shop change;
- illegal Frontier move/species/form;
- missing retype audit;
- Battleground trainer unreachable without calendar wait;
- Rival still weekend-only;
- duplicate Print reward claim path;
- postgame item reward permanently lost to full bag;
- Frontier requirement for species completion.

Generate:
`docs/overhaul/implementation/postgame/POSTGAME_VALIDATION_REPORT.md`.

## 13. Runtime QA

Test:
- one ordinary round in each of five facilities;
- one Silver Brain award;
- one Gold Brain award;
- Arcade BP roulette;
- Castle Point spending/payout;
- TM and held-item Frontier purchase;
- Battleground repeated reshuffle until all eight leaders can appear;
- companion Battleground prerequisite behavior;
- Rival rematch on weekday + daily lockout;
- one full E4/Cynthia rematch run;
- Fight Area tag battle;
- one Silver Print milestone;
- all-Silver reward;
- one Gold Print milestone;
- all-Gold reward with bag space and full-bag retry.

## 14. Build order

Recommended commits:
1. manifests + validators;
2. BP payout;
3. shop table;
4. Frontier set/Brain alignment;
5. Battleground access;
6. Rival/League rematch access;
7. Print rewards;
8. Fight Area integration;
9. final reports/status.

Build US Rev 0 and Rev 1 after BP-engine changes and final integration.

## 15. Status

Update:
- `docs/overhaul/STATUS.md`
- `docs/overhaul/DESIGN_PIPELINE.md`

D6 becomes VERIFIED only after:
- dual-revision builds;
- validator pass;
- representative runtime BP/Frontier/rematch/reward tests.

## 16. Acceptance

Complete when:
- Frontier challenge structure is preserved;
- BP grind is halved via 2x payouts;
- locked TM prices remain correct;
- rematches are readily accessible without weekly waiting;
- Frontier sets are coherent with the overhaul;
- Print rewards work once and safely;
- postgame remains rewarding without gating Pokédex completion.
