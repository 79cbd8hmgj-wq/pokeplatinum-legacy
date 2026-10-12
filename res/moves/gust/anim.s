#include "macros/btlanimcmd.inc"

// Opal B9 (P0, air_gust): three wind streaks and a crescent sweep from the user across the target (launched inside the native 5-frame
// lead-in), a translucent swirl on the target as the native gale lands, and leaf debris carried off it. Native emitters, camera
// projection, sound and the 15-frame defender flutter are untouched; no extra delay.
// Donors: pokeemerald air_wave / air_wave_2 / whirlwind (opal_b9_wind), leaf (opal_b9_nature).
#define WIND OPAL_RES(opal_b9_wind, opal_b9_wind)
#define NATURE OPAL_RES(opal_b9_nature, opal_b9_nature)

L_0:
    LoadParticleResource 0, gust_spa
    OpalSheetBegin 1, 8, WIND
    OpalSheetBegin 2, 4, NATURE
    SetCameraProjection 0, 0
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 8
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 8
    OpalFx 1, WIND, OPAL_B9_WIND_SEQ_STREAK, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 18, 14, -8, -2, -12, 0, 100, 0
    Delay 2
    OpalFx 1, WIND, OPAL_B9_WIND_SEQ_STREAK, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 18, 14, 6, 0, 4, 0, 110, 0
    Delay 2
    OpalFx 1, WIND, OPAL_B9_WIND_SEQ_CRESCENT, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 18, 14, 0, 0, 14, 0, 100, 0
    Delay 1
    PlaySoundEffectR SEQ_SE_DP_W239
    Delay 15
    OpalImpactBurst 1, WIND, OPAL_B9_WIND_SEQ_SWIRL, BATTLE_ANIM_DEFENDER, 100, 0, -4, 22, OPAL_FX_FLAG_TRANSLUCENT
    OpalResidual 2, NATURE, OPAL_B9_NATURE_SEQ_FLUTTER, BATTLE_ANIM_DEFENDER, 24, 100, -6, -4
    OpalResidual 2, NATURE, OPAL_B9_NATURE_SEQ_FLUTTER, BATTLE_ANIM_DEFENDER, 20, 80, 10, 2
    Func_Shake 3, 0, 1, 15, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    WaitForAnimTasks
    End
