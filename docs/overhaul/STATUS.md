# Pokémon Platinum Overhaul — Current Status

Last verified against repository/project history: 2026-09-13.

## Executive status

- **Design:** Pokémon/move design through C3 is closed.
- **C2.5E created moves:** IMPLEMENTED + L2 BUILD VERIFIED on `main`.
- **C3H species + TM compatibility:** IMPLEMENTED + L2 BUILD VERIFIED on `main`.
- **C1 existing-move rebalance:** LOCKED, fully recovered into an 82-edit canonical manifest, **not yet implemented** on `main`.
- **Evolution design:** **LOCKED in Pass A** across #001–#493; complete historical master had 50 consolidated type/evolution decisions. The repo still needs the complete machine-readable evolution manifest reconstructed from that locked authority.
- **Known design blockers:** 0.
- **Next source task:** guarded C1 implementation against current `main`, then remaining C2 mechanics and focused runtime QA.

## Mainline implementation evidence

### Created moves

Commit `071b8c7976801e64af5296f30b7437d7da2d8632` — **Implement Platinum overhaul custom moves and mod-aware CI**

Implements all 22 created moves, IDs 468–489, move-table plumbing / `MAX_MOVES = 490`, text/scripts/animations, Resonant Slash sound registration, Star Jab punching registration, Magnet Volley exact-three-hit support, and a Rev 0/Rev 1 CI matrix.

GitHub Actions run `33981291318`: **SUCCESS**.

Status: source implemented; L2 build verified; focused L4 runtime behavior still pending.

### Species + TM compatibility

Commit `8a74452654e1552b78bfb329afcb351a2caec5cf` — **Apply C3H species and TM compatibility overhaul**

Applies the TM21/TM78 compatibility rebuild, explicit compatibility additions, 225 guarded C3 species operations, and final Torkoal/Seviper corrections.

GitHub Actions run `33995072848`: **SUCCESS**.

Status: source implemented; L2 build verified; runtime/campaign QA still pending.

## Canonical documentation

Branch: `overhaul/canonical-docs`

Draft PR: **#8**

Historical recovery branches:

- `overhaul/c3h-species-compat`
- `overhaul/c3h-ledger-archive`

They are provenance sources, not current implementation targets.

## Completion matrix

| Area | Design | Implementation | Verification |
|---|---|---|---|
| Core project identity | LOCKED | n/a | n/a |
| Types/stats/abilities/roles | LOCKED | IMPLEMENTED through C3H | L2 build |
| Existing move rework (C1) | LOCKED / CANONICALIZED | NOT YET IMPLEMENTED | pending |
| Created moves (C2.5E) | LOCKED | IMPLEMENTED | L2 build |
| C3 learnsets/species edits | LOCKED | IMPLEMENTED | L2 build |
| TM21/TM78 compatibility | LOCKED | IMPLEMENTED | L2 build |
| Retype compatibility additions | LOCKED | IMPLEMENTED | L2 build |
| Reusable TMs | LOCKED | not yet fully audited/implemented | pending |
| HM battle rework | LOCKED | not yet fully audited/implemented | pending |
| TM acquisition/economy | LOCKED | not yet fully audited/implemented | pending |
| Tutor consolidation | LOCKED | baseline retained | audit pending |
| Egg-move consolidation | LOCKED | baseline retained | audit pending |
| Evolution-method overhaul | **LOCKED / RECOVERY NEEDED FOR FULL MANIFEST** | not yet implemented as a complete system | pending |
| World/#001–#493 availability | PLANNED | not started | pending |
| Trainer overhaul | PLANNED | not started | pending |
| Economy/EXP port | PLANNED PORT | not started | pending |
| Capture/Poké Ball port | PLANNED PORT | not started | pending |
| Breeding-system port | PLANNED PORT | not started | pending |
| Event restoration | PLANNED | not started | pending |
| Frontier/postgame | PLANNED | partial design only | pending |
| Full QA/release | PLANNED | not started | pending |

## C1 authority

C1 final audit contains exactly **82 edited existing moves**.

Canonical authority:

- human-readable: `moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`
- machine-readable: `implementation/c1_move_changes_manifest.json`
- membership/provenance: `implementation/c1_move_edit_membership_recovery.json`
- recovery evidence: `moves/C1_RECOVERED_BATCHES_SUPPLEMENT.md`

The machine manifest contains exactly **82 entries** and changes only listed fields.

### Final Batch 9F values

- Bind — 30 / 90 / 20
- Wrap — 30 / 90 / 20
- Fire Spin — 35 / 90 / 15
- Whirlpool — 35 / 90 / 15
- Sand Tomb — 35 / 90 / 15
- Clamp — 35 / 90 / 10
- Magma Storm — KEEP 120 / 70 / 5

Trapping duration/residual behavior is unchanged.

The previously surfaced Sand Tomb 50/95 value came from an unrelated Emerald move-rework spec and is **not Platinum C1 authority**.

### C1 implementation state

C1 has not yet been applied to current main; for example, Fury Cutter remains vanilla in source.

Next implementation procedure:

1. inspect current move files;
2. generate before-value/source guards;
3. apply `implementation/c1_move_changes_manifest.json`;
4. assert exact edit count = 82;
5. update Razor Wind's description alongside its effect reassignment;
6. semantic-diff the move table;
7. build Rev 0 and Rev 1;
8. record evidence in this file.

## Evolution authority

Evolution was part of **Pass A: Identity & Evolution**, not an undesigned future phase.

Canonical recovery entry:

`evolution/EVOLUTION_SPEC.md`

Final global rule:

> **Evolution stones are the only evolution items. No trade or held non-stone item is required for evolution.**

Recovered locked examples include:

- Kadabra/Machoke/Graveler/Haunter → Lv36 final evolutions;
- Onix → Steelix Lv35;
- Scyther → Scizor Lv38;
- Seadra → Kingdra Lv42;
- Electabuzz/Magmar → Lv42 final evolutions;
- Rhydon → Rhyperior Lv52;
- Porygon → Porygon2 Lv30 → Porygon-Z Lv45;
- Dusclops → Dusknoir Lv45;
- Gligar/Sneasel → Lv38 at night;
- Poliwhirl/Slowpoke/Clamperl branch logic uses stat comparisons;
- genuine stones, location evolutions, Beauty, Wurmple/Shedinja, and other identity-positive mechanics are retained.

The historical locked Pass A master contained **50 consolidated type/evolution decisions**. The remaining task is to recover/check in the full machine-readable evolution manifest and map it to source—not to redesign the system.

## C3 provenance

Exact historical species payload:

`implementation/archive/c3h-apply-species-original.yml`

- historical commit: `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob: `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- ledger counts: `67 / 27 / 40 / 53 / 38 = 225`

Verifier/extractor:

`tools/overhaul/recover_c3h_ledgers.py`

These ledgers are provenance only. Do **not** reapply them over current main.

Final corrections visible on main:

- Banette: Shadow Ball 31; Cursed Stitch 38; Shadow Claw 42.
- Torkoal: Yawn 52; Heat Wave 55.
- Seviper: Sludge Bomb 55.

## Focused runtime QA still required

High-priority L4 checks:

- Resonant Slash sound/Soundproof interaction;
- Star Jab punching/Iron Fist interaction;
- Magnet Volley exactly 3 equal-power hits (`25 + 25 + 25` before normal modifiers);
- representative custom move effects/text/animations;
- Defog behavior once C2 HM work is implemented/audited;
- representative C3 evolution-timing and compatibility cases.

## Historical unresolved design item

`Dragon Swipe` is implemented as a finalized move, but recovered C3 documentation does not prove a final recipient.

Do not invent one. This is not a build blocker.

## Immediate next actions

1. Apply C1 from the canonical manifest with live-source guards.
2. Build Rev 0 + Rev 1 and archive validation evidence.
3. Audit/implement remaining C2 reusable-TM/HM/economy behavior.
4. Run focused L4 runtime QA for C2.5/C3 high-risk mechanics.
5. Reconstruct the complete locked Pass A evolution manifest and implement it; **no new evolution-design pass is required**.
6. Perform the remaining Emerald-to-Platinum port audit for EXP/economy/capture/breeding.
7. Continue into #001–#493 availability, trainers, economy, events, and postgame.

## Rule for future sessions

Do not reconstruct status from memory when this file answers the question. Update this file in the same branch/PR that materially changes project state.
