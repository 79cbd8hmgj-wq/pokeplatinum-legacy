#include "macros/btlanimcmd.inc"

// Opal B4 WEATHER_ACCENT (sandstorm): dust haze rings at every battler's feet. One-shot, bounded, freed here.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_earth)

.data

L_0:
    LoadParticleResource 0, 219
    OpalSheetBegin 1, 6, RING
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 8, BATTLE_COLOR_DARK_YELLOW
    CreateEmitter 0, 0, EMITTER_CB_NONE
    CreateEmitter 0, 1, EMITTER_CB_NONE
    PlayPannedSoundEffect SEQ_SE_DP_W201, 0
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ALL_BATTLERS, 130, 0, 22, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 14
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ALL_BATTLERS, 90, -6, 24, 0, OPAL_FX_FLAG_TRANSLUCENT
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 8, 0, BATTLE_COLOR_DARK_YELLOW
    WaitForAnimTasks
    End
