#include "overlay005/map_name_popup.h"

#include <nitro.h>

#include "constants/field_base_tiles.h"
#include "constants/graphics.h"
#include "constants/heap.h"

#include "field/field_system.h"
#include "field/field_system_sub2_t.h"

#include "bg_window.h"
#include "graphics.h"
#include "heap.h"
#include "map_header.h"
#include "map_header_util.h"
#include "message.h"
#include "rtc.h"
#include "string_gf.h"
#include "sys_task.h"
#include "sys_task_manager.h"
#include "text.h"

#include "res/text/bank/location_names.h"

#define POPUP_WIDTH_TILES  17
#define POPUP_HEIGHT_TILES 5
#define POPUP_SIZE_TILES   (POPUP_WIDTH_TILES * POPUP_HEIGHT_TILES)

// IO-PREVIEW: an optional area card drawn into the otherwise blank right-hand tiles of the
// 32x5-tile popup window. It reuses the window's pixels, tilemap, BG palette slot and
// BG3 layer, so it needs no allocation beyond the temporary NARC buffer and is cleared by
// the same Window_FillTilemap / Window_ClearAndCopyToVRAM calls as the popup itself.
// Layout: tiles 0-16 popup, tile 17 gap, tiles 18-30 card, tile 31 margin.
#define AREA_CARD_TILE_X      18
#define AREA_CARD_WIDTH_TILES 13
#define AREA_CARD_SIZE_TILES  (AREA_CARD_WIDTH_TILES * POPUP_HEIGHT_TILES)

// The map header stores MAP_LABEL_WINDOW_FOREST (5); the popup is handed that value minus one
// (see FieldSystem_RequestLocationName), which is also the popup style's NARC pair index / 2.
#define POPUP_STYLE_FOREST 4

// Extra area_win_gra members, appended after the nine NCGR/NCLR pairs (see map_popup.order).
// Each shares the forest popup palette (BG palette slot 7), so no palette is loaded for them.
enum AreaCardNarcMember {
    AREA_CARD_NARC_ETERNA_FOREST_DAY = 18,
    AREA_CARD_NARC_ETERNA_FOREST_DUSK,
    AREA_CARD_NARC_ETERNA_FOREST_NIGHT,
};

enum MapNamePopUpState {
    MAP_NAME_POPUP_STATE_END,
    MAP_NAME_POPUP_STATE_SLIDE_IN,
    MAP_NAME_POPUP_STATE_SLIDE_OUT,
    MAP_NAME_POPUP_STATE_WAIT
};

static void MapNamePopUp_CreateWindow(MapNamePopUp *mapPopUp);
static void MapNamePopUp_LoadAreaGfx(MapNamePopUp *mapPopUp, u8 bgLayer, u16 tileStart, u8 plttOffset, u8 unused);
static void MapNamePopUp_Reset(MapNamePopUp *mapPopUp);
static void MapNamePopUp_SetBgConfig(MapNamePopUp *mapPopUp, BgConfig *bgConfig);
static void SysTask_MapNamePopUpWindow(SysTask *task, void *data);
static void MapNamePopUp_DrawWindowFrame(MapNamePopUp *mapPopUp, s32 strWidth);
static void MapNamePopUp_StartSlideOut(MapNamePopUp *mapPopUp);
static void MapNamePopUp_PrintMapName(MapNamePopUp *mapPopUp, const String *string);
static void MapNamePopUp_DrawAreaCard(MapNamePopUp *mapPopUp);

static void MapNamePopUp_LoadPalette(void *src, u16 size, u16 offset)
{
    DC_FlushRange(src, PLTT_OFFSET(size));
    GX_LoadBGPltt(src, PLTT_OFFSET(offset), PLTT_OFFSET(size));
}

static void MapNamePopUp_CreateWindow(MapNamePopUp *mapPopUp)
{
    Window_Add(mapPopUp->bgConfig, &mapPopUp->window, BG_LAYER_MAIN_3, 0, 0, 32, 5, 7, BASE_TILE_MESSAGE_WINDOW - (32 * 5));
}

static void MapNamePopUp_LoadAreaGfx(MapNamePopUp *mapPopUp, u8 bgLayer, u16 tileStart, u8 plttOffset, u8 unused)
{

    NNSG2dPaletteData *paletteData;
    u8 narcMemberIdx = mapPopUp->windowID * 2;

    mapPopUp->tiles = Graphics_GetCharData(NARC_INDEX_ARC__AREA_WIN_GRA, narcMemberIdx, FALSE, &mapPopUp->charData, HEAP_ID_FIELD1);
    Bg_LoadTiles(mapPopUp->bgConfig, bgLayer, mapPopUp->charData->pRawData, mapPopUp->charData->szByte, tileStart);
    void *ptr = Graphics_GetPlttData(NARC_INDEX_ARC__AREA_WIN_GRA, narcMemberIdx + 1, &paletteData, HEAP_ID_FIELD1);

    MapNamePopUp_LoadPalette(paletteData->pRawData, 1, plttOffset);
    Heap_Free(ptr);
}

static void MapNamePopUp_DrawWindowFrame(MapNamePopUp *mapPopUp, s32 strWidth)
{
    int marginSize = ((strWidth + 8) / 8 * 8) - strWidth;
    int leftMargin = marginSize / 2;

    u8 spareTile;
    if (8 <= (4 + leftMargin)) {
        spareTile = 0;
    } else {
        spareTile = (((8 - (4 + leftMargin)) * 2) + 8 - 1) / 8;
    }

    int width = strWidth;

    int xOffset;
    if (width <= 0) {
        xOffset = 0;
    } else {
        int strWidthTiles = ((width + 8) / 8) + spareTile;
        xOffset = ((strWidthTiles * 8) + 8 - strWidth) / 2;
    }

    mapPopUp->xOffset = (8 - 4) + xOffset;

    MapNamePopUp_LoadAreaGfx(mapPopUp, BG_LAYER_MAIN_3, BASE_TILE_MAP_TRANSITION_DROPDOWN, 7, 0);
    Window_FillTilemap(&mapPopUp->window, 0);

    for (int i = 0; i < POPUP_SIZE_TILES; i++) {
        Window_BlitBitmapRect(&mapPopUp->window, mapPopUp->charData->pRawData, i * 8, 0, 8, 8, (i % POPUP_WIDTH_TILES) * 8, (i / POPUP_WIDTH_TILES) * 8, 8, 8);
    }

    MapNamePopUp_DrawAreaCard(mapPopUp);

    Window_CopyToVRAM(&mapPopUp->window);
    Heap_Free(mapPopUp->tiles);
}

static BOOL MapNamePopUp_GetAreaCardMember(const MapNamePopUp *mapPopUp, u32 *narcMember)
{
    // Eterna Forest only. Eterna Forest's outside-gate header shares this text ID but uses the
    // route popup style, so the style check keeps the card off that map.
    if (mapPopUp->entryID != LocationNames_Text_EternaForest || mapPopUp->windowID != POPUP_STYLE_FOREST) {
        return FALSE;
    }

    // Same clock the field area lighting uses (ov5_021F134C), so card and scene lighting agree.
    switch (GetTimeOfDay()) {
    case TIMEOFDAY_TWILIGHT:
        *narcMember = AREA_CARD_NARC_ETERNA_FOREST_DUSK;
        break;
    case TIMEOFDAY_NIGHT:
    case TIMEOFDAY_LATE_NIGHT:
        *narcMember = AREA_CARD_NARC_ETERNA_FOREST_NIGHT;
        break;
    default:
        *narcMember = AREA_CARD_NARC_ETERNA_FOREST_DAY;
        break;
    }

    return TRUE;
}

static void MapNamePopUp_DrawAreaCard(MapNamePopUp *mapPopUp)
{
    u32 narcMember;
    NNSG2dCharacterData *charData;

    if (!MapNamePopUp_GetAreaCardMember(mapPopUp, &narcMember)) {
        return;
    }

    void *tiles = Graphics_GetCharData(NARC_INDEX_ARC__AREA_WIN_GRA, narcMember, FALSE, &charData, HEAP_ID_FIELD1);

    // Fail closed: a short or missing resource leaves the vanilla popup untouched.
    if (charData->szByte >= AREA_CARD_SIZE_TILES * TILE_SIZE_4BPP) {
        for (int i = 0; i < AREA_CARD_SIZE_TILES; i++) {
            Window_BlitBitmapRect(&mapPopUp->window, charData->pRawData, i * 8, 0, 8, 8, (AREA_CARD_TILE_X + (i % AREA_CARD_WIDTH_TILES)) * 8, (i / AREA_CARD_WIDTH_TILES) * 8, 8, 8);
        }
    }

    Heap_Free(tiles);
}

static void MapNamePopUp_Reset(MapNamePopUp *mapPopUp)
{
    mapPopUp->isInited = FALSE;
    mapPopUp->state = MAP_NAME_POPUP_STATE_END;
    mapPopUp->task = NULL;
    mapPopUp->yOffset = 0;
    mapPopUp->timer = 0;
    mapPopUp->shouldSlideIn = FALSE;
    mapPopUp->entryID = 0;
    mapPopUp->bgConfig = NULL;
}

static void MapNamePopUp_SetBgConfig(MapNamePopUp *mapPopUp, BgConfig *bgConfig)
{
    MapNamePopUp_Reset(mapPopUp);
    mapPopUp->bgConfig = bgConfig;
}

static void SysTask_MapNamePopUpWindow(SysTask *task, void *data)
{
    u32 strWidth;
    MapNamePopUp *mapPopUp = data;

    switch (mapPopUp->state) {
    case MAP_NAME_POPUP_STATE_SLIDE_IN:
        mapPopUp->yOffset -= 4;

        if (mapPopUp->yOffset < 0) {
            mapPopUp->yOffset = 0;
        }

        Bg_SetOffset(mapPopUp->bgConfig, BG_LAYER_MAIN_3, BG_OFFSET_UPDATE_SET_Y, mapPopUp->yOffset);

        if (mapPopUp->yOffset == 0) {
            mapPopUp->timer = 0;
            mapPopUp->state = MAP_NAME_POPUP_STATE_WAIT;
        }

        break;
    case MAP_NAME_POPUP_STATE_WAIT:
        mapPopUp->timer++;

        if (mapPopUp->timer >= 60) {
            mapPopUp->timer = 0;
            mapPopUp->state = MAP_NAME_POPUP_STATE_SLIDE_OUT;
        }

        break;
    case MAP_NAME_POPUP_STATE_SLIDE_OUT:
        mapPopUp->yOffset += 4;

        if (mapPopUp->yOffset > 38) {
            mapPopUp->yOffset = 38;
        }

        Bg_SetOffset(mapPopUp->bgConfig, BG_LAYER_MAIN_3, BG_OFFSET_UPDATE_SET_Y, mapPopUp->yOffset);

        if (mapPopUp->yOffset == 38) {
            if (mapPopUp->shouldSlideIn) {
                mapPopUp->shouldSlideIn = FALSE;

                strWidth = MapHeader_LoadString(mapPopUp->msgLoader, mapPopUp->entryID, mapPopUp->string);

                MapNamePopUp_DrawWindowFrame(mapPopUp, strWidth);
                MapNamePopUp_PrintMapName(mapPopUp, mapPopUp->string);
                mapPopUp->state = MAP_NAME_POPUP_STATE_SLIDE_IN;
            } else {
                MapNamePopUp_Hide(mapPopUp);
                return;
            }
        }

        break;
    case MAP_NAME_POPUP_STATE_END:
    default:
        break;
    }
}

static void MapNamePopUp_PrintMapName(MapNamePopUp *mapPopUp, const String *string)
{
    TextColor color = TEXT_COLOR(3, 2, 0);
    Text_AddPrinterWithParamsAndColor(&mapPopUp->window, FONT_SYSTEM, string, mapPopUp->xOffset, 8 * 2, TEXT_SPEED_INSTANT, color, NULL);
}

static void MapNamePopUp_StartSlideOut(MapNamePopUp *mapPopUp)
{
    mapPopUp->state = MAP_NAME_POPUP_STATE_SLIDE_OUT;
    mapPopUp->timer = 0;
}

MapNamePopUp *MapNamePopUp_Create(BgConfig *bgConfig)
{
    MapNamePopUp *mapPopUp = Heap_Alloc(HEAP_ID_FIELD1, sizeof(MapNamePopUp));
    mapPopUp->string = String_Init(22, HEAP_ID_FIELD1);

    MapNamePopUp_SetBgConfig(mapPopUp, bgConfig);
    MapNamePopUp_CreateWindow(mapPopUp);

    mapPopUp->msgLoader = MessageLoader_Init(MSG_LOADER_LOAD_ON_DEMAND, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_LOCATION_NAMES, HEAP_ID_FIELD1);
    return mapPopUp;
}

void MapNamePopUp_Destroy(MapNamePopUp *mapPopUp)
{
    MessageLoader_Free(mapPopUp->msgLoader);
    Window_Remove(&mapPopUp->window);
    String_Free(mapPopUp->string);
    Heap_Free(mapPopUp);

    mapPopUp = NULL;
}

void MapNamePopUp_Show(MapNamePopUp *mapPopUp, s32 mapLabelTextID, s32 mapLabelWindowID)
{
    u32 strWidth;

    mapPopUp->entryID = mapLabelTextID;

    if (mapPopUp->isInited == FALSE) {
        mapPopUp->isInited = TRUE;

        Bg_SetOffset(mapPopUp->bgConfig, BG_LAYER_MAIN_3, BG_OFFSET_UPDATE_SET_Y, 38);

        mapPopUp->yOffset = 38;
        mapPopUp->task = SysTask_Start(SysTask_MapNamePopUpWindow, mapPopUp, 0);
        mapPopUp->state = MAP_NAME_POPUP_STATE_SLIDE_IN;

        strWidth = MapHeader_LoadString(mapPopUp->msgLoader, mapPopUp->entryID, mapPopUp->string);
        mapPopUp->windowID = mapLabelWindowID;

        MapNamePopUp_DrawWindowFrame(mapPopUp, strWidth);
        MapNamePopUp_PrintMapName(mapPopUp, mapPopUp->string);
    } else {
        switch (mapPopUp->state) {
        case MAP_NAME_POPUP_STATE_SLIDE_IN:
        case MAP_NAME_POPUP_STATE_WAIT:
            MapNamePopUp_StartSlideOut(mapPopUp);
            mapPopUp->shouldSlideIn = TRUE;
            mapPopUp->windowID = mapLabelWindowID;
            break;
        case MAP_NAME_POPUP_STATE_SLIDE_OUT:
            mapPopUp->shouldSlideIn = TRUE;
            mapPopUp->windowID = mapLabelWindowID;
            break;
        case MAP_NAME_POPUP_STATE_END:
        default:
            GF_ASSERT(FALSE);
            break;
        }
    }
}

void MapNamePopUp_Hide(MapNamePopUp *mapPopUp)
{
    if (mapPopUp->task != NULL) {
        SysTask_Done(mapPopUp->task);
    }

    Window_ClearAndCopyToVRAM(&mapPopUp->window);
    Bg_SetOffset(mapPopUp->bgConfig, BG_LAYER_MAIN_3, BG_OFFSET_UPDATE_SET_Y, 0);

    BgConfig *bgConfig = mapPopUp->bgConfig;
    MapNamePopUp_SetBgConfig(mapPopUp, bgConfig);
}

void FieldSystem_RequestLocationName(FieldSystem *fieldSystem)
{
    if (MapHeader_GetMapLabelWindowID(fieldSystem->location->mapHeaderID) == 0) {
        return;
    }

    if (!MapHeader_IsBuilding(fieldSystem->location->mapHeaderID)) {
        u32 mapLabelTextID = MapHeader_GetMapLabelTextID(fieldSystem->location->mapHeaderID);
        u32 mapLabelWindowID = MapHeader_GetMapLabelWindowID(fieldSystem->location->mapHeaderID);

        if (mapLabelWindowID != 0) {
            mapLabelWindowID--;
        }

        MapNamePopUp_Show(fieldSystem->unk_04->mapPopup, mapLabelTextID, mapLabelWindowID);
    }
}
