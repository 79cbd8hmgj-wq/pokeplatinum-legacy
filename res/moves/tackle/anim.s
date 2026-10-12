#include "macros/btlanimcmd.inc"

// Opal B9 (P0, physical_contact): dig-in dust -> native lunge -> hit flash + light reaction -> native restore.
// Native emitters, sounds and timing unchanged; the shake is replaced by REACT_LIGHT (same frame, same 2px recoil + one flash).
// Donors: pokeemerald speed_dust (opal_b9_wind), hit (opal_b9_strike); see docs/visual_overhaul/opal_b9/RECIPES.md
#define STRIKE OPAL_RES(opal_b9_strike, opal_b9_strike)
#define WIND OPAL_RES(opal_b9_wind, opal_b9_wind)

L_0:
    LoadParticleResource 0, tackle_spa
    OpalSheetBegin 1, 3, STRIKE
    OpalSheetBegin 2, 3, WIND
    PlaySoundEffectR SEQ_SE_DP_050
    OpalImpactBurst 2, WIND, OPAL_B9_WIND_SEQ_PUFF, BATTLE_ANIM_ATTACKER, 85, -6, 16, 0, OPAL_FX_FLAG_TRANSLUCENT
    Func_MoveBattler BATTLE_ANIM_BATTLER_SPRITE_ATTACKER, 14, -8, 2
    WaitForAnimTasks
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_HIT_SMALL, BATTLE_ANIM_DEFENDER, 130
    OpalReactLight BATTLE_ANIM_DEFENDER
    Func_MoveBattler BATTLE_ANIM_BATTLER_SPRITE_ATTACKER, -14, 8, 2
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    End
