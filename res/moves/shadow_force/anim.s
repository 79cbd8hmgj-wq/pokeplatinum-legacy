#include "macros/btlanimcmd.inc"

// Opal B2-05: the release path (L_2) gets a ghost ring + star burst on the defender. The charge path (L_1) is untouched:
// the attacker is hidden and invulnerable there, so no cue is anchored to it, and the native hide/grayscale handling is not altered.
// Donor: procedural opal_fx_ring (ghost palette).
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_ghost)

L_0:
    LoadParticleResource 0, shadow_force_spa
    JumpIfEffectChanceOdd L_1, L_2
    End

L_1:
    PlaySoundEffectL SEQ_SE_DP_W467
    Func_BlinkAttacker 5, 0
    Delay 2
    Func_SetBgGrayscale TRUE
    WaitForAnimTasks
    Func_HideBattler BATTLE_ANIM_ATTACKER, TRUE
    Delay 15
    WaitForAllEmitters
    UnloadParticleSystem 0
    Func_SetBgGrayscale FALSE
    WaitForAnimTasks
    End

L_2:
    Func_SetBgGrayscale TRUE
    PlaySoundEffectR SEQ_SE_DP_186
    WaitForAnimTasks
    Delay 20
    PlaySoundEffectR SEQ_SE_DP_W007
    OpalSheetBegin 1, 4, RING
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 190, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_DEFENDER, 160, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_Shake 4, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Delay 5
    PlayDelayedSoundEffectR SEQ_SE_DP_W109, 8
    PlayDelayedSoundEffectR SEQ_SE_DP_W109, 13
    Func_BlinkAttacker 5, 0
    WaitForAnimTasks
    Func_HideBattler BATTLE_ANIM_ATTACKER, FALSE
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    Func_SetBgGrayscale FALSE
    WaitForAnimTasks
    End
