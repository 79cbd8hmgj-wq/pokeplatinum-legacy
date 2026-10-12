#include "macros/btlanimcmd.inc"

// Opal B9 (P0, status_gesture): each of the two native wags leaves a soft wind crescent behind the user; during the second wag a
// small gold star pops on every resolved target as the "less wary" feedback pulse. The native two-iteration loop is unrolled so the
// pulse can attach to the second wag; sounds, revolve timing and total length are identical. Played only after the Defense drop
// succeeded (subscript_update_stat_stage).
// Donors: pokeemerald air_wave_2 (opal_b9_wind crescent), procedural Opal star (opal_fx_wx_gold).
#define WIND OPAL_RES(opal_b9_wind, opal_b9_wind)
#define STAR OPAL_RES(opal_fx_wx, opal_fx_wx_gold)

L_0:
    OpalSheetBegin 1, 4, WIND
    OpalSheetBegin 2, 4, STAR
    PlaySoundEffectL SEQ_SE_DP_112
    OpalImpactBurst 1, WIND, OPAL_B9_WIND_SEQ_CRESCENT, BATTLE_ANIM_ATTACKER, 110, -14, 4, 12, OPAL_FX_FLAG_TRANSLUCENT
    Func_RevolveBattler BATTLE_ANIM_ATTACKER, 1, 12
    WaitForAnimTasks
    PlaySoundEffectL SEQ_SE_DP_112
    OpalImpactBurst 1, WIND, OPAL_B9_WIND_SEQ_CRESCENT, BATTLE_ANIM_ATTACKER, 110, -14, 4, 12, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 2, STAR, OPAL_WX_SEQ_STAR_POP, BATTLE_ANIM_DEFENDER_SIDE, 140, 0, -10, 12, OPAL_FX_FLAG_TRANSLUCENT
    Func_RevolveBattler BATTLE_ANIM_ATTACKER, 1, 12
    WaitForAnimTasks
    OpalSheetEnd 1
    OpalSheetEnd 2
    End
