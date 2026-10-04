# D8 Mystery Egg Starter — Hardened Backend

Status: **production candidate; runtime verification pending**

This document supersedes the earlier active-backend assumptions in the D8 implementation notes.

## Runtime result that forced the redesign

Diagnostic Build A / PR #31 used the pre-D8 vanilla chooser byte-for-byte while retaining the custom Mystery Starter backend. It still reproduced the permanent black-screen failure after starter confirmation.

Therefore the Egg preview presentation is not the active blocker. The failure boundary moved downstream of the chooser.

## Hardened architecture

The production candidate keeps the intended Mystery Egg presentation but removes D8 custom work from the application-exit boundary.

```
Mystery Egg chooser
  -> vanilla SaveChosenStarter
  -> ReturnToField
  -> FadeScreenIn
  -> WaitFadeScreen
  -> native GetRandom VAR_0x8000, 100
  -> native GoToIfLt weighted routing
  -> native SetVar:
       VAR_MYSTERY_STARTER_SPECIES = actual species
       VAR_PLAYER_STARTER = canonical Sinnoh branch
  -> native SetVarFromVar
  -> vanilla GivePokemon Lv5
```

The chooser position is never an RNG input.

## Locked distribution

- 0–2: Bulbasaur (3%)
- 3–5: Charmander (3%)
- 6–8: Squirtle (3%)
- 9: Pikachu (1%)
- 10–19: Chikorita (10%)
- 20–29: Cyndaquil (10%)
- 30–39: Totodile (10%)
- 40–49: Treecko (10%)
- 50–59: Torchic (10%)
- 60–69: Mudkip (10%)
- 70–79: Turtwig (10%)
- 80–89: Chimchar (10%)
- 90–99: Piplup (10%)

Exactly one native script RNG draw is performed, only after the field is fully restored.

## Canonical Rival/story mapping

`VAR_PLAYER_STARTER` remains limited to the original three Sinnoh starter values.

- Grass family: Turtwig branch
- Fire family: Chimchar branch
- Water family: Piplup branch
- Pikachu: Piplup branch

`VAR_MYSTERY_STARTER_SPECIES` stores the actual awarded species in the existing former `VAR_UNUSED_0x4031` slot.

## Removed runtime surface

The hardened candidate deliberately removes the following from the active ROM design:

- D8 RNG from `ScrCmd_SaveChosenStarter`
- `GetMysteryStarterSpecies` custom field-script command
- `GiveMysteryStarterEgg` custom field-script command
- `HatchMysteryStarterEgg` custom field-script command
- D8 custom script-command macros/opcodes
- Mystery starter C setter
- Mystery starter C module from `src/meson.build`
- custom Day Care egg-level plumbing
- custom egg-hatch level override
- custom field-system Mystery hatch path

The ordinary Day Care and hatch engine files are restored byte-for-byte to pre-D8 `6fc1eedf`.

`src/mystery_egg_starter.c` and `include/mystery_egg_starter.h` remain only as offline validation/reference material and are not linked into the ROM.

## Remaining D8 runtime changes

The runtime feature is now limited to:

1. Three identical `SPECIES_EGG` chooser previews and neutral Egg wording.
2. `VAR_UNUSED_0x4031` renamed to `VAR_MYSTERY_STARTER_SPECIES`.
3. One small getter used by player-starter name buffering.
4. Route 201 native-script weighted selection and direct Lv5 award.
5. Sandgem lab gift filtering reading the actual species with `SetVarFromVar`.
6. Player starter name buffering using the actual Mystery species, while Rival/counterpart logic remains keyed to canonical `VAR_PLAYER_STARTER`.

## Validation gates

Static validation must enforce:

- vanilla chooser exit contract;
- exactly one `GetRandom ..., 100` after `WaitFadeScreen`;
- exact locked thresholds;
- all 13 actual/canonical assignments;
- one Lv5 `GivePokemon`;
- no custom Mystery starter field-script commands;
- no linked Mystery starter C module;
- breeding/hatch engine byte identity to pre-D8;
- no Rival consumers using the actual Mystery species.

Runtime verification is intentionally reduced to **one final intro playthrough** after both Rev0 and Rev1 build successfully.

### Required runtime result

1. Three Mystery Eggs render.
2. Confirm any Egg.
3. Game returns from the chooser instead of remaining black.
4. Player receives exactly one Lv5 starter from the locked pool.
5. Rowan/Rival scene continues.
6. First Rival battle starts normally.

Do not resume multi-build intro bisection unless this hardened candidate fails.
