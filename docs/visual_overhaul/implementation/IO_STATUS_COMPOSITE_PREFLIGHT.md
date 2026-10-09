# IO-STATUS — battle condition composite-overlay preflight

**Status:** design and source preflight, not implemented. Gates A, B and E resolved at source level; Gate C partially resolved (static budget known, peak usage needs the runtime measurement in the appendix); Gate D open. Manual runtime/visual acceptance deferred.
**Verified against:** `main` @ `96f63c29` (second-pass findings below; first pass was `7f5bfb98`) (source-only; no ARM toolchain or emulator was available when this was written).
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

## Verified source findings (Gates A, B, C, E)

### Gate A — battler sprite position/visibility: PASS (source-level)

- Pokémon battler sprites are **3D textured quads** (`PokemonSpriteManager`, `src/pokemon_sprite.c`, drawn via `G3_*` in `PokemonSpriteManager_DrawSprites`), **not OAM sprites**. They cost no OAM and no OBJ char/palette VRAM; the mon manager uses its own palette area (`PokemonSpriteManager_SetPlttBaseAddrAndSize(.., 0, PALETTE_SIZE_BYTES * 6)`, `battle_main.c:587`).
- Per-battler handle: `BattlerData.monSprite` / `.monSpriteBackup` (`include/struct_defs/battler_data.h`), read through `BattlerData_GetPokemonSprite()` (`battle_display.c:5836`, returns `monSprite` else `monSpriteBackup`). Battler data from `BattleSystem_GetBattlerData(battleSys, i)`; count from `BattleSystem_GetMaxBattlers`.
- Position/visibility getters: `PokemonSprite_GetAttribute` with `MON_SPRITE_X_CENTER`, `Y_CENTER`, `X_OFFSET`, `Y_OFFSET`, `HIDE`, `HIDE_2`, `SCALE_X/Y`, `ALPHA`, `DRAW_HEIGHT` (`generated/pokemon_sprite_attributes.txt`). Encounter code sets `X_CENTER`/`Y_CENTER` in screen-like pixel values (`battle_display.c:283-284`); exact unit/anchor relative to OAM space must be confirmed at runtime.
- **Lifecycle hazards (must be honoured by any overlay):**
  1. `PokemonSprite_Delete` only clears `active` (`pokemon_sprite.c:657`); the slot is pooled and reused. Return (`battle_display.c:2571`), capture-open-ball (`:2610`) and faint (`:5076`) call it **without** nulling `BattlerData.monSprite`. A cached or even re-read pointer can be dangling/aliased. Gate every read on `PokemonSprite_IsActive()` (asserts non-NULL, so check NULL first).
  2. Hide paths: `MON_SPRITE_HIDE` (vanish/substitute toggle, `Task_ToggleVanish` `:5121`; send-out `:2050,2270`), scale reaching 0 (send-out/return), `DRAW_HEIGHT` reaching 0 (faint). Overlay visible = active && !HIDE && !HIDE_2 && SCALE_X>0 && DRAW_HEIGHT>0 (and, for substitute, follow `BattlerData.isAlternateSprite`).
  3. Move animations move the sprite through the same attributes, so polling the attributes each frame covers them.
- Healthbox status icon pipeline (`HealthBox_DrawStatusIcon`) is independent of all of the above and is left untouched.

### Gate B — context access and tick/teardown boundary: PASS with constraints

- Display code already reads `BattleContext` directly: `BattleSystem_GetBattleContext(...)` + `BattleMon_Get(...)` in `battle_display.c:3449,3585,3644,3747`. Volatile bits: `BattleMon_Get(battleCtx, battler, <volatile-status field>, NULL)` against `VOLATILE_CONDITION_CONFUSION` / `VOLATILE_CONDITION_ATTRACT` (`include/constants/battle/condition.h`; both are multi-bit counters, test with `&` for non-zero). The exact `BATTLEMON_*` accessor name for volatile status still has to be confirmed in `battle_mon` code before implementation.
- Prefer a read-only poll in an overlay-owned `SysTask` rather than hooking status script commands (no new state, no gameplay mutation).
- Existing task bounds: `SysTask_DrawSprites` priority 60000 (`battle_main.c:620`) draws mon sprites, then `SpriteSystem_DrawSprites`, then OAM transfer; an overlay tick must run at a **lower priority number than 60000** (runs earlier) so its position matches that frame's draw.
- **Teardown order in `BattleMain_Free` area (`battle_main.c:~735-775`):** `BattleContext_Free` (`:748`) → `BattlerData_Delete` for each battler → `PokemonSpriteManager_Free` (`:755`) → `BattleSystem_FreeGraphics` (`:758`, frees spriteSys/spriteMan) → `SysTask_Done(taskDrawSprites)` (`:770`). An overlay manager (task + sprites) must be destroyed **before `BattleContext_Free`** (its tick reads the context) and before `BattleSystem_FreeGraphics`. `BattlerData_Delete` (`battle_io_command.c:237`) is the natural per-battler hook; the manager free needs a new call placed ahead of `:748`.
- Second free path: capture→naming screen frees graphics early (`battle_script.c:~10715-10732`: destroys healthboxes, per-battler `managedSprite`, then `BattleSystem_FreeGraphics`, then `SetRenderMode(1)`). The overlay must be destroyed there too, before `BattleSystem_FreeGraphics`.
- Link: both clients construct `BattleContext_New` (`battle_main.c:1071`) and run `BattleSystem_ExecuteBattlerCommand`; whether non-master clients hold current `battleMons` volatile state was **not** verified. Treat link as unsupported (see Gate E) until verified.

### Gate C — OAM / palette / VRAM capacity: PARTIAL (static budget only)

Static budget (`battle_main.c:131-161,563-572`):

| Resource | Capacity | Notes |
|---|---|---|
| Main OAM | 128 entries (`sOamTemplate`), 32 affine | Mon sprites use none (3D). Consumers: healthboxes, party gauges, terrain, balls/trainers, catch UI. |
| Sprite pool | `SpriteSystem_InitSprites(.., 64 + 64)` | |
| Resource capacities | char 96, pltt 32, cell 64, anim 64 (`sCapacities`) | Shared with healthboxes etc. |
| Main OBJ char VRAM | 64K 1D (`sizeMain = 0x10000` = 2048 tiles); last 16 tiles reserved for wireless icon (`sprite_util.c:180-192`) | |
| Main OBJ palettes | 16 slots; slots 14, 15 reserved (`ReserveSlotsForWirelessIconPalette`) | |

Known main-OBJ palette users: healthbox primary (RESID 20006) and effects (20007, both loaded from `healthbox_primary_NCLR`), healthbox safari (20008, Safari/Pal Park only), party gauge (`party_gauge.c:165`), terrain (`terrain.c:326-327`), transient catch/level-up resources in `battle_script.c:12023-12032` (2 + 3 palettes). Peak concurrent main-OBJ char and palette occupancy, and peak simultaneous OAM entries (healthboxes ×≤4, party gauges, ball/trainer sprites, particle/effect sprites during animations), were **not derivable from source**; per-resource tile counts live in NARC data. **No overlay allocation is justified until the measurement below is done.** Any implementation must additionally: request ≤1 palette slot and a fixed small char budget, check the allocation result, and silently skip overlay creation on failure.

### Gate E — render / battle modes: PASS (decision made)

`BattleSystem_GetRenderMode` values (`battle_system.c:1186`, `battle_main.c`, `battle_script.c`):

| Mode | Set at | Meaning | Overlay |
|---|---|---|---|
| 0 | `battle_main.c:349` (init / exit sub-menu) | normal; particles + mon + OAM drawn | allowed |
| 1 | `battle_script.c:10730` | graphics freed (catch → naming) | destroyed before; none |
| 2 | `battle_script.c:10745` | graphics freed, nothing drawn; `BattlerData_Delete` skips healthbox free | none |
| 3 | `battle_main.c:313` (`BattleSystem_EnterSubMenu`) | sub-menu: sprite system alive, mon+OAM still drawn, particles not | hide, do not free |

Decision: create/update only in mode 0 (hide in 3); never create in 1/2. Also disable for `BATTLE_TYPE_LINK` (client state parity unverified), recording/playback (`BATTLE_STATUS_RECORDING`), `BATTLE_TYPE_SAFARI | BATTLE_TYPE_PAL_PARK | BATTLE_TYPE_CATCH_TUTORIAL`. Pure no-op in those cases; no logic changes.

### Gate D — still open
No native confusion/infatuation glyph resources were located; no PMD donor pixel assets are present. A new NCGR/NCER/NANR/NCLR set (or a OAM-primitive alternative) and its NARC registration is required and cannot be validated without the build toolchain.

## Second-pass findings (Gates A, B, C, E) — source-level, on `main` @ `96f63c29`

No ARM toolchain/emulator was available; everything below is from reading source.

### Resolved since the first pass

| Item | Result | Evidence |
|---|---|---|
| Volatile-status accessor name (Gate B) | `BattleMon_Get(battleCtx, battler, BATTLEMON_VOLATILE_STATUS, NULL)` returns `battleMon->statusVolatile` (u32). Test `& VOLATILE_CONDITION_CONFUSION` (bits 0–2, counter) and `& VOLATILE_CONDITION_ATTRACT` (bits 16–19, counter) for non-zero. | `battle_lib.c:438-439`; `include/constants/battle/condition.h:32-51,65,70` |
| Mon-sprite screen anchor (Gate A) | The 3D quad is drawn with `NNS_G2dDrawSpriteFast(xCenter - MON_SPRITE_FRAME_WIDTH/2 + drawXOffset + xOffset, yCenter - MON_SPRITE_FRAME_HEIGHT/2 + drawYOffset + yOffset - shadow.height, ...)`, frame = 10×10 tiles = 80×80 px. So the visual frame centre is `(xCenter + xOffset, yCenter + yOffset - shadow.height)` in the same integer pixel space the sprite code uses. An overlay should anchor to that centre plus a per-battler-side offset. Whether this space equals main-OAM screen coordinates 1:1 is still a runtime check (appendix, step 6). | `pokemon_sprite.c:499-500,517-518`; `include/constants/graphics.h:44-47` |
| Draw skipping conditions (Gate A) | Quad is drawn only while `active && !hide && !hide2` (plus scale/draw-height effects). Matches the visibility predicate in Gate A above. | `pokemon_sprite.c:~469` (loop guard) |
| Who runs `BattleContext_Main` (Gate B/E) | `BattleMain_ExecuteBattlerCommands` calls `BattleContext_Main` on the local `battleCtx` unconditionally (guarded only by `battleInitialized`) in **both** the link and non-link branches. No host/master check exists in `battle_controller_player.c` or `battle_main.c`. This suggests every link client simulates its own context, but nothing verifies the clients stay in volatile-state lockstep. | `battle_main.c:643-675`; `battle_controller_player.c:194-209` |
| Display-side volatile reads (Gate B) | Precedent for reading `statusVolatile` from the shared context outside scripts: `battle_controller.c:309,330,347,382,389,396,430,881,894` (transform/substitute). No display code reads it today, so the overlay would be the first reader in `battle_display.c`. | as listed |

### Gate A — final: PASS (source)
Position/visibility/lifecycle API is fully identified (`BattlerData_GetPokemonSprite` → `PokemonSprite_IsActive` → `PokemonSprite_GetAttribute` for `X_CENTER`, `Y_CENTER`, `X_OFFSET`, `Y_OFFSET`, `HIDE`, `HIDE_2`, `SCALE_X`, `DRAW_HEIGHT`). Poll every frame; never cache the pointer (pooled slots are reused, see hazards above). Remaining unknown is only the pixel-space equivalence with OAM (runtime step 6).

### Gate B — final: PASS with constraints
Poll-only overlay task at priority number < 60000, destroyed before `BattleContext_Free` (`battle_main.c:748`) and in the capture→naming early-free path before `BattleSystem_FreeGraphics`. The overlay must hold no pointer to `BattleContext` across frames; re-fetch via `BattleSystem_GetBattleContext(battleSys)` each tick and bail if the manager has been marked dead.

### Gate C — final: BLOCKED on runtime measurement (no safe allocation justified)
Static facts (capacities, reserved slots) are unchanged from the first pass. Peak OAM/palette/char occupancy depends on NARC tile counts and animation-time particle sprites, which are not derivable from `.c` source. **No overlay allocation is introduced by this PR.** The measurement procedure below is the narrowest one that unlocks Gate C; an implementation must (a) request ≤1 palette slot and a fixed char budget, (b) check every allocation result, (c) silently skip creation on failure.

### Gate E — final: PASS (decision unchanged, link rationale sharpened)
Mode table and the disable list are unchanged. Link stays disabled: although each client runs its own `BattleContext_Main` (above), volatile-state parity across clients is not verifiable from source, and the overlay is purely cosmetic so the cost of disabling is zero gameplay impact.

### Remaining open items
1. Gate C runtime numbers (appendix).
2. Gate D glyph resources (out of scope here).
3. Runtime pixel-space check (appendix step 6).

## Appendix — minimal runtime measurement procedure (for Gate C)

Goal: peak main-screen OBJ usage in the worst case; no code changes required.

1. Build the ROM unmodified from the pinned commit; run in an emulator with OAM, tile (OBJ, 1D) and palette (OBJ) viewers (e.g. melonDS or DeSmuME).
2. Scenarios (record at the peak frame of each): (a) wild single; (b) trainer single; (c) trainer double with 4 healthboxes + party gauges at battle start; (d) doubles with a heavy move animation (e.g. Rain Dance/Sandstorm, Explosion, Thunder); (e) Safari/Pal Park; (f) catch sequence incl. level-up/exp box; (g) bag/party sub-menu (render mode 3) while in (c).
3. For each: count non-hidden main OAM entries; note OBJ palette slots that are non-zero (confirm 14/15 reserved); in the OBJ tile viewer note the highest used tile index and the largest contiguous free run below tile 2032.
4. Pass criterion to unlock implementation: ≥1 free OBJ palette slot **and** ≥ (glyph tiles × 2 frames × 4 battlers) contiguous free tiles **and** ≥4 free OAM entries in every scenario above. Record the numbers in this file; if any scenario fails, restrict the overlay to singles.
5. Optional repeat after a 10-turn battle and after two consecutive battles to check for resource leaks.
6. Coordinate check: in scenario (a), temporarily note (debugger/memory viewer on the `PokemonSprite` transforms) `xCenter`, `xOffset`, `yCenter`, `yOffset`, `shadow.height` for the player and enemy mon, and compare the on-screen mon centre in pixels (top screen origin) against `(xCenter+xOffset, yCenter+yOffset-shadow.height)`. Record any constant delta; repeat with a doubles battle for all four battlers.
