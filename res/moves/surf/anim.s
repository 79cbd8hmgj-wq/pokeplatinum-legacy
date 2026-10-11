#include "macros/btlanimcmd.inc"

// Opal B2 canonical composite: LAYERED_BATTLEFIELD_SWEEP
//   build    water column rises at the attacker, camera focus, native wave sprites begin
//   crest    native Surf wave + backdrop scroll (unchanged) with spray layered over every battler the engine resolved
//   contact  foam burst + droplets on each battler in the existing NOT_ATTACKER set (ally included in doubles),
//            existing fades/shakes untouched
//   drain    droplets finish, sheet released, weather accent only if weather is active
// Donor: pokeemerald water_column / water_droplet / water_impact (opal_water provenance)
#define WATER OPAL_RES(opal_water, opal_water)

L_0:
    LoadParticleResource 0, aqua_jet_spa
    OpalSheetBegin 1, 10, WATER
    InitSpriteManager 0, 2, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, surf_NCGR_lz
    LoadPlttRes 0, surf_NCLR, 1
    LoadCellResObj 0, surf_cell_NCER_lz
    LoadAnimResObj 0, surf_anim_NANR_lz
    AddSprite 0, 0, surf_NCGR_lz, surf_NCLR, surf_cell_NCER_lz, surf_anim_NANR_lz, 0, 0
    AddSprite 0, 1, surf_NCGR_lz, surf_NCLR, surf_cell_NCER_lz, surf_anim_NANR_lz, 0, 0
    OpalCamFocusAttacker
    OpalChargeAura 1, WATER, OPAL_WATER_SEQ_COLUMN, 24, 110, BATTLE_ANIM_ATTACKER, 0, 8
    PlaySoundEffectL SEQ_SE_DP_W057
    Func_Surf 0
    WaitForAnimTasks
    FreeSpriteManager 0
    Func_ScrollCustomBg 48, 0, 256, -6, 6, TRUE, 20, 45
    PlaySoundEffectC SEQ_SE_DP_W057B
    Delay 15
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER_SIDE
    OpalImpactBurst 1, WATER, OPAL_WATER_SEQ_FOAM, BATTLE_ANIM_NOT_ATTACKER, 170, 0, 6, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalResidual 1, WATER, OPAL_WATER_SEQ_DROPLET, BATTLE_ANIM_NOT_ATTACKER, 26, 100, 0, -14
    OpalCamPunch
    OpalWeatherAccent
    JumpIfFriendlyFire L_1
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER_PARTNER, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER_PARTNER, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_Shake 2, 0, 1, 6, BATTLE_ANIM_BATTLER_SPRITES | BATTLE_ANIM_NOT_ATTACKER
    WaitForAnimTasks
    WaitForAllEmitters
    Jump L_4

L_1:
    JumpIfBattlerSide BATTLER_ROLE_ATTACKER, L_2, L_3
    End

L_2:
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_FadeBattlerSprite BATTLE_ANIM_BATTLER_ENEMY_1, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_FadeBattlerSprite BATTLE_ANIM_BATTLER_ENEMY_2, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_Shake 2, 0, 1, 6, BATTLE_ANIM_BATTLER_SPRITES | BATTLE_ANIM_NOT_ATTACKER
    WaitForAnimTasks
    WaitForAllEmitters
    Jump L_4

L_3:
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_FadeBattlerSprite BATTLE_ANIM_BATTLER_PLAYER_1, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_FadeBattlerSprite BATTLE_ANIM_BATTLER_PLAYER_2, 0, 1, BATTLE_COLOR_TEAL_GREEN, 10, 10
    Func_Shake 2, 0, 1, 6, BATTLE_ANIM_BATTLER_SPRITES | BATTLE_ANIM_NOT_ATTACKER
    WaitForAnimTasks
    WaitForAllEmitters
    Jump L_4

// Single exit for every branch: release sprite managers before the particle system, then end.
L_4:
    OpalSheetEnd 1
    OpalWeatherAccentEnd 2
    UnloadParticleSystem 0
    End

    OpalWeatherAccentSub 2, BATTLE_ANIM_NOT_ATTACKER
