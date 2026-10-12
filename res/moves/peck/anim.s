#include "macros/btlanimcmd.inc"

// Opal B9 (P0, pierce_contact): a thin thrust streak runs beak-to-target during the native head-tilt, then a sharp eight-point
// pierce flash and a light reaction land with the native emitters. Native rotation, emitters, sound and timing unchanged.
// Donors: pokeemerald air_wave (opal_b9_wind), impact (opal_b9_strike star).
#define STRIKE OPAL_RES(opal_b9_strike, opal_b9_strike)
#define WIND OPAL_RES(opal_b9_wind, opal_b9_wind)

L_0:
    LoadParticleResource 0, peck_spa
    OpalSheetBegin 1, 2, STRIKE
    OpalSheetBegin 2, 2, WIND
    Func_RotateMon DEG_TO_IDX(360), DEG_TO_IDX(350), 2
    OpalFx 2, WIND, OPAL_B9_WIND_SEQ_STREAK, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 4, 10, -4, 0, -2, 0, 70, 0
    Delay 2
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_W030
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_STAR, BATTLE_ANIM_DEFENDER, 110, 0, 0, 10, OPAL_FX_FLAG_TRANSLUCENT
    OpalReactLight BATTLE_ANIM_DEFENDER
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    WaitForAnimTasks
    End
