#include "macros/btlanimcmd.inc"

// Opal B9 (P0, speed_contact): ground dust at the launch point, a trailing wind streak with two afterimages along the dash and a
// streak-star hit flash on contact. The native dash, sounds, shake and timing are untouched (all additions are asynchronous).
// Donors: pokeemerald speed_dust / air_wave (opal_b9_wind), slash (opal_b9_strike).
#define STRIKE OPAL_RES(opal_b9_strike, opal_b9_strike)
#define WIND OPAL_RES(opal_b9_wind, opal_b9_wind)

L_0:
    LoadParticleResource 0, quick_attack_spa
    OpalSheetBegin 1, 3, STRIKE
    OpalSheetBegin 2, 6, WIND
    InitPokemonSpriteManager
    LoadPokemonSpriteDummyResources 0
    LoadPokemonSpriteDummyResources 1
    PlaySoundEffectL SEQ_SE_DP_W104
    AddPokemonSprite BATTLER_ROLE_ATTACKER, FALSE, BATTLE_ANIM_MON_SPRITE_0, 0
    AddPokemonSprite BATTLER_ROLE_ATTACKER, FALSE, BATTLE_ANIM_MON_SPRITE_1, 1
    LoadPokemonSpriteDummyResources 4
    AddPokemonSprite BATTLER_ROLE_ATTACKER_PARTNER, FALSE, BATTLE_ANIM_MON_SPRITE_4, 4
    BtlAnimCmd_082 2, 0, 4
    Func_QuickAttack
    OpalImpactBurst 2, WIND, OPAL_B9_WIND_SEQ_PUFF, BATTLE_ANIM_ATTACKER, 90, -4, 14, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalProjectile 2, WIND, OPAL_B9_WIND_SEQ_STREAK, 12, 100, 0, 0, 0, 8, 0, 8
    Delay 15
    PlaySoundEffectR SEQ_SE_DP_030
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_0
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_1
    FreePokemonSpriteManager
    BtlAnimCmd_083 0
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_4
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    OpalImpactBurst 1, STRIKE, OPAL_B9_STRIKE_SEQ_STREAK, BATTLE_ANIM_DEFENDER, 120, -4, -2
    Func_Shake 2, 0, 1, 1, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    End
