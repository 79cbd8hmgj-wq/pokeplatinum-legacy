# Pokémon Platinum Overhaul — EXP/Economy Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority: `docs/overhaul/economy/EXP_ECONOMY_SPEC.md`

Claude Code implements this spec; it does not redesign the EXP formula or economy.

## 1. Source targets already confirmed

### EXP
Primary logic:
- `src/battle/battle_script.c`
  - `BtlCmd_CalcExpGain`
  - `BattleScript_GetExpTask`

Current source computes:
- raw EXP = base EXP reward × defeated level / 7;
- vanilla Exp. Share 50/50 split;
- Lucky Egg individual 1.5x;
- trainer-battle individual 1.5x;
- traded bonuses 1.5x / 1.7x.

Growth tables:
- `res/pokemon/.shared/exp_tables.csv`

Do not modify growth-rate tables.

### Prize money
- `src/battle/battle_script.c::BattleScript_CalcPrizeMoney`
- `include/data/trainer_class_prize_mul.h`

Preserve formula; change only the three locked class multipliers.

### Item prices
- `res/items/data/*.json`

### Common/special marts
- `include/data/mart_items.h`
- field mart scripts under `res/field/scripts/scripts_*_mart.s`

### Move Reminder
- Pastoria Move Reminder scripts/application; locate exact payment script before editing.
- Move-list logic under `src/move_reminder_data.c` does not itself need redesign.

### Move Tutors
- `res/pokemon/move_tutors.json`
- `src/overlay005/scrcmd_move_tutor.c`

## 2. EXP implementation

### E0 — source guard

Before changing code, record the exact current behavior of:
- participant counting;
- Exp. Share counting;
- fainted eligibility;
- Lv100 handling;
- Lucky Egg;
- trainer bonus;
- traded bonus;
- EV grant.

Create regression tests or a small deterministic harness where feasible.

### E1 — allocation data

Implement per-KO counts/sets:
- eligible party set;
- battle-group set = participants ∪ eligible Exp. Share holders.

Do not count a participant twice.

Exclude:
- HP 0;
- Lv100;
- Eggs/invalid species.

### E2 — conserved split

From the raw pre-trainer EXP pool:
- battlePool = floor(raw * 60 / 100);
- teamPool = raw - battlePool so integer remainder is conserved.

Per recipient:
- if in battle group, add battlePool / battleGroupCount;
- if eligible, add teamPool / eligibleCount.

Handle integer remainder deterministically. Prefer distributing remainder without allowing total pre-individual-modifier payout to exceed raw by more than unavoidable legacy minimum-1 behavior.

### E3 — individual modifiers

After allocation preserve current order/behavior for:
- Lucky Egg 1.5x;
- trainer battle 1.5x;
- traded Pokémon bonus.

Do not add wild/trainer overhaul multipliers.

### E4 — EV separation

Current EXP task grants EVs while granting EXP.

Modify the task so:
- actual participants receive EVs;
- team-share-only recipients do not;
- Exp. Share holders that never participated do not receive EVs solely due to global sharing.

Validate Pokerus/Macho Brace/etc. remain correct for participants.

### E5 — messages/UI

Every recipient receiving nonzero EXP must process:
- EXP message;
- gauge update where relevant;
- level-up;
- move learning;
- evolution eligibility after battle as current engine expects.

Avoid excessive delays if six party members receive EXP. Preserve correctness first; optimize message pacing only if needed.

## 3. EXP simulation tool

Create:
`tools/overhaul/simulate_progression.py`

Inputs should support:
- current trainer manifests;
- current species base EXP yields;
- current level/growth tables;
- configurable party size;
- direct/normal/completionist encounter profiles;
- team-share allocation.

Outputs:
- expected party level bands at each major boss;
- average/median/max levels;
- EXP deficit/surplus to next boss;
- flags where primary profile is >3 below ace or >2 above ace;
- comparison against vanilla/no-team-share baseline.

This is a calibration model, not a claim to perfectly reproduce human play.

Do not finalize trainer-level adjustments until this report exists.

## 4. Economy manifest

Create:
`docs/overhaul/implementation/economy/economy_manifest.json`

Include:
- item price changes;
- trainer class prize multipliers;
- move tutor shard costs;
- Move Reminder cost;
- evolution-stone shop placement;
- Rare Candy postgame placement;
- source file/path;
- before value;
- target value;
- progression gate.

All edits must be source-guarded.

## 5. Price changes

Apply exact locked prices:
- Potion 200
- Super Potion 500
- Hyper Potion 900
- Max Potion 2000
- Full Restore 2500
- Revive 1200
- vitamins 4900 each.

Generate the status-medicine 75–80% table from current source, round cleanly, and include it in the manifest for review before application. This is mechanical derivation, not a new design choice.

Do not modify Poké Ball prices during D2.

## 6. Prize multipliers

In `include/data/trainer_class_prize_mul.h`:
- Tuber male/female: 1 → 3
- Poké Kid: 2 → 4
- Ninja Boy: 2 → 4

No other class multiplier changes without spec revision.

## 7. Move Reminder

Locate the actual Pastoria payment script.

Remove the Heart Scale requirement/payment while preserving:
- eligibility check;
- move selection;
- refusal/cancel behavior;
- dialogue flow.

Update dialogue so it no longer claims a Heart Scale is required.

Do not alter which moves are eligible for reminder.

## 8. Move Tutors

For every entry in `res/pokemon/move_tutors.json`:
- each nonzero color cost becomes ceil(old / 2);
- zero stays zero.

Validator must verify:
- move/location unchanged;
- only shard-cost fields changed;
- every resulting paid tutor still costs at least one shard.

## 9. Evolution-stone shop

Audit every evolution stone used by the locked #001–#493 evolution spec.

Add a repeatable midgame shop source no later than Veilstone.

Prefer an existing Department Store vendor/table rather than creating a new engine/shop system.

Do not add former trade-evolution items as evolution requirements.

Validator must prove every required stone is purchasable pre-E4.

## 10. Rare Candy

Keep campaign finite pickups.

Add unlimited postgame stock at a Battle Zone/postgame shop:
- preferred price 5000;
- if changing base item price causes undesirable sell-value/global side effects, retain current 4800 and document the implementation choice.

Do not add unlimited pre-E4 stock.

## 11. Validation

Create:
`tools/overhaul/validate_economy.py`

Fail on:
- wrong locked item price;
- unintended Poké Ball price edits;
- unapproved trainer class multiplier edits;
- tutor cost not equal to ceil(vanilla/2);
- Move Reminder still consuming Heart Scale;
- required evolution stone without repeatable pre-E4 source;
- Rare Candy unlimited source before postgame;
- Emerald EXP multipliers present.

Generate:
`docs/overhaul/implementation/economy/ECONOMY_VALIDATION_REPORT.md`

## 12. Runtime tests

At minimum test:
- one wild KO with 1, 3, and 6 eligible party members;
- one trainer KO with 6 eligible members;
- switched battle with two participants;
- one benched Exp. Share holder;
- multiple Exp. Share holders;
- participant also holding Exp. Share;
- Lucky Egg holder;
- traded Pokémon;
- fainted party member;
- Lv100 party member;
- level-up + move learning for a benched team-share recipient;
- EV result for participant vs team-share-only member;
- payout from changed low-prize trainer classes;
- Move Reminder free flow;
- representative shard tutor payment;
- evolution-stone purchase;
- postgame Rare Candy purchase.

For EXP tests, assert exact numeric payout.

## 13. Build / sequencing

Recommended commits:
1. manifests + validators + simulation;
2. team-wide EXP;
3. EXP runtime tests/calibration report;
4. prize-money cleanup;
5. healing/vitamin prices;
6. Move Reminder/tutor costs;
7. evolution-stone + postgame convenience stock;
8. final dual-revision build and STATUS update.

Build both supported US revisions after each engine-affecting EXP batch and at final integration.

## 14. Trainer calibration handoff

After progression simulation:
- compare results to `docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md`;
- only small level changes justified by simulation are allowed;
- do not alter trainer species/team identity as an economy fix;
- record any level adjustment and evidence in both trainer/economy validation reports.

## 15. Completion status

Mark D2:
- `IMPLEMENTING` when edits begin;
- `IMPLEMENTED` after source changes + both builds;
- `VERIFIED` only after numeric EXP runtime checks, economy checks, and progression simulation pass.
