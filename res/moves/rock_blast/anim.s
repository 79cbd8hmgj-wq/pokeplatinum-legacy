#include "macros/btlanimcmd.inc"

L_0:
    LoadParticleResource 0, rock_blast_spa
    JumpIfContest L_1
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 6, 1, 0, 0
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W207, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Delay 8
    CreateEmitter 0, 2, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_W088
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

L_1:
    CreateEmitter 0, 1, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 1, 1, 0, 0
    PlayMovingSoundEffectAtkDef SEQ_SE_DP_W207, BATTLE_SOUND_PAN_LEFT, BATTLE_SOUND_PAN_RIGHT, 4, 2
    Delay 8
    CreateEmitter 0, 2, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    PlaySoundEffectR SEQ_SE_DP_W088
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
