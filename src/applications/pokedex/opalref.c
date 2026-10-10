#include "applications/pokedex/opalref.h"

#include <nitro.h>
#include <string.h>

#include "constants/narc.h"

#include "applications/pokedex/opal_data.h"
#include "applications/pokedex/pokedex_data_manager.h"
#include "applications/pokedex/pokedex_graphics.h"
#include "applications/pokedex/pokedex_graphics_manager.h"
#include "applications/pokedex/pokedex_main.h"
#include "applications/pokedex/pokedex_sort.h"
#include "applications/pokedex/species_caught_status.h"

#include "bg_window.h"
#include "font.h"
#include "graphics.h"
#include "heap.h"
#include "message.h"
#include "message_util.h"
#include "narc.h"
#include "pokemon_sprite.h"
#include "string_gf.h"
#include "text.h"

#include "res/graphics/pokedex/zukan.naix"
#include "res/text/bank/pokedex.h"

#define OPALREF_PALETTE_BYTES (4 * 32)
#define OPALREF_SPRITE_X      208
#define OPALREF_SPRITE_Y      80

// Bank-0 palette indices of the text window (see tools/opal_pokedex/build_opal_ref_assets.py).
#define OPALREF_PAL_TRACK    14
#define OPALREF_PAL_BAR_LOW  10
#define OPALREF_PAL_BAR_MID  11
#define OPALREF_PAL_BAR_HIGH 12
#define OPALREF_PAL_BAR_MAX  13
#define OPALREF_BAR_X        96
#define OPALREF_BAR_WIDTH    144
#define OPALREF_BAR_HEIGHT   8

typedef struct OpalRefGraphics {
    u16 savedPalette[OPALREF_PALETTE_BYTES / 2]; // BG palette banks 0-3 as they were before this screen
    u32 renderedVersion;
    int renderedScroll;
    BOOL spriteShown;
} OpalRefGraphics;

static const u32 sTextColors[] = {
    TEXT_COLOR(1, 2, 0), // OPAL_COLOR_TEXT
    TEXT_COLOR(3, 2, 0), // OPAL_COLOR_ACCENT
    TEXT_COLOR(4, 2, 0), // OPAL_COLOR_GOLD
    TEXT_COLOR(5, 2, 0), // OPAL_COLOR_DIM
    TEXT_COLOR(8, 9, 0), // OPAL_COLOR_HEADER
    TEXT_COLOR(6, 2, 0), // OPAL_COLOR_GOOD
    TEXT_COLOR(7, 2, 0), // OPAL_COLOR_BAD
};

static const u16 sPageTitles[OPAL_PAGE_MAX] = {
    pl_msg_pokedex_opal_title_overview,
    pl_msg_pokedex_opal_title_abilities,
    pl_msg_pokedex_opal_title_evolution,
    pl_msg_pokedex_opal_title_learnset,
    pl_msg_pokedex_opal_title_tmhm,
    pl_msg_pokedex_opal_title_stats,
    pl_msg_pokedex_opal_title_locations,
    pl_msg_pokedex_opal_title_forms,
};

static const u16 sPageTabs[OPAL_PAGE_MAX] = {
    pl_msg_pokedex_opal_tab_overview,
    pl_msg_pokedex_opal_tab_abilities,
    pl_msg_pokedex_opal_tab_evolution,
    pl_msg_pokedex_opal_tab_learnset,
    pl_msg_pokedex_opal_tab_tmhm,
    pl_msg_pokedex_opal_tab_stats,
    pl_msg_pokedex_opal_tab_locations,
    pl_msg_pokedex_opal_tab_forms,
};

static OpalRefState *AllocateState(enum HeapID heapID, PokedexApp *pokedexApp);
static PokedexGraphicData **AllocateGraphicsData(enum HeapID heapID, PokedexApp *pokedexApp);
static int GetNumScreenStates(void);
static int InitData(PokedexDataManager *dataMan, void *data);
static int UpdateData(PokedexDataManager *dataMan, void *data);
static int FinalizeData(PokedexDataManager *dataMan, void *data);
static int InitGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan);
static int UpdateGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan);
static int FinalizeGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan);
static void RebuildPage(OpalRefState *state, enum HeapID heapID);
static void LoadBackground(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData, enum HeapID heapID);
static void RenderPage(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData, const OpalRefState *state, enum HeapID heapID);
static void RenderHeader(Window *window, const OpalRefState *state, enum HeapID heapID);
static void RenderRows(Window *window, const OpalRefState *state);
static void RenderBar(Window *window, int value, int y);
static void UpdateSprite(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData, const OpalRefState *state);
static void HideSprite(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData);

u32 OpalRef_PageTitleMessage(enum OpalPage page)
{
    return sPageTitles[page];
}

u32 OpalRef_PageTabMessage(enum OpalPage page)
{
    return sPageTabs[page];
}

void OpalRef_SetPage(OpalRefState *state, enum OpalPage page)
{
    if (state->page != page) {
        state->page = page;
        state->scroll = 0;
        state->dirty = TRUE;
    }
}

BOOL OpalRef_StepSpecies(OpalRefState *state, int step)
{
    if (PokedexSort_TakeStep_Loop(state->sortData, step)) {
        state->scroll = 0;
        state->dirty = TRUE;
        return TRUE;
    }

    return FALSE;
}

BOOL OpalRef_Scroll(OpalRefState *state, int delta)
{
    int scroll = state->scroll + delta;

    if (scroll < 0) {
        scroll = 0;
    }

    if (scroll > state->maxScroll) {
        scroll = state->maxScroll;
    }

    if (scroll != state->scroll) {
        state->scroll = scroll;
        return TRUE;
    }

    return FALSE;
}

void OpalRef_InitScreen(PokedexScreenManager *screenManager, PokedexApp *pokedexApp, enum HeapID heapID)
{
    OpalRefState *state = AllocateState(heapID, pokedexApp);
    PokedexGraphicData **graphicsData = AllocateGraphicsData(heapID, pokedexApp);

    screenManager->pageData = state;
    screenManager->pageGraphics = graphicsData;
    screenManager->screenStates = NULL;
    screenManager->numStates = GetNumScreenStates();
    screenManager->dataFunc[0] = InitData;
    screenManager->dataFunc[1] = UpdateData;
    screenManager->dataFunc[2] = FinalizeData;
    screenManager->graphicsFunc[0] = InitGraphics;
    screenManager->graphicsFunc[1] = UpdateGraphics;
    screenManager->graphicsFunc[2] = FinalizeGraphics;
}

void OpalRef_FreeScreen(PokedexScreenManager *screenManager)
{
    OpalRefState *state = screenManager->pageData;

    GF_ASSERT(state);
    GF_ASSERT(screenManager->pageGraphics);

    OpalData_FreePage(state->pageData);
    Heap_Free(state);
    Heap_Free(screenManager->pageGraphics);
}

static OpalRefState *AllocateState(enum HeapID heapID, PokedexApp *pokedexApp)
{
    OpalRefState *state = Heap_Alloc(heapID, sizeof(OpalRefState));

    GF_ASSERT(state);
    memset(state, 0, sizeof(OpalRefState));

    state->pokedexApp = pokedexApp;
    state->sortData = PokedexMain_GetSortData(pokedexApp);
    state->graphicData = PokedexMain_GetGraphicData(pokedexApp);
    state->infoState = ov21_021D1410(pokedexApp, 2)->pageData;
    state->page = OPAL_PAGE_OVERVIEW;

    return state;
}

static PokedexGraphicData **AllocateGraphicsData(enum HeapID heapID, PokedexApp *pokedexApp)
{
    PokedexGraphicData **graphicsData = Heap_Alloc(heapID, sizeof(PokedexGraphicData *));

    GF_ASSERT(graphicsData);
    memset(graphicsData, 0, sizeof(PokedexGraphicData *));

    *graphicsData = PokedexMain_GetGraphicData(pokedexApp);

    return graphicsData;
}

static int GetNumScreenStates(void)
{
    return 0;
}

static int InitData(PokedexDataManager *dataMan, void *data)
{
    OpalRefState *state = data;

    // The generated location table lives in zukan.narc next to the other Pokedex resources.
    state->locationTable = NARC_AllocAndReadWholeMember(PokedexGraphics_GetNARC(state->graphicData), opal_locations_bin, dataMan->heapID);
    state->scroll = 0;
    state->dirty = TRUE;
    RebuildPage(state, dataMan->heapID);

    return TRUE;
}

static int UpdateData(PokedexDataManager *dataMan, void *data)
{
    OpalRefState *state = data;

    if (dataMan->exit == TRUE) {
        return TRUE;
    }

    if (dataMan->unchanged == TRUE) {
        return FALSE;
    }

    if (state->dirty) {
        RebuildPage(state, dataMan->heapID);
    }

    return FALSE;
}

static int FinalizeData(PokedexDataManager *dataMan, void *data)
{
    OpalRefState *state = data;

    OpalData_FreePage(state->pageData);
    state->pageData = NULL;

    if (state->locationTable != NULL) {
        Heap_Free(state->locationTable);
        state->locationTable = NULL;
    }

    return TRUE;
}

static void RebuildPage(OpalRefState *state, enum HeapID heapID)
{
    int status = PokedexSort_CurrentCaughtStatus(state->sortData);
    u16 species = PokedexSort_CurrentSpecies(state->sortData);
    int lines = 0;
    int row;

    OpalData_FreePage(state->pageData);

    state->seen = status >= CS_ENCOUNTERED;
    state->caught = status == CS_CAUGHT;
    state->species = species;
    state->pageData = OpalData_BuildPage(state->page, species, state->seen, state->caught, state->locationTable, heapID);

    // The last scroll position leaves the final OPALREF_VIEW_LINES lines visible.
    state->maxScroll = 0;

    for (row = state->pageData->numRows - 1; row >= 0; row--) {
        lines += state->pageData->rows[row].lines;

        if (lines > OPALREF_VIEW_LINES) {
            state->maxScroll = row + 1;
            break;
        }
    }

    if (state->scroll > state->maxScroll) {
        state->scroll = state->maxScroll;
    }

    state->dirty = FALSE;
    state->renderVersion++;
}

static int InitGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan)
{
    const OpalRefState *state = data;
    PokedexGraphicData **graphicsData = graphics;
    OpalRefGraphics *opalGraphics = graphicsMan->pageGraphics;

    switch (graphicsMan->state) {
    case 0:
        graphicsMan->pageGraphics = Heap_Alloc(graphicsMan->heapID, sizeof(OpalRefGraphics));
        memset(graphicsMan->pageGraphics, 0, sizeof(OpalRefGraphics));
        graphicsMan->state++;
        break;
    case 1:
        LoadBackground(opalGraphics, *graphicsData, graphicsMan->heapID);
        RenderPage(opalGraphics, *graphicsData, state, graphicsMan->heapID);
        PokedexGraphics_InitBlendTransition(&(*graphicsData)->blendMain, 4, -16, 0, 0, 16, (GX_BLEND_PLANEMASK_BG0 | GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), (GX_BLEND_PLANEMASK_BG0 | GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), 0);
        graphicsMan->state++;
        break;
    case 2:
        if (PokedexGraphics_TakeBlendTransitionStep(&(*graphicsData)->blendMain)) {
            graphicsMan->state++;
        }
        break;
    case 3:
        G2_BlendNone();
        UpdateSprite(opalGraphics, *graphicsData, state);
        return TRUE;
    default:
        break;
    }

    return FALSE;
}

static int UpdateGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan)
{
    const OpalRefState *state = data;
    PokedexGraphicData **graphicsData = graphics;
    OpalRefGraphics *opalGraphics = graphicsMan->pageGraphics;

    if (opalGraphics->renderedVersion != state->renderVersion || opalGraphics->renderedScroll != state->scroll) {
        RenderPage(opalGraphics, *graphicsData, state, graphicsMan->heapID);
        UpdateSprite(opalGraphics, *graphicsData, state);
    }

    return FALSE;
}

static int FinalizeGraphics(void *graphics, PokedexGraphicsManager *graphicsMan, const void *data, const PokedexDataManager *dataMan)
{
    PokedexGraphicData **graphicsData = graphics;
    OpalRefGraphics *opalGraphics = graphicsMan->pageGraphics;

    switch (graphicsMan->state) {
    case 0:
        HideSprite(opalGraphics, *graphicsData);
        PokedexGraphics_InitBlendTransition(&(*graphicsData)->blendMain, 4, 0, -16, 16, 0, (GX_BLEND_PLANEMASK_BG0 | GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), (GX_BLEND_PLANEMASK_BG0 | GX_BLEND_PLANEMASK_BG1 | GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3 | GX_BLEND_PLANEMASK_BD), 0);
        graphicsMan->state++;
        break;
    case 1:
        if (PokedexGraphics_TakeBlendTransitionStep(&(*graphicsData)->blendMain)) {
            graphicsMan->state++;
        }
        break;
    case 2:
        Window_FillTilemap(&(*graphicsData)->window, 0);
        Window_CopyToVRAM(&(*graphicsData)->window);
        Bg_ClearTilemap((*graphicsData)->bgConfig, BG_LAYER_MAIN_3);
        GX_LoadBGPltt(opalGraphics->savedPalette, 0, OPALREF_PALETTE_BYTES);
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

static void LoadBackground(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData, enum HeapID heapID)
{
    void *tilemapData;
    NNSG2dScreenData *screenData;

    // The Info/tab screens rely on the palette banks this screen overwrites: keep a copy and
    // restore it when leaving (the screen is faded out by then).
    MI_CpuCopy16((void *)HW_BG_PLTT, opalGraphics->savedPalette, OPALREF_PALETTE_BYTES);

    // 4 palette banks: 0 = text/bars, 1 = art, 2/3 = art variants (unused on this LCD).
    PokedexGraphics_LoadGraphicNarcPaletteData(graphicData, opal_ref_NCLR, PAL_LOAD_MAIN_BG, 0, OPALREF_PALETTE_BYTES, heapID);
    PokedexGraphics_LoadGraphicNarcCharacterData(graphicData, opal_ref_main_NCGR_lz, graphicData->bgConfig, BG_LAYER_MAIN_3, 0, 0, TRUE, heapID);

    tilemapData = PokedexGraphics_GetGraphicNarcTilemapData(graphicData, opal_ref_main_NSCR_lz, TRUE, &screenData, heapID);
    Bg_LoadToTilemapRect(graphicData->bgConfig, BG_LAYER_MAIN_3, screenData->rawData, 0, 0, screenData->screenWidth / 8, screenData->screenHeight / 8);
    Heap_Free(tilemapData);
    Bg_ScheduleTilemapTransfer(graphicData->bgConfig, BG_LAYER_MAIN_3);
}

static void RenderPage(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData, const OpalRefState *state, enum HeapID heapID)
{
    Window *window = &graphicData->window;

    Window_FillTilemap(window, 0);
    RenderHeader(window, state, heapID);
    RenderRows(window, state);
    Window_CopyToVRAM(window);

    opalGraphics->renderedVersion = state->renderVersion;
    opalGraphics->renderedScroll = state->scroll;
}

static void RenderHeader(Window *window, const OpalRefState *state, enum HeapID heapID)
{
    MessageLoader *loader = MessageLoader_Init(MSG_LOADER_PRELOAD_ENTIRE_BANK, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_POKEDEX, heapID);
    String *title = MessageLoader_GetNewString(loader, sPageTitles[state->page]);
    String *name;
    u32 width;

    Text_AddPrinterWithParamsAndColor(window, FONT_SYSTEM, title, 28, 4, TEXT_SPEED_INSTANT, sTextColors[OPAL_COLOR_HEADER], NULL);
    String_Free(title);

    if (state->seen) {
        name = MessageUtil_SpeciesName(state->species, heapID);
    } else {
        name = MessageLoader_GetNewString(loader, pl_msg_pokedex_opal_unknown);
    }

    width = Font_CalcMaxLineWidth(FONT_SYSTEM, name, 0);
    Text_AddPrinterWithParamsAndColor(window, FONT_SYSTEM, name, 248 - width, 4, TEXT_SPEED_INSTANT, sTextColors[OPAL_COLOR_HEADER], NULL);
    String_Free(name);

    if (state->scroll > 0) {
        String *arrow = MessageLoader_GetNewString(loader, pl_msg_pokedex_opal_arrow_up);
        Text_AddPrinterWithParamsAndColor(window, FONT_SYSTEM, arrow, 240, OPALREF_VIEW_TOP - 4, TEXT_SPEED_INSTANT, sTextColors[OPAL_COLOR_ACCENT], NULL);
        String_Free(arrow);
    }

    if (state->scroll < state->maxScroll) {
        String *arrow = MessageLoader_GetNewString(loader, pl_msg_pokedex_opal_arrow_down);
        Text_AddPrinterWithParamsAndColor(window, FONT_SYSTEM, arrow, 240, OPALREF_VIEW_TOP + (OPALREF_VIEW_LINES - 1) * OPAL_LINE_HEIGHT + 2, TEXT_SPEED_INSTANT, sTextColors[OPAL_COLOR_ACCENT], NULL);
        String_Free(arrow);
    }

    MessageLoader_Free(loader);
}

static void RenderRows(Window *window, const OpalRefState *state)
{
    const OpalPageData *page = state->pageData;
    int row, cell;
    int line = 0;
    int y = OPALREF_VIEW_TOP;

    for (row = state->scroll; row < page->numRows; row++) {
        const OpalRow *opalRow = &page->rows[row];

        if (line + opalRow->lines > OPALREF_VIEW_LINES) {
            break;
        }

        if (opalRow->barValue != OPAL_BAR_NONE) {
            RenderBar(window, opalRow->barValue, y);
        }

        for (cell = 0; cell < opalRow->numCells; cell++) {
            const OpalCell *opalCell = &opalRow->cells[cell];

            Text_AddPrinterWithParamsAndColor(window, FONT_SYSTEM, opalCell->text, opalCell->x, y, TEXT_SPEED_INSTANT, sTextColors[opalCell->color], NULL);
        }

        y += opalRow->lines * OPAL_LINE_HEIGHT;
        line += opalRow->lines;
    }
}

static void RenderBar(Window *window, int value, int y)
{
    int width = (value * OPALREF_BAR_WIDTH) / 255;
    int color;

    if (value < 60) {
        color = OPALREF_PAL_BAR_LOW;
    } else if (value < 100) {
        color = OPALREF_PAL_BAR_MID;
    } else if (value < 140) {
        color = OPALREF_PAL_BAR_HIGH;
    } else {
        color = OPALREF_PAL_BAR_MAX;
    }

    if (width < 1) {
        width = 1;
    }

    Window_FillRectWithColor(window, OPALREF_PAL_TRACK, OPALREF_BAR_X, y + 4, OPALREF_BAR_WIDTH, OPALREF_BAR_HEIGHT);
    Window_FillRectWithColor(window, color, OPALREF_BAR_X, y + 4, width, OPALREF_BAR_HEIGHT);
}

static void UpdateSprite(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData, const OpalRefState *state)
{
    if (state->page == OPAL_PAGE_OVERVIEW && state->seen) {
        PokedexSortData *sortData = state->sortData;
        PokemonSprite *sprite;

        PokedexMain_DisplayPokemonSprite(graphicData, sortData, state->species, 2, OPALREF_SPRITE_X, OPALREF_SPRITE_Y);
        sprite = PokemonGraphics_GetPokemonChar(graphicData);
        PokemonSprite_SetAttribute(sprite, MON_SPRITE_HIDE, FALSE);
        opalGraphics->spriteShown = TRUE;
    } else {
        HideSprite(opalGraphics, graphicData);
    }
}

static void HideSprite(OpalRefGraphics *opalGraphics, PokedexGraphicData *graphicData)
{
    if (opalGraphics->spriteShown) {
        PokemonSprite *sprite = PokemonGraphics_GetPokemonChar(graphicData);

        PokemonSprite_SetAttribute(sprite, MON_SPRITE_HIDE, TRUE);
        PokemonSprite_ClearFade(sprite);
        opalGraphics->spriteShown = FALSE;
    }
}
