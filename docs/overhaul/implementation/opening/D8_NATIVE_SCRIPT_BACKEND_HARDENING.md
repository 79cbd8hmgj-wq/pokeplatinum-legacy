# D8 Mystery Egg Starter — Native Script Backend Hardening

Status: production candidate architecture; runtime verification still pending.

## Why the architecture changed

Diagnostic Build A restored the chooser to the pre-D8 implementation byte-for-byte while retaining the Mystery Starter backend. It reproduced the permanent black-screen failure after confirmation. That rules out the Mystery Egg presentation as the sole cause and moves the production hardening target downstream.

Rather than continue asking for repeated intro playthroughs, the active D8 backend has been reduced to native Platinum field-script operations.

## Production boundary

The chooser remains the intended Mystery Egg presentation:

- three identical `SPECIES_EGG` previews;
- neutral confirmation text;
- no species cry before reveal;
- vanilla `ChooseStarterData` layout and exit contract.

The application boundary is now vanilla:

```
StartChooseStarterScene
SaveChosenStarter
ReturnToField
FadeScreenIn
WaitFadeScreen
```

`ScrCmd_SaveChosenStarter` is restored to the pre-D8 implementation. It reads the chooser's ordinary Turtwig/Chimchar/Piplup output, writes `VAR_PLAYER_STARTER`, frees the chooser data, and performs no Mystery Starter RNG, branch calculation, or custom variable write.

Only after `WaitFadeScreen` does D8 begin.

## Native 13-way draw

Route 201 uses Platinum's existing `GetRandom` script command:

```
GetRandom VAR_0x8000, 100
```

This command already implements `LCRNG_Next() % upperBound` in the vanilla script engine.

The script then maps the 0–99 result with fixed thresholds:

| Roll | Actual starter | Canonical story/Rival branch |
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

Each label writes only two ordinary script variables:

- `VAR_MYSTERY_STARTER_SPECIES` = actual 13-way species;
- `VAR_PLAYER_STARTER` = canonical Turtwig/Chimchar/Piplup branch.

The selected Egg position is not read by the RNG or mapping logic.

## Award and downstream reads

The starter is awarded directly through the vanilla command:

```
GivePokemon VAR_MYSTERY_STARTER_SPECIES, 5, ITEM_NONE, VAR_RESULT
```

No custom Mystery Starter getter command participates in the Route 201 award.

The Sandgem lab starter-gift skip also reads the actual species with native script plumbing:

```
SetVarFromVar VAR_0x8000, VAR_MYSTERY_STARTER_SPECIES
```

The player-starter name buffer remains defensive: it reads the actual Mystery species and falls back to vanilla `VAR_PLAYER_STARTER` if the Mystery variable is unset.

## Dormant custom helpers

The deferred hatch helpers and legacy C table may remain compiled for now, but they are not part of the active Route 201/Sandgem flow. The validator requires zero active C callers of `MysteryStarter_Draw` and `MysteryStarter_GetRivalBranch`, and zero active field-script users of `GetMysteryStarterSpecies`.

This deliberately minimizes the amount of custom code executed during the fragile chooser-to-field transition.

## Validation policy

The D8 validator now enforces:

- vanilla `SaveChosenStarter` boundary;
- exactly one native `GetRandom VAR_0x8000, 100`;
- RNG occurs only after `ReturnToField + FadeScreenIn + WaitFadeScreen`;
- exact locked thresholds;
- all 13 actual-species writes;
- exact 13→3 canonical Rival mappings;
- Pikachu → Piplup;
- direct Lv5 award from `VAR_MYSTERY_STARTER_SPECIES`;
- no active custom C RNG/branch caller;
- no active custom Mystery getter in Route 201 or Sandgem;
- unchanged save size and variable-table position;
- unchanged ordinary breeding behavior.

Runtime remains unverified until a production-candidate ROM is tested, but additional diagnostic intro playthroughs are no longer required before this hardened architecture is built.
