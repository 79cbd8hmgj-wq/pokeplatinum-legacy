#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, aurora_beam_spa
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W062, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 6, 1, 4096, 0
    SetExtraParams 3, 0, 0, 0, 0
    Delay 10
    Func_Shake 1, 0, 1, 4, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    // Donor sprite: Pokemon Ranger 2 e009 frost-flare (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_ice_bloom.provenance.json)
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_ice_bloom_NCGR_lz
    LoadPlttRes 0, ranger_ice_bloom_NCLR, 1
    LoadCellResObj 0, ranger_ice_bloom_cell_NCER_lz
    LoadAnimResObj 0, ranger_ice_bloom_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_ice_bloom_NCGR_lz, ranger_ice_bloom_NCLR, ranger_ice_bloom_cell_NCER_lz, ranger_ice_bloom_anim_NANR_lz, 0, 0, 0, -4
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    End
