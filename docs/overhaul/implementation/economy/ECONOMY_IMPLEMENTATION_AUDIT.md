# EXP / Economy Implementation Audit

Starting SHA (latest `main`, PR #15 merged): `447833b79fa5c0456d60bcbd8ec03ec109d92c23`
Authority: `docs/overhaul/economy/EXP_ECONOMY_SPEC.md`, `EXP_ECONOMY_IMPLEMENTATION_PLAN.md`.
Manifest: `economy_manifest.json` (23 price/prize edits, 38 tutor entries, plus EXP/Reminder/stone/Rare Candy records).
Runtime/emulator QA: **DEFERRED TO FINAL OVERHAUL PLAYTEST**.

## EXP (`src/battle/battle_script.c`)

* `BtlCmd_CalcExpGain` keeps the raw pool `base_exp_reward * level / 7`, then splits it
  `battle_pool = raw * 60 / 100`, `team_pool = raw - battle_pool` (`EXP_BATTLE_POOL_PERCENT`, `include/constants/battle.h`).
* Eligible = valid species, not Egg, HP > 0, level < 100. Battle group = unique union of actual participants
  (`sideGetExpMask`) and eligible Exp. Share holders (counted once however many Exp. Shares / participation).
* Battle pool is divided among the battle group, team pool among **all** eligible members; battle members get both shares.
  If no eligible battle-group member remains (for example all participants are fainted/Lv100 and no eligible Exp. Share holder exists),
  the 60% battle pool is folded into the team pool so the raw pool is still conserved among eligible recipients.
* Remainders: lowest party slots first, independently for each pool, so pre-modifier allocations sum to `raw` exactly.
  Legacy minimum of 1 EXP applies only to a battle-group member whose total would be 0 (can exceed `raw` only when
  `battle_pool < battle group size`, i.e. raw pools of a few EXP).
* Results land in `BattleContext.expAlloc[slot]` plus `expRecipientMask` (replacing `gainedExp`/`sharedExp`).
  `BattleScript_GetExpTask` iterates the recipient mask, so every eligible member goes through the unchanged EXP message,
  gauge, level-up, move-learning and post-battle-evolution path. Individual modifiers (Lucky Egg, trainer 1.5x,
  same-language 1.5x / foreign 1.7x traded) are untouched and still applied per recipient after allocation.
* EVs: `BattleScript_CalcEffortValues` now runs only for actual participants. Team-share-only and bench Exp. Share
  holders earn none; Pokerus/Macho Brace/Power items are handled inside the unchanged EV routine.
* Growth tables untouched. No Emerald multipliers.

## Economy

| Area | File(s) | Change |
|---|---|---|
| Prize multipliers | `include/data/trainer_class_prize_mul.h` | Tuber M/F 1→3, Poké Kid 2→4, Ninja Boy 2→4; formula untouched |
| Healing/vitamins | `res/items/data/*.json` | Potion 200, Super 500, Hyper 900, Max 2000, Full Restore 2500, Revive 1200; six vitamins 4900 |
| Status medicines | same | `ceil(0.75·vanilla / 50)·50`: Antidote 100 (no clean value in 75–80%, unchanged), Burn/Ice Heal & Awakening 250→200, Parlyz Heal 200→150, Full Heal 600→450 |
| Move Reminder | `scripts_pastoria_city_east_house.s`, text JSON | Heart Scale check/consume removed; eligibility, selection, cancel/egg/no-move branches kept; dialogue updated |
| Tutors | `res/pokemon/move_tutors.json` | every nonzero shard cost → `ceil(old/2)` (38 entries); moves/locations/colour identity unchanged; the C engine reads this table with no cost literals |
| Evolution stones | `include/data/mart_items.h` (`VeilstoneDeptStoreStock_2F_MID`) | Fire/Water/Thunder/Leaf/Moon/Sun/Shiny/Dusk/Dawn appended at base 2100; existing Veilstone vendor, no new shop engine |
| Rare Candy | `mart_items.h`, `generated/mart_specialties_id.txt`, `scripts_fight_area_mart.s`, `rare_candy.json` | postgame-only unlimited stock (`FLAG_GAME_COMPLETED`) at the Fight Area mart's Clown, 4800→5000 |

Stone audit: the merged evolution manifest consumes exactly nine stones (Moon 5 edges, Water 4, Leaf 4, Fire 3, Thunder 2,
Sun 2, Dawn 2, Dusk 2, Shiny 2); all nine are in the new stock. The Veilstone Department Store is open from Veilstone arrival
(4th-badge window) with no postgame gate. Oval Stone is not required (Happiny→Chansey is level/daytime).

Rare Candy price: 5000 chosen. The item JSON price only drives purchase price and the 50% sell value (2400→2500);
nothing else reads it. Finite campaign sources (field pickups, gifts, Frontier BP exchange) are unchanged; no pre-E4
shop sells it.

## Progression simulation (`tools/overhaul/economy/simulate_progression.py`, output `progression_simulation.json`)

Calibration model only. Findings relative to locked targets (average party level vs ace):

* direct: 12 flags (model puts a 5-member rotation 3–27 below ace);
* normal: within target through Maylene/Wake (+1.4…−2.7), then falls 4.7–14 below from Byron onward;
* completionist: +2.3…+6 above ace at Roark–Wake, then falls below from Volkner.

Team-wide EXP changes the vanilla curve by only ~+1…+3 levels (conserved pool, as designed). The late-game gap is
**not** caused by the economy change: the vanilla baseline shows the same shortfall. Contributing model limits: few
ordinary trainers exist in the late ace-level buckets (6–9 for Aaron/Cynthia), no rematches/postgame trainers, wild
EXP uses a flat per-segment KO count, mandatory vs optional trainers are not tagged in data. Live Fantina ace is 26
vs locked 27. Per the plan these are **reported for the trainer phase**; no trainer level was changed in this PR.

## Discrepancies / blockers

None blocking. Items for later phases: trainer-level calibration (above), Poké Ball rebalance (next source task).
Validators for created moves / C3 species have no standalone scripts; C2 (which re-checks TM21/TM78 recipient masks) and
C1 pass.
