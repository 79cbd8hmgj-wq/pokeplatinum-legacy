#include "macros/btlanimcmd.inc"

.data

L_0:
    LoadParticleResource 0, 219
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 8, BATTLE_COLOR_DARK_YELLOW
    CreateEmitter 0, 0, EMITTER_CB_NONE
    CreateEmitter 0, 1, EMITTER_CB_NONE
    PlayPannedSoundEffect SEQ_SE_DP_W201, 0
    WaitForAllEmitters
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 8, 0, BATTLE_COLOR_DARK_YELLOW
    WaitForAnimTasks
    End
