#include "overlay005/field_effect_renderer.h"

#include <nitro.h>
#include <string.h>

#include "constants/field/field_effect_renderer.h"

#include "field/field_system.h"
#include "overlay005/berry_patch_effects.h"
#include "overlay005/dist_world_surf_mount_renderer.h"
#include "overlay005/ov5_021F10E8.h"
#include "overlay005/ov5_021F134C.h"
#include "overlay005/ov5_021F17B8.h"
#include "overlay005/ov5_021F1CC8.h"
#include "overlay005/ov5_021F23D0.h"
#include "overlay005/ov5_021F2850.h"
#include "overlay005/ov5_021F2A7C.h"
#include "overlay005/ov5_021F2BD0.h"
#include "overlay005/ov5_021F2D20.h"
#include "overlay005/ov5_021F3284.h"
#include "overlay005/ov5_021F348C.h"
#include "overlay005/ov5_021F37A8.h"
#include "overlay005/ov5_021F3A50.h"
#include "overlay005/ov5_021F3D00.h"
#include "overlay005/ov5_021F3E74.h"
#include "overlay005/ov5_021F4018.h"
#include "overlay005/ov5_021F47B0.h"
#include "overlay005/ov5_021F4DAC.h"
#include "overlay005/ov5_021F4E08.h"
#include "overlay005/ov5_021F5060.h"
#include "overlay005/ov5_021F50BC.h"
#include "overlay005/ov5_021F5284.h"
#include "overlay005/ov5_021F5428.h"
#include "overlay005/ov5_021F55CC.h"
#include "overlay005/ov5_021F575C.h"
#include "overlay005/ov5_021F5894.h"
#include "overlay005/ov5_021F5A10.h"
#include "overlay005/ov5_021F600C.h"
#include "overlay005/ov5_021F61BC.h"
#include "overlay005/surf_mount_renderer.h"
#include "overlay005/veilstone_gym_object_renderer.h"

#include "field_system.h"
#include "player_avatar.h"
#include "sys_task.h"

typedef struct ForestAmbienceRenderer {
    FieldEffectManager *fieldEffMan;
    FieldSystem *fieldSystem;
    SysTask *task;
    u16 frameCounter;
    u8 offsetIndex;
} ForestAmbienceRenderer;

static void ForestAmbienceRenderer_Task(SysTask *task, void *data);

static void *ForestAmbienceRenderer_New(FieldEffectManager *fieldEffMan)
{
    ForestAmbienceRenderer *renderer = FieldEffectManager_HeapAllocInit(fieldEffMan, sizeof(ForestAmbienceRenderer), FALSE, 0);

    renderer->fieldEffMan = fieldEffMan;
    renderer->fieldSystem = FieldEffectManager_GetFieldSystem(fieldEffMan);
    renderer->task = SysTask_Start(ForestAmbienceRenderer_Task, renderer, 255);

#ifdef GDB_DEBUGGING
    if (gG4RuntimeQAControl.status == G4_RUNTIME_QA_WARPING) {
        gG4RuntimeQAControl.eventFlags |= G4_RUNTIME_QA_EVENT_FOREST_RENDERER;
    }
#endif

    GF_ASSERT(renderer->task != NULL);
    return renderer;
}

static void ForestAmbienceRenderer_Free(void *data)
{
    ForestAmbienceRenderer *renderer = data;

    if (renderer->task != NULL) {
        SysTask_Done(renderer->task);
    }

    FieldEffectManager_HeapFree(renderer);
}

static void ForestAmbienceRenderer_Task(SysTask *task, void *data)
{
    static const s8 sAmbientOffsets[][3] = {
        { -10, 8, -6 },
        { 12, 12, 5 },
        { -5, 16, 11 },
        { 8, 10, -12 },
        { -14, 14, 3 },
        { 4, 18, 14 },
    };
    ForestAmbienceRenderer *renderer = data;
    VecFx32 position;
    const VecFx32 *playerPos;

    renderer->frameCounter++;
    if (renderer->frameCounter < 90) {
        return;
    }

    renderer->frameCounter = 0;

#ifdef GDB_DEBUGGING
    if (gG4RuntimeQAControl.status == G4_RUNTIME_QA_LOADED
        || gG4RuntimeQAControl.status == G4_RUNTIME_QA_WARPING) {
        gG4RuntimeQAControl.eventFlags |= G4_RUNTIME_QA_EVENT_FOREST_TASK;
    }
#endif

    playerPos = PlayerAvatar_GetPos(FieldSystem_GetPlayerAvatar(renderer->fieldSystem));
    position = *playerPos;

    position.x += sAmbientOffsets[renderer->offsetIndex][0] * FX32_ONE;
    position.y += sAmbientOffsets[renderer->offsetIndex][1] * FX32_ONE;
    position.z += sAmbientOffsets[renderer->offsetIndex][2] * FX32_ONE;

    BerryPatchGraphics_NewSparkleEffectAt(renderer->fieldEffMan, &position, 255);

    renderer->offsetIndex++;
    if (renderer->offsetIndex >= NELEMS(sAmbientOffsets)) {
        renderer->offsetIndex = 0;
    }
}

const FieldEffectRendererFuncs sFieldEffectRendererHandlers[FIELD_EFFECT_RENDERER_COUNT + 1] = {
    { FIELD_EFFECT_RENDERER_00, ov5_021F134C, ov5_021F1370 },
    { FIELD_EFFECT_RENDERER_01, ov5_021F17B8, ov5_021F17D4 },
    { FIELD_EFFECT_RENDERER_02, ov5_021F4DAC, ov5_021F4DC8 },
    { FIELD_EFFECT_RENDERER_03, ov5_021F4E08, ov5_021F4E28 },
    { FIELD_EFFECT_RENDERER_04, ov5_021F5060, ov5_021F507C },
    { FIELD_EFFECT_RENDERER_05, ov5_021F50BC, ov5_021F50D8 },
    { FIELD_EFFECT_RENDERER_06, ov5_021F5284, ov5_021F52A0 },
    { FIELD_EFFECT_RENDERER_07, ov5_021F5428, ov5_021F5444 },
    { FIELD_EFFECT_RENDERER_08, ov5_021F55CC, ov5_021F55E8 },
    { FIELD_EFFECT_RENDERER_09, ov5_021F575C, ov5_021F5778 },
    { FIELD_EFFECT_RENDERER_0A, ov5_021F5894, ov5_021F58B0 },
    { FIELD_EFFECT_RENDERER_0B, ov5_021F1CC8, ov5_021F1CE8 },
    { FIELD_EFFECT_RENDERER_BERRY_PATCH, BerryPatchGraphicsManager_New, BerryPatchGraphicsManager_Free },
    { FIELD_EFFECT_RENDERER_0D, ov5_021F23D0, ov5_021F23EC },
    { FIELD_EFFECT_RENDERER_0E, ov5_021F61BC, ov5_021F61D8 },
    { FIELD_EFFECT_RENDERER_SURF_MOUNT, SurfMountRenderer_New, SurfMountRenderer_Free },
    { FIELD_EFFECT_RENDERER_10, ov5_021F2850, ov5_021F2864 },
    { FIELD_EFFECT_RENDERER_11, ov5_021F2A7C, ov5_021F2A98 },
    { FIELD_EFFECT_RENDERER_12, ov5_021F2BD0, ov5_021F2BEC },
    { FIELD_EFFECT_RENDERER_13, ov5_021F2D20, ov5_021F2D3C },
    { FIELD_EFFECT_RENDERER_14, ov5_021F5A10, ov5_021F5A24 },
    { FIELD_EFFECT_RENDERER_15, ov5_021F3284, ov5_021F32A0 },
    { FIELD_EFFECT_RENDERER_16, ov5_021F600C, ov5_021F6028 },
    { FIELD_EFFECT_RENDERER_17, ov5_021F348C, ov5_021F34A8 },
    { FIELD_EFFECT_RENDERER_18, ov5_021F37A8, ov5_021F37C4 },
    { FIELD_EFFECT_RENDERER_19, ov5_021F3A50, ov5_021F3A6C },
    { FIELD_EFFECT_RENDERER_1A, ov5_021F3D00, ov5_021F3D1C },
    { FIELD_EFFECT_RENDERER_1B, ov5_021F3E74, ov5_021F3E90 },
    { FIELD_EFFECT_RENDERER_BERRY_PATCH_EFFECT_COUNTER, BerryPatchGraphicsManager_NewEffectCounter, BerryPatchGraphicsManager_FreeEffectCounter },
    { FIELD_EFFECT_RENDERER_1D, ov5_021F10E8, ov5_021F10FC },
    { FIELD_EFFECT_RENDERER_1E, ov5_021F4018, ov5_021F4034 },
    { FIELD_EFFECT_RENDERER_VEILSTONE_GYM_OBJECTS, VeilstoneGymObjectRenderer_New, VeilstoneGymObjectRenderer_Free },
    { FIELD_EFFECT_RENDERER_20, ov5_021F47B0, ov5_021F47CC },
    { FIELD_EFFECT_RENDERER_DISTORTION_WORLD_SURF_MOUNT, DistWorldSurfMountRenderer_New, DistWorldSurfMountRenderer_Free },
    { FIELD_EFFECT_RENDERER_FOREST_AMBIENCE, ForestAmbienceRenderer_New, ForestAmbienceRenderer_Free },
    { FIELD_EFFECT_RENDERER_INVALID, NULL, NULL }
};

const u32 sDefaultFieldEffectRenderers[FIELD_EFFECT_RENDERER_COUNT + 1] = {
    FIELD_EFFECT_RENDERER_1D,
    FIELD_EFFECT_RENDERER_00,
    FIELD_EFFECT_RENDERER_0B,
    FIELD_EFFECT_RENDERER_BERRY_PATCH,
    FIELD_EFFECT_RENDERER_0E,
    FIELD_EFFECT_RENDERER_SURF_MOUNT,
    FIELD_EFFECT_RENDERER_10,
    FIELD_EFFECT_RENDERER_1A,
    FIELD_EFFECT_RENDERER_0D,
    FIELD_EFFECT_RENDERER_11,
    FIELD_EFFECT_RENDERER_12,
    FIELD_EFFECT_RENDERER_13,
    FIELD_EFFECT_RENDERER_14,
    FIELD_EFFECT_RENDERER_15,
    FIELD_EFFECT_RENDERER_16,
    FIELD_EFFECT_RENDERER_17,
    FIELD_EFFECT_RENDERER_18,
    FIELD_EFFECT_RENDERER_19,
    FIELD_EFFECT_RENDERER_1B,
    FIELD_EFFECT_RENDERER_01,
    FIELD_EFFECT_RENDERER_BERRY_PATCH_EFFECT_COUNTER,
    FIELD_EFFECT_RENDERER_INVALID
};

const u32 sForestFieldEffectRenderers[FIELD_EFFECT_RENDERER_COUNT + 1] = {
    FIELD_EFFECT_RENDERER_1D,
    FIELD_EFFECT_RENDERER_00,
    FIELD_EFFECT_RENDERER_0B,
    FIELD_EFFECT_RENDERER_BERRY_PATCH,
    FIELD_EFFECT_RENDERER_0E,
    FIELD_EFFECT_RENDERER_SURF_MOUNT,
    FIELD_EFFECT_RENDERER_10,
    FIELD_EFFECT_RENDERER_1A,
    FIELD_EFFECT_RENDERER_0D,
    FIELD_EFFECT_RENDERER_11,
    FIELD_EFFECT_RENDERER_12,
    FIELD_EFFECT_RENDERER_13,
    FIELD_EFFECT_RENDERER_14,
    FIELD_EFFECT_RENDERER_15,
    FIELD_EFFECT_RENDERER_16,
    FIELD_EFFECT_RENDERER_17,
    FIELD_EFFECT_RENDERER_18,
    FIELD_EFFECT_RENDERER_19,
    FIELD_EFFECT_RENDERER_1B,
    FIELD_EFFECT_RENDERER_01,
    FIELD_EFFECT_RENDERER_BERRY_PATCH_EFFECT_COUNTER,
    FIELD_EFFECT_RENDERER_FOREST_AMBIENCE,
    FIELD_EFFECT_RENDERER_INVALID
};

const u32 sUndergroundFieldEffectRenderers[FIELD_EFFECT_RENDERER_COUNT + 1] = {
    FIELD_EFFECT_RENDERER_1D,
    FIELD_EFFECT_RENDERER_02,
    FIELD_EFFECT_RENDERER_03,
    FIELD_EFFECT_RENDERER_04,
    FIELD_EFFECT_RENDERER_05,
    FIELD_EFFECT_RENDERER_06,
    FIELD_EFFECT_RENDERER_07,
    FIELD_EFFECT_RENDERER_0E,
    FIELD_EFFECT_RENDERER_08,
    FIELD_EFFECT_RENDERER_09,
    FIELD_EFFECT_RENDERER_0A,
    FIELD_EFFECT_RENDERER_14,
    FIELD_EFFECT_RENDERER_INVALID
};

const u32 sDistWorldFieldEffectRenderers[FIELD_EFFECT_RENDERER_COUNT + 1] = {
    FIELD_EFFECT_RENDERER_1D,
    FIELD_EFFECT_RENDERER_14,
    FIELD_EFFECT_RENDERER_DISTORTION_WORLD_SURF_MOUNT,
    FIELD_EFFECT_RENDERER_17,
    FIELD_EFFECT_RENDERER_0E,
    FIELD_EFFECT_RENDERER_INVALID
};
