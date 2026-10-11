# Opal B2–B8 — emulator / hardware QA sheet

**Evidence tier of everything below: `build-verified` at best. Nothing in this PR has been run in an emulator or on hardware by the
author. Every row is `NOT_RUN` until you execute it.** Record: ROM revision + SHA256, scenario ID, PASS/FAIL/NOT_TESTABLE, screenshots/video,
observed fault, source commit. Scenario IDs match `docs/visual_overhaul/B2_B8_OWNER_RUNTIME_QA.json`.

## Build the ROMs

```sh
make skrew && make configure ROM_REVISION=0 && make rom ROM_REVISION=0     # US Rev 0
make configure ROM_REVISION=1 && make rom ROM_REVISION=1                   # US Rev 1
# or download the CI artifacts pokeplatinum-us-rev{0,1}-<sha> from the `build` workflow of PR #110
```

Reduced-flash / reduced-motion builds (compile-time, see `include/constants/battle/battle_anim.h`): set `OPAL_LOW_FLASH 1` (halves every
backdrop pulse/dim, no white pulses) and/or `OPAL_REDUCED_MOTION 1` (camera cues compiled out; FX pop/shrink/drift motion disabled).

## Fast smoke test (about 10 minutes)

| # | Do | Look for |
|---|----|----------|
| 1 | Singles: use **Thunderbolt** on a wild/trainer mon, then use a different move | blue-tinted charge with sparks at you, forked bolt on the target, spark ring, yellow-white backdrop pulse, **backdrop returns to normal brightness and stays at x=0** |
| 2 | **Shadow Ball**, then **Flash Cannon** | violet wisps + converging ring, ghost orb with two afterimages, ring + wisps on impact; no violet tint on the next move |
| 3 | Doubles with all four Pokémon alive: **Surf** | water column at *your* side, foam + droplets on **each** of the three other battlers (partner included), healthboxes never move |
| 4 | **Protect** the target of an attack | blocked cue (pearl ring contracts then expands, cool glance) *only* where the text says "protected itself" |
| 5 | Burn / poison / paralyze / freeze a Pokémon | one short cue per status; none when the status is blocked (type immunity, Safeguard, ability) |
| 6 | Start any battle under rain / sun / hail / sandstorm (or use the move) | brief ripple / shimmer / fleck / dust accents, gone after ~1 s |

## Scenario matrix

| ID | Setup | Moves / action | Expected (what proves it) | Notes / how Opal differs from vanilla |
|----|-------|----------------|---------------------------|---------------------------------------|
| B2-ELECTRIC-01 | single | Thunderbolt (player + opponent as attacker) | charge → release → impact → afterglow distinct, arena tint restored | cue log: `docs/visual_overhaul/opal_b2_b8/cue_trace_baseline.json` → `thunderbolt` |
| B2-GHOST-01 | single | Shadow Ball, then any other move | gather/travel/impact/dissipate, final palette clean | two sprite managers (ghost + ring) |
| B2-SURF-01 | double | Surf with 2 mons per side | water column on attacker, foam/droplets on every resolved neighbour, no layer drop | spread targets come from the engine's NOT_ATTACKER set |
| B2-SURF-02 | partner / friendly fire | Surf where the ally is hit | same set incl. ally; no branch skips cleanup | branches L_1…L_3 rejoin at `L_4` |
| B2-FIRE-01 / B2-ICE-01 | single | Fire Blast, Ice Beam | layered flame / crystalline cues + B1 ranger bloom | vanilla emitters untouched |
| (new) B2-QUAKE-01 | single + double | Earthquake | ground rings at attacker + defender feet; native sprite/BG shake | rings only at attacker and primary defender (see report) |
| (new) B2-PSYCHIC-01 | single | Psychic | pink rings pulse at attacker, then converge/expand on target during native confusion warp | no base-BG fade layered (native BG switch owns it) |
| (new) B2-HYPER-01 | single, friendly-fire double, contest | Hyper Beam | gold rings converge with the native charge emitter, star + ring at impact; recharge turn unchanged | all three native branches |
| B6-SYNC-02 | single | Solar Beam charge turn, then release turn; then in sun | charge turn: solar rings + motes, dim; release: gold ring, light trail, star burst; **in sun only the release plays** | branch chosen by the engine, not by Opal |
| B2-BLOCK-01 | single | Protect / miss / immune / Substitute, each followed by a normal attack | no cue on miss/immune (animation never plays); blocked cue only on Protect | `subscript_missed.s` hook |
| B3-CAMERA-01 | single | Thunderbolt, Ice Beam, **Iron Tail** | backdrop eases 3–6 px and returns, punch on contact; healthboxes/mons/text fixed | `OpalCam*` cues, base BG layer only |
| B3-CAMERA-02 | double | Surf, Shadow Ball | no displacement of any battler/healthbox; contest keeps fixed backdrop | contests: camera cue is a no-op |
| B4-PALETTE-01 | weather | Thunderbolt in rain; Surf in sun | transient pulse composes with the weather grade; weather accent appears | `OpalWeatherAccent` |
| B4-PALETTE-03 | rapid sequence | Shadow Ball → Flash Cannon → Thunderbolt → Ice Beam | **no cumulative tint, fade or BG offset** after four moves | validator proves per-script; this proves the engine side |
| B5-RECOIL-01 | single | Iron Tail (heavy), Shadow Claw (light) | recoil returns to exact anchor; ring + camera punch on heavy | `OpalReact*` |
| B5-SUBSTITUTE-01 | special state | Substitute, then a physical move | no status/blocked cue on the Substitute holder (engine filter `BattleSystem_ShouldShowStatusEffect`) | vanilla behaviour, verify unchanged |
| B5-FAINT-01 | faint / switch | KO with Thunderbolt then switch in | clean faint, no palette/OAM residue | |
| B7-INTRO-01 | special encounter | Giratina (Distortion World), Dialga, Palkia, Uxie/Mesprit/Azelf; Darkrai/Shaymin/Arceus/Cresselia/Regigigas/Heatran if reachable | violet / steel-blue / pink-violet / lake-tinted arrival before the healthbox slides in; **ordinary wild battle shows nothing extra** | gate = `BATTLE_STATUS_LEGENDARY` (+ `_GIRATINA`) + enemy species |
| B7-INTRO-02 | interruption | flee, catch, faint, retry, save/reload at the threshold | cue replays once per battle start; no stuck fade/tint | |
| B8-RESOURCE-01 | stress | long doubles with weather, spread, multi-hit; repeat each canonical move 20× then change battle | no accumulating corruption; no slowdown | audit numbers: `PERFORMANCE_AUDIT.md` |
| Options | Battle Scene = Off | any move | animation skipped entirely (vanilla path); no Opal cue | `BattleSystem_AreAnimationsOn` |

## Reproducing the three special-encounter checks

1. **Giratina / Distortion World** – any save at the Giratina fight (Distortion World, Origin Forme encounter). Expect: violet backdrop fade, two converging
   halo rings, expanding halo + two motes, backdrop restored, then the usual "The Distortion World's Giratina appeared!" text and healthbox.
2. **Spear Pillar** – the Dialga/Palkia fight (`Encounter_NewVsSpeciesAtLevel(..., isLegendary=TRUE)`). Dialga: steel-blue rings, one controlled
   pulse; Palkia: pink/violet rings, one controlled pulse.
3. **Lake guardians** – Uxie (gold), Mesprit (pink), Azelf (blue): two ripples, a soft glow, one expanding ring, no stage pulse.

If a legendary does not show its cue, that encounter was started with `isLegendary = FALSE`; record it as `NOT_TESTABLE` rather than FAIL — the gate
deliberately never guesses from map IDs.

## Reproducible comparison captures for the three canonical effects (B2-06)

Run the **same** save state / move on three ROMs: vanilla-B1 head (`b85106dc`), this PR with defaults, this PR with `OPAL_LOW_FLASH 1`. With melonDS under X11
(`xdotool`, ImageMagick `import`) and `$WIN` the melonDS window id (`xdotool search --name melonDS`):

```sh
for move in thunderbolt shadow_ball surf; do      # select the move in the menu first, then press the DS A button (host key mapped to it)
  tools/visual_overhaul/b1_capture_melonds_window.sh "$WIN" "qa/$ROM_SHA/$move" z
done
```

`before.png` / `after.png` per move are the comparison pair; for mid-effect frames use melonDS's own frame advance and screenshot. The cue timelines the frames
should match are the `cue_log` entries of `thunderbolt`, `shadow_ball` and `surf` in `cue_trace_baseline.json`.

## Capture helpers already in the repo

`tools/visual_overhaul/capture_b1_battle_runtime.sh`, `b1_capture_melonds_window.sh`, `b1_melonds_preflight.sh` (melonDS window capture) and the
`b1-melonds-opal-runtime` workflow (manual dispatch). Static art preview without an emulator: `docs/visual_overhaul/opal_b2_b8/fx_sheets_preview.png`.

## Known runtime risks to look at first

1. **OBJ palette / VRAM pressure in doubles.** Each Opal sprite manager owns one OBJ palette and 51–184 tiles; scripts are capped at 2 managers and
   ≤ 400 concurrent tiles (static proof only). Look for flickering/wrong-colour sprites or missing healthbox parts in doubles + weather + spread moves.
2. **Sprite priority.** FX sprites use the engine's standard FX priority (100 / explicit 1). If a halo that should sit *behind* a legendary draws in front of it,
   that is a priority tuning item (`opal_cinematic.c`, `ManagedSprite_SetExplicitPriority`).
3. **Pan direction.** `OPAL_CAM_*_DX` signs in `asm/macros/btlanim_opal.inc` are the only values to flip if the parallax reads backwards.
4. **Burn tick.** Burn damage re-uses the burn animation every turn (vanilla did too), so the added ember also plays each turn; it lasts ≈ 14 frames. If it prolongs the
   tick noticeably, drop the `OpalImpactBurst` line in `res/battle/scripts/common_anims/burn.s`.
