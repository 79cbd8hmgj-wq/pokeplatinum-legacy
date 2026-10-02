#include "macros/scrcmd.inc"
#include "res/text/bank/victory_road_1f.h"


    ScriptEntry VictoryRoad_OnTransition
    ScriptEntry VictoryRoad_Collector
    ScriptEntryEnd

VictoryRoad_OnTransition:
    SetFlag FLAG_FIRST_ARRIVAL_VICTORY_ROAD
    GoToIfUnset FLAG_GAME_COMPLETED, VictoryRoad_DontHideCollector
    GetNationalDexEnabled VAR_MAP_LOCAL_0x00
    GoToIfEq VAR_MAP_LOCAL_0x00, FALSE, VictoryRoad_DontHideCollector
    // Keep the Collector available until the locked TM78 gift has actually been received.
    GoToIfUnset FLAG_RECEIVED_ROUTE_204_NORTH_TM78, VictoryRoad_DontHideCollector
    SetFlag FLAG_HIDE_VICTORY_ROAD_1F_COLLECTOR
VictoryRoad_DontHideCollector:
    End

VictoryRoad_Collector:
    PlaySE SEQ_SE_CONFIRM
    LockAll
    FacePlayer
    // Award TM78 before choosing the pre/postgame dialogue so skipping this NPC
    // before the Elite Four can never make Power Gem permanently missable.
    GoToIfSet FLAG_RECEIVED_ROUTE_204_NORTH_TM78, VictoryRoad1F_TM78AlreadyReceived
    Message VictoryRoad1F_Text_AimForPokemonLeague
    SetVar VAR_0x8004, ITEM_TM78
    SetVar VAR_0x8005, 1
    GoToIfCannotFitItem VAR_0x8004, VAR_0x8005, VAR_RESULT, VictoryRoad1F_TM78BagFull
    Common_GiveItemQuantity
    SetFlag FLAG_RECEIVED_ROUTE_204_NORTH_TM78
    GoTo VictoryRoad1F_CollectorEnd
    End

VictoryRoad1F_TM78AlreadyReceived:
    GoToIfSet FLAG_GAME_COMPLETED, VictoryRoad1F_YoullMeetManyPokemon
    Message VictoryRoad1F_Text_AimForPokemonLeague
    GoTo VictoryRoad1F_CollectorEnd
    End

VictoryRoad1F_TM78BagFull:
    Common_MessageBagIsFull
    CloseMessage
    ReleaseAll
    End

VictoryRoad1F_YoullMeetManyPokemon:
    Message VictoryRoad1F_Text_YoullMeetManyPokemon
    GoTo VictoryRoad1F_CollectorEnd
    End

VictoryRoad1F_CollectorEnd:
    WaitButton
    CloseMessage
    ReleaseAll
    End

    .balign 4, 0
