# QA Index (D7 Phase 1)

Authority: `FINAL_INTEGRATION_QA_SPEC.md`, `FINAL_INTEGRATION_QA_IMPLEMENTATION_PLAN.md`. Starting point: `main` @ `19cbadaa` (PR #21 merged).

> **IMPLEMENTED ≠ VERIFIED.** "Verified" in this index means *runtime-verified in-game* (spec s21). Nothing below is `VERIFIED`: every row has
> runtime evidence **NONE** (`RUNTIME_TEST_MATRIX.md`: 0 PASS / 0 FAIL / 206 NOT RUN). Static validation and CI builds are recorded separately and are
> not runtime evidence.

**Project state: CORE 1.0 SOURCE-COMPLETE — RUNTIME QA PENDING.** Not `CORE 1.0 VERIFIED`, not a release candidate.

## Build state (applies to every row)

`main` @ `19cbadaaa296b7ae1c51e2be2e99226fe3d42813` (all subsystems below merged): GitHub Actions run
[`37081807517`](https://github.com/79cbd8hmgj-wq/pokeplatinum-legacy/actions/runs/37081807517) — job `build (US rev 0)` **success**, job `build (US rev 1)` **success**.
Per-subsystem merge runs are listed in the *Merge commit / CI run* column; earlier merges (#10–#14) are covered by the cumulative run above. The D7 PR's own
dual-revision run is recorded in `BUILD_MATRIX.md`.

## Subsystem table

Common columns: **Rev 0 / Rev 1** = CI build state at the merge commit and at current `main` (both `build OK`); **Runtime** = none performed; **Verification** =
`IMPLEMENTED — static + build verified; runtime QA pending` unless stated.

| Subsystem | Canonical spec | Manifest(s) | Validator | Merge / implementation commit · CI run | Open defects | Verification |
|---|---|---|---|---|---|---|
| C3 species / types / stats / abilities / learnsets | `species/C3_IMPLEMENTATION_AUTHORITY.md` | `implementation/c3_species_provenance.json`, `ledgers/`, `archive/c3h-apply-species-original.yml` | `tools/overhaul/qa/validate_species_c3.py` (D7; 225 ledger postconditions + final corrections) | `8a744526` · run `33995072848` | none (Dragon Swipe final recipient historically unresolved — not invented; see RELEASE_BLOCKERS A-5) | IMPLEMENTED — static + build verified; runtime pending |
| Created moves 468–489 | `moves/CREATED_MOVES.md` | `implementation/created_moves_manifest.json` | `tools/overhaul/qa/validate_created_moves.py` (D7) | `071b8c79` · run `33981291318` | **D7 fix:** Solar Petal lacked the contact flag the manifest requires (fixed, regression-tested; runtime recheck MV-06) | IMPLEMENTED — static + build verified; runtime pending |
| C1 existing-move rebalance (82 edits) | `moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md` | `implementation/c1_move_changes_manifest.json`, `c1_move_guards.json` | `tools/overhaul/moves/validate_c1.py` (+24 mutation cases) | PR #13 `e13b728f` | none | IMPLEMENTED — static + build verified; runtime pending |
| C2 TM/HM, reusable TMs, TM economy | `tm_hm/TM_HM_SPEC.md` | `implementation/tm_compat_manifest.json`, `c2_mechanics_manifest.json` | `tools/overhaul/c2/validate_c2.py` (+76 mutation cases) | PR #14 `3b7b843e` | none | IMPLEMENTED — static + build verified; runtime pending |
| Evolution (Pass A) | `evolution/EVOLUTION_SPEC.md` | `implementation/evolution_manifest.json` | `tools/overhaul/evolution/validate_evolutions.py`; D7 graph `qa/evolution_graph.json` | PR #15 `447833b7` · run `37049315078` | none | IMPLEMENTED — static + build verified; runtime pending |
| Ordinary wild availability (#001–#493) | `AVAILABILITY_ARCHITECTURE.md` | `implementation/wild_encounters.json`, `encounter_zones.json`, `availability_families.json` | `tools/overhaul/availability/validate_availability.py` | PR #10 `f89dfc79` | none (7 families' recorded band later than planning matrix; all pre-E4) | IMPLEMENTED — static + build verified; runtime pending |
| Special acquisitions (28 families) | `implementation/SPECIAL_ACQUISITION.md` | `implementation/special_acquisitions.json`, `special_systems.json` | `validate_availability.py` + `availability/test_validators.py` (26 mutation cases) | PR #11 `67af26fb` | none | IMPLEMENTED — static + build verified; runtime pending |
| EXP / economy (D2) | `economy/EXP_ECONOMY_SPEC.md` | `implementation/economy/economy_manifest.json` | `tools/overhaul/economy/validate_economy.py`; D7 `qa/progression_report.py` | PR #16 `fb9003d9` · run `37057147545` | model-flagged calibration items (RELEASE_BLOCKERS B-1) | IMPLEMENTED — static + build verified; runtime pending |
| Poké Balls (D3) | `pokeballs/POKE_BALL_REBALANCE_SPEC.md` | `implementation/pokeballs/pokeball_manifest.json`, `pokeball_shop_manifest.json` | `tools/overhaul/pokeballs/validate_pokeballs.py` | PR #17 `e2d73d33` · run `37061225786` | none | IMPLEMENTED — static + build verified; runtime pending |
| Breeding 2.0 (D4) | `breeding/BREEDING_SPEC.md` | `implementation/breeding/*.json` | `tools/overhaul/validate_breeding.py` (+ host harness) | PR #18 `77ff7a74` · run `37065524379` | none | IMPLEMENTED — static + build verified; runtime pending |
| Trainer overhaul (D1) | `trainers/TRAINER_OVERHAUL_SPEC.md` | `implementation/trainers/*.json` | `tools/overhaul/trainers/validate_trainers.py` | PR #19 `08092189` · run `37068740706` | none (16 documented warnings accepted) | IMPLEMENTED — static + build verified; runtime pending |
| Legendary / Mythical events (D5) | `events/LEGENDARY_MYTHICAL_SPEC.md` | `implementation/events/*.json` | `tools/overhaul/validate_legendary_availability.py` | PR #20 `98f9cbdf` · run `37077868600` | duplicate spec file bannered non-authoritative (RELEASE_BLOCKERS A-4) | IMPLEMENTED — static + build verified; runtime pending |
| Battle Frontier / postgame (D6) | `postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md` | `implementation/postgame/*.json` | `tools/overhaul/postgame/validate_postgame.py` | PR #21 `19cbadaa` · run `37081807517` | none | IMPLEMENTED — static + build verified; runtime pending |
| D7 completion graphs | `FINAL_INTEGRATION_QA_SPEC.md` s4 | `qa/pokedex_493_graph.json`, `evolution_graph.json`, `event_dependency_graph.json`, `progression_gates.json` | `tools/overhaul/qa/build_qa_graphs.py --check` (+9 mutation tests) | D7 PR | none | STATIC PROOF ONLY (493/493 reachable in the model; no in-game 493 run) |
| Save compatibility | spec s17 | — | — | — | runtime import untested (`SAVE_COMPATIBILITY_REPORT.md`) | NOT VERIFIED |
| Visual overhaul (G-series) | out of D7 gameplay scope | — | — | PR #12 and CI audit workflows | not assessed by D7 | out of scope |

## Evidence index

| Evidence | Path |
|---|---|
| Master validation | `MASTER_VALIDATION_REPORT.md`, `master_validation_summary.json`, `python3 tools/overhaul/validate_overhaul.py` |
| Completion graphs / 493 | `pokedex_493_graph.json`, `evolution_graph.json`, `event_dependency_graph.json`, `progression_gates.json`, `POKEDEX_493_COMPLETION_REPORT.md` |
| Release consistency audit | `RELEASE_CONSISTENCY_AUDIT.md`, `release_consistency_audit.json` |
| Progression simulation | `PROGRESSION_SIMULATION_REPORT.md`, `progression_simulation_qa.json` |
| Runtime matrix (NOT RUN) | `RUNTIME_TEST_MATRIX.md`, `runtime_test_matrix.json` |
| Full campaign (pending) | `FULL_CAMPAIGN_REPORT.md` |
| Save compatibility | `SAVE_COMPATIBILITY_REPORT.md` |
| Blockers | `RELEASE_BLOCKERS.md` |
| Builds / artifacts | `BUILD_MATRIX.md`, `RELEASE_ARTIFACTS.md` |
