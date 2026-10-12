#include "macros/btlanimcmd.inc"

// Opal B9 (P0, vine_lash): native wind-up lunge, then a two-part vine strike - a thrown lash travels from the user to the target, a
// second shorter flick lands on the native shake frame - with leaf debris after the snap. REACT_LIGHT replaces the native 1px shake
// on the same frame. Native emitters / sounds / timing unchanged.
// Donors: pokeemerald vine_2 / leaf (opal_b9_nature).
#define NATURE OPAL_RES(opal_b9_nature, opal_b9_nature)

L_0:
    LoadParticleResource 0, vine_whip_spa
    OpalSheetBegin 1, 6, NATURE
    Func_MoveBattlerX2 3, 24, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    WaitForAnimTasks
    Func_MoveBattlerX2 3, -24, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_MUCHI
    OpalFx 1, NATURE, OPAL_B9_NATURE_SEQ_VINE_LASH, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 5, 14, -6, -10, -8, 0, 120, 0
    Delay 5
    OpalImpactBurst 1, NATURE, OPAL_B9_NATURE_SEQ_VINE_LASH, BATTLE_ANIM_DEFENDER, 110, -6, -2
    OpalReactLight BATTLE_ANIM_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_PASA2
    OpalResidual 1, NATURE, OPAL_B9_NATURE_SEQ_FLUTTER, BATTLE_ANIM_DEFENDER, 24, 100, -8, -6
    OpalResidual 1, NATURE, OPAL_B9_NATURE_SEQ_FLUTTER, BATTLE_ANIM_DEFENDER, 20, 80, 10, 0
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    WaitForAnimTasks
    End
