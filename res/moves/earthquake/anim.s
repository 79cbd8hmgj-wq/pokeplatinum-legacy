#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, earthquake_spa
    Func_Earthquake 0
    Func_ShakeBg 4, 3, 0, 5, 0, SHAKE_BG_TARGET_BASE
    Delay 2
    PlaySoundEffectC SEQ_SE_DP_W089
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    WaitForAnimTasks
    WaitForAllEmitters
    UnloadParticleSystem 0
    End
