# Release Blockers (D7 Phase 10)

Severity: **BLOCKER** (release cannot proceed) · **MAJOR** (gameplay/progression defect requiring fix) · **MINOR** (non-blocking polish/process) · **COSMETIC**.

**Release state: CORE 1.0 SOURCE-COMPLETE — RUNTIME QA PENDING; D8 runtime BLOCKER C-1 OPEN (Section C).** No source/static BLOCKER or MAJOR remains open. Section B lists runtime-unverified items:
they are not defects, but they prevent `CORE 1.0 VERIFIED / RELEASE CANDIDATE` under spec s21.

## A. Source / static items

| ID | Severity | Status | Item |
|---|---|---|---|
| A-1 | MAJOR | **FIXED in D7** | Solar Petal (ID 478) was missing `MOVE_FLAG_MAKES_CONTACT`; the created-move manifest and `CREATED_MOVES.md` both specify contact = Yes. |
| A-2 | MINOR | **FIXED in D7** | Three subsystem test/validator harnesses had stale post-merge baselines (no gameplay effect). |
| A-3 | MINOR | **FIXED in D7** | Stale status/authority text (QA "not started", D2/D6/D7 states, draft headers, wrong spec pointer). |
| A-4 | MINOR | OPEN — owner confirmation | `events/LEGENDARY_MYTHICAL_EVENT_SPEC.md` is a near-duplicate of `LEGENDARY_MYTHICAL_SPEC.md`; both said `LOCKED SPEC`. Now bannered non-authoritative; deletion needs owner OK. |
| A-5 | MINOR | OPEN — design (pre-existing) | Dragon Swipe (ID 471) is a finalized move with no historically proven final recipient. **Not invented**; asserted unreferenced by `validate_created_moves.py`. |
| A-6 | BLOCKER for release *packaging* only | OPEN — process | The repository has no supported patch-generation path (no xdelta/IPS/BPS tooling), so spec s20 patch artifacts cannot be produced. See `RELEASE_ARTIFACTS.md`. Does not block source integration. |

### Fix records (BLOCKER/MAJOR/validator fixes)

| ID | Owning subsystem | Fix | Regression test | Validators rerun |
|---|---|---|---|---|
| A-1 | Created moves (C2.5E) | `res/moves/solar_petal/data.json`: add `MOVE_FLAG_MAKES_CONTACT` (data-only; no engine change) | `tools/overhaul/qa/validate_created_moves.py` (checks every created move's contact flag against the manifest) + `test_qa_validators.py::test_solar_petal_contact_regression` | created-move, C1, C2, ID integrity, postgame (scope allow-list), master validator |
| A-2 | Economy | `economy/test_validate_economy.py`: clean-tree check now uses the post-merge baseline (`enforce_pr_scope=False`, as the CLI does); PR-scope mutations must add a failure beyond the documented later-subsystem baseline (D3 specialist-ball stock, D5/D6 `src/scrcmd.c`); one mutation (`frontier_exchange_modified`) is documented as indistinguishable post-merge. Previously the suite exited 1 and its mutations were vacuously "caught". | the suite itself: 56/56 + 1 documented skip, rc 0 | economy validator + suite |
| A-2 | Trainers | `trainers/test_validate_trainers.py`: `check_manifest(..., use_git=True)` (D6 re-derives Frontier base bytes via git; `False` always tripped the fingerprint check). Suite previously exited 1 on the unmutated tree. | the suite itself (all mutations + `unmutated tree has 0 errors`) | trainer validator + suite |
| A-2 | Postgame | `postgame/validate_postgame.py`: D7 paths added to the explicit scope allow-list so the D6 check keeps rejecting any *other* later change | `postgame/test_validate_postgame.py` | postgame validator + suite |
| A-3 | Docs | `STATUS.md`, `DESIGN_PIPELINE.md`, `AVAILABILITY_ARCHITECTURE.md`, `implementation/AVAILABILITY_IMPLEMENTATION_REPORT.md`, spec banner | `tools/overhaul/qa/audit_release_consistency.py` (45 hits all classified; stale-state regexes) | audit, master |

### Reviewed warnings (accepted, no change)

* Trainer validator: 16 warnings — locked-spec boss/Rival/commander evolution stages, vanilla repeated-species ordinary trainers, Volkner `iv_scale 2500` preserved.
* Recorded wild-band drift for aron, dratini, finneon, igglybuff, magikarp, tentacool, togepi (live band later than the planning matrix; still pre-E4): `progression_gates.json`.
* Availability: 0 warnings. Evolution/C1/C2/economy/balls/breeding/events/postgame: 0 failures.

## B. Runtime-unverified items (not defects; gate VERIFIED / release candidate)

| ID | Severity if confirmed | Item | Evidence state |
|---|---|---|---|
| B-1 | MAJOR candidate (release blocker per spec s19 "major progression over/under-leveling") | **Progression calibration is model-flagged, unproven.** The D2 calibration model (final source) reports normal-explorer party average 3.5–12.8 below the boss ace from Byron on, completionist +2.3…+7.0 above ace at Roark–Candice (+4.3…+8.6 with story trainers) and direct 3–26 below. Diagnosis: the model omitted 92 mandatory story trainers; with them the normal deficit shrinks to −3.5…−7.2 but 26/39 profile×boss cells remain out of tolerance. The same gap exists under vanilla EXP in the model. No source defect was proven, so **no trainer level or EXP value was changed** (no blanket rescaling). | `PROGRESSION_SIMULATION_REPORT.md`; needs the human campaign (CG-01) |
| B-2 | — | All 120 mandatory runtime cases (103 D7 + 17 D8 `OP-*`) × 2 revisions are **NOT RUN** (240 runs). | `RUNTIME_TEST_MATRIX.md` |
| B-3 | — | Full fresh-save campaign not performed. | `FULL_CAMPAIGN_REPORT.md` (template) |
| B-4 | — | In-game 493 completion run not performed (static graph proof only). | `POKEDEX_493_COMPLETION_REPORT.md` |
| B-5 | — | No vanilla-save import / overhaul save reload test was run. | `SAVE_COMPATIBILITY_REPORT.md` |
| B-6 | — | Clean-build output checksums are only recorded by the new CI provenance step on the D7 PR run; no local toolchain/base ROM was available. | `BUILD_MATRIX.md` |

## C. D8 runtime-QA defects (user-reported)

| ID | Severity | Status | Item |
|---|---|---|---|
| C-1 | **BLOCKER** | **OPEN — starter-state refactor applied, NOT runtime-verified** | After confirming a Mystery Egg, both screens stay black indefinitely (music continues; progression never resumes). PR #26's hatch-script reorder did not fix it. Source change (D8 simplification): `Route201_Briefcase` is back to the vanilla award flow — `StartChooseStarterScene`, `SaveChosenStarter`, `ReturnToField`, `FadeScreenIn`, `WaitFadeScreen`, `GetPlayerStarterSpecies`, `GivePokemon` Lv5 — and no longer calls `GiveMysteryStarterEgg` / `HatchMysteryStarterEgg` (native hatch presentation DEFERRED / DISABLED). The chooser lifecycle (Poké Ball model visibility, preview movement, sprite hide/show, teardown) is restored to vanilla; only the preview sprite content (SPECIES_EGG) and the species-neutral text/cry removal differ. PR #28 still black-screened at the same point, so the hatch path is ruled out. Follow-up: `VAR_PLAYER_STARTER` is restored to its vanilla 3-species invariant (Turtwig/Chimchar/Piplup) and the actual 13-way species is stored in `VAR_MYSTERY_STARTER_SPECIES` (the former unused `VAR_UNUSED_0x4031`); the Route 201 award reads the new variable, every Rival/branch consumer is vanilla again. PR #29 still black-screened at the same point; the follow-up restores the vanilla `ChooseStarterData` layout and the `ChooseStarter_Exit` `data->species` output contract (egg sprites kept) and records a static exit-boundary/SysTask/`SaveChosenStarter`/var-index audit in `implementation/opening/CHOOSER_EXIT_BOUNDARY_AUDIT.md` (no defect found statically). Root cause is not proven; the fix is hypothesized, not verified. Closes only when OP-01…OP-03 and OP-10/OP-11 pass on Rev 0 and Rev 1.
| C-2 | MAJOR | **OPEN — superseded, NOT runtime-verified** | Mystery Egg sprites rendered tiny / pasted over the briefcase. The resting-state sprites (`MYSTERY_EGG_REST_*`) were removed in the D8 simplification: the vanilla Poké Ball models are shown again and the egg appears only in the confirm preview at the vanilla scale/offset. Visual quality of the egg preview still needs runtime review. |

Regression coverage: `tools/overhaul/validate_mystery_starter.py` (vanilla chooser lifecycle, vanilla Route 201 award flow, no hatch calls) plus the mutation suite in `opening/test_validate_mystery_starter.py`. These are source-level guards, not runtime evidence.

## Release-readiness summary

* Runtime BLOCKER open: **C-1** (Mystery Egg black screen; simplified vanilla award flow unverified). Source/static BLOCKER open: **0**. Source/static MAJOR open: **0** (A-1 fixed).
* Open for release candidate: B-1…B-6 plus A-6 (patch tooling), and owner confirmation items A-4/A-5.
* Therefore: **CORE 1.0 SOURCE-COMPLETE — RUNTIME QA PENDING**; artifacts, if any, are TEST/QA builds only.
