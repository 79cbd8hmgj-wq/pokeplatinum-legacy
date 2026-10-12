// Opal cinematic cue vocabulary (B2-B8). Presentation only.
//
// Every cue below expands to existing animation commands (Func_FadeBg, Func_Shake, AddSpriteWithFunc, ...)
// plus the Opal C hooks in src/battle_anim/opal_cinematic.c.  Nothing here reads or writes battle state:
// a move script runs only after the engine has decided the move executes, and the animation system
// resolves battlers (attacker / defender / partners / "not attacker") itself, so a cue can never appear on a
// battler the engine did not resolve.
//
// Lifecycle contract (checked by tools/visual_overhaul/validate_opal_cue_balance.py on every path):
//   OpalSheetBegin   <-> OpalSheetEnd        (sprite manager, always before UnloadParticleSystem)
//   OpalDimIn        <-> OpalDimOut          (base BG fade, restored to alpha 0)
//   Func_OpalCamera                           (self-restoring; never overlaps)
//   OpalWeatherAccent -> OpalWeatherAccentEnd (manager 1)
//
// Tunables (pixels / frames) are the only values to adjust after emulator review.

// Resource bundle: sheet -> CHAR, PLTT, CELL, ANIM resource ids (cpp pastes the generated NAIX names)
#define OPAL_RES(sheet, pal) sheet##_NCGR_lz, pal##_NCLR, sheet##_cell_NCER_lz, sheet##_anim_NANR_lz

// Sequence indices of each sheet (must match tools/visual_overhaul/opal_fx/recipes/*.json)
#define OPAL_THUNDER_SEQ_BOLT       0
#define OPAL_THUNDER_SEQ_SPARKS     1
#define OPAL_THUNDER_SEQ_ORB        2
#define OPAL_THUNDER_SEQ_BOLT_FADE  3
#define OPAL_GHOST_SEQ_ORB          0
#define OPAL_GHOST_SEQ_WISP         1
#define OPAL_WATER_SEQ_COLUMN       0
#define OPAL_WATER_SEQ_DROPLET      1
#define OPAL_WATER_SEQ_FOAM         2
#define OPAL_FIRE_SEQ_PLUME         0
#define OPAL_FIRE_SEQ_TONGUE        1
#define OPAL_ICE_SEQ_SHATTER        0
#define OPAL_ICE_SEQ_GLINT          1
#define OPAL_RING_SEQ_EXPAND        0
#define OPAL_RING_SEQ_CONVERGE      1
#define OPAL_RING_SEQ_FLAT_EXPAND   2
#define OPAL_RING_SEQ_FLAT_CONVERGE 3
#define OPAL_RING_SEQ_STAR_POP      4
#define OPAL_RING_SEQ_DOT_PULSE     5
#define OPAL_WX_SEQ_FLAT_EXPAND     0
#define OPAL_WX_SEQ_STAR_POP        1

// B9 (everyday moves) sheets; indices must match tools/visual_overhaul/opal_b9/make_b9_recipes.py
#define OPAL_B9_STRIKE_SEQ_HIT_SMALL   0
#define OPAL_B9_STRIKE_SEQ_STAR        1
#define OPAL_B9_STRIKE_SEQ_CLAW_A      2
#define OPAL_B9_STRIKE_SEQ_CLAW_B      3
#define OPAL_B9_STRIKE_SEQ_JAW_UPPER   4
#define OPAL_B9_STRIKE_SEQ_JAW_LOWER   5
#define OPAL_B9_STRIKE_SEQ_STREAK      6
#define OPAL_B9_EMBER_SEQ_EMBER        0
#define OPAL_B9_EMBER_SEQ_SPARK_ARC    1
#define OPAL_B9_EMBER_SEQ_EMBER_POP    2
#define OPAL_B9_NATURE_SEQ_LEAF_SPIN   0
#define OPAL_B9_NATURE_SEQ_RAZOR       1
#define OPAL_B9_NATURE_SEQ_VINE_LASH   2
#define OPAL_B9_NATURE_SEQ_FLUTTER     3
#define OPAL_B9_WIND_SEQ_STREAK        0
#define OPAL_B9_WIND_SEQ_CRESCENT      1
#define OPAL_B9_WIND_SEQ_SWIRL         2
#define OPAL_B9_WIND_SEQ_PUFF          3
#define OPAL_B9_WIND_SEQ_FLECKS        4
#define OPAL_B9_WIND_SEQ_STREAK_FLIP   5
#define OPAL_B9_ROCK_SEQ_BOULDER       0
#define OPAL_B9_ROCK_SEQ_BREAK         1
#define OPAL_B9_ROCK_SEQ_SHARDS        2
#define OPAL_B9_ROCK_SEQ_DIRT          3
#define OPAL_B9_BUBBLE_SEQ_BUBBLE      0
#define OPAL_B9_BUBBLE_SEQ_SMALL       1
#define OPAL_B9_BUBBLE_SEQ_POP         2
#define OPAL_B9_BUBBLE_SEQ_POP_BIG     3
#define OPAL_B9_SENSE_SEQ_GLINT        0
#define OPAL_B9_SENSE_SEQ_SOUND_ARC    1
#define OPAL_B9_SENSE_SEQ_ROAR_JAG     2

// Camera tunables (B3)
#define OPAL_CAM_FOCUS_DX   (-3)
#define OPAL_CAM_FOCUS_DY   1
#define OPAL_CAM_FOLLOW_DX  6
#define OPAL_CAM_PUNCH_DX   3
#define OPAL_CAM_PUNCH_DY   2
#define OPAL_CAM_HEAVY_DX   4
#define OPAL_CAM_HEAVY_DY   3

// Light tunables (B4). With OPAL_LOW_FLASH the white pulses become pale tints at half strength.
#define OPAL_LIGHT_PULSE_MAX 8
#if OPAL_LOW_FLASH
#define OPAL_LIGHT_PEAK(level) ((level) / 2)
#else
#define OPAL_LIGHT_PEAK(level) (level)
#endif

// ---------------------------------------------------------------------------------------------
// B2: sheet lifecycle
// ---------------------------------------------------------------------------------------------

// Loads one Opal FX sheet into a sprite manager. Use at most two managers at a time (move sheet + ring/weather).
// maxSprites must cover the worst-case number of concurrently live sprites (a spread cue can spawn up to 4).
    .macro OpalSheetBegin mgr:req, maxSprites:req, char:req, pltt:req, cell:req, animres:req
    InitSpriteManager \mgr, \maxSprites, 1, 1, 1, 1, 0, 0
    LoadCharResObj \mgr, \char
    LoadPlttRes \mgr, \pltt, 1
    LoadCellResObj \mgr, \cell
    LoadAnimResObj \mgr, \animres
    .endm

// Waits for every FX sprite task to finish (each has a hard lifetime cap) and frees the manager.
    .macro OpalSheetEnd mgr:req
    WaitForAnimTasks
    FreeSpriteManager \mgr
    .endm

// Generic FX sprite. anchor/dest are BATTLE_ANIM_* masks resolved by the animation system.
// dest = 0 -> static burst on each resolved anchor; dest != 0 -> travel from the first anchor to each resolved dest.
    .macro OpalFx mgr:req, char:req, pltt:req, cell:req, animres:req, seq:req, anchor:req, dest:req, frames:req, ox:req, oy:req, dox:req, doy:req, arc:req, scale:req, flags:req
    AddSpriteWithFunc \mgr, SPRITE_FUNC_OPAL_FX, \char, \pltt, \cell, \animres, 0, 0, \anchor, \dest, \frames, \ox, \oy, \dox, \doy, \arc, \scale, (OPAL_FX_ANIM(\seq) | (\flags))
    .endm

// CHARGE_AURA: translucent pop-in effect around the attacker side
    .macro OpalChargeAura mgr:req, char:req, pltt:req, cell:req, animres:req, seq:req, frames:req, scale=100, anchor=BATTLE_ANIM_ATTACKER, ox=0, oy=0
    OpalFx \mgr, \char, \pltt, \cell, \animres, \seq, \anchor, 0, \frames, \ox, \oy, 0, 0, 0, \scale, (OPAL_FX_FLAG_TRANSLUCENT | OPAL_FX_FLAG_POP | OPAL_FX_FLAG_SHRINK_OUT)
    .endm

// PROJECTILE_TRAIL: lead sprite plus two lagging afterimages travelling attacker -> every resolved defender
    .macro OpalProjectile mgr:req, char:req, pltt:req, cell:req, animres:req, seq:req, frames:req, scale=100, arc=0, flags=0, sox=0, soy=0, dox=0, doy=0
    OpalFx \mgr, \char, \pltt, \cell, \animres, \seq, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, \frames, \sox, \soy, \dox, \doy, \arc, \scale, (OPAL_FX_FLAG_TRAIL | \flags)
    .endm

// IMPACT_BURST: pop-in burst on every battler the engine resolved for `targets`
    .macro OpalImpactBurst mgr:req, char:req, pltt:req, cell:req, animres:req, seq:req, targets=BATTLE_ANIM_DEFENDER, scale=100, ox=0, oy=0, frames=0, flags=0
    OpalFx \mgr, \char, \pltt, \cell, \animres, \seq, \targets, 0, \frames, \ox, \oy, 0, 0, 0, \scale, (OPAL_FX_FLAG_POP | \flags)
    .endm

// RESIDUAL_PARTICLES: small drifting, shrinking, translucent particles left after an impact
    .macro OpalResidual mgr:req, char:req, pltt:req, cell:req, animres:req, seq:req, targets=BATTLE_ANIM_DEFENDER, frames=24, scale=100, ox=0, oy=0
    OpalFx \mgr, \char, \pltt, \cell, \animres, \seq, \targets, 0, \frames, \ox, \oy, 0, 0, 0, \scale, (OPAL_FX_FLAG_TRANSLUCENT | OPAL_FX_FLAG_DRIFT_UP | OPAL_FX_FLAG_SHRINK_OUT)
    .endm

// ---------------------------------------------------------------------------------------------
// B3: camera cues (battle backdrop only; HUD / sprites / touch screen never move)
// ---------------------------------------------------------------------------------------------

// FOCUS_ATTACKER: 14-frame ease of the backdrop against the attacker's facing at charge start
    .macro OpalCamFocusAttacker
    Func_OpalCamera OPAL_CAM_MODE_PAN, OPAL_CAM_FOCUS_DX, OPAL_CAM_FOCUS_DY, 6, 2, 6
    .endm

// FOLLOW_PROJECTILE: slow backdrop slide toward the defender, `frames` long in total (ease-in = frames - 6, 6-frame return)
    .macro OpalCamFollow frames:req
    Func_OpalCamera OPAL_CAM_MODE_PAN, OPAL_CAM_FOLLOW_DX, 0, (\frames) - 6, 0, 6
    .endm

// IMPACT_PUNCH: one decaying 6-frame shake on confirmed contact (the animation only runs when the move hit)
    .macro OpalCamPunch
    Func_OpalCamera OPAL_CAM_MODE_PUNCH, OPAL_CAM_PUNCH_DX, OPAL_CAM_PUNCH_DY, 6, 0, 1
    .endm

    .macro OpalCamPunchHeavy
    Func_OpalCamera OPAL_CAM_MODE_PUNCH, OPAL_CAM_HEAVY_DX, OPAL_CAM_HEAVY_DY, 8, 0, 1
    .endm

// ---------------------------------------------------------------------------------------------
// B4: light cues (base battle backdrop only; healthboxes / text / mons untouched)
// ---------------------------------------------------------------------------------------------

// BATTLE_DIM: darken the stage behind the sprites. Always pair with OpalDimOut.
    .macro OpalDimIn color=BATTLE_COLOR_BLACK, level=8, step=1
    Func_FadeBg FADE_BG_TYPE_BASE, \step, 0, OPAL_LIGHT_PEAK(\level), \color
    .endm

    .macro OpalDimOut color=BATTLE_COLOR_BLACK, level=8, step=1
    Func_FadeBg FADE_BG_TYPE_BASE, \step, OPAL_LIGHT_PEAK(\level), 0, \color
    .endm

// LIGHT_PULSE: short burst tint of the backdrop that decays back to the original palette (restores itself)
    .macro OpalLightPulse color:req, peak=6
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, OPAL_LIGHT_PEAK(\peak), \color
    Delay OPAL_LIGHT_PEAK(\peak) + 1
    Func_FadeBg FADE_BG_TYPE_BASE, 2, OPAL_LIGHT_PEAK(\peak), 0, \color
    .endm

// ---------------------------------------------------------------------------------------------
// B4: weather accents. Reads the existing weather state through JumpIfWeather; draws a brief accent
// on the resolved target(s), then OpalWeatherAccentEnd frees its sprite manager. Nothing persists between moves.
// The accent owns the sprite manager `mgr` passed to OpalWeatherAccentSub / OpalWeatherAccentEnd (use one that the
// move script does not use for anything else).
// ---------------------------------------------------------------------------------------------
    .macro OpalWeatherAccent
    Call Opal_WeatherAccentSub
    .endm

    .macro OpalWeatherAccentEnd mgr:req
    WaitForAnimTasks
    FreeSpriteManager \mgr
    .endm

// Emits the accent subroutine. Place after the script's final End.
    .macro OpalWeatherAccentSub mgr:req, targets=BATTLE_ANIM_DEFENDER
Opal_WeatherAccentSub:
    JumpIfWeather Opal_WxNone, Opal_WxRain, Opal_WxSand, Opal_WxSun, Opal_WxHail

Opal_WxNone:
    Return

Opal_WxRain:
    OpalSheetBegin \mgr, 4, OPAL_RES(opal_fx_wx, opal_fx_wx_water)
    OpalImpactBurst \mgr, OPAL_RES(opal_fx_wx, opal_fx_wx_water), OPAL_WX_SEQ_FLAT_EXPAND, \targets, 100, 0, 22, 0, OPAL_FX_FLAG_TRANSLUCENT
    Return

Opal_WxSand:
    OpalSheetBegin \mgr, 4, OPAL_RES(opal_fx_wx, opal_fx_wx_earth)
    OpalImpactBurst \mgr, OPAL_RES(opal_fx_wx, opal_fx_wx_earth), OPAL_WX_SEQ_FLAT_EXPAND, \targets, 130, 0, 22, 0, OPAL_FX_FLAG_TRANSLUCENT
    Return

Opal_WxSun:
    OpalSheetBegin \mgr, 4, OPAL_RES(opal_fx_wx, opal_fx_wx_gold)
    OpalResidual \mgr, OPAL_RES(opal_fx_wx, opal_fx_wx_gold), OPAL_WX_SEQ_STAR_POP, \targets, 20, 100, -10, -12
    Return

Opal_WxHail:
    OpalSheetBegin \mgr, 4, OPAL_RES(opal_fx_wx, opal_fx_wx_ice)
    OpalResidual \mgr, OPAL_RES(opal_fx_wx, opal_fx_wx_ice), OPAL_WX_SEQ_STAR_POP, \targets, 20, 100, 10, -14
    Return
    .endm

// ---------------------------------------------------------------------------------------------
// B5: battler reactions. `role` is a BATTLE_ANIM_* battler role (DEFENDER, ATTACKER, ...). The move/common-animation
// script only runs after the engine confirmed the outcome: a missed, immune, Protect-blocked or failed move never reaches
// its animation, status animations run only from the status-application path, and multi-hit moves replay the script once per
// real hit. The animation system resolves `role` to the live battler sprite (Substitute draws on its own sprite).
// ---------------------------------------------------------------------------------------------

// REACT_LIGHT: 2-pixel recoil and one brief white flash
    .macro OpalReactLight role=BATTLE_ANIM_DEFENDER
    Func_Shake 1, 0, 1, 2, (\role) | BATTLE_ANIM_BATTLER_SPRITES
    Func_FadeBattlerSprite \role, 0, 1, BATTLE_COLOR_WHITE, 6, 0
    .endm

// REACT_HEAVY: stronger 3-pixel recoil, brighter flash, impact ring on the battler plane and a camera punch
    .macro OpalReactHeavy mgr:req, char:req, pltt:req, cell:req, animres:req, role=BATTLE_ANIM_DEFENDER
    Func_Shake 3, 0, 1, 4, (\role) | BATTLE_ANIM_BATTLER_SPRITES
    Func_FadeBattlerSprite \role, 0, 1, BATTLE_COLOR_WHITE, 10, 0
    OpalImpactBurst \mgr, \char, \pltt, \cell, \animres, OPAL_RING_SEQ_EXPAND, \role, 140, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalCamPunchHeavy
    .endm

// REACT_MAGIC: tinted pulse on the battler, no recoil (special hits flow through the body)
    .macro OpalReactMagic color:req, role=BATTLE_ANIM_DEFENDER
    Func_FadeBattlerSprite \role, 0, 2, \color, 8, 2
    .endm
