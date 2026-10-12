#include "macros/btlanimcmd.inc"

// Opal B9 (P0, ice_snow): snow flecks gather around the user while the native gust forms, an ice-tinted swirl is driven across to the
// target, then frost glints fade on the target after each native flash. The native 50-frame hold is split 14 + 12 + 12 + 12 around
// the cues (same total). Native emitters, fades, sounds and timing unchanged.
// Donors: pokeemerald whirlwind / snowball (opal_b9_wind, `ice` palette variant), ice_crystals_0 (opal_ice, B2 sheet).
#define WIND OPAL_RES(opal_b9_wind, opal_b9_wind_ice)
#define ICE OPAL_RES(opal_ice, opal_ice)

L_0:
    LoadParticleResource 0, powder_snow_spa
    OpalSheetBegin 1, 8, WIND
    OpalSheetBegin 2, 4, ICE
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_BLACK
    OpalImpactBurst 1, WIND, OPAL_B9_WIND_SEQ_FLECKS, BATTLE_ANIM_ATTACKER, 100, 8, -10, 14, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 1, WIND, OPAL_B9_WIND_SEQ_FLECKS, BATTLE_ANIM_ATTACKER, 80, 14, 2, 14, OPAL_FX_FLAG_TRANSLUCENT
    WaitForAnimTasks
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 6, 5, 0, 0
    OpalFx 1, WIND, OPAL_B9_WIND_SEQ_SWIRL, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 22, 16, -4, -6, 0, 0, 100, OPAL_FX_FLAG_TRANSLUCENT
    Delay 5
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_WHITE, 14, 0
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER_PARTNER, 0, 1, BATTLE_COLOR_WHITE, 14, 0
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER_SIDE
    Func_Shake 2, 0, 1, 10, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 2, 0, 1, 10, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    PlayLoopedSoundEffectR SEQ_SE_DP_150, 3, 8
    OpalImpactBurst 2, ICE, OPAL_ICE_SEQ_GLINT, BATTLE_ANIM_DEFENDER, 120, -8, -8, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 14
    OpalImpactBurst 1, WIND, OPAL_B9_WIND_SEQ_FLECKS, BATTLE_ANIM_DEFENDER, 100, 8, -12, 14, OPAL_FX_FLAG_TRANSLUCENT
    Delay 12
    OpalImpactBurst 2, ICE, OPAL_ICE_SEQ_GLINT, BATTLE_ANIM_DEFENDER, 100, 8, 4, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 12
    OpalImpactBurst 1, WIND, OPAL_B9_WIND_SEQ_FLECKS, BATTLE_ANIM_DEFENDER, 90, -10, 6, 14, OPAL_FX_FLAG_TRANSLUCENT
    Delay 12
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_WHITE, 14, 0
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER_PARTNER, 0, 1, BATTLE_COLOR_WHITE, 14, 0
    Func_Shake 2, 0, 1, 10, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 2, 0, 1, 10, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    PlayLoopedSoundEffectR SEQ_SE_DP_W258, 6, 2
    OpalImpactBurst 2, ICE, OPAL_ICE_SEQ_GLINT, BATTLE_ANIM_DEFENDER, 130, 0, -2, 0, OPAL_FX_FLAG_TRANSLUCENT
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    End
