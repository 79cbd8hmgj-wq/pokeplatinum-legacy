# C3 Species Implementation Authority

Status: **LOCKED DESIGN / IMPLEMENTED HISTORICALLY / CANONICAL RECOVERY IN PROGRESS**

This file records the strongest surviving implementation authority for Pass C3. It exists so C3 is never reconstructed from memory or redesigned because an old ledger file was removed from a working branch.

## Authoritative conclusion

The C3 design is **not missing** and is **not open for redesign**.

The complete guarded species implementation was applied on the historical branch `overhaul/c3h-species-compat` in commit:

- `e93080d07141426042504363e385c121fbe88d89` — **Apply C3H 225 species operations**

Two explicit post-application corrections then followed:

- `e21bf6d81e08c10bf335dcad3097f3597f8b9d15` — **Apply final C3 Torkoal learnset correction**
- `887c0d8a17104cebfab2d66b284b1ee7feae7f20` — **Apply final C3 Seviper learnset correction**

Therefore, for species fields covered by C3 (types, base stats, abilities, and level-up learnsets), the source state at:

`887c0d8a17104cebfab2d66b284b1ee7feae7f20`

is the strongest surviving implementation snapshot after the 225-operation batch and its known follow-up corrections.

## Guard/source baseline

The historical recovery workflows pin their before-state validation to:

`0fee7dc526f3220dc6a3b58986415446423f83de`

Historical guarded ledgers used SHA-256 checks against `res/pokemon/<species>/data.json` from that source state.

## Important precedence rules

1. **Final source state beats reconstructed prose.** If a later recovery note conflicts with the actual applied source state at the authoritative snapshot, investigate the conflict; do not silently overwrite the source with the note.
2. **Final-audit corrections beat older C3 batches.** In particular, Banette's final ruling remains Shadow Ball 31, Cursed Stitch 38, Shadow Claw 42.
3. **TM/HM compatibility is a separate authority.** `by_tm` changes are governed by `docs/overhaul/tm_hm/TM_HM_SPEC.md` and `docs/overhaul/implementation/tm_compat_manifest.json`, not regenerated from this species authority.
4. **Created moves are a separate build dependency.** Species learnsets that reference custom `MOVE_*` constants must only be applied after created-move plumbing builds successfully.
5. Later commits named as recovery/rebuild hypotheses are **not automatically authoritative**. Several temporary L3/L4 reconstruction workflows were later removed or explicitly marked superseded.

## Historical ledger evidence

Git history confirms the project used semantic guarded ledgers with operations including:

- `set_base_stat`
- `set_types`
- `set_abilities`
- `insert_level_move`
- `replace_level_move`
- `remove_level_move`

The application commit states that **225 species operations** were applied.

At least one removed ledger remains recoverable verbatim from history:

- `overhaul_ledgers/platinum_c3h_l4_gen3_guarded_ledger_v1.json`

A later temporary workflow reconstructed this as an exact **53-operation Gen III ledger** validated against the pinned source baseline. Because subsequent commits explicitly called some reconstruction artifacts superseded, the final source snapshot above remains the primary authority until all original L1-L5 ledgers are reconciled.

## Canonical regeneration procedure

Claude Code or another implementation agent should regenerate a clean machine-readable C3 ledger from the historical implementation, not from chat summaries:

1. Read baseline species data from `0fee7dc526f3220dc6a3b58986415446423f83de`.
2. Read final species state from `887c0d8a17104cebfab2d66b284b1ee7feae7f20`.
3. Compare only C3-owned fields:
   - `base_stats`
   - `types`
   - `abilities`
   - `learnset.by_level`
4. Convert differences into the ROM Mod Toolkit semantic operations listed above.
5. Preserve baseline file SHA-256 guards.
6. Exclude `learnset.by_tm`; compatibility is governed separately.
7. Verify that replaying the regenerated ledger from the pinned baseline reproduces the final snapshot exactly for all C3-owned fields.
8. Record operation count and species count. Investigate any difference from the historical **225-operation** application before accepting the regenerated ledger.
9. Run explicit checks for the known final-audit cases, especially Banette, Torkoal, and Seviper.
10. Commit the regenerated ledger under `docs/overhaul/implementation/` and update `RECOVERY_INDEX.md` from recovery-in-progress to recovered/verified.

## Known final-audit invariants

These are validation anchors, not a substitute for the complete regenerated ledger:

- Banette: Shadow Ball 31 retained; Cursed Stitch 38; Shadow Claw 42.
- Hitmonchan: post-evolution Mach Punch 21 and Bullet Punch 26.
- Octillery: Octazooka 26 after Lv25 evolution.
- Rampardos: Rock Slide 31 after Lv30 evolution.
- Toxicroak: Aura Burst 38 after Lv37 evolution.
- Drapion: Cross Poison 41 after Lv40 evolution.
- Omastar: Power Gem 41 after Lv40 evolution.
- Kabutops: Slash 41 after Lv40 evolution.
- Glalie: Iron Head 43 after Lv42 evolution; Frost Rush later in its finalized progression.

## Current canonical status

- C3 design: **COMPLETE / LOCKED**
- Historical C3 implementation: **FOUND**
- Historical 225-op application commit: **FOUND**
- Final post-application corrections: **FOUND**
- Clean consolidated machine-readable C3 ledger in canonical docs: **TO REGENERATE AND VERIFY**

No C3 design work should be repeated while that final regeneration is performed.
