#include "macros/btlanimcmd.inc"

// Opal B4 WEATHER_ACCENT (rain): ripples at every battler's feet while the native rain falls. One-shot, bounded, freed here.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_water)

.data

L_0:
    OpalSheetBegin 1, 6, RING
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_DARK_BLUE
    LoadParticleResource 0, 257
    CreateEmitter 0, 0, EMITTER_CB_NONE
    PlayPannedSoundEffect SEQ_SE_DP_W240, 0
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ALL_BATTLERS, 100, 0, 22, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 14
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ALL_BATTLERS, 70, 8, 24, 0, OPAL_FX_FLAG_TRANSLUCENT
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_DARK_BLUE
    WaitForAnimTasks
    End
