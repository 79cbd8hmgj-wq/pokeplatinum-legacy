#include "macros/btlanimcmd.inc"

// Opal B9 (P0, status_sound): a soft sound ring pulses off the user with each cry (small, then a larger one with the louder second
// cry), pale sound arcs and a jagged roar line sweep toward every resolved target. Only commands that do not wait are added, so the
// cry waits, shakes and total length are the native ones. The engine plays this animation only after the Attack drop succeeded
// (subscript_update_stat_stage: ChangeStatStage fails before PlayMoveAnimation), so no cue shows on a blocked / maxed stat.
// Donors: procedural Opal ring (opal_fx_ring_gold), pokeemerald movement_waves / noise_line (opal_b9_sense).
#define RING OPAL_RES(opal_fx_ring, opal_fx_ring_gold)
#define SENSE OPAL_RES(opal_b9_sense, opal_b9_sense)

L_0:
    LoadParticleResource 0, growl_spa
    OpalSheetBegin 1, 4, RING
    OpalSheetBegin 2, 6, SENSE
    CreateEmitter 0, 1, EMITTER_CB_SET_POS_TO_ATTACKER
    CreateEmitter 0, 0, EMITTER_CB_SET_POS_TO_ATTACKER
    PlayPokemonCry 9, -117, 100
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ATTACKER, 90, 10, -2, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalFx 2, SENSE, OPAL_B9_SENSE_SEQ_SOUND_ARC, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER_SIDE, 24, 22, -4, 0, -8, 0, 80, OPAL_FX_FLAG_TRANSLUCENT
    WaitForPokemonCries 0
    PlayPokemonCry 10, -117, 127
    OpalImpactBurst 1, RING, OPAL_RING_SEQ_FLAT_EXPAND, BATTLE_ANIM_ATTACKER, 130, 14, -2, 0, OPAL_FX_FLAG_TRANSLUCENT
    OpalFx 2, SENSE, OPAL_B9_SENSE_SEQ_SOUND_ARC, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER_SIDE, 24, 22, -4, 0, -8, 0, 110, OPAL_FX_FLAG_TRANSLUCENT
    OpalFx 2, SENSE, OPAL_B9_SENSE_SEQ_ROAR_JAG, BATTLE_ANIM_ATTACKER, BATTLE_ANIM_DEFENDER_SIDE, 20, 22, 6, 0, 8, 0, 90, OPAL_FX_FLAG_TRANSLUCENT
    Delay 5
    WaitForPokemonCries 0
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER
    Func_Shake 1, 0, 1, 2, BATTLE_ANIM_BATTLER_SPRITE_DEFENDER_PARTNER
    WaitForAllEmitters
    OpalSheetEnd 1
    OpalSheetEnd 2
    UnloadParticleSystem 0
    End
