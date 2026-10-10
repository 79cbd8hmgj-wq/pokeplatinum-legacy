# B1 — Pokémon Opal cinematic battle presentation architecture

**Status: architecture and source ownership audit; not a completed battle engine.**
**Scope: visual, audio-synchronization and cinematic presentation only.** Do not change move damage, accuracy, PP, targeting, priority, abilities, status calculations, weather effects or trainer AI.

## Existing implementations we must preserve

- Merged **PR #50 / G7.1–G7.3**: battle command UI, move selection, healthbox art, message frames and related palette changes. Source contracts: `docs/visual_overhaul/G7_1A_BATTLE_COMMAND_MENU.md` and `G7_2A_HEALTHBOX.md`.
- Merged **PR #101 / AV1**: animated cursor and party markers; existing sequence enhancements to Ember, Fire Spin, Thunder Shock, Spark, Psybeam, Swift in `res/moves/*/anim.s`. Source contract: `docs/visual_overhaul/AV1_ANIMATED_BATTLE_PRESENTATION.md`.
- The native battle animation engine lives in `src/battle_anim/battle_anim_system.c`, `battle_anim_helpers.c`, `battle_particle_util.c`, `emitter_callbacks.c`, `generic_emitter_callback_camera.c`, and `script_func_tables.c`.
- Animation command scripts are `res/moves/<move>/anim.s` with `macros/btlanimcmd.inc`; battle runtime presentation lives in `src/battle/battle_display.c`, `battle_subscreen.c`, `healthbox.c`, `battle_status_overlay.c`.
- Actual healthboxes are composite OAM sprites with glyphs/gauge segments blitted into VRAM; never assume they are ordinary BG window art. The bottom command panel uses layered SUB BG tilemaps, text sprites and focus bracket OAM. Preserve coordinates and hitboxes until explicit audit.
- Existing particle archives (`.spa`) are SPL-format binaries with no established in-repo texture/emitter authoring workflow. AV1 safely reused existing emitters; an advanced particle system must verify loader/API capabilities before attempting new emitters or textures.

## Design language

Opal-specific polish, not an indiscriminate metallic skin:
- Pearl/off-white backgrounds and legible neutral text; mineral-violet interaction focus.
- Opalescent micro-highlights and sparing gold trim for meaningful information hierarchy.
- Each move type retains **its recognizable elemental colors**. Opal identity belongs in framing, timing, geometric language and finish effects, not purple recolors of fire/water/lightning.
- Effects must have readable wind-up, action, impact and decay phases; avoid indiscriminate full-screen flashes.

## Architecture proposal: sequencing without combat modifications

**B1-A — Capability and budget audit:** Enumerate all animation commands and callback implementations, particle archives, battler sprites, window/BG resources, VRAM/OBJ banks, scene fades, camera/shake and sound sequencing. Build a source-backed capability matrix. Do not claim performance headroom without measurements.

**B1-B — Reusable visual motifs:** Propose a small semantic composition vocabulary for move scripts: `anticipate`, `charge`, `launch`, `impact`, `afterglow`, `reset`. Implement through existing validated animation commands and macros where possible. Ensure no changes to game battle logic and no permanent palette/fade states.

**B1-C — Battle HUD 2.0:** Coordinated updates to healthboxes, command/move-selection panels, status symbols, HP/EXP animation cadence, focus animations and ability-trigger presentation. Implement within verified OBJ/BG bank and touch contracts. Battle info additions must display data already known to the player, without leaking hidden opponent details.

**B1-D — Elemental libraries:** Reusable per-type emitter composites and effects. Pilot one each for Fire, Water, Electric and Ghost/Psychic with detailed resource/anchor mapping, then scale to all 17 Gen IV types. Avoid clones that erase move individuality.

**B1-E — Environment and encounter cinematics:** Improved scene-layer transitions, intensity scaling, weather visual feedback, boss and legendary introductions, faint and switch transitions. These must be deterministic and never change turn timing, move effect results or AI.

**B1-F — Performance and quality:** Compare singles, doubles, multi-target, weather + status combinations, Pokémon with large sprites, first-turn/return-to-field transitions, and scripted boss encounters on both US ROM revisions. Include fallback behavior for resource conflicts and verify animation cleanup.

## Enforceable safety invariants

- For all animation-only PRs, no edits to `res/moves/*/data.json`, species balance tables, battle scripts that calculate effects, damage logic, or AI.
- No new particle emitter ID without locating it in a real `.spa` and proving callback/anchor compatibility.
- Effects must release particle resources, restore brightness/scene tint and return camera/sprite position; test cancellation and interruption.
- Avoid making battle instructions slow or inaccessible: do not hold the input panel longer for ornamentation unless intentionally user-approved.
- Preserve DS 30/60 FPS expectations as measured, not asserted; profile frames/VRAM rather than guess.
- Runtime proof is separate from build success. Do not mark the cinematic presentation complete until actual game/emulator inspection.

## First production work packet

1. Build and commit the capability matrix from sources, including move-script command catalog and existing AV1 emitter usage.
2. Implement one vertical slice (**electric impact or water charge**) with wind-up, layered impact and full reset; baseline still plays identically mechanically.
3. Integrate static checks of animation scripts and no-mechanics-change diff guards into CI.
4. Test normal/single/double target, zero-effect/immunity, faint/switch, and weather interactions; report what cannot be run.
5. Expand to coordinated HUD and elemental effects in substantial feature batches, not dozens of palette-only commits.

**Parallel-work rule:** This branch is based on `main` and must not cherry-pick, modify or merge Pokédex PR #109 or Bag PR #108.
