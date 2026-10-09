#include "macros/btlanimcmd.inc"

// AV1: layered fire burst (ember core -> secondary embers -> dissipating glow).
// Secondary embers reuse fire_punch.spa defender emitters 0 and 2.
L_0:
    LoadParticleResource 0, ember_spa
    LoadParticleResource 1, fire_punch_spa
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 8, BATTLE_COLOR_DARK_RED2
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_RED, 10, 0
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    PlayLoopedSoundEffectR SEQ_SE_DP_W052, 3, 4
    Delay 6
    CreateEmitter 1, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Delay 8
    CreateEmitter 1, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_LIGHT_ORANGE, 6, 6
    WaitForAnimTasks
    WaitForAllEmitters
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 8, 0, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    End
