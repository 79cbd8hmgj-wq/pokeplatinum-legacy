#include "applications/still_card.h"

#include <nitro.h>
#include <string.h>

#include "constants/heap.h"
#include "constants/narc.h"

#include "bg_window.h"
#include "font.h"
#include "game_options.h"
#include "graphics.h"
#include "gx_layers.h"
#include "heap.h"
#include "message.h"
#include "overlay_manager.h"
#include "palette.h"
#include "render_text.h"
#include "render_window.h"
#include "save_player.h"
#include "screen_fade.h"
#include "sound_playback.h"
#include "string_gf.h"
#include "system.h"
#include "text.h"
#include "touch_screen.h"

#include "res/graphics/still_card/still_card.naix"
#include "res/text/bank/menu_entries.h"
#include "res/text/bank/solaceon_town_pokemon_news_press.h"

// Main-screen layout (tiles unless noted).
#define PAGE_ART_TILES      (32 * 24)
#define MESSAGE_FRAME_TILES 64 // tiles reserved at the start of BG0 for the native message frame / scroll arrow
#define MESSAGE_FRAME_PAL   14
#define TEXT_PAL            2
#define ART_PAL             1
#define ART_TILE_LEFT       12
#define ART_TILE_TOP        8
#define ART_TILES_PER_SIDE  8
#define ART_FIRST_TILE      8 // art PNGs start with one blank tile row so tile 0 is transparent

#define HEAD_WINDOW_WIDTH  32
#define HEAD_WINDOW_HEIGHT 7
#define BODY_WINDOW_LEFT   2
#define BODY_WINDOW_TOP    17
#define BODY_WINDOW_WIDTH  27
#define BODY_WINDOW_HEIGHT 6

// Sub-screen (touch) layout.
#define PANEL_WINDOW_LEFT     3
#define PANEL_WINDOW_TOP      2
#define PANEL_WINDOW_WIDTH    26
#define PANEL_WINDOW_HEIGHT   20
#define PANEL_ACTIVE_PAL      3
#define PANEL_BUTTON_TOP_PX   16
#define PANEL_BUTTON_STEP     32
#define PANEL_BUTTON_H_PX     24
#define PANEL_BUTTON_LEFT_PX  24
#define PANEL_BUTTON_RIGHT_PX 231

enum StillCardRunState {
    STILL_CARD_STATE_SETUP = 0,
    STILL_CARD_STATE_FADE_IN,
    STILL_CARD_STATE_RUN,
    STILL_CARD_STATE_FADE_OUT,
    STILL_CARD_STATE_DONE,
};

// A card descriptor selects the art, headline and article text for each state.
typedef struct StillCardStateDesc {
    u16 headlineMsg; // menu_entries bank
    u16 articleMsg; // card text bank
    u16 artNcgr;
    u16 artNclr;
} StillCardStateDesc;

typedef struct StillCardDesc {
    u16 numStates;
    u16 textBank;
    u16 mastheadMsg;
    u16 exitMsg; // menu_entries bank
    u16 pageNcgr;
    u16 pageNclr;
    u16 panelNcgr;
    u16 panelNclr;
    u16 panelActiveNclr;
    const StillCardStateDesc *states;
} StillCardDesc;

static const StillCardStateDesc sSolaceonNewsStates[] = {
    { MenuEntries_Text_Article_DuskBall, SolaceonTownPokemonNewsPress_Text_ArticleDuskBall, art_dusk_NCGR, art_dusk_NCLR },
    { MenuEntries_Text_Article_HealBall, SolaceonTownPokemonNewsPress_Text_ArticleHealBall, art_heal_NCGR, art_heal_NCLR },
    { MenuEntries_Text_Article_QuickBall, SolaceonTownPokemonNewsPress_Text_ArticleQuickBall, art_quick_NCGR, art_quick_NCLR },
    { MenuEntries_Text_Article_DiveBall, SolaceonTownPokemonNewsPress_Text_ArticleDiveBall, art_dive_NCGR, art_dive_NCLR },
};

static const StillCardDesc sStillCardDescs[STILL_CARD_COUNT] = {
    [STILL_CARD_SOLACEON_NEWS_PRESS] = {
        .numStates = NELEMS(sSolaceonNewsStates),
        .textBank = TEXT_BANK_SOLACEON_TOWN_POKEMON_NEWS_PRESS,
        .mastheadMsg = SolaceonTownPokemonNewsPress_Text_CardMasthead,
        .exitMsg = MenuEntries_Text_Article_Exit,
        .pageNcgr = page_NCGR,
        .pageNclr = page_NCLR,
        .panelNcgr = panel_NCGR,
        .panelNclr = panel_NCLR,
        .panelActiveNclr = panel_active_NCLR,
        .states = sSolaceonNewsStates,
    },
};

// Touch targets on the bottom screen: one per card state, then exit.
static const TouchScreenRect sTouchRects[] = {
    { .rect = { PANEL_BUTTON_TOP_PX + 0 * PANEL_BUTTON_STEP, PANEL_BUTTON_TOP_PX + 0 * PANEL_BUTTON_STEP + PANEL_BUTTON_H_PX - 1, PANEL_BUTTON_LEFT_PX, PANEL_BUTTON_RIGHT_PX } },
    { .rect = { PANEL_BUTTON_TOP_PX + 1 * PANEL_BUTTON_STEP, PANEL_BUTTON_TOP_PX + 1 * PANEL_BUTTON_STEP + PANEL_BUTTON_H_PX - 1, PANEL_BUTTON_LEFT_PX, PANEL_BUTTON_RIGHT_PX } },
    { .rect = { PANEL_BUTTON_TOP_PX + 2 * PANEL_BUTTON_STEP, PANEL_BUTTON_TOP_PX + 2 * PANEL_BUTTON_STEP + PANEL_BUTTON_H_PX - 1, PANEL_BUTTON_LEFT_PX, PANEL_BUTTON_RIGHT_PX } },
    { .rect = { PANEL_BUTTON_TOP_PX + 3 * PANEL_BUTTON_STEP, PANEL_BUTTON_TOP_PX + 3 * PANEL_BUTTON_STEP + PANEL_BUTTON_H_PX - 1, PANEL_BUTTON_LEFT_PX, PANEL_BUTTON_RIGHT_PX } },
    { .rect = { PANEL_BUTTON_TOP_PX + 4 * PANEL_BUTTON_STEP, PANEL_BUTTON_TOP_PX + 4 * PANEL_BUTTON_STEP + PANEL_BUTTON_H_PX - 1, PANEL_BUTTON_LEFT_PX, PANEL_BUTTON_RIGHT_PX } },
    { .rect = { TOUCHSCREEN_TABLE_TERMINATOR, 0, 0, 0 } },
};

typedef struct StillCard {
    enum HeapID heapID;
    const StillCardDesc *desc;
    SaveData *saveData;
    BgConfig *bgConfig;
    Window headWindow;
    Window bodyWindow;
    Window panelWindow;
    MessageLoader *cardLoader;
    MessageLoader *menuLoader;
    String *string;
    u8 current;
    u8 printerID;
    u8 printerActive;
    u8 textFrameDelay;
} StillCard;

static void StillCard_VBlankCallback(void *data);
static void StillCard_InitBgs(StillCard *card);
static void StillCard_FreeBgs(StillCard *card);
static void StillCard_InitWindows(StillCard *card);
static void StillCard_FreeWindows(StillCard *card);
static void StillCard_LoadStaticGraphics(StillCard *card);
static void StillCard_DrawPanelLabels(StillCard *card);
static void StillCard_ShowState(StillCard *card, u8 index);
static void StillCard_CancelPrinter(StillCard *card);
static void StillCard_DrawCentered(StillCard *card, Window *window, u32 y, u32 msgBank, u32 msgID);

BOOL StillCard_Init(ApplicationManager *appMan, int *state)
{
    enum HeapID heapID = HEAP_ID_STILL_CARD;

    Heap_Create(HEAP_ID_APPLICATION, heapID, 0x20000);

    StillCard *card = ApplicationManager_NewData(appMan, sizeof(StillCard), heapID);
    memset(card, 0, sizeof(StillCard));
    card->heapID = heapID;

    StillCardData *args = ApplicationManager_Args(appMan);
    GF_ASSERT(args->cardID < STILL_CARD_COUNT);

    card->desc = &sStillCardDescs[args->cardID];
    card->saveData = args->saveData;
    card->current = args->startState < card->desc->numStates ? args->startState : 0;
    card->textFrameDelay = Options_TextFrameDelay(SaveData_GetOptions(card->saveData));

    SetScreenColorBrightness(DS_SCREEN_MAIN, COLOR_BLACK);
    SetScreenColorBrightness(DS_SCREEN_SUB, COLOR_BLACK);
    SetVBlankCallback(NULL, NULL);
    SetHBlankCallback(NULL, NULL);
    GXLayers_DisableEngineALayers();
    GXLayers_DisableEngineBLayers();

    GX_SetVisiblePlane(0);
    GXS_SetVisiblePlane(0);

    StillCard_InitBgs(card);
    StillCard_InitWindows(card);

    SetVBlankCallback(StillCard_VBlankCallback, card);
    GXLayers_TurnBothDispOn();

    return TRUE;
}

BOOL StillCard_Main(ApplicationManager *appMan, int *state)
{
    StillCard *card = ApplicationManager_Data(appMan);
    const StillCardDesc *desc = card->desc;

    switch (*state) {
    case STILL_CARD_STATE_SETUP:
        StillCard_LoadStaticGraphics(card);
        StillCard_DrawPanelLabels(card);
        StillCard_DrawCentered(card, &card->headWindow, 8, desc->textBank, desc->mastheadMsg);
        StillCard_ShowState(card, card->current);

        Bg_ToggleLayer(BG_LAYER_MAIN_0, TRUE);
        Bg_ToggleLayer(BG_LAYER_MAIN_1, TRUE);
        Bg_ToggleLayer(BG_LAYER_MAIN_3, TRUE);
        Bg_ToggleLayer(BG_LAYER_SUB_0, TRUE);
        Bg_ToggleLayer(BG_LAYER_SUB_3, TRUE);
        StartScreenFade(FADE_BOTH_SCREENS, FADE_TYPE_BRIGHTNESS_IN, FADE_TYPE_BRIGHTNESS_IN, COLOR_BLACK, 6, 1, card->heapID);
        *state = STILL_CARD_STATE_FADE_IN;
        break;

    case STILL_CARD_STATE_FADE_IN:
        if (IsScreenFadeDone() == TRUE) {
            *state = STILL_CARD_STATE_RUN;
        }
        break;

    case STILL_CARD_STATE_RUN: {
        BOOL shouldExit = FALSE;
        int next = card->current;
        int touched = TouchScreen_CheckRectanglePressed(sTouchRects);

        card->printerActive = card->printerActive && Text_IsPrinterActive(card->printerID);

        if (JOY_NEW(PAD_BUTTON_B) || touched == desc->numStates) {
            shouldExit = TRUE;
        } else if (touched >= 0 && touched < desc->numStates) {
            next = touched;
        } else if (JOY_NEW(PAD_KEY_RIGHT | PAD_KEY_DOWN | PAD_BUTTON_R)) {
            next = (card->current + 1) % desc->numStates;
        } else if (JOY_NEW(PAD_KEY_LEFT | PAD_KEY_UP | PAD_BUTTON_L)) {
            next = (card->current + desc->numStates - 1) % desc->numStates;
        } else if (JOY_NEW(PAD_BUTTON_A) && !card->printerActive) {
            // Printing is finished; the same A press that would dismiss the original
            // WaitButton message dismisses the card. While text is still paging, A is
            // consumed by the native text printer to advance \r / \f breaks.
            shouldExit = TRUE;
        }

        if (shouldExit) {
            StillCard_CancelPrinter(card);
            Sound_PlayEffect(SEQ_SE_CONFIRM);
            StartScreenFade(FADE_BOTH_SCREENS, FADE_TYPE_BRIGHTNESS_OUT, FADE_TYPE_BRIGHTNESS_OUT, COLOR_BLACK, 6, 1, card->heapID);
            *state = STILL_CARD_STATE_FADE_OUT;
        } else if (next != card->current) {
            Sound_PlayEffect(SEQ_SE_CONFIRM);
            StillCard_ShowState(card, next);
        }
        break;
    }

    case STILL_CARD_STATE_FADE_OUT:
        if (IsScreenFadeDone() == TRUE) {
            return TRUE;
        }
        break;
    }

    return FALSE;
}

BOOL StillCard_Exit(ApplicationManager *appMan, int *state)
{
    StillCard *card = ApplicationManager_Data(appMan);
    enum HeapID heapID = card->heapID;

    StillCard_CancelPrinter(card);
    SetVBlankCallback(NULL, NULL);
    StillCard_FreeWindows(card);
    StillCard_FreeBgs(card);

    GXLayers_DisableEngineALayers();
    GXLayers_DisableEngineBLayers();

    ApplicationManager_FreeData(appMan);
    Heap_Destroy(heapID);

    return TRUE;
}

static void StillCard_VBlankCallback(void *data)
{
    Bg_RunScheduledUpdates(((StillCard *)data)->bgConfig);
}

static void StillCard_InitBgs(StillCard *card)
{
    GXBanks banks = {
        GX_VRAM_BG_128_B,
        GX_VRAM_BGEXTPLTT_NONE,
        GX_VRAM_SUB_BG_128_C,
        GX_VRAM_SUB_BGEXTPLTT_NONE,
        GX_VRAM_OBJ_NONE,
        GX_VRAM_OBJEXTPLTT_NONE,
        GX_VRAM_SUB_OBJ_NONE,
        GX_VRAM_SUB_OBJEXTPLTT_NONE,
        GX_VRAM_TEX_NONE,
        GX_VRAM_TEXPLTT_NONE,
    };

    GXLayers_SetBanks(&banks);

    card->bgConfig = BgConfig_New(card->heapID);

    GraphicsModes graphicsModes = {
        .displayMode = GX_DISPMODE_GRAPHICS,
        .mainBgMode = GX_BGMODE_0,
        .subBgMode = GX_BGMODE_0,
        .bg0As2DOr3D = GX_BG0_AS_2D,
    };

    SetAllGraphicsModes(&graphicsModes);

    BgTemplate template = {
        .x = 0,
        .y = 0,
        .bufferSize = 0x800,
        .baseTile = 0,
        .screenSize = BG_SCREEN_SIZE_256x256,
        .colorMode = GX_BG_COLORMODE_16,
        .screenBase = GX_BG_SCRBASE_0x0000,
        .charBase = GX_BG_CHARBASE_0x10000,
        .bgExtPltt = GX_BG_EXTPLTT_01,
        .priority = 0,
        .areaOver = 0,
        .mosaic = FALSE,
    };

    // Text layer (frame/scroll arrow tiles, then window bitmaps).
    Bg_InitFromTemplate(card->bgConfig, BG_LAYER_MAIN_0, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(card->bgConfig, BG_LAYER_MAIN_0);
    Bg_InitFromTemplate(card->bgConfig, BG_LAYER_SUB_0, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(card->bgConfig, BG_LAYER_SUB_0);

    // Illustration layer (main only).
    template.screenBase = GX_BG_SCRBASE_0x0800;
    template.charBase = GX_BG_CHARBASE_0x0c000;
    template.priority = 1;
    Bg_InitFromTemplate(card->bgConfig, BG_LAYER_MAIN_1, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(card->bgConfig, BG_LAYER_MAIN_1);

    // Page / panel art layer.
    template.screenBase = GX_BG_SCRBASE_0x1000;
    template.charBase = GX_BG_CHARBASE_0x04000;
    template.priority = 3;
    Bg_InitFromTemplate(card->bgConfig, BG_LAYER_MAIN_3, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(card->bgConfig, BG_LAYER_MAIN_3);
    Bg_InitFromTemplate(card->bgConfig, BG_LAYER_SUB_3, &template, BG_TYPE_STATIC);
    Bg_ClearTilemap(card->bgConfig, BG_LAYER_SUB_3);

    Bg_ToggleLayer(BG_LAYER_MAIN_0, FALSE);
    Bg_ToggleLayer(BG_LAYER_MAIN_1, FALSE);
    Bg_ToggleLayer(BG_LAYER_MAIN_2, FALSE);
    Bg_ToggleLayer(BG_LAYER_MAIN_3, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_0, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_1, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_2, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_3, FALSE);
}

static void StillCard_FreeBgs(StillCard *card)
{
    Bg_ToggleLayer(BG_LAYER_MAIN_0, FALSE);
    Bg_ToggleLayer(BG_LAYER_MAIN_1, FALSE);
    Bg_ToggleLayer(BG_LAYER_MAIN_3, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_0, FALSE);
    Bg_ToggleLayer(BG_LAYER_SUB_3, FALSE);

    Bg_FreeTilemapBuffer(card->bgConfig, BG_LAYER_MAIN_0);
    Bg_FreeTilemapBuffer(card->bgConfig, BG_LAYER_MAIN_1);
    Bg_FreeTilemapBuffer(card->bgConfig, BG_LAYER_MAIN_3);
    Bg_FreeTilemapBuffer(card->bgConfig, BG_LAYER_SUB_0);
    Bg_FreeTilemapBuffer(card->bgConfig, BG_LAYER_SUB_3);
    Heap_Free(card->bgConfig);
}

static void StillCard_InitWindows(StillCard *card)
{
    Text_ResetAllPrinters();

    card->cardLoader = MessageLoader_Init(MSG_LOADER_LOAD_ON_DEMAND, NARC_INDEX_MSGDATA__PL_MSG, card->desc->textBank, card->heapID);
    card->menuLoader = MessageLoader_Init(MSG_LOADER_LOAD_ON_DEMAND, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_MENU_ENTRIES, card->heapID);
    card->string = String_Init(512, card->heapID);

    u16 baseTile = MESSAGE_FRAME_TILES;

    Window_Add(card->bgConfig, &card->headWindow, BG_LAYER_MAIN_0, 0, 0, HEAD_WINDOW_WIDTH, HEAD_WINDOW_HEIGHT, TEXT_PAL, baseTile);
    baseTile += HEAD_WINDOW_WIDTH * HEAD_WINDOW_HEIGHT;
    Window_Add(card->bgConfig, &card->bodyWindow, BG_LAYER_MAIN_0, BODY_WINDOW_LEFT, BODY_WINDOW_TOP, BODY_WINDOW_WIDTH, BODY_WINDOW_HEIGHT, TEXT_PAL, baseTile);
    Window_Add(card->bgConfig, &card->panelWindow, BG_LAYER_SUB_0, PANEL_WINDOW_LEFT, PANEL_WINDOW_TOP, PANEL_WINDOW_WIDTH, PANEL_WINDOW_HEIGHT, TEXT_PAL, 1);

    Window_FillTilemap(&card->headWindow, 0);
    Window_FillTilemap(&card->bodyWindow, 0);
    Window_FillTilemap(&card->panelWindow, 0);
}

static void StillCard_FreeWindows(StillCard *card)
{
    Window_Remove(&card->panelWindow);
    Window_Remove(&card->bodyWindow);
    Window_Remove(&card->headWindow);
    String_Free(card->string);
    MessageLoader_Free(card->menuLoader);
    MessageLoader_Free(card->cardLoader);
}

static void StillCard_LoadStaticGraphics(StillCard *card)
{
    const StillCardDesc *desc = card->desc;

    // Page (main BG3) and touch panel (sub BG3): 4bpp tiles in scan order, so the
    // tilemap is the identity mapping.
    Graphics_LoadTilesToBgLayer(NARC_INDEX_GRAPHIC__STILL_CARD, desc->pageNcgr, card->bgConfig, BG_LAYER_MAIN_3, 0, 0, FALSE, card->heapID);
    Graphics_LoadPalette(NARC_INDEX_GRAPHIC__STILL_CARD, desc->pageNclr, PAL_LOAD_MAIN_BG, PLTT_OFFSET(0), PALETTE_SIZE_BYTES, card->heapID);
    Graphics_LoadTilesToBgLayer(NARC_INDEX_GRAPHIC__STILL_CARD, desc->panelNcgr, card->bgConfig, BG_LAYER_SUB_3, 0, 0, FALSE, card->heapID);
    Graphics_LoadPalette(NARC_INDEX_GRAPHIC__STILL_CARD, desc->panelNclr, PAL_LOAD_SUB_BG, PLTT_OFFSET(0), PALETTE_SIZE_BYTES, card->heapID);
    Graphics_LoadPalette(NARC_INDEX_GRAPHIC__STILL_CARD, desc->panelActiveNclr, PAL_LOAD_SUB_BG, PLTT_OFFSET(PANEL_ACTIVE_PAL), PALETTE_SIZE_BYTES, card->heapID);

    u16 *mainMap = Bg_GetTilemapBuffer(card->bgConfig, BG_LAYER_MAIN_3);
    u16 *subMap = Bg_GetTilemapBuffer(card->bgConfig, BG_LAYER_SUB_3);

    for (int i = 0; i < PAGE_ART_TILES; i++) {
        mainMap[i] = i;
        subMap[i] = i;
    }

    Bg_CopyTilemapBufferToVRAM(card->bgConfig, BG_LAYER_MAIN_3);
    Bg_CopyTilemapBufferToVRAM(card->bgConfig, BG_LAYER_SUB_3);

    // Text layers: native message frame (provides the scroll-arrow tiles at base tile 0,
    // which is what the text printer assumes) and the standard font palette.
    LoadMessageBoxGraphics(card->bgConfig, BG_LAYER_MAIN_0, 0, MESSAGE_FRAME_PAL, Options_Frame(SaveData_GetOptions(card->saveData)), card->heapID);
    Font_LoadTextPalette(PAL_LOAD_MAIN_BG, PLTT_OFFSET(TEXT_PAL), card->heapID);
    Font_LoadTextPalette(PAL_LOAD_SUB_BG, PLTT_OFFSET(TEXT_PAL), card->heapID);

    // Illustration tilemap: an 8x8 block of consecutive tiles, loaded per state.
    u16 *artMap = Bg_GetTilemapBuffer(card->bgConfig, BG_LAYER_MAIN_1);

    for (int y = 0; y < ART_TILES_PER_SIDE; y++) {
        for (int x = 0; x < ART_TILES_PER_SIDE; x++) {
            artMap[(ART_TILE_TOP + y) * 32 + ART_TILE_LEFT + x] = (ART_PAL << 12) | (ART_FIRST_TILE + y * ART_TILES_PER_SIDE + x);
        }
    }

    Bg_CopyTilemapBufferToVRAM(card->bgConfig, BG_LAYER_MAIN_1);

    // The scroll arrow is drawn into the cells right of the body window and keeps the
    // palette already in the tilemap, so pre-set it to the message-frame palette.
    Bg_ChangeTilemapRectPalette(card->bgConfig, BG_LAYER_MAIN_0, BODY_WINDOW_LEFT + BODY_WINDOW_WIDTH + 1, BODY_WINDOW_TOP + 2, 2, 2, MESSAGE_FRAME_PAL);
}

static void StillCard_DrawCentered(StillCard *card, Window *window, u32 y, u32 msgBank, u32 msgID)
{
    MessageLoader *loader = (msgBank == TEXT_BANK_MENU_ENTRIES) ? card->menuLoader : card->cardLoader;

    MessageLoader_GetString(loader, msgID, card->string);

    u32 width = Font_CalcStringWidth(FONT_SYSTEM, card->string, 0);
    u32 x = (Window_GetWidth(window) * 8 - width) / 2;

    Text_AddPrinterWithParamsAndColor(window, FONT_SYSTEM, card->string, x, y, TEXT_SPEED_INSTANT, TEXT_COLOR(1, 2, 0), NULL);
    Window_ScheduleCopyToVRAM(window);
}

static void StillCard_DrawPanelLabels(StillCard *card)
{
    const StillCardDesc *desc = card->desc;

    for (int i = 0; i <= desc->numStates; i++) {
        u32 msgID = (i < desc->numStates) ? desc->states[i].headlineMsg : desc->exitMsg;

        MessageLoader_GetString(card->menuLoader, msgID, card->string);

        u32 width = Font_CalcStringWidth(FONT_SYSTEM, card->string, 0);
        u32 x = (PANEL_WINDOW_WIDTH * 8 - width) / 2;
        u32 y = (PANEL_BUTTON_TOP_PX + i * PANEL_BUTTON_STEP - PANEL_WINDOW_TOP * 8) + 4;

        Text_AddPrinterWithParamsAndColor(&card->panelWindow, FONT_SYSTEM, card->string, x, y, TEXT_SPEED_INSTANT, TEXT_COLOR(1, 2, 0), NULL);
    }

    Window_ScheduleCopyToVRAM(&card->panelWindow);
}

static void StillCard_CancelPrinter(StillCard *card)
{
    if (card->printerActive && Text_IsPrinterActive(card->printerID)) {
        Text_RemovePrinter(card->printerID);
    }

    card->printerActive = FALSE;
}

static void StillCard_ShowState(StillCard *card, u8 index)
{
    const StillCardDesc *desc = card->desc;
    const StillCardStateDesc *state = &desc->states[index];

    StillCard_CancelPrinter(card);
    card->current = index;

    // Illustration: item-icon-derived tiles + palette.
    Graphics_LoadTilesToBgLayer(NARC_INDEX_GRAPHIC__STILL_CARD, state->artNcgr, card->bgConfig, BG_LAYER_MAIN_1, 0, 0, FALSE, card->heapID);
    Graphics_LoadPalette(NARC_INDEX_GRAPHIC__STILL_CARD, state->artNclr, PAL_LOAD_MAIN_BG, PLTT_OFFSET(ART_PAL), PALETTE_SIZE_BYTES, card->heapID);

    // Active tab highlight on the touch panel.
    for (int i = 0; i <= desc->numStates; i++) {
        u8 pal = (i == index) ? PANEL_ACTIVE_PAL : 0;

        Bg_ChangeTilemapRectPalette(card->bgConfig, BG_LAYER_SUB_3, PANEL_BUTTON_LEFT_PX / 8, (PANEL_BUTTON_TOP_PX + i * PANEL_BUTTON_STEP) / 8, (PANEL_BUTTON_RIGHT_PX + 1 - PANEL_BUTTON_LEFT_PX) / 8, PANEL_BUTTON_H_PX / 8, pal);
    }

    Bg_CopyTilemapBufferToVRAM(card->bgConfig, BG_LAYER_SUB_3);

    // Headline (row 5 of the head window) - clear that strip then redraw.
    Window_FillRectWithColor(&card->headWindow, 0, 0, 40, HEAD_WINDOW_WIDTH * 8, 16);
    StillCard_DrawCentered(card, &card->headWindow, 40, TEXT_BANK_MENU_ENTRIES, state->headlineMsg);

    // Article body via the native printer; existing \r / \f breaks page on A.
    Window_FillTilemap(&card->bodyWindow, 0);
    MessageLoader_GetString(card->cardLoader, state->articleMsg, card->string);
    card->printerID = Text_AddPrinterWithParamsAndColor(&card->bodyWindow, FONT_MESSAGE, card->string, 0, 0, card->textFrameDelay, TEXT_COLOR(1, 2, 0), NULL);
    card->printerActive = TRUE;
    Window_PutToTilemap(&card->headWindow);
    Window_PutToTilemap(&card->bodyWindow);
    Window_PutToTilemap(&card->panelWindow);
    Bg_CopyTilemapBufferToVRAM(card->bgConfig, BG_LAYER_MAIN_0);
    Bg_CopyTilemapBufferToVRAM(card->bgConfig, BG_LAYER_SUB_0);
    Window_CopyToVRAM(&card->headWindow);
    Window_CopyToVRAM(&card->bodyWindow);
    Window_CopyToVRAM(&card->panelWindow);
}
