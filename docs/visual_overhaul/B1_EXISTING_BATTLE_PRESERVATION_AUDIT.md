# B1 — Existing battle work preservation audit

**Date:** 2026-10-10. **Status:** Historical PR/file ownership reconnaissance, **not** a line-by-line full engine or emulator audit.

## Already-merged foundations — do not redo or silently overwrite

| Upstream PR | Established work | Evidence to inspect before editing | B1 preservation requirement |
| --- | --- | --- | --- |
| #12, Pass G through G5 | Earlier battle presentation/polish foundation (among extensive visual work) | `docs/visual_overhaul/G5_BATTLE_PRESENTATION_COMPLETE.md`, `G5_DONOR_TECHNIQUE_AUDIT.md` and Pass G source/art | Trace existing impacts, palettes, shakes and battle effects before any replacement |
| #50, G7 | Command UI, move selection, player/enemy healthbox graphics, message-frame redesign | `G7_1A_BATTLE_COMMAND_MENU.md`, `G7_1B_MOVE_SELECTION.md`, `G7_2A_HEALTHBOX.md`, `G7_2B_MESSAGE_FRAMES.md`; UI generators and validators | Preserve existing tiled SUB BG ownership, OAM command cursor, healthbox text/gauge tile contract and palette semantics |
| #55–57, G7.5 | Global message-frame and indicator refinements | `G7_5_GLOBAL_WINDOWS.md`, associated resource/validation fixes | Keep message/indicator contrast and tile layout consistent with shared window system |
| #60, G7.7 | Final cohesion work and ownership ledger | `G7_7_FINAL_COHESION_REPORT.md`, `G7_7_RESOURCE_OWNERSHIP.json` | Respect resource ownership and palette conventions |
| #97, S2-D | Animated terrain/water/ice/Distortion World/cave presentation, including `src/battle/terrain.c` | S2-D implementation and validation; inspect field/battle terrain pathways separately | Avoid competing palette writes, animations or camera changes; distinguish battle terrain from overworld animation |
| #101, AV1 | Six enhanced move scripts: Ember, Fire Spin, Thunder Shock, Spark, Psybeam, Swift; command cursor and healthbox active-marker animation | `AV1_ANIMATED_BATTLE_PRESENTATION.md`, `res/moves/<move>/anim.s`, cursor/arrow NANR, generator and validator | Preserve AV1 emitter indices, sequencing, cleanup/reset behavior and player feedback |

## Confirmed technical owners

- `src/battle/battle_subscreen.c`: command/move-selection sub-screen controls, layered backgrounds and touch behavior.
- `src/battle/healthbox.c`: healthbox OAM/VRAM text and bars; corresponding `res/graphics/battle/healthbox/` assets.
- `src/battle/battle_display.c`: battle display orchestration.
- `src/battle/terrain.c`: terrain rendering path modified by S2-D.
- `src/battle_anim/`: animation helpers, system, particles, emitters and script command handlers.
- `res/moves/*/anim.s`: per-move animation sequences. The actual `.spa` authoring capability is not established.

## Risks to test before first cinematic implementation

1. Existing G5 effects vs AV1 move scripts: determine whether shared sprite fades, impact shakes, palette fades or scene resets stack safely.
2. G7 command palette banks and G7.5 text/window indicators vs new overlays: inspect BG/OBJ priorities and palette ownership, especially on SUB LCD.
3. S2-D battle terrain resources vs weather effects: inspect palette update ownership, per-frame callbacks and restoration on exit.
4. Singles/doubles and multi-target moves: compare sprite anchors, selection layout and effect sequencing.
5. Busy particle contexts: verify simultaneous existing AV1 particle systems do not exhaust allocated emitters/VRAM; performance claims need measurements.
6. No editing damage, PP, accuracy, status logic, AI, move data or species balance for a cinematic-only change.

## Unverified / pending

- Comprehensive source diff against each listed merged PR and current `main`.
- Exact per-frame effect priority/resource budget and interactive emulator verification.
- Whether AV1/G5 effects operate without visual conflicts in every battle mode.
- Full move-script command coverage and any safety limits not exposed by current static tests.

**Disposition:** B1 is safe to pursue on a separate branch, but implementation is not complete and effects must first be measured/validated against these existing systems. The list explicitly avoids calling all prior visuals "untouched" or "fully verified."
