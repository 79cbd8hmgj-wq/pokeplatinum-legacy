#include "macros/btlanimcmd.inc"

// Opal B4 WEATHER_ACCENT (harsh sunlight): gold shimmer stars rise from every battler. One-shot, bounded, freed here.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_gold)

.data

L_0:
    LoadParticleResource 0, 258
    OpalSheetBegin 1, 8, RING
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_LIGHT_YELLOW1
    CreateEmitter 0, 1, EMITTER_CB_NONE
    CreateEmitter 0, 2, EMITTER_CB_NONE
    CreateEmitter 0, 0, EMITTER_CB_NONE
    PlayPannedSoundEffect SEQ_SE_DP_W080, 0
    OpalResidual 1, RING, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_ALL_BATTLERS, 22, 100, -12, -14
    Delay 12
    OpalResidual 1, RING, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_ALL_BATTLERS, 22, 80, 12, -6
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_LIGHT_YELLOW1
    WaitForAnimTasks
    End
