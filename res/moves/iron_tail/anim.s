#include "macros/btlanimcmd.inc"

// Opal B3/B5 physical exemplar: FOCUS_ATTACKER during the metal charge, IMPACT_PUNCH + REACT_HEAVY on the confirmed hit.
// Native emitters, sounds and timing unchanged. Donor: procedural opal_fx_ring (steel palette).
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_steel)

L_0:
    LoadParticleResource 0, iron_tail_spa
    OpalSheetBegin 1, 4, RING
    OpalCamFocusAttacker
    PlayLoopedSoundEffectL SEQ_SE_DP_W231, 8, 2
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_ATTACKER
    InitPokemonSpriteManager
    LoadPokemonSpriteDummyResources 0
    LoadPokemonSpriteDummyResources 1
    AddPokemonSprite BATTLER_ROLE_ATTACKER, FALSE, BATTLE_ANIM_MON_SPRITE_0, 0
    AddPokemonSprite BATTLER_ROLE_ATTACKER, FALSE, BATTLE_ANIM_MON_SPRITE_1, 0
    AddPokemonSprite BATTLER_ROLE_ATTACKER_PARTNER, FALSE, BATTLE_ANIM_MON_SPRITE_2, 1
    Func_StatChangeMetal STAT_CHANGE_MODE_ATTACKER
    WaitForAnimTasks
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_0
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_1
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_2
    FreePokemonSpriteManager
    Delay 30
    PlaySoundEffectR SEQ_SE_DP_BRADE
    PlayDelayedSoundEffectR SEQ_SE_DP_W025B, 6
    CreateEmitter 0, 3, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalReactHeavy 1, RING, BATTLE_ANIM_DEFENDER
    WaitForAllEmitters
    OpalSheetEnd 1
    UnloadParticleSystem 0
    End
