#include "macros/btlanimcmd.inc"

// Opal B7 LAKE_GUARDIANS (Mesprit). Played once by subscript_start_encounter.s for a BATTLE_STATUS_LEGENDARY wild encounter whose
// enemy species is Mesprit. Quieter than the Spear Pillar cues: thin ripples at the feet, a soft glow, no full-stage pulse.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_psychic)

.data

L_0:
    OpalSheetBegin 0, 8, RING
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ATTACKER, 170, 0, 24, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 8
    OpalChargeAura 0, RING, OPAL_RING_SEQ_DOT_PULSE, 34, 260, BATTLE_ANIM_ATTACKER, 0, -4
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ATTACKER, 230, 0, 26, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 14
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_ATTACKER, 240, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalSheetEnd 0
    End
