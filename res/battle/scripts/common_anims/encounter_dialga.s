#include "macros/btlanimcmd.inc"

// Opal B7 SPEAR_PILLAR (Dialga). Played once by subscript_start_encounter.s for a wild encounter flagged BATTLE_STATUS_LEGENDARY
// whose enemy species is Dialga (read-only gate; no encounter, flag or event data is touched).
//   phase 1 stage hue fade   phase 2 species rings converge / expand   phase 3 one controlled pulse   phase 4 restore before the healthbox
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_steel)

.data

L_0:
    OpalSheetBegin 0, 8, RING
    OpalDimIn BATTLE_COLOR_DARK_BLUE, 8, 1
    OpalChargeAura 0, RING, OPAL_RING_SEQ_CONVERGE, 0, 340, BATTLE_ANIM_ATTACKER, 0, -4
    Delay 6
    OpalChargeAura 0, RING, OPAL_RING_SEQ_CONVERGE, 0, 230, BATTLE_ANIM_ATTACKER, 0, -4
    Delay 10
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_ATTACKER, 320, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_ATTACKER, 400, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalDimOut BATTLE_COLOR_DARK_BLUE, 8, 1
    Delay 10
    OpalLightPulse BATTLE_COLOR_LIGHT_BLUE, 4
    Delay 6
    OpalSheetEnd 0
    End
