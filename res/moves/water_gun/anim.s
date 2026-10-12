#include "macros/btlanimcmd.inc"

// Opal B9 (P0, water_jet): a continuous three-pulse droplet stream (lead + two afterimages each) rides the native water jet, a foam
// splash and rebounding droplets mark the impact. The three launches are carved out of the native 10-frame lead-in (3 + 3 + 4), so
// the impact still lands on the original frame. Contest branch is left fully native.
// Donors: pokeemerald water_droplet / water_impact (opal_water, B2 sheet reused).
#define WATER OPAL_RES(opal_water, opal_water)

L_0:
    LoadParticleResource 0, water_gun_spa
    JumpIfFriendlyFire L_1
    JumpIfContest L_2
    OpalSheetBegin 1, 12, WATER
    CreateEmitterForMove 0, 2, 3, 4, 5, 7, 6, 18
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W055, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    OpalProjectile 1, WATER, OPAL_WATER_SEQ_DROPLET, 10, 90, 0, 0, 10, -2, 0, 0
    Delay 3
    OpalProjectile 1, WATER, OPAL_WATER_SEQ_DROPLET, 10, 100, 4, 0, 10, 2, 0, 2
    Delay 3
    OpalProjectile 1, WATER, OPAL_WATER_SEQ_DROPLET, 10, 80, -4, 0, 10, 0, 0, -2
    Delay 4
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, WATER, OPAL_WATER_SEQ_FOAM, BATTLE_ANIM_DEFENDER, 130, 0, 4, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalResidual 1, WATER, OPAL_WATER_SEQ_DROPLET, BATTLE_ANIM_DEFENDER, 20, 90, 0, -6
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    WaitForAnimTasks
    End

L_1:
    OpalSheetBegin 1, 12, WATER
    CreateEmitterForFriendlyFire 0, 9, 10, 9, 10, 3
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W055, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    OpalProjectile 1, WATER, OPAL_WATER_SEQ_DROPLET, 10, 90, 0, 0, 10, -2, 0, 0
    Delay 3
    OpalProjectile 1, WATER, OPAL_WATER_SEQ_DROPLET, 10, 100, 4, 0, 10, 2, 0, 2
    Delay 3
    OpalProjectile 1, WATER, OPAL_WATER_SEQ_DROPLET, 10, 80, -4, 0, 10, 0, 0, -2
    Delay 4
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, WATER, OPAL_WATER_SEQ_FOAM, BATTLE_ANIM_DEFENDER, 130, 0, 4, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalResidual 1, WATER, OPAL_WATER_SEQ_DROPLET, BATTLE_ANIM_DEFENDER, 20, 90, 0, -6
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    WaitForAnimTasks
    End

L_2:
    CreateEmitter 0, 8, EMITTER_CB_GENERIC
    SetExtraParams 0, 1, 5, 0, 0, 0
    SetExtraParams 0, 9976, -7568, 0
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W055, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Delay 10
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    UnloadParticleSystem 0
    WaitForAnimTasks
    End
