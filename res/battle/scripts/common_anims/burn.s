#include "macros/btlanimcmd.inc"

// Opal B5 STATUS_APPLY (burn): ember flare layered on the native flame emitter; same wait structure as before.
// Played only from subscript_burn.s after every immunity / Safeguard / ability check passed (and from the native burn damage tick).
#define FIRE OPAL_RES(opal_fire, opal_fire)

.data

L_0:
    LoadParticleResource 0, 27
    OpalSheetBegin 1, 4, FIRE
    PlayPannedSoundEffect SEQ_SE_DP_W172, BATTLE_SOUND_PAN_LEFT
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_ATTACKER
    OpalImpactBurst 1, FIRE, OPAL_FIRE_SEQ_PLUME, BATTLE_ANIM_ATTACKER, 60, 0, 6, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 1, BATTLE_COLOR_RED, 10, 0
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
