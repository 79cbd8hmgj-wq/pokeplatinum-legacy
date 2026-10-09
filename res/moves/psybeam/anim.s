#include "macros/btlanimcmd.inc"

// AV1: the beam is released as three staggered, shrinking pulses with a
// breathing psychic glow, instead of a single constant stream.
L_0:
    LoadParticleResource 0, psybeam_spa
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 6, BATTLE_COLOR_DARK_PURPLE
    WaitForAnimTasks
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W060C, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 14, 8, 0, 0
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_PURPLE, 8, 10
    Func_FadeBg FADE_BG_TYPE_BASE, 0, 6, 10, BATTLE_COLOR_DARK_PURPLE
    Delay 10
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 14, 6, 0, 0
    Func_FadeBg FADE_BG_TYPE_BASE, 0, 10, 6, BATTLE_COLOR_DARK_PURPLE
    Delay 10
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 14, 4, 0, 0
    Func_FadeBg FADE_BG_TYPE_BASE, 0, 6, 10, BATTLE_COLOR_DARK_PURPLE
    BeginLoop 2
    Func_MoveBattlerX2 8, 8, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Delay 8
    Func_MoveBattlerX2 16, -16, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Delay 16
    Func_MoveBattlerX2 8, 8, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Delay 8
    EndLoop
    WaitForAnimTasks
    WaitForAllEmitters
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 10, 0, BATTLE_COLOR_DARK_PURPLE
    WaitForAnimTasks
    End
