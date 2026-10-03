#ifndef POKEPLATINUM_MYSTERY_EGG_STARTER_H
#define POKEPLATINUM_MYSTERY_EGG_STARTER_H

#include <nitro/types.h>

#define MYSTERY_STARTER_POOL_SIZE  13
#define MYSTERY_STARTER_ROLL_RANGE 100
#define MYSTERY_STARTER_LEVEL      5

// Maps a roll in [0, MYSTERY_STARTER_ROLL_RANGE) to the actual starter species.
// The table is identical for every egg position; position is never an input.
u16 MysteryStarter_SpeciesFromRoll(u32 roll);

// Performs the single weighted draw and returns the actual starter species.
u16 MysteryStarter_Draw(void);

// Maps an actual starter species to the representative of its three-way Rival
// branch (Turtwig / Chimchar / Piplup).
u16 MysteryStarter_GetRivalBranch(u16 species);

#endif // POKEPLATINUM_MYSTERY_EGG_STARTER_H
