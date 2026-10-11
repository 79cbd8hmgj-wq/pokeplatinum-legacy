#include "macros/btlanimcmd.inc"

// Opal B5 REACT_BLOCKED. Played from subscript_missed.s only on the engine's own "protected itself" branch
// (MOVE_STATUS_PROTECTED), on the protecting battler. It is a guard cue (contracting + expanding pearl ring and a cool glance),
// deliberately not a damage recoil: nothing moves, shakes or flashes red. Resource lifetime is bounded by the FX hard cap.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_opal)

.data

L_0:
    OpalSheetBegin 0, 4, RING
    PlaySoundEffectC SEQ_SE_DP_W115
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_CONVERGE, BATTLE_ANIM_ATTACKER, 170, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 1, BATTLE_COLOR_LIGHT_BLUE, 6, 4
    Delay 8
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_ATTACKER, 210, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalSheetEnd 0
    End
