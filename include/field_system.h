#ifndef POKEPLATINUM_FIELD_SYSTEM_H
#define POKEPLATINUM_FIELD_SYSTEM_H

#include "applications/poketch/poketch_system.h"
#include "field/field_system_decl.h"

#include "bg_window.h"
#include "overlay_manager.h"
#include "savedata.h"

#ifdef GDB_DEBUGGING
enum G4RuntimeQATarget {
    G4_RUNTIME_QA_NONE = 0,
    G4_RUNTIME_QA_ETERNA_FOREST,
    G4_RUNTIME_QA_SNOWPOINT,
    G4_RUNTIME_QA_SPEAR_PILLAR,
    G4_RUNTIME_QA_LAKE_VERITY,
    G4_RUNTIME_QA_TURNBACK_CAVE,
    G4_RUNTIME_QA_GALACTIC_HQ,
    G4_RUNTIME_QA_MT_CORONET,
};

enum G4RuntimeQAStatus {
    G4_RUNTIME_QA_IDLE = 0,
    G4_RUNTIME_QA_WARPING,
    G4_RUNTIME_QA_LOADED,
    G4_RUNTIME_QA_REJECTED,
};

enum G4RuntimeQAEvent {
    G4_RUNTIME_QA_EVENT_AREA_LIGHT = 1 << 0,
    G4_RUNTIME_QA_EVENT_FOREST_RENDERER = 1 << 1,
    G4_RUNTIME_QA_EVENT_FOREST_TASK = 1 << 2,
    G4_RUNTIME_QA_EVENT_SPECIAL_FOG = 1 << 3,
    G4_RUNTIME_QA_EVENT_FOG_APPLY = 1 << 4,
};

typedef struct G4RuntimeQAControl {
    volatile u32 request;
    volatile u32 status;
    volatile u32 loadedMapHeader;
    volatile u32 eventFlags;
    volatile u32 lightArchiveID;
} G4RuntimeQAControl;

extern G4RuntimeQAControl gG4RuntimeQAControl;
#endif

void FieldSystem_StartFieldMapInner(FieldSystem *fieldSystem);
void FieldSystem_FlagNotRunningFieldMap(FieldSystem *fieldSystem);
BOOL FieldSystem_HasParentProcess(FieldSystem *fieldSystem);
BOOL FieldSystem_IsRunningFieldMapInner(FieldSystem *fieldSystem);
BOOL FieldSystem_HasChildProcess(FieldSystem *fieldSystem);
void FieldSystem_StartChildProcess(FieldSystem *fieldSystem, const ApplicationManagerTemplate *appTemplate, void *appArgs);
void FieldSystem_PauseProcessing(void);
void FieldSystem_ResumeProcessing(void);
PoketchSystem *FieldSystem_GetPoketchSystem(void);
BgConfig *FieldSystem_GetBgConfig(void *fieldSystem);
SaveData *FieldSystem_GetSaveData(void *fieldSystem);

#endif // POKEPLATINUM_UNK_0203CC84_H
