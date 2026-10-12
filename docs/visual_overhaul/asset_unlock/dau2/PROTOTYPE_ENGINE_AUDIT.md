# Pokémon Opal B9 — prototype engine audit (initial source-backed pass)

Branch based on DAU2 PR #113 head `8abed71b`. This is a **gate document**, not an animation implementation or runtime approval. Preserve PR #113; do not merge this branch automatically.

## Direct script findings (source: `res/moves/*/anim.s`)

| Prototype | Actual script behavior | Implementation constraint | Status |
|---|---|---|---|
| Spark | Loads both `spark_spa` in particle slot 0 and `discharge_spa` in slot 1; creates both attacker and defender emitters; fades BG in loops and later at impact; unloads both slots | Do not add another assumed particle slot, stack another BG fade over existing fades or claim the native move is only `discharge.spa` | SOURCE AUDITED |
| Metal Claw | Creates/removes Pokémon sprite copies; frees Pokémon sprite manager; *then* initializes `InitSpriteManager 0` and loads native `claw` CHAR/PLTT/CELL/ANIM; loops battler motion twice | Add Opal effects only in a proven safe manager window, or sequentially after the native manager closes. Do not overlap another manager using ID 0 or double the claw graphics without review | SOURCE AUDITED |
| Hypnosis | Loads `hypnosis_spa`, creates emitters 0–4 with timed `Delay 30`, already fades the defender purple | Preserve five-emitter behavior and its hit timing; avoid overlapping an additional battler fade with the existing fade; recolored PMD spiral is still an unlicensed/unverified donor | SOURCE AUDITED |
| Swords Dance | Native `swords_dance_spa`, emitters 1 and 0 at the attacker, waits for emitters then unloads | Baked orbit must be tested against the native particle visuals; no runtime proof that four added sprites fit or appear correctly | SOURCE AUDITED |
| Double Team | Explicitly adds four attacker Pokémon sprite copies plus partner copy, runs `Func_DoubleTeam` and `Func_BlinkAttacker`, waits, removes sprites and frees manager | Existing copies are the silhouettes. Tinting the copies is unproven; do not invoke `Func_FadeBattlerSprite` on copy handles without confirming accepted roles and fallback behavior | SOURCE AUDITED |

## Gate rules for code changes

1. Preserve native emitters, sounds, timing gates, cleanup and original gameplay behavior.
2. Before changing a script, inspect all currently live sprite manager IDs, particle resource slots and fade writers. Maintain lifecycle on every exit path.
3. Favor zero-new-donor-art proof of choreography first. No newly decoded donor art is approved for public redistribution; avoid committing donor-derived sheets pending rights review.
4. Do not substitute a claimed 400-OBJ-tile / 40-OAM policy cap for empirical measurements. Both DS hardware resources and battle-specific actual allocations matter.
5. Prototype **Spark and Metal Claw first** as resource-collision cases, then Hypnosis, Swords Dance and Double Team.
6. Enforce unchanged impact and turn cadence where possible; record any divergence. Confirm contest/singles/doubles behavior.
7. Validate both ROM revisions, source gates, low-flash and reduced-motion variants. Do not mark emulator QA passed unless an emulator was actually run.
8. Before claiming implementation, link changed source files and the test results in this branch/PR.

## Known blockers

- No emulator/hardware capture available in this audit.
- No runtime measurement of actual OAM/OBJ/palette/particle pressure.
- Double Team copy-tint semantics unresolved.
- Native particle/fade overlap and Opal manager allocation must be inspected for any new cue.
- Donor redistribution clearance pending.

Next deliverable: a minimal non-donor prototype implementing one safe move enhancement, with compile-tested assembly and explicit cleanup; then expand only after validation.
