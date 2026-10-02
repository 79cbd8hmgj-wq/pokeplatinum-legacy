#include "macros/scrcmd.inc"
#include "res/text/bank/route_204_north.h"


    ScriptEntry Route204North_Youngster
    ScriptEntry Route204North_AceTrainerF
    ScriptEntry Route204North_ArrowSignpostFloaromaTown
    ScriptEntryEnd

Route204North_Youngster:
    NPCMessage Route204North_Text_RaisingDifferentPokemon
    End

Route204North_AceTrainerF:
    NPCMessage Route204North_Text_CaptivateOppositeGender
    End

Route204North_ArrowSignpostFloaromaTown:
    ShowArrowSign Route204North_Text_SignFloaromaTown
    End

    .balign 4, 0
