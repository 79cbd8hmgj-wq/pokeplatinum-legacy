#include "overlay005/forest_ambient_effects.h"

#include <nitro.h>

#include "field/field_system.h"
#include "overlay005/berry_patch_effects.h"
#include "overlay005/field_effect_manager.h"

#include "overworld_anim_manager.h"
#include "player_avatar.h"

#define FOREST_AMBIENT_SPAWN_INTERVAL 48
#define FOREST_AMBIENT_EFFECT_PRIORITY 0xFF

typedef struct ForestAmbientEmitterContext {
    FieldSystem *fieldSystem;
    FieldEffectManager *fieldEffMan;
} ForestAmbientEmitterContext;

typedef struct ForestAmbientEmitter {
    ForestAmbientEmitterContext context;
    int frameCounter;
    int spawnIndex;
} ForestAmbientEmitter;

static BOOL ForestAmbientEmitter_Init(OverworldAnimManager *manager, void *context);
static void ForestAmbientEmitter_Exit(OverworldAnimManager *manager, void *context);
static void ForestAmbientEmitter_Tick(OverworldAnimManager *manager, void *context);
static void ForestAmbientEmitter_Render(OverworldAnimManager *manager, void *context);

static const VecFx32 sForestAmbientOffsets[] = {
    { FX32_ONE * -40, FX32_ONE * -4, FX32_ONE * 20 },
    { FX32_ONE * 32, FX32_ONE * -8, FX32_ONE * 36 },
    { FX32_ONE * -20, FX32_ONE * -12, FX32_ONE * -28 },
    { FX32_ONE * 48, FX32_ONE * -6, FX32_ONE * -12 },
    { FX32_ONE * -52, FX32_ONE * -10, FX32_ONE * 4 },
    { FX32_ONE * 16, FX32_ONE * -14, FX32_ONE * 52 },
    { FX32_ONE * 40, FX32_ONE * -8, FX32_ONE * -40 },
    { FX32_ONE * -28, FX32_ONE * -6, FX32_ONE * 44 },
};

static const OverworldAnimManagerFuncs sForestAmbientEmitterFuncs = {
    sizeof(ForestAmbientEmitter),
    ForestAmbientEmitter_Init,
    ForestAmbientEmitter_Exit,
    ForestAmbientEmitter_Tick,
    ForestAmbientEmitter_Render
};

void ForestAmbientEffects_Start(FieldSystem *fieldSystem)
{
    ForestAmbientEmitterContext context;
    VecFx32 position = *PlayerAvatar_GetPos(fieldSystem->playerAvatar);

    context.fieldSystem = fieldSystem;
    context.fieldEffMan = fieldSystem->fieldEffMan;

    FieldEffectManager_InitAnimManager(
        fieldSystem->fieldEffMan,
        &sForestAmbientEmitterFuncs,
        &position,
        0,
        &context,
        FOREST_AMBIENT_EFFECT_PRIORITY);
}

static BOOL ForestAmbientEmitter_Init(OverworldAnimManager *manager, void *context)
{
    ForestAmbientEmitter *emitter = context;
    const ForestAmbientEmitterContext *emitterContext = OverworldAnimManager_GetUserData(manager);

    emitter->context = *emitterContext;
    emitter->frameCounter = 0;
    emitter->spawnIndex = 0;

    return TRUE;
}

static void ForestAmbientEmitter_Exit(OverworldAnimManager *manager, void *context)
{
    return;
}

static void ForestAmbientEmitter_Tick(OverworldAnimManager *manager, void *context)
{
    ForestAmbientEmitter *emitter = context;

    emitter->frameCounter++;

    if (emitter->frameCounter < FOREST_AMBIENT_SPAWN_INTERVAL) {
        return;
    }

    emitter->frameCounter = 0;

    VecFx32 position = *PlayerAvatar_GetPos(emitter->context.fieldSystem->playerAvatar);
    const VecFx32 *offset = &sForestAmbientOffsets[emitter->spawnIndex];

    position.x += offset->x;
    position.y += offset->y;
    position.z += offset->z;

    BerryPatchGraphics_NewSparkleEffectAt(
        emitter->context.fieldEffMan,
        &position,
        FOREST_AMBIENT_EFFECT_PRIORITY);

    emitter->spawnIndex++;

    if (emitter->spawnIndex >= NELEMS(sForestAmbientOffsets)) {
        emitter->spawnIndex = 0;
    }
}

static void ForestAmbientEmitter_Render(OverworldAnimManager *manager, void *context)
{
    return;
}
