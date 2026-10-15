// LOCAL RUNTIME-QA HARNESS - never committed. Boots straight into the Pokedex with every species
// seen/caught so the Opal pages can be driven in an emulator without playing through the intro.
#include <nitro.h>
#include <string.h>

#include "constants/heap.h"
#include "constants/species.h"

#include "applications/pokedex/pokedex_main.h"

#include "gx_layers.h"
#include "heap.h"
#include "main.h"
#include "overlay_manager.h"
#include "pokedex.h"
#include "pokedex_memory.h"
#include "savedata.h"
#include "trainer_info.h"

typedef struct OpalQaData {
    ApplicationManager *child;
    PokedexOverlayArgs args;
} OpalQaData;

static BOOL OpalQa_Init(ApplicationManager *appMan, int *state);
static BOOL OpalQa_Main(ApplicationManager *appMan, int *state);
static BOOL OpalQa_Exit(ApplicationManager *appMan, int *state);

const ApplicationManagerTemplate gOpalDexQaAppTemplate = {
    OpalQa_Init,
    OpalQa_Main,
    OpalQa_Exit,
    FS_OVERLAY_ID_NONE
};

static BOOL OpalQa_Init(ApplicationManager *appMan, int *state)
{
    FS_EXTERN_OVERLAY(pokedex);
    static const ApplicationManagerTemplate sDex = {
        PokedexMain_Init,
        PokedexMain_Main,
        PokedexMain_Exit,
        FS_OVERLAY_ID(pokedex)
    };

    GXLayers_TurnBothDispOn();
    Heap_Create(HEAP_ID_APPLICATION, HEAP_ID_FIELD2, HEAP_SIZE_FIELD2);

    OpalQaData *data = ApplicationManager_NewData(appMan, sizeof(OpalQaData), HEAP_ID_FIELD2);
    SaveData *save = ((ApplicationArgs *)ApplicationManager_Args(appMan))->saveData;
    Pokedex *dex = SaveData_GetPokedex(save);
    int sp;

    for (sp = 1; sp <= NATIONAL_DEX_COUNT; sp++) {
        dex->caughtPokemon[(sp - 1) / 32] |= 1 << ((sp - 1) % 32);
        dex->seenPokemon[(sp - 1) / 32] |= 1 << ((sp - 1) % 32);
    }

    memset(dex->recordedLanguages, 0x3F, sizeof(dex->recordedLanguages));
    dex->shellosFormsSeen = 3;
    dex->gastrodonFormsSeen = 3;
    dex->burmyFormsSeen = 7;
    dex->wormadamFormsSeen = 7;
    dex->canDetectForms = TRUE;
    dex->canDetectLanguages = TRUE;
    dex->pokedexObtained = TRUE;
    dex->nationalDexObtained = TRUE;

    data->args.pokedex = dex;
    data->args.trainerInfo = SaveData_GetTrainerInfo(save);
    data->args.timeOfDay = 1;
    data->args.fullmoonIslandVisible = FALSE;
    data->args.newmoonIslandVisible = FALSE;
    data->args.springPathVisible = FALSE;
    data->args.seabreakPathVisible = FALSE;
    data->args.pokedexMemory = PokedexMemory_New(HEAP_ID_FIELD2);

    data->child = ApplicationManager_New(&sDex, &data->args, HEAP_ID_FIELD2);
    return TRUE;
}

static BOOL OpalQa_Main(ApplicationManager *appMan, int *state)
{
    OpalQaData *data = ApplicationManager_Data(appMan);

    if (data->child && ApplicationManager_Exec(data->child)) {
        ApplicationManager_Free(data->child);
        data->child = NULL;
        return TRUE;
    }

    return FALSE;
}

static BOOL OpalQa_Exit(ApplicationManager *appMan, int *state)
{
    return TRUE;
}
