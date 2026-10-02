#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, wood_hammer_spa
    PlaySoundEffectR SEQ_SE_DP_W452
    CreateEmitter 0, 4, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 2, 0, 1, 6, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_ShakeBg 0, 5, 1, 5, 0
    Func_ShakeBg 2, 3, 0, 3, 0, SHAKE_BG_TARGET_BASE
    WaitForAllEmitters
    UnloadParticleSystem 0
    End
