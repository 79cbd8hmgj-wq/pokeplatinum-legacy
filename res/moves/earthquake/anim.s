#include "macros/btlanimcmd.inc"

// Opal B2: SCREEN_SPACE_GROUND_SHOCK
//   windup  converging earth ripple at the attacker's feet; native sprite/BG shake unchanged
//   impact  two staggered flat shock rings + dust at the defender's feet (same anchor as the native emitter);
//           the native base-BG shake (Func_ShakeBg) is this move's camera cue, so no second camera cue is layered on it
// The native animation is played once per use for the engine's primary defender and shakes every battler; the
// Opal rings are anchored to the same primary defender and the attacker only, so no per-target "hit" is invented for
// battlers the animation cannot know are immune.
// Donor: procedural opal_fx_ring (earth palette)
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_earth)

L_0:
    LoadParticleResource 0, earthquake_spa
    OpalSheetBegin 1, 6, RING
    OpalChargeAura 1, RING, OPAL_RING_SEQ_FLAT_CONVERGE, 0, 150, BATTLE_ANIM_ATTACKER, 0, 24
    Func_Earthquake 0
    Func_ShakeBg 4, 3, 0, 5, 0, SHAKE_BG_TARGET_BASE
    Delay 2
    PlaySoundEffectC SEQ_SE_DP_W089
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_DEFENDER, 190, 0, 24, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 6
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_DEFENDER, 130, 0, 26, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalResidual 1, RING, OPAL_RING_SEQ_DOT_PULSE, BATTLE_ANIM_DEFENDER, 22, 80, -18, 18
    OpalResidual 1, RING, OPAL_RING_SEQ_DOT_PULSE, BATTLE_ANIM_DEFENDER, 22, 60, 18, 20
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
