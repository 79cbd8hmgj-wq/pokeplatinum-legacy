#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, razor_wind_spa
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER_SIDE
    PlayDelayedSoundEffectR SEQ_SE_DP_146, 5
    Delay 10
    Func_Shake 3, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 3, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    WaitForAllEmitters
    UnloadParticleSystem 0
    End
