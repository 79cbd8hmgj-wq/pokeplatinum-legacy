#include <nitro.h>
#include <string.h>

#include "constants/narc.h"
#include "generated/sdat.h"

#include "applications/pokedex/opal_data.h"
#include "applications/pokedex/opalref.h"
#include "applications/pokedex/ov21_021D4340.h"
#include "applications/pokedex/pokedex_data_manager.h"
#include "applications/pokedex/pokedex_graphics.h"
#include "applications/pokedex/pokedex_graphics_manager.h"
#include "applications/pokedex/pokedex_main.h"
#include "applications/pokedex/pokedex_sort.h"
#include "applications/pokedex/struct_ov21_021D4660.h"

#include "bg_window.h"
#include "font.h"
#include "graphics.h"
#include "heap.h"
#include "message.h"
#include "message_util.h"
#include "narc.h"
#include "sound_playback.h"
#include "string_gf.h"
#include "string_template.h"
#include "system.h"
#include "text.h"
#include "touch_screen.h"
#include "touch_screen_actions.h"

#include "res/graphics/pokedex/zukan.naix"
#include "res/text/bank/pokedex.h"

enum OpalRefSubButton {
    OPALREFSUB_BUTTON_TAB_FIRST = 0,
    OPALREFSUB_BUTTON_TAB_LAST = OPAL_PAGE_MAX - 1,
    OPALREFSUB_BUTTON_PREV,
    OPALREFSUB_BUTTON_UP,
    OPALREFSUB_BUTTON_DOWN,
    OPALREFSUB_BUTTON_NEXT,
    OPALREFSUB_BUTTON_BACK,
    OPALREFSUB_NUM_BUTTONS
};

// Palette banks of the art layer: normal, selected tab, pressed.
#define OPALREFSUB_BANK_NORMAL   1
#define OPALREFSUB_BANK_SELECTED 2
#define OPALREFSUB_BANK_PRESSED  3

#define OPALREFSUB_HOLD_DELAY  12 // frames before a held scroll button repeats
#define OPALREFSUB_HOLD_PERIOD 4

#define OPALREFSUB_EXIT_BIT      (1 << 0)
#define OPALREFSUB_PALETTE_BYTES (4 * 32)

typedef struct OpalRefSubData {
    OpalRefState *state;
    TouchScreenActions *touchActions;
    TouchScreenHitTable hitTable[OPALREFSUB_NUM_BUTTONS];
    int heldFrames[OPALREFSUB_NUM_BUTTONS];
    BOOL pressed[OPALREFSUB_NUM_BUTTONS];
    int *command;
} OpalRefSubData;

typedef struct OpalRefSubGraphics {
    u16 savedPalette[OPALREFSUB_PALETTE_BYTES / 2]; // sub BG palette banks 0-3 before this screen
    Window header;
    Window tabRow[OPALREF_TAB_ROWS];
    Window buttonRow;
    Window back;
    Window hint;
    u32 renderedVersion;
    int highlightedPage;
    BOOL pressedShown[OPALREFSUB_NUM_BUTTONS];
} OpalRefSubGraphics;

static const u32 sTextColor = TEXT_COLOR(1, 2, 0);
static const u32 sHeaderColor = TEXT_COLOR(8, 9, 0);
static const u32 sDimColor = TEXT_COLOR(5, 2, 0);
static const u32 sGoldColor = TEXT_COLOR(4, 2, 0);

static PokedexGraphicData **AllocateGraphicsData(enum HeapID heapID, PokedexApp *pokedexApp);
static UnkStruct_ov21_021D4660 *AllocateScreenStates(enum HeapID heapID, PokedexApp *pokedexApp);
static int GetNumScreenStates(void);
static int InitData(PokedexDataManager *dataMan, void *data);
static int UpdateData(PokedexDataManager *dataMan, void *data);
static int FinalizeData(PokedexDataManager *dataMan, void *data);
static int InitGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan);
static int UpdateGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan);
static int FinalizeGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan);
static void SetHitRect(TouchScreenHitTable *hitTable, int x, int y, int w, int h);
static void TouchAction(u32 button, enum TouchScreenButtonState buttonState, void *context);
static void HandleKeys(OpalRefSubData *subData);
static void RequestExit(OpalRefSubData *subData);
static void StepPage(OpalRefSubData *subData, int step);
static void ButtonGeometry(int button, int *x, int *y, int *w, int *h);
static void LoadBackground(OpalRefSubGraphics *subGraphics, PokedexGraphicData *graphicData, enum HeapID heapID);
static void AddWindows(OpalRefSubGraphics *subGraphics, PokedexGraphicData *graphicData);
static void RemoveWindows(OpalRefSubGraphics *subGraphics);
static void RenderStaticText(OpalRefSubGraphics *subGraphics, enum HeapID heapID);
static void RenderHeader(OpalRefSubGraphics *subGraphics, const OpalRefState *state, enum HeapID heapID);
static void PrintCentered(Window *window, MessageLoader *loader, u32 messageID, int x, int width, int y, u32 color);
static void RefreshButtons(OpalRefSubGraphics *subGraphics, PokedexGraphicData *graphicData, const OpalRefState *state, const OpalRefSubData *subData);

void OpalRefSub_InitScreen(PokedexScreenManager *screenManager, PokedexApp *pokedexApp, enum HeapID heapID)
{
    screenManager->pageData = ov21_021D1410(pokedexApp, 10)->pageData; // shared OpalRefState
    screenManager->pageGraphics = AllocateGraphicsData(heapID, pokedexApp);
    screenManager->screenStates = AllocateScreenStates(heapID, pokedexApp);
    screenManager->numStates = GetNumScreenStates();
    screenManager->dataFunc[0] = InitData;
    screenManager->dataFunc[1] = UpdateData;
    screenManager->dataFunc[2] = FinalizeData;
    screenManager->graphicsFunc[0] = InitGraphics;
    screenManager->graphicsFunc[1] = UpdateGraphics;
    screenManager->graphicsFunc[2] = FinalizeGraphics;
}

void OpalRefSub_FreeScreen(PokedexScreenManager *screenManager)
{
    GF_ASSERT(screenManager->pageGraphics);
    GF_ASSERT(screenManager->screenStates);

    Heap_Free(screenManager->pageGraphics);
    ov21_021D4660(&screenManager->screenStates[0]);
    Heap_Free(screenManager->screenStates);
}

static PokedexGraphicData **AllocateGraphicsData(enum HeapID heapID, PokedexApp *pokedexApp)
{
    PokedexGraphicData **graphicsData = Heap_Alloc(heapID, sizeof(PokedexGraphicData *));

    GF_ASSERT(graphicsData);
    memset(graphicsData, 0, sizeof(PokedexGraphicData *));

    *graphicsData = PokedexMain_GetGraphicData(pokedexApp);

    return graphicsData;
}

// State 0 leaves the Opal pages and re-enters the species Info tab.
static UnkStruct_ov21_021D4660 *AllocateScreenStates(enum HeapID heapID, PokedexApp *pokedexApp)
{
    UnkStruct_ov21_021D4660 *states = Heap_Alloc(heapID, sizeof(UnkStruct_ov21_021D4660) * GetNumScreenStates());

    GF_ASSERT(states);
    memset(states, 0, sizeof(UnkStruct_ov21_021D4660) * GetNumScreenStates());

    ov21_021D475C(heapID, &states[0], pokedexApp, OPALREFSUB_EXIT_BIT);

    return states;
}

static int GetNumScreenStates(void)
{
    return 1;
}

static void ButtonGeometry(int button, int *x, int *y, int *w, int *h)
{
    if (button <= OPALREFSUB_BUTTON_TAB_LAST) {
        *x = OPALREF_TAB_X0 + (button % OPALREF_TAB_COLS) * OPALREF_TAB_W;
        *y = OPALREF_TAB_Y0 + (button / OPALREF_TAB_COLS) * OPALREF_TAB_ROW_PITCH;
        *w = OPALREF_TAB_W;
        *h = OPALREF_TAB_H;
    } else if (button == OPALREFSUB_BUTTON_BACK) {
        *x = OPALREF_BACK_X;
        *y = OPALREF_BACK_Y;
        *w = OPALREF_BACK_W;
        *h = OPALREF_BACK_H;
    } else {
        *x = OPALREF_TAB_X0 + (button - OPALREFSUB_BUTTON_PREV) * OPALREF_BTN_W;
        *y = OPALREF_BTN_Y;
        *w = OPALREF_BTN_W;
        *h = OPALREF_BTN_H;
    }
}

static void SetHitRect(TouchScreenHitTable *hitTable, int x, int y, int w, int h)
{
    PokedexMain_SetHitTableRect(hitTable, y, y + h, x, x + w);
}

static int InitData(PokedexDataManager *dataMan, void *data)
{
    OpalRefState *state = data;
    OpalRefSubData *subData = Heap_Alloc(dataMan->heapID, sizeof(OpalRefSubData));
    int button, x, y, w, h;

    GF_ASSERT(subData);
    memset(subData, 0, sizeof(OpalRefSubData));

    subData->state = state;
    subData->command = ov21_021D13A0(state->pokedexApp);

    for (button = 0; button < OPALREFSUB_NUM_BUTTONS; button++) {
        ButtonGeometry(button, &x, &y, &w, &h);
        SetHitRect(&subData->hitTable[button], x, y, w, h);
    }

    subData->touchActions = TouchScreenActions_RegisterHandler(subData->hitTable, OPALREFSUB_NUM_BUTTONS, TouchAction, subData, dataMan->heapID);
    dataMan->pageData = subData;

    return TRUE;
}

static int UpdateData(PokedexDataManager *dataMan, void *data)
{
    OpalRefSubData *subData = dataMan->pageData;

    if (dataMan->exit == TRUE) {
        return TRUE;
    }

    if (dataMan->unchanged == TRUE) {
        return FALSE;
    }

    HandleKeys(subData);
    TouchScreenActions_HandleAction(subData->touchActions);

    return FALSE;
}

static int FinalizeData(PokedexDataManager *dataMan, void *data)
{
    OpalRefSubData *subData = dataMan->pageData;

    TouchScreenActions_Free(subData->touchActions);
    Heap_Free(subData);
    dataMan->pageData = NULL;

    return TRUE;
}

static void RequestExit(OpalRefSubData *subData)
{
    // Returning to the Info tab: its main screen fades rather than slides.
    subData->state->infoState->animationMode = ANIM_BLEND;
    *subData->command |= OPALREFSUB_EXIT_BIT;
    Sound_PlayEffect(SEQ_SE_DP_DECIDE);
}

static void StepPage(OpalRefSubData *subData, int step)
{
    int page = (subData->state->page + step + OPAL_PAGE_MAX) % OPAL_PAGE_MAX;

    OpalRef_SetPage(subData->state, page);
    Sound_PlayEffect(SEQ_SE_DP_DENSI06);
}

static void HandleKeys(OpalRefSubData *subData)
{
    OpalRefState *state = subData->state;

    if (gSystem.pressedKeys & PAD_BUTTON_B) {
        RequestExit(subData);
        return;
    }

    if (gSystem.pressedKeys & (PAD_KEY_RIGHT | PAD_BUTTON_A)) {
        StepPage(subData, 1);
    }

    if (gSystem.pressedKeys & PAD_KEY_LEFT) {
        StepPage(subData, -1);
    }

    if (gSystem.pressedKeys & PAD_BUTTON_L) {
        if (OpalRef_StepSpecies(state, -1)) {
            Sound_PlayEffect(SEQ_SE_DP_DENSI06);
        }
    }

    if (gSystem.pressedKeys & PAD_BUTTON_R) {
        if (OpalRef_StepSpecies(state, 1)) {
            Sound_PlayEffect(SEQ_SE_DP_DENSI06);
        }
    }

    if (gSystem.pressedKeysRepeatable & PAD_KEY_UP) {
        if (OpalRef_Scroll(state, -1)) {
            Sound_PlayEffect(SEQ_SE_DP_DENSI06);
        }
    }

    if (gSystem.pressedKeysRepeatable & PAD_KEY_DOWN) {
        if (OpalRef_Scroll(state, 1)) {
            Sound_PlayEffect(SEQ_SE_DP_DENSI06);
        }
    }
}

static void TouchAction(u32 button, enum TouchScreenButtonState buttonState, void *context)
{
    OpalRefSubData *subData = context;
    OpalRefState *state = subData->state;

    switch (buttonState) {
    case TOUCH_BUTTON_PRESSED:
        subData->pressed[button] = TRUE;
        subData->heldFrames[button] = 0;

        if (button <= OPALREFSUB_BUTTON_TAB_LAST) {
            if (state->page != (int)button) {
                OpalRef_SetPage(state, button);
                Sound_PlayEffect(SEQ_SE_DP_DENSI06);
            }
        } else if (button == OPALREFSUB_BUTTON_PREV) {
            if (OpalRef_StepSpecies(state, -1)) {
                Sound_PlayEffect(SEQ_SE_DP_DENSI06);
            }
        } else if (button == OPALREFSUB_BUTTON_NEXT) {
            if (OpalRef_StepSpecies(state, 1)) {
                Sound_PlayEffect(SEQ_SE_DP_DENSI06);
            }
        } else if (button == OPALREFSUB_BUTTON_UP) {
            if (OpalRef_Scroll(state, -1)) {
                Sound_PlayEffect(SEQ_SE_DP_DENSI06);
            }
        } else if (button == OPALREFSUB_BUTTON_DOWN) {
            if (OpalRef_Scroll(state, 1)) {
                Sound_PlayEffect(SEQ_SE_DP_DENSI06);
            }
        } else if (button == OPALREFSUB_BUTTON_BACK) {
            RequestExit(subData);
        }
        break;
    case TOUCH_BUTTON_HELD:
        subData->pressed[button] = TRUE;
        subData->heldFrames[button]++;

        if (button == OPALREFSUB_BUTTON_UP || button == OPALREFSUB_BUTTON_DOWN) {
            int held = subData->heldFrames[button];

            if (held >= OPALREFSUB_HOLD_DELAY && (held - OPALREFSUB_HOLD_DELAY) % OPALREFSUB_HOLD_PERIOD == 0) {
                OpalRef_Scroll(state, button == OPALREFSUB_BUTTON_UP ? -1 : 1);
            }
        }
        break;
    case TOUCH_BUTTON_RELEASED:
    case TOUCH_BUTTON_HELD_OUT_OF_BOUNDS:
        subData->pressed[button] = FALSE;
        subData->heldFrames[button] = 0;
        break;
    default:
        break;
    }
}

static int InitGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan)
{
    const OpalRefState *state = data;
    const OpalRefSubData *subData = dataMan->pageData;
    PokedexGraphicData **graphicsData = graphics;
    OpalRefSubGraphics *subGraphics = graphicsMan->pageGraphics;

    switch (graphicsMan->state) {
    case 0:
        graphicsMan->pageGraphics = Heap_Alloc(graphicsMan->heapID, sizeof(OpalRefSubGraphics));
        memset(graphicsMan->pageGraphics, 0, sizeof(OpalRefSubGraphics));
        ((OpalRefSubGraphics *)graphicsMan->pageGraphics)->highlightedPage = -1;
        graphicsMan->state++;
        break;
    case 1:
        LoadBackground(subGraphics, *graphicsData, graphicsMan->heapID);
        AddWindows(subGraphics, *graphicsData);
        RenderStaticText(subGraphics, graphicsMan->heapID);
        RenderHeader(subGraphics, state, graphicsMan->heapID);
        subGraphics->renderedVersion = state->renderVersion;
        RefreshButtons(subGraphics, *graphicsData, state, subData);
        PokedexGraphics_InitBlendTransition(&(*graphicsData)->blendSub, 1, -16, 0, 0, 16, (GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), (GX_BLEND_PLANEMASK_BG0 | GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), 1);
        graphicsMan->state++;
        break;
    case 2:
        if (PokedexGraphics_TakeBlendTransitionStep(&(*graphicsData)->blendSub)) {
            graphicsMan->state++;
        }
        break;
    case 3:
        G2S_BlendNone();
        return TRUE;
    default:
        break;
    }

    return FALSE;
}

static int UpdateGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan)
{
    const OpalRefState *state = data;
    const OpalRefSubData *subData = dataMan->pageData;
    PokedexGraphicData **graphicsData = graphics;
    OpalRefSubGraphics *subGraphics = graphicsMan->pageGraphics;

    if (subGraphics->renderedVersion != state->renderVersion) {
        RenderHeader(subGraphics, state, graphicsMan->heapID);
        subGraphics->renderedVersion = state->renderVersion;
    }

    RefreshButtons(subGraphics, *graphicsData, state, subData);

    return FALSE;
}

static int FinalizeGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan)
{
    PokedexGraphicData **graphicsData = graphics;
    OpalRefSubGraphics *subGraphics = graphicsMan->pageGraphics;

    switch (graphicsMan->state) {
    case 0:
        PokedexGraphics_InitBlendTransition(&(*graphicsData)->blendSub, 1, 0, -16, 16, 0, (GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), (GX_BLEND_PLANEMASK_BG0 | GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), 1);
        graphicsMan->state++;
        break;
    case 1:
        if (PokedexGraphics_TakeBlendTransitionStep(&(*graphicsData)->blendSub)) {
            graphicsMan->state++;
        }
        break;
    case 2:
        RemoveWindows(subGraphics);
        Bg_ClearTilemap((*graphicsData)->bgConfig, BG_LAYER_SUB_2);
        Bg_ClearTilemap((*graphicsData)->bgConfig, BG_LAYER_SUB_1);
        GXS_LoadBGPltt(subGraphics->savedPalette, 0, OPALREFSUB_PALETTE_BYTES);
        graphicsMan->state++;
        break;
    case 3:
        Heap_Free(graphicsMan->pageGraphics);
        graphicsMan->pageGraphics = NULL;
        graphicsMan->state++;
        break;
    case 4:
        return TRUE;
    default:
        break;
    }

    return FALSE;
}

static void LoadBackground(OpalRefSubGraphics *subGraphics, PokedexGraphicData *graphicData, enum HeapID heapID)
{
    void *tilemapData;
    NNSG2dScreenData *screenData;

    // Keep the Info tab's sub palette banks; restored in FinalizeGraphics.
    MI_CpuCopy16((void *)HW_DB_BG_PLTT, subGraphics->savedPalette, OPALREFSUB_PALETTE_BYTES);
    PokedexGraphics_LoadGraphicNarcPaletteData(graphicData, opal_ref_NCLR, PAL_LOAD_SUB_BG, 0, OPALREFSUB_PALETTE_BYTES, heapID);
    PokedexGraphics_LoadGraphicNarcCharacterData(graphicData, opal_ref_sub_NCGR_lz, graphicData->bgConfig, BG_LAYER_SUB_2, 0, 0, TRUE, heapID);

    tilemapData = PokedexGraphics_GetGraphicNarcTilemapData(graphicData, opal_ref_sub_NSCR_lz, TRUE, &screenData, heapID);
    Bg_LoadToTilemapRect(graphicData->bgConfig, BG_LAYER_SUB_2, screenData->rawData, 0, 0, screenData->screenWidth / 8, screenData->screenHeight / 8);
    Heap_Free(tilemapData);
    Bg_ScheduleTilemapTransfer(graphicData->bgConfig, BG_LAYER_SUB_2);
}

// 414 of the 512 tiles SUB_1's character block can hold before it meets SUB_2's.
static void AddWindows(OpalRefSubGraphics *subGraphics, PokedexGraphicData *graphicData)
{
    BgConfig *bgConfig = graphicData->bgConfig;
    int row;
    int baseTile = 0;

    Window_Add(bgConfig, &subGraphics->header, BG_LAYER_SUB_1, 0, 0, 32, 2, 0, baseTile);
    baseTile += 32 * 2;

    for (row = 0; row < OPALREF_TAB_ROWS; row++) {
        Window_Add(bgConfig, &subGraphics->tabRow[row], BG_LAYER_SUB_1, OPALREF_TAB_X0 / 8, (OPALREF_TAB_Y0 + row * OPALREF_TAB_ROW_PITCH) / 8, 28, 3, 0, baseTile);
        baseTile += 28 * 3;
    }

    Window_Add(bgConfig, &subGraphics->buttonRow, BG_LAYER_SUB_1, OPALREF_TAB_X0 / 8, OPALREF_BTN_Y / 8, 28, 3, 0, baseTile);
    baseTile += 28 * 3;
    Window_Add(bgConfig, &subGraphics->back, BG_LAYER_SUB_1, OPALREF_BACK_X / 8, OPALREF_BACK_Y / 8, OPALREF_BACK_W / 8, 3, 0, baseTile);
    baseTile += (OPALREF_BACK_W / 8) * 3;
    Window_Add(bgConfig, &subGraphics->hint, BG_LAYER_SUB_1, OPALREF_TAB_X0 / 8, 22, 28, 2, 0, baseTile);

    Window_FillTilemap(&subGraphics->header, 0);
    Window_FillTilemap(&subGraphics->tabRow[0], 0);
    Window_FillTilemap(&subGraphics->tabRow[1], 0);
    Window_FillTilemap(&subGraphics->buttonRow, 0);
    Window_FillTilemap(&subGraphics->back, 0);
    Window_FillTilemap(&subGraphics->hint, 0);
}

static void RemoveWindows(OpalRefSubGraphics *subGraphics)
{
    int row;

    Window_ClearAndCopyToVRAM(&subGraphics->header);
    Window_Remove(&subGraphics->header);

    for (row = 0; row < OPALREF_TAB_ROWS; row++) {
        Window_ClearAndCopyToVRAM(&subGraphics->tabRow[row]);
        Window_Remove(&subGraphics->tabRow[row]);
    }

    Window_ClearAndCopyToVRAM(&subGraphics->buttonRow);
    Window_Remove(&subGraphics->buttonRow);
    Window_ClearAndCopyToVRAM(&subGraphics->back);
    Window_Remove(&subGraphics->back);
    Window_ClearAndCopyToVRAM(&subGraphics->hint);
    Window_Remove(&subGraphics->hint);
}

static void PrintCentered(Window *window, MessageLoader *loader, u32 messageID, int x, int width, int y, u32 color)
{
    String *string = MessageLoader_GetNewString(loader, messageID);
    u32 textWidth = Font_CalcMaxLineWidth(FONT_SYSTEM, string, 0);

    Text_AddPrinterWithParamsAndColor(window, FONT_SYSTEM, string, x + (width - textWidth) / 2, y, TEXT_SPEED_INSTANT, color, NULL);
    String_Free(string);
}

static void RenderStaticText(OpalRefSubGraphics *subGraphics, enum HeapID heapID)
{
    MessageLoader *loader = MessageLoader_Init(MSG_LOADER_PRELOAD_ENTIRE_BANK, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_POKEDEX, heapID);
    int page;

    for (page = 0; page < OPAL_PAGE_MAX; page++) {
        PrintCentered(&subGraphics->tabRow[page / OPALREF_TAB_COLS], loader, OpalRef_PageTabMessage(page), (page % OPALREF_TAB_COLS) * OPALREF_TAB_W, OPALREF_TAB_W, 4, sTextColor);
    }

    PrintCentered(&subGraphics->buttonRow, loader, pl_msg_pokedex_opal_btn_prev, 0 * OPALREF_BTN_W, OPALREF_BTN_W, 4, sTextColor);
    PrintCentered(&subGraphics->buttonRow, loader, pl_msg_pokedex_opal_btn_up, 1 * OPALREF_BTN_W, OPALREF_BTN_W, 4, sTextColor);
    PrintCentered(&subGraphics->buttonRow, loader, pl_msg_pokedex_opal_btn_down, 2 * OPALREF_BTN_W, OPALREF_BTN_W, 4, sTextColor);
    PrintCentered(&subGraphics->buttonRow, loader, pl_msg_pokedex_opal_btn_next, 3 * OPALREF_BTN_W, OPALREF_BTN_W, 4, sTextColor);
    PrintCentered(&subGraphics->back, loader, pl_msg_pokedex_opal_back, 0, OPALREF_BACK_W, 4, sTextColor);
    PrintCentered(&subGraphics->hint, loader, pl_msg_pokedex_opal_sub_hint, 0, 28 * 8, 0, sDimColor);

    MessageLoader_Free(loader);

    Window_CopyToVRAM(&subGraphics->tabRow[0]);
    Window_CopyToVRAM(&subGraphics->tabRow[1]);
    Window_CopyToVRAM(&subGraphics->buttonRow);
    Window_CopyToVRAM(&subGraphics->back);
    Window_CopyToVRAM(&subGraphics->hint);
}

static void RenderHeader(OpalRefSubGraphics *subGraphics, const OpalRefState *state, enum HeapID heapID)
{
    MessageLoader *loader = MessageLoader_Init(MSG_LOADER_PRELOAD_ENTIRE_BANK, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_POKEDEX, heapID);
    StringTemplate *template = StringTemplate_Default(heapID);
    String *text;
    String *name;
    u32 width;

    Window_FillTilemap(&subGraphics->header, 0);

    if (state->seen) {
        StringTemplate_SetNumber(template, 0, state->species, 3, PADDING_MODE_ZEROES, CHARSET_MODE_EN);
        text = MessageUtil_ExpandedString(template, loader, pl_msg_pokedex_opal_dex_no, heapID);
        Text_AddPrinterWithParamsAndColor(&subGraphics->header, FONT_SYSTEM, text, 8, 1, TEXT_SPEED_INSTANT, sGoldColor, NULL);
        String_Free(text);

        name = MessageUtil_SpeciesName(state->species, heapID);
        Text_AddPrinterWithParamsAndColor(&subGraphics->header, FONT_SYSTEM, name, 80, 1, TEXT_SPEED_INSTANT, sHeaderColor, NULL);
        String_Free(name);
    } else {
        name = MessageLoader_GetNewString(loader, pl_msg_pokedex_opal_unknown);
        Text_AddPrinterWithParamsAndColor(&subGraphics->header, FONT_SYSTEM, name, 8, 1, TEXT_SPEED_INSTANT, sHeaderColor, NULL);
        String_Free(name);
    }

    StringTemplate_SetNumber(template, 0, state->page + 1, 1, PADDING_MODE_NONE, CHARSET_MODE_EN);
    StringTemplate_SetNumber(template, 1, OPAL_PAGE_MAX, 1, PADDING_MODE_NONE, CHARSET_MODE_EN);
    text = MessageUtil_ExpandedString(template, loader, pl_msg_pokedex_opal_page_of, heapID);
    width = Font_CalcMaxLineWidth(FONT_SYSTEM, text, 0);
    Text_AddPrinterWithParamsAndColor(&subGraphics->header, FONT_SYSTEM, text, 248 - width, 1, TEXT_SPEED_INSTANT, sHeaderColor, NULL);
    String_Free(text);

    Window_CopyToVRAM(&subGraphics->header);

    StringTemplate_Free(template);
    MessageLoader_Free(loader);
}

// Page changes move the selected tab; presses tint the touched button.
static void RefreshButtons(OpalRefSubGraphics *subGraphics, PokedexGraphicData *graphicData, const OpalRefState *state, const OpalRefSubData *subData)
{
    BgConfig *bgConfig = graphicData->bgConfig;
    BOOL changed = FALSE;
    int button, x, y, w, h, bank;

    for (button = 0; button < OPALREFSUB_NUM_BUTTONS; button++) {
        BOOL pressed = subData->pressed[button];
        BOOL selectedChanged = FALSE;

        if (button <= OPALREFSUB_BUTTON_TAB_LAST) {
            selectedChanged = (subGraphics->highlightedPage == button) != (state->page == button);
        }

        if (pressed == subGraphics->pressedShown[button] && !selectedChanged && subGraphics->highlightedPage != -1) {
            continue;
        }

        ButtonGeometry(button, &x, &y, &w, &h);

        if (pressed) {
            bank = OPALREFSUB_BANK_PRESSED;
        } else if (button <= OPALREFSUB_BUTTON_TAB_LAST && state->page == button) {
            bank = OPALREFSUB_BANK_SELECTED;
        } else {
            bank = OPALREFSUB_BANK_NORMAL;
        }

        Bg_ChangeTilemapRectPalette(bgConfig, BG_LAYER_SUB_2, x / 8, y / 8, w / 8, h / 8, bank);
        subGraphics->pressedShown[button] = pressed;
        changed = TRUE;
    }

    subGraphics->highlightedPage = state->page;

    if (changed) {
        Bg_ScheduleTilemapTransfer(bgConfig, BG_LAYER_SUB_2);
    }
}
