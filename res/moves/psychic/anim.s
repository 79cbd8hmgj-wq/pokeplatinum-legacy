#include "macros/btlanimcmd.inc"

// Opal B2: PSYCHIC_LENSING
//   pulse   translucent pink rings expand around the attacker while it flashes (native), deliberate stagger
//   strike  paired rings on the defender as the native confusion wobble + BG warp run; rings are battler-plane only (HUD untouched)
// The native effect-BG switch (52) and Func_Confusion are unchanged; no base-BG fade is layered on top of them.
// Donor: procedural opal_fx_ring (psychic palette)
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_psychic)

L_0:
    OpalSheetBegin 1, 8, RING
    InitPokemonSpriteManager
    LoadPokemonSpriteDummyResources 0
    AddPokemonSprite BATTLER_ROLE_DEFENDER, FALSE, BATTLE_ANIM_MON_SPRITE_0, 0
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 8
    SwitchBg 52, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_MOVE
    WaitForBgSwitch
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_FadeBattlerSprite BATTLE_ANIM_ATTACKER, 0, 1, BATTLE_COLOR_LIGHT_YELLOW1, 10, 0
    OpalChargeAura 1, RING, OPAL_RING_SEQ_EXPAND, 0, 160, BATTLE_ANIM_ATTACKER
    Delay 5
    OpalChargeAura 1, RING, OPAL_RING_SEQ_EXPAND, 0, 220, BATTLE_ANIM_ATTACKER
    Delay 5
    LoadPokemonSpriteDummyResources 4
    AddPokemonSprite BATTLER_ROLE_DEFENDER_PARTNER, FALSE, BATTLE_ANIM_MON_SPRITE_4, 4
    BtlAnimCmd_082 3, 0, 4
    PlayLoopedSoundEffectR SEQ_SE_DP_480, 4, 2
    Func_Confusion
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_CONVERGE, BATTLE_ANIM_DEFENDER, 230, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    Delay 8
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_EXPAND, BATTLE_ANIM_DEFENDER, 190, 0, 0, 0, OPAL_FX_FLAG_TRANSLUCENT
    WaitForAnimTasks
    OpalSheetEnd 1
    FreePokemonSpriteManager
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_0
    BtlAnimCmd_083 0
    RemovePokemonSprite BATTLE_ANIM_MON_SPRITE_4
    SetVar BATTLE_ANIM_VAR_BG_MOVE_STEP_Y, 8
    RestoreBg 52, BATTLE_BG_SWITCH_MODE_FADE | BATTLE_BG_SWITCH_FLAG_STOP
    WaitForBgSwitch
    End
