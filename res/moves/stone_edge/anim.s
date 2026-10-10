#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, stone_edge_spa
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    PlayLoopedSoundEffectR SEQ_SE_DP_W088, 2, 4
    Delay 25
    Func_Shake 2, 0, 1, 6, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_ShakeBg 2, 1, 0, 2, 0, SHAKE_BG_TARGET_BASE
    PlaySoundEffectR SEQ_SE_DP_W082
    // B1: collapsing stone fragments follow the main rock impact.
    Delay 4
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    PlayLoopedSoundEffectR SEQ_SE_DP_W088, 6, 3
    // Donor sprite: Pokemon Ranger 2 e002 rock shatter (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_rock_burst.provenance.json)
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_rock_burst_NCGR_lz
    LoadPlttRes 0, ranger_rock_burst_NCLR, 1
    LoadCellResObj 0, ranger_rock_burst_cell_NCER_lz
    LoadAnimResObj 0, ranger_rock_burst_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_rock_burst_NCGR_lz, ranger_rock_burst_NCLR, ranger_rock_burst_cell_NCER_lz, ranger_rock_burst_anim_NANR_lz, 0, 0, 0, 0
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    UnloadParticleSystem 0
    End
