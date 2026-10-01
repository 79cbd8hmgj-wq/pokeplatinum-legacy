# Pokémon Platinum Overhaul — Final Integration & QA Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority:
- `docs/overhaul/qa/FINAL_INTEGRATION_QA_SPEC.md`
- all locked subsystem specs/manifests

Claude Code coordinates implementation validation; it must not redesign gameplay during QA.

## 1. QA index

Create:
`docs/overhaul/qa/QA_INDEX.md`

Track each subsystem:
- spec;
- manifest;
- validator;
- implementation commit;
- Rev 0 build;
- Rev 1 build;
- runtime evidence;
- open defects;
- verification state.

## 2. Master validator

Create:
`tools/overhaul/validate_overhaul.py`

It should orchestrate existing subsystem validators rather than duplicate their logic.

Output machine-readable summary plus:
`docs/overhaul/qa/MASTER_VALIDATION_REPORT.md`.

Fail the master run if any subsystem validator fails.

## 3. Canonical graph generation

Generate:
- `docs/overhaul/qa/pokedex_493_graph.json`;
- `docs/overhaul/qa/evolution_graph.json`;
- `docs/overhaul/qa/event_dependency_graph.json`;
- `docs/overhaul/qa/progression_gates.json`.

Use them to detect:
- unreachable species;
- circular event requirements;
- missing evolution items;
- unavailable move-known evolution;
- external dependency;
- postgame-only nonlegendary family error.

## 4. Build matrix

From clean checkout:
- build US Rev 0;
- build US Rev 1;
- record source commit;
- record toolchain version;
- record output checksum.

Automate in CI if not already covered.

No local-only binary patch may be required.

## 5. Static validation phase

Run in order:
1. canonical-doc consistency;
2. species/evolution;
3. moves;
4. TM/HM;
5. encounters;
6. trainers;
7. economy/EXP;
8. Poké Balls;
9. breeding;
10. events;
11. Frontier/postgame;
12. master graph.

Archive reports under `docs/overhaul/qa/reports/` or the established implementation report paths.

## 6. Progression simulation

Run the locked D2 profiles against final trainer/encounter source:
- direct;
- normal explorer;
- completionist.

If a milestone violates locked tolerance:
- diagnose source of EXP drift;
- make smallest owning-subsystem correction;
- update manifest and rerun.

Do not tune by blanket trainer-level changes.

## 7. Automated smoke harness

Where practical, create debug/test hooks for:
- starting representative battles;
- granting progression flags;
- spawning event encounters;
- querying party EXP/EV;
- reading shop inventory/prices;
- checking event flags.

Test-only/debug code must not alter release gameplay state unless explicitly compiled in a debug configuration.

## 8. Manual runtime checklist

Create:
`docs/overhaul/qa/RUNTIME_TEST_MATRIX.md`

Each case records:
- revision;
- save state/setup;
- steps;
- expected;
- actual;
- pass/fail;
- tester/date;
- screenshot/log reference where useful.

Cover every mandatory case in the D7 spec.

## 9. Full campaign run

Create:
`docs/overhaul/qa/FULL_CAMPAIGN_REPORT.md`.

Record at each major gate:
- party;
- levels;
- money;
- badges;
- key items;
- notable captures/evolutions;
- boss result;
- grinding performed;
- defects.

Do not use progression cheats in the canonical campaign run.

## 10. 493 completion verification

Create tooling that reads save/manifest state but does not directly mark Pokédex entries.

Use legitimate encounter/evolution/breeding/event paths.

Record evidence in:
`docs/overhaul/qa/POKEDEX_493_COMPLETION_REPORT.md`.

A species counts only if the acquisition path is implemented and reachable.

## 11. Save compatibility matrix

Test both revisions with:
- new save;
- matching vanilla save import;
- heavily progressed overhaul save;
- created-move Pokémon;
- custom event flags;
- breeding;
- Frontier records.

Create:
`docs/overhaul/qa/SAVE_COMPATIBILITY_REPORT.md`.

If save format remains structurally unchanged, state that explicitly.

## 12. Defect tracking

Create:
`docs/overhaul/qa/RELEASE_BLOCKERS.md`.

Severity:
- BLOCKER — release cannot proceed;
- MAJOR — gameplay/progression defect requiring fix;
- MINOR — nonblocking polish;
- COSMETIC — presentation only.

Every BLOCKER/MAJOR fix must cite:
- owning subsystem;
- fix commit;
- regression test;
- validators rerun.

## 13. Release consistency audit

Before release:
- search repo for `TODO`, `DRAFT PLAN`, `USER_DECISION_REQUIRED`, `UNRESOLVED`, and superseded implementation instructions;
- classify each hit;
- no unresolved gameplay authority may remain accidentally actionable.

Historical/provenance material may retain those labels when clearly archived.

## 14. Release artifacts

Use repository-supported tooling to generate legal patch artifacts for both supported revisions.

Include:
- patch filenames;
- source commit/tag;
- checksums;
- patch/input revision mapping;
- installation instructions;
- known limitations;
- save statement.

Never bundle the base ROM.

## 15. Status transition

Only after all required evidence:
- update every subsystem state;
- update `docs/overhaul/STATUS.md`;
- mark D7 `VERIFIED`;
- mark project `CORE 1.0 VERIFIED / RELEASE CANDIDATE`.

Do not use VERIFIED as shorthand for build-only success.

## 16. Recommended execution order

1. finish all subsystem implementations;
2. master static validation;
3. dual-revision clean build;
4. progression simulation;
5. targeted runtime matrix;
6. full fresh-save campaign;
7. exhaustive 493/postgame pass;
8. save compatibility;
9. blocker fixes/regressions;
10. final dual-revision build;
11. release artifacts/docs;
12. release-candidate sign-off.

## 17. Acceptance

D7 is complete only when every release criterion in the QA spec is evidenced in-repo and no release blocker remains.
