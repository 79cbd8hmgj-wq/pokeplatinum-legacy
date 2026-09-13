# Pokémon Platinum Overhaul — Implementation Plan

## Purpose

This document defines how locked overhaul design becomes repository changes and how already-landed work is audited without being duplicated.

Implementation agents must not redesign approved content while coding. If source reality conflicts with the design, record the conflict and stop that specific operation rather than silently substituting a different behavior.

## Current implementation baseline

Before changing anything, inspect current `main`.

Two major implementation batches already landed:

### C2.5E created moves

Commit:

`071b8c7976801e64af5296f30b7437d7da2d8632`

- implements all 22 created moves and move-table plumbing;
- adds mod-aware CI builds for US revisions 0 and 1;
- GitHub Actions run `33981291318`: success.

### C3H species + TM compatibility

Commit:

`8a74452654e1552b78bfb329afcb351a2caec5cf`

- applies the TM21/TM78 compatibility rebuild;
- applies 225 guarded species operations;
- applies final Torkoal and Seviper learnset corrections;
- GitHub Actions run `33995072848`: success.

**Do not reapply the historical C3H ledgers over current main.** They are provenance/audit material.

## Primary tools/workflow

### ROM Mod Toolkit

Use first for ordinary source/data work:

- Pokémon types/stats/abilities;
- level-up learnsets;
- items;
- trainers;
- encounters;
- source validation;
- guarded change ledgers;
- semantic diffs;
- checkpoints/restores;
- build verification.

### NDS Disassembly Toolkit

Escalate only when source does not clearly expose the required mechanic:

- unknown engine behavior;
- function discovery;
- CFG/XRef/data-flow work;
- runtime tracing/differentials;
- ambiguous field/battle logic.

Do not begin with disassembly when the decomp/source already exposes the behavior.

## Guarded-edit rules

1. Inspect current source before generating a patch.
2. Pin the source revision for every implementation batch.
3. Record expected original/current values.
4. Fail closed if guards do not match.
5. Apply related changes atomically where practical.
6. Run source validation before building.
7. Produce semantic diffs after application.
8. Build before combining with the next mechanical subsystem.
9. Keep unrelated changes in separate commits.
10. Never weaken a guard solely to force a patch through.
11. Do not reapply a historical migration whose result is already present on main.
12. If source reality contradicts a planning assumption, preserve the intended design and update the implementation spec explicitly.

## C1 — next source implementation target

C1 design is complete and locked, but current main still contains vanilla values for C1 moves such as Fury Cutter.

### Recovery gate

Do not implement C1 until the repository contains a complete machine-readable **82-edit** manifest.

Current recovery state:

- 82/82 edit membership recovered;
- most final values recovered;
- final superseding values still unresolved for:
  - Bind
  - Wrap
  - Fire Spin
  - Whirlpool
  - Clamp
- Sand Tomb is confirmed at 50 BP / 95 Acc / 15 PP.

Authority/recovery files:

- `moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`
- `moves/C1_RECOVERED_BATCHES_SUPPLEMENT.md`
- `implementation/c1_move_edit_membership_recovery.json`

### C1 implementation gate

Once recovery is complete:

1. generate one canonical 82-edit manifest;
2. compare each intended edit with current `res/moves/*/data.json`;
3. fail closed if the current value is not the expected vanilla/current baseline;
4. apply only the fields defined by the locked C1 design;
5. validate exact edit count = 82;
6. semantic-diff the move table;
7. build Rev 0 and Rev 1;
8. perform focused runtime tests for effect-sensitive edits where appropriate.

## C2.5E — created moves: landed, now QA

The move layer is already implemented.

Design/runtime invariants that still require focused QA:

### Resonant Slash

- sound-move registration must interact correctly with sound logic/Soundproof;
- preserve contact/high-crit behavior.

### Star Jab

- punching registration must interact correctly with Iron Fist/punch logic;
- preserve contact/flinch behavior.

### Magnet Volley

- Steel / Special / 25 BP per hit;
- exactly three hits;
- equal power each hit;
- target pattern `25 + 25 + 25` before normal modifiers;
- no Triple Kick escalating-power logic.

### Verification status

- L0/L1: source exists and builds through generated resources;
- L2: passed Rev 0 / Rev 1 CI build;
- L4: focused runtime behavior still pending unless separate evidence is later checked in.

## C3H — species/compatibility: landed, now audit/QA

Historical implementation consisted of five guarded ledgers totaling 225 operations.

Historical provenance:

- `docs/overhaul/implementation/archive/c3h-apply-species-original.yml`
- `tools/overhaul/recover_c3h_ledgers.py`
- counts `67 / 27 / 40 / 53 / 38`.

Use those only to audit current source.

### Final corrections that must remain present

- Banette: Shadow Ball 31; Cursed Stitch 38; Shadow Claw 42.
- Torkoal: Yawn 52; Heat Wave 55.
- Seviper: Sludge Bomb 55.

### C3 audit procedure

1. compare current main against the canonical design/manifests;
2. verify created-move references resolve;
3. verify TM21/TM78 recipient masks;
4. verify explicit compatibility additions;
5. verify final follow-up corrections;
6. report semantic discrepancies rather than reapplying the old ledger wholesale;
7. perform runtime/campaign checks only after source audit is clean.

## TM/HM compatibility

The C3H compatibility portion is already applied.

Invariants:

- TM21 old Frustration compatibility is cleared;
- only locked Air Slash recipients receive TM21;
- TM78 old Captivate compatibility is cleared;
- only locked Power Gem recipients receive TM78;
- Raichu TM91 Flash Cannon reconciliation is present;
- no accidental broad same-type expansion.

Use `tm_hm/TM_HM_SPEC.md` and `implementation/tm_compat_manifest.json` for auditing.

## Remaining C2 mechanics

Do not confuse the landed compatibility work with the whole C2 system.

Still implement/audit separately:

### Reusable TMs

- TMs are reusable;
- first acquisition remains the progression gate;
- do not make all TMs globally unlocked;
- duplicate-purchase UX is secondary to correct reusable behavior.

### HM battle targets

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

Defog is the main behavior-change case and needs focused runtime testing.

### TM economy/source policy

Implement only from `tm_hm/TM_HM_SPEC.md`; preserve first-acquisition progression and locked Game Corner/Frontier pricing decisions.

## Emerald-port implementation method

For each Emerald subsystem:

1. identify final Emerald design authority;
2. identify actual Emerald source implementation;
3. identify Platinum equivalent subsystem;
4. classify `DIRECT PORT` / `ADAPT` / `PLATINUM-SPECIFIC` / `DEFER`;
5. write/update Platinum implementation spec;
6. implement behind guards;
7. build and runtime-test;
8. update `STATUS.md`.

Do not mechanically copy Emerald source files between engines unless structures are demonstrably compatible.

## Commit strategy

Recommended future granularity:

- documentation/recovery;
- C1 move rework;
- reusable TMs;
- HM behavior;
- evolution changes;
- EXP/economy;
- capture balls;
- breeding;
- encounter zones;
- trainers;
- events;
- Frontier/postgame;
- focused runtime QA fixes.

Each mechanical subsystem should be independently revertible.

## Verification levels

### L0 — syntax/data

- JSON/source parses;
- generated resources compile.

### L1 — structural

- expected counts/IDs;
- compatibility masks;
- no duplicate learnset slots unless intentional;
- no invalid species/move/item references.

### L2 — build

- supported Platinum builds complete.

### L3 — semantic

- diff/current source matches design spec;
- no unrelated source mutation.

### L4 — runtime

- representative emulator tests;
- edge cases for changed mechanics.

### L5 — campaign/system QA

- progression, availability, economy, event state, and completion checks.

Never label a change runtime-verified merely because CI builds it.

## Required handoff format from Claude Code / implementation agents

Every completed implementation task should report:

- starting branch/commit;
- resulting branch/commit;
- files changed;
- canonical design spec implemented/audited;
- guards used;
- validation commands/results;
- build results;
- runtime tests performed;
- unresolved discrepancies;
- whether `STATUS.md` was updated.

This prevents implementation state from becoming another chat-only artifact.
