#ifndef POKEPLATINUM_STRUCT_020425E0_H
#define POKEPLATINUM_STRUCT_020425E0_H

#include "game_options.h"

typedef struct ChooseStarterData {
    int eggPosition; // output only; never selects a species
    const Options *options;
} ChooseStarterData;

#endif // POKEPLATINUM_STRUCT_020425E0_H
