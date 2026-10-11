#include "macros/btlanimcmd.inc"

// Opal B4 WEATHER_ACCENT (hail): icy flecks pop around every battler. One-shot, bounded, freed here.
#define RING OPAL_RES(opal_fx_wx, opal_fx_wx_ice)

.data

L_0:
    LoadParticleResource 0, 275
    OpalSheetBegin 1, 8, RING
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 10, BATTLE_COLOR_LIGHT_BLUE
    WaitForAnimTasks
    PlayLoopedSoundEffect SEQ_SE_DP_W258, 0, 3, 7
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_ATTACKER
    OpalResidual 1, RING, OPAL_WX_SEQ_STAR_POP, BATTLE_ANIM_ALL_BATTLERS, 22, 90, 10, -14
    Delay 12
    OpalResidual 1, RING, OPAL_WX_SEQ_STAR_POP, BATTLE_ANIM_ALL_BATTLERS, 22, 70, -10, -4
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 10, 0, BATTLE_COLOR_LIGHT_BLUE
    WaitForAnimTasks
    End
