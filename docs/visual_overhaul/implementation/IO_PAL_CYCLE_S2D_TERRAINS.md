# IO-PAL-CYCLE S2-D/S2-E — data-driven terrain palette animation

Class: `technique_donor` (PMD Sky palette-cycling idea) · donor pixels reused: **0** · no terrain art or palette asset changed.
Builds on `IO_PAL_CYCLE_PREFLIGHT.md` and `IO_PAL_CYCLE_WATER_PILOT.md` (PR #79, preserved).

**Scope decision.** S2-C (water runtime/visual verification) was skipped by the project owner. Runtime and visual QA is the owner's
responsibility and was **not performed** here (not "passed"). It is not a blocker for this change.

## Design

The water-specific task in `src/battle/terrain.c` became one task (`SysTask_CycleTerrainPalette`) driven by a four-row table,
`sTerrainCycleConfigs`. A terrain without a row stays static; a row failing `Terrain_FindCycleConfig`'s sanity checks also stays static
(the static-fallback path), as does a missing/invalid OBJ palette allocation.

Modes (colors always derived from a snapshot of the palette that was actually loaded, so day/evening/night inherit their own look):
- `RAMP`: entry *i* shows `base[clamp(i + step, 0, count-1)]` (≤ 1 rung per step, no wrap).
- `GLOW`: entry *i* shows `base[i]` brightened by `step` 5-bit units per channel (saturating).

`steps[0]` must be 0 so phase 0 is the authored platform.

## Per-terrain configuration (chosen from the real sprite index usage)

| Terrain | Resources (OBJ + BG slot 7 mirror) | Mode | Entries | Interval × phases | Steps | What moves |
|---|---|---|---|---|---|---|
| Water | `water/{day,evening,night}.pal` | RAMP | 4–7 | 16 × 4 (~1.07 s) | 0,+1,0,−1 | highlight bands (unchanged from pilot) |
| Ice | `ice/{day,evening,night}.pal` | RAMP | 9–11 | 20 × 6 (2.0 s) | 0,+1,+1,0,−1,−1 | diagonal reflective streaks / rim highlight; ≤ 1 rung/step |
| Distortion World | `distortion_world/all.pal` | GLOW | 10–11 | 10 × 8 (~1.33 s) | 0,1,2,3,2,1,0,0 | crack cores pulse, peak +3 units; never brighter than the surface |
| Cave | `cave/all.pal` | GLOW | 10 | 12 × 12 (2.4 s) | 0,0,0,0,0,0,0,1,2,1,0,0 | sparse mineral speckles on rocks (81/117 px); peak +2 units, dwell ≈ 60% of the loop |

Never touched: index 0 (transparent), black outline entries, each sprite's dominant body index, and all other entries
(e.g. ice 12 pure white rim, cave 8/9 surface, distortion 8 surface). Animated entries cover ≤ 30% of drawn pixels in both sprites
(water 27–29%, ice ≈ 20%/12%, distortion ≈ 12%, cave ≈ 2–3%). Cave and Distortion World use one palette for all times of day.

Considered and not animated: cave index 7 (33 px of scattered edge pixels, not crystal-like) and every other terrain (no
supported range was requested). No terrain required a blocker; all four requested environments are implemented.

## Resource ownership and cleanup contracts

- One OBJ palette (resource 20009) is allocated by the player-side `Terrain_Init`; the enemy side receives `0xFF` and owns nothing.
  Only the owning side creates the task, once (`paletteTask != NULL` guard); `Terrain_Init` zeroes state first.
- The task reads/writes only `[firstIdx, firstIdx+count)` of the OBJ palette and BG slot 7, only through `Terrain_WriteCycleColors`.
- Safeguards (unchanged from the pilot, now generic): idle while `renderMode != 0`; idle (phase not advanced) while a fade selects
  `PLTTBUF_MAIN_OBJ`/`MAIN_BG`; write only if the unfaded range is the expected phase or base colors and faded == unfaded;
  unfaded buffer is authoritative so later fades/restores start from valid colors; phase advances only after a successful OBJ write.
- No allocation; one SysTask per battle; work only every `interval` frames on ≤ 4 entries.
- Cleanup: `Terrain_StopPaletteCycle` ends the task and restores base colors (when no fade owns the buffers). Called from
  `Terrain_Destroy` and from the normal battle-exit path in `battle_main.c` for both terrains.

## Validation (S2-E)

`tools/visual_overhaul/io_pal_cycle/validate_terrain_cycle.py` (CI: `.github/workflows/validate-io-pal-cycle.yml`):
config validity and palette bounds; protected entries (transparent/black/dominant body); pixel coverage in both sprites;
ramp monotonicity; per-variant evaluation of every phase with the C color math (step ≤ 0.12 luminance, peak ≤ 0.12, glow ≤ 1 unit/step,
min interval 8 frames); phase 0 equals authored; glow never outshines the lightest surface colour; source contract (single task
creation, guards, fade/render-mode checks before writes, ownership check, confined writes, OBJ+BG mirror, no allocation, cleanup
on destroy and battle exit); water pilot parameters unchanged; exactly the four terrains animated; terrain assets unchanged vs
baseline `98b550a1`; and a 23-defect mutation self-test.

Command: `python3 -I tools/visual_overhaul/io_pal_cycle/validate_terrain_cycle.py`

Results and build results: see the "Results" section below.

## Known limitations / unverified

- Runtime behavior (fades, double battles, bake path, consecutive battles) and the look/subtlety of each animation are **not verified**;
  owner testing is pending. Values (indices, intervals, peaks) are first-pass and tunable in the table alone.
- Cave glints are intentionally rare and small; Distortion peak was kept below the surface tone.
- Validators are static; the phase model mirrors the C math in Python.

## Rollback

Revert this PR, or reduce to the water pilot by deleting the Ice/Distortion/Cave rows of `sTerrainCycleConfigs`
(the generic code then behaves exactly as the water pilot). No assets to restore.

## Results (authoring environment, source commit base `98b550a1`)

- `python3 -I tools/visual_overhaul/io_pal_cycle/validate_terrain_cycle.py`: pass, 4 configs, mutation self-test 23/23 rejected.
- `clang-format --dry-run --Werror src/battle/terrain.c include/battle/terrain.h`: clean.
- Existing validators: `validate_area_light_contract`, `validate_g6_showcase_integration`, `validate_g76_atmosphere`, `validate_g77_final_cohesion`,
  `validate_g7_battle_command_ui`, `validate_g7_battle_hud`, `validate_g7_core_menus`, `validate_g7_global_windows`, `validate_g7_message_frames`,
  `io_status/validate_confusion_overlay.py`: all pass (g76/g77/core_menus need full git history, not a shallow clone).
- `make rom ROM_REVISION=0`: success, sha256 `65fc08fe8251368868ddd24857ee90c8d7aca8f901178ea16a416b1b94117ed9`.
- `make rom ROM_REVISION=1` (separate build dir): success, sha256 `60428fe05a7857a6e33b4b018f40adc6fdf0cd2dfefe0cbbef60d700f33da993`.
- Emulator/runtime/visual QA: **not performed** (owner responsibility, deferred by owner decision).
