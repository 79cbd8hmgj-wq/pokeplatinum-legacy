#include "macros/btlanimcmd.inc"

// Opal B7 GIRATINA_DISTORTION. Played once by subscript_start_encounter.s when the encounter was started by
// Encounter_NewVsGiratinaOrigin (BATTLE_STATUS_GIRATINA | BATTLE_STATUS_DISTORTION | BATTLE_STATUS_LEGENDARY).
//   phase 1 violet scene fade, arena backdrop only      phase 2 backdrop parallax offset (opposing shadow feel)
//   phase 3 distortion halo rings around the enemy      phase 4 backdrop restored; the script ends before the healthbox slides in
// ~64 frames, every resource is released before End. No flag, table or story state is read or written here.
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_ghost)

.data

L_0:
    OpalSheetBegin 0, 8, RING
    OpalDimIn BATTLE_COLOR_DARK_PURPLE, 10, 1
    OpalCamFocusAttacker
    OpalChargeAura 0, RING, OPAL_RING_SEQ_CONVERGE, 0, 360, BATTLE_ANIM_ATTACKER, 0, -4
    Delay 8
    OpalChargeAura 0, RING, OPAL_RING_SEQ_CONVERGE, 0, 250, BATTLE_ANIM_ATTACKER, 0, -4
    Delay 10
    OpalImpactBurst 0, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_ATTACKER, 380, 0, -4, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalResidual 0, RING, OPAL_RING_SEQ_DOT_PULSE, BATTLE_ANIM_ATTACKER, 30, 90, -22, -4
    OpalResidual 0, RING, OPAL_RING_SEQ_DOT_PULSE, BATTLE_ANIM_ATTACKER, 30, 70, 22, 6
    Delay 14
    OpalDimOut BATTLE_COLOR_DARK_PURPLE, 10, 1
    OpalSheetEnd 0
    End
