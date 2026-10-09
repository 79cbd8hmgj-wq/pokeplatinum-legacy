#include "macros/btlanimcmd.inc"

// AV1: branching secondary arcs and a layered defender flash accent.
// Branching arcs reuse thunderbolt.spa defender emitters 0, 1 and 3.
L_0:
    LoadParticleResource 0, thunder_shock_spa
    LoadParticleResource 1, thunderbolt_spa
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    PlaySoundEffectR SEQ_SE_DP_W085
    PlayDelayedSoundEffectR SEQ_SE_DP_W063B, 13
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Delay 5
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_BLACK, 15, 0
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Delay 4
    CreateEmitter 1, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_LIGHT_YELLOW1, 12, 0
    Delay 5
    CreateEmitter 1, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Delay 5
    CreateEmitter 1, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_LIGHT_YELLOW2, 8, 6
    WaitForAnimTasks
    WaitForAllEmitters
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    End
