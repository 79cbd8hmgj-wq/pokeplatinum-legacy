#include "macros/btlanimcmd.inc"

// Opal B2 canonical composite: GHOST_ORB_PROJECTILE
//   gather     two offset wisps + converging violet ring around the attacker, stage darkens
//   travel     native shadow-ball emitters keep their timing; ghost orb with two afterimages rides the same path
//   impact     inward-collapse ring + wisp burst on the defender; single native hit reaction
//   dissipate  wisps rise and shrink, stage brightness restored
// Donor: pokeemerald shadow_ball / ghostly_spirit (violet ramp recolor) + procedural opal_fx_ring (ghost palette)
#define GHOST OPAL_RES(opal_ghost, opal_ghost)
#define RING  OPAL_RES(opal_fx_ring, opal_fx_ring_ghost)

L_0:
    LoadParticleResource 0, shadow_ball_spa
    OpalSheetBegin 0, 10, GHOST
    OpalSheetBegin 1, 4, RING
    OpalCamFocusAttacker
    OpalDimIn BATTLE_COLOR_DARK_PURPLE, 8, 1
    WaitForAnimTasks
    CreateEmitter 0, 4, EMITTER_CB_NONE
    CreateEmitter 0, 0, EMITTER_CB_NONE
    CreateEmitter 0, 1, EMITTER_CB_NONE
    PlayLoopedSoundEffectC SEQ_SE_DP_W028, 2, 12
    OpalChargeAura 0, GHOST, OPAL_GHOST_SEQ_WISP, 44, 80, BATTLE_ANIM_ATTACKER, -16, -6
    OpalChargeAura 0, GHOST, OPAL_GHOST_SEQ_WISP, 44, 80, BATTLE_ANIM_ATTACKER, 16, 6
    OpalChargeAura 1, RING, OPAL_RING_SEQ_CONVERGE, 0, 180
    Delay 14
    OpalChargeAura 1, RING, OPAL_RING_SEQ_CONVERGE, 0, 130
    Delay 41
    CreateEmitter 0, 2, EMITTER_CB_NONE
    Func_MoveEmitterA2BLinear 0, 0, 0, 0, 8, 255, EMITTER_ANIMATION_MODE_ATK_TO_DEF, SKIP_F(4)
    OpalProjectile 0, GHOST, OPAL_GHOST_SEQ_ORB, 8, 100, 0, 0
    OpalCamFollow 8
    Delay 8
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 150, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 0, GHOST, OPAL_GHOST_SEQ_WISP, BATTLE_ANIM_DEFENDER, 110, 0, 0, 14, OPAL_FX_FLAG_TRANSLUCENT
    OpalCamPunch
    Delay 3
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_DARK_PURPLE, 14, 0
    PlaySoundEffectR SEQ_SE_DP_480
    OpalResidual 0, GHOST, OPAL_GHOST_SEQ_WISP, BATTLE_ANIM_DEFENDER, 26, 70, 0, -4
    WaitForAllEmitters
    OpalSheetEnd 0
    OpalSheetEnd 1
    UnloadParticleSystem 0
    OpalDimOut BATTLE_COLOR_DARK_PURPLE, 8, 1
    WaitForAnimTasks
    End
