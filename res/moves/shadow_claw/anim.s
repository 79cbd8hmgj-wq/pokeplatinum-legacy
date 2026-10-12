#include "macros/btlanimcmd.inc"

// Opal B5: REACT_LIGHT on the confirmed hit (replaces the bare 1px shake; same frame).

L_0:
    LoadParticleResource 0, shadow_claw_spa
    PlaySoundEffectR SEQ_SE_DP_161
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    Delay 5
    OpalReactLight BATTLE_ANIM_DEFENDER
    WaitForAllEmitters
    UnloadParticleSystem 0
    End
