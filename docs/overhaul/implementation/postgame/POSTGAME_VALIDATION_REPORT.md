# D6 Postgame Validation Report

Start SHA: `98f9cbdf43f9a8ef4c04c3f80e7ee0b6d9482638`

Result: **119 PASS / 0 FAIL**

Static validation only (source, data, manifests). In-game runtime QA has NOT been performed; D6 is IMPLEMENTED, not VERIFIED.

| Check | Result | Detail |
|---|---|---|
| BP multiplier constant is exactly 2 | PASS | value=2 |
| payout point tower: target present once, multiplier applied once | PASS | target count=1, multiplier uses in file=1 |
| payout point factory: target present once, multiplier applied once | PASS | target count=1, multiplier uses in file=1 |
| payout point castle: target present once, multiplier applied once | PASS | target count=1, multiplier uses in file=1 |
| payout point hall_round: target present once, multiplier applied once | PASS | target count=1, multiplier uses in file=1 |
| payout point arcade_round: target present once, multiplier applied once | PASS | target count=1, multiplier uses in file=1 |
| payout point arcade_roulette: target present once, multiplier applied once | PASS | target count=1, multiplier uses in file=1 |
| payout point hall_record_keeper: target present once, multiplier applied once | PASS | target count=1, multiplier uses in file=1 |
| no stray multiplier use outside manifest payout points (no 4x) | PASS |  |
| exactly 7 multiplier applications across src | PASS | total=7 |
| credit command ScrCmd_GiveBattlePoints unchanged (still 1x) | PASS |  |
| credit command FrontierScrCmd_GiveBattlePoints unchanged (still 1x) | PASS |  |
| base table unchanged: castle BP table | PASS |  |
| base table unchanged: hall BP table | PASS |  |
| base table unchanged: arcade BP table | PASS |  |
| base table unchanged: arcade +1 BP table | PASS |  |
| base table unchanged: arcade +3 BP table | PASS |  |
| Arcade roulette sBonus1BP base starts at 1 -> 2 | PASS | base=[1, 1, 1] |
| Arcade roulette sBonus3BP base starts at 3 -> 6 | PASS | base=[3, 3, 3] |
| Frontier milestone/round constants unchanged | PASS | 9 constants |
| Factory streak literals 21/49 unchanged | PASS |  |
| Castle Points code untouched (only include + BP return changed) | PASS | 3 changed lines |
| locked TM BP price ITEM_TM06=16 | PASS | live=16 |
| locked TM BP price ITEM_TM73=16 | PASS | live=16 |
| locked TM BP price ITEM_TM61=16 | PASS | live=16 |
| locked TM BP price ITEM_TM45=16 | PASS | live=16 |
| locked TM BP price ITEM_TM40=20 | PASS | live=20 |
| locked TM BP price ITEM_TM31=20 | PASS | live=20 |
| locked TM BP price ITEM_TM89=20 | PASS | live=20 |
| locked TM BP price ITEM_TM08=24 | PASS | live=24 |
| locked TM BP price ITEM_TM04=24 | PASS | live=24 |
| locked TM BP price ITEM_TM81=32 | PASS | live=32 |
| locked TM BP price ITEM_TM30=32 | PASS | live=32 |
| locked TM BP price ITEM_TM53=32 | PASS | live=32 |
| locked TM BP price ITEM_TM36=40 | PASS | live=40 |
| locked TM BP price ITEM_TM59=40 | PASS | live=40 |
| locked TM BP price ITEM_TM71=40 | PASS | live=40 |
| locked TM BP price ITEM_TM26=40 | PASS | live=40 |
| no unexpected non-TM shop change (full-table diff) | PASS | {} |
| shop manifest changed_records empty and consistent | PASS |  |
| Frontier set audit: INVALID findings == 0 | PASS |  |
| Frontier set audit: RETYPE findings == 0 | PASS |  |
| Frontier set audit: LOST_STAB findings == 0 | PASS |  |
| Frontier set audit: STAT findings == 0 | PASS |  |
| Frontier set audit: REMOVED findings == 0 | PASS |  |
| Frontier set audit: DUPLICATE findings == 0 | PASS |  |
| all Frontier species/forms valid | PASS |  |
| Frontier set count unchanged (951, no regeneration) | PASS | 951 |
| set-change manifest matches source (no drift) | PASS |  |
| no unmanifested Frontier set edits (no table rebuild) | PASS | extra=[] missing=[] |
| Brain sets audited separately, no unmanifested Brain edits | PASS |  |
| FRONTIER_SET_AUDIT.md exists | PASS |  |
| retype audit covers every retyped Frontier species | PASS |  |
| Hall static type pool matches live species types | PASS |  |
| Battleground reshuffle clears all per-trainer daily defeated flags | PASS | 13/13 |
| Battleground reshuffle resets the daily generation flag | PASS |  |
| Battleground reshuffle re-enters the map (OnTransition regenerates) | PASS |  |
| Battleground reshuffle requires current group resolved | PASS |  |
| Battleground trainers not calendar-locked | PASS |  |
| partner prerequisite unchanged: TryHideCheryl | PASS |  |
| partner prerequisite unchanged: TryHideRiley | PASS |  |
| partner prerequisite unchanged: TryHideMarley | PASS |  |
| partner prerequisite unchanged: TryHideBuck | PASS |  |
| partner prerequisite unchanged: TryHideMira | PASS |  |
| all 8 Gym Leaders in the random pool with a rematch trainer ID | PASS | pool=8 rematch ids=8 |
| leader rematch trainer IDs exist | PASS |  |
| trainer reshuffle avoids previous group (best effort) | PASS |  |
| Rival rematch is not weekend-only | PASS |  |
| Rival daily lock: flag checked first and set on victory | PASS |  |
| Rival starter branches preserved | PASS |  |
| Rival rematch trainer IDs exist | PASS | 6 |
| League rematch trigger aaron | PASS |  |
| League main-story team kept pre-postgame aaron | PASS |  |
| League rematch trigger bertha | PASS |  |
| League main-story team kept pre-postgame bertha | PASS |  |
| League rematch trigger flint | PASS |  |
| League main-story team kept pre-postgame flint | PASS |  |
| League rematch trigger lucian | PASS |  |
| League main-story team kept pre-postgame lucian | PASS |  |
| League rematch trigger champion | PASS |  |
| League main-story team kept pre-postgame champion | PASS |  |
| Fight Area tag battle references resolve to trainer records | PASS | TRAINER_ELITE_FOUR_FLINT_FIGHT_AREA,TRAINER_LEADER_VOLKNER_FIGHT_AREA,TRAINER_RIVAL_FIGHT_AREA_CHIMCHAR,TRAINER_RIVAL_FIGHT_AREA_PIPLUP,TRAINER_RIVAL_FIGHT_AREA |
| Fight Area script untouched (flow/Palmer/route unblock preserved) | PASS |  |
| trainer data present: TRAINER_ELITE_FOUR_FLINT_FIGHT_AREA | PASS |  |
| trainer data present: TRAINER_LEADER_VOLKNER_FIGHT_AREA | PASS |  |
| trainer data present: TRAINER_RIVAL_FIGHT_AREA_CHIMCHAR | PASS |  |
| trainer data present: TRAINER_RIVAL_FIGHT_AREA_PIPLUP | PASS |  |
| trainer data present: TRAINER_RIVAL_FIGHT_AREA_TURTWIG | PASS |  |
| print reward flag exists: FLAG_RECEIVED_FRONTIER_ALL_SILVER_BP | PASS |  |
| print reward flag exists: FLAG_RECEIVED_FRONTIER_ALL_SILVER_PP_MAX | PASS |  |
| print reward flag exists: FLAG_RECEIVED_FRONTIER_ALL_GOLD_BP | PASS |  |
| print reward flag exists: FLAG_RECEIVED_FRONTIER_ALL_GOLD_MASTER_BALL | PASS |  |
| Silver all-print reward ordering (done-guard, BP flag, CanFitItem, AddItem, item flag) | PASS | [45, 691, 780, 954, 995] |
| Silver reward: item flag set exactly once, only after AddItem | PASS |  |
| Silver reward: BP flag set exactly once, BP granted at most once | PASS |  |
| Silver reward: full bag does not consume the item flag | PASS |  |
| Silver reward item constant ITEM_PP_MAX | PASS |  |
| Silver reward requires all five facilities | PASS |  |
| Gold all-print reward ordering (done-guard, BP flag, CanFitItem, AddItem, item flag) | PASS | [43, 689, 774, 958, 999] |
| Gold reward: item flag set exactly once, only after AddItem | PASS |  |
| Gold reward: BP flag set exactly once, BP granted at most once | PASS |  |
| Gold reward: full bag does not consume the item flag | PASS |  |
| Gold reward item constant ITEM_MASTER_BALL | PASS |  |
| Gold reward requires all five facilities | PASS |  |
| all-print BP amounts 50 / 100 | PASS |  |
| tower: first Silver +10 BP / first Gold +30 BP, one path each | PASS |  |
| tower: retry hook present | PASS |  |
| factory: first Silver +10 BP / first Gold +30 BP, one path each | PASS |  |
| factory: retry hook present | PASS |  |
| castle: first Silver +10 BP / first Gold +30 BP, one path each | PASS |  |
| castle: retry hook present | PASS |  |
| hall: first Silver +10 BP / first Gold +30 BP, one path each | PASS |  |
| hall: retry hook present | PASS |  |
| arcade: first Silver +10 BP / first Gold +30 BP, one path each | PASS |  |
| arcade: retry hook present | PASS |  |
| common script IDs 0x80A/0x80B match macros | PASS |  |
| print-bonus BP goes through the un-multiplied field credit (no 4x) | PASS |  |
| no Frontier/BP/Print requirement in availability or special-acquisition manifests (Pokedex completion) | PASS |  |
| diff contains no unrelated subsystem changes | PASS |  |
