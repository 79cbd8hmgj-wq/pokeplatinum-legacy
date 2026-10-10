#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, flame_wheel_spa
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_ATTACKER
    PlayLoopedSoundEffectL SEQ_SE_DP_W172, 3, 12
    Delay 20
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 1, BATTLE_COLOR_RED, 12, 
    WaitForAnimTasks
    Func_MoveBattlerX2 3, 24, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_RED, 12, 
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_W172B
    // Donor sprite: Pokemon Ranger 2 e010 fireball-flare (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_fire_bloom.provenance.json).
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_fire_bloom_NCGR_lz
    LoadPlttRes 0, ranger_fire_bloom_NCLR, 1
    LoadCellResObj 0, ranger_fire_bloom_cell_NCER_lz
    LoadAnimResObj 0, ranger_fire_bloom_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_fire_bloom_NCGR_lz, ranger_fire_bloom_NCLR, ranger_fire_bloom_cell_NCER_lz, ranger_fire_bloom_anim_NANR_lz, 0, 0, 0, -8
    WaitForAnimTasks
    Func_MoveBattlerX2 3, -24, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    WaitForAnimTasks
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    UnloadParticleSystem 0
    End
