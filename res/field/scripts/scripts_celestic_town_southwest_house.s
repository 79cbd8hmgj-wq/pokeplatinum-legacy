#include "macros/scrcmd.inc"
#include "res/text/bank/celestic_town_southwest_house.h"


    ScriptEntry CelesticTownPokecenter1F_BlackBelt
    ScriptEntry CelesticTownPokecenter1F_Happiny
    ScriptEntryEnd

CelesticTownPokecenter1F_BlackBelt:
    PlaySE SEQ_SE_CONFIRM
    LockAll
    FacePlayer
    CheckPoketchAppRegistered POKETCH_APPID_ANALOGWATCH, VAR_RESULT
    GoToIfEq VAR_RESULT, TRUE, CelesticTownSoutheastHouse_CheckGifts
    Message CelesticTownSoutheastHouse_Text_TakeThisFromMe
    SetVar VAR_0x8004, POKETCH_APPID_ANALOGWATCH
    Common_GivePoketchApp
    WaitButton
    CloseMessage
    ReleaseAll
    End

CelesticTownSoutheastHouse_CheckGifts:
    GoToIfUnset FLAG_RECEIVED_CELESTIC_TOWN_SOUTHWEST_HOUSE_TYROGUE, CelesticTownSoutheastHouse_OfferTyrogue
    GoToIfUnset FLAG_RECEIVED_CELESTIC_TOWN_SOUTHWEST_HOUSE_HAPPINY, CelesticTownSoutheastHouse_OfferHappiny
    GoTo CelesticTownSoutheastHouse_AnalogOrDigital
    End

CelesticTownSoutheastHouse_OfferTyrogue:
    Message CelesticTownSoutheastHouse_Text_OfferTyrogue
    ShowYesNoMenu VAR_RESULT
    GoToIfEq VAR_RESULT, MENU_NO, CelesticTownSoutheastHouse_GiftDeclined
    GetPartyCount VAR_RESULT
    GoToIfEq VAR_RESULT, MAX_PARTY_SIZE, CelesticTownSoutheastHouse_GiftPartyFull
    BufferPlayerName 0
    PlayFanfare SEQ_FANFA4
    Message CelesticTownSoutheastHouse_Text_PlayerReceivedTyrogue
    WaitFanfare
    GivePokemon SPECIES_TYROGUE, 15, ITEM_NONE, VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, CelesticTownSoutheastHouse_GiftPartyFull
    SetFlag FLAG_RECEIVED_CELESTIC_TOWN_SOUTHWEST_HOUSE_TYROGUE
    GoTo CelesticTownSoutheastHouse_GiftEnd
    End

CelesticTownSoutheastHouse_OfferHappiny:
    Message CelesticTownSoutheastHouse_Text_OfferHappiny
    ShowYesNoMenu VAR_RESULT
    GoToIfEq VAR_RESULT, MENU_NO, CelesticTownSoutheastHouse_GiftDeclined
    GetPartyCount VAR_RESULT
    GoToIfEq VAR_RESULT, MAX_PARTY_SIZE, CelesticTownSoutheastHouse_GiftPartyFull
    BufferPlayerName 0
    PlayFanfare SEQ_FANFA4
    Message CelesticTownSoutheastHouse_Text_PlayerReceivedHappiny
    WaitFanfare
    GivePokemon SPECIES_HAPPINY, 10, ITEM_NONE, VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, CelesticTownSoutheastHouse_GiftPartyFull
    SetFlag FLAG_RECEIVED_CELESTIC_TOWN_SOUTHWEST_HOUSE_HAPPINY
    GoTo CelesticTownSoutheastHouse_GiftEnd
    End

CelesticTownSoutheastHouse_GiftDeclined:
    Message CelesticTownSoutheastHouse_Text_GiftDeclined
    GoTo CelesticTownSoutheastHouse_GiftEnd
    End

CelesticTownSoutheastHouse_GiftPartyFull:
    Message CelesticTownSoutheastHouse_Text_GiftPartyFull
    GoTo CelesticTownSoutheastHouse_GiftEnd
    End

CelesticTownSoutheastHouse_GiftEnd:
    WaitButton
    CloseMessage
    ReleaseAll
    End

CelesticTownSoutheastHouse_AnalogOrDigital:
    Message CelesticTownSoutheastHouse_Text_AnalogOrDigital
    WaitButton
    CloseMessage
    ReleaseAll
    End

CelesticTownPokecenter1F_Happiny:
    PokemonCryAndMessage SPECIES_HAPPINY, CelesticTownSoutheastHouse_Text_HappinyCry
    End
