#include "macros/btlanimcmd.inc"

// Opal B2-05: IMPACT_BURST on each of the three native meteor impacts (same frames as the native hit emitters / shakes),
// no change to the native dim, emitters or timing. Donor: pokeemerald fire_plume (opal_fire). Camera: the native base-BG shakes are the cue.
#define FIRE OPAL_RES(opal_fire, opal_fire)

L_0:
    LoadParticleResource 0, draco_meteor_spa
    OpalSheetBegin 1, 6, FIRE
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_DARK_BLUE
    PlaySoundEffectC SEQ_SE_DP_201
    WaitForAnimTasks
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 0
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 0
    Delay 50
    PlaySoundEffectC SEQ_SE_DP_W089
    CreateEmitter 0, 2, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 0
    CreateEmitter 0, 2, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 0
    CreateEmitter 0, 3, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 0
    CreateEmitter 0, 3, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 0, 0, 0, 0
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W434, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Delay 15
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W434, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, FIRE, OPAL_FIRE_SEQ_PLUME, BATTLE_ANIM_DEFENDER, 130, -10, 2, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_Shake 4, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_ShakeBg 0, 3, 0, 1, 0
    Delay 10
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W434, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, FIRE, OPAL_FIRE_SEQ_PLUME, BATTLE_ANIM_DEFENDER, 130, 10, 2, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_Shake 4, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_ShakeBg 0, 3, 0, 1, 0
    Delay 15
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, FIRE, OPAL_FIRE_SEQ_PLUME, BATTLE_ANIM_DEFENDER, 170, 0, 2, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_Shake 4, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_ShakeBg 0, 4, 0, 4, 0
    Func_ShakeBg 2, 3, 0, 2, 0, SHAKE_BG_TARGET_BASE
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W434, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Delay 20
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_DARK_BLUE
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
