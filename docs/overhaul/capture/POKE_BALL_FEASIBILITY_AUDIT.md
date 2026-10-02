# Poké Ball Feasibility Audit

Base: `fb9003d9d7894fc5b1c9c36ecaf9bdecb8176afd`. Authority: `pokeballs/POKE_BALL_REBALANCE_SPEC.md` (LOCKED) + `POKE_BALL_IMPLEMENTATION_PLAN.md`.

| Q | Finding |
|---|---|
| A | `BattleScript_CalcCatchShakes`, `src/battle/battle_script.c` (called from `BattleScript_CatchMonTask`, `SEQ_CATCH_MON_CALC_SHAKES`). |
| B | `switch (battleCtx->msgItemTemp)` inside the same function; Poké/Great/Ultra/Safari via `sBasicBallMod[]`; Master via post-roll override. Modifier units are 1/10. |
| C | Platinum has Quick, Timer, Repeat, Heal (no catch branch), plus Net, Nest, Dusk, Dive, Luxury, Premier. There are **no Level Ball or Lure Ball item slots**. |
| D | Vanilla: Quick 40 on turn 0; Timer `10+turns` cap 40; Repeat 30; Nest `40-targetLevel` (<40, min 10); Dive 35 water terrain; Dusk 35 night/cave; Net 30 Water/Bug; Heal 10. |
| E | Turns: `battleCtx->totalTurns` (yes). Caught-before: `BattleSystem_HasCaughtSpecies` (yes). Active level: `battleMons[attacker].level` (attacker = thrower's battler, set by the item command). Target level: `battleMons[defender].level`. Fishing origin: **not exposed** to battle code (only `TERRAIN_WATER`). |
| F | `Pokemon_SetCatchData` (`src/pokemon.c`) restores HP and clears status for `ITEM_HEAL_BALL`. Preserved unchanged. |
| G | Prices: `res/items/data/*_ball.json`. Shops: `include/data/mart_items.h` (`PokeMartCommonItems` badge-stage gates; per-city `*MartSpecialties[]`). Common gate value is a stage: 0 badges=1, 1–2=2, 3–4=3, 5–6=4. |
| H | Yes, entirely source-level. |
| I | `check_pr_scope` (economy validator, PR-local mode) flagged ball price edits and ball entries in shop arrays. Ownership moved: `CAPTURE_BALLS` items are excluded from D2 stock/price scope; locked D2 invariants and all other items are still enforced. |

## Design mapping (chat brief vs. locked repo spec)

The locked spec is the Platinum adaptation of the Emerald plan and is followed. Discrepancies with the chat brief, resolved by the spec (no new design chosen):

- **Level Ball → Nest Ball** (no new slot): ratio model 1.0 / 2.0 / 3.5 / 5.0 exactly as briefed.
- **Lure Ball → Dive Ball** (water terrain 4.0x). No reliable fishing flag exists; plan §5 forbids building one.
- **Quick Ball 5.0x** (spec) rather than the brief's 4.0x. One constant if the owner prefers 4.0.
- Timer: `1.0 + 0.3/turn`, cap 4.0 at turn 10 (brief: 10–12). Repeat 3.5, Heal 1.5 as briefed. Also per spec: Net 3.5, Dusk 3.0.

## Availability / prices

Prices already match the locked table; none changed. Shop changes: Great Ball gate 3→2 (after 1st badge), Ultra Ball gate 4→3 (3–4 badges), Dive Ball added to Pastoria and the League mart. All other specialist gates already match spec §11.
