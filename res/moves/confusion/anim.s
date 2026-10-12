#include "macros/btlanimcmd.inc"

// Opal B9 (P0, psychic_small): two concentric, translucent psychic rings ripple out of the target alongside the native warp
// and a soft magenta pulse dissolves on it. Native background switch, warp task, sounds and timing unchanged; the cues are asynchronous.
// Donors: procedural Opal ring (opal_fx_ring_psychic, B2 sheet).
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_psychic)

L_0:
    SwitchBg 20, BATTLE_BG_SWITCH_MODE_FADE
    WaitForBgSwitch
    OpalSheetBegin 1, 4, RING
    InitPokemonSpriteManager
    LoadPokemonSpriteDummyResources 0
    AddPokemonSprite BATTLER_ROLE_DEFENDER, FALSE, BATTLE_ANIM_MON_SPRITE_0, 0
    Func_Shake 2, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_ATTACKER
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 1, BATTLE_COLOR_WHITE, 4
    Delay 10
    PlaySoundEffectR SEQ_SE_DP_480
    LoadPokemonSpriteDummyResources 4
    AddPokemonSprite BATTLER_ROLE_DEFENDER_PARTNER, FALSE, BATTLE_ANIM_MON_SPRITE_4, 4
    BtlAnimCmd_082 3, 0, 4
    Func_Confusion
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 90, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 150, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalReactMagic 0x725F, BATTLE_ANIM_DEFENDER
    WaitForAnimTasks
    OpalSheetEnd 1
    FreePokemonSpriteManager
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_0
    BtlAnimCmd_083 0
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_4
    RestoreBg 20, BATTLE_BG_SWITCH_MODE_FADE
    WaitForBgSwitch
    End
