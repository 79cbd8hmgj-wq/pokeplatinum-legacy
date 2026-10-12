#include "macros/btlanimcmd.inc"

// Opal B2: CRYSTALLINE_BEAM
//   charge   cold backdrop (native light-blue fade) + glint sparkles at the attacker, camera focus
//   strike   native beam emitter follows; ice shards burst on the defender, delayed second shatter offset for sharp fragments
//   aftermath frost glints drift; hail flecks only when hail is active. No freeze visual: nothing here depends on status.
// Donors: pokeemerald ice_chunk / ice_crystals_0 (opal_ice), pokeranger2 e009 (ranger_ice_bloom, B1)
#define ICE OPAL_RES(opal_ice, opal_ice)

L_0:
    LoadParticleResource 0, ice_beam_spa
    OpalSheetBegin 1, 8, ICE
    OpalCamFocusAttacker
    OpalDimIn BATTLE_COLOR_LIGHT_BLUE, 8, 1
    OpalChargeAura 1, ICE, OPAL_ICE_SEQ_GLINT, 16, 130, BATTLE_ANIM_ATTACKER, 10, -10
    WaitForAnimTasks
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 6, 1, 0, 0
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_025, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    OpalCamFollow 15
    Delay 15
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, ICE, OPAL_ICE_SEQ_SHATTER, BATTLE_ANIM_DEFENDER, 160, 0, -4
    OpalCamPunch
    // B1: lingering ice-crystal impact after the initial beam.
    Delay 3
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, ICE, OPAL_ICE_SEQ_SHATTER, BATTLE_ANIM_DEFENDER, 110, 14, 10, 0, OPAL_FX_FLAG_TRANSLUCENT | OPAL_FX_FLAG_MIRROR
    // Donor sprite: Pokemon Ranger 2 e009 frost-flare (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_ice_bloom.provenance.json)
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_ice_bloom_NCGR_lz
    LoadPlttRes 0, ranger_ice_bloom_NCLR, 1
    LoadCellResObj 0, ranger_ice_bloom_cell_NCER_lz
    LoadAnimResObj 0, ranger_ice_bloom_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_ice_bloom_NCGR_lz, ranger_ice_bloom_NCLR, ranger_ice_bloom_cell_NCER_lz, ranger_ice_bloom_anim_NANR_lz, 0, 0, 0, -4
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    OpalResidual 1, ICE, OPAL_ICE_SEQ_GLINT, BATTLE_ANIM_DEFENDER, 22, 110, -12, -16
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    OpalWeatherAccent
    OpalSheetEnd 1
    OpalWeatherAccentEnd 2
    UnloadParticleSystem 0
    OpalDimOut BATTLE_COLOR_LIGHT_BLUE, 8, 1
    WaitForAnimTasks
    End

    OpalWeatherAccentSub 2
