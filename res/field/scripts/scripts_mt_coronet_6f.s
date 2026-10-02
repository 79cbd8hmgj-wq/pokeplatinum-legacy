#include "macros/scrcmd.inc"
#include "res/text/bank/mt_coronet_2f.h"


    ScriptEntry MtCoronet6F_OnTransition
    ScriptEntry MtCoronet6F_OnLoad
    ScriptEntry MtCoronet6F_Jirachi
    ScriptEntryEnd

MtCoronet6F_OnTransition:
    GoToIfSet FLAG_SPEAR_PILLAR_IS_DISTORTED, MtCoronet6F_SetWarpSpearPillarDistorted
    GoToIfUnset FLAG_SPEAR_PILLAR_IS_DISTORTED, MtCoronet6F_TrySetWarpSpearPillarDialgaPalkia
    End

MtCoronet6F_OnLoad:
    Call MtCoronet6F_RemoveSpearPillarWarps
    GoToIfSet FLAG_SPEAR_PILLAR_IS_DISTORTED, MtCoronet6F_SetWarpSpearPillarDistorted
    GoToIfUnset FLAG_SPEAR_PILLAR_IS_DISTORTED, MtCoronet6F_TrySetWarpSpearPillarDialgaPalkia
    End

MtCoronet6F_SetWarpSpearPillarDistorted:
    SetWarpEventPos 2, 7, 5
    End

MtCoronet6F_TrySetWarpSpearPillarDialgaPalkia:
    GoToIfGe VAR_EXITED_DISTORTION_WORLD_STATE, 2, MtCoronet6F_TrySetWarpSpearPillarDialga
    GoTo MtCoronet6F_SetWarpSpearPillarNormal
    End

MtCoronet6F_SetWarpSpearPillarNormal:
    SetWarpEventPos 1, 7, 5
    End

MtCoronet6F_TrySetWarpSpearPillarDialga:
    GoToIfUnset FLAG_UNLOCKED_DIALGA_PALKIA_SPEAR_PILLAR, MtCoronet6F_SetWarpSpearPillarNormal
    GoToIfSet FLAG_CAUGHT_DIALGA, MtCoronet6F_TrySetWarpSpearPillarPalkia
    GoToIfGe VAR_SPEAR_PILLAR_DIALGA_STATE, 1, MtCoronet6F_TrySetWarpSpearPillarPalkia
    CheckItem ITEM_ADAMANT_ORB, 1, VAR_MAP_LOCAL_0x01
    GoToIfEq VAR_MAP_LOCAL_0x01, TRUE, MtCoronet6F_SetWarpSpearPillarDialga
    CheckPartyHasHeldItem ITEM_ADAMANT_ORB, VAR_MAP_LOCAL_0x01
    GoToIfEq VAR_MAP_LOCAL_0x01, TRUE, MtCoronet6F_SetWarpSpearPillarDialga
    GoTo MtCoronet6F_TrySetWarpSpearPillarPalkia
    End

MtCoronet6F_TrySetWarpSpearPillarPalkia:
    GoToIfSet FLAG_CAUGHT_PALKIA, MtCoronet6F_SetWarpSpearPillarNormal
    GoToIfGe VAR_SPEAR_PILLAR_PALKIA_STATE, 1, MtCoronet6F_SetWarpSpearPillarNormal
    CheckItem ITEM_LUSTROUS_ORB, 1, VAR_MAP_LOCAL_0x01
    GoToIfEq VAR_MAP_LOCAL_0x01, TRUE, MtCoronet6F_SetWarpSpearPillarPalkia
    CheckPartyHasHeldItem ITEM_LUSTROUS_ORB, VAR_MAP_LOCAL_0x01
    GoToIfEq VAR_MAP_LOCAL_0x01, TRUE, MtCoronet6F_SetWarpSpearPillarPalkia
    GoTo MtCoronet6F_SetWarpSpearPillarNormal
    End

MtCoronet6F_SetWarpSpearPillarDialga:
    SetWarpEventPos 3, 7, 5
    End

MtCoronet6F_SetWarpSpearPillarPalkia:
    SetWarpEventPos 4, 7, 5
    End

MtCoronet6F_RemoveSpearPillarWarps:
    SetWarpEventPos 1, 1, 5
    SetWarpEventPos 2, 1, 5
    SetWarpEventPos 3, 1, 5
    SetWarpEventPos 4, 1, 5
    Return

    .balign 4, 0

MtCoronet6F_Jirachi:
    GoToIfUnset FLAG_GAME_COMPLETED, MtCoronet6F_JirachiEnd
    GoToIfSet FLAG_CAUGHT_JIRACHI, MtCoronet6F_JirachiEnd
    PlaySE SEQ_SE_CONFIRM
    LockAll
    PlayCry SPECIES_JIRACHI
    Message MtCoronet6F_Text_JirachiAppears
    CloseMessage
    StartLegendaryBattle SPECIES_JIRACHI, 50
    CheckWonBattle VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, MtCoronet6F_JirachiBlackOut
    CheckDidNotCapture VAR_RESULT
    GoToIfEq VAR_RESULT, TRUE, MtCoronet6F_JirachiGotAway
    SetFlag FLAG_CAUGHT_JIRACHI
    ReleaseAll
    End

MtCoronet6F_JirachiGotAway:
    Message MtCoronet6F_Text_JirachiGotAway
    WaitButton
    CloseMessage
    ReleaseAll
    End

MtCoronet6F_JirachiBlackOut:
    BlackOutFromBattle
    ReleaseAll
    End

MtCoronet6F_JirachiEnd:
    End
