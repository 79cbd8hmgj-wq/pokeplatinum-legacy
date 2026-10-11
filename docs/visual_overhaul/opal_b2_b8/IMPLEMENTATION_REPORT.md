# Opal B2–B8 implementation report (PR #110)

Base: `b85106dc` (B1 head of `feat/b1-opal-cinematic-battle-foundation`). All work is additive on that branch; B1 inventory, G7 HUD, AV1 and
S2-D terrain code are untouched except where a B1 pilot script was superseded by its Opal composite (list below).

**Runtime status: nothing here has been run in an emulator or on hardware.** Static validators, host property tests and both US ROM builds are the
only verification performed; every visual claim below is a design claim until `EMULATOR_QA.md` has been executed.

## Batch status

| Batch | Status | What exists | Not done / variance |
|---|---|---|---|
| **B1 preflight** | done | `source_map.json` (23 anchors, symbols + sha256, generated and CI-checked) | — |
| **B2** primitives + composites | implemented | `OpalChargeAura / OpalProjectile / OpalImpactBurst / OpalResidual` over `SPRITE_FUNC_OPAL_FX`; 7 Emerald/procedural sheets; composites for Thunderbolt, Shadow Ball, Surf (canonical) and Fire Blast, Ice Beam, Earthquake, Psychic, Hyper Beam, SolarBeam; B2-05 applied to Draco Meteor and Shadow Force (release path only) | Emerald **background** donors (ghost/water/psychic `.bin`, `solarbeam.bin`) and `impact.png` unused — GBA tile-map backgrounds have no safe Platinum BG-layer budget; native `SwitchBg` resources + procedural rings + palette fades cover those roles (documented variance) |
| **B3** camera | implemented | `Func_OpalCamera` (PAN / PUNCH on the base backdrop only), `OpalCamFocusAttacker / OpalCamFollow / OpalCamPunch(Heavy)`; hooked into Thunderbolt, Shadow Ball, Surf, Ice Beam, SolarBeam, Iron Tail (physical exemplar), reaction macro; compile-out under `OPAL_REDUCED_MOTION`; no-op in contests | no zoom / 3D camera (no renderer support; spec allows omission); not layered on scripts that already run a native base-BG shake (Earthquake, Fire Blast impact, Hyper Beam, SolarBeam release shake, Draco Meteor) because two writers would fight over the BG offset |
| **B4** light / weather | implemented | `OpalDimIn/Out`, `OpalLightPulse` (Thunderbolt, Ice Beam, Shadow Ball, SolarBeam, Spear Pillar cue); `OpalWeatherAccent` per move; accents in the four weather-start animations; `OPAL_LOW_FLASH` | **persistent per-turn weather layer not implemented**: the engine has no per-turn weather presentation hook, only the one-shot weather-start animations; accents are bounded one-shots (never accumulate). Warm Fire Blast cue is the native effect-BG switch (single palette owner) |
| **B5** reactions / status | implemented | `OpalReactLight/Heavy/Magic` (Shadow Claw, Iron Tail, Psychic); STATUS_APPLY cues in burn/poison/paralysis/freeze common animations; REACT_BLOCKED common animation hooked into `subscript_missed.s` on `MOVE_STATUS_PROTECTED` only | sleep / confusion / infatuation keep their native cues; burn re-plays on the damage tick like vanilla; no per-move retrofit of every script — the macros are ready, adoption is incremental |
| **B6** sequencing | implemented (bounded layer) | the macro vocabulary *is* the scheduler over the existing script interpreter (`CINEMATIC_SEQUENCE` = Thunderbolt/Surf pattern, `MULTITARGET_SEQUENCE` = Surf, two-turn = SolarBeam); `opal_cue_trace.py` symbolically executes every path (cue log, ordering, ownership); baseline JSON drift gate in CI | no second interpreter, no new battle state machine (by design) |
| **B7** encounters | implemented | Giratina (Distortion World), Dialga, Palkia, Uxie, Mesprit, Azelf and a generic cue for Darkrai / Shaymin / Arceus / Cresselia / Regigigas / Heatran / non-Distortion Giratina; read-only gate in `subscript_start_encounter.s` | cannot prove which story encounters pass `isLegendary = TRUE` without running them; those that don't simply show the vanilla intro |
| **B8** cohesion / QA / docs | implemented | CI workflow, validators, host property test, evidence generators, budget tables, QA sheet, provenance, this report | no emulator/hardware measurement (see QA sheet); frame-time / VBlank DMA cost is **not measured** |

## Engine facts the design relies on (all source-verified; see `source_map.json`)

* `BtlCmd_PlayMoveAnimation` runs once per move use (`SYSCTL_PLAYED_MOVE_ANIMATION`) and is skipped entirely when the *Battle Scene* option is off ⇒ misses, immunities,
  Protect-blocked hits and "effects off" never reach a move script; spread moves play one script for all targets.
* `BattleSystem_ShouldShowStatusEffect` suppresses every status/common animation on a battler with a Substitute or in a semi-invulnerable turn (except an explicit always-shown list that contains no Opal cue).
* `BattleAnimScriptCmd_End` waits for every animation task and emitter, frees every sprite manager and particle system, restores BG priorities, resets the base and effect BG
  offsets to 0 and restores the default blend. This is the engine-side guarantee behind "no leaked transform"; Opal's own cues additionally finish by themselves and the validator proves they are all
  finished before `End`.
* `BattleAnimUtil_GetBattlerSprites` is the single battler resolver used by `Func_Shake` / `Func_FadeBattlerSprite`; Opal sprites use it, so a cue can only appear on a battler the engine resolved.
* Status animations are played from the status-application subscripts only after immunity / Safeguard / ability checks (e.g. `subscript_burn.s`); `Encounter_NewVsGiratinaOrigin` and the
  `isLegendary` parameter are what set `BATTLE_STATUS_*`.

## Files

* New C: `src/battle_anim/opal_cinematic.c`, `include/battle_anim/opal_cinematic.h`, `include/battle_anim/opal_cinematic_math.h`
* Touched C / headers: `src/battle_anim/battle_anim_system.c` (one reset call in `StartMove`), `src/battle_anim/script_func_tables.c` (+2 table entries), `src/meson.build`,
  `include/constants/battle/battle_anim.h` (constants), `generated/battle_sub_animations.txt` (names for slots 23, 24, 41–46)
* Macros: `asm/macros/btlanim_opal.inc` (new), `btlanimcmd.inc` (+1 include), `btlanimfunc.inc` (+`Func_OpalCamera`)
* Scripts rewritten as Opal composites (B1 text markers superseded; native emitters/timing retained): `thunderbolt`, `shadow_ball`, `surf`, `fire_blast`, `ice_beam`, `earthquake`, `psychic`,
  `hyper_beam`, `solar_beam`, `iron_tail`, `shadow_claw`, `draco_meteor`, `shadow_force`
* Common animations: `blocked` (was `dummy23`), `burn`, `poison`, `paralysis`, `freeze`, `weather_{rain,sun,hail,sandstorm}`, `encounter_{giratina,dialga,palkia,uxie,mesprit,azelf,legend}` (were `dummy24`, `dummy41`–`46`)
* Battle scripts (animation calls only): `subscript_missed.s`, `subscript_start_encounter.s`
* Assets: `res/graphics/battle/moves/opal_*` (7 sheets + 14 palette-only variants) and the four `anim_*.order` files, `meson.build`
* Tooling / CI / docs: `tools/visual_overhaul/opal_fx/**`, `opal_cue_trace.py`, `validate_opal_assets.py`, `build_opal_b2_b8_reports.py`, `opal_budget_report.py`, `test_opal_cinematic_math.c`,
  `.github/workflows/validate-opal-b2-b8.yml`, `docs/visual_overhaul/opal_b2_b8/**`, `docs/visual_overhaul/opal_installed_fx/**`
* Full list: `git diff --name-status b85106dc..HEAD`

## Donor provenance (details: `donor_assets_used.json`, `docs/visual_overhaul/opal_installed_fx/*.provenance.json`)

| Sheet | Source | Conversion |
|---|---|---|
| `opal_thunder` | pokeemerald `lightning_2.png`, `electricity.png`, `electric_orbs.png` | frame cuts → median-cut fold to 15 colours → DS cells |
| `opal_ghost` | pokeemerald `shadow_ball.png`, `ghostly_spirit.png` | luminance-ramp recolour to Opal violet → fold → cells |
| `opal_water` | pokeemerald `water_column.png`, `water_droplet.png`, `water_impact.png` (ramp recolour to foam) | fold → cells |
| `opal_fire` | pokeemerald `fire_plume.png`, `fire.png` | fold → cells |
| `opal_ice` | pokeemerald `ice_chunk.png`, `ice_crystals_0.png` (ramp recolour) | fold → cells |
| `opal_fx_ring`, `opal_fx_wx` | procedural (Opal) | ring / star / dot generator, 10 + 4 palette variants |
| (B1, reused) | Pokémon Ranger 2 `e009/e010/e002` | unchanged B1 installs |

Emerald's repo licence/provenance of the PNGs is recorded by path + sha256 only; confirm redistribution terms you are comfortable with before release.

## Validation performed

See the “Results” block at the bottom (filled from the actual runs).
