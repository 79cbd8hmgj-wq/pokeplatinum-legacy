#include "macros/btlanimcmd.inc"

// Opal B9 (P0, slash_contact): three staggered claw arcs (two directions) over the native scratch emitters + light reaction.
// The 2 + 2 frame stagger sits inside the native emitter lifetime, so the animation ends when it did before.
// Donor: pokeemerald fury_swipes (opal_b9_strike claw_a / claw_b), hit (opal_b9_strike).
#define STRIKE OPAL_RES(opal_b9_strike, opal_b9_strike)

L_0:
    LoadParticleResource 0, scratch_spa
    OpalSheetBegin 1, 5, STRIKE
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_CLAW_A, BATTLE_ANIM_DEFENDER, 115, -10, -6
    PlaySoundEffectR SEQ_SE_DP_W010
    Delay 2
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_CLAW_B, BATTLE_ANIM_DEFENDER, 115, 0, 0
    OpalReactLight BATTLE_ANIM_DEFENDER
    Delay 2
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_CLAW_A, BATTLE_ANIM_DEFENDER, 115, 10, 6
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_HIT_SMALL, BATTLE_ANIM_DEFENDER, 90, 6, 4
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
