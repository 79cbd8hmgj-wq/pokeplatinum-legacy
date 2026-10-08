# IO-STATUS — battle condition composite-overlay preflight

**Status:** design and source preflight, not implemented. Manual runtime/visual acceptance deferred.
**Canonical opportunity:** `docs/visual_overhaul/selection/CROSS_GEN_IMPLEMENTATION_PLAN.md`, IO-STATUS (wave 2, rank 8).

## Objective / composite asset recipe

Enhance Platinum's actual battle presentation with restrained persistent layered status indicators; do not replace Pokémon sprites or the existing healthbox major-status icons.

**Donor ingredients and roles**
- PMD Sky `opp:pmd_sky/battler_status_indicators`: persistent per-battler feedback as the primary interaction/visual model.
- PMD Red `opp:pmd_red/battler_status_overlays`: conditional mask/slot/timing behavior as corroboration.
- PMD Red `opp:pmd_red/battler_status_overlays/multi_status_cycling`: optional cycling when overlap requires it, *not* mandatory.
- Platinum existing battle/status animation resources: preferred compositing inputs where exact reusable elements are identified. Favor native particle/glow/symbol treatment, palette-matched and redrawn where required. **Never claim donor pixels were imported unless extracted assets and provenance are explicitly supplied.**
- Composite recipe per condition: small recognizable central symbol + subtle two-frame breathing/pulse + optional native accent particles; stagger motion and opacity rather than stacking unrelated full-size donor sprites.
- The first pilot is **confusion** and **infatuation** on single-battle battlers; design hook must allow double-battle safe positioning. Add taunt/stat-drop/etc. only after working state/teardown and headroom measured. Exclude transient flinch and unrelated gameplay changes.

## Source findings verified on main

1. `src/battle/healthbox.c` `HealthBox_DrawStatusIcon` draws existing *major* statuses (sleep, poison, burn, freeze, paralysis) through healthbox VRAM; **do not edit or duplicate that pipeline**.
2. `src/battle/battle_lib.c` contains `battleCtx->battleMons[battler].statusVolatile`, `VOLATILE_CONDITION_CONFUSION`, `VOLATILE_CONDITION_ATTRACT`; volatile state is reset on switch/faint paths (around code sections at lines 2055–2180, exact positions may move). Do not invent status from move animation events.
3. `src/battle/battle_system.c` exposes `BattleSystem_GetBattleContext`, `GetBattlerData`, `GetMaxBattlers`, `GetPokemonSpriteManager`, `GetSpriteManager`, `GetBattlerType`, `GetBattlerSide`, `GetPokemonSpriteDataByIndex`, and `GetRenderMode` (see `include/battle/battle_system.h`).
4. `src/battle/battle_display.c` already has SysTasks for encounter/show/return/faint/animation and existing Pokémon/healthbox render handling; adding an overlay *without* binding to sprite visible/position/switch/faint lifecycle is unsafe.
5. `src/battle/healthbox.c` uses `SpriteSystem_NewSprite`, `ManagedSprite_SetPositionXY`, `SysTask_Start` / `SysTask_Done`. Reuse relevant sprite-management patterns where appropriate.
6. Do **not** assume `src/battle/battle_anim.c` exists (not found in repository). The ranking notes `src/battle_anim/script_funcs_status.c`, which must be verified before code is written.

## Pre-implementation gate (must be answered before coding)

A. Identify the **exact** active battler Pokémon sprite coordinate/visibility API and lifecycle point, including doubles, vanish/substitute, send-out/switch, faint and animation movement. Prefer attaching to a battler position getter each frame, not hardcoded absolute coordinates.
B. Identify the **authoritative battle-context** access path and safe tick boundary (battle system vs UI/command state) so status updates cannot read released context, and later removal cannot leave tasks on freed sprites.
C. Measure OAM sprite count, palette slots, and VRAM free capacity for 1–4 battlers; choose an alloc strategy with a safe no-op fallback on exhaustion. This is a previously identified evidence gap: `defer:platinum/battle_overlay_oam_palette_headroom`. **Do not create overlays before resolving it.**
D. Find existing native animated symbols, palettes, and mapping or locate the exact PMD donor components in the catalog; record precise provenance. If missing, draw minimal new Platinum-native glyphs and be explicit about source.
E. Determine whether link/recording/special-render modes can safely receive the overlay. If not, disable this purely visual enhancement in those contexts; no battle-logic modification.

If any gate requires broad architecture work, stop with a concise blocker report rather than running an extensive Claude exploration.

## Intended pilot behavior

- On battle UI setup: initialize one overlay manager with zero or a bounded number of sprite objects.
- Each visible battler: read current volatile status, determine glyph, and follow its Pokémon sprite when it moves; hide during capture, recall, vanish, faint and battles in unsupported render modes.
- Confusion and infatuation: recognizable distinct symbols/palette and slow pulse; visible while condition is active, disappears promptly when cleared.
- Multiple simultaneous statuses: priority/short cycle, never uncontrolled stacks; do not obscure Pokémon face or healthbox in doubles.
- Destroy manager/tasks/resources **before** sprite manager/battle system teardown, even with early exits and alternate battle modes; no stale VBlank transfers.
- Do not alter status logic, move effects, AI, combat RNG, save state, damage or status-duration counters.
- Do not rework healthboxes, battle animation scripts, or terrain palette cycling as part of the pilot.

## Claude read budget and deliverable

Read this file, then only: `src/battle/battle_system.c`, `src/battle/battle_main.c`, `src/battle/battle_display.c`, `src/battle/healthbox.c`, `src/battle/battle_lib.c`, relevant headers and exact sprite helpers uncovered through targeted search. Consult donor documents only for **exact named provenance**, not rediscovery.

Before implementation, produce a brief technical gate table (A–E) with concrete symbols, allocations and rationale. If all pass: implement minimal confusion/infatuation composite pilot, reproducible glyph assets, source-level checks, and a focused PR. If one fails: document exact blocker and stop. No general repo-wide audit.

## Review / acceptance

- Source/build/format checks pass. `g7-visual-validation` known historical baseline failure must be assessed separately, never automatically attributed to the pilot.
- Static audit confirms lifecycle, no gameplay mutation, no OAM/palette allocation collision, and fallbacks.
- Manual QA pending: singles & doubles, switch/faint, substitute/vanish, confusion ending, infatuation ending, repeat battles, animation movement, alternate battle types, performance/clutter at DS native resolution.
- Visual goal: unmistakably better and richer Platinum feedback—not a wall of persistent UI icons.
