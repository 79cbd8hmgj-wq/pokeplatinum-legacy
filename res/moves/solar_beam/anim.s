#include "macros/btlanimcmd.inc"

// Opal B2: TWO_TURN_LIGHT_CHARGE
// The engine selects the charge or release call (JumpIfEffectChanceOdd); this script never decides whether a charge
// turn happens, so sunlight's instant-use rule is untouched and an interrupted charge simply never reaches the release path.
//   charge   (L_1) converging green-gold rings and light motes around the attacker, softened backdrop dim, camera focus
//   release  (L_2) gold ring + star burst on the attacker, luminous beam trail attacker -> defender, bright impact + warm pulse
// Donor: procedural opal_fx_ring (solar / gold palettes)
#define RING_SOLAR OPAL_RES(opal_fx_ring, opal_fx_ring_solar)
#define RING_GOLD  OPAL_RES(opal_fx_ring, opal_fx_ring_gold)

L_0:
    LoadParticleResource 0, solar_beam_spa
    JumpIfEffectChanceOdd L_1, L_2
    End

L_1:
    OpalSheetBegin 1, 8, RING_SOLAR
    OpalCamFocusAttacker
    OpalDimIn BATTLE_COLOR_DARK_BLUE, 9, 1
    WaitForAnimTasks
    CreateEmitter 0, 19, EMITTER_CB_SET_POS_TO_ATTACKER
    OpalChargeAura 1, RING_SOLAR, OPAL_RING_SEQ_CONVERGE, 0, 230, BATTLE_ANIM_ATTACKER
    Delay 10
    PlaySoundEffectL SEQ_SE_DP_SHUSHU
    OpalChargeAura 1, RING_SOLAR, OPAL_RING_SEQ_CONVERGE, 0, 160, BATTLE_ANIM_ATTACKER
    OpalResidual 1, RING_SOLAR, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_ATTACKER, 24, 100, -14, 6
    OpalResidual 1, RING_SOLAR, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_ATTACKER, 24, 100, 14, 10
    Delay 20
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 2, BATTLE_COLOR_LIGHT_YELLOW1, 10, 0
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    WaitForAnimTasks
    OpalDimOut BATTLE_COLOR_DARK_BLUE, 9, 1
    WaitForAnimTasks
    End

L_2:
    OpalSheetBegin 1, 8, RING_GOLD
    OpalCamFocusAttacker
    OpalDimIn BATTLE_COLOR_DARK_BLUE, 8, 1
    WaitForAnimTasks
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 8, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 9, EMITTER_CB_SET_POS_TO_ATTACKER
    OpalImpactBurst 1, RING_GOLD, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_ATTACKER, 220, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 5
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W076B, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    OpalProjectile 1, RING_GOLD, OPAL_RING_SEQ_DOT_PULSE, 15, 160, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalCamFollow 15
    Delay 15
    CreateEmitter 0, 10, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 11, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, RING_GOLD, OPAL_RING_SEQ_STAR_POP, BATTLE_ANIM_DEFENDER, 300, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 1, RING_GOLD, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 240, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 5
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 2, BATTLE_COLOR_LIGHT_YELLOW1, 14, 0
    Func_Shake 4, 0, 1, 12, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_ShakeBg 2, 0, 0, 2, 0, SHAKE_BG_TARGET_BASE
    OpalWeatherAccent
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalWeatherAccentEnd 2
    UnloadParticleSystem 0
    OpalDimOut BATTLE_COLOR_DARK_BLUE, 8, 1
    WaitForAnimTasks
    End

    OpalWeatherAccentSub 2
