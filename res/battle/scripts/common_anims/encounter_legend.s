#include "macros/btlanimcmd.inc"

// Opal B7 generic legendary arrival, for BATTLE_STATUS_LEGENDARY wild encounters whose species is one of the event/legendary
// roster (Darkrai, Shaymin, Arceus, Cresselia, Regigigas, Heatran, Giratina outside the Distortion World). Presentation only; if the
// project does not reach such an encounter the animation is simply never called.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_opal)

.data

L_0:
    OpalSheetBegin 0, 8, RING
    OpalDimIn BATTLE_COLOR_DARK_PURPLE, 5, 1
    OpalChargeAura 0, RING, OPAL_RING_SEQ_CONVERGE, 0, 300, BATTLE_ANIM_ATTACKER, 0, -4
    Delay 8
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_ATTACKER, 280, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_ATTACKER, 340, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 12
    OpalDimOut BATTLE_COLOR_DARK_PURPLE, 5, 1
    OpalSheetEnd 0
    End
