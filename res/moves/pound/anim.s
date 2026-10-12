#include "macros/btlanimcmd.inc"

// Opal B9 (P0, physical_contact): soft heavy contact. Larger, slower hit flash + a soft gold pressure ring and a light camera
// punch on the confirmed hit; native emitters, sound and the 1px recoil shake keep their original frames (REACT_LIGHT replaces the shake).
// Donors: pokeemerald hit (opal_b9_strike), procedural Opal ring (opal_fx_ring_gold).
#define STRIKE OPAL_RES(opal_b9_strike, opal_b9_strike)
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_gold)

L_0:
    LoadParticleResource 0, pound_spa
    OpalSheetBegin 1, 3, STRIKE
    OpalSheetBegin 2, 3, RING
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_HIT_SMALL, BATTLE_ANIM_DEFENDER, 170
    OpalImpactBurst 2, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 120, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalReactLight BATTLE_ANIM_DEFENDER
    OpalCamPunch
    PlaySoundEffectR SEQ_SE_DP_030
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    End
