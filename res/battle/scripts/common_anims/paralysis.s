#include "macros/btlanimcmd.inc"

// Opal B5 STATUS_APPLY (paralysis): a spark burst over the battler on top of the native spark emitter.
#define THUNDER OPAL_RES(opal_thunder, opal_thunder)

.data

L_0:
    LoadParticleResource 0, 114
    OpalSheetBegin 1, 4, THUNDER
    PlayPannedSoundEffect SEQ_SE_DP_W085C, BATTLE_SOUND_PAN_LEFT
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 1, BATTLE_COLOR_BLACK, 15, 0
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_ATTACKER
    OpalImpactBurst 1, THUNDER, OPAL_THUNDER_SEQ_SPARKS, BATTLE_ANIM_ATTACKER, 150, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
