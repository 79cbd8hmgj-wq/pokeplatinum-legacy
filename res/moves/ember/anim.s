#include "macros/btlanimcmd.inc"

// AV1: layered fire burst (ember core -> secondary embers -> dissipating glow).
// Secondary embers reuse fire_punch.spa defender emitters 0 and 2.
// Opal B9 (P0, fire_small): a three-ember volley (small flame sprites on separate arcs, launched inside the native 6-frame lead-in) and
// drifting cinders after the Ranger bloom. Native emitters, fades and timing unchanged. Donors: pokeemerald small_ember (opal_b9_ember).
#define EMBER OPAL_RES(opal_b9_ember, opal_b9_ember)
L_0:
    LoadParticleResource 0, ember_spa
    LoadParticleResource 1, fire_punch_spa
    OpalSheetBegin 1, 10, EMBER
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 8, BATTLE_COLOR_DARK_RED2
    CreateEmitter 0, 0, EMITTER_CB_GENERIC
    SetExtraParams 0, 2, 2, 0, 0, 0
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_RED, 10, 0
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    PlayLoopedSoundEffectR SEQ_SE_DP_W052, 3, 4
    OpalFx 1, EMBER, OPAL_B9_EMBER_SEQ_EMBER, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 12, 12, -2, 0, -6, 14, 100, 0
    Delay 2
    OpalFx 1, EMBER, OPAL_B9_EMBER_SEQ_EMBER, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 12, 12, 2, 0, 2, -6, 80, 0
    Delay 2
    OpalFx 1, EMBER, OPAL_B9_EMBER_SEQ_EMBER, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 12, 12, 0, 0, 8, 0, 70, 0
    Delay 2
    CreateEmitter 1, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Delay 8
    CreateEmitter 1, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    // Donor sprite: Pokemon Ranger 2 e010 fireball-flare (donor cells, docs/visual_overhaul/b1_installed_donors/ranger_fire_bloom.provenance.json).
    InitSpriteManager 0, 1, 1, 1, 1, 1, 0, 0
    LoadCharResObj 0, ranger_fire_bloom_NCGR_lz
    LoadPlttRes 0, ranger_fire_bloom_NCLR, 1
    LoadCellResObj 0, ranger_fire_bloom_cell_NCER_lz
    LoadAnimResObj 0, ranger_fire_bloom_anim_NANR_lz
    AddSpriteWithFunc 0, SPRITE_FUNC_OFFSET_AND_ANIMATE, ranger_fire_bloom_NCGR_lz, ranger_fire_bloom_NCLR, ranger_fire_bloom_cell_NCER_lz, ranger_fire_bloom_anim_NANR_lz, 0, 0, 0, -8
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_LIGHT_ORANGE, 6, 6
    OpalResidual 1, EMBER, OPAL_B9_EMBER_SEQ_EMBER_POP, BATTLE_ANIM_DEFENDER, 22, 90, -6, -4
    OpalResidual 1, EMBER, OPAL_B9_EMBER_SEQ_EMBER_POP, BATTLE_ANIM_DEFENDER, 26, 70, 8, 2
    WaitForAnimTasks
    WaitForAllEmitters
    WaitForAnimTasks
    FreeSpriteManager 0
    OpalSheetEnd 1
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 8, 0, BATTLE_COLOR_DARK_RED2
    WaitForAnimTasks
    End
