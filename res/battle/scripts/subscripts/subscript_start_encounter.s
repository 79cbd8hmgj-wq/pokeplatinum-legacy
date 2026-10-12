#include "macros/btlcmd.inc"


_000:
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_TYPE, BATTLE_TYPE_TRAINER, _118
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_TYPE, BATTLE_TYPE_SAFARI, _215
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_TYPE, BATTLE_TYPE_PAL_PARK, _237
    SetPokemonEncounter BTLSCR_ENEMY
    SetTrainerEncounter BTLSCR_PLAYER
    PlayEncounterAnimation 
    WaitTime 122
    // Opal B7: presentation-only arrival cue, gated read-only on flags/species the engine already set (see _opal_cue)
    GoTo _opal_cue

_opal_cue_done:
    HealthBoxSlideInDelay BTLSCR_ENEMY
    Wait 
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_DISTORTION, _073
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_LEGENDARY, _067
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_FIRST_BATTLE, _055
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_HONEY_TREE, _061
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_TYPE, BATTLE_TYPE_DOUBLES, _079
    // A wild {0} appeared!
    PrintGlobalMessage BattleStrings_Text_AWildPokemonAppeared, TAG_NICKNAME, BTLSCR_ENEMY
    GoTo _084

_055:
    // Whoa! A wild {0} came charging!
    PrintGlobalMessage BattleStrings_Text_WhoaAWildPokemonCameCharging, TAG_NICKNAME, BTLSCR_ENEMY
    GoTo _084

_061:
    // A wild {0} appeared from the tree you slathered with Honey!
    PrintGlobalMessage BattleStrings_Text_AWildPokemonAppearedFromTheTreeYouSlatheredWithHoney, TAG_NICKNAME, BTLSCR_ENEMY
    GoTo _084

_067:
    // A wild {0} appeared!
    PrintGlobalMessage BattleStrings_Text_AWildPokemonAppeared3, TAG_NICKNAME, BTLSCR_ENEMY
    GoTo _084

_073:
    // The Distortion World’s {0} appeared!
    PrintGlobalMessage BattleStrings_Text_TheDistortionWorldsPokemonAppeared, TAG_NICKNAME, BTLSCR_ENEMY
    GoTo _084

_079:
    // A wild {0} and {1} appeared!
    PrintGlobalMessage BattleStrings_Text_AWildPokemonAndPokemonAppeared, TAG_NICKNAME_NICKNAME, BTLSCR_ENEMY_SLOT_1, BTLSCR_ENEMY_SLOT_2

_084:
    Wait 
    WaitButtonABTime 30
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_TYPE, BATTLE_TYPE_2vs2, _098
    // Go! {0}!
    PrintMessage BattleStrings_Text_GoPokemon, TAG_NICKNAME, BTLSCR_PLAYER
    GoTo _100

_098:
    PrintFirstSendOutMessage BTLSCR_PLAYER

_100:
    SpriteToOAM BTLSCR_ENEMY
    Wait 
    ThrowPokeball BTLSCR_PLAYER, BTLSCR_THROW_POKE_BALL
    PokemonSlideIn BTLSCR_PLAYER
    WaitTime 96
    HealthBoxSlideInDelay BTLSCR_PLAYER
    Wait 
    OAMToSprite BTLSCR_ENEMY
    Wait 
    GoTo _258

_118:
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_RECORDED, _169
    PlayEncounterAnimation 
    SetTrainerEncounter BTLSCR_ALL_BATTLERS
    WaitTime 96
    LoadPartyGaugeGraphics 
    ShowBattleStartPartyGauge BTLSCR_ENEMY
    ShowBattleStartPartyGauge BTLSCR_PLAYER
    PrintEncounterMessage BTLSCR_ENEMY
    Wait 
    WaitButtonABTime 30
    PrintFirstSendOutMessage BTLSCR_ENEMY
    HideBattleStartPartyGauge BTLSCR_ENEMY
    ThrowPokeball BTLSCR_ENEMY, BTLSCR_THROW_POKE_BALL
    PokemonSlideIn BTLSCR_ENEMY
    WaitTime 112
    HealthBoxSlideInDelay BTLSCR_ENEMY
    Wait 
    PrintFirstSendOutMessage BTLSCR_PLAYER
    HideBattleStartPartyGauge BTLSCR_PLAYER
    ThrowPokeball BTLSCR_PLAYER, BTLSCR_THROW_POKE_BALL
    PokemonSlideIn BTLSCR_PLAYER
    WaitTime 96
    HealthBoxSlideInDelay BTLSCR_PLAYER
    Wait 
    FreePartyGaugeGraphics 
    GoTo _258

_169:
    PlayEncounterAnimation 
    SetTrainerEncounter BTLSCR_ALL_BATTLERS
    WaitTime 96
    LoadPartyGaugeGraphics 
    ShowBattleStartPartyGauge BTLSCR_ENEMY
    ShowBattleStartPartyGauge BTLSCR_PLAYER
    PrintEncounterMessage BTLSCR_ENEMY
    Wait 
    WaitButtonABTime 30
    PrintFirstSendOutMessage BTLSCR_PLAYER
    HideBattleStartPartyGauge BTLSCR_PLAYER
    ThrowPokeball BTLSCR_PLAYER, BTLSCR_THROW_POKE_BALL
    PokemonSlideIn BTLSCR_PLAYER
    WaitTime 96
    HealthBoxSlideInDelay BTLSCR_PLAYER
    Wait 
    PrintFirstSendOutMessage BTLSCR_ENEMY
    HideBattleStartPartyGauge BTLSCR_ENEMY
    ThrowPokeball BTLSCR_ENEMY, BTLSCR_THROW_POKE_BALL
    PokemonSlideIn BTLSCR_ENEMY
    WaitTime 112
    HealthBoxSlideInDelay BTLSCR_ENEMY
    Wait 
    FreePartyGaugeGraphics 
    GoTo _258

_215:
    SetPokemonEncounter BTLSCR_ENEMY
    SetTrainerEncounter BTLSCR_PLAYER
    PlayEncounterAnimation 
    WaitTime 122
    HealthBoxSlideInDelay BTLSCR_ENEMY
    Wait 
    // A wild {0} appeared!
    PrintGlobalMessage BattleStrings_Text_AWildPokemonAppeared, TAG_NICKNAME, BTLSCR_ENEMY
    Wait 
    HealthBoxSlideIn BTLSCR_PLAYER
    WaitButtonABTime 7
    Wait 
    GoTo _258

_237:
    SetPokemonEncounter BTLSCR_ENEMY
    SetTrainerEncounter BTLSCR_PLAYER
    PlayEncounterAnimation 
    WaitTime 122
    HealthBoxSlideInDelay BTLSCR_ENEMY
    Wait 
    // Wow! {0}’s {1} is drawing close!
    PrintGlobalMessage BattleStrings_Text_01219, TAG_TRNAME_NICKNAME, BTLSCR_ENEMY, BTLSCR_ENEMY
    Wait 
    HealthBoxSlideIn BTLSCR_PLAYER
    WaitButtonABTime 7
    Wait 

_258:
    SetBattleBackground 
    End 

// Opal B7 cinematic encounter cues. Reads BATTLE_STATUS_* and the enemy species only; writes nothing. Every path returns to
// _opal_cue_done, so ordinary wild battles (no LEGENDARY flag) fall straight through with no extra frames.
_opal_cue:
    CompareVarToValue OPCODE_FLAG_NOT, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_LEGENDARY, _opal_cue_done
    CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_GIRATINA, _opal_cue_giratina
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_DIALGA, _opal_cue_dialga
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_PALKIA, _opal_cue_palkia
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_UXIE, _opal_cue_uxie
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_MESPRIT, _opal_cue_mesprit
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_AZELF, _opal_cue_azelf
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_GIRATINA, _opal_cue_legend
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_DARKRAI, _opal_cue_legend
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_SHAYMIN, _opal_cue_legend
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_ARCEUS, _opal_cue_legend
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_CRESSELIA, _opal_cue_legend
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_REGIGIGAS, _opal_cue_legend
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ENEMY, BATTLEMON_SPECIES, SPECIES_HEATRAN, _opal_cue_legend
    GoTo _opal_cue_done

_opal_cue_giratina:
    PlayBattleAnimation BTLSCR_ENEMY, BATTLE_ANIMATION_ENCOUNTER_GIRATINA
    Wait 
    GoTo _opal_cue_done

_opal_cue_dialga:
    PlayBattleAnimation BTLSCR_ENEMY, BATTLE_ANIMATION_ENCOUNTER_DIALGA
    Wait 
    GoTo _opal_cue_done

_opal_cue_palkia:
    PlayBattleAnimation BTLSCR_ENEMY, BATTLE_ANIMATION_ENCOUNTER_PALKIA
    Wait 
    GoTo _opal_cue_done

_opal_cue_uxie:
    PlayBattleAnimation BTLSCR_ENEMY, BATTLE_ANIMATION_ENCOUNTER_UXIE
    Wait 
    GoTo _opal_cue_done

_opal_cue_mesprit:
    PlayBattleAnimation BTLSCR_ENEMY, BATTLE_ANIMATION_ENCOUNTER_MESPRIT
    Wait 
    GoTo _opal_cue_done

_opal_cue_azelf:
    PlayBattleAnimation BTLSCR_ENEMY, BATTLE_ANIMATION_ENCOUNTER_AZELF
    Wait 
    GoTo _opal_cue_done

_opal_cue_legend:
    PlayBattleAnimation BTLSCR_ENEMY, BATTLE_ANIMATION_ENCOUNTER_LEGEND
    Wait 
    GoTo _opal_cue_done
