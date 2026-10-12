#include "macros/btlanimcmd.inc"

// Opal B9 (P0, rock_projectile): a lobbed boulder with trailing grit crosses on an arc and lands on the native impact frame
// (12 + 8 = 20), where it breaks into fragments, a Ranger dust burst and a light camera punch; the native vertical shake is kept.
// Native emitters, sounds and the 20-frame cadence are unchanged (launch is async, travel = 20 frames).
// Donors: pokeemerald rocks / flat_rock / flying_dirt (opal_b9_rock), Ranger 2 e002 (ranger_rock_burst, B1 install).
#define ROCK OPAL_RES(opal_b9_rock, opal_b9_rock)
#define DUST OPAL_RES(ranger_rock_burst, ranger_rock_burst)

L_0:
    LoadParticleResource 0, rock_throw_spa
    OpalSheetBegin 1, 8, ROCK
    OpalSheetBegin 2, 2, DUST
    OpalFx 1, ROCK, OPAL_B9_ROCK_SEQ_BOULDER, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 20, 10, -6, 0, -4, 0, 90, OPAL_FX_FLAG_HOLD_LAST
    OpalFx 1, ROCK, OPAL_B9_ROCK_SEQ_SHARDS, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER, 20, 6, -4, 0, -6, 12, 100, 0
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 2, EMITTER_CB_SET_POS_TO_DEFENDER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_DEFENDER
    Delay 12
    PlaySoundEffectR SEQ_SE_DP_W088
    Delay 8
    PlaySoundEffectR SEQ_SE_DP_W070
    OpalImpactBurst 1, ROCK, OPAL_B9_ROCK_SEQ_BREAK, BATTLE_ANIM_DEFENDER, 130
    OpalImpactBurst 1, ROCK, OPAL_B9_ROCK_SEQ_DIRT, BATTLE_ANIM_DEFENDER, 110, 0, 10, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalImpactBurst 2, DUST, 0, BATTLE_ANIM_DEFENDER, 80, 0, 6, 24, OPAL_FX_FLAG_TRANSLUCENT
    OpalCamPunch
    Func_Shake 0, 1, 1, 8, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    WaitForAnimTasks
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    End
