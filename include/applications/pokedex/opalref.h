#ifndef POKEPLATINUM_OPALREF_H
#define POKEPLATINUM_OPALREF_H

#include "applications/pokedex/infomain.h"
#include "applications/pokedex/opal_data.h"
#include "applications/pokedex/pokedex_app.h"
#include "applications/pokedex/pokedex_graphics.h"
#include "applications/pokedex/pokedex_sort_data.h"
#include "applications/pokedex/struct_ov21_021E68F4.h"

#include "heap.h"

// Opal gameplay-reference screen pair.
//   main LCD: header + scrolling data panel for the selected page
//   sub LCD : page tabs, species/scroll buttons and back button
// Both halves share one OpalRefState (the main half owns the allocation).

// Main LCD layout (pixels). Shared with tools/opal_pokedex/build_opal_ref_assets.py,
// which validate_opal_ref_assets.py cross-checks.
#define OPALREF_VIEW_TOP   30
#define OPALREF_VIEW_LINES 9

// Sub LCD layout (pixels; all tile aligned).
#define OPALREF_TAB_COLS      4
#define OPALREF_TAB_ROWS      2
#define OPALREF_TAB_X0        16
#define OPALREF_TAB_W         56
#define OPALREF_TAB_H         24
#define OPALREF_TAB_Y0        40
#define OPALREF_TAB_ROW_PITCH 32
#define OPALREF_BTN_Y         112
#define OPALREF_BTN_W         56
#define OPALREF_BTN_H         24
#define OPALREF_BACK_X        72
#define OPALREF_BACK_Y        144
#define OPALREF_BACK_W        112
#define OPALREF_BACK_H        24

typedef struct OpalRefState {
    PokedexApp *pokedexApp;
    PokedexSortData *sortData;
    PokedexGraphicData *graphicData;
    InfoMainState *infoState;
    u8 *locationTable;
    OpalPageData *pageData;
    int page; // enum OpalPage
    int scroll; // first visible row
    int maxScroll;
    BOOL dirty; // page content must be rebuilt (page, species or form changed)
    u32 renderVersion; // incremented whenever pageData is replaced
    u16 species; // species the current pageData was built for
    BOOL caught;
    BOOL seen;
} OpalRefState;

void OpalRef_InitScreen(PokedexScreenManager *screenManager, PokedexApp *pokedexApp, enum HeapID heapID);
void OpalRef_FreeScreen(PokedexScreenManager *screenManager);
void OpalRefSub_InitScreen(PokedexScreenManager *screenManager, PokedexApp *pokedexApp, enum HeapID heapID);
void OpalRefSub_FreeScreen(PokedexScreenManager *screenManager);

u32 OpalRef_PageTitleMessage(enum OpalPage page);
u32 OpalRef_PageTabMessage(enum OpalPage page);
void OpalRef_SetPage(OpalRefState *state, enum OpalPage page);
BOOL OpalRef_StepSpecies(OpalRefState *state, int step);
BOOL OpalRef_Scroll(OpalRefState *state, int delta);

#endif // POKEPLATINUM_OPALREF_H
