#ifndef POKEPLATINUM_BATTLE_TERRAIN_H
#define POKEPLATINUM_BATTLE_TERRAIN_H

#include "struct_decls/battle_system.h"

#include "sprite_system.h"
#include "sys_task_manager.h"

// IO-PAL-CYCLE: maximum number of palette entries any terrain animates
#define TERRAIN_CYCLE_MAX_COLORS 4

typedef struct TerrainCycleConfig TerrainCycleConfig;

// This is the circular platform that the battler sprites stand on
typedef struct Terrain {
    ManagedSprite *managedSprite;
    BattleSystem *battleSys;
    SysTask *paletteTask;
    const TerrainCycleConfig *cycleConfig;
    u16 cycleBaseColors[TERRAIN_CYCLE_MAX_COLORS];
    u8 side;
    u8 terrainType;
    u8 objPaletteIdx;
    u8 cycleTimer;
    u8 cycleStep;
} Terrain;

void Terrain_LoadResources(Terrain *terrain);
void Terrain_CreateSprite(Terrain *terrain);
void Terrain_DeleteSprite(Terrain *terrain);
void Terrain_UnloadResources(Terrain *terrain);
void Terrain_StopPaletteCycle(Terrain *terrain);
void Terrain_SetVisibility(Terrain *terrain, BOOL draw);
void Terrain_Init(Terrain *terrain, BattleSystem *battleSys, u16 side, int terrainType);
void Terrain_Destroy(Terrain *terrain);

#endif // POKEPLATINUM_BATTLE_TERRAIN_H
