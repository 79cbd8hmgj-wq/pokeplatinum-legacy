#include "macros/btlanimcmd.inc"

// Opal B9 (P0, water_bubble): individual bubbles of three sizes rise on separate arcs toward every resolved target and pop on arrival
// (small pop per target, one iridescent big pop on the first). The native 10 + 10 frame cadence is kept; launches are carved out of the
// first Delay 10 (5 + 5). Contest branch is left fully native.
// Donors: pokeemerald bubble / small_bubbles / bubble_burst / bubble_burst_2 (opal_b9_bubble).
#define BUBBLE OPAL_RES(opal_b9_bubble, opal_b9_bubble)

L_0:
    LoadParticleResource 0, bubble_spa
    LoadParticleResource 1, bubble_spa
    JumpIfContest L_1
    OpalSheetBegin 1, 10, BUBBLE
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 31, 24, 0, 4
    PlayLoopedSoundEffectC SEQ_SE_DP_W145, 2, 5
    OpalFx 1, BUBBLE, OPAL_B9_BUBBLE_SEQ_BUBBLE, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER_SIDE, 20, 12, -4, 0, -4, 14, 100, 0
    Delay 5
    OpalFx 1, BUBBLE, OPAL_B9_BUBBLE_SEQ_SMALL, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER_SIDE, 18, 12, 4, 0, 6, 18, 90, 0
    Delay 5
    CreateEmitter 1, 1, EMITTER_CB_SET_POS_TO_DEFENDER_SIDE
    OpalFx 1, BUBBLE, OPAL_B9_BUBBLE_SEQ_BUBBLE, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER_SIDE, 10, 8, 0, 0, -6, 12, 70, 0
    Delay 10
    OpalImpactBurst 1, BUBBLE, OPAL_B9_BUBBLE_SEQ_POP, BATTLE_ANIM_DEFENDER_SIDE, 130
    OpalImpactBurst 1, BUBBLE, OPAL_B9_BUBBLE_SEQ_POP_BIG, BATTLE_ANIM_DEFENDER, 120, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    PlayLoopedSoundEffectR SEQ_SE_DP_W145C, 2, 2
    Delay 10
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    End

L_1:
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 0, 28, 22, 0, 4
    PlayLoopedSoundEffectC SEQ_SE_DP_W145, 2, 5
    Delay 10
    CreateEmitter 1, 1, EMITTER_CB_SET_POS_TO_DEFENDER_SIDE
    Delay 10
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    PlayLoopedSoundEffectR SEQ_SE_DP_W145C, 2, 2
    Delay 10
    WaitForAllEmitters
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    End
