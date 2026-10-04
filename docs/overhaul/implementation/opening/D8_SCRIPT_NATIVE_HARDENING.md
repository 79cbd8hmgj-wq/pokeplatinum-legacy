# D8 Mystery Starter — script-native hardened architecture

Status: production candidate for blocker C-1. Runtime verification still required once, after static/build validation.

## Reason for redesign

Diagnostic Build A restored the entire chooser to pre-D8 vanilla code while keeping the D8 randomized backend. It still reproduced the permanent black-screen failure after starter confirmation.

That result rules the Mystery Egg presentation out as the immediate cause and implicates the post-choice D8 backend boundary.

The production fix therefore keeps the intended Egg presentation but removes custom D8 logic from the critical application-to-field transition.

## Hardened flow

```
Mystery Egg chooser
    -> vanilla ChooseStarter_Exit contract
    -> vanilla ScrCmd_SaveChosenStarter
    -> vanilla ReturnToField
    -> vanilla FadeScreenIn / WaitFadeScreen
    -> native GetRandom VAR_0x8001, 100
    -> field-script weighted mapping
       -> VAR_MYSTERY_STARTER_SPECIES = actual species
       -> VAR_PLAYER_STARTER = canonical story branch
    -> native SetVar copy to VAR_0x8000
    -> vanilla GivePokemon Lv5
```

No D8-specific C function runs before the field has completely returned.

## What was retired from the active runtime path

- `MysteryStarter_Draw()` from `ScrCmd_SaveChosenStarter`
- C-side branch normalization in `ScrCmd_SaveChosenStarter`
- `SystemVars_SetMysteryStarterSpecies` / `SystemVars_GetMysteryStarterSpecies`
- custom `GetMysteryStarterSpecies` script command
- custom `GiveMysteryStarterEgg` script command
- custom `HatchMysteryStarterEgg` script command
- their assembly macros / script-command table entries

The deferred native hatch experiment may remain as source/reference material, but it is not reachable from the active opening flow.

## Weighted table

The resolver uses Platinum's existing `GetRandom dest, 100`, which is the native script wrapper around `LCRNG_Next() % upperBound`.

| Roll | Species | Story branch |
|---|---|---|
| 0–2 | Bulbasaur | Turtwig |
| 3–5 | Charmander | Chimchar |
| 6–8 | Squirtle | Piplup |
| 9 | Pikachu | Piplup |
| 10–19 | Chikorita | Turtwig |
| 20–29 | Cyndaquil | Chimchar |
| 30–39 | Totodile | Piplup |
| 40–49 | Treecko | Turtwig |
| 50–59 | Torchic | Chimchar |
| 60–69 | Mudkip | Piplup |
| 70–79 | Turtwig | Turtwig |
| 80–89 | Chimchar | Chimchar |
| 90–99 | Piplup | Piplup |

The chooser position is overwritten by the resolver before any story/rival consumer uses `VAR_PLAYER_STARTER`, so left/center/right cannot determine the actual starter or final story branch.

## Additional hardening

- Sandgem starter-gift exclusion reads `VAR_MYSTERY_STARTER_SPECIES` with native `SetVar` / `SetVarFromVar`; no custom getter.
- The Mystery species remains the renamed pre-existing `0x4031` variable slot; save layout is unchanged.
- Three Mystery Egg previews and species-neutral/no-cry presentation remain intact.
- A dedicated validator exhaustively simulates all rolls 0–99, verifies exact weights and story branches, checks the critical command ordering, checks the Egg chooser contract, and fails if retired custom commands reappear.
- The master validator now uses the script-native validator and regression test.

## Runtime policy

Do not request multiple intro playthroughs for diagnosis. Once Rev 0 / Rev 1 compile and static validation is green, one normal opening playthrough is sufficient to verify C-1 behavior. Further diagnosis should use static/build evidence or targeted instrumentation rather than repeated full intros.
