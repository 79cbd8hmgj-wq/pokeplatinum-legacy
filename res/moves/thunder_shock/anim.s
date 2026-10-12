#include "macros/btlanimcmd.inc"

// AV1: branching secondary arcs and a layered defender flash accent.
// Branching arcs reuse thunderbolt.spa defender emitters 0, 1 and 3.
// Opal B9 (P0, electric_small): a short spark charge at the user during the native dim, three horizontal zig-zag arcs that jump
// across the target (offset and staggered inside the native 5 / 4 / 5 frame gaps) and a small spark burst; scaled well below
// Thunderbolt so the two read differently. Native emitters, fades, sounds and timing unchanged.
// Donors: pokeemerald electricity / electric_orbs (opal_thunder, B2 sheet), spark_h (opal_b9_ember).
#define THUNDER OPAL_RES(opal_thunder, opal_thunder)
#define ARCS OPAL_RES(opal_b9_ember, opal_b9_ember)

L_0:
    LoadParticleResource 0, thunder_shock_spa
    LoadParticleResource 1, thunderbolt_spa
    OpalSheetBegin 1, 4, THUNDER
    OpalSheetBegin 2, 6, ARCS
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 0, 12, BATTLE_COLOR_BLACK
    OpalChargeAura 1, THUNDER, OPAL_THUNDER_SEQ_SPARKS, 12, 90
    WaitForAnimTasks
    PlaySoundEffectR SEQ_SE_DP_W085
    PlayDelayedSoundEffectR SEQ_SE_DP_W063B, 13
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalFx 2, ARCS, OPAL_B9_EMBER_SEQ_SPARK_ARC, BATTLE_ANIM_DEFENDER, 0, 14, 0, -10, 0, 0, 0, 110, OPAL_FX_FLAG_TRANSLUCENT
    Delay 5
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_BLACK, 15, 0
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    OpalFx 2, ARCS, OPAL_B9_EMBER_SEQ_SPARK_ARC, BATTLE_ANIM_DEFENDER, 0, 12, 0, 6, 0, 0, 0, 100, OPAL_FX_FLAG_TRANSLUCENT
    Delay 4
    CreateEmitter 1, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_LIGHT_YELLOW1, 12, 0
    OpalFx 2, ARCS, OPAL_B9_EMBER_SEQ_SPARK_ARC, BATTLE_ANIM_DEFENDER, 0, 10, 0, -14, 0, 0, 0, 90, OPAL_FX_FLAG_TRANSLUCENT
    Delay 5
    CreateEmitter 1, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    OpalImpactBurst 1, THUNDER, OPAL_THUNDER_SEQ_SPARKS, BATTLE_ANIM_DEFENDER, 110
    Delay 5
    CreateEmitter 1, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_DEFENDER, 0, 1, BATTLE_COLOR_LIGHT_YELLOW2, 8, 6
    OpalResidual 1, THUNDER, OPAL_THUNDER_SEQ_SPARKS, BATTLE_ANIM_DEFENDER, 18, 80, 0, -4
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    UnloadParticleSystem 1
    Func_FadeBg FADE_BG_TYPE_BASE, 1, 12, 0, BATTLE_COLOR_BLACK
    WaitForAnimTasks
    End
