#include "macros/btlanimcmd.inc"

// AV1: fire vortex gains a flickering heat-glow and trailing embers.
// Trailing embers reuse flame_wheel.spa defender emitters 1 and 2.
L_0:
    LoadParticleResource 0, fire_spin_spa
    LoadParticleResource 1, flame_wheel_spa
    PlaySoundEffectR SEQ_SE_DP_W221B
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 2, BATTLE_COLOR_RED, 10, 10
    Func_Shake 1, 0, 1, 8, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 6, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    Delay 10
    CreateEmitter 1, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    BeginLoop 2
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 6, 10, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 10, 6, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    EndLoop
    CreateEmitter 1, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_LIGHT_ORANGE, 6, 6
    WaitForAnimTasks
    WaitForAllEmitters
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 6, 0, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    End
