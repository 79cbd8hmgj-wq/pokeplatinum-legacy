#ifndef POKEPLATINUM_APPLICATIONS_STILL_CARD_H
#define POKEPLATINUM_APPLICATIONS_STILL_CARD_H

#include "overlay_manager.h"
#include "savedata.h"

enum StillCardID {
    STILL_CARD_SOLACEON_NEWS_PRESS = 0,
    STILL_CARD_COUNT,
};

typedef struct StillCardData {
    SaveData *saveData;
    enum StillCardID cardID;
    u8 startState;
} StillCardData;

BOOL StillCard_Init(ApplicationManager *appMan, int *state);
BOOL StillCard_Main(ApplicationManager *appMan, int *state);
BOOL StillCard_Exit(ApplicationManager *appMan, int *state);

#endif // POKEPLATINUM_APPLICATIONS_STILL_CARD_H
