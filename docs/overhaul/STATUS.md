# Pokémon Platinum Overhaul — Current Status

Last verified against repository history: 2026-09-13.

## Executive status

**Design:** Pokémon/move design through C3 is closed.

**C2.5E created moves:** **IMPLEMENTED + L2 BUILD VERIFIED** on `main`.

**C3H species + TM compatibility:** **IMPLEMENTED + L2 BUILD VERIFIED** on `main`.

**C1 existing-move rebalance:** design complete/locked; **not yet implemented** on `main`; canonical recovery is almost complete.

**Known design blockers:** 0.

**Remaining completed-design recovery blocker:** final superseding values for five Batch 9F trapping moves before C1 can be converted into a complete implementation manifest.

## Mainline implementation evidence

### Created moves

Commit:

`071b8c7976801e64af5296f30b7437d7da2d8632` — **Implement Platinum overhaul custom moves and mod-aware CI**

This commit implements:

- all 22 created moves;
- IDs 468–489;
- move-table plumbing / `MAX_MOVES` expansion;
- custom move resources/text/scripts/animations;
- Resonant Slash sound registration;
- Star Jab punching registration;
- Magnet Volley exact-three-hit effect support;
- mod-aware CI matrix for both supported US revisions.

GitHub Actions build run `33981291318` completed successfully. The workflow matrix builds US revisions 0 and 1.

**Status:** source implemented; L2 build verified. Focused runtime behavior is still a separate L4 verification task.

### Species + TM compatibility

Commit:

`8a74452654e1552b78bfb329afcb351a2caec5cf` — **Apply C3H species and TM compatibility overhaul**

This commit applies:

- the C3H TM21/TM78 compatibility rebuild;
- explicit compatibility additions;
- the 225 guarded C3 species operations;
- final Torkoal learnset correction;
- final Seviper learnset correction.

GitHub Actions build run `33995072848` completed successfully under the same Rev 0/Rev 1 build matrix.

**Status:** source implemented; L2 build verified. Runtime/campaign verification remains future QA.

### Current mainline baseline

The documentation branch was created from `main` after the C2.5E/C3H implementation landed. Claude must therefore **audit/continue from the existing implementation**, not reapply the historical ledgers over `main`.

Historical ledgers remain useful for provenance and semantic verification only.

## Canonical documentation branch

`overhaul/canonical-docs`

Draft PR: **#8**

Existing historical branches include:

- `overhaul/c3h-species-compat`
- `overhaul/c3h-ledger-archive`

They are recovery/provenance sources, not the current implementation target.

## Design completion matrix

| Area | Design | Implementation | Verification |
|---|---|---|---|
| Core project identity | LOCKED | n/a | n/a |
| Types/stats/abilities/roles | LOCKED | IMPLEMENTED through C3H | L2 build |
| Existing move rework (C1) | LOCKED | NOT YET IMPLEMENTED | pending |
| HM battle rework | LOCKED | not fully audited as implemented | pending |
| TM roster | LOCKED | compatibility side implemented; broader reusable-TM/economy behavior still separate | partial |
| TM acquisition/economy | LOCKED | not yet fully implemented/audited | pending |
| TM21 Air Slash compatibility | LOCKED | IMPLEMENTED | L2 build |
| TM78 Power Gem compatibility | LOCKED | IMPLEMENTED | L2 build |
| Retype compatibility additions | LOCKED | IMPLEMENTED | L2 build |
| Created move set | LOCKED | IMPLEMENTED | L2 build |
| Level-up learnsets | LOCKED | IMPLEMENTED through C3H | L2 build |
| Evolution timing audit | LOCKED | reflected in C3 implementation | L2 build; campaign QA pending |
| Tutor consolidation | LOCKED | design baseline retained | audit pending |
| Egg-move consolidation | LOCKED | vanilla baseline retained unless explicitly changed | audit pending |
| Evolution-method overhaul | PARTIAL | not yet canonicalized/implemented as a complete system | pending |
| World/encounter overhaul | PLANNED | not started | pending |
| Trainer overhaul | PLANNED | not started | pending |
| Economy/EXP port | PLANNED PORT | not started | pending |
| Capture/Poké Ball port | PLANNED PORT | not started | pending |
| Breeding-system port | PLANNED PORT | not started | pending |
| Event restoration | PLANNED | not started | pending |
| Frontier/postgame | PLANNED | partial TM-BP design only | pending |
| Full QA/release | PLANNED | not started | pending |

## C1 recovery status

The historical C1 final audit contains **82 edited existing moves**.

Repository recovery now has:

- exact membership of all **82/82** edits in `implementation/c1_move_edit_membership_recovery.json`;
- recovered final values for all batches except part of Batch 9F;
- human-readable recovery authority in:
  - `moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`
  - `moves/C1_RECOVERED_BATCHES_SUPPLEMENT.md`

Batch 9F membership is exactly:

- Bind
- Wrap
- Fire Spin
- Whirlpool
- Sand Tomb
- Clamp

Sand Tomb is independently confirmed at **50 BP / 95 Acc / 15 PP**.

The final superseding values for **Bind, Wrap, Fire Spin, Whirlpool, and Clamp** still require exact final-audit recovery before generating the authoritative 82-edit implementation manifest.

Do not infer those values from older proposal material.

## C3 provenance

The exact historical species implementation payload is preserved at:

`docs/overhaul/implementation/archive/c3h-apply-species-original.yml`

Historical provenance:

- commit `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- exact operation counts `67 / 27 / 40 / 53 / 38 = 225`

`tools/overhaul/recover_c3h_ledgers.py` verifies/extracts the historical ledger set.

Important: these ledgers are now provenance. **Do not reapply them to current `main`.** Current source already contains the implementation plus final follow-up corrections.

### Authoritative final corrections visible on current main

- Banette: Shadow Ball 31 retained; Cursed Stitch 38; Shadow Claw 42.
- Torkoal: Yawn 52; Heat Wave 55.
- Seviper: Sludge Bomb 55.

## Created-move invariants still needing focused runtime QA

Source/build success does not prove every battle interaction.

High-priority L4 checks:

- Resonant Slash is blocked/recognized by sound-move logic as intended;
- Star Jab receives punching/Iron Fist handling;
- Magnet Volley produces exactly three equal-power hits (`25 + 25 + 25` before normal modifiers);
- custom move text/animation behavior is correct in battle;
- representative custom effects behave as specified.

## Historical unresolved design item

`Dragon Swipe` is implemented as one of the 22 moves, but recovered final C3 documentation does not prove a final recipient.

- do not invent a recipient;
- absence of a recipient is not a build blocker;
- resolve only from authoritative recovered design evidence or a new explicit design decision.

## Immediate next actions

### Repository preparation

1. Finish C1 recovery by resolving the five remaining Batch 9F values.
2. Generate the complete machine-readable 82-edit C1 implementation manifest.
3. Validate that manifest against current `main` before Claude applies C1.
4. Preserve mainline C2.5E/C3H commits/build evidence in the canonical docs.
5. Merge the canonical documentation PR only after authority/status files agree.

### Claude implementation after handoff

1. **Do not redo C2.5E/C3H.** Audit current main and use the landed commits as baseline.
2. Implement C1 from the final canonical manifest once recovery is complete.
3. Run source/build validation for C1.
4. Perform focused L4 runtime tests for custom moves and other high-risk mechanics.
5. Begin the Emerald-to-Platinum port audit and evolution-system work.
6. Continue into #001–#493 availability, trainers, economy, events, and postgame according to `MASTER_PLAN.md`.

## Rule for future sessions

Do not reconstruct status from memory when this file answers the question. Update this file in the same branch/PR that materially changes project state.
