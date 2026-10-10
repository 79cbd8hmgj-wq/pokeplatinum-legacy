#include "applications/pokedex/opal_data.h"

#include <nitro.h>
#include <string.h>

#include "constants/charcode.h"
#include "constants/forms.h"
#include "constants/heap.h"
#include "constants/narc.h"
#include "constants/species.h"
#include "constants/string.h"
#include "generated/abilities.h"
#include "generated/evolution_methods.h"
#include "generated/items.h"
#include "generated/move_attributes.h"
#include "generated/move_classes.h"
#include "generated/species_data_params.h"
#include "generated/text_banks.h"

#include "struct_defs/species.h"

#include "font.h"
#include "heap.h"
#include "item.h"
#include "message.h"
#include "message_util.h"
#include "move_table.h"
#include "narc.h"
#include "pokemon.h"
#include "string_gf.h"
#include "string_template.h"

#include "res/text/bank/pokedex.h"

#define OPAL_NATIONAL_MAX 493
#define OPAL_NUM_MACHINES 100 // TM01-TM92, HM01-HM08
#define OPAL_FIRST_HM     92
#define OPAL_TEXT_X       8
#define OPAL_SCREEN_RIGHT 248

// Generated location table layout (tools/opal_pokedex/build_gameplay_data.py)
enum OpalLocationKind {
    OPAL_LOC_LAND = 0,
    OPAL_LOC_SURF,
    OPAL_LOC_OLD_ROD,
    OPAL_LOC_GOOD_ROD,
    OPAL_LOC_SUPER_ROD,
    OPAL_LOC_RADAR,
    OPAL_LOC_SWARM,
    OPAL_LOC_STATIC,
    OPAL_LOC_GIFT,
    OPAL_LOC_FOSSIL,
    OPAL_LOC_RITUAL,
    OPAL_LOC_ROAMER,
    OPAL_LOC_BREEDING,
    OPAL_LOC_LEGACY,
    OPAL_LOC_EVENT,
    OPAL_LOC_FIXED_TILE,
    OPAL_LOC_EGG,
    OPAL_LOC_KIND_MAX
};

#define OPAL_LOCF_MORNING 0x01
#define OPAL_LOCF_DAY     0x02
#define OPAL_LOCF_NIGHT   0x04
#define OPAL_LOCF_ALLTIME (OPAL_LOCF_MORNING | OPAL_LOCF_DAY | OPAL_LOCF_NIGHT)
#define OPAL_LOCF_HOF     0x08
#define OPAL_LOCF_ONCE    0x10
#define OPAL_LOCF_BADGES  0x20
#define OPAL_LOC_AUX_SPECIES 0x40 // `name` is a species ID (Egg parent)
#define OPAL_LOC_AUX_TEXT    0x80 // `name` indexes the pokedex bank instead of the location names bank
#define OPAL_LOC_NAME_NONE 0xFFFF

typedef struct OpalLocationRecord {
    u8 kind;
    u8 flags;
    u16 name;
    u8 minLevel;
    u8 maxLevel;
    u8 percent;
    u8 aux;
} OpalLocationRecord;

typedef struct BuildContext {
    enum HeapID heapID;
    OpalPageData *page;
    MessageLoader *uiLoader;
    StringTemplate *template;
    const u8 *locationTable;
    u16 species;
} BuildContext;

static const u16 sLocationKindLabel[OPAL_LOC_KIND_MAX] = {
    pl_msg_pokedex_opal_lo_land,
    pl_msg_pokedex_opal_lo_surf,
    pl_msg_pokedex_opal_lo_old_rod,
    pl_msg_pokedex_opal_lo_good_rod,
    pl_msg_pokedex_opal_lo_super_rod,
    pl_msg_pokedex_opal_lo_radar,
    pl_msg_pokedex_opal_lo_swarm,
    pl_msg_pokedex_opal_lo_static,
    pl_msg_pokedex_opal_lo_gift,
    pl_msg_pokedex_opal_lo_fossil,
    pl_msg_pokedex_opal_lo_ritual,
    pl_msg_pokedex_opal_lo_roamer,
    pl_msg_pokedex_opal_lo_breeding,
    pl_msg_pokedex_opal_lo_legacy,
    pl_msg_pokedex_opal_lo_event,
    pl_msg_pokedex_opal_lo_fixed,
    pl_msg_pokedex_opal_lo_egg,
};

static OpalRow *AddRow(BuildContext *ctx, u8 lines);
static void AddCell(OpalRow *row, u8 x, enum OpalColor color, String *text);
static String *UiString(BuildContext *ctx, u32 messageID);
static String *UiExpanded(BuildContext *ctx, u32 messageID);
static void AddLabelRow(BuildContext *ctx, u32 messageID, enum OpalColor color);
static void AddLockedRow(BuildContext *ctx, u32 messageID);
static void BuildOverview(BuildContext *ctx);
static void BuildAbilities(BuildContext *ctx);
static void BuildEvolution(BuildContext *ctx);
static void BuildLearnset(BuildContext *ctx);
static void BuildMachines(BuildContext *ctx);
static void BuildStats(BuildContext *ctx);
static void BuildLocations(BuildContext *ctx);
static void BuildForms(BuildContext *ctx);
static String *NumberString(BuildContext *ctx, int value, u32 digits);
static String *SpeciesNameString(BuildContext *ctx, u16 species);
static String *AbilityNameString(BuildContext *ctx, int ability);
static String *TypeNameString(BuildContext *ctx, int type);
static String *MoveNameString(BuildContext *ctx, int move);
static String *EvolutionMethodString(BuildContext *ctx, const SpeciesEvolution *evolution);
static u16 *LoadPreEvolutions(enum HeapID heapID);
static u16 FindFamilyRoot(const u16 *preEvolutions, u16 species);
static void AddFamilyBranch(BuildContext *ctx, const u16 *preEvolutions, NARC *evolutionNarc, u16 species, int depth);
static u8 SpeciesFormCount(u16 species);
static const OpalLocationRecord *LocationRecords(const u8 *table, u16 species, u8 *count);
static int StatValue(const SpeciesData *data, int param);

u8 OpalData_NumDataForms(u16 species)
{
    switch (species) {
    case SPECIES_DEOXYS:
        return DEOXYS_FORM_COUNT;
    case SPECIES_WORMADAM:
        return WORMADAM_FORM_COUNT;
    case SPECIES_GIRATINA:
        return GIRATINA_FORM_COUNT;
    case SPECIES_SHAYMIN:
        return SHAYMIN_FORM_COUNT;
    case SPECIES_ROTOM:
        return ROTOM_FORM_COUNT;
    }

    return 1;
}

BOOL OpalData_PageRequiresCaught(enum OpalPage page)
{
    return page != OPAL_PAGE_OVERVIEW && page != OPAL_PAGE_LOCATIONS;
}

OpalPageData *OpalData_BuildPage(enum OpalPage page, u16 species, BOOL seen, BOOL caught, const u8 *locationTable, enum HeapID heapID)
{
    BuildContext ctx;
    OpalPageData *pageData = Heap_Alloc(heapID, sizeof(OpalPageData));

    GF_ASSERT(pageData);
    memset(pageData, 0, sizeof(OpalPageData));
    pageData->heapID = heapID;

    ctx.heapID = heapID;
    ctx.page = pageData;
    ctx.uiLoader = MessageLoader_Init(MSG_LOADER_PRELOAD_ENTIRE_BANK, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_POKEDEX, heapID);
    ctx.template = StringTemplate_Default(heapID);
    ctx.locationTable = locationTable;
    ctx.species = species;

    if (species == SPECIES_NONE || species > OPAL_NATIONAL_MAX || !seen) {
        pageData->locked = TRUE;
        AddLockedRow(&ctx, pl_msg_pokedex_opal_locked_unseen);
    } else if (OpalData_PageRequiresCaught(page) && !caught) {
        pageData->locked = TRUE;
        AddLockedRow(&ctx, pl_msg_pokedex_opal_locked_seen);
    } else {
        switch (page) {
        case OPAL_PAGE_OVERVIEW:
            BuildOverview(&ctx);
            if (!caught) {
                AddLockedRow(&ctx, pl_msg_pokedex_opal_locked_seen);
            }
            break;
        case OPAL_PAGE_ABILITIES:
            BuildAbilities(&ctx);
            break;
        case OPAL_PAGE_EVOLUTION:
            BuildEvolution(&ctx);
            break;
        case OPAL_PAGE_LEARNSET:
            BuildLearnset(&ctx);
            break;
        case OPAL_PAGE_TMHM:
            BuildMachines(&ctx);
            break;
        case OPAL_PAGE_STATS:
            BuildStats(&ctx);
            break;
        case OPAL_PAGE_LOCATIONS:
            BuildLocations(&ctx);
            break;
        case OPAL_PAGE_FORMS:
            BuildForms(&ctx);
            break;
        }
    }

    StringTemplate_Free(ctx.template);
    MessageLoader_Free(ctx.uiLoader);

    return pageData;
}

void OpalData_FreePage(OpalPageData *pageData)
{
    int row, cell;

    if (pageData == NULL) {
        return;
    }

    for (row = 0; row < pageData->numRows; row++) {
        for (cell = 0; cell < pageData->rows[row].numCells; cell++) {
            if (pageData->rows[row].cells[cell].text != NULL) {
                String_Free(pageData->rows[row].cells[cell].text);
            }
        }
    }

    Heap_Free(pageData);
}

static OpalRow *AddRow(BuildContext *ctx, u8 lines)
{
    OpalRow *row;

    if (ctx->page->numRows >= OPAL_MAX_ROWS) {
        return NULL;
    }

    row = &ctx->page->rows[ctx->page->numRows];
    ctx->page->numRows++;
    ctx->page->totalLines += lines;
    row->numCells = 0;
    row->lines = lines;
    row->barValue = OPAL_BAR_NONE;

    return row;
}

static void AddCell(OpalRow *row, u8 x, enum OpalColor color, String *text)
{
    if (row == NULL || row->numCells >= OPAL_ROW_MAX_CELLS) {
        String_Free(text);
        return;
    }

    row->cells[row->numCells].x = x;
    row->cells[row->numCells].color = color;
    row->cells[row->numCells].text = text;
    row->numCells++;
}

static String *UiString(BuildContext *ctx, u32 messageID)
{
    return MessageLoader_GetNewString(ctx->uiLoader, messageID);
}

// Expands a pokedex-bank message using the arguments currently set on the template.
static String *UiExpanded(BuildContext *ctx, u32 messageID)
{
    return MessageUtil_ExpandedString(ctx->template, ctx->uiLoader, messageID, ctx->heapID);
}

static String *NumberString(BuildContext *ctx, int value, u32 digits)
{
    String *string = String_Init(8, ctx->heapID);
    String_FormatInt(string, value, digits, PADDING_MODE_NONE, CHARSET_MODE_EN);
    return string;
}

static String *SpeciesNameString(BuildContext *ctx, u16 species)
{
    return MessageUtil_SpeciesName(species, ctx->heapID);
}

static String *MoveNameString(BuildContext *ctx, int move)
{
    return MessageUtil_MoveName(move, ctx->heapID);
}

static String *AbilityNameString(BuildContext *ctx, int ability)
{
    StringTemplate_SetAbilityName(ctx->template, 0, ability);
    return UiExpanded(ctx, pl_msg_pokedex_opal_slot0);
}

static String *TypeNameString(BuildContext *ctx, int type)
{
    StringTemplate_SetPokemonTypeName(ctx->template, 0, type);
    return UiExpanded(ctx, pl_msg_pokedex_opal_slot0);
}

static void AddLabelRow(BuildContext *ctx, u32 messageID, enum OpalColor color)
{
    OpalRow *row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, color, UiString(ctx, messageID));
}

// Locked pages show their (one or two line) message from the top of the panel.
static void AddLockedRow(BuildContext *ctx, u32 messageID)
{
    String *message = UiString(ctx, messageID);
    u32 lines = String_NumLines(message);
    u32 line;
    String *part;

    for (line = 0; line < lines; line++) {
        OpalRow *row = AddRow(ctx, 1);
        part = String_Init(64, ctx->heapID);
        String_CopyLineNum(part, message, line);
        AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, part);
    }

    String_Free(message);
}

static int StatValue(const SpeciesData *data, int param)
{
    return SpeciesData_GetValue((SpeciesData *)data, param);
}

// --------------------------------------------------------------------------
// Overview
// --------------------------------------------------------------------------
static void BuildOverview(BuildContext *ctx)
{
    OpalRow *row;
    SpeciesData *data = SpeciesData_FromMonSpecies(ctx->species, ctx->heapID);
    int type1 = StatValue(data, SPECIES_DATA_TYPE_1);
    int type2 = StatValue(data, SPECIES_DATA_TYPE_2);
    int ability1 = StatValue(data, SPECIES_DATA_ABILITY_1);
    int ability2 = StatValue(data, SPECIES_DATA_ABILITY_2);
    int total = 0;
    int stat;
    String *text;

    for (stat = SPECIES_DATA_BASE_HP; stat <= SPECIES_DATA_BASE_SP_DEF; stat++) {
        total += StatValue(data, stat);
    }

    SpeciesData_Free(data);

    StringTemplate_SetNumber(ctx->template, 0, ctx->species, 3, PADDING_MODE_ZEROES, CHARSET_MODE_EN);
    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_GOLD, UiExpanded(ctx, pl_msg_pokedex_opal_dex_no));
    AddCell(row, 72, OPAL_COLOR_TEXT, SpeciesNameString(ctx, ctx->species));

    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ov_types));
    AddCell(row, 72, OPAL_COLOR_ACCENT, TypeNameString(ctx, type1));

    if (type2 != type1) {
        AddCell(row, 136, OPAL_COLOR_ACCENT, TypeNameString(ctx, type2));
    }

    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ov_ability));
    AddCell(row, 72, OPAL_COLOR_TEXT, AbilityNameString(ctx, ability1));

    row = AddRow(ctx, 1);

    if (ability2 != ABILITY_NONE && ability2 != ability1) {
        AddCell(row, 72, OPAL_COLOR_TEXT, AbilityNameString(ctx, ability2));
    }

    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ov_bst));
    text = NumberString(ctx, total, 3);
    AddCell(row, 136, OPAL_COLOR_GOLD, text);

    if (OpalData_NumDataForms(ctx->species) > 1) {
        StringTemplate_SetNumber(ctx->template, 0, OpalData_NumDataForms(ctx->species), 2, PADDING_MODE_NONE, CHARSET_MODE_EN);
        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_tab_forms));
        AddCell(row, 72, OPAL_COLOR_TEXT, UiExpanded(ctx, pl_msg_pokedex_opal_ov_form_count));
    }

    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ov_hint_pages));
}

// --------------------------------------------------------------------------
// Abilities
// --------------------------------------------------------------------------
static void AddAbilityBlock(BuildContext *ctx, u32 slotLabel, int ability, MessageLoader *descriptions)
{
    OpalRow *row = AddRow(ctx, 1);
    String *description;
    u32 lines, line;

    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, slotLabel));
    AddCell(row, 72, OPAL_COLOR_ACCENT, AbilityNameString(ctx, ability));

    description = MessageLoader_GetNewString(descriptions, ability);
    lines = String_NumLines(description);

    for (line = 0; line < lines; line++) {
        String *part = String_Init(64, ctx->heapID);
        String_CopyLineNum(part, description, line);
        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X + 8, OPAL_COLOR_TEXT, part);
    }

    String_Free(description);
}

static void BuildAbilities(BuildContext *ctx)
{
    SpeciesData *data = SpeciesData_FromMonSpecies(ctx->species, ctx->heapID);
    int ability1 = StatValue(data, SPECIES_DATA_ABILITY_1);
    int ability2 = StatValue(data, SPECIES_DATA_ABILITY_2);
    MessageLoader *descriptions = MessageLoader_Init(MSG_LOADER_PRELOAD_ENTIRE_BANK, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_ABILITY_DESCRIPTIONS, ctx->heapID);
    BOOL hasSecond = ability2 != ABILITY_NONE && ability2 != ability1;

    SpeciesData_Free(data);

    AddAbilityBlock(ctx, hasSecond ? pl_msg_pokedex_opal_ab_slot1 : pl_msg_pokedex_opal_ab_single, ability1, descriptions);

    if (hasSecond) {
        AddAbilityBlock(ctx, pl_msg_pokedex_opal_ab_slot2, ability2, descriptions);
    }

    MessageLoader_Free(descriptions);

    {
        String *note = UiString(ctx, pl_msg_pokedex_opal_ab_note);
        u32 lines = String_NumLines(note);
        u32 line;

        AddRow(ctx, 1);

        for (line = 0; line < lines; line++) {
            String *part = String_Init(64, ctx->heapID);
            String_CopyLineNum(part, note, line);
            AddCell(AddRow(ctx, 1), OPAL_TEXT_X, OPAL_COLOR_DIM, part);
        }

        String_Free(note);
    }
}

// --------------------------------------------------------------------------
// Stats
// --------------------------------------------------------------------------
static void BuildStats(BuildContext *ctx)
{
    static const u16 sStatLabels[] = {
        pl_msg_pokedex_opal_st_hp,
        pl_msg_pokedex_opal_st_atk,
        pl_msg_pokedex_opal_st_def,
        pl_msg_pokedex_opal_st_spa,
        pl_msg_pokedex_opal_st_spd,
        pl_msg_pokedex_opal_st_spe,
    };
    // personal-data parameters in display order (HP, Atk, Def, SpA, SpD, Spe)
    static const u8 sStatParams[] = {
        SPECIES_DATA_BASE_HP,
        SPECIES_DATA_BASE_ATK,
        SPECIES_DATA_BASE_DEF,
        SPECIES_DATA_BASE_SP_ATK,
        SPECIES_DATA_BASE_SP_DEF,
        SPECIES_DATA_BASE_SPEED,
    };
    SpeciesData *data = SpeciesData_FromMonSpecies(ctx->species, ctx->heapID);
    OpalRow *row;
    int i, value, total = 0;

    AddLabelRow(ctx, pl_msg_pokedex_opal_st_note, OPAL_COLOR_DIM);

    for (i = 0; i < 6; i++) {
        value = StatValue(data, sStatParams[i]);
        total += value;
        row = AddRow(ctx, 1);

        if (row != NULL) {
            row->barValue = value;
        }

        AddCell(row, OPAL_TEXT_X, OPAL_COLOR_TEXT, UiString(ctx, sStatLabels[i]));
        AddCell(row, 64, value >= 100 ? OPAL_COLOR_GOLD : OPAL_COLOR_ACCENT, NumberString(ctx, value, 3));
    }

    SpeciesData_Free(data);

    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_st_total));
    AddCell(row, 64, OPAL_COLOR_GOLD, NumberString(ctx, total, 3));
}

// --------------------------------------------------------------------------
// Evolution
// --------------------------------------------------------------------------
static String *EvolutionMethodString(BuildContext *ctx, const SpeciesEvolution *evolution)
{
    u32 messageID = pl_msg_pokedex_opal_ev_m_special;
    BOOL numberParam = FALSE;
    BOOL itemParam = FALSE;

    switch (evolution->method) {
    case EVO_LEVEL_HAPPINESS:
        messageID = pl_msg_pokedex_opal_ev_m_happy;
        break;
    case EVO_LEVEL_HAPPINESS_DAY:
        messageID = pl_msg_pokedex_opal_ev_m_happy_day;
        break;
    case EVO_LEVEL_HAPPINESS_NIGHT:
        messageID = pl_msg_pokedex_opal_ev_m_happy_night;
        break;
    case EVO_LEVEL:
        messageID = pl_msg_pokedex_opal_ev_m_level;
        numberParam = TRUE;
        break;
    case EVO_USE_ITEM:
        messageID = pl_msg_pokedex_opal_ev_m_item;
        itemParam = TRUE;
        break;
    case EVO_LEVEL_ATK_GT_DEF:
        messageID = pl_msg_pokedex_opal_ev_m_atk_gt_def;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_ATK_EQ_DEF:
        messageID = pl_msg_pokedex_opal_ev_m_atk_eq_def;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_ATK_LT_DEF:
        messageID = pl_msg_pokedex_opal_ev_m_atk_lt_def;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_PID_LOW:
        messageID = pl_msg_pokedex_opal_ev_m_pid_low;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_PID_HIGH:
        messageID = pl_msg_pokedex_opal_ev_m_pid_high;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_NINJASK:
        messageID = pl_msg_pokedex_opal_ev_m_ninjask;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_SHEDINJA:
        messageID = pl_msg_pokedex_opal_ev_m_shedinja;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_BEAUTY:
        messageID = pl_msg_pokedex_opal_ev_m_beauty;
        numberParam = TRUE;
        break;
    case EVO_USE_ITEM_MALE:
        messageID = pl_msg_pokedex_opal_ev_m_item_male;
        itemParam = TRUE;
        break;
    case EVO_USE_ITEM_FEMALE:
        messageID = pl_msg_pokedex_opal_ev_m_item_female;
        itemParam = TRUE;
        break;
    case EVO_LEVEL_WITH_HELD_ITEM_DAY:
        messageID = pl_msg_pokedex_opal_ev_m_held_day;
        itemParam = TRUE;
        break;
    case EVO_LEVEL_WITH_HELD_ITEM_NIGHT:
        messageID = pl_msg_pokedex_opal_ev_m_held_night;
        itemParam = TRUE;
        break;
    case EVO_LEVEL_KNOW_MOVE:
        messageID = pl_msg_pokedex_opal_ev_m_know_move;
        StringTemplate_SetMoveName(ctx->template, 0, evolution->param);
        return UiExpanded(ctx, messageID);
    case EVO_LEVEL_SPECIES_IN_PARTY: {
        String *speciesName = SpeciesNameString(ctx, evolution->param);
        StringTemplate_SetString(ctx->template, 0, speciesName, 0, 0, 0);
        String_Free(speciesName);
        return UiExpanded(ctx, pl_msg_pokedex_opal_ev_m_party);
    }
    case EVO_LEVEL_MALE:
        messageID = pl_msg_pokedex_opal_ev_m_level_male;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_FEMALE:
        messageID = pl_msg_pokedex_opal_ev_m_level_female;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_MAGNETIC_FIELD:
        messageID = pl_msg_pokedex_opal_ev_m_magnetic;
        break;
    case EVO_LEVEL_MOSS_ROCK:
        messageID = pl_msg_pokedex_opal_ev_m_moss;
        break;
    case EVO_LEVEL_ICE_ROCK:
        messageID = pl_msg_pokedex_opal_ev_m_ice;
        break;
    case EVO_LEVEL_SPATK_GT_ATK:
        messageID = pl_msg_pokedex_opal_ev_m_spa_gt_atk;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_SPATK_GE_ATK:
        messageID = pl_msg_pokedex_opal_ev_m_spa_ge_atk;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_ATK_GT_SPATK:
        messageID = pl_msg_pokedex_opal_ev_m_atk_gt_spa;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_SPDEF_GT_DEF:
        messageID = pl_msg_pokedex_opal_ev_m_spd_gt_def;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_NIGHT:
        messageID = pl_msg_pokedex_opal_ev_m_level_night;
        numberParam = TRUE;
        break;
    case EVO_LEVEL_DAY:
        messageID = pl_msg_pokedex_opal_ev_m_level_day;
        numberParam = TRUE;
        break;
    default:
        // EVO_TRADE / EVO_TRADE_WITH_HELD_ITEM must never appear in Opal's evolution tables;
        // the generator validator fails the build on any such edge. Show a neutral label otherwise.
        break;
    }

    if (numberParam) {
        StringTemplate_SetNumber(ctx->template, 0, evolution->param, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
    } else if (itemParam) {
        StringTemplate_SetItemName(ctx->template, 0, evolution->param);
    }

    return UiExpanded(ctx, messageID);
}

static u16 *LoadPreEvolutions(enum HeapID heapID)
{
    u16 *preEvolutions = Heap_Alloc(heapID, sizeof(u16) * (OPAL_NATIONAL_MAX + 1));
    SpeciesEvolution evolutions[MAX_EVOLUTIONS];
    NARC *evolutionNarc = NARC_ctor(NARC_INDEX_POKETOOL__PERSONAL__EVO, heapID);
    int species, i;

    memset(preEvolutions, 0, sizeof(u16) * (OPAL_NATIONAL_MAX + 1));

    for (species = 1; species <= OPAL_NATIONAL_MAX; species++) {
        NARC_ReadWholeMember(evolutionNarc, species, evolutions);

        for (i = 0; i < MAX_EVOLUTIONS; i++) {
            if (evolutions[i].method != EVO_NONE && evolutions[i].targetSpecies > 0 && evolutions[i].targetSpecies <= OPAL_NATIONAL_MAX) {
                preEvolutions[evolutions[i].targetSpecies] = species;
            }
        }
    }

    NARC_dtor(evolutionNarc);
    return preEvolutions;
}

static u16 FindFamilyRoot(const u16 *preEvolutions, u16 species)
{
    int guard;

    for (guard = 0; guard < 4 && preEvolutions[species] != 0; guard++) {
        species = preEvolutions[species];
    }

    return species;
}

static void AddFamilyBranch(BuildContext *ctx, const u16 *preEvolutions, NARC *evolutionNarc, u16 species, int depth)
{
    SpeciesEvolution evolutions[MAX_EVOLUTIONS];
    int i;

    if (depth > 3) {
        return;
    }

    NARC_ReadWholeMember(evolutionNarc, species, evolutions);

    for (i = 0; i < MAX_EVOLUTIONS; i++) {
        u16 target = evolutions[i].targetSpecies;
        OpalRow *row;
        String *targetName;
        String *method;
        u8 x = OPAL_TEXT_X + depth * 8;
        u32 nameWidth, methodWidth;
        enum OpalColor nameColor;

        if (evolutions[i].method == EVO_NONE || target == SPECIES_NONE || target > OPAL_NATIONAL_MAX) {
            continue;
        }

        targetName = SpeciesNameString(ctx, target);
        method = EvolutionMethodString(ctx, &evolutions[i]);
        nameWidth = Font_CalcMaxLineWidth(FONT_SYSTEM, targetName, 0);
        methodWidth = Font_CalcMaxLineWidth(FONT_SYSTEM, method, 0);
        nameColor = (target == ctx->species) ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT;

        row = AddRow(ctx, 1);

        {
            String *arrowName = String_Init(48, ctx->heapID);

            String_AppendChar(arrowName, CHAR_ARROW_RIGHT);
            String_Concat(arrowName, targetName);
            AddCell(row, x, nameColor, arrowName);
        }

        if (x + 12 + nameWidth + 8 + methodWidth <= OPAL_SCREEN_RIGHT) {
            AddCell(row, x + 12 + nameWidth + 8, OPAL_COLOR_DIM, method);
        } else {
            row = AddRow(ctx, 1);
            AddCell(row, x + 12, OPAL_COLOR_DIM, method);
        }

        String_Free(targetName);
        AddFamilyBranch(ctx, preEvolutions, evolutionNarc, target, depth + 1);
    }
}

static void BuildEvolution(BuildContext *ctx)
{
    u16 *preEvolutions = LoadPreEvolutions(ctx->heapID);
    u16 root = FindFamilyRoot(preEvolutions, ctx->species);
    NARC *evolutionNarc = NARC_ctor(NARC_INDEX_POKETOOL__PERSONAL__EVO, ctx->heapID);
    SpeciesEvolution evolutions[MAX_EVOLUTIONS];
    OpalRow *row;
    int i;
    BOOL hasEvolution = FALSE;

    NARC_ReadWholeMember(evolutionNarc, root, evolutions);

    for (i = 0; i < MAX_EVOLUTIONS; i++) {
        if (evolutions[i].method != EVO_NONE) {
            hasEvolution = TRUE;
        }
    }

    if (!hasEvolution) {
        AddLabelRow(ctx, pl_msg_pokedex_opal_ev_none, OPAL_COLOR_DIM);
    } else {
        AddLabelRow(ctx, pl_msg_pokedex_opal_ev_family, OPAL_COLOR_DIM);

        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X, root == ctx->species ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, SpeciesNameString(ctx, root));
        AddFamilyBranch(ctx, preEvolutions, evolutionNarc, root, 1);
    }

    NARC_dtor(evolutionNarc);
    Heap_Free(preEvolutions);
}

// --------------------------------------------------------------------------
// Level-up learnset
// --------------------------------------------------------------------------
static void BuildLearnset(BuildContext *ctx)
{
    u16 *moves = Heap_Alloc(ctx->heapID, sizeof(SpeciesLearnset));
    OpalRow *row;
    int i;
    BOOL any = FALSE;

    Pokemon_LoadLevelUpMovesOf(ctx->species, 0, moves);

    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ls_h_lv));
    AddCell(row, 34, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ls_h_move));
    AddCell(row, 120, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ls_h_type));
    AddCell(row, 170, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ls_h_pow));
    AddCell(row, 196, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ls_h_acc));
    AddCell(row, 222, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_ls_h_pp));

    for (i = 0; moves[i] != LEARNSET_SENTINEL_ENTRY; i++) {
        u16 move = moves[i] & 0x1FF;
        u16 level = (moves[i] & 0xFE00) >> 9;
        int power = MoveTable_LoadParam(move, MOVEATTRIBUTE_POWER);
        int accuracy = MoveTable_LoadParam(move, MOVEATTRIBUTE_ACCURACY);
        int pp = MoveTable_LoadParam(move, MOVEATTRIBUTE_PP);
        int type = MoveTable_LoadParam(move, MOVEATTRIBUTE_TYPE);
        int class = MoveTable_LoadParam(move, MOVEATTRIBUTE_CLASS);
        enum OpalColor color = OPAL_COLOR_TEXT;

        if (class == CLASS_PHYSICAL) {
            color = OPAL_COLOR_BAD;
        } else if (class == CLASS_SPECIAL) {
            color = OPAL_COLOR_ACCENT;
        } else {
            color = OPAL_COLOR_DIM;
        }

        any = TRUE;
        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X, OPAL_COLOR_GOLD, NumberString(ctx, level, 3));
        AddCell(row, 34, color, MoveNameString(ctx, move));
        AddCell(row, 120, OPAL_COLOR_TEXT, TypeNameString(ctx, type));

        if (power > 0) {
            AddCell(row, 170, OPAL_COLOR_TEXT, NumberString(ctx, power, 3));
        }

        if (accuracy > 0) {
            AddCell(row, 196, OPAL_COLOR_TEXT, NumberString(ctx, accuracy, 3));
        }

        AddCell(row, 222, OPAL_COLOR_DIM, NumberString(ctx, pp, 2));
    }

    if (!any) {
        AddLabelRow(ctx, pl_msg_pokedex_opal_ls_empty, OPAL_COLOR_DIM);
    }

    Heap_Free(moves);
}

// --------------------------------------------------------------------------
// TM / HM compatibility
// --------------------------------------------------------------------------
static String *MachineEntryString(BuildContext *ctx, int machine)
{
    String *label;
    String *name;
    String *entry;
    int number = machine < OPAL_FIRST_HM ? machine + 1 : machine - OPAL_FIRST_HM + 1;

    StringTemplate_SetNumber(ctx->template, 0, number, 2, PADDING_MODE_ZEROES, CHARSET_MODE_EN);
    label = UiExpanded(ctx, machine < OPAL_FIRST_HM ? pl_msg_pokedex_opal_tm_tm : pl_msg_pokedex_opal_tm_hm);
    name = MoveNameString(ctx, Item_MoveForTMHM(ITEM_TM01 + machine));

    entry = String_Init(40, ctx->heapID);
    String_Copy(entry, label);
    String_AppendChar(entry, CHAR_SPACE);
    String_Concat(entry, name);

    String_Free(label);
    String_Free(name);
    return entry;
}

static void BuildMachines(BuildContext *ctx)
{
    int machine, count = 0;
    OpalRow *row;
    BOOL pendingLeft = FALSE;
    OpalRow *current = NULL;

    for (machine = 0; machine < OPAL_NUM_MACHINES; machine++) {
        if (CanPokemonFormLearnTM(ctx->species, 0, machine)) {
            count++;
        }
    }

    if (count == 0) {
        AddLabelRow(ctx, pl_msg_pokedex_opal_tm_none, OPAL_COLOR_DIM);
        return;
    }

    StringTemplate_SetNumber(ctx->template, 0, count, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
    StringTemplate_SetNumber(ctx->template, 1, OPAL_NUM_MACHINES, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_GOLD, UiExpanded(ctx, pl_msg_pokedex_opal_tm_count));

    for (machine = 0; machine < OPAL_NUM_MACHINES; machine++) {
        if (!CanPokemonFormLearnTM(ctx->species, 0, machine)) {
            continue;
        }

        if (!pendingLeft) {
            current = AddRow(ctx, 1);
            AddCell(current, OPAL_TEXT_X, machine >= OPAL_FIRST_HM ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, MachineEntryString(ctx, machine));
            pendingLeft = TRUE;
        } else {
            AddCell(current, 130, machine >= OPAL_FIRST_HM ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, MachineEntryString(ctx, machine));
            pendingLeft = FALSE;
        }
    }
}

// --------------------------------------------------------------------------
// Locations
// --------------------------------------------------------------------------
static const OpalLocationRecord *LocationRecords(const u8 *table, u16 species, u8 *count)
{
    const u16 *offsets;
    u32 offset;

    *count = 0;

    if (table == NULL || species > OPAL_NATIONAL_MAX) {
        return NULL;
    }

    offsets = (const u16 *)(table + 2);
    offset = offsets[species];
    *count = table[offset];

    return (const OpalLocationRecord *)(table + offset + 1);
}

static String *TimeFlagsString(BuildContext *ctx, u8 flags)
{
    String *string = String_Init(8, ctx->heapID);
    // M/D/N initials, from the three bands the species appears in
    static const charcode_t sInitials[3] = { CHAR_M, CHAR_D, CHAR_N };
    int band;

    if ((flags & OPAL_LOCF_ALLTIME) == OPAL_LOCF_ALLTIME) {
        return string;
    }

    for (band = 0; band < 3; band++) {
        if (flags & (1 << band)) {
            String_AppendChar(string, sInitials[band]);
        }
    }

    return string;
}

static void BuildLocations(BuildContext *ctx)
{
    u8 count;
    const OpalLocationRecord *records = LocationRecords(ctx->locationTable, ctx->species, &count);
    int kind, i;
    OpalRow *row;

    if (records == NULL || count == 0) {
        // Not a recorded wild/event source: say so rather than guessing.
        u16 preEvolution = 0;
        u16 *preEvolutions = LoadPreEvolutions(ctx->heapID);

        preEvolution = preEvolutions[ctx->species];
        Heap_Free(preEvolutions);

        if (preEvolution != 0) {
            StringTemplate_SetNumber(ctx->template, 0, 0, 1, PADDING_MODE_NONE, CHARSET_MODE_EN);
            AddLabelRow(ctx, pl_msg_pokedex_opal_ev_family, OPAL_COLOR_DIM);
            row = AddRow(ctx, 1);
            AddCell(row, OPAL_TEXT_X, OPAL_COLOR_ACCENT, SpeciesNameString(ctx, preEvolution));
        } else {
            String *message = UiString(ctx, pl_msg_pokedex_opal_lo_none);
            u32 lines = String_NumLines(message);
            u32 line;

            for (line = 0; line < lines; line++) {
                String *part = String_Init(64, ctx->heapID);
                String_CopyLineNum(part, message, line);
                AddCell(AddRow(ctx, 1), OPAL_TEXT_X, OPAL_COLOR_DIM, part);
            }

            String_Free(message);
        }

        return;
    }

    AddLabelRow(ctx, pl_msg_pokedex_opal_lo_time_legend, OPAL_COLOR_DIM);

    for (kind = 0; kind < OPAL_LOC_KIND_MAX; kind++) {
        BOOL headerAdded = FALSE;

        for (i = 0; i < count; i++) {
            const OpalLocationRecord *record = &records[i];
            u8 flags = record->flags;
            String *place;
            String *time;
            u8 nameX = OPAL_TEXT_X + 8;

            if (record->kind != kind) {
                continue;
            }

            if (!headerAdded) {
                AddLabelRow(ctx, sLocationKindLabel[kind], OPAL_COLOR_GOLD);
                headerAdded = TRUE;
            }

            if (record->aux & OPAL_LOC_AUX_SPECIES) {
                place = SpeciesNameString(ctx, record->name);
            } else if (record->aux & OPAL_LOC_AUX_TEXT) {
                place = UiString(ctx, record->name);
            } else {
                StringTemplate_SetLocationName(ctx->template, 0, record->name);
                place = UiExpanded(ctx, pl_msg_pokedex_opal_slot0);
            }

            row = AddRow(ctx, 1);
            AddCell(row, nameX, OPAL_COLOR_TEXT, place);

            time = TimeFlagsString(ctx, flags);

            if (String_Length(time) > 0) {
                AddCell(row, 128, OPAL_COLOR_DIM, time);
            } else {
                String_Free(time);
            }

            if (record->maxLevel != 0) {
                if (record->minLevel == record->maxLevel) {
                    StringTemplate_SetNumber(ctx->template, 0, record->minLevel, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
                    AddCell(row, 152, OPAL_COLOR_ACCENT, UiExpanded(ctx, pl_msg_pokedex_opal_lo_level));
                } else {
                    StringTemplate_SetNumber(ctx->template, 0, record->minLevel, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
                    StringTemplate_SetNumber(ctx->template, 1, record->maxLevel, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
                    AddCell(row, 152, OPAL_COLOR_ACCENT, UiExpanded(ctx, pl_msg_pokedex_opal_lo_level_range));
                }
            }

            if (record->percent != 0) {
                StringTemplate_SetNumber(ctx->template, 0, record->percent, 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
                AddCell(row, 214, OPAL_COLOR_TEXT, UiExpanded(ctx, pl_msg_pokedex_opal_lo_pct));
            }

            if (flags & (OPAL_LOCF_HOF | OPAL_LOCF_BADGES | OPAL_LOCF_ONCE)) {
                row = AddRow(ctx, 1);
                nameX += 8;

                if (flags & OPAL_LOCF_HOF) {
                    AddCell(row, nameX, OPAL_COLOR_GOOD, UiString(ctx, pl_msg_pokedex_opal_lo_hof));
                    nameX += 120;
                }

                if (flags & OPAL_LOCF_BADGES) {
                    StringTemplate_SetNumber(ctx->template, 0, record->aux & 0x3F, 1, PADDING_MODE_NONE, CHARSET_MODE_EN);
                    AddCell(row, nameX, OPAL_COLOR_GOOD, UiExpanded(ctx, pl_msg_pokedex_opal_lo_badges));
                    nameX += 72;
                }

                if (flags & OPAL_LOCF_ONCE) {
                    AddCell(row, nameX, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_lo_once));
                }
            }
        }
    }

    row = AddRow(ctx, 1);
    AddCell(row, OPAL_TEXT_X, OPAL_COLOR_DIM, UiString(ctx, pl_msg_pokedex_opal_lo_note));
}

// --------------------------------------------------------------------------
// Forms
// --------------------------------------------------------------------------
static u8 SpeciesFormCount(u16 species)
{
    return OpalData_NumDataForms(species);
}

static u32 FormNameMessage(u16 species, int form)
{
    static const u16 sDeoxys[] = { pl_msg_pokedex_opal_fo_deoxys_0, pl_msg_pokedex_opal_fo_deoxys_1, pl_msg_pokedex_opal_fo_deoxys_2, pl_msg_pokedex_opal_fo_deoxys_3 };
    static const u16 sWormadam[] = { pl_msg_pokedex_opal_fo_wormadam_0, pl_msg_pokedex_opal_fo_wormadam_1, pl_msg_pokedex_opal_fo_wormadam_2 };
    static const u16 sGiratina[] = { pl_msg_pokedex_opal_fo_giratina_0, pl_msg_pokedex_opal_fo_giratina_1 };
    static const u16 sShaymin[] = { pl_msg_pokedex_opal_fo_shaymin_0, pl_msg_pokedex_opal_fo_shaymin_1 };
    static const u16 sRotom[] = { pl_msg_pokedex_opal_fo_rotom_0, pl_msg_pokedex_opal_fo_rotom_1, pl_msg_pokedex_opal_fo_rotom_2, pl_msg_pokedex_opal_fo_rotom_3, pl_msg_pokedex_opal_fo_rotom_4, pl_msg_pokedex_opal_fo_rotom_5 };

    switch (species) {
    case SPECIES_DEOXYS:
        return sDeoxys[form];
    case SPECIES_WORMADAM:
        return sWormadam[form];
    case SPECIES_GIRATINA:
        return sGiratina[form];
    case SPECIES_SHAYMIN:
        return sShaymin[form];
    case SPECIES_ROTOM:
        return sRotom[form];
    }

    return pl_msg_pokedex_opal_fo_base;
}

static BOOL HasCosmeticForms(u16 species)
{
    switch (species) {
    case SPECIES_UNOWN:
    case SPECIES_CASTFORM:
    case SPECIES_BURMY:
    case SPECIES_CHERRIM:
    case SPECIES_SHELLOS:
    case SPECIES_GASTRODON:
    case SPECIES_ARCEUS:
        return TRUE;
    }

    return FALSE;
}

static void BuildForms(BuildContext *ctx)
{
    static const u8 sStatParams[] = {
        SPECIES_DATA_BASE_HP,
        SPECIES_DATA_BASE_ATK,
        SPECIES_DATA_BASE_DEF,
        SPECIES_DATA_BASE_SP_ATK,
        SPECIES_DATA_BASE_SP_DEF,
        SPECIES_DATA_BASE_SPEED,
    };
    u8 numForms = SpeciesFormCount(ctx->species);
    SpeciesData *base;
    int form, i;
    OpalRow *row;

    if (numForms <= 1) {
        String *message = UiString(ctx, HasCosmeticForms(ctx->species) ? pl_msg_pokedex_opal_fo_cosmetic : pl_msg_pokedex_opal_fo_none);
        u32 lines = String_NumLines(message);
        u32 line;

        for (line = 0; line < lines; line++) {
            String *part = String_Init(64, ctx->heapID);
            String_CopyLineNum(part, message, line);
            AddCell(AddRow(ctx, 1), OPAL_TEXT_X, OPAL_COLOR_DIM, part);
        }

        String_Free(message);
        return;
    }

    AddLabelRow(ctx, pl_msg_pokedex_opal_fo_changed_note, OPAL_COLOR_DIM);
    base = SpeciesData_FromMonForm(ctx->species, 0, ctx->heapID);

    for (form = 0; form < numForms; form++) {
        SpeciesData *data = SpeciesData_FromMonForm(ctx->species, form, ctx->heapID);
        int stats[6];
        BOOL typeChanged, abilityChanged, statsChanged1 = FALSE, statsChanged2 = FALSE;
        int type1 = StatValue(data, SPECIES_DATA_TYPE_1);
        int type2 = StatValue(data, SPECIES_DATA_TYPE_2);
        int ability1 = StatValue(data, SPECIES_DATA_ABILITY_1);
        int ability2 = StatValue(data, SPECIES_DATA_ABILITY_2);

        typeChanged = form > 0 && (type1 != StatValue(base, SPECIES_DATA_TYPE_1) || type2 != StatValue(base, SPECIES_DATA_TYPE_2));
        abilityChanged = form > 0 && (ability1 != StatValue(base, SPECIES_DATA_ABILITY_1) || ability2 != StatValue(base, SPECIES_DATA_ABILITY_2));

        for (i = 0; i < 6; i++) {
            stats[i] = StatValue(data, sStatParams[i]);

            if (form > 0 && stats[i] != StatValue(base, sStatParams[i])) {
                if (i < 3) {
                    statsChanged1 = TRUE;
                } else {
                    statsChanged2 = TRUE;
                }
            }
        }

        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X, OPAL_COLOR_GOLD, UiString(ctx, FormNameMessage(ctx->species, form)));

        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X + 8, typeChanged ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, TypeNameString(ctx, type1));

        if (type2 != type1) {
            AddCell(row, 88, typeChanged ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, TypeNameString(ctx, type2));
        }

        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X + 8, abilityChanged ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, AbilityNameString(ctx, ability1));

        if (ability2 != ABILITY_NONE && ability2 != ability1) {
            AddCell(row, 128, abilityChanged ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, AbilityNameString(ctx, ability2));
        }

        StringTemplate_SetNumber(ctx->template, 0, stats[0], 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        StringTemplate_SetNumber(ctx->template, 1, stats[1], 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        StringTemplate_SetNumber(ctx->template, 2, stats[2], 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X + 8, statsChanged1 ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, UiExpanded(ctx, pl_msg_pokedex_opal_fo_stat_line1));

        StringTemplate_SetNumber(ctx->template, 0, stats[3], 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        StringTemplate_SetNumber(ctx->template, 1, stats[4], 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        StringTemplate_SetNumber(ctx->template, 2, stats[5], 3, PADDING_MODE_NONE, CHARSET_MODE_EN);
        row = AddRow(ctx, 1);
        AddCell(row, OPAL_TEXT_X + 8, statsChanged2 ? OPAL_COLOR_GOLD : OPAL_COLOR_TEXT, UiExpanded(ctx, pl_msg_pokedex_opal_fo_stat_line2));

        SpeciesData_Free(data);
    }

    SpeciesData_Free(base);
}
