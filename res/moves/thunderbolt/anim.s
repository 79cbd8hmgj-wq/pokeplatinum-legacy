#include "macros/btlanimcmd.inc"

// Opal B2 canonical composite: ELECTRIC_CHARGE_CHAIN
//   charge     attacker sparks converge, backdrop dims toward blue, restrained camera focus
//   release    native thunderbolt emitters keep their original timing; forked bolt layered on the defender
//   impact     spark burst + short backdrop light pulse + camera punch on the confirmed hit
//   afterglow  residual sparks taper, every fade/sprite resource is restored
// Donor: pokeemerald lightning_2 / electricity (docs/visual_overhaul/opal_installed_fx/opal_thunder.provenance.json)
#define THUNDER OPAL_RES(opal_thunder, opal_thunder)

L_0:
    LoadParticleResource 0, thunderbolt_spa
    OpalSheetBegin 0, 8, THUNDER
    OpalCamFocusAttacker
    OpalChargeAura 0, THUNDER, OPAL_THUNDER_SEQ_SPARKS, 14, 140
    OpalDimIn BATTLE_COLOR_DARK_BLUE, 5, 2
    WaitForAnimTasks
    OpalDimOut BATTLE_COLOR_DARK_BLUE, 5, 1
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_KAMI
    OpalFx 0, THUNDER, OPAL_THUNDER_SEQ_BOLT, BATTLE_ANIM_DEFENDER, 0, 14, 0, -30, 0, 0, 0, 200, 0
    Delay 5
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_BLACK, 15, 0
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 1, 0, 1, 4, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    OpalImpactBurst 0, THUNDER, OPAL_THUNDER_SEQ_SPARKS, BATTLE_ANIM_DEFENDER, 190
    OpalCamPunch
    OpalLightPulse BATTLE_COLOR_LIGHT_YELLOW1, 4
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    PlayDelayedSoundEffectR SEQ_SE_DP_W063B, 50
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    OpalWeatherAccent
    Delay 3
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalResidual 0, THUNDER, OPAL_THUNDER_SEQ_SPARKS, BATTLE_ANIM_DEFENDER, 24, 110, 0, -6
    WaitForAllEmitters
    OpalSheetEnd 0
    OpalWeatherAccentEnd 1
    UnloadParticleSystem 0
    WaitForAnimTasks
    End

    OpalWeatherAccentSub 1
