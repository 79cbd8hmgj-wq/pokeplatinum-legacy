# DAU2 - P1/P2 animation recipes (PROVISIONAL until runtime verified)

Per move: native baseline, one primary and up to two alternatives. Parts show role, timing (anchor `L` = script start, `H` = native hit beat; frames at 60 fps), source and the Opal macro. See `DESIGN_SHORTLIST.md` for the one-page view. Provisional: not built, not run, not approved.

## Headbutt (P1, `heavy_contact`) - shoulder/head impact

Native: `headbutt` emitters [0, 1], lower-bound duration 21f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/headbutt/anim.s`.

### PRIMARY: Skull-first slam (native+opal) - PROVISIONAL

Keep the native burst/star masks; add a ground puff on the lunge, a Ranger 2 ring-burst plus Emerald starburst on the hit, a gold ring and heavy recoil, then dizzy stars.

*Why:* Heavy-contact template (weight transfer, compressed impact burst, recovery); the hit beat stays on the native frame so cadence is unchanged.

* keep native emitters [0, 1] (native burst + star masks at the hit)
* launch @ L+0 (+8f): installed `opal_b9_wind` / `puff` x1 - OpalFx ... OPAL_B9_WIND_SEQ_PUFF (feet) - dust under the attacker as it winds up
* impact @ H+0 (+12f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `ef014_LZ.bin#2` (44t); Pokemon Emerald `impact.png` (16t) x1 - OpalImpactBurst x2 (ring-burst, starburst 130%) - Ranger 2 ef014 ring + fireball burst; Emerald impact.png starburst
* impact @ H+0 (+12f): installed `opal_fx_ring` [gold] / `ring_expand` x1 - OpalReactHeavy (ring + heavy shake + camera punch)
* aftermath @ H+2 (+20f): NEW donor cell(s) Pokemon Emerald `gold_stars.png` (8t) x1 - OpalResidual (drifting stars over the defender) - Emerald gold_stars.png

*Compatibility:* macros OpalFx, OpalImpactBurst, OpalReactHeavy, OpalResidual; installed sheets opal_b9_wind, opal_fx_ring; new sheet `opal_b9p_headbutt` (68 tiles, <= 14 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +68 new OBJ tiles; peak 252t / 2 mgr / 6 OAM; ~17 GX quads, 3072 B tex; ~30f (+9 vs native lb).

### ALTERNATIVE 1: Light thud (opal_existing) - PROVISIONAL

Zero new art: existing strike flash + gold ring + light recoil.

*Why:* Cheapest and closest to the P0 contact language.

* keep native emitters [0, 1]
* launch @ L+0 (+8f): installed `opal_b9_wind` / `puff` x1 - OpalFx puff
* impact @ H+0 (+10f): installed `opal_b9_strike` / `hit_small` x1 - OpalImpactBurst
* impact @ H+0 (+12f): installed `opal_fx_ring` [gold] / `ring_expand` x1 - OpalImpactBurst
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalFx, OpalImpactBurst, OpalReactLight; installed sheets opal_b9_strike, opal_b9_wind, opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 368t / 2 mgr / 8 OAM; ~17 GX quads, 3072 B tex; ~21f (+0 vs native lb).

### ALTERNATIVE 2: Ranger ring-burst (native+donor) - PROVISIONAL

A bigger, explosive hit from a Ranger 2 ring + fireball cell and sparkle aftermath.

*Why:* Bolder silhouette for a signature Headbutt; larger tile cost.

* keep native emitters [0, 1]
* impact @ H+0 (+14f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `ef014_LZ.bin#2` (44t) x1 - OpalImpactBurst scale 120
* aftermath @ H+4 (+22f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e011_LZ.bin#4` (80t) x1 - OpalResidual
* cue @ H+0: OpalCamPunchHeavy

*Compatibility:* macros OpalCamPunchHeavy, OpalImpactBurst, OpalResidual; installed sheets none; new sheet `opal_b9p_headbutt` (124 tiles, <= 12 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +124 new OBJ tiles; peak 124t / 1 mgr / 2 OAM; ~17 GX quads, 3072 B tex; ~34f (+13 vs native lb). Notes: cadence unverifiable: the native lower bound is only 21 frames (task durations unknown), so +13 cannot be judged without a runtime measurement

## Slam (P1, `heavy_contact`) - heavier contact

Native: `slam` emitters [0, 1], lower-bound duration 18f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/slam/anim.s`.

### PRIMARY: Shockwave drop (native+opal) - PROVISIONAL

Native radial/spike masks, a red-yellow directional strike plus starburst on the hit, rock-sheet break and dirt at the feet, heavy camera punch.

*Why:* Heavier-than-Headbutt: ground debris and a heavy camera punch sell the weight; all cues hang off the native hit frame.

* keep native emitters [0, 1]
* impact @ H+0 (+10f): NEW donor cell(s) Pokemon Emerald `horn_hit.png` (16t); Pokemon Emerald `impact.png` (16t) x1 - OpalImpactBurst x2 - Emerald horn_hit.png (down-strike) + impact.png
* aftermath @ H+2 (+13f): installed `opal_b9_rock` / `break` x2 - OpalImpactBurst (ground)
* aftermath @ H+4 (+10f): installed `opal_b9_rock` / `dirt` x3 - OpalResidual
* cue @ H+0: OpalCamPunchHeavy
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalCamPunchHeavy, OpalImpactBurst, OpalReactLight, OpalResidual; installed sheets opal_b9_rock; new sheet `opal_b9p_slam` (32 tiles, <= 9 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +32 new OBJ tiles; peak 116t / 2 mgr / 21 OAM; ~21 GX quads, 1280 B tex; ~23f (+5 vs native lb).

### ALTERNATIVE 1: Existing-only slam (opal_existing) - PROVISIONAL

Strike flash + earth ring, no new art.

*Why:* Zero-tile fallback.

* keep native emitters [0, 1]
* impact @ H+0 (+10f): installed `opal_b9_strike` / `hit_small` x2 - OpalImpactBurst
* impact @ H+2 (+14f): installed `opal_fx_ring` [earth] / `flat_expand` x1 - OpalReactHeavy

*Compatibility:* macros OpalImpactBurst, OpalReactHeavy; installed sheets opal_b9_strike, opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 368t / 2 mgr / 12 OAM; ~21 GX quads, 1280 B tex; ~24f (+6 vs native lb).

### ALTERNATIVE 2: Debris slam (native+opal) - PROVISIONAL

Rock-sheet shards and dust around the hit.

*Why:* Reuses the P0 rock vocabulary.

* keep native emitters [0, 1]
* impact @ H+0 (+15f): installed `opal_b9_rock` / `shards` x1 - OpalImpactBurst
* aftermath @ H+4 (+12f): installed `opal_b9_rock` / `dirt` x2 - OpalResidual
* cue @ H+0: OpalCamPunchHeavy

*Compatibility:* macros OpalCamPunchHeavy, OpalImpactBurst, OpalResidual; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 12 OAM; ~21 GX quads, 1280 B tex; ~24f (+6 vs native lb).

## Wing Attack (P1, `wing_strike`) - wing arcs and pressure

Native: `wing_attack` emitters [0, 1], lower-bound duration 40f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/wing_attack/anim.s`.

### PRIMARY: Crescent sweep (native+opal) - PROVISIONAL

Native feather masks; installed wind crescents sweep to the target alongside white feather / air-slash trails from Emerald art, with a light recoil on the hit.

*Why:* Wing-strike template: wing arcs, displaced air, then impact; the crescents reuse the installed wind sheet so the sweep matches Gust/Quick Attack, the feathers add the wing identity.

* keep native emitters [0, 1]
* travel @ L+2 (+24f): installed `opal_b9_wind` / `crescent` x2 - OpalProjectile (trail, arc 6)
* travel @ L+6 (+16f): NEW donor cell(s) Pokemon Emerald `white_feather.png` (16t); Pokemon Emerald `air_slash.png` (9t) x2 - OpalProjectile (trail, arc 6) - Emerald white_feather.png + air_slash.png
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalProjectile, OpalReactLight; installed sheets opal_b9_wind; new sheet `opal_b9p_wing_attack` (25 tiles, <= 14 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +25 new OBJ tiles; peak 103t / 2 mgr / 12 OAM; ~12 GX quads, 1280 B tex; ~40f (+0 vs native lb).

### ALTERNATIVE 1: Existing wind (opal_existing) - PROVISIONAL

Wind crescent + streaks and a hit flash from installed sheets.

*Why:* Zero new tiles.

* keep native emitters [0, 1]
* travel @ L+4 (+20f): installed `opal_b9_wind` / `crescent` x2 - OpalProjectile
* impact @ H+0 (+10f): installed `opal_b9_strike` / `hit_small` x1 - OpalImpactBurst
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactLight; installed sheets opal_b9_strike, opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 262t / 2 mgr / 12 OAM; ~12 GX quads, 1280 B tex; ~40f (+0 vs native lb).

### ALTERNATIVE 2: Cyan blade wings (native+donor) - PROVISIONAL

Ranger 2 cyan blade streak for a harder, brighter wing slice.

*Why:* More aggressive look.

* keep native emitters [0, 1]
* travel @ L+6 (+14f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `ef010_LZ.bin#2` (41t) x2 - OpalProjectile
* borrow @ H+0 (+17f): borrow Platinum `slash.spa` emitters [0, 1, 2] - slash flash masks (peak 32 quads, 1024 B tex)
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalProjectile, OpalReactLight; installed sheets none; new sheet `opal_b9p_wing_attack` (41 tiles, <= 7 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +41 new OBJ tiles; peak 41t / 1 mgr / 2 OAM; ~44 GX quads, 2304 B tex; ~40f (+0 vs native lb).

## Aerial Ace (P1, `speed_contact`) - fast double-cut

Native: `aerial_ace` emitters [0, 1, 2, 3], lower-bound duration 55f, hit beat H = 15 (budget 15); existing sprite resources: none. Script: `res/moves/aerial_ace/anim.s`.

### PRIMARY: Double cut (native+opal) - PROVISIONAL

Native four-emitter cut at frame 15; add dash lines and a cyan blade streak ahead of it and a mirrored double claw-cut flash on the hit.

*Why:* Speed-contact template (afterimage, short dash, impact); the second cut lands 3 frames after the first for the 'double' read.

* keep native emitters [0, 1, 2, 3]
* travel @ L+0 (+15f): NEW donor cell(s) Pokemon Emerald `blue_lines.png` (2t); Pokemon Ranger: Shadows of Almia `ef010_LZ.bin#2` (41t) x2 - OpalProjectile (trail) - Emerald blue_lines.png + Ranger 2 ef010 cyan blade streak
* impact @ H+0 (+10f): installed `opal_b9_strike` / `claw_a` x1 - OpalImpactBurst
* impact @ H+3 (+10f): installed `opal_b9_strike` / `claw_b` x1 - OpalImpactBurst
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactLight; installed sheets opal_b9_strike; new sheet `opal_b9p_aerial_ace` (43 tiles, <= 9 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +43 new OBJ tiles; peak 184t / 1 mgr / 8 OAM; ~52 GX quads, 1536 B tex; ~55f (+0 vs native lb).

### ALTERNATIVE 1: Existing wind cut (opal_existing) - PROVISIONAL

Wind streak lead-in + strike claw cuts.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2, 3]
* travel @ L+0 (+15f): installed `opal_b9_wind` / `streak` x2 - OpalProjectile
* impact @ H+0 (+10f): installed `opal_b9_strike` / `claw_a` x1 - OpalImpactBurst
* impact @ H+3 (+10f): installed `opal_b9_strike` / `claw_b` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst, OpalProjectile; installed sheets opal_b9_strike, opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 8 OAM; ~52 GX quads, 1536 B tex; ~55f (+0 vs native lb).

### ALTERNATIVE 2: PMD streak cuts (native+donor) - PROVISIONAL

PMD Sky white cut lines for crisp speed slashes.

*Why:* Crisp, graphic read; large PMD tile cost (needs splitting).

* keep native emitters [0, 1, 2, 3]
* impact @ H+0 (+12f): NEW donor cell(s) Pokemon Mystery Dungeon: Explorers of Sky `effect.bin#244` (109t); Pokemon Emerald `air_slash.png` (9t) x2 - OpalImpactBurst
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalReactLight; installed sheets none; new sheet `opal_b9p_aerial_ace` (118 tiles, <= 12 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +118 new OBJ tiles; peak 118t / 1 mgr / 4 OAM; ~52 GX quads, 1536 B tex; ~55f (+0 vs native lb).

## Spark (P1, `electric_contact`) - charging aura into impact

Native: `discharge` emitters [0, 1, 2, 3], lower-bound duration 65f, hit beat H = 5 (budget 8); existing sprite resources: none. Script: `res/moves/spark/anim.s`.

### PRIMARY: Charge-and-jump (native+opal) - PROVISIONAL

Native discharge emitters; thunder-orb charge aura on the user, orange zig-zag arcs travelling to the target, spark burst, yellow light pulse.

*Why:* Electric-contact template: charging aura into impact; reuses the B2 thunder sheet so the look matches Thunder Shock/Thunderbolt.

* keep native emitters [0, 1, 2, 3]
* launch @ L+0 (+12f): installed `opal_thunder` / `orb` x1 - OpalChargeAura
* travel @ L+8 (+12f): NEW donor cell(s) Pokemon Emerald `spark_1.png` (16t) x2 - OpalProjectile (trail) - Emerald spark_1.png
* impact @ H+0 (+12f): installed `opal_thunder` / `sparks` x1 - OpalImpactBurst
* cue @ H+0: OpalLightPulse yellow
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalChargeAura, OpalImpactBurst, OpalLightPulse, OpalProjectile, OpalReactLight; installed sheets opal_thunder; new sheet `opal_b9p_spark` (16 tiles, <= 1 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +16 new OBJ tiles; peak 123t / 2 mgr / 12 OAM; ~43 GX quads, 3328 B tex; ~65f (+0 vs native lb).

### ALTERNATIVE 1: Existing thunder (opal_existing) - PROVISIONAL

Installed thunder sheet only.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2, 3]
* launch @ L+0 (+12f): installed `opal_thunder` / `orb` x1 - OpalChargeAura
* impact @ H+0 (+13f): installed `opal_thunder` / `bolt` x1 - OpalImpactBurst

*Compatibility:* macros OpalChargeAura, OpalImpactBurst; installed sheets opal_thunder; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 107t / 1 mgr / 8 OAM; ~43 GX quads, 3328 B tex; ~65f (+0 vs native lb).

### ALTERNATIVE 2: Sparkle crackle (native+donor) - PROVISIONAL

Ranger 2 yellow sparkles as residual crackle.

*Why:* Adds residual sparkle.

* keep native emitters [0, 1, 2, 3]
* launch @ L+0 (+12f): installed `opal_thunder` / `orb` x1 - OpalChargeAura
* aftermath @ H+2 (+20f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e011_LZ.bin#4` (80t) x1 - OpalResidual

*Compatibility:* macros OpalChargeAura, OpalResidual; installed sheets opal_thunder; new sheet `opal_b9p_spark` (80 tiles, <= 4 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +80 new OBJ tiles; peak 187t / 2 mgr / 5 OAM; ~43 GX quads, 3328 B tex; ~65f (+0 vs native lb).

## Flame Wheel (P1, `fire_contact`) - flaming roll

Native: `flame_wheel` emitters [0, 1, 2], lower-bound duration 65f, hit beat H = 20 (budget 20); existing sprite resources: ['ranger_fire_bloom_NCGR_lz']. Script: `res/moves/flame_wheel/anim.s`.

### PRIMARY: Rolling fire ring (native+opal) - PROVISIONAL

Keep native emitters and the already-installed Ranger fire-bloom sprite; add an ember trail along the dash, an Opal flame tongue on the hit and an orange light pulse.

*Why:* Fire-contact template (fire orbit, forward roll, cinders). The native script already carries a Ranger 2 donor sprite, so this stays within a known-good donor mix.

* keep native emitters [0, 1, 2] (native wheel + bloom)
* travel @ H-16 (+16f): installed `opal_b9_ember` / `ember` x3 - OpalProjectile (trail) - ember trail along the native 24-px dash
* impact @ H+0 (+11f): installed `opal_fire` / `tongue` x1 - OpalImpactBurst
* cue @ H+0: OpalLightPulse orange
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalLightPulse, OpalProjectile, OpalReactLight; installed sheets opal_b9_ember, opal_fire; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 148t / 1 mgr / 12 OAM; ~44 GX quads, 1024 B tex; ~65f (+0 vs native lb).

### ALTERNATIVE 1: Ember only (opal_existing) - PROVISIONAL

Ember trail + pop only.

*Why:* Cheapest.

* keep native emitters [0, 1, 2]
* travel @ H-16 (+16f): installed `opal_b9_ember` / `ember` x3 - OpalProjectile
* impact @ H+0 (+8f): installed `opal_b9_ember` / `ember_pop` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst, OpalProjectile; installed sheets opal_b9_ember; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 56t / 1 mgr / 12 OAM; ~44 GX quads, 1024 B tex; ~65f (+0 vs native lb).

### ALTERNATIVE 2: Spiral flame ring (native+donor) - PROVISIONAL

A recoloured PMD spiral disc rotating around the user as a 'wheel', plus ember trail.

*Why:* Gives the 'wheel' an explicit rotating shape.

* keep native emitters [0, 1, 2]
* launch @ L+0 (+24f): NEW donor cell(s) Pokemon Mystery Dungeon: Explorers of Sky `effect.bin#128` (32t) x1 - OpalChargeAura (spiral, scale growth) - PMD effect.bin#128 recoloured to the fire ramp
* travel @ H-16 (+16f): installed `opal_b9_ember` / `ember` x3 - OpalProjectile

*Compatibility:* macros OpalChargeAura, OpalProjectile; installed sheets opal_b9_ember; new sheet `opal_b9p_flame_wheel` (32 tiles, <= 7 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +32 new OBJ tiles; peak 88t / 2 mgr / 13 OAM; ~44 GX quads, 1024 B tex; ~65f (+0 vs native lb).

## Aqua Jet (P1, `water_contact`) - water-wrapped dash

Native: `aqua_jet` emitters [0, 1, 2, 3, 4, 5], lower-bound duration 49f, hit beat H = 10 (budget 10); existing sprite resources: none. Script: `res/moves/aqua_jet/anim.s`.

### PRIMARY: Water-wrapped dash (native+opal) - PROVISIONAL

Native emitters; a water column wraps the dash, a Ranger 2 spray fan and Opal foam burst on the hit, droplets after.

*Why:* Water-contact template (water cocoon, charge, splash). Reuses the B2 water sheet; the new spray fan adds a directional splash.

* keep native emitters [0, 1, 2, 3, 4, 5] (native aqua jet emitters)
* travel @ L+0 (+16f): installed `opal_water` / `column` x1 - OpalProjectile (trail)
* impact @ H+0 (+12f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e052_LZ.bin#12` (96t) x1 - OpalImpactBurst - Ranger 2 e052 blue-white spray fan
* impact @ H+0 (+6f): installed `opal_water` / `foam` x1 - OpalImpactBurst
* aftermath @ H+3 (+24f): installed `opal_water` / `droplet` x3 - OpalResidual
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactLight, OpalResidual; installed sheets opal_water; new sheet `opal_b9p_aqua_jet` (96 tiles, <= 5 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +96 new OBJ tiles; peak 186t / 2 mgr / 21 OAM; ~81 GX quads, 3584 B tex; ~49f (+0 vs native lb).

### ALTERNATIVE 1: Existing water (opal_existing) - PROVISIONAL

Column + foam + droplets.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2, 3, 4, 5]
* travel @ L+0 (+16f): installed `opal_water` / `column` x1 - OpalProjectile
* impact @ H+0 (+6f): installed `opal_water` / `foam` x1 - OpalImpactBurst
* aftermath @ H+3 (+24f): installed `opal_water` / `droplet` x3 - OpalResidual

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalResidual; installed sheets opal_water; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 90t / 1 mgr / 20 OAM; ~81 GX quads, 3584 B tex; ~49f (+0 vs native lb).

### ALTERNATIVE 2: Pulse bubble (native+opal) - PROVISIONAL

Borrowed Water Pulse sphere/droplet emitters with Opal foam.

*Why:* Glossier water.

* keep native emitters [0, 1, 2, 3, 4, 5]
* borrow @ H+0 (+33f): borrow Platinum `water_pulse.spa` emitters [0, 1, 2] - glossy bubble sphere + droplets (peak 13 quads, 3072 B tex)
* impact @ H+0 (+6f): installed `opal_water` / `foam` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_water; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 90t / 1 mgr / 4 OAM; ~94 GX quads, 6656 B tex; ~49f (+0 vs native lb).

## BubbleBeam (P1, `water_bubble`) - dense bubbles and burst

Native: `bubble_beam` emitters [0], lower-bound duration 111f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/bubble_beam/anim.s`.

### PRIMARY: Dense bubble stream (native+opal) - PROVISIONAL

Native stream; three staggered bubble lanes of two sizes, a ripple ring and pop burst on arrival.

*Why:* Water-bubble template (slow varied bubbles, collision, pop and ripples).

* keep native emitters [0]
* travel @ L+0 (+40f): installed `opal_b9_bubble` / `bubble` x3 - OpalProjectile (lanes at 0/6/12)
* travel @ L+3 (+40f): installed `opal_b9_bubble` / `bubble_small` x3 - OpalProjectile
* impact @ H+0 (+15f): NEW donor cell(s) Pokemon Mystery Dungeon: Explorers of Sky `effect.bin#183` (30t) x1 - OpalImpactBurst - PMD effect.bin#183 ring + dots as ripples
* impact @ H+0 (+13f): installed `opal_b9_bubble` / `pop_big` x1 - OpalImpactBurst
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactLight; installed sheets opal_b9_bubble; new sheet `opal_b9p_bubble_beam` (30 tiles, <= 6 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +30 new OBJ tiles; peak 128t / 2 mgr / 29 OAM; ~13 GX quads, 8192 B tex; ~111f (+0 vs native lb).

### ALTERNATIVE 1: Bubble sheet only (opal_existing) - PROVISIONAL

P0 bubble sheet at higher density.

*Why:* Zero new tiles.

* keep native emitters [0]
* travel @ L+0 (+40f): installed `opal_b9_bubble` / `bubble` x4 - OpalProjectile
* impact @ H+0 (+12f): installed `opal_b9_bubble` / `pop` x3 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst, OpalProjectile; installed sheets opal_b9_bubble; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 98t / 1 mgr / 28 OAM; ~13 GX quads, 8192 B tex; ~111f (+0 vs native lb).

### ALTERNATIVE 2: Glossy bubbles (native+opal) - PROVISIONAL

Borrowed Bubble emitters (glossy sphere) plus foam.

*Why:* Native-look bubbles.

* keep native emitters [0]
* borrow @ L+0 (+51f): borrow Platinum `bubble.spa` emitters [0, 1] - glossy bubble spheres (peak 15 quads, 4096 B tex)
* impact @ H+0 (+6f): installed `opal_water` / `foam` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_water; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 90t / 1 mgr / 4 OAM; ~28 GX quads, 12288 B tex; ~111f (+0 vs native lb).

## Magical Leaf (P1, `leaf_homing`) - curved leafy projectiles

Native: `magical_leaf` emitters [0, 1, 2], lower-bound duration 196f, hit beat H = 160 (budget 160); existing sprite resources: none. Script: `res/moves/magical_leaf/anim.s`.

### PRIMARY: Homing curved leaves (native+opal) - PROVISIONAL

Native leaf waves; hero leaf from Ranger 2 shaded art on curved arcs with Opal leaf spins, razor glint and flutter on arrival.

*Why:* Leaf-homing template (offset launch, curved travel, convergence); the shaded Ranger leaf adds a hero projectile over the P0 leaf vocabulary.

* keep native emitters [0, 1, 2] (native leaf waves at 0/80/160)
* travel @ L+0 (+34f): installed `opal_b9_nature` / `leaf_spin` x3 - OpalProjectile (arc 8)
* travel @ L+4 (+34f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e079_LZ.bin#12` (12t) x2 - OpalProjectile (arc 10) - Ranger 2 e079 shaded leaves
* impact @ H+0 (+12f): installed `opal_b9_nature` / `razor_blade` x1 - OpalImpactBurst
* aftermath @ H+4 (+24f): installed `opal_b9_nature` / `leaf_flutter` x3 - OpalResidual
* cue @ H+0: OpalReactMagic green

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactMagic, OpalResidual; installed sheets opal_b9_nature; new sheet `opal_b9p_magical_leaf` (12 tiles, <= 4 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +12 new OBJ tiles; peak 118t / 2 mgr / 16 OAM; ~96 GX quads, 2560 B tex; ~196f (+0 vs native lb).

### ALTERNATIVE 1: Existing nature (opal_existing) - PROVISIONAL

Installed leaf spin + flutter.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2]
* travel @ L+0 (+34f): installed `opal_b9_nature` / `leaf_spin` x4 - OpalProjectile
* aftermath @ H+4 (+24f): installed `opal_b9_nature` / `leaf_flutter` x3 - OpalResidual

*Compatibility:* macros OpalProjectile, OpalResidual; installed sheets opal_b9_nature; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 106t / 1 mgr / 16 OAM; ~96 GX quads, 2560 B tex; ~196f (+0 vs native lb).

### ALTERNATIVE 2: Blade leaves (native+opal) - PROVISIONAL

Borrowed Leaf Blade emitters for sharper leaves.

*Why:* Sharper silhouette.

* keep native emitters [0, 1, 2]
* borrow @ L+0 (+85f): borrow Platinum `leaf_blade.spa` emitters [0, 1, 2, 3, 4] - leaf silhouettes (peak 58 quads, 5632 B tex)
* impact @ H+0 (+12f): installed `opal_b9_nature` / `razor_blade` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_b9_nature; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 106t / 1 mgr / 4 OAM; ~154 GX quads, 8192 B tex; ~196f (+0 vs native lb).

## Metal Claw (P1, `steel_slash`) - metal glint/trailing slash

Native: `no particle archive` emitters [], lower-bound duration 10f, hit beat H = 5 (budget 8); existing sprite resources: ['claw_NCGR_lz']. Script: `res/moves/metal_claw/anim.s`.

### PRIMARY: Steel rake (native+opal) - PROVISIONAL

The native script is sprite-based (no particles); keep its claw sprite and add steel-tinted claw swipes, a four-point metal glint and a light recoil.

*Why:* Steel-slash template (metal glint, trailing slash). Platinum has no particle for this move, so Opal carries the effect.

* keep native emitters [] (native claw sprite flow (no particle archive))
* travel @ L+2 (+10f): installed `opal_b9_strike` / `claw_a` x1 - OpalImpactBurst (steel palette variant) - needs a steel palette variant of the strike sheet
* travel @ L+5 (+10f): installed `opal_b9_strike` / `claw_b` x1 - OpalImpactBurst
* impact @ H+0 (+10f): NEW donor cell(s) Pokemon Emerald `sparkle_6.png` (4t) x2 - OpalImpactBurst x2 - Emerald sparkle_6.png glint
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalReactLight; installed sheets opal_b9_strike; new sheet `opal_b9p_metal_claw` (4 tiles, <= 5 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG. Needs: needs a steel palette variant of the strike sheet.
*Cost (static estimate):* +4 new OBJ tiles; peak 188t / 2 mgr / 10 OAM; ~0 GX quads, 0 B tex; ~18f (+8 vs native lb).

### ALTERNATIVE 1: Donor claw swipes (native+donor) - PROVISIONAL

Emerald claw_slash.png swipes + glint.

*Why:* Distinct claw drawing.

* keep native emitters []
* travel @ L+2 (+14f): NEW donor cell(s) Pokemon Emerald `claw_slash.png` (60t) x3 - OpalImpactBurst
* impact @ H+0 (+10f): NEW donor cell(s) Pokemon Emerald `sparkle_6.png` (4t) x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets none; new sheet `opal_b9p_metal_claw` (64 tiles, <= 13 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +64 new OBJ tiles; peak 64t / 1 mgr / 16 OAM; ~0 GX quads, 0 B tex; ~18f (+8 vs native lb).

### ALTERNATIVE 2: Slash flash (native+opal) - PROVISIONAL

Borrowed Slash flash masks + glint.

*Why:* Native-look slashes.

* keep native emitters []
* borrow @ L+2 (+17f): borrow Platinum `slash.spa` emitters [0, 1, 2] - slash flash masks (peak 32 quads, 1024 B tex)
* impact @ H+0 (+10f): NEW donor cell(s) Pokemon Emerald `sparkle_6.png` (4t) x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets none; new sheet `opal_b9p_metal_claw` (4 tiles, <= 5 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +4 new OBJ tiles; peak 4t / 1 mgr / 1 OAM; ~32 GX quads, 1024 B tex; ~19f (+9 vs native lb).

## Rock Tomb (P1, `rock_fall`) - rocks converge

Native: `rock_tomb` emitters [0, 1], lower-bound duration 106f, hit beat H = 60 (budget 60); existing sprite resources: none. Script: `res/moves/rock_tomb/anim.s`.

### PRIMARY: Converging boulders (native+opal) - PROVISIONAL

Native falling rocks (30-60 frame cadence); Opal boulder, break and dirt at each landing plus residual dust.

*Why:* Rock-fall template (telegraph, staggered fall, dust settle); reuses the P0 rock sheet.

* keep native emitters [1, 0] (native rock falls)
* travel @ L+28 (+14f): installed `opal_b9_rock` / `boulder` x3 - OpalProjectile (fall)
* impact @ H+0 (+13f): installed `opal_b9_rock` / `break` x2 - OpalImpactBurst
* aftermath @ H+2 (+20f): installed `opal_b9_rock` / `dirt` x3 - OpalResidual
* cue @ H+0: OpalCamPunch

*Compatibility:* macros OpalCamPunch, OpalImpactBurst, OpalProjectile, OpalResidual; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 20 OAM; ~32 GX quads, 1024 B tex; ~106f (+0 vs native lb).

### ALTERNATIVE 1: Camera-light tomb (opal_existing) - PROVISIONAL

Rock sheet only, no camera cue.

*Why:* Cheapest.

* keep native emitters [1, 0]
* impact @ H+0 (+13f): installed `opal_b9_rock` / `break` x2 - OpalImpactBurst
* aftermath @ H+2 (+20f): installed `opal_b9_rock` / `dirt` x3 - OpalResidual

*Compatibility:* macros OpalImpactBurst, OpalResidual; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 20 OAM; ~32 GX quads, 1024 B tex; ~106f (+0 vs native lb).

### ALTERNATIVE 2: Stone spikes (native+opal) - PROVISIONAL

Borrowed Stone Edge emitters (spikes + boulder) as a rising tomb wall.

*Why:* Walled-in look.

* keep native emitters [1, 0]
* borrow @ L+28 (+58f): borrow Platinum `stone_edge.spa` emitters [0, 1, 2, 3] - spike/boulder masks (peak 60 quads, 2560 B tex)
* aftermath @ H+2 (+20f): installed `opal_b9_rock` / `dirt` x3 - OpalResidual

*Compatibility:* macros OpalResidual; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 12 OAM; ~92 GX quads, 3584 B tex; ~106f (+0 vs native lb).

## Rock Slide (P1, `rock_fall`) - spread rocks

Native: `rock_slide` emitters [0, 1, 2], lower-bound duration 73f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/rock_slide/anim.s`.

### PRIMARY: Spread slide (native+opal) - PROVISIONAL

Native three-emitter slide; three boulder lanes spreading across the target side, break/dirt per landing, pebble debris and a camera punch.

*Why:* Rock-fall (spread) template; heavier camera cue than Rock Tomb to separate the two.

* keep native emitters [0, 1, 2]
* travel @ L+0 (+40f): installed `opal_b9_rock` / `boulder` x3 - OpalProjectile (3 lanes)
* impact @ H+0 (+13f): installed `opal_b9_rock` / `break` x3 - OpalImpactBurst
* aftermath @ H+4 (+22f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e129_LZ.bin#4` (20t) x2 - OpalResidual - Ranger 2 e129 pebbles
* cue @ H+0: OpalCamPunchHeavy

*Compatibility:* macros OpalCamPunchHeavy, OpalImpactBurst, OpalProjectile, OpalResidual; installed sheets opal_b9_rock; new sheet `opal_b9p_rock_slide` (20 tiles, <= 9 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +20 new OBJ tiles; peak 104t / 2 mgr / 28 OAM; ~283 GX quads, 5376 B tex; ~73f (+0 vs native lb).

### ALTERNATIVE 1: Existing slide (opal_existing) - PROVISIONAL

Rock sheet only.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2]
* travel @ L+0 (+40f): installed `opal_b9_rock` / `boulder` x3 - OpalProjectile
* impact @ H+0 (+13f): installed `opal_b9_rock` / `break` x3 - OpalImpactBurst
* aftermath @ H+4 (+12f): installed `opal_b9_rock` / `dirt` x3 - OpalResidual

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalResidual; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 36 OAM; ~283 GX quads, 5376 B tex; ~73f (+0 vs native lb).

### ALTERNATIVE 2: Wrecker debris (native+opal) - PROVISIONAL

Borrowed Rock Wrecker debris emitters.

*Why:* More debris.

* keep native emitters [0, 1, 2]
* borrow @ H+0 (+40f): borrow Platinum `rock_wrecker.spa` emitters [0, 1, 2, 3, 4] - debris masks (peak 148 quads, 9472 B tex)
* impact @ H+0 (+13f): installed `opal_b9_rock` / `break` x2 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 8 OAM; ~431 GX quads, 14848 B tex; ~73f (+0 vs native lb).

## Crunch (P1, `bite`) - powerful closing impact

Native: `crunch` emitters [0, 1, 2, 3, 4], lower-bound duration 39f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/crunch/anim.s`.

### PRIMARY: Closing jaws (native+opal) - PROVISIONAL

Native five-emitter jaw rows; flanking purple fangs, a heavier-scaled snap and light recoil, with a camera punch.

*Why:* Bite template, bigger and darker than P0 Bite: purple flanking fangs and a larger snap.

* keep native emitters [0, 1, 2, 3, 4]
* launch @ L+0 (+12f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e020_LZ.bin#4` (16t) x2 - OpalFx (closing fangs) - Ranger 2 e020 purple fangs
* impact @ H-4 (+8f): installed `opal_b9_strike` / `jaw_upper` x1 - OpalImpactBurst scale 130
* impact @ H-4 (+8f): installed `opal_b9_strike` / `jaw_lower` x1 - OpalImpactBurst scale 130
* impact @ H+0 (+10f): installed `opal_b9_strike` / `hit_small` x1 - OpalImpactBurst
* cue @ H+0: OpalCamPunch
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalCamPunch, OpalFx, OpalImpactBurst, OpalReactLight; installed sheets opal_b9_strike; new sheet `opal_b9p_crunch` (16 tiles, <= 4 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +16 new OBJ tiles; peak 200t / 2 mgr / 14 OAM; ~20 GX quads, 9216 B tex; ~39f (+0 vs native lb).

### ALTERNATIVE 1: Existing jaws (opal_existing) - PROVISIONAL

P0 jaw sprites, larger.

*Why:* Zero new tiles; risks looking like Bite.

* keep native emitters [0, 1, 2, 3, 4]
* impact @ H-4 (+8f): installed `opal_b9_strike` / `jaw_upper` x1 - OpalImpactBurst scale 130
* impact @ H-4 (+8f): installed `opal_b9_strike` / `jaw_lower` x1 - OpalImpactBurst scale 130
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalReactLight; installed sheets opal_b9_strike; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 8 OAM; ~20 GX quads, 9216 B tex; ~39f (+0 vs native lb).

### ALTERNATIVE 2: Fang masks (native+opal) - PROVISIONAL

Borrowed Bite/Thunder Fang jaw masks.

*Why:* Native-look jaws.

* keep native emitters [0, 1, 2, 3, 4]
* borrow @ H-2 (+52f): borrow Platinum `thunder_fang.spa` emitters [0, 1, 2, 3, 4, 5] - jaw-row masks (peak 79 quads, 12544 B tex)
* impact @ H+0 (+10f): installed `opal_b9_strike` / `hit_small` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_b9_strike; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 4 OAM; ~99 GX quads, 21760 B tex; ~58f (+19 vs native lb). Notes: CADENCE: extends the native lower-bound duration by 19 frames (> 12); needs a payoff argument or a cut

## Ice Shard (P1, `ice_projectile`) - sharp ice pieces

Native: `ice_shard` emitters [0, 1, 2, 3, 4], lower-bound duration 167f, hit beat H = 100 (budget 100); existing sprite resources: none. Script: `res/moves/ice_shard/anim.s`.

### PRIMARY: Shard volley (native+opal) - PROVISIONAL

Native shard emitters; three icicle lead shards with trails, ice shatter and glints on impact.

*Why:* Ice-projectile template (crystalline shards, sharp burst); joins the B2 ice sheet.

* keep native emitters [1, 3, 2, 4, 0]
* travel @ L+0 (+24f): NEW donor cell(s) Pokemon Emerald `icicle_spear.png` (8t) x3 - OpalProjectile (trail) - Emerald icicle_spear.png
* impact @ H+0 (+12f): NEW donor cell(s) Pokemon Emerald `ice_crystals_2.png` (2t) x3 - OpalImpactBurst - Emerald ice_crystals_2.png
* impact @ H+0 (+12f): installed `opal_ice` / `shatter` x1 - OpalImpactBurst
* aftermath @ H+4 (+9f): installed `opal_ice` / `glint` x3 - OpalResidual
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactLight, OpalResidual; installed sheets opal_ice; new sheet `opal_b9p_ice_shard` (10 tiles, <= 10 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +10 new OBJ tiles; peak 82t / 2 mgr / 19 OAM; ~78 GX quads, 6656 B tex; ~167f (+0 vs native lb).

### ALTERNATIVE 1: Existing ice (opal_existing) - PROVISIONAL

Shatter + glint only.

*Why:* Zero new tiles.

* keep native emitters [1, 3, 2, 4, 0]
* impact @ H+0 (+12f): installed `opal_ice` / `shatter` x2 - OpalImpactBurst
* aftermath @ H+4 (+9f): installed `opal_ice` / `glint` x3 - OpalResidual

*Compatibility:* macros OpalImpactBurst, OpalResidual; installed sheets opal_ice; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 72t / 1 mgr / 20 OAM; ~78 GX quads, 6656 B tex; ~167f (+0 vs native lb).

### ALTERNATIVE 2: Spear borrow (native+opal) - PROVISIONAL

Borrowed Icicle Spear emitters.

*Why:* Native-look icicle.

* keep native emitters [1, 3, 2, 4, 0]
* borrow @ L+0 (+20f): borrow Platinum `icicle_spear.spa` emitters [0, 1] - spike masks + ice chunk (peak 9 quads, 2048 B tex)
* impact @ H+0 (+12f): installed `opal_ice` / `shatter` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_ice; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 72t / 1 mgr / 4 OAM; ~87 GX quads, 8704 B tex; ~167f (+0 vs native lb).

## Icy Wind (P1, `ice_wind`) - chilling current

Native: `icy_wind` emitters [0, 1, 2], lower-bound duration 116f, hit beat H = 20 (budget 20); existing sprite resources: none. Script: `res/moves/icy_wind/anim.s`.

### PRIMARY: Frost current (native+opal) - PROVISIONAL

Native gust emitters; ice-palette wind swirl/streaks to the target and violet-blue crystal drift.

*Why:* Ice-wind template (sweeping haze, frost sparkles); uses the existing ice wind palette variant.

* keep native emitters [0, 1, 2]
* travel @ L+0 (+40f): installed `opal_b9_wind` [ice] / `swirl` x1 - OpalProjectile
* travel @ L+10 (+50f): installed `opal_b9_wind` [ice] / `flecks` x3 - OpalResidual (ice flecks)
* aftermath @ H+4 (+24f): NEW donor cell(s) Pokemon Emerald `ice_crystals_4.png` (2t); Pokemon Emerald `ice_crystals_2.png` (2t) x3 - OpalResidual - Emerald ice_crystals_4/2

*Compatibility:* macros OpalProjectile, OpalResidual; installed sheets opal_b9_wind; new sheet `opal_b9p_icy_wind` (4 tiles, <= 7 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +4 new OBJ tiles; peak 82t / 2 mgr / 19 OAM; ~137 GX quads, 6400 B tex; ~116f (+0 vs native lb).

### ALTERNATIVE 1: Wind ice only (opal_existing) - PROVISIONAL

Ice-variant wind sheet.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2]
* travel @ L+0 (+40f): installed `opal_b9_wind` [ice] / `swirl` x1 - OpalProjectile
* aftermath @ H+0 (+40f): installed `opal_b9_wind` [ice] / `flecks` x3 - OpalResidual

*Compatibility:* macros OpalProjectile, OpalResidual; installed sheets opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 78t / 1 mgr / 16 OAM; ~137 GX quads, 6400 B tex; ~116f (+0 vs native lb).

### ALTERNATIVE 2: Powder snow borrow (native+opal) - PROVISIONAL

Borrowed Powder Snow sparkles.

*Why:* Snowier look.

* keep native emitters [0, 1, 2]
* borrow @ H+0 (+115f): borrow Platinum `powder_snow.spa` emitters [0, 1] - snow-crystal sparkle masks (peak 49 quads, 5376 B tex)
* travel @ L+0 (+40f): installed `opal_b9_wind` [ice] / `swirl` x1 - OpalProjectile

*Compatibility:* macros OpalProjectile; installed sheets opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 78t / 1 mgr / 4 OAM; ~186 GX quads, 11776 B tex; ~135f (+19 vs native lb). Notes: CADENCE: extends the native lower-bound duration by 19 frames (> 12); needs a payoff argument or a cut

## Mud Shot (P1, `mud_projectile`) - earth splash

Native: `mud_shot` emitters [10, 14], lower-bound duration 87f, hit beat H = 10 (budget 10); existing sprite resources: none. Script: `res/moves/mud_shot/anim.s`.

### PRIMARY: Clod volley (native+opal) - PROVISIONAL

Native muddy spray; three brown clods on arcs, droplet splats and a rock-sheet dirt burst on landing.

*Why:* Mud-projectile template (earth splash).

* keep native emitters [14, 10]
* travel @ L+0 (+24f): NEW donor cell(s) Pokemon Emerald `dirt_mound.png` (16t) x3 - OpalProjectile (arc 8) - Emerald dirt_mound.png
* impact @ H+0 (+14f): NEW donor cell(s) Pokemon Emerald `mud_sand_0.png` (1t) x3 - OpalImpactBurst - Emerald mud_sand_0.png droplets
* impact @ H+0 (+10f): installed `opal_b9_rock` / `dirt` x2 - OpalImpactBurst
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactLight; installed sheets opal_b9_rock; new sheet `opal_b9p_mud_shot` (17 tiles, <= 10 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +17 new OBJ tiles; peak 101t / 2 mgr / 14 OAM; ~140 GX quads, 7936 B tex; ~87f (+0 vs native lb).

### ALTERNATIVE 1: Existing dirt (opal_existing) - PROVISIONAL

Rock dirt/shards only.

*Why:* Zero new tiles.

* keep native emitters [14, 10]
* impact @ H+0 (+10f): installed `opal_b9_rock` / `dirt` x3 - OpalImpactBurst
* aftermath @ H+2 (+15f): installed `opal_b9_rock` / `shards` x2 - OpalResidual

*Compatibility:* macros OpalImpactBurst, OpalResidual; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 20 OAM; ~140 GX quads, 7936 B tex; ~87f (+0 vs native lb).

### ALTERNATIVE 2: Slap splat (native+opal) - PROVISIONAL

Borrowed Mud-Slap splat masks.

*Why:* Native-look splat.

* keep native emitters [14, 10]
* borrow @ H+0 (+51f): borrow Platinum `mud_slap.spa` emitters [0, 1] - radial splat + puff masks (peak 53 quads, 5376 B tex)
* impact @ H+0 (+10f): installed `opal_b9_rock` / `dirt` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 4 OAM; ~193 GX quads, 13312 B tex; ~87f (+0 vs native lb).

## Mud Bomb (P1, `mud_projectile`) - heavy earthen orb

Native: `mud_bomb` emitters [0, 1, 2, 3], lower-bound duration 55f, hit beat H = 1 (budget 8); existing sprite resources: none. Script: `res/moves/mud_bomb/anim.s`.

### PRIMARY: Heavy earthen orb (native+opal) - PROVISIONAL

Native orb + defender emitters; a lobbed boulder-clod orb from Ranger 2 art, splash clods and a heavy camera punch.

*Why:* Mud-projectile (heavy orb): a single large lobbed mass, not a spray - distinct from Mud Shot.

* keep native emitters [0, 1, 3, 2]
* travel @ L+0 (+30f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e115_LZ.bin#4` (139t) x1 - OpalProjectile (arc 16) - Ranger 2 e115 boulders/clods
* impact @ H+0 (+14f): NEW donor cell(s) Pokemon Emerald `dirt_mound.png` (16t) x3 - OpalImpactBurst - Emerald dirt_mound.png splash
* cue @ H+0: OpalCamPunchHeavy
* cue @ H+0: OpalReactLight

*Compatibility:* macros OpalCamPunchHeavy, OpalImpactBurst, OpalProjectile, OpalReactLight; installed sheets none; new sheet `opal_b9p_mud_bomb` (155 tiles, <= 16 colours, palette fold needed); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +155 new OBJ tiles; peak 155t / 1 mgr / 7 OAM; ~124 GX quads, 10496 B tex; ~55f (+0 vs native lb).

### ALTERNATIVE 1: Existing boulder (opal_existing) - PROVISIONAL

Rock boulder/dirt.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 3, 2]
* travel @ L+0 (+30f): installed `opal_b9_rock` / `boulder` x1 - OpalProjectile (arc 16)
* impact @ H+0 (+10f): installed `opal_b9_rock` / `dirt` x3 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst, OpalProjectile; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 16 OAM; ~124 GX quads, 10496 B tex; ~55f (+0 vs native lb).

### ALTERNATIVE 2: Sludge blob (native+opal) - PROVISIONAL

Borrowed Sludge Bomb blob masks.

*Why:* Gloopier.

* keep native emitters [0, 1, 3, 2]
* borrow @ H+0 (+47f): borrow Platinum `sludge_bomb.spa` emitters [0, 1, 2] - soft blob masks (peak 76 quads, 5632 B tex)
* impact @ H+0 (+10f): installed `opal_b9_rock` / `dirt` x2 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_b9_rock; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 84t / 1 mgr / 8 OAM; ~200 GX quads, 16128 B tex; ~55f (+0 vs native lb).

## Psybeam (P1, `psychic_beam`) - colored psychic pulse

Native: `psybeam` emitters [0], lower-bound duration 94f, hit beat H = 20 (budget 20); existing sprite resources: none. Script: `res/moves/psybeam/anim.s`.

### PRIMARY: Colour-pulse beam (native+opal) - PROVISIONAL

Native pulsing beam; psychic ring pulses and a pink orb travel along it, expanding purple rings and a magenta pulse on the target.

*Why:* Psychic-beam template (coloured psychic pulse).

* keep native emitters [0]
* travel @ L+0 (+40f): installed `opal_fx_ring` [psychic] / `ring_expand` x3 - OpalProjectile (3 rings, psychic)
* travel @ L+0 (+30f): NEW donor cell(s) Pokemon Emerald `pink_orb.png` (1t) x3 - OpalProjectile - Emerald pink_orb.png
* impact @ H+0 (+20f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e041_LZ.bin#4` (116t) x1 - OpalImpactBurst - Ranger 2 e041 purple elliptical rings
* cue @ H+0: OpalReactMagic magenta

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactMagic; installed sheets opal_fx_ring; new sheet `opal_b9p_psybeam` (117 tiles, <= 5 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +117 new OBJ tiles; peak 301t / 2 mgr / 17 OAM; ~78 GX quads, 8192 B tex; ~94f (+0 vs native lb).

### ALTERNATIVE 1: Ring-only (opal_existing) - PROVISIONAL

Installed psychic ring palette only.

*Why:* Zero new tiles.

* keep native emitters [0]
* travel @ L+0 (+40f): installed `opal_fx_ring` [psychic] / `ring_expand` x3 - OpalProjectile
* cue @ H+0: OpalReactMagic magenta

*Compatibility:* macros OpalProjectile, OpalReactMagic; installed sheets opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 12 OAM; ~78 GX quads, 8192 B tex; ~94f (+0 vs native lb).

### ALTERNATIVE 2: Signal borrow (native+opal) - PROVISIONAL

Borrowed Signal Beam / Psycho Cut masks.

*Why:* Beamier.

* keep native emitters [0]
* borrow @ L+0 (+58f): borrow Platinum `signal_beam.spa` emitters [0] - beam body masks (emitter 0 only: all 9 together peak at ~1,400 quads) (peak 159 quads, 2048 B tex)
* impact @ H+0 (+10f): installed `opal_fx_ring` [psychic] / `ring_expand` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 4 OAM; ~237 GX quads, 10240 B tex; ~94f (+0 vs native lb).

## Swift (P1, `star_volley`) - star trails

Native: `swift` emitters [0, 1, 2], lower-bound duration 70f, hit beat H = 20 (budget 20); existing sprite resources: none. Script: `res/moves/swift/anim.s`.

### PRIMARY: Star volley (native+opal) - PROVISIONAL

Native star emitters; a five-star fan of yellow stars with trails, twinkle glints and a pierce star on arrival.

*Why:* Star-volley template (star trails).

* keep native emitters [2, 1, 0]
* travel @ L+0 (+24f): NEW donor cell(s) Pokemon Emerald `yellow_star.png` (8t) x5 - OpalProjectile (5-star fan, trail) - Emerald yellow_star.png
* travel @ L+4 (+24f): NEW donor cell(s) Pokemon Emerald `sparkle_6.png` (4t) x3 - OpalResidual (twinkles) - Emerald sparkle_6.png
* impact @ H+0 (+8f): installed `opal_b9_strike` / `star_pierce` x2 - OpalImpactBurst
* cue @ H+0: OpalLightPulse yellow

*Compatibility:* macros OpalImpactBurst, OpalLightPulse, OpalProjectile, OpalResidual; installed sheets opal_b9_strike; new sheet `opal_b9p_swift` (12 tiles, <= 7 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +12 new OBJ tiles; peak 196t / 2 mgr / 16 OAM; ~111 GX quads, 6656 B tex; ~70f (+0 vs native lb).

### ALTERNATIVE 1: Existing stars (opal_existing) - PROVISIONAL

Strike star + wx star pop.

*Why:* Zero new tiles.

* keep native emitters [2, 1, 0]
* impact @ H+0 (+8f): installed `opal_b9_strike` / `star_pierce` x3 - OpalImpactBurst
* aftermath @ H+2 (+7f): installed `opal_fx_wx` [gold] / `star_pop` x3 - OpalResidual

*Compatibility:* macros OpalImpactBurst, OpalResidual; installed sheets opal_b9_strike, opal_fx_wx; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 235t / 2 mgr / 24 OAM; ~111 GX quads, 6656 B tex; ~70f (+0 vs native lb).

### ALTERNATIVE 2: Cosmic stars (native+opal) - PROVISIONAL

Borrowed Cosmic Power star/ring masks.

*Why:* More celestial.

* keep native emitters [2, 1, 0]
* borrow @ L+0 (+67f): borrow Platinum `cosmic_power.spa` emitters [0, 1, 2, 3] - rings + sparkle + star masks (peak 119 quads, 10752 B tex)
* impact @ H+0 (+8f): installed `opal_b9_strike` / `star_pierce` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_b9_strike; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 4 OAM; ~230 GX quads, 17408 B tex; ~70f (+0 vs native lb).

## Thunder Wave (P2, `status_electric`) - electric bind/brief paralysis

Native: `thunder_wave` emitters [0, 1, 2], lower-bound duration 84f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/thunder_wave/anim.s`.

### PRIMARY: Binding arcs (native+opal) - PROVISIONAL

Native ring/bolt emitters; thunder-sheet zig-zag arcs wrap the target with Diamond and Emerald arc drawings, flicker and a yellow magic pulse.

*Why:* Electric-bind template (arcs wrap the target, brief paralysis flicker).

* keep native emitters [0, 1, 2]
* travel @ L+0 (+13f): installed `opal_thunder` / `bolt` x2 - OpalProjectile
* reaction @ H+0 (+16f): NEW donor cell(s) Pokemon Diamond/Pearl `narc_0035.NCER` (67t); Pokemon Emerald `spark_2.png` (12t) x3 - OpalImpactBurst (3 arcs) - Diamond narc_0035 jagged yellow arcs + Emerald spark_2.png zig-zag
* reaction @ H+4 (+8f): installed `opal_thunder` / `bolt_fade` x2 - OpalResidual
* cue @ H+0: OpalReactMagic yellow

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactMagic, OpalResidual; installed sheets opal_thunder; new sheet `opal_b9p_thunder_wave` (79 tiles, <= 2 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +79 new OBJ tiles; peak 186t / 2 mgr / 25 OAM; ~19 GX quads, 10240 B tex; ~84f (+0 vs native lb).

### ALTERNATIVE 1: Existing thunder (opal_existing) - PROVISIONAL

Bolt + fade only.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2]
* travel @ L+0 (+13f): installed `opal_thunder` / `bolt` x2 - OpalProjectile
* reaction @ H+4 (+8f): installed `opal_thunder` / `bolt_fade` x2 - OpalResidual

*Compatibility:* macros OpalProjectile, OpalResidual; installed sheets opal_thunder; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 107t / 1 mgr / 16 OAM; ~19 GX quads, 10240 B tex; ~84f (+0 vs native lb).

### ALTERNATIVE 2: Diamond arcs (native+donor) - PROVISIONAL

Diamond move-effect yellow jagged arcs.

*Why:* Distinct arc drawing.

* keep native emitters [0, 1, 2]
* reaction @ H+0 (+16f): NEW donor cell(s) Pokemon Diamond/Pearl `narc_0035.NCER` (67t) x2 - OpalImpactBurst
* cue @ H+0: OpalReactMagic yellow

*Compatibility:* macros OpalImpactBurst, OpalReactMagic; installed sheets none; new sheet `opal_b9p_thunder_wave` (67 tiles, <= 1 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +67 new OBJ tiles; peak 67t / 1 mgr / 6 OAM; ~19 GX quads, 10240 B tex; ~84f (+0 vs native lb).

## Hypnosis (P2, `status_sleep`) - spiral and drowse

Native: `hypnosis` emitters [0, 1, 2, 3, 4], lower-bound duration 90f, hit beat H = 30 (budget 30); existing sprite resources: none. Script: `res/moves/hypnosis/anim.s`.

### PRIMARY: Spiral drowse (custom composite) (custom_composite) - PROVISIONAL

Native ring emitters + purple fade; a recoloured PMD spiral blooms over the target, psychic rings converge on the eyes, then 'z' glyphs drift up.

*Why:* Status-sleep template (spiral and drowse). Composite because no pool has a ready 'hypnosis spiral + z' set.

* keep native emitters [0, 1, 2, 3, 4] (native rings at L, defender swirl at 30)
* DESIGN NOTE - Spiral: PMD effect.bin#128 is the only true spiral drawing in all pools (red spiral on a disc): recolour to the hypnosis purple/blue ramp, play as an expanding static burst over the defender (scale 60% -> 130%).
* reaction @ H+0 (+30f): NEW donor cell(s) Pokemon Mystery Dungeon: Explorers of Sky `effect.bin#128` (32t) x1 - OpalImpactBurst (growth, 60% -> 130%) - PMD effect.bin#128 spiral, recoloured purple/blue
* travel @ H-12 (+14f): installed `opal_fx_ring` [psychic] / `ring_converge` x3 - OpalProjectile (3 rings -> eyes)
* aftermath @ H+12 (+30f): NEW donor cell(s) Pokemon Emerald `z.png` (8t) x3 - OpalResidual (z drift) - Emerald z.png
* cue @ H+0: OpalReactMagic purple

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactMagic, OpalResidual; installed sheets opal_fx_ring; new sheet `opal_b9p_hypnosis` (40 tiles, <= 10 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +40 new OBJ tiles; peak 224t / 2 mgr / 13 OAM; ~16 GX quads, 5632 B tex; ~90f (+0 vs native lb).

### ALTERNATIVE 1: Rings and z (opal_existing+donor) - PROVISIONAL

Installed psychic rings + z glyphs only.

*Why:* Cheap and legible.

* keep native emitters [0, 1, 2, 3, 4]
* travel @ H-12 (+14f): installed `opal_fx_ring` [psychic] / `ring_converge` x3 - OpalProjectile
* aftermath @ H+12 (+30f): NEW donor cell(s) Pokemon Emerald `z.png` (8t) x3 - OpalResidual

*Compatibility:* macros OpalProjectile, OpalResidual; installed sheets opal_fx_ring; new sheet `opal_b9p_hypnosis` (8 tiles, <= 3 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +8 new OBJ tiles; peak 184t / 1 mgr / 12 OAM; ~16 GX quads, 5632 B tex; ~90f (+0 vs native lb).

### ALTERNATIVE 2: Lullaby (native+opal) - PROVISIONAL

Borrowed Sing rings + note masks, z glyphs.

*Why:* Softer, musical.

* keep native emitters [0, 1, 2, 3, 4]
* borrow @ L+0 (+111f): borrow Platinum `sing.spa` emitters [0, 1, 2] - concentric rings + note masks (peak 7 quads, 8192 B tex)
* aftermath @ H+12 (+30f): NEW donor cell(s) Pokemon Emerald `z.png` (8t) x3 - OpalResidual

*Compatibility:* macros OpalResidual; installed sheets none; new sheet `opal_b9p_hypnosis` (8 tiles, <= 3 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +8 new OBJ tiles; peak 8t / 1 mgr / 3 OAM; ~23 GX quads, 13824 B tex; ~111f (+21 vs native lb). Notes: CADENCE: extends the native lower-bound duration by 21 frames (> 12); needs a payoff argument or a cut

## Confuse Ray (P2, `status_confusion`) - looping ghost orbs

Native: `confuse_ray` emitters [0, 1], lower-bound duration 93f, hit beat H = 6 (budget 8); existing sprite resources: none. Script: `res/moves/confuse_ray/anim.s`.

### PRIMARY: Looping ghost orbs (native+opal) - PROVISIONAL

Native emitters; three ghost orbs loop around the target on staggered arcs with two heavier Ranger 2 dark orbs and a purple magic pulse.

*Why:* Confusion template (looping ghost orbs); reuses the B2 ghost sheet.

* keep native emitters [0, 1]
* travel @ L+0 (+30f): installed `opal_ghost` / `orb` x3 - OpalProjectile (looping arcs)
* reaction @ H+0 (+24f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e118_LZ.bin#4` (96t) x2 - OpalFx (orbit) - Ranger 2 e118 dark purple orbs with rim
* reaction @ H+4 (+20f): installed `opal_ghost` / `wisp` x2 - OpalResidual
* cue @ H+0: OpalReactMagic purple

*Compatibility:* macros OpalFx, OpalProjectile, OpalReactMagic, OpalResidual; installed sheets opal_ghost; new sheet `opal_b9p_confuse_ray` (96 tiles, <= 10 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +96 new OBJ tiles; peak 144t / 2 mgr / 22 OAM; ~4 GX quads, 512 B tex; ~93f (+0 vs native lb).

### ALTERNATIVE 1: Existing ghost (opal_existing) - PROVISIONAL

Ghost sheet only.

*Why:* Zero new tiles.

* keep native emitters [0, 1]
* travel @ L+0 (+30f): installed `opal_ghost` / `orb` x3 - OpalProjectile
* reaction @ H+4 (+20f): installed `opal_ghost` / `wisp` x2 - OpalResidual

*Compatibility:* macros OpalProjectile, OpalResidual; installed sheets opal_ghost; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 48t / 1 mgr / 20 OAM; ~4 GX quads, 512 B tex; ~93f (+0 vs native lb).

### ALTERNATIVE 2: Green wisp contrast (native+donor) - PROVISIONAL

Emerald blue-green orb as a contrast orb.

*Why:* Lighter, brighter orbs.

* keep native emitters [0, 1]
* travel @ L+0 (+30f): NEW donor cell(s) Pokemon Emerald `bluegreen_orb.png` (4t) x3 - OpalProjectile
* cue @ H+0: OpalReactMagic purple

*Compatibility:* macros OpalProjectile, OpalReactMagic; installed sheets none; new sheet `opal_b9p_confuse_ray` (4 tiles, <= 5 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +4 new OBJ tiles; peak 4t / 1 mgr / 3 OAM; ~4 GX quads, 512 B tex; ~93f (+0 vs native lb).

## Poison Powder (P2, `status_powder`) - poison pollen

Native: `poison_powder` emitters [0], lower-bound duration 86f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/poison_powder/anim.s`.

### PRIMARY: Toxic pollen cloud (native+opal) - PROVISIONAL

Native defender emitter; purple flecks drift in with a PMD speck cloud and a purple tint on the target.

*Why:* Status-powder template (poison pollen).

* keep native emitters [0]
* travel @ L+0 (+40f): installed `opal_b9_wind` / `flecks` x3 - OpalProjectile (purple palette variant) - needs a purple palette variant of the wind sheet
* reaction @ H+0 (+24f): NEW donor cell(s) Pokemon Mystery Dungeon: Explorers of Sky `effect.bin#266` (40t) x2 - OpalResidual - PMD effect.bin#266 purple/white specks
* cue @ H+0: OpalReactMagic purple

*Compatibility:* macros OpalProjectile, OpalReactMagic, OpalResidual; installed sheets opal_b9_wind; new sheet `opal_b9p_poison_powder` (40 tiles, <= 4 colours); runtime palette dependency: none; decode: HIGH. Needs: needs a purple palette variant of the wind sheet.
*Cost (static estimate):* +40 new OBJ tiles; peak 118t / 2 mgr / 20 OAM; ~100 GX quads, 512 B tex; ~86f (+0 vs native lb).

### ALTERNATIVE 1: Flecks only (opal_existing) - PROVISIONAL

Wind flecks in a purple palette.

*Why:* Cheapest.

* keep native emitters [0]
* travel @ L+0 (+40f): installed `opal_b9_wind` / `flecks` x3 - OpalProjectile
* cue @ H+0: OpalReactMagic purple

*Compatibility:* macros OpalProjectile, OpalReactMagic; installed sheets opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 78t / 1 mgr / 12 OAM; ~100 GX quads, 512 B tex; ~86f (+0 vs native lb).

### ALTERNATIVE 2: Toxic puffs (native+opal) - PROVISIONAL

Borrowed Toxic soft puff masks in purple.

*Why:* Cloudier.

* keep native emitters [0]
* borrow @ L+0 (+59f): borrow Platinum `toxic.spa` emitters [0, 1, 2] - soft puff masks (peak 78 quads, 2304 B tex)
* cue @ H+0: OpalReactMagic purple

*Compatibility:* macros OpalReactMagic; installed sheets none; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 0t / 0 mgr / 0 OAM; ~178 GX quads, 2816 B tex; ~86f (+0 vs native lb).

## Sleep Powder (P2, `status_powder`) - sleep pollen

Native: `sleep_powder` emitters [0], lower-bound duration 86f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/sleep_powder/anim.s`.

### PRIMARY: Drifting spores to drowse (native+opal) - PROVISIONAL

Native defender emitter; three soft pink clouds drift over, then lavender and blue 'z' glyphs rise, with a blue magic tint.

*Why:* Status-powder template (sleep pollen).

* keep native emitters [0]
* travel @ L+0 (+30f): NEW donor cell(s) Pokemon Emerald `pink_cloud.png` (16t) x3 - OpalProjectile (arc 6) - Emerald pink_cloud.png
* reaction @ H+4 (+36f): NEW donor cell(s) Pokemon Emerald `snore_z.png` (16t); Pokemon Emerald `z.png` (8t) x3 - OpalResidual (z drift) - Emerald snore_z.png + z.png
* cue @ H+0: OpalReactMagic blue

*Compatibility:* macros OpalProjectile, OpalReactMagic, OpalResidual; installed sheets none; new sheet `opal_b9p_sleep_powder` (40 tiles, <= 16 colours, palette fold needed); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +40 new OBJ tiles; peak 40t / 1 mgr / 6 OAM; ~100 GX quads, 512 B tex; ~86f (+0 vs native lb).

### ALTERNATIVE 1: Z only (native+donor) - PROVISIONAL

Native powder + z glyphs.

*Why:* Cheapest.

* keep native emitters [0]
* reaction @ H+4 (+36f): NEW donor cell(s) Pokemon Emerald `z.png` (8t) x3 - OpalResidual
* cue @ H+0: OpalReactMagic blue

*Compatibility:* macros OpalReactMagic, OpalResidual; installed sheets none; new sheet `opal_b9p_sleep_powder` (8 tiles, <= 3 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +8 new OBJ tiles; peak 8t / 1 mgr / 3 OAM; ~100 GX quads, 512 B tex; ~86f (+0 vs native lb).

### ALTERNATIVE 2: Scent petals (native+opal) - PROVISIONAL

Borrowed Sweet Scent petal/haze masks.

*Why:* Floral.

* keep native emitters [0]
* borrow @ L+0 (+83f): borrow Platinum `sweet_scent.spa` emitters [0, 1, 2, 3, 4] - petal + haze masks (peak 97 quads, 10240 B tex)
* reaction @ H+4 (+36f): NEW donor cell(s) Pokemon Emerald `z.png` (8t) x3 - OpalResidual

*Compatibility:* macros OpalResidual; installed sheets none; new sheet `opal_b9p_sleep_powder` (8 tiles, <= 3 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +8 new OBJ tiles; peak 8t / 1 mgr / 3 OAM; ~197 GX quads, 10752 B tex; ~86f (+0 vs native lb).

## Stun Spore (P2, `status_powder`) - stun pollen

Native: `stun_spore` emitters [0], lower-bound duration 86f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/stun_spore/anim.s`.

### PRIMARY: Yellow pollen to static (native+opal) - PROVISIONAL

Native defender emitter; white/tan spore balls on arcs, installed thunder sparks and Ranger 2 lightning strands on the target.

*Why:* Status-powder template (stun pollen).

* keep native emitters [0]
* travel @ L+0 (+30f): NEW donor cell(s) Pokemon Emerald `spore.png` (8t) x3 - OpalProjectile (arc 6) - Emerald spore.png
* reaction @ H+0 (+12f): installed `opal_thunder` / `sparks` x2 - OpalImpactBurst
* reaction @ H+2 (+20f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e103_LZ.bin#4` (152t) x2 - OpalImpactBurst - Ranger 2 e103 yellow lightning strands
* cue @ H+0: OpalReactMagic yellow

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactMagic; installed sheets opal_thunder; new sheet `opal_b9p_stun_spore` (160 tiles, <= 9 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG, HIGH.
*Cost (static estimate):* +160 new OBJ tiles; peak 267t / 2 mgr / 23 OAM; ~100 GX quads, 512 B tex; ~86f (+0 vs native lb).

### ALTERNATIVE 1: Sparks only (opal_existing) - PROVISIONAL

Thunder sparks only.

*Why:* Zero new tiles.

* keep native emitters [0]
* reaction @ H+0 (+12f): installed `opal_thunder` / `sparks` x2 - OpalImpactBurst
* cue @ H+0: OpalReactMagic yellow

*Compatibility:* macros OpalImpactBurst, OpalReactMagic; installed sheets opal_thunder; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 107t / 1 mgr / 8 OAM; ~100 GX quads, 512 B tex; ~86f (+0 vs native lb).

### ALTERNATIVE 2: Emerald zig-zag (native+donor) - PROVISIONAL

Emerald spark_1 zig-zag arcs.

*Why:* Lighter static read.

* keep native emitters [0]
* reaction @ H+0 (+14f): NEW donor cell(s) Pokemon Emerald `spark_1.png` (16t) x2 - OpalImpactBurst
* cue @ H+0: OpalReactMagic yellow

*Compatibility:* macros OpalImpactBurst, OpalReactMagic; installed sheets none; new sheet `opal_b9p_stun_spore` (16 tiles, <= 1 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +16 new OBJ tiles; peak 16t / 1 mgr / 4 OAM; ~100 GX quads, 512 B tex; ~86f (+0 vs native lb).

## Swords Dance (P2, `status_buff`) - orbiting blades

Native: `swords_dance` emitters [0, 1], lower-bound duration 42f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/swords_dance/anim.s`.

### PRIMARY: Orbiting blades (custom composite) (custom_composite) - PROVISIONAL

Native glow + sword-mask emitters; four blue blades orbit the user (baked orbit animation), a charge aura and a final white-blue flash.

*Why:* Status-buff template (orbiting blades). Composite: no pool contains an orbit set; the blade art exists (Emerald), the orbit is authored.

* keep native emitters [1, 0] (native sparkle + sword mask at the attacker)
* DESIGN NOTE - Orbit: DS OBJ sprites cannot rotate in the sheet pipeline: bake a 12-step orbit animation from TWO pixel-exact blade frames (upright, horizontal); the other orientations come from hflip/vflip. Four blades start 90 degrees apart and rotate once over ~36 frames.
* launch @ L+4 (+40f): NEW donor cell(s) Pokemon Emerald `sword.png` (32t) x4 - OpalFx x4 (baked orbit animation) - Emerald sword.png (blue blade); 2 baked frames
* launch @ L+0 (+14f): installed `opal_fx_ring` [steel] / `ring_converge` x1 - OpalChargeAura
* aftermath @ L+36 (+7f): installed `opal_fx_ring` [steel] / `star_pop` x1 - OpalImpactBurst (targets=attacker)
* cue @ L+38: OpalLightPulse white

*Compatibility:* macros OpalChargeAura, OpalFx, OpalImpactBurst, OpalLightPulse; installed sheets opal_fx_ring; new sheet `opal_b9p_swords_dance` (32 tiles, <= 2 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +32 new OBJ tiles; peak 216t / 2 mgr / 12 OAM; ~41 GX quads, 6144 B tex; ~44f (+2 vs native lb).

### ALTERNATIVE 1: Single blade rise (native+donor) - PROVISIONAL

One blade rises and glints.

*Why:* Much cheaper; no orbit.

* keep native emitters [1, 0]
* launch @ L+4 (+30f): NEW donor cell(s) Pokemon Emerald `sword.png` (32t) x1 - OpalFx (rise)
* cue @ L+30: OpalLightPulse white

*Compatibility:* macros OpalFx, OpalLightPulse; installed sheets none; new sheet `opal_b9p_swords_dance` (32 tiles, <= 2 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +32 new OBJ tiles; peak 32t / 1 mgr / 2 OAM; ~41 GX quads, 6144 B tex; ~42f (+0 vs native lb).

### ALTERNATIVE 2: Native + ring (opal_existing) - PROVISIONAL

Native emitters with a steel ring flourish.

*Why:* Zero new tiles.

* keep native emitters [1, 0]
* launch @ L+0 (+14f): installed `opal_fx_ring` [steel] / `ring_converge` x1 - OpalChargeAura
* aftermath @ L+30 (+7f): installed `opal_fx_ring` [steel] / `star_pop` x1 - OpalImpactBurst

*Compatibility:* macros OpalChargeAura, OpalImpactBurst; installed sheets opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 4 OAM; ~41 GX quads, 6144 B tex; ~42f (+0 vs native lb).

## Defense Curl (P2, `status_buff`) - defensive curl glint

Native: `defense_curl` emitters [0, 1], lower-bound duration 25f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/defense_curl/anim.s`.

### PRIMARY: Curl glint (native+opal) - PROVISIONAL

Native sphere + crescent emitters; a gold defensive ring pulse and a borrowed Disable star glint, with a white light pulse.

*Why:* Defensive-curl glint template.

* keep native emitters [0, 1]
* launch @ L+0 (+12f): installed `opal_fx_ring` [gold] / `flat_expand` x1 - OpalChargeAura
* borrow @ L+12 (+19f): borrow Platinum `disable.spa` emitters [0, 1] - four-point star glint masks (Platinum Disable) (peak 2 quads, 4096 B tex)
* cue @ L+12: OpalLightPulse white

*Compatibility:* macros OpalChargeAura, OpalLightPulse; installed sheets opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 4 OAM; ~4 GX quads, 9216 B tex; ~31f (+6 vs native lb).

### ALTERNATIVE 1: Ring only (opal_existing) - PROVISIONAL

Gold ring pulse.

*Why:* Zero new tiles.

* keep native emitters [0, 1]
* launch @ L+0 (+12f): installed `opal_fx_ring` [gold] / `flat_expand` x1 - OpalChargeAura

*Compatibility:* macros OpalChargeAura; installed sheets opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 4 OAM; ~2 GX quads, 5120 B tex; ~25f (+0 vs native lb).

### ALTERNATIVE 2: Shell glint (native+opal) - PROVISIONAL

Borrowed Withdraw shell masks + an Emerald glint.

*Why:* More shell-like.

* keep native emitters [0, 1]
* borrow @ L+0 (+52f): borrow Platinum `withdraw.spa` emitters [0, 1, 2, 3] - shell masks (peak 12 quads, 13312 B tex)
* aftermath @ L+12 (+14f): NEW donor cell(s) Pokemon Emerald `sparkle_3.png` (12t) x2 - OpalImpactBurst (targets=attacker)

*Compatibility:* macros OpalImpactBurst; installed sheets none; new sheet `opal_b9p_defense_curl` (12 tiles, <= 7 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +12 new OBJ tiles; peak 12t / 1 mgr / 4 OAM; ~14 GX quads, 18432 B tex; ~52f (+27 vs native lb). Notes: cadence unverifiable: the native lower bound is only 25 frames (task durations unknown), so +27 cannot be judged without a runtime measurement

## Focus Energy (P2, `status_buff`) - focus tightening

Native: `focus_energy` emitters [0, 1], lower-bound duration 50f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/focus_energy/anim.s`.

### PRIMARY: Tightening aura (native+opal) - PROVISIONAL

Native gradient/spire emitters; three red-orange rings converge on the user, then twin glints.

*Why:* Focus-tightening template.

* keep native emitters [1, 0]
* launch @ L+0 (+30f): installed `opal_fx_ring` [fire] / `ring_converge` x3 - OpalChargeAura (3 rings)
* aftermath @ L+30 (+14f): NEW donor cell(s) Pokemon Emerald `sparkle_3.png` (12t) x2 - OpalImpactBurst (targets=attacker) - Emerald sparkle_3.png
* cue @ L+30: OpalLightPulse orange

*Compatibility:* macros OpalChargeAura, OpalImpactBurst, OpalLightPulse; installed sheets opal_fx_ring; new sheet `opal_b9p_focus_energy` (12 tiles, <= 7 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +12 new OBJ tiles; peak 184t / 1 mgr / 12 OAM; ~24 GX quads, 512 B tex; ~50f (+0 vs native lb).

### ALTERNATIVE 1: Rings only (opal_existing) - PROVISIONAL

Fire-palette converging rings.

*Why:* Zero new tiles.

* keep native emitters [1, 0]
* launch @ L+0 (+30f): installed `opal_fx_ring` [fire] / `ring_converge` x3 - OpalChargeAura

*Compatibility:* macros OpalChargeAura; installed sheets opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 12 OAM; ~24 GX quads, 512 B tex; ~50f (+0 vs native lb).

### ALTERNATIVE 2: Glaring eyes (native+donor) - PROVISIONAL

Diamond red glaring eyes flash.

*Why:* Intense-focus read; large tile cost.

* keep native emitters [1, 0]
* launch @ L+10 (+20f): NEW donor cell(s) Pokemon Diamond/Pearl `narc_0006.NCER` (168t) x1 - OpalChargeAura
* launch @ L+0 (+20f): installed `opal_fx_ring` [fire] / `ring_converge` x1 - OpalChargeAura

*Compatibility:* macros OpalChargeAura; installed sheets opal_fx_ring; new sheet `opal_b9p_focus_energy` (168 tiles, <= 4 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +168 new OBJ tiles; peak 352t / 2 mgr / 7 OAM; ~24 GX quads, 512 B tex; ~50f (+0 vs native lb).

## Sand Attack (P2, `status_debuff`) - directed grains

Native: `sand_attack` emitters [0, 1, 2, 3], lower-bound duration 30f, hit beat H = 9 (budget 9); existing sprite resources: none. Script: `res/moves/sand_attack/anim.s`.

### PRIMARY: Directed grains (native+opal) - PROVISIONAL

Native emitters; a spray of tan grains and clods flung at the target and a dust puff on arrival.

*Why:* Directed-grains template.

* keep native emitters [2, 3, 0, 1]
* travel @ L+0 (+18f): NEW donor cell(s) Pokemon Emerald `smokescreen_impact.png` (12t); Pokemon Emerald `flying_dirt.png` (16t) x3 - OpalProjectile (3 lanes) - Emerald smokescreen_impact.png + flying_dirt.png
* reaction @ H+0 (+10f): installed `opal_b9_wind` / `puff` x2 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst, OpalProjectile; installed sheets opal_b9_wind; new sheet `opal_b9p_sand_attack` (28 tiles, <= 8 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +28 new OBJ tiles; peak 106t / 2 mgr / 14 OAM; ~58 GX quads, 2048 B tex; ~30f (+0 vs native lb).

### ALTERNATIVE 1: Dust only (opal_existing) - PROVISIONAL

Wind puff only.

*Why:* Zero new tiles.

* keep native emitters [2, 3, 0, 1]
* reaction @ H+0 (+10f): installed `opal_b9_wind` / `puff` x3 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 78t / 1 mgr / 12 OAM; ~58 GX quads, 2048 B tex; ~30f (+0 vs native lb).

### ALTERNATIVE 2: Smoke borrow (native+opal) - PROVISIONAL

Borrowed Smoke Screen / Sandstorm masks.

*Why:* Native-look dust.

* keep native emitters [2, 3, 0, 1]
* borrow @ H+0 (+47f): borrow Platinum `sandstorm.spa` emitters [0, 1] - dust puff + grain dots + haze masks (peak 97 quads, 10240 B tex)

*Compatibility:* macros -; installed sheets none; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 0t / 0 mgr / 0 OAM; ~155 GX quads, 12288 B tex; ~56f (+26 vs native lb). Notes: CADENCE: extends the native lower-bound duration by 26 frames (> 12); needs a payoff argument or a cut

## String Shot (P2, `status_bind`) - thread arc

Native: `string_shot` emitters [0], lower-bound duration 36f, hit beat H = 0 (budget 8); existing sprite resources: ['string_shot_NCGR_lz']. Script: `res/moves/string_shot/anim.s`.

### PRIMARY: Thread arc to wrap (native+opal) - PROVISIONAL

Native emitters + native string sprites; two thread arcs of different weight and a white wrap ring converging on the target.

*Why:* Status-bind template (thread arc).

* keep native emitters [0] (native emitter; native string sprites stay)
* travel @ L+0 (+20f): NEW donor cell(s) Pokemon Emerald `string.png` (16t); Pokemon Emerald `string_2.png` (40t) x2 - OpalProjectile (arc 12) - Emerald string.png + string_2.png
* reaction @ H+0 (+12f): installed `opal_fx_ring` [opal] / `flat_converge` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst, OpalProjectile; installed sheets opal_fx_ring; new sheet `opal_b9p_string_shot` (56 tiles, <= 5 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +56 new OBJ tiles; peak 240t / 2 mgr / 10 OAM; ~7 GX quads, 256 B tex; ~36f (+0 vs native lb).

### ALTERNATIVE 1: Strings only (native+donor) - PROVISIONAL

Thread arcs only.

*Why:* Cheaper.

* keep native emitters [0]
* travel @ L+0 (+20f): NEW donor cell(s) Pokemon Emerald `string.png` (16t); Pokemon Emerald `string_2.png` (40t) x2 - OpalProjectile

*Compatibility:* macros OpalProjectile; installed sheets none; new sheet `opal_b9p_string_shot` (56 tiles, <= 5 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +56 new OBJ tiles; peak 56t / 1 mgr / 6 OAM; ~7 GX quads, 256 B tex; ~36f (+0 vs native lb).

### ALTERNATIVE 2: Arc borrow (native+opal) - PROVISIONAL

Borrowed Aurora Beam arc masks as thread loops.

*Why:* Smoother arc.

* keep native emitters [0]
* borrow @ L+0 (+73f): borrow Platinum `aurora_beam.spa` emitters [0] - bright arc masks (peak 56 quads, 1024 B tex)
* reaction @ H+0 (+12f): installed `opal_fx_ring` [opal] / `flat_converge` x1 - OpalImpactBurst

*Compatibility:* macros OpalImpactBurst; installed sheets opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 184t / 1 mgr / 4 OAM; ~63 GX quads, 1280 B tex; ~73f (+37 vs native lb). Notes: CADENCE: extends the native lower-bound duration by 37 frames (> 12); needs a payoff argument or a cut

## Leech Seed (P2, `seed_bind`) - seed impact + vine strands

Native: `bullet_seed` emitters [0, 1, 2], lower-bound duration 74f, hit beat H = 10 (budget 10); existing sprite resources: none. Script: `res/moves/leech_seed/anim.s`.

### PRIMARY: Seed, vines, drain (native+opal) - PROVISIONAL

Native bullet-seed emitters; a green seed lobbed to the target, vine strands wrap it, and leaves flutter back to the user.

*Why:* Seed-bind template (seed impact + vine strands).

* keep native emitters [0, 1, 2]
* travel @ L+0 (+24f): NEW donor cell(s) Pokemon Emerald `seed_2.png` (1t) x1 - OpalProjectile (arc 10) - Emerald seed_2.png
* reaction @ H+0 (+24f): NEW donor cell(s) Pokemon Emerald `vine.png` (80t); Pokemon Emerald `vine_2.png` (80t) x2 - OpalImpactBurst (vine strands) - Emerald vine.png + vine_2.png
* aftermath @ H+6 (+24f): installed `opal_b9_nature` / `leaf_flutter` x3 - OpalResidual
* cue @ H+0: OpalReactMagic green

*Compatibility:* macros OpalImpactBurst, OpalProjectile, OpalReactMagic, OpalResidual; installed sheets opal_b9_nature; new sheet `opal_b9p_leech_seed` (161 tiles, <= 15 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +161 new OBJ tiles; peak 267t / 2 mgr / 23 OAM; ~9 GX quads, 1280 B tex; ~74f (+0 vs native lb).

### ALTERNATIVE 1: Nature only (opal_existing) - PROVISIONAL

Vine lash + flutter.

*Why:* Zero new tiles.

* keep native emitters [0, 1, 2]
* reaction @ H+0 (+14f): installed `opal_b9_nature` / `vine_lash` x2 - OpalImpactBurst
* aftermath @ H+6 (+24f): installed `opal_b9_nature` / `leaf_flutter` x3 - OpalResidual

*Compatibility:* macros OpalImpactBurst, OpalResidual; installed sheets opal_b9_nature; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 106t / 1 mgr / 20 OAM; ~9 GX quads, 1280 B tex; ~74f (+0 vs native lb).

### ALTERNATIVE 2: Whip borrow (native+donor) - PROVISIONAL

Borrowed Vine Whip crescents + seed.

*Why:* Whip-like vines.

* keep native emitters [0, 1, 2]
* travel @ L+0 (+24f): NEW donor cell(s) Pokemon Emerald `seed_2.png` (1t) x1 - OpalProjectile
* borrow @ H+0 (+45f): borrow Platinum `vine_whip.spa` emitters [0, 1, 2] - burst + crescent masks (peak 14 quads, 9216 B tex)

*Compatibility:* macros OpalProjectile; installed sheets none; new sheet `opal_b9p_leech_seed` (1 tiles, <= 7 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +1 new OBJ tiles; peak 1t / 1 mgr / 1 OAM; ~23 GX quads, 10496 B tex; ~74f (+0 vs native lb).

## Supersonic (P2, `status_sound`) - resonant sound waves

Native: `supersonic` emitters [0], lower-bound duration 57f, hit beat H = 0 (budget 8); existing sprite resources: none. Script: `res/moves/supersonic/anim.s`.

### PRIMARY: Resonant rings (native+opal) - PROVISIONAL

Native arc emitter; three expanding steel-blue rings and installed sound arcs sweep to the target.

*Why:* Status-sound template (pulsing sound rings).

* keep native emitters [0]
* travel @ L+0 (+30f): installed `opal_fx_ring` [steel] / `ring_expand` x3 - OpalProjectile (3 rings)
* travel @ L+4 (+30f): installed `opal_b9_sense` / `sound_arc` x3 - OpalProjectile
* cue @ H+0: OpalReactMagic blue

*Compatibility:* macros OpalProjectile, OpalReactMagic; installed sheets opal_b9_sense, opal_fx_ring; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 312t / 2 mgr / 24 OAM; ~20 GX quads, 1024 B tex; ~57f (+0 vs native lb).

### ALTERNATIVE 1: Arcs only (opal_existing) - PROVISIONAL

Sound arcs only.

*Why:* Zero new tiles.

* keep native emitters [0]
* travel @ L+0 (+30f): installed `opal_b9_sense` / `sound_arc` x3 - OpalProjectile

*Compatibility:* macros OpalProjectile; installed sheets opal_b9_sense; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 128t / 1 mgr / 12 OAM; ~20 GX quads, 1024 B tex; ~57f (+0 vs native lb).

### ALTERNATIVE 2: Cyan rings (native+donor) - PROVISIONAL

Ranger 2 cyan bubble rings.

*Why:* Brighter rings.

* keep native emitters [0]
* travel @ L+0 (+30f): NEW donor cell(s) Pokemon Ranger: Shadows of Almia `e037_LZ.bin#4` (80t) x3 - OpalProjectile
* cue @ H+0: OpalReactMagic blue

*Compatibility:* macros OpalProjectile, OpalReactMagic; installed sheets none; new sheet `opal_b9p_supersonic` (80 tiles, <= 3 colours); runtime palette dependency: none; decode: HIGH.
*Cost (static estimate):* +80 new OBJ tiles; peak 80t / 1 mgr / 3 OAM; ~20 GX quads, 1024 B tex; ~57f (+0 vs native lb).

## Double Team (P2, `evasion`) - echo silhouettes

Native: `no particle archive` emitters [], lower-bound duration 50f, hit beat H = 25 (budget 25); existing sprite resources: none. Script: `res/moves/double_team/anim.s`.

### PRIMARY: Echo afterimages (custom composite) (custom_composite) - PROVISIONAL

The native script already spawns real battler-sprite copies; keep it and add staggered tinted afterimages, speed dust at the feet, ground shadows and shimmer pulses.

*Why:* Evasion template (echo silhouettes). Composite built on the battler copies the engine already draws.

* keep native emitters [] (native script: 4 attacker sprite copies + 1 partner copy, Func_DoubleTeam sway, blink)
* DESIGN NOTE - Afterimages: The silhouettes are the battler itself (no art to find): tint each sprite copy with Func_FadeBattlerSprite at staggered white/cyan alpha. VERIFY at runtime that Func_FadeBattlerSprite accepts BATTLE_ANIM_MON_SPRITE_n copies (not proven by source reading).
* launch @ L+0 (+10f): installed `opal_b9_wind` / `puff` x5 - OpalFx (feet dust)
* launch @ L+0 (+40f): NEW donor cell(s) Pokemon Emerald `white_shadow.png` (32t) x5 - OpalFx (ground ellipses under each copy) - Emerald white_shadow.png
* cue @ L+0: OpalLightPulse white
* cue @ L+36: OpalLightPulse white

*Compatibility:* macros OpalFx, OpalLightPulse; installed sheets opal_b9_wind; new sheet `opal_b9p_double_team` (32 tiles, <= 3 colours); runtime palette dependency: none; decode: EXACT_INDEXED_PNG.
*Cost (static estimate):* +32 new OBJ tiles; peak 110t / 2 mgr / 30 OAM; ~0 GX quads, 0 B tex; ~50f (+0 vs native lb).

### ALTERNATIVE 1: Dust and pulse (opal_existing) - PROVISIONAL

Wind dust + light pulses only.

*Why:* Zero new tiles.

* keep native emitters []
* launch @ L+0 (+10f): installed `opal_b9_wind` / `puff` x5 - OpalFx
* cue @ L+0: OpalLightPulse white

*Compatibility:* macros OpalFx, OpalLightPulse; installed sheets opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 78t / 1 mgr / 20 OAM; ~0 GX quads, 0 B tex; ~50f (+0 vs native lb).

### ALTERNATIVE 2: Agility streaks (native+opal) - PROVISIONAL

Borrowed Agility soft streak masks as speed trails.

*Why:* Streakier.

* keep native emitters []
* borrow @ L+0 (+97f): borrow Platinum `agility.spa` emitters [0, 1] - soft streak masks (peak 144 quads, 1280 B tex)
* launch @ L+0 (+10f): installed `opal_b9_wind` / `puff` x5 - OpalFx

*Compatibility:* macros OpalFx; installed sheets opal_b9_wind; no new sheet; runtime palette dependency: none; decode: n/a (no new donor art).
*Cost (static estimate):* +0 new OBJ tiles; peak 78t / 1 mgr / 20 OAM; ~144 GX quads, 1280 B tex; ~97f (+47 vs native lb). Notes: CADENCE: extends the native lower-bound duration by 47 frames (> 12); needs a payoff argument or a cut

