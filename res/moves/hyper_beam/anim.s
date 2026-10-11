#include "macros/btlanimcmd.inc"

// Opal B2: CHARGE_RELEASE_BEAM (all three native branches: battle, friendly fire, contest)
//   charge   two concentric gold rings + a star converge on the attacker together with the native charge emitter (no added delay)
//   beam     native beam + BG scroll/shake unchanged (the native base-BG shake is this move's camera cue)
//   impact   large star burst + expanding ring on the defender; no base-BG light pulse (the native BG switch owns the backdrop)
//   recharge nothing here touches the recharge turn: this script only runs when the engine plays the attack animation
// Contest branch keeps the vanilla look plus the same sprite cues.
// Donor: procedural opal_fx_ring (gold palette)
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_gold)

    .macro HyperCharge
    OpalSheetBegin 1, 8, RING
    OpalChargeAura 1, RING, OPAL_RING_SEQ_CONVERGE, 0, 220, BATTLE_ANIM_ATTACKER
    OpalChargeAura 1, RING, OPAL_RING_SEQ_CONVERGE, 0, 150, BATTLE_ANIM_ATTACKER
    OpalChargeAura 1, RING, OPAL_RING_SEQ_STAR_POP, 14, 130, BATTLE_ANIM_ATTACKER
    .endm

    .macro HyperImpact
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_DEFENDER, 280, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 220, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    .endm

L_0:
    LoadParticleResource 0, hyper_beam_spa
    JumpIfFriendlyFire L_1
    JumpIfContest L_2
    ResetVars
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_X, -32
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 0
    SetVar BATTLE_ANIM_VAR_BG_ANIM_MODE, 1
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    SwitchBg 14, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_MOVE
    WaitForBgSwitch
    Func_ShakeBg 0, 3, 0, 20, 0
    Func_ShakeBg 3, 1, 0, 4, 0, SHAKE_BG_TARGET_BASE
    HyperCharge
    CreateEmitter 0, 9, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitterForMove 0, 0, 1, 2, 3, 4, 5, 18
    CreateEmitterForMove 0, 10, 10, 10, 11, 11, 11, 18
    Delay 5
    HyperImpact
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W062D, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Func_Shake 4, 0, 1, 20, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    ResetVars
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_X, -32
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 0
    SetVar BATTLE_ANIM_VAR_BG_ANIM_MODE, 1
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    RestoreBg 14, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_STOP
    WaitForBgSwitch
    End

L_1:
    ResetVars
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_X, -32
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 0
    SetVar BATTLE_ANIM_VAR_BG_ANIM_MODE, 1
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    SwitchBg 14, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_MOVE
    WaitForBgSwitch
    Func_ShakeBg 0, 3, 0, 20, 0
    Func_ShakeBg 3, 1, 0, 4, 0, SHAKE_BG_TARGET_BASE
    HyperCharge
    CreateEmitter 0, 9, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitterForFriendlyFire 0, 7, 8, 7, 8, 3
    CreateEmitterForFriendlyFire 0, 13, 13, 13, 13, 3
    Delay 5
    HyperImpact
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W062D, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Func_Shake 4, 0, 1, 20, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    ResetVars
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_X, -32
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 0
    SetVar BATTLE_ANIM_VAR_BG_ANIM_MODE, 1
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    RestoreBg 14, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_STOP
    WaitForBgSwitch
    End

L_2:
    ResetVars
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_X, -32
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 0
    SetVar BATTLE_ANIM_VAR_BG_ANIM_MODE, 1
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    SwitchBg 14, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_MOVE
    WaitForBgSwitch
    Func_ShakeBg 0, 3, 0, 20, 0
    Func_ShakeBg 3, 1, 0, 4, 0, SHAKE_BG_TARGET_BASE
    HyperCharge
    CreateEmitter 0, 9, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 6, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, 11008, -8256, 0
    CreateEmitter 0, 12, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, 11008, -8256, 0
    Delay 5
    HyperImpact
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W062D, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Func_Shake 4, 0, 1, 20, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    ResetVars
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_X, -32
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 0
    SetVar BATTLE_ANIM_VAR_BG_ANIM_MODE, 1
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    RestoreBg 14, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_STOP
    WaitForBgSwitch
    End
