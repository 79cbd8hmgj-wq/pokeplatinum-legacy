# Pokémon Platinum Overhaul — Implementation Plan

## Purpose

This document defines how locked overhaul design becomes repository changes.

Implementation agents must not redesign approved content while coding. If source reality conflicts with the design, record the conflict and stop that specific operation rather than silently substituting a different behavior.

## Primary tools/workflow

### ROM Mod Toolkit

Use first for ordinary source/data work:

- Pokémon types/stats/abilities
- level-up learnsets
- items
- trainers
- encounters
- source validation
- guarded change ledgers
- semantic diffs
- checkpoints/restores
- build verification

### NDS Disassembly Toolkit

Escalate only when source does not clearly expose the required mechanic:

- unknown engine behavior
- function discovery
- CFG/XRef/data-flow work
- runtime tracing/differentials
- ambiguous field/battle logic

Do not begin with disassembly when the decomp/source already exposes the behavior.

## Guarded-edit rules

1. Pin the source revision for every implementation batch.
2. Record expected original values.
3. Fail closed if guards do not match.
4. Apply related changes atomically where practical.
5. Run source validation before building.
6. Produce semantic diffs after application.
7. Build before combining with the next mechanical subsystem.
8. Keep unrelated changes in separate commits.
9. Never weaken a guard solely to force a patch through.
10. If source reality contradicts an old planning assumption, preserve the intended design and update the implementation spec explicitly.

## C2.5E — Created moves

### Dependency rule

Created moves are the current top implementation dependency. Species learnsets referencing new constants must wait until this layer builds.

### ID allocation

- IDs 468–489: created moves
- `MAX_MOVES = 490`

### Required audit surface

- generated move enum/source input
- move validity/range checks
- move-data serialization/NARC generation
- move names
- move descriptions
- battle scripts/effects
- battle animations
- contest metadata
- any move-ID indexed tables
- sound-move registry
- punching-move registry
- AI/effect metadata if indexed by move ID
- save/runtime assumptions involving `MAX_MOVES`

### Special cases

#### Resonant Slash

- register as a sound move
- preserve its approved contact/high-crit behavior

#### Star Jab

- register as a punching move
- preserve approved contact/flinch behavior

#### Magnet Volley

- Steel / Special / 25 BP per hit
- exactly three hits
- equal power each hit
- use normal multi-hit behavior capable of exactly 3 hits
- do not use Triple Kick's escalating-power logic
- target damage pattern: 25 + 25 + 25 before normal modifiers

### Created-move build gate

A created-move implementation batch is not `VERIFIED` until:

- all move resources generate successfully
- enum/constants compile
- no out-of-range/index failures appear
- both target Platinum builds complete where the repo supports them
- representative moves execute in battle
- Resonant Slash is recognized by Soundproof/sound logic
- Star Jab is recognized by Iron Fist/punch logic
- Magnet Volley performs exactly three equal-power hits

## C3H — Pokémon guarded ledger

### Supported operation model

Recovered ROM Toolkit support includes:

- `insert_level_move`
- `replace_level_move`
- `remove_level_move`
- `set_base_stat`
- `set_types`
- `set_abilities`

### Required guards

Each operation should include:

- species/form target
- source path
- expected original value
- intended new value
- file hash or equivalent pinned-source guard
- duplicate/conflict detection for learnset levels

### Application order

1. types/stats/abilities that do not reference created moves may be staged
2. created-move build gate must pass
3. apply level-up moves including created moves
4. validate all species data
5. check evolution-timing assertions
6. semantic diff against approved design
7. build

### Critical final-audit correction

Banette authority:

- Shadow Ball Lv31 remains
- Cursed Stitch inserted Lv38
- Shadow Claw Lv42 replaces Embargo

Any ledger encoding Cursed Stitch at Lv31 is invalid and must fail review.

## TM/HM compatibility patch

Compatibility must not inherit old TM21/TM78 masks.

### Required whole-set behavior

- clear TM21 legacy Frustration compatibility
- apply only the locked Air Slash recipient set
- clear TM78 legacy Captivate compatibility
- apply only the locked Power Gem recipient set

### Explicit compatibility additions

Preserve the locked retype-family additions and the Raichu TM91 source reconciliation.

### Validation

- no former TM21/TM78 flag survives accidentally
- Rotom appliance handling is not broken by TM21 Air Slash
- Mew's universal-machine identity is retained as designed
- Shaymin Sky handling remains form-appropriate
- no accidental blanket same-type compatibility expansion appears

## Reusable TM implementation

Design rule:

- TMs are reusable
- first acquisition remains the progression gate

Implementation should modify consumption behavior without bypassing acquisition or turning all TMs into automatically known/unlocked moves.

Vendor behavior should avoid meaningless repeat purchases where practical, but vendor UX changes should not block Core 1.0 if the reusable behavior itself is correct.

## HM implementation

Locked battle targets:

| HM | Target |
|---|---|
| Cut | 70 BP / 100 Acc / 30 PP / high crit |
| Fly | 100 BP / 100 Acc / 15 PP / retain two-turn behavior |
| Surf | 95 BP / 100 Acc / 15 PP / vanilla targeting/effect |
| Strength | 80 BP / 100 Acc / 15 PP |
| Defog | Evasion -1; clear hazards on both sides; clear target-side screens/safeguard/mist as designed |
| Rock Smash | 60 BP / 100 Acc / 15 PP / 50% Defense -1 |
| Waterfall | 80 BP / 100 Acc / 15 PP / 20% flinch |
| Rock Climb | 90 BP / 95 Acc / 20 PP / 20% confusion |

Defog is the main behavior-change case and should receive focused runtime tests.

Field-move decoupling is deferred for Core 1.0.

## Emerald-port implementation method

For each Emerald subsystem:

1. identify the final Emerald design authority
2. identify the actual Emerald source implementation
3. identify the Platinum equivalent subsystem
4. classify: DIRECT PORT / ADAPT / PLATINUM-SPECIFIC / DEFER
5. write a Platinum implementation spec
6. implement behind guards
7. build and runtime-test
8. update `STATUS.md`

Do not copy Emerald source files mechanically between engines unless the structures are demonstrably compatible.

## Commit strategy

Recommended granularity:

- documentation-only commits
- created-move plumbing
- created-move resources/text
- special registries/multi-hit behavior
- Pokémon ledger batches
- TM/HM compatibility
- reusable TMs
- HM behavior
- evolution changes
- EXP/economy
- capture balls
- breeding
- encounter zones
- trainers
- events
- Frontier/postgame

Each mechanical subsystem should be independently revertible.

## Verification levels

### L0 — syntax/data

- JSON/source parses
- generated resources compile

### L1 — structural

- expected counts/IDs
- compatibility masks
- no duplicate learnset slots unless intentional
- no invalid species/move/item references

### L2 — build

- supported Platinum builds complete

### L3 — semantic

- diff matches the design spec
- no unrelated source mutation

### L4 — runtime

- representative emulator tests
- edge cases for changed mechanics

### L5 — campaign/system QA

- progression, availability, economy, event state, and completion checks

A change is only `VERIFIED` at the level actually tested; do not label source-only work runtime-verified.

## Required handoff format from Claude Code / implementation agents

Every completed implementation task should report:

- branch
- commit SHA
- files changed
- design spec implemented
- guards used
- validation commands/results
- build results
- runtime tests performed
- unresolved discrepancies
- whether docs/status were updated

This prevents implementation state from becoming another chat-only artifact.
