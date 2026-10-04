# Chooser exit-boundary audit (post PR #29)

Source baseline: `880f5506` (main after PR #29). Pre-D8 reference: `6fc1eedfec637041733b5e5d9626a49c7524daa9`.
Runtime status: **BLOCKER C-1 / NOT VERIFIED.** This pass is a source-level restoration plus static audit; no ROM was run (no ARM toolchain in this session; Rev 0 / Rev 1 builds are CI-only).

## Change

Everything in the chooser except the egg visuals is now byte-identical to pre-D8 (`git diff 6fc1eedf -- src/choose_starter` shows only: `MakeMysteryEggSprite` + 3-iteration loop, no cry, fixed confirmation text index).

* `ChooseStarterData` restored to `{ int species; const Options *options; }` (same size/field order as vanilla; D8 had shrunk it by 4 bytes and moved `options` to offset 0).
* `ChooseStarter_Exit` again performs `data->species = GetSelectedSpecies(app->cursorPosition);` immediately after `SetVBlankCallback(NULL, NULL)`; `GetSelectedSpecies` and `STARTER_OPTION_0/1/2` restored. Teardown order unchanged from pre-D8.
* `ScrCmd_SaveChosenStarter`: still exactly one `MysteryStarter_Draw()`; the (now unused) local `chooseStarterData` was dropped. It never reads `data->species`. `Heap_Free(*fieldSysDataPtr)` is unchanged and still the single free.
* Kept: three `SPECIES_EGG` sprites, species-neutral text, no cry, `VAR_MYSTERY_STARTER_SPECIES` (actual) vs `VAR_PLAYER_STARTER` (canonical branch).

## Exit-boundary findings (static)

| Item | Finding |
| --- | --- |
| Script resume | `StartChooseStarterScene` → `FieldSystem_StartChildProcess` sets `processManager->child`; `ScriptContext_WaitForApplicationExit` returns `!FieldSystem_IsRunningApplication` (`child != NULL`). The field loop calls `ExecuteAndCleanupIfDone(&child)`, which clears `child` once `Exit` returns TRUE. `ChooseStarter_Exit` returns TRUE unconditionally. So the script resumes iff `Main` returns TRUE. |
| Main state machine | `IsSelectionMade` returns TRUE only at `CHOICE_STEP_FINISH`, reached from `MENU_YES` via `AdvanceChoiceStep(app, 1)`. `Main` then runs `StartFadeOut` → waits `IsFadeDone` → returns TRUE. A black screen during this fade is the intended fade-out; a hang there would mean the fade never completes, not an exit fault. Unchanged from vanilla. |
| `UpdateGraphics` at FINISH | only `G2_BlendNone()`. Unchanged. |
| SysTasks (camera) | task handle not stored; self-terminates after 6 frames, started at the intro (`SHOW_3D_GRAPHICS`), long before YES is possible. |
| SysTasks (preview window + preview graphics) | both started together with the same 6-frame length; the confirm step waits on the window task (`HasAppPreviewWindowMovementFinished`) before the YES/NO menu is created, so both are finished before YES can be chosen. CANCEL path: both restart with increment −2 and `DELETE_THESE_ARE_POKE_BALLS_TEXT` waits for completion before returning to choose. Both tasks null their handle when done. |
| SysTasks (cursor) | the only task live at exit; stopped by `StopCursorMovement` inside `Exit` (same call order as vanilla), before `ApplicationManager_FreeData` / `Heap_Destroy(HEAP_ID_CHOOSE_STARTER_APP)`. `Exit` runs atomically within one frame, so the task cannot execute between `DeleteCursorCellActor` and `StopCursorMovement`. |
| YES vs CANCEL vs vanilla | task lifetimes are identical on all three paths; none of this code was modified by D8 except the egg sprite content. |
| VBlank / VRAM transfer | `SetVBlankCallback(NULL, NULL)` first, `VramTransfer_Free()` before `FreeData` — unchanged. |
| Args lifetime | `ChooseStarterData` is allocated by `StartChooseStarterScene` on `HEAP_ID_FIELD2`, passed as app args, and freed only in `SaveChosenStarter` after the app is gone. `Exit` reads `data` (now writes `data->species`) before teardown. |

## SaveChosenStarter as first post-app command

* `fieldSysDataPtr` = `FieldSystem_GetScriptMemberPtr(..., SCRIPT_MANAGER_DATA_PTR)`; nothing between app exit and `SaveChosenStarter` touches it, so `*fieldSysDataPtr` is the allocation from `StartChooseStarterScene`.
* `MysteryStarter_Draw()`: `LCRNG_Next() % 100` → `SpeciesFromRoll`; table weights sum to 100 (validator + host test), so the trailing `GF_ASSERT` is unreachable.
* `MysteryStarter_GetRivalBranch` returns only Turtwig/Chimchar/Piplup, so `SystemVars_SetPlayerStarter` receives canonical species only.
* `Heap_Free(*fieldSysDataPtr)` once, after the last use; nothing reads `ChooseStarterData` afterwards.

## VAR_MYSTERY_STARTER_SPECIES address proof

`generated/vars_flags.txt` enum evaluation: `VARS_START = 16384 (0x4000)`, `VAR_PLAYER_STARTER = 0x4030`, `VAR_MYSTERY_STARTER_SPECIES = 0x4031`, `VARS_END = 0x4120`, `NUM_VARS = VARS_END − VARS_START = 288`.
`VarsFlags_GetVarAddress` asserts `varID − VARS_START < NUM_VARS` and returns `&varsFlags->vars[varID − VARS_START]`: index **49** of 288 (`u16 vars[NUM_VARS]` inside the existing `VarsFlags` struct). `TrySetVarToValue` additionally requires `VARS_START ≤ varID ≤ SCRIPT_LOCAL_VARS_START`; 0x4031 passes. The slot was an existing array element (renamed from `VAR_UNUSED_0x4031`, no enum insertion), so `NUM_VARS` and the save size are unchanged.

## Conclusion

No static defect was found in the exit boundary, task lifetimes, `SaveChosenStarter`, or the var write. Restoring the vanilla layout/output contract removes the one remaining structural difference (struct size/offset and the missing `data->species` write). Whether the black screen is resolved is **not known** until a ROM is run; if it persists, the next suspects are outside this audit (egg sprite resource loading at `Init`, which is the only remaining non-vanilla chooser behavior).
