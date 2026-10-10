#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, ice_beam_spa
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 8, BATTLE_COLOR_LIGHT_BLUE
    WaitForAnimTasks
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 6, 1, 0, 0
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_025, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Delay 15
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    // B1: lingering ice-crystal impact after the initial beam.
    Delay 3
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    // Donor sprite: Pokemon Ranger 2 e009 frost-flare (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_ice_bloom.provenance.json)
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_ice_bloom_NCGR_lz
    LoadPlttRes 0, ranger_ice_bloom_NCLR, 1
    LoadCellResObj 0, ranger_ice_bloom_cell_NCER_lz
    LoadAnimResObj 0, ranger_ice_bloom_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_ice_bloom_NCGR_lz, ranger_ice_bloom_NCLR, ranger_ice_bloom_cell_NCER_lz, ranger_ice_bloom_anim_NANR_lz, 0, 0, 0, -4
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 8, 0, BATTLE_COLOR_LIGHT_BLUE
    WaitForAnimTasks
    End
