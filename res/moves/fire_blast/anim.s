#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, fire_blast_spa
    LoadParticleResource 1, fire_blast_spa
    CreateEmitter 0, 5, EMITTER_CB_SET_POS_TO_ATTACKER
    PlayLoopedSoundEffectL SEQ_SE_DP_W172, 4, 10
    Delay 20
    CreateEmitterEx 0, 1, 6, EMITTER_CB_SET_POS_TO_ATTACKER
    Func_MoveEmitterA2BLinear 1, 0, 0, 0, 19, 64
    Delay 25
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 4, EMITTER_CB_SET_POS_TO_DEFENDER
    Delay 5
    ResetVars
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    SwitchBg 22, BATTLE_BG_SWITCH_MODE_FADE
    StopSoundEffect SEQ_SE_DP_W172
    PlaySoundEffectR SEQ_SE_DP_W172B
    Delay 10
    PlaySoundEffectR SEQ_SE_DP_W120
    // Donor sprite: Pokemon Ranger 2 e010 fireball-flare (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_fire_bloom.provenance.json).
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_fire_bloom_NCGR_lz
    LoadPlttRes 0, ranger_fire_bloom_NCLR, 1
    LoadCellResObj 0, ranger_fire_bloom_cell_NCER_lz
    LoadAnimResObj 0, ranger_fire_bloom_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_fire_bloom_NCGR_lz, ranger_fire_bloom_NCLR, ranger_fire_bloom_cell_NCER_lz, ranger_fire_bloom_anim_NANR_lz, 0, 0, 0, -8
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 2, BATTLE_COLOR_RED, 10, 0
    Func_Shake 2, 0, 1, 8, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_ShakeBg 2, 1, 0, 2, 0, SHAKE_BG_TARGET_BASE
    WaitForAnimTasks
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    UnloadParticleSystem 0
    SetVar BATTLE_ANIM_VAR_BG_SCREEN_MODE, 1
    RestoreBg 22, BATTLE_BG_SWITCH_MODE_FADE
    WaitForBgSwitch
    End
