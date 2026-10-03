# Save Compatibility Report (D7 Phase 9)

Authority: `FINAL_INTEGRATION_QA_SPEC.md` s1 and s17. Fresh-save play is the canonical support target; loading an overhaul save back into unmodified vanilla is **not supported**
once custom moves, new flags or altered systems have been used.

**Status: SOURCE EVIDENCE ONLY — runtime import/reload NOT TESTED (all SV-* cases NOT RUN).** Source evidence below is a static diff review, not a compatibility proof.

## Source evidence (static)

Method: per-merge scan of the overhaul PRs #10–#21 (`git diff <merge>^1 <merge>`) for save-related paths (`include/struct_defs/**`, `*save*.{c,h}`, `generated/vars_flags.txt`,
`generated/vars.txt`), plus a vanilla (`1c1fb925`) → `main` comparison of the flag table.

| Area | Finding |
|---|---|
| Save structures | No overhaul PR (#10–#21) modifies `include/struct_defs/**` or any `*save*` file. The only vanilla→main save-struct difference is `battle_frontier.h` / `battle_frontier_save.c` (commit `5fd93829`, a repository sync commit bundled with the D5 design lock): `UnkStruct_*` types replaced by named `BattleFactorySave`/`BattleArcadeSave` members. The diff is type-name/header changes only, with no field added, but layout equality was **not** proven by a `sizeof`/offset comparison (no host build of the struct tree was run). |
| Flags | `generated/vars_flags.txt` has the **same line count (4420 lines) as vanilla**. 24 entries differ, all repurposing vanilla `FLAG_UNUSED_*` slots (special acquisitions PR #11, D5 events, D6 Frontier prints). No flag table growth; vars unchanged. Vanilla saves have those bits clear, so imported saves read them as "not received". |
| Created-move Pokémon | Move IDs are stored as `u16` (`include/struct_defs/pokemon.h`, `frontier_pokemon_base.h`, `hall_of_fame_entries.h`); IDs 468–489 (`MAX_MOVES = 490`) fit without a format change. |
| Evolution methods / species data | Live in ROM species data, not in the save; new evolution methods 27–32 (appended) do not change stored Pokémon data. |
| Breeding 2.0 | Rule changes only (inheritance, hatch cycles, egg-step checks); no new save fields. |
| Frontier records | No field additions visible in the `BattleFrontierSave` diff; D6 changes payout/BP logic and sets, and Print rewards reuse existing Print/BP state plus repurposed flags. |

## Matrix (both US revisions; all NOT RUN)

| Case | Rev 0 | Rev 1 | Notes |
|---|---|---|---|
| New overhaul save: create / save / reload (SV-01) | NOT RUN | NOT RUN | |
| Matching vanilla save imported (SV-02) | NOT RUN | NOT RUN | needs a vanilla US save of the matching revision (user-supplied; none in repo) |
| Progressed overhaul save reload (SV-04) | NOT RUN | NOT RUN | after D5 event flags |
| Created-move Pokémon save/reload (SV-03) | NOT RUN | NOT RUN | |
| Custom event flags (SV-04) | NOT RUN | NOT RUN | |
| Breeding state (SV-05) | NOT RUN | NOT RUN | eggs mid-hatch, Day Care |
| Frontier records (SV-05) | NOT RUN | NOT RUN | |

## Compatibility statement (current evidence)

* The save format is **structurally unchanged by the overhaul as far as static review can tell**; flags were allocated from unused slots.
* This is **not** a compatibility claim: runtime save import and reload have not been exercised on either revision.
* Not promised: overhaul save → vanilla ROM. Imported vanilla saves may contain Pokémon whose moves/abilities/types differ from the overhaul tables; the game does not rewrite them.
* A format change, if ever introduced, must be versioned and documented before release (spec s17).
