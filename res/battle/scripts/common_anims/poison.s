#include "macros/btlanimcmd.inc"

// Opal B5 STATUS_APPLY (poison / toxic): two rising violet motes beside the native poison emitter.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_ghost)

.data

L_0:
    LoadParticleResource 0, 27
    OpalSheetBegin 1, 4, RING
    PlayLoopedSoundEffect SEQ_SE_DP_W092D, BATTLE_SOUND_PAN_LEFT, 3, 3
    CreateEmitter 0, 7, EMITTER_CB_SET_POS_TO_ATTACKER
    OpalResidual 1, RING, OPAL_RING_SEQ_DOT_PULSE, BATTLE_ANIM_ATTACKER, 26, 80, -12, 6
    OpalResidual 1, RING, OPAL_RING_SEQ_DOT_PULSE, BATTLE_ANIM_ATTACKER, 26, 60, 12, 12
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 1, BATTLE_COLOR_PURPLE, 10, 0
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
