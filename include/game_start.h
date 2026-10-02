#ifndef POKEPLATINUM_GAME_START_H
#define POKEPLATINUM_GAME_START_H

#include "overlay_manager.h"

extern const ApplicationManagerTemplate gGameStartLoadSaveAppTemplate;
extern const ApplicationManagerTemplate gGameStartNewSaveAppTemplate;
extern const ApplicationManagerTemplate gGameStartRowanIntroAppTemplate;
#ifdef GDB_DEBUGGING
extern const ApplicationManagerTemplate gGameStartRuntimeQANewSaveAppTemplate;
#endif

#endif // POKEPLATINUM_GAME_START_H
