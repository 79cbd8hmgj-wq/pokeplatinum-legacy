#include "macros/btlanimcmd.inc"

// Opal B5 STATUS_APPLY (freeze): ice glints pop around the battler with the native frost emitter.
#define ICE OPAL_RES(opal_ice, opal_ice)

.data

L_0:
    LoadParticleResource 0, 27
    OpalSheetBegin 1, 4, ICE
    PlayLoopedSoundEffect SEQ_SE_DP_W258, BATTLE_SOUND_PAN_LEFT, 8, 2
    CreateEmitter 0, 6, EMITTER_CB_SET_POS_TO_ATTACKER
    OpalImpactBurst 1, ICE, OPAL_ICE_SEQ_GLINT, BATTLE_ANIM_ATTACKER, 150, -14, -14, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 1, ICE, OPAL_ICE_SEQ_GLINT, BATTLE_ANIM_ATTACKER, 120, 14, 4, 0, OPAL_FX_FLAG_TRANSLUCENT | OPAL_FX_FLAG_MIRROR
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
