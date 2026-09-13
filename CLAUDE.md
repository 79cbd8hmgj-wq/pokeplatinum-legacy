# Claude Code Handoff — Pokémon Platinum Overhaul

This repository is the implementation source of truth. Do not reconstruct approved design from chat history when canonical repo documentation exists.

## Official role boundary

Future unfinished subsystem design is owned by **Codex `/plan`**, following `/AGENTS.md`.

Claude Code's role is:

- implement approved/locked Codex plans;
- inspect source as needed to implement them correctly;
- generate guarded edits/manifests/scripts;
- build, test, validate, and report discrepancies;
- update implementation/status documentation after changes land.

Claude Code must **not** take ownership of future design planning unless the user explicitly asks it to. If implementation reveals a genuine design ambiguity, stop the affected change and report the issue rather than choosing a new design independently.

Default workflow:

> **Codex `/plan` → user approval → canonical repo spec/manifest → Claude Code implementation → validation/status update**

## Read first

1. `AGENTS.md`
2. `docs/overhaul/README.md`
3. `docs/overhaul/MASTER_PLAN.md`
4. `docs/overhaul/STATUS.md`
5. `docs/overhaul/MASTER_SPEC.md`
6. `docs/overhaul/IMPLEMENTATION_PLAN.md`
7. The relevant approved/locked subsystem spec under `docs/overhaul/`
8. Machine-readable manifests/ledgers under `docs/overhaul/implementation/`

## Authority rules

- **LOCKED SPEC** is implementation authority. Do not redesign it unilaterally.
- A Codex `DRAFT PLAN` is not implementation authority.
- **SUPERSEDED** material must not be implemented.
- **UNRESOLVED** means stop and report the ambiguity; do not guess.
- Current `main` source wins over historical application ledgers when determining what is already implemented.
- Machine-readable canonical manifests override older prose when they explicitly encode a later locked correction.
- Historical proposal files marked `Needs approval`, `Proposed`, or similar are not final authority.

## Current checkpoint

Planning/design through C3 is closed.

**Do not implement C2.5E/C3H from scratch. It already landed on `main`.**

### Landed created-move implementation

Commit `071b8c7976801e64af5296f30b7437d7da2d8632`

- all 22 custom moves and move-table plumbing;
- mod-aware Rev 0 / Rev 1 CI build matrix;
- GitHub Actions run `33981291318`: success.

### Landed C3H implementation

Commit `8a74452654e1552b78bfb329afcb351a2caec5cf`

- C3H TM compatibility rebuild;
- 225 guarded Pokémon operations;
- final Torkoal correction;
- final Seviper correction;
- GitHub Actions run `33995072848`: success.

Starting assumption:

> C2.5E/C3H are **implemented and L2 build-verified**, but still need focused runtime/semantic QA. Do not reapply historical ledgers over current `main`.

## Immediate implementation priorities

1. Audit current `main` against canonical specs; do not redo landed C2.5E/C3H work.
2. Implement C1 from `docs/overhaul/implementation/c1_move_changes_manifest.json` using live-source before-value guards.
3. Build both supported US revisions.
4. Audit/implement remaining C2 mechanics: reusable TMs, HM battle changes, TM source/economy rules.
5. Run focused runtime tests for custom/high-risk mechanics.
6. Implement the locked Pass A evolution design once its canonical manifest/source mapping is ready.
7. For genuinely unfinished design areas, wait for approved Codex `/plan` output before implementation.

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

Focused runtime verification is still required even though the build passes.

Dragon Swipe is implemented as a finalized move, but its historical final C3 recipient remains unresolved. **Do not invent a recipient.**

## Critical C3 species facts

The historical species implementation consisted of five guarded ledgers totaling:

`[67, 27, 40, 53, 38] = 225 operations`

Historical provenance:

- commit: `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob: `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- archived copy: `docs/overhaul/implementation/archive/c3h-apply-species-original.yml`
- verifier/extractor: `tools/overhaul/recover_c3h_ledgers.py`

These are provenance/audit material, not instructions to reapply them to current main.

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

Key invariants:

- TM21 = Air Slash using the locked 49-recipient mask.
- TM78 = Power Gem using the locked 27-recipient mask.
- Old Frustration/Captivate masks must not leak into replacement slots.
- Explicit additions include the Raichu TM91 Flash Cannon reconciliation.

Reusable-TM behavior, HM battle changes, TM economy/source policy, and other C2 implementation details still need separate implementation/audit unless current source proves they already landed.

## C1 authority

C1 design is complete and locked. C1 is **not yet implemented** on current main; Fury Cutter is still vanilla in source.

Canonical authority:

- human-readable: `docs/overhaul/moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`
- machine-readable: `docs/overhaul/implementation/c1_move_changes_manifest.json`
- historical recovery evidence: `docs/overhaul/moves/C1_RECOVERED_BATCHES_SUPPLEMENT.md`

The manifest contains exactly **82 edits**.

### Batch 9F final Platinum values

- Bind — 30 / 90 / 20
- Wrap — 30 / 90 / 20
- Fire Spin — 35 / 90 / 15
- Whirlpool — 35 / 90 / 15
- Sand Tomb — 35 / 90 / 15
- Clamp — 35 / 90 / 10
- Magma Storm — KEEP 120 / 70 / 5

Trapping duration/residual behavior remains unchanged.

The previously surfaced Sand Tomb **50/95** value belongs to a separate Emerald move-rework spec and is explicitly **not Platinum C1 authority**.

### C1 implementation rules

- inspect each current move file first;
- generate before-value/source guards from current `main`;
- apply only fields listed under each manifest entry's `target`;
- preserve all other fields/effects/flags unless the manifest says otherwise;
- Razor Wind is the only effect reassignment: `BATTLE_EFFECT_CHARGE_TURN_HIGH_CRIT` → `BATTLE_EFFECT_HIGH_CRITICAL`;
- update Razor Wind's description so it no longer claims to be a two-turn move;
- assert exact applied edit count = 82;
- run semantic diff and Rev 0 / Rev 1 builds.

Do not substitute values from older proposal spreadsheets or Emerald move specs.

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
