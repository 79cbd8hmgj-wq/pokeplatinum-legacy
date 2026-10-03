# Mystery Egg Starter — Implementation Report (D8)

**Starting SHA:** `6fc1eedfec637041733b5e5d9626a49c7524daa9` (`main` had not advanced). **Status: IMPLEMENTED — runtime QA PENDING (not VERIFIED).**

## Source audit findings
`MYSTERY_EGG_STARTER_SOURCE_AUDIT.md`. No blocker. Key facts: stock hatch is hard-coded Lv1 and logs a TV segment; `VAR_PLAYER_STARTER` is an existing u16 var; 19 script
call sites and two C helpers branched on the starter; the Sandgem lab gift logic is an actual-species consumer.

## Files changed
- **New:** `src/mystery_egg_starter.c`, `include/mystery_egg_starter.h`, `tools/overhaul/validate_mystery_starter.py`, `tools/overhaul/opening/{build_manifest,test_validate_mystery_starter}.py`, `docs/overhaul/implementation/opening/*`.
- **Source:** `src/choose_starter/choose_starter_app.c`, `include/struct_defs/choose_starter_data.h`, `src/scrcmd.c`, `include/data/scripts/scrcmd.h`, `asm/macros/scrcmd.inc`, `src/system_vars.c`, `include/system_vars.h`, `src/overlay005/daycare.c`, `include/overlay005/daycare.h`, `src/egg_hatch.c`, `include/egg_hatch.h`, `src/unk_0203D1B8.c`, `include/unk_0203D1B8.h`, `src/meson.build`.
- **Scripts/text:** `res/field/scripts/scripts_route_201.s` (egg flow) + 14 Rival/branch-consumer scripts (`GetPlayerStarterSpecies` → `GetPlayerStarterBranch`, 19 sites); `res/text/unk_0360.json`, `res/text/route_201.json`.
- **QA integration:** `tools/overhaul/validate_overhaul.py` (phase 14 + suite), `tools/overhaul/qa/runtime_cases.py` (+17 `OP-*` cases), `tools/overhaul/postgame/validate_postgame.py` (D8 scope allowlist; Fight Area script check now allows only the branch-query line swap), regenerated D7 docs.

## UI approach
The chooser keeps its camera, cursor, navigation, bag animation and confirmation menu. The three Poké Ball 3D models stay hidden; three **identical `SPECIES_EGG` sprites** are placed at the ball positions (scale 0.40, the zoom-from point of the existing preview animation) and the existing zoom-to-center confirm animation now shows the egg. Removed: per-slot species sprites, species cry on confirm, per-slot species text. Text bank 360 is neutral ("Mystery Egg", identical for all positions). No new art.

## Weighted RNG
`MysteryStarter_Draw()` = `LCRNG_Next() % 100` → `MysteryStarter_SpeciesFromRoll(roll)` over one static integer table (3/3/3/1/10×9; ranges 0–2, 3–5, 6–8, 9, 10–19 … 90–99). No position input exists in any signature. Called from exactly one place, `ScrCmd_SaveChosenStarter`, after the chooser app has exited with a confirmed egg. Note: `LCRNG_Next()` yields 16 bits, so `% 100` carries the engine's inherent ≤1/655 granularity (buckets of 655/656 of 65 536); the table itself is exact.

## Actual starter persistence
`VAR_PLAYER_STARTER` (existing var; **no save-format change**) is written immediately in `ScrCmd_SaveChosenStarter` with the real 13-way species. Nothing rerolls on hatch, field return or battle start. A save made before the choice can reroll (by design).

## Rival branch mechanism
`MysteryStarter_GetRivalBranch()` (pure function of the actual species; Grass→Turtwig, Fire→Chimchar, Water→Piplup, Pikachu→Piplup, unknown→Piplup as before) backs `SystemVars_GetPlayerStarterBranch`, new script command `GetPlayerStarterBranch`, `SystemVars_GetRivalStarter` and `SystemVars_GetPlayerCounterpartStarter` (so `BufferRivalStarterSpeciesName` and counterpart name/partner mon follow the branch). No trainer ID, team or label was added; no thirteen-way campaign. `GetPlayerStarterSpecies` is kept only in the Sandgem lab gift logic.

## Hatch / reveal mechanism
Route 201: `StartChooseStarterScene → SaveChosenStarter → ReturnToField → fade in → GiveMysteryStarterEgg → fade out → "Oh? The Egg is hatching!" → HatchMysteryStarterEgg → fade in → …Rowan/counterpart leave… → Barry battle`.
`GiveMysteryStarterEgg` builds a genuine party egg of the rolled species via a level-parameterised `Egg_CreateEggAtLevel` (Lv5 seed, `INIT_IVS_RANDOM`, random personality, no Day Care inheritance). `HatchMysteryStarterEgg` runs the native hatch scene with `EggHatchArgs.hatchLevel = 5`, which routes to `Egg_CreateHatchedMonAtLevel` (same body as ordinary hatch with the level parameterised); the existing hatch task already clears the egg flag, sets OT/met data and records the catch. Ordinary entry points pass level 1 / `hatchLevel = 0` and keep the TV segment; `include/constants/daycare.h`, `src/daycare_save.c` and the Breeding 2.0 manifests are untouched. Pikachu is stored as Pikachu in the egg and hatches as Pikachu. No guaranteed IV/nature/gender/shiny/item.

## Validator, mutation and exhaustive RNG results
See `MYSTERY_EGG_STARTER_VALIDATION_REPORT.md`: **99 pass / 0 fail**; **36/36 mutations detected, 0 baseline failures** (Pikachu weight, Gen I/II/III/IV weights, total weight, egg-position table input, second RNG call, Pikachu Rival mapping ×2, non-Sinnoh fall-through ×3, output level ×2, preview/cry/text/ball-model regressions, persistence, extra/missing species, hatch ordering, ordinary-breeding level/logic/constants, thirteen-way duplication, manifest drift). The real `mystery_egg_starter.c` is host-compiled with stub headers and run for all 100 rolls × left/center/right: histogram Bulbasaur 3, Charmander 3, Squirtle 3, Pikachu 1, every other starter 10; identical species for identical inputs at every position; independent Python model agrees; Rival mapping matches for every roll.

## Cross-system / D7 result
`python3 tools/overhaul/validate_overhaul.py`: **PASS (33/33)** — all established validators (docs, C3, evolution, C1, created moves, ID integrity, C2, availability/special acquisition, trainers, economy/progression, Poké Balls, breeding, events, Frontier/postgame, graphs, runtime matrix, smoke) plus all mutation suites and the new D8 validator/suite. `postgame` scope guard was extended to allow D8's files only. D7 artifacts regenerated: `qa/MASTER_VALIDATION_REPORT.md`, `master_validation_summary.json`, `RUNTIME_TEST_MATRIX.md` (+17 `OP-*` cases → 120 cases × 2 revisions = 240 NOT RUN), `QA_INDEX.md`, `RELEASE_ARTIFACTS.md`, `RELEASE_BLOCKERS.md`, `STATUS.md`, `DESIGN_PIPELINE.md`. The completion graphs do not model the starter path; `build_qa_graphs.py --check` passes unchanged.

## Build results
CI run [37089678263](https://github.com/79cbd8hmgj-wq/pokeplatinum-legacy/actions/runs/37089678263) on source commit `fae2b539`: **US Rev 0 success, US Rev 1 success, pr-lint success, format success** (also recorded in `qa/BUILD_MATRIX.md`).

## Runtime QA status
All 17 `OP-*` cases × 2 revisions: **NOT RUN** (no emulator/hardware in the session). D8 is **IMPLEMENTED, not VERIFIED**; the project is not a release candidate.

## Unresolved blockers
None. Visual caveats that only runtime can settle: egg-sprite placement/scale over the old ball positions and sprite layering against the briefcase BG (OP-01…OP-03, OP-09).
