# Claude Code Handoff — Pokémon Platinum Overhaul

This repository is the implementation source of truth. Do not reconstruct approved design from chat history when canonical repo documentation exists.

## Read first

1. `docs/overhaul/README.md`
2. `docs/overhaul/MASTER_PLAN.md`
3. `docs/overhaul/STATUS.md`
4. `docs/overhaul/MASTER_SPEC.md`
5. `docs/overhaul/IMPLEMENTATION_PLAN.md`
6. The relevant subsystem spec under `docs/overhaul/`
7. Machine-readable manifests/ledgers under `docs/overhaul/implementation/`

## Authority rules

- **LOCKED** design is implementation authority. Do not redesign it unilaterally.
- **SUPERSEDED** material must not be implemented.
- **UNRESOLVED** means stop and report the ambiguity; do not guess.
- Current `main` source wins over historical application ledgers when determining what is already implemented.
- Machine-readable canonical manifests override older prose when they explicitly encode a later locked correction.
- Historical proposal files marked `Needs approval`, `Proposed`, or similar are not final authority.
- Chat history is recovery evidence only where the repo explicitly says canonicalization is incomplete.

## Current checkpoint

Planning/design through C3 is closed.

**Do not implement C2.5E/C3H from scratch. It already landed on `main`.**

### Landed created-move implementation

Commit:

`071b8c7976801e64af5296f30b7437d7da2d8632`

This implements all 22 custom moves and move-table plumbing, plus a mod-aware Rev 0/Rev 1 CI build matrix.

GitHub Actions run `33981291318` completed successfully.

### Landed C3H implementation

Commit:

`8a74452654e1552b78bfb329afcb351a2caec5cf`

This applies:

- C3H TM compatibility rebuild;
- 225 guarded Pokémon operations;
- final Torkoal correction;
- final Seviper correction.

GitHub Actions run `33995072848` completed successfully.

Therefore your starting assumption is:

> C2.5E/C3H are **implemented and L2 build-verified**, but still need focused runtime/semantic QA. Do not reapply historical ledgers over current `main`.

## Immediate implementation priorities

1. Audit current `main` against the canonical specs; do not redo landed C2.5E/C3H work.
2. Wait for the final canonical C1 manifest before implementing C1 existing-move edits.
3. Once C1 recovery is complete, implement the exact 82-edit manifest against current `main` with before-value guards.
4. Build both supported US revisions.
5. Run focused runtime tests for custom/high-risk mechanics.
6. Continue to evolution-system implementation and Emerald-to-Platinum port audit according to `MASTER_PLAN.md`.

## Critical created-move facts

Design authority:

- `docs/overhaul/moves/CREATED_MOVES.md`
- `docs/overhaul/implementation/created_moves_manifest.json`

Implementation facts:

- IDs 468–489
- `MAX_MOVES = 490`
- Resonant Slash is registered as a sound move.
- Star Jab is registered as a punching move.
- Magnet Volley must hit **exactly three times at equal 25 BP per hit** (25+25+25), with no Triple Kick-style escalation.

Focused runtime verification is still required for those interactions even though the build passes.

Dragon Swipe is implemented as a finalized move, but its historical final C3 recipient remains unresolved. **Do not invent a recipient.**

## Critical C3 species facts

The historical species implementation consisted of five guarded ledgers totaling:

`[67, 27, 40, 53, 38] = 225 operations`

Historical provenance:

- commit: `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob: `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- archived copy: `docs/overhaul/implementation/archive/c3h-apply-species-original.yml`
- verifier/extractor: `tools/overhaul/recover_c3h_ledgers.py`

These are **provenance and audit material**, not instructions to reapply them to current main.

Never substitute the known superseded inferred L3 reconstruction from old branch history.

### Final corrections

Current main/final audit authority includes:

- Banette: Shadow Ball Lv31 remains; Cursed Stitch Lv38; Shadow Claw Lv42.
- Torkoal: Yawn Lv52; Heat Wave Lv55.
- Seviper: Sludge Bomb Lv55.

Any older ledger/prose conflicting with these is superseded.

## TM/HM authority

See:

- `docs/overhaul/tm_hm/TM_HM_SPEC.md`
- `docs/overhaul/implementation/tm_compat_manifest.json`

The C3H compatibility changes are already applied on main. Audit them; do not blindly reapply them.

Key invariants remain:

- TM21 = Air Slash using the locked 49-recipient mask.
- TM78 = Power Gem using the locked 27-recipient mask.
- Old Frustration/Captivate masks must not leak into replacement slots.
- Explicit additions include the Raichu TM91 Flash Cannon reconciliation.

Reusable-TM behavior, HM battle changes, TM economy/source policy, and other C2 implementation details still need separate implementation/audit unless current source proves they already landed.

## C1 recovery status

C1 design is complete and locked. C1 is **not yet implemented** on current main; for example, Fury Cutter remains vanilla in source.

Recovery status:

- all **82/82 edited move names** are enumerated in `docs/overhaul/implementation/c1_move_edit_membership_recovery.json`;
- confirmed values/rulings are in:
  - `docs/overhaul/moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`
  - `docs/overhaul/moves/C1_RECOVERED_BATCHES_SUPPLEMENT.md`
- final superseding values remain unresolved for five Batch 9F moves:
  - Bind
  - Wrap
  - Fire Spin
  - Whirlpool
  - Clamp
- Sand Tomb is independently confirmed at **50 BP / 95 Acc / 15 PP**.

Until the final 82-edit implementation manifest is checked in:

- do not implement C1 from an old proposal spreadsheet;
- do not infer the five unresolved trapping values;
- do not substitute Emerald move-rework values for Platinum C1;
- report C1 implementation as blocked on canonical recovery if asked to apply it prematurely.

## Required implementation behavior

For every implementation batch:

- pin/report the source commit you started from;
- inspect current source first so already-landed work is not repeated;
- preserve before-value/source guards where supplied;
- fail closed on unexpected source state;
- make the smallest source-level change that implements locked design;
- prefer Platinum source/resource edits over binary patches;
- use disassembly/runtime tooling only for genuine engine ambiguity;
- do not silently broaden scope;
- update `docs/overhaul/STATUS.md` when project state materially changes.

Before calling a batch complete, report:

1. files changed;
2. commit/branch;
3. exact validation/build commands run;
4. results;
5. runtime checks performed, if applicable;
6. any discrepancy from canonical spec;
7. any blocker/unresolved design question;
8. whether status/docs were updated.

If an approved spec and live source disagree, **do not resolve the design yourself**. Document the discrepancy and stop the affected change until it is reconciled.
