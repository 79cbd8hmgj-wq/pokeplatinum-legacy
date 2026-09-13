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
- Machine-readable canonical manifests/ledgers override older prose when they explicitly encode a later locked correction.
- Historical proposal files marked `Needs approval`, `Proposed`, or similar are not final authority.
- Chat history is recovery evidence only when the repo explicitly says canonicalization is still incomplete.

## Current checkpoint

Planning/design through C3 is closed. Implementation is in **C2.5E / C3H**.

Implementation order:

1. Implement the 22 created moves (IDs 468–489; target `MAX_MOVES = 490`).
2. Run the created-move build/resource gate. Do not proceed if it fails.
3. Apply the exact guarded C3 species ledgers.
4. Apply the locked TM/HM compatibility patch.
5. Build and perform semantic/runtime verification.
6. Only then continue to the next master-plan phase.

## Critical created-move facts

- Created move authority: `docs/overhaul/moves/CREATED_MOVES.md`
- Machine-readable authority: `docs/overhaul/implementation/created_moves_manifest.json`
- Resonant Slash must be registered as a sound move.
- Star Jab must be registered as a punching move.
- Magnet Volley must hit **exactly three times at equal 25 BP per hit** (25+25+25), with no Triple Kick-style power escalation.
- Dragon Swipe is finalized as a move, but its historical final C3 recipient remains unresolved. **Do not invent a recipient.**

## Critical C3 species facts

The exact historical species implementation consisted of five ledgers with operation counts:

`[67, 27, 40, 53, 38] = 225 total operations`

Historical source of truth:

- commit: `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob: `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- archived copy: `docs/overhaul/implementation/archive/c3h-apply-species-original.yml`
- deterministic verifier/extractor: `tools/overhaul/recover_c3h_ledgers.py`

Never substitute the known superseded inferred L3 reconstruction from old branch history.

### Banette correction

The final-audit correction is authoritative:

- Shadow Ball Lv31 remains.
- Cursed Stitch is inserted at Lv38.
- Shadow Claw is Lv42.

Any older ledger or prose that replaces Shadow Ball Lv31 with Cursed Stitch is superseded.

## TM/HM authority

See `docs/overhaul/tm_hm/TM_HM_SPEC.md` and `docs/overhaul/implementation/tm_compat_manifest.json`.

Key invariants:

- TMs are reusable.
- TM21 = Air Slash; rebuild its compatibility from the locked 49-recipient list.
- TM78 = Power Gem; rebuild its compatibility from the locked 27-recipient list.
- Old Frustration/Captivate masks must not leak into the replacement slots.
- Apply the explicit compatibility additions, including the Raichu TM91 Flash Cannon reconciliation.

## C1 recovery status

C1 design is complete and locked. The final audit records **82 existing move edits**. Canonical repo recovery of that complete 82-move ledger is still being finalized.

Until the canonical C1 manifest is present:

- do not use old proposal spreadsheets as implementation authority;
- do not infer missing move values;
- report any C1-dependent implementation need as blocked on canonical recovery.

## Required implementation behavior

For every implementation batch:

- pin/report the source commit you started from;
- preserve before-value/source guards where supplied;
- fail closed on unexpected source state;
- make the smallest source-level change that implements the locked design;
- prefer Platinum source/resource edits over binary patches;
- use disassembly/runtime tooling only for genuine engine ambiguity;
- do not silently broaden scope.

Before calling a batch complete, report:

1. files changed;
2. commit/branch;
3. exact validation/build commands run;
4. results;
5. runtime checks performed, if applicable;
6. any discrepancy from the canonical spec;
7. any blocker or unresolved design question.

If an approved spec and the live source disagree, **do not resolve the design yourself**. Document the discrepancy and stop that affected change until it is reconciled.
