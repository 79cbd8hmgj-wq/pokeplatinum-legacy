#ifndef POKEPLATINUM_OPAL_DATA_H
#define POKEPLATINUM_OPAL_DATA_H

#include "constants/heap.h"

#include "string_gf.h"

// Gameplay-reference pages added by the Pokemon Opal Pokedex overhaul.
// Every value shown is read at runtime from the compiled gameplay tables
// (personal, evolution, level-up, TM/HM masks, move table, text banks) plus the
// generated opal_locations table - nothing is copied per species.
enum OpalPage {
    OPAL_PAGE_OVERVIEW = 0,
    OPAL_PAGE_ABILITIES,
    OPAL_PAGE_EVOLUTION,
    OPAL_PAGE_LEARNSET,
    OPAL_PAGE_TMHM,
    OPAL_PAGE_STATS,
    OPAL_PAGE_LOCATIONS,
    OPAL_PAGE_FORMS,
    OPAL_PAGE_MAX
};

// Palette index (within the BG palette bank used by the text window) a cell is drawn with.
enum OpalColor {
    OPAL_COLOR_TEXT = 0,
    OPAL_COLOR_ACCENT,
    OPAL_COLOR_GOLD,
    OPAL_COLOR_DIM,
    OPAL_COLOR_HEADER,
    OPAL_COLOR_GOOD,
    OPAL_COLOR_BAD,
};

#define OPAL_ROW_MAX_CELLS 6
#define OPAL_MAX_ROWS      128
#define OPAL_BAR_NONE      (-1)

typedef struct OpalCell {
    u8 x;
    u8 color;
    String *text;
} OpalCell;

typedef struct OpalRow {
    u8 numCells;
    u8 lines; // text lines the row occupies (each line is OPAL_LINE_HEIGHT pixels)
    s16 barValue; // base stat value for a stat bar, or OPAL_BAR_NONE
    OpalCell cells[OPAL_ROW_MAX_CELLS];
} OpalRow;

typedef struct OpalPageData {
    enum HeapID heapID;
    u16 numRows;
    u16 totalLines;
    BOOL locked; // page content withheld by seen/caught gating
    OpalRow rows[OPAL_MAX_ROWS];
} OpalPageData;

#define OPAL_LINE_HEIGHT 16

// Builds the rows of one page for a species. `locationTable` is the generated
// opal_locations member of zukan.narc (may be NULL: locations are then omitted). `caught` selects the full
// mechanics reference; seen-only entries get only the pages the vanilla Pokedex
// already exposes (overview name/number and the wild locations).
OpalPageData *OpalData_BuildPage(enum OpalPage page, u16 species, BOOL seen, BOOL caught, const u8 *locationTable, enum HeapID heapID);
void OpalData_FreePage(OpalPageData *pageData);

// Number of distinct personal-data forms for the species (1 if it has none).
u8 OpalData_NumDataForms(u16 species);

// Whether the page needs a caught species (everything except Overview/Locations).
BOOL OpalData_PageRequiresCaught(enum OpalPage page);

#endif // POKEPLATINUM_OPAL_DATA_H
