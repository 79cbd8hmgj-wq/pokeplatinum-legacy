#include "macros/btlanimcmd.inc"

// Opal B9 (P0, bite): an upper and a lower jaw close on the target over the native 10-frame lead-in and snap exactly where the native
// shake used to start; native emitters, sound and timing unchanged. The script now ends through WaitForAllEmitters /
// UnloadParticleSystem like every other Opal script (End already waited for both).
// Donors: pokeemerald fangs (opal_b9_strike jaw_upper / jaw_lower), hit (opal_b9_strike).
// QA note: if the native bite_spa emitters already draw jaws on the same frames the two read as one doubled bite - see EMULATOR_QA.md.
#define STRIKE OPAL_RES(opal_b9_strike, opal_b9_strike)

L_0:
    LoadParticleResource 0, bite_spa
    OpalSheetBegin 1, 4, STRIKE
    OpalFx 1, STRIKE, OPAL_B9_STRIKE_SEQ_JAW_UPPER, BATTLE_ANIM_DEFENDER, BATTLE_ANIM_DEFENDER, 10, 0, -26, 0, -6, 0, 100, OPAL_FX_FLAG_HOLD_LAST
    OpalFx 1, STRIKE, OPAL_B9_STRIKE_SEQ_JAW_LOWER, BATTLE_ANIM_DEFENDER, BATTLE_ANIM_DEFENDER, 10, 0, 22, 0, 4, 0, 100, OPAL_FX_FLAG_HOLD_LAST
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 4, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    Delay 2
    PlaySoundEffectR SEQ_SE_DP_W044
    Delay 8
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_HIT_SMALL, BATTLE_ANIM_DEFENDER, 140
    OpalReactLight BATTLE_ANIM_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
