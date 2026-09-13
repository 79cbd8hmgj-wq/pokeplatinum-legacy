# Pokémon Platinum Overhaul — Current Status

Last reconstructed checkpoint: 2026-09-13.

## Executive status

**Design:** Phase 1 Pokémon/move design through C3 is closed.

**Implementation:** C2.5E/C3H is active.

**Known design blockers:** 0.

**Current implementation dependency:** the 22 created moves must be fully plumbed and build-validated before species ledgers that reference their `MOVE_*` constants are applied.

## Canonical branch/workflow

This documentation is being reconstructed on:

`overhaul/canonical-docs`

Existing implementation/history branches discovered in the repository include:

- `overhaul/c3h-species-compat`
- `overhaul/c3h-ledger-archive`

Those branches are implementation/history sources, but this documentation package is intended to become the long-term design/status authority after review and merge.

## Design completion matrix

| Area | Status | Notes |
|---|---|---|
| Core project identity | LOCKED | Single-save #001–#493 target; Emerald-successor philosophy |
| Types/stats/abilities/roles | LOCKED | Targeted enrichment; no blanket BST inflation |
| Existing move rework (C1) | LOCKED | Weak-move revival and Gen IV role repair complete |
| HM battle rework | LOCKED | 5 changed, 3 retained |
| TM roster | LOCKED | TM21 Air Slash; TM78 Power Gem; 90 unchanged |
| TM acquisition policy | LOCKED | Preserve first-acquisition progression |
| TM economy | LOCKED | Department Store mostly preserved; Game Corner/Frontier grind reduced |
| TM/HM compatibility framework | LOCKED | Vanilla baseline; selective additions only |
| TM21 Air Slash compatibility | LOCKED | 49 recipients |
| TM78 Power Gem compatibility | LOCKED | 27 recipients |
| Retype-family compatibility additions | LOCKED | 11 original additions plus Raichu TM91 source reconciliation at implementation |
| Created move set | LOCKED | 22 moves: 9 generic + 13 identity |
| Created move feasibility | LOCKED | All 22 retained |
| Level-up learnsets | LOCKED | C3 closed |
| Evolution timing audit | LOCKED | One Banette correction; no remaining known conflict |
| Natural-STAB/dead-slot audit | LOCKED | No further correction required after Banette |
| Tutor consolidation | LOCKED | No created move becomes a general tutor in Core 1.0 |
| Egg-move consolidation | LOCKED | Vanilla baseline; breeding not required for basic functionality |
| World/encounter overhaul | PLANNED | Next major design/implementation phase after core implementation |
| Trainer overhaul | PLANNED | Not yet canonicalized in detail |
| Economy/EXP port | PLANNED | Emerald port candidate |
| Capture/Poké Ball port | PLANNED | Emerald port candidate; Platinum has more native specialist balls |
| Breeding system port | PLANNED | Emerald ideas require Platinum-specific audit |
| Event restoration | PLANNED | Prefer Platinum-native event infrastructure |
| Frontier/postgame | PLANNED | Later phase |
| Full QA/release | PLANNED | Release-blocking phase |

## Created-move implementation checkpoint

### Allocation

- 22 custom moves total.
- IDs `468–489`.
- Generic moves: `468–476`.
- Identity moves: `477–489`.
- Target `MAX_MOVES`: `490`.

### Technical resolution

The latest recovered source-plumbing checkpoint establishes:

- authoritative move enum input: `generated/moves.txt`
- Resonant Slash must be added to `sSoundMoves`
- Star Jab must be added to `sPunchingMoves`
- Magnet Volley uses the existing multi-hit machinery with `SetMultiHit 3, SYSCTL_MULTI_HIT_MOVE`
- Magnet Volley must deal equal power on all three hits: `25 + 25 + 25`
- Triple Kick-style per-hit power escalation must not be used
- retail animation/move-script padding `490–500` is preserved
- move-data handling must support the expanded custom move records

The previously generated apply script passed syntax/invariant inspection. A local dry run failed because it was pointed at an empty/non-Platinum directory, not because the source guards were disproven.

### Build gate

Before species ledgers are applied:

1. validate all 22 generated move directories/resources against the real repository
2. apply move enum/data/text/script/animation/contest plumbing
3. apply sound/punch registry changes
4. verify Magnet Volley behavior
5. audit `MAX_MOVES`-sized consumers
6. build
7. only then allow species learnsets to reference the new constants

## Species implementation checkpoint

Recovered implementation planning reached at least:

- **225 guarded Pokémon operations** across C3H-L1 through C3H-L5
- operations include:
  - `set_base_stat`
  - `set_types`
  - `set_abilities`
  - `insert_level_move`
  - `replace_level_move`
  - `remove_level_move`

The ROM Mod Toolkit workflow uses expected-original-value guards and file SHA-256 checks.

### Known authoritative final correction

Banette:

- leave Shadow Ball at Lv31
- evolve from Shuppet at Lv37
- insert Cursed Stitch at Lv38
- replace Embargo Lv42 with Shadow Claw Lv42

Any older C3D11 instruction replacing Shadow Ball Lv31 with Cursed Stitch is **SUPERSEDED**.

## TM/HM compatibility implementation checkpoint

Recovered compatibility implementation contains:

- TM21 Air Slash: 49 locked recipients
- TM78 Power Gem: 27 locked recipients
- 12 explicit additions in the implementation set
  - 11 design-locked retype-family additions
  - Raichu TM91 Flash Cannon source reconciliation

A recovered compatibility checkpoint reported:

- pinned source commit: `0fee7dc526f3220dc6a3b58986415446423f83de`
- syntax/invariant validation: PASS

Important: the Pokémon guarded ledger schema did not support arbitrary TM add/remove operations at that checkpoint, so compatibility work was separated into a guarded general source patch.

## Final C3 policy reminders

### Machines

- Created moves do not consume TM slots.
- TM21/TM78 replacement masks must be rebuilt; old Frustration/Captivate compatibility must not leak through.
- No broad compatibility expansion merely because a Pokémon gained a new type.

### Tutors

- Tutors are specialization, not baseline functionality.
- No created identity move becomes a general tutor in Core 1.0.
- No generic created move becomes a tutor until balance testing supports broader distribution.

### Egg moves

- Vanilla Platinum egg pools remain the baseline.
- Breeding must not be required for ordinary STAB or campaign functionality.
- Identity moves tied to evolved anatomy/state should not be pushed into base-form egg pools.

## Historical unresolved item

`Dragon Swipe` remains a finalized move definition, but the recovered final C3 checkpoints did not prove an authoritative final recipient. The final audit deliberately did **not** invent one.

Status:

- move remains valid and implemented as part of the 22-move set
- no new recipient should be invented during implementation
- distribution remains a documentation/recovery item, not a build blocker

## Next actions

### Implementation

1. Finish created-move resource validation and build gate.
2. Apply guarded species ledgers.
3. Apply compatibility patch.
4. Build + semantic-diff + runtime validation.

### Planning

1. Complete Emerald-to-Platinum port matrix.
2. Canonicalize evolution system decisions.
3. Build the #001–#493 availability/encounter plan.
4. Canonicalize trainers/economy/events/postgame.

## Rule for future sessions

Do not reconstruct project status from memory when this file answers the question. Update this file in the same commit/PR that materially changes project state.
