# EXP / Economy Validation Report

Base: `447833b79fa5c0456d60bcbd8ec03ec109d92c23`. Commands run from `tools/overhaul/economy/`.

| Command | Result |
|---|---|
| `python3 test_exp_model.py` | 24 tests OK (party sizes 1/3/6; 1/multiple participants; 1/multiple Exp. Shares; participant+Exp. Share; fainted/Lv100/Egg exclusions; odd pools; trainer, Lucky Egg, traded 1.5x, foreign 1.7x; EV recipients; `sum(pre-modifier allocations) == raw_pool` whenever no legacy min-1 floor applies; simulation determinism) |
| `python3 build_manifest.py` | 23 edits, 38 tutor entries; before-values read from the base commit |
| `python3 validate_economy.py` | 0 failures |
| `python3 test_validate_economy.py` | clean tree PASS; 59/59 mutations rejected |
| `python3 scope_audit_economy.py` | 0 files outside economy scope |
| `python3 simulate_progression.py --json ../../../docs/overhaul/implementation/economy/progression_simulation.json` | deterministic; flags reported in the audit, no trainer edits |

Existing validators re-run on this branch (all unchanged and passing): C1 (`validate_c1.py` 0 problems / 82 edits; mutation 24/24),
C2 (`validate_c2.py` OK; mutation 76/76, also guards TM21/TM78 recipient masks and Game Corner/Frontier TM economy),
evolution (`validate_evolutions.py` PASS; 22 tests), ordinary availability + special acquisition
(`validate_availability.py` 0 failures/0 warnings; mutation 12/12 and 25/25).

Mutation classes covered: 50/50 split, full-EXP-for-everyone, party-size pool inflation, Exp. Share extra EXP,
participant+Exp. Share double count, fainted/Lv100/Egg denominator bugs, empty-battle-group pool loss, include-guard regression, participant-state cleanup, omitted team recipients, EVs to bench/Exp. Share
holders, trainer/Lucky Egg/traded/foreign modifier edits, extra (Emerald-style) multiplier, wrong locked/status prices,
any Poké Ball price, unrelated item/TM price, unrelated trainer-class multiplier, Heart Scale still checked/consumed/
mentioned, lost Move Reminder branches, tutor cost not ceil(old/2) / free / zero→nonzero / move or location changed /
entry dropped, missing stones, postgame-gated stone vendor, Oval Stone, changed vitamin stock, Rare Candy in a common or
Veilstone mart, missing postgame gate, and modified Game Corner / Frontier TM economy sources.

## Builds

Rev 0 / Rev 1 (GitHub Actions `build`) on the final head: see PR checks (recorded below once green).
Runtime/emulator QA: DEFERRED TO FINAL OVERHAUL PLAYTEST.
