#ifndef POKEPLATINUM_BATTLE_TERRAIN_H
#define POKEPLATINUM_BATTLE_TERRAIN_H

#include "struct_decls/battle_system.h"

#include "sprite_system.h"
#include "sys_task_manager.h"

// IO-PAL-CYCLE water pilot: number of ramp entries that are cycled
#define TERRAIN_WATER_CYCLE_COUNT 4

// This is the circular platform that the battler sprites stand on
typedef struct Terrain {
    ManagedSprite *managedSprite;
    BattleSystem *battleSys;
    SysTask *paletteTask;
    u16 cycleBaseColors[TERRAIN_WATER_CYCLE_COUNT];
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
