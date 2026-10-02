#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, hail_spa
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 10, BATTLE_COLOR_LIGHT_BLUE
    WaitForAnimTasks
    PlayLoopedSoundEffectC SEQ_SE_DP_W258, 3, 9
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    WaitForAllEmitters
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 10, 0, BATTLE_COLOR_LIGHT_BLUE
    WaitForAnimTasks
    End
