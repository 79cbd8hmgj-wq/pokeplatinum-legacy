#include "macros/btlanimcmd.inc"

// Opal B9 (P0, status_gaze): an eye glint flashes at the user's eyes, then a second, larger glint lands on every resolved target
// as the native stare flashes. Cues are asynchronous - native dim, emitters, sounds and timing unchanged. Played only after the
// Defense drop succeeded (subscript_update_stat_stage). Contest branch is left fully native.
// Donors: pokeemerald leer glint (opal_b9_sense).
#define SENSE OPAL_RES(opal_b9_sense, opal_b9_sense)

L_0:
    LoadParticleResource 0, leer_spa
    JumpIfContest L_1
    OpalSheetBegin 1, 4, SENSE
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_BLACK
    OpalImpactBurst 1, SENSE, OPAL_B9_SENSE_SEQ_GLINT, BATTLE_ANIM_ATTACKER, 100, 12, -14, 0, OPAL_FX_FLAG_TRANSLUCENT
    WaitForAnimTasks
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, -4128, 0, 0
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, -4128, 0, 0
    CreateEmitter 0, 2, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, -4128, 0, 0
    Delay 10
    OpalImpactBurst 1, SENSE, OPAL_B9_SENSE_SEQ_GLINT, BATTLE_ANIM_DEFENDER_SIDE, 150, 0, -8, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    PlaySoundEffectL SEQ_SE_DP_W043
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End

L_1:
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, 4128, 0, 0
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, 4128, 0, 0
    CreateEmitter 0, 2, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, 4128, 0, 0
    Delay 10
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    PlaySoundEffectL SEQ_SE_DP_W043
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    WaitForAllEmitters
    UnloadParticleSystem 0
    End
