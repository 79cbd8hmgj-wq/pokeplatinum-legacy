#include "battle/terrain.h"

#include "generated/battle_terrains.h"

#include "struct_decls/battle_system.h"

#include "battle/battle_system.h"

#include "narc.h"
#include "palette.h"
#include "sprite_system.h"
#include "sys_task.h"

#include "res/graphics/battle/sprites.naix"

static const SpriteTemplate sTerrainSpriteTemplates[] = {
    {
        .x = 336,
        .y = 136,
        .z = 0,
        .animIdx = 0,
        .priority = 1000,
        .plttIdx = 0,
        .vramType = NNS_G2D_VRAM_TYPE_2DMAIN,
        .resources = {
            0x4E2D,
            0x4E29,
            0x4E25,
            0x4E25,
            0xFFFFFFFF,
            0xFFFFFFFF,
        },
        .bgPriority = 3,
        .vramTransfer = FALSE,
    },
    {
        .x = -80,
        .y = 88,
        .z = 0,
        .animIdx = 0,
        .priority = 1000,
        .plttIdx = 0,
        .vramType = NNS_G2D_VRAM_TYPE_2DMAIN,
        .resources = {
            0x4E2E,
            0x4E29,
            0x4E26,
            0x4E26,
            0xFFFFFFFF,
            0xFFFFFFFF,
        },
        .bgPriority = 3,
        .vramTransfer = FALSE,
    },
};

// clang-format off
ALIGN_4 static const u16 sTerrainSpriteSource_PlayerSide[TERRAIN_MAX] = {
    [TERRAIN_PLAIN]            = terrain_path_player_NCGR_lz,
    [TERRAIN_SAND]             = terrain_sand_player_NCGR_lz,
    [TERRAIN_GRASS]            = terrain_grass_player_NCGR_lz,
    [TERRAIN_PUDDLE]           = terrain_path_puddles_player_NCGR_lz,
    [TERRAIN_MOUNTAIN]         = terrain_rocky_player_NCGR_lz,
    [TERRAIN_CAVE]             = terrain_cave_player_NCGR_lz,
    [TERRAIN_SNOW]             = terrain_snow_player_NCGR_lz,
    [TERRAIN_WATER]            = terrain_water_player_NCGR_lz,
    [TERRAIN_ICE]              = terrain_ice_player_NCGR_lz,
    [TERRAIN_BUILDING]         = terrain_indoors_player_NCGR_lz,
    [TERRAIN_GREAT_MARSH]      = terrain_mud_player_NCGR_lz,
    [TERRAIN_BRIDGE]           = terrain_path_puddles_player_NCGR_lz,
    [TERRAIN_AARON]            = terrain_league_aaron_player_NCGR_lz,
    [TERRAIN_BERTHA]           = terrain_league_bertha_player_NCGR_lz,
    [TERRAIN_FLINT]            = terrain_league_flint_player_NCGR_lz,
    [TERRAIN_LUCIAN]           = terrain_league_lucian_player_NCGR_lz,
    [TERRAIN_CYNTHIA]          = terrain_league_cynthia_player_NCGR_lz,
    [TERRAIN_DISTORTION_WORLD] = terrain_distortion_world_player_NCGR_lz,
    [TERRAIN_BATTLE_TOWER]     = terrain_battle_tower_player_NCGR_lz,
    [TERRAIN_BATTLE_FACTORY]   = terrain_battle_factory_player_NCGR_lz,
    [TERRAIN_BATTLE_ARCADE]    = terrain_battle_arcade_player_NCGR_lz,
    [TERRAIN_BATTLE_CASTLE]    = terrain_battle_castle_player_NCGR_lz,
    [TERRAIN_BATTLE_HALL]      = terrain_battle_hall_player_NCGR_lz,
    [TERRAIN_GIRATINA]         = terrain_giratina_player_NCGR_lz,
};

ALIGN_4 static const u16 sTerrainSpriteSource_EnemySide[TERRAIN_MAX] = {
    [TERRAIN_PLAIN]            = terrain_path_enemy_NCGR_lz,
    [TERRAIN_SAND]             = terrain_sand_enemy_NCGR_lz,
    [TERRAIN_GRASS]            = terrain_grass_enemy_NCGR_lz,
    [TERRAIN_PUDDLE]           = terrain_path_puddles_enemy_NCGR_lz,
    [TERRAIN_MOUNTAIN]         = terrain_rocky_enemy_NCGR_lz,
    [TERRAIN_CAVE]             = terrain_cave_enemy_NCGR_lz,
    [TERRAIN_SNOW]             = terrain_snow_enemy_NCGR_lz,
    [TERRAIN_WATER]            = terrain_water_enemy_NCGR_lz,
    [TERRAIN_ICE]              = terrain_ice_enemy_NCGR_lz,
    [TERRAIN_BUILDING]         = terrain_indoors_enemy_NCGR_lz,
    [TERRAIN_GREAT_MARSH]      = terrain_mud_enemy_NCGR_lz,
    [TERRAIN_BRIDGE]           = terrain_mud_enemy_NCGR_lz,
    [TERRAIN_AARON]            = terrain_league_aaron_enemy_NCGR_lz,
    [TERRAIN_BERTHA]           = terrain_league_bertha_enemy_NCGR_lz,
    [TERRAIN_FLINT]            = terrain_league_flint_enemy_NCGR_lz,
    [TERRAIN_LUCIAN]           = terrain_league_lucian_enemy_NCGR_lz,
    [TERRAIN_CYNTHIA]          = terrain_league_cynthia_enemy_NCGR_lz,
    [TERRAIN_DISTORTION_WORLD] = terrain_distortion_world_enemy_NCGR_lz,
    [TERRAIN_BATTLE_TOWER]     = terrain_battle_tower_enemy_NCGR_lz,
    [TERRAIN_BATTLE_FACTORY]   = terrain_battle_factory_enemy_NCGR_lz,
    [TERRAIN_BATTLE_ARCADE]    = terrain_battle_arcade_enemy_NCGR_lz,
    [TERRAIN_BATTLE_CASTLE]    = terrain_battle_castle_enemy_NCGR_lz,
    [TERRAIN_BATTLE_HALL]      = terrain_battle_hall_enemy_NCGR_lz,
    [TERRAIN_GIRATINA]         = terrain_giratina_enemy_NCGR_lz,
};

ALIGN_4 static const u16 sTerrainPaletteSource[TERRAIN_MAX][3] = {
    [TERRAIN_PLAIN]            = { terrain_path_day_NCLR,             terrain_path_evening_NCLR,           terrain_path_night_NCLR             },
    [TERRAIN_SAND]             = { terrain_sand_day_NCLR,             terrain_sand_evening_NCLR,           terrain_sand_night_NCLR             },
    [TERRAIN_GRASS]            = { terrain_grass_day_NCLR,            terrain_grass_evening_NCLR,          terrain_grass_night_NCLR            },
    [TERRAIN_PUDDLE]           = { terrain_path_puddles_day_NCLR,     terrain_path_puddles_evening_NCLR,   terrain_path_puddles_night_NCLR     },
    [TERRAIN_MOUNTAIN]         = { terrain_rocky_day_NCLR,            terrain_rocky_evening_NCLR,          terrain_rocky_night_NCLR            },
    [TERRAIN_CAVE]             = { terrain_cave_all_NCLR,             terrain_cave_all_NCLR_1,             terrain_cave_all_NCLR_2             },
    [TERRAIN_SNOW]             = { terrain_snow_day_NCLR,             terrain_snow_evening_NCLR,           terrain_snow_night_NCLR             },
    [TERRAIN_WATER]            = { terrain_water_day_NCLR,            terrain_water_evening_NCLR,          terrain_water_night_NCLR            },
    [TERRAIN_ICE]              = { terrain_ice_day_NCLR,              terrain_ice_evening_NCLR,            terrain_ice_night_NCLR              },
    [TERRAIN_BUILDING]         = { terrain_indoors_all_NCLR,          terrain_indoors_all_NCLR_1,          terrain_indoors_all_NCLR_2          },
    [TERRAIN_GREAT_MARSH]      = { terrain_mud_day_NCLR,              terrain_mud_evening_NCLR,            terrain_mud_night_NCLR              },
    [TERRAIN_BRIDGE]           = { terrain_mud_day_NCLR,              terrain_mud_evening_NCLR,            terrain_mud_night_NCLR              },
    [TERRAIN_AARON]            = { terrain_league_aaron_all_NCLR,     terrain_league_aaron_all_NCLR_1,     terrain_league_aaron_all_NCLR_2     },
    [TERRAIN_BERTHA]           = { terrain_league_bertha_all_NCLR,    terrain_league_bertha_all_NCLR_1,    terrain_league_bertha_all_NCLR_2    },
    [TERRAIN_FLINT]            = { terrain_league_flint_all_NCLR,     terrain_league_flint_all_NCLR_1,     terrain_league_flint_all_NCLR_2     },
    [TERRAIN_LUCIAN]           = { terrain_league_lucian_all_NCLR,    terrain_league_lucian_all_NCLR_1,    terrain_league_lucian_all_NCLR_2    },
    [TERRAIN_CYNTHIA]          = { terrain_league_cynthia_all_NCLR,   terrain_league_cynthia_all_NCLR_1,   terrain_league_cynthia_all_NCLR_2   },
    [TERRAIN_DISTORTION_WORLD] = { terrain_distortion_world_all_NCLR, terrain_distortion_world_all_NCLR_1, terrain_distortion_world_all_NCLR_2 },
    [TERRAIN_BATTLE_TOWER]     = { terrain_battle_tower_all_NCLR,     terrain_battle_tower_all_NCLR_1,     terrain_battle_tower_all_NCLR_2     },
    [TERRAIN_BATTLE_FACTORY]   = { terrain_battle_factory_all_NCLR,   terrain_battle_factory_all_NCLR_1,   terrain_battle_factory_all_NCLR_2   },
    [TERRAIN_BATTLE_ARCADE]    = { terrain_battle_arcade_all_NCLR,    terrain_battle_arcade_all_NCLR_1,    terrain_battle_arcade_all_NCLR_2    },
    [TERRAIN_BATTLE_CASTLE]    = { terrain_battle_castle_all_NCLR,    terrain_battle_castle_all_NCLR_1,    terrain_battle_castle_all_NCLR_2    },
    [TERRAIN_BATTLE_HALL]      = { terrain_battle_hall_all_NCLR,      terrain_battle_hall_all_NCLR_1,      terrain_battle_hall_all_NCLR_2      },
    [TERRAIN_GIRATINA]         = { terrain_giratina_all_NCLR,         terrain_giratina_all_NCLR_1,         terrain_giratina_all_NCLR_2         },
};
// clang-format on

// IO-PAL-CYCLE (water pilot): subtle shimmer on the water terrain platform.
//
// Only palette entries 4-7 (the lighter mid-tone highlight bands of the water ramp) are
// animated. Entries 0-3 (transparent / outline / brightest sparkle) and 8-15 (body and
// shadow tones) are never touched, so the platform keeps its time-of-day identity. Each
// step moves every animated entry at most one ramp rung (see sWaterCycleShifts), which
// avoids a visible wrap-around jump.
#define TERRAIN_OBJ_PALETTE_NONE      0xFF
#define TERRAIN_BG_PALETTE_SLOT       7
#define TERRAIN_WATER_CYCLE_FIRST_IDX 4
#define TERRAIN_WATER_CYCLE_INTERVAL  16 // frames between steps; a full loop is 4 steps (~1.07s)
#define TERRAIN_WATER_CYCLE_PHASES    4

static const s8 sWaterCycleShifts[TERRAIN_WATER_CYCLE_PHASES] = { 0, 1, 0, -1 };

static void Terrain_BuildCycleColors(const Terrain *terrain, u32 step, u16 *out)
{
    for (int i = 0; i < TERRAIN_WATER_CYCLE_COUNT; i++) {
        int src = i + sWaterCycleShifts[step];

        if (src < 0) {
            src = 0;
        } else if (src > TERRAIN_WATER_CYCLE_COUNT - 1) {
            src = TERRAIN_WATER_CYCLE_COUNT - 1;
        }

        out[i] = terrain->cycleBaseColors[src];
    }
}

static BOOL Terrain_RangeEquals(const u16 *a, const u16 *b)
{
    for (int i = 0; i < TERRAIN_WATER_CYCLE_COUNT; i++) {
        if (a[i] != b[i]) {
            return FALSE;
        }
    }

    return TRUE;
}

// Updates the animated range of one palette in the given PaletteData buffer. The unfaded
// buffer is the authoritative copy; the faded buffer and hardware palette are only touched
// when no fade owns them. Returns FALSE (leaving everything untouched) when the range does
// not currently hold water terrain colors or has been tinted by another effect.
static BOOL Terrain_WriteCycleColors(Terrain *terrain, PaletteData *paletteData, enum PaletteBufferID bufferID, u16 paletteIdx, const u16 *curColors, const u16 *newColors)
{
    u32 start = PLTT_DEST(paletteIdx) + TERRAIN_WATER_CYCLE_FIRST_IDX;
    u16 *unfaded = PaletteData_GetUnfadedBuffer(paletteData, bufferID) + start;
    u16 *faded = PaletteData_GetFadedBuffer(paletteData, bufferID) + start;

    if (Terrain_RangeEquals(unfaded, curColors) == FALSE && Terrain_RangeEquals(unfaded, terrain->cycleBaseColors) == FALSE) {
        return FALSE;
    }

    if (Terrain_RangeEquals(faded, unfaded) == FALSE) {
        return FALSE;
    }

    u32 size = TERRAIN_WATER_CYCLE_COUNT * sizeof(u16);
    u32 hwOffset = PLTT_OFFSET(paletteIdx) + TERRAIN_WATER_CYCLE_FIRST_IDX * sizeof(u16);

    MI_CpuCopy16(newColors, unfaded, size);
    MI_CpuCopy16(newColors, faded, size);
    DC_FlushRange(faded, size);

    if (bufferID == PLTTBUF_MAIN_OBJ) {
        GX_LoadOBJPltt(faded, hwOffset, size);
    } else {
        GX_LoadBGPltt(faded, hwOffset, size);
    }

    return TRUE;
}

static void SysTask_CycleWaterPalette(SysTask *task, void *param)
{
    Terrain *terrain = param;
    BattleSystem *battleSys = terrain->battleSys;

    // Sub-menus (bag/party/move forget) and post-battle screens own the palettes.
    if (BattleSystem_GetRenderMode(battleSys) != 0) {
        terrain->cycleTimer = 0;
        return;
    }

    terrain->cycleTimer++;

    if (terrain->cycleTimer < TERRAIN_WATER_CYCLE_INTERVAL) {
        return;
    }

    terrain->cycleTimer = 0;

    PaletteData *paletteData = BattleSystem_GetPaletteData(battleSys);

    // While a fade is running on the buffer, leave it entirely to the fade.
    if (PaletteData_GetSelectedBuffersMask(paletteData) & (PLTTBUF_MAIN_OBJ_F | PLTTBUF_MAIN_BG_F)) {
        return;
    }

    u16 curColors[TERRAIN_WATER_CYCLE_COUNT];
    u16 newColors[TERRAIN_WATER_CYCLE_COUNT];
    u32 nextStep = (terrain->cycleStep + 1) % TERRAIN_WATER_CYCLE_PHASES;

    Terrain_BuildCycleColors(terrain, terrain->cycleStep, curColors);
    Terrain_BuildCycleColors(terrain, nextStep, newColors);

    if (Terrain_WriteCycleColors(terrain, paletteData, PLTTBUF_MAIN_OBJ, terrain->objPaletteIdx, curColors, newColors) == FALSE) {
        return;
    }

    // Keep the BG slot 7 mirror (consumed by BattleSystem_BakeSpritesToBackground) in step
    // so a baked terrain matches what was on screen.
    Terrain_WriteCycleColors(terrain, paletteData, PLTTBUF_MAIN_BG, TERRAIN_BG_PALETTE_SLOT, curColors, newColors);
    terrain->cycleStep = nextStep;
}

static void Terrain_StartPaletteCycle(Terrain *terrain, PaletteData *paletteData, u8 objPaletteIdx)
{
    // Both terrain sides request resource 20009; only the first load allocates a palette
    // (the second returns TERRAIN_OBJ_PALETTE_NONE), so the cycle is owned by that side.
    if (terrain->terrainType != TERRAIN_WATER || objPaletteIdx == TERRAIN_OBJ_PALETTE_NONE) {
        return;
    }

    u16 *unfaded = PaletteData_GetUnfadedBuffer(paletteData, PLTTBUF_MAIN_OBJ) + PLTT_DEST(objPaletteIdx) + TERRAIN_WATER_CYCLE_FIRST_IDX;

    MI_CpuCopy16(unfaded, terrain->cycleBaseColors, sizeof(terrain->cycleBaseColors));
    terrain->objPaletteIdx = objPaletteIdx;
    terrain->cycleTimer = 0;
    terrain->cycleStep = 0;
    terrain->paletteTask = SysTask_Start(SysTask_CycleWaterPalette, terrain, 60001);
}

void Terrain_StopPaletteCycle(Terrain *terrain)
{
    if (terrain->paletteTask == NULL) {
        return;
    }

    SysTask_Done(terrain->paletteTask);
    terrain->paletteTask = NULL;

    // Restore the pristine palette if it still holds a cycled state and nothing owns it.
    PaletteData *paletteData = BattleSystem_GetPaletteData(terrain->battleSys);

    if (terrain->cycleStep != 0 && (PaletteData_GetSelectedBuffersMask(paletteData) & (PLTTBUF_MAIN_OBJ_F | PLTTBUF_MAIN_BG_F)) == 0) {
        u16 curColors[TERRAIN_WATER_CYCLE_COUNT];

        Terrain_BuildCycleColors(terrain, terrain->cycleStep, curColors);
        Terrain_WriteCycleColors(terrain, paletteData, PLTTBUF_MAIN_OBJ, terrain->objPaletteIdx, curColors, terrain->cycleBaseColors);
        Terrain_WriteCycleColors(terrain, paletteData, PLTTBUF_MAIN_BG, TERRAIN_BG_PALETTE_SLOT, curColors, terrain->cycleBaseColors);
    }

    terrain->cycleStep = 0;
}

void Terrain_LoadResources(Terrain *terrain)
{
    SpriteSystem *spriteSys;
    SpriteManager *spriteMan;
    int charNarcIdx, charResID, cellNarcIdx, cellResID, animNarcIdx, animResID;
    int bgTimeOffset;
    u8 objPaletteIdx;
    NARC *objNarc = NARC_ctor(NARC_INDEX_BATTLE__GRAPHIC__PL_BATT_OBJ, HEAP_ID_BATTLE);
    spriteSys = BattleSystem_GetSpriteSystem(terrain->battleSys);
    spriteMan = BattleSystem_GetSpriteManager(terrain->battleSys);
    bgTimeOffset = BattleSystem_GetBackgroundTimeOffset(terrain->battleSys);

    if (terrain->side == 0) {
        charNarcIdx = sTerrainSpriteSource_PlayerSide[terrain->terrainType];
        charResID = 20013;
        cellNarcIdx = terrain_player_cell_NCER_lz;
        cellResID = 20005;
        animNarcIdx = terrain_player_anim_NANR_lz;
        animResID = 20005;
    } else {
        charNarcIdx = sTerrainSpriteSource_EnemySide[terrain->terrainType];
        charResID = 20014;
        cellNarcIdx = terrain_enemy_cell_NCER_lz;
        cellResID = 20006;
        animNarcIdx = terrain_enemy_anim_NANR_lz;
        animResID = 20006;
    }

    SpriteSystem_LoadCharResObjFromOpenNarc(spriteSys, spriteMan, objNarc, charNarcIdx, TRUE, NNS_G2D_VRAM_TYPE_2DMAIN, charResID);
    objPaletteIdx = SpriteSystem_LoadPaletteBufferFromOpenNarc(BattleSystem_GetPaletteData(terrain->battleSys), PLTTBUF_MAIN_OBJ, spriteSys, spriteMan, objNarc, sTerrainPaletteSource[terrain->terrainType][bgTimeOffset], FALSE, 1, NNS_G2D_VRAM_TYPE_2DMAIN, 20009);
    PaletteData_LoadBufferFromFileStart(BattleSystem_GetPaletteData(terrain->battleSys), NARC_INDEX_BATTLE__GRAPHIC__PL_BATT_OBJ, sTerrainPaletteSource[terrain->terrainType][bgTimeOffset], HEAP_ID_BATTLE, PLTTBUF_MAIN_BG, PALETTE_SIZE_BYTES, PLTT_DEST(TERRAIN_BG_PALETTE_SLOT));
    Terrain_StartPaletteCycle(terrain, BattleSystem_GetPaletteData(terrain->battleSys), objPaletteIdx);
    SpriteSystem_LoadCellResObjFromOpenNarc(spriteSys, spriteMan, objNarc, cellNarcIdx, TRUE, cellResID);
    SpriteSystem_LoadAnimResObjFromOpenNarc(spriteSys, spriteMan, objNarc, animNarcIdx, TRUE, animResID);
    NARC_dtor(objNarc);
}

void Terrain_CreateSprite(Terrain *terrain)
{
    SpriteSystem *spriteSys;
    SpriteManager *spriteMan;
    const SpriteTemplate *spriteTemplate;

    spriteSys = BattleSystem_GetSpriteSystem(terrain->battleSys);
    spriteMan = BattleSystem_GetSpriteManager(terrain->battleSys);
    spriteTemplate = &sTerrainSpriteTemplates[terrain->side];

    terrain->managedSprite = SpriteSystem_NewSprite(spriteSys, spriteMan, spriteTemplate);
    Sprite_TickFrame(terrain->managedSprite->sprite);
}

void Terrain_DeleteSprite(Terrain *terrain)
{
    if (terrain->managedSprite == NULL) {
        return;
    }

    Sprite_DeleteAndFreeResources(terrain->managedSprite);
    terrain->managedSprite = NULL;
}

void Terrain_UnloadResources(Terrain *terrain)
{
    SpriteManager *spriteMan;
    int charResourceID, cellResourceID, animResourceID;

    spriteMan = BattleSystem_GetSpriteManager(terrain->battleSys);

    if (terrain->side == 0) {
        charResourceID = 20013;
        cellResourceID = 20005;
        animResourceID = 20005;
    } else {
        charResourceID = 20014;
        cellResourceID = 20006;
        animResourceID = 20006;
    }

    SpriteManager_UnloadCharObjById(spriteMan, charResourceID);
    SpriteManager_UnloadPlttObjById(spriteMan, 20009);
    SpriteManager_UnloadCellObjById(spriteMan, cellResourceID);
    SpriteManager_UnloadAnimObjById(spriteMan, animResourceID);
}

void Terrain_SetVisibility(Terrain *terrain, BOOL draw)
{
    if (terrain->managedSprite == NULL) {
        return;
    }

    ManagedSprite_SetDrawFlag(terrain->managedSprite, draw);
}

void Terrain_Init(Terrain *terrain, BattleSystem *battleSys, u16 side, int terrainType)
{
    MI_CpuClearFast(terrain, sizeof(Terrain));

    terrain->battleSys = battleSys;
    terrain->side = side;
    terrain->terrainType = terrainType;

    if (terrainType >= TERRAIN_MAX) {
        GF_ASSERT(FALSE);
        terrain->terrainType = 0;
    }

    Terrain_LoadResources(terrain);
    Terrain_CreateSprite(terrain);
}

void Terrain_Destroy(Terrain *terrain)
{
    Terrain_StopPaletteCycle(terrain);
    Terrain_DeleteSprite(terrain);
    Terrain_UnloadResources(terrain);
    MI_CpuClearFast(terrain, sizeof(Terrain));
}
