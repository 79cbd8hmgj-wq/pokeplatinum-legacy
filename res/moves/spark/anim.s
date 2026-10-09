#include "macros/btlanimcmd.inc"

// AV1: after the lunge, a discharge arc fans out from the impact point.
// Impact arc reuses discharge.spa defender emitter 1.
L_0:
    LoadParticleResource 0, spark_spa
    LoadParticleResource 1, discharge_spa
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_ATTACKER
    PlaySoundEffectL SEQ_SE_DP_W209
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 1, 1, BATTLE_COLOR_LIGHT_YELLOW1, 10, 
    BeginLoop 3
    Func_FadeBg FADE_BG_TYPE_BASE, 0, 0, 8, BATTLE_COLOR_LIGHT_YELLOW1
    WaitForAnimTasks
    Func_FadeBg FADE_BG_TYPE_BASE, 0, 8, 0, BATTLE_COLOR_LIGHT_YELLOW1
    WaitForAnimTasks
    EndLoop
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 1, 1, BATTLE_COLOR_LIGHT_YELLOW1, 10, 
    Delay 5
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 1, 0, 1, 6, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_W086
    Delay 1
    Func_MoveBattlerX2 3, 24, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    Delay 5
    Func_MoveBattlerX2 3, -24, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    CreateEmitter 1, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBg FADE_BG_TYPE_BASE, 0, 0, 6, BATTLE_COLOR_LIGHT_YELLOW2
    WaitForAnimTasks
    Func_FadeBg FADE_BG_TYPE_BASE, 0, 6, 0, BATTLE_COLOR_LIGHT_YELLOW2
    WaitForAnimTasks
    WaitForAllEmitters
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    End
