#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, flamethrower_spa
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 6, 1, 0, 0
    PlaySoundEffectR SEQ_SE_DP_W053
    Delay 50
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 2, 0, 1, 14, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    Delay 3
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_RED, 10, 25
    // Donor sprite: Pokemon Ranger 2 e010 fireball-flare (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_fire_bloom.provenance.json).
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_fire_bloom_NCGR_lz
    LoadPlttRes 0, ranger_fire_bloom_NCLR, 1
    LoadCellResObj 0, ranger_fire_bloom_cell_NCER_lz
    LoadAnimResObj 0, ranger_fire_bloom_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_fire_bloom_NCGR_lz, ranger_fire_bloom_NCLR, ranger_fire_bloom_cell_NCER_lz, ranger_fire_bloom_anim_NANR_lz, 0, 0, 0, -8
    // B1: trailing flame bloom uses the existing impact emitter.
    Delay 3
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 2, 0, 1, 14, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    UnloadParticleSystem 0
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    End
