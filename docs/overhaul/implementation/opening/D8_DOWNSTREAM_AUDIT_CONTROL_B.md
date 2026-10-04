# D8 downstream isolation audit and Control Build B

Status: DIAGNOSTIC ONLY — DO NOT MERGE AS FINAL FEATURE.

## Why this exists

PR #31 isolates the chooser presentation by keeping the current Mystery Starter backend.

Control Build B removes the backend variable from the equation too. It answers a stricter question:

> Does the original Platinum starter flow still exit the chooser and return to Route 201 correctly on the current overhaul mainline?

## Static downstream audit

Compared current main `41e7524a` against pre-D8 `6fc1eedf`.

### Confirmed vanilla / unchanged

- `ScrCmd_ReturnToField` is byte-identical to pre-D8.
- Route 201 ordering remains vanilla:
  `StartChooseStarterScene -> SaveChosenStarter -> ReturnToField -> FadeScreenIn -> WaitFadeScreen -> getter -> GivePokemon`.
- `ScrCmd_GivePokemon` / `Pokemon_GiveMonFromScript` call site is byte-identical to pre-D8.
- The starter chooser-data allocation size/layout is vanilla after PR #30.
- The chooser data pointer being freed without immediately nulling `SCRIPT_MANAGER_DATA_PTR` is also vanilla behavior; it is not a D8 regression.

### D8-specific downstream pieces reviewed

- `ScrCmd_SaveChosenStarter` currently replaces the vanilla selected-species save with exactly one `MysteryStarter_Draw()`.
- The actual species is stored in `VAR_MYSTERY_STARTER_SPECIES`.
- The canonical story/rival branch is stored in `VAR_PLAYER_STARTER`.
- `GetMysteryStarterSpecies` is a direct getter from the new system variable.
- `VAR_MYSTERY_STARTER_SPECIES` is the renamed pre-existing `VAR_UNUSED_0x4031`; the variable array size and save structure are unchanged.
- The new script commands were appended to the end of the script-command table. Existing command order/opcodes were not shifted by D8.
- `GivePokemon` accepts the species variable through the same vanilla code path used by the original starter.

No static downstream defect was found in these pieces.

## Control Build B changes

Starting point: current main `41e7524a`.

Only the active starter path is restored to pre-D8 behavior:

1. `src/choose_starter/choose_starter_app.c` restored byte-for-byte from `6fc1eedf`.
2. `ScrCmd_SaveChosenStarter` restored to vanilla: reads `ChooseStarterData->species` and writes only `VAR_PLAYER_STARTER`.
3. Route 201 restored to `GetPlayerStarterSpecies VAR_0x8000` before `GivePokemon`.

The unused D8 helper code and commands remain compiled but are not called by this control path.

## Runtime interpretation

- **PASS-B:** original Platinum starter flow works on current mainline. If Build A fails while B passes, the defect is definitely inside the D8 post-choice backend (`MysteryStarter_Draw`, variable writes/reads, or their immediate integration).
- **FAIL-B:** even the vanilla starter control hangs. The blocker is outside the D8 chooser/backend logic and must be investigated at the wider field/application transition level or build/runtime identity level.

## Test discipline

Use the exact CI artifact for this PR and record revision, PR head SHA, run ID, artifact name and SHA-256 when available. Do not identify the build only by a local filename.
