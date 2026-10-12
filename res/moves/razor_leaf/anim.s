#include "macros/btlanimcmd.inc"

// Opal B9 (P0, leaf_volley): the native gale gathers; a three-lane leaf fan (lead + two curved flyers, each with a razor-blade
// crescent riding the lane) is launched so it lands on the native impact frame (t = 75), followed by leaf flutter. Every native delay is
// preserved: the first 50-frame wait is split 25 + 25 around the fan launch (travel = 34 frames; arrival ~ frame 74-75).
// Donors: pokeemerald leaf / razor_leaf (opal_b9_nature).
#define NATURE OPAL_RES(opal_b9_nature, opal_b9_nature)

L_0:
    LoadParticleResource 0, razor_leaf_spa
    OpalSheetBegin 1, 10, NATURE
    PlaySoundEffectL SEQ_SE_DP_KAZE
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 6, 5, 0, 0
    Delay 15
    StopSoundEffect SEQ_SE_DP_KAZE
    Delay 25
    OpalFx 1, NATURE, OPAL_B9_NATURE_SEQ_LEAF_SPIN, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 34, 14, -6, 0, -2, 24, 100, 0
    OpalFx 1, NATURE, OPAL_B9_NATURE_SEQ_LEAF_SPIN, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 34, 14, 0, 0, 2, 0, 90, 0
    OpalFx 1, NATURE, OPAL_B9_NATURE_SEQ_LEAF_SPIN, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 34, 14, 6, 0, 6, -20, 80, 0
    OpalProjectile 1, NATURE, OPAL_B9_NATURE_SEQ_RAZOR, 34, 90, 8, 0, 14, 0, 0, 0
    Delay 25
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_209, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Delay 10
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER_SIDE
    OpalImpactBurst 1, NATURE, OPAL_B9_NATURE_SEQ_RAZOR, BATTLE_ANIM_DEFENDER, 120, 0, -2, 12
    OpalReactLight BATTLE_ANIM_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    Delay 7
    PlayLoopedSoundEffectR SEQ_SE_DP_HURU, 3, 5
    OpalResidual 1, NATURE, OPAL_B9_NATURE_SEQ_FLUTTER, BATTLE_ANIM_DEFENDER, 26, 100, -8, -8
    OpalResidual 1, NATURE, OPAL_B9_NATURE_SEQ_FLUTTER, BATTLE_ANIM_DEFENDER, 22, 80, 10, -2
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
