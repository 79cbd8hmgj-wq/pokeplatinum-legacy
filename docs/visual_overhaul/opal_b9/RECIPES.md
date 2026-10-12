# Opal B9 P0 — per-move recipes

Common to every move: host = `res/moves/<move>/anim.s` (label `L_0`), all FX sprites are `SPRITE_FUNC_OPAL_FX` sprites resolved through
`BattleAnimUtil_GetBattlerSprites` (so only battlers the engine resolved get a cue), every sheet is opened with `OpalSheetBegin` and closed with
`OpalSheetEnd` **before** `UnloadParticleSystem` and `End` on every control-flow path (checked by `opal_cue_trace.py`), ≤ 2 sprite managers live,
no base-BG fade added except where the native script already had one (Ember, Thunder Shock, Powder Snow, Leer — their native fade is unchanged).
"Native kept" = vanilla emitters, sounds, delays and task order are unchanged unless the *Timing* column says otherwise.
Sheet short names: STRIKE = `opal_b9_strike`, EMBER = `opal_b9_ember`, NATURE = `opal_b9_nature`, WIND = `opal_b9_wind` (+`_ice`), ROCK = `opal_b9_rock`,
BUBBLE = `opal_b9_bubble`, SENSE = `opal_b9_sense`; B2 sheets `opal_water`, `opal_ice`, `opal_thunder`, `opal_fx_ring(_gold/_psychic)`, `opal_fx_wx(_gold)`; B1 `ranger_rock_burst`.

| Move | Template | Choreography (cue lifecycle) | Assets | Timing vs native | Outcome gating / branches |
|---|---|---|---|---|---|
| Tackle | physical_contact | WIND puff at user's feet → native lunge → STRIKE hit flash + `OpalReactLight` on the native shake frame → native return | WIND puff, STRIKE hit_small | +0 frames (cues async; REACT_LIGHT replaces the 2px shake on the same frame, adds one white flash) | animation runs only on a confirmed hit |
| Scratch | slash_contact | three claw arcs (A, B mirrored, A) at 0/2/4 frames over the native emitters, hit flash, `OpalReactLight` | STRIKE claw_a/claw_b/hit_small | ≤ +4 frames, and only if the native emitters are shorter than the 2 + 2 frame stagger (end is still `WaitForAllEmitters`) | as above |
| Pound | physical_contact | larger STRIKE hit flash + gold pressure ring + `OpalReactLight` + light `OpalCamPunch` | STRIKE hit_small, `opal_fx_ring_gold` | +0 | as above; camera cue is a no-op in contests |
| Quick Attack | speed_contact | launch dust + 3-copy wind streak along the native dash; streak-star at contact; native shake | WIND puff/streak, STRIKE streak | +0 (all async) | as above |
| Bite | bite | upper + lower jaw close over the native 10-frame lead-in, snap on the native shake frame with hit flash + `OpalReactLight` | STRIKE jaw_upper/jaw_lower/hit_small | +0; script now ends via `WaitForAllEmitters`+`UnloadParticleSystem` (engine `End` did the same) | as above; **QA: possible doubled jaws** |
| Ember | fire_small | 3-ember volley (3 arcs, launched at 0/2/4 frames inside the native 6-frame lead-in); native core, fades and Ranger bloom stay; cinders drift off the target | EMBER ember / ember_pop (small_ember) | +0 | as above |
| Water Gun | water_jet | 3 droplet pulses (lead + 2 afterimages each) at 0/3/6 frames, impact at native frame 10 with foam + rebound droplets; native shake | `opal_water` droplet/foam | +0 (3 + 3 + 4 = native Delay 10) | normal and friendly-fire branches get cues; **contest branch unchanged** |
| Bubble | water_bubble | 3 bubbles of different size/arc to every resolved target (0/5/10 frames) → small pops on every target + one iridescent pop on the primary at native frame 20 | BUBBLE bubble/small/pop/pop_big | +0 (5 + 5 = native Delay 10) | normal branch only; **contest branch unchanged** |
| Vine Whip | vine_lash | native lunge → thrown lash → second flick on the native shake frame (+`OpalReactLight`) → leaf debris | NATURE vine_lash / flutter | +0 | as above |
| Razor Leaf | leaf_volley | native gale; leaf fan (3 lanes + razor-blade crescents) launched at frame 40, 34-frame travel, lands on native impact frame 75; blade + `OpalReactLight`; leaf flutter | NATURE leaf_spin / razor / flutter | +0 (15 + 25 + 25 + 10 = native 15 + 50 + 10) | as above; **QA: arrival vs native leaves** |
| ThunderShock | electric_small | spark charge at the user inside the native 12-frame dim; three horizontal zig-zag arcs on the target at the native bolt frames; small spark burst + residual | `opal_thunder` sparks, EMBER spark_arc | +0 | as above; native dim/restore unchanged |
| Powder Snow | ice_snow | flecks around the user while the native gust forms → ice-tinted swirl to the target → frost glints after each native flash (14/12/12/12 split of the native 50-frame hold) | WIND swirl/flecks (`ice` palette), `opal_ice` glint | +0 | as above |
| Gust | air_gust | three wind streaks + crescent from the user (0/2/4 frames), landing swirl + leaf flutter on the native shake frame | WIND streak/crescent/swirl, NATURE flutter | +0 (2 + 2 + 1 = native Delay 5, then native Delay 15) | as above |
| Peck | pierce_contact | thrust streak during the native head tilt → 8-point pierce star + `OpalReactLight` with the emitters | WIND streak, STRIKE star | +0; **new** light recoil (native Peck had none) | as above |
| Rock Throw | rock_projectile | lobbed boulder + shard trail (20 frames) → lands on native frame 20: break, dirt, Ranger grit puff, light camera punch; native vertical shake | ROCK boulder/shards/break/dirt, `ranger_rock_burst` | +0 | as above |
| Confusion | psychic_small | two concentric psychic rings + magenta pulse on the target alongside the native warp | `opal_fx_ring_psychic` | +0 (async; native BG switch and warp untouched) | as above |
| Growl | status_sound | gold sound ring + arcs with cry 1, larger ring + arcs + roar jag with cry 2; native shakes | `opal_fx_ring_gold`, SENSE sound_arc / roar_jag | +0 (no Delay added) | played only after the Attack drop succeeded (see below); doubles: one arc per resolved foe |
| Leer | status_gaze | eye glint at the user's eyes during the native dim, larger glint on every resolved foe on the native shake frame | SENSE glint | +0 | as above (Defense drop); **contest branch unchanged** |
| Tail Whip | status_gesture | wind crescent behind the user on each of the two wags; gold star pop on every resolved foe during the 2nd wag | WIND crescent, `opal_fx_wx_gold` star_pop | +0 (loop unrolled into two identical iterations) | as above (Defense drop) |

## Outcome gating (source-verified)

* Move animations are played by `BtlCmd_PlayMoveAnimation` once the engine has decided the move executes; misses, immunities, Protect and "Battle Scene: Off"
  never reach a script (B2–B8 report, `source_map.json`). Multi-hit moves replay the script per hit.
* Growl / Leer / Tail Whip use `effect_script_0018` (+ `MOVE_SUBSCRIPT_PTR_ATTACK/DEFENSE_DOWN_1_STAGE`) → `subscript_update_stat_stage.s`:
  `ChangeStatStage` branches to its failure labels (`_041` / `_060`, no `PlayMoveAnimation`) when the stat change fails, so
  the move animation — and the Opal cues inside it — only run on a successful drop.
* Status-effect animations are suppressed on Substitute / semi-invulnerable targets by `BattleSystem_ShouldShowStatusEffect` (unchanged).
