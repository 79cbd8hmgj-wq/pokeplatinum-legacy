#include "mystery_egg_starter.h"

#include <nitro.h>

#include "generated/species.h"

#include "math_util.h"

typedef struct MysteryStarterEntry {
    u16 species;
    u8 weight;
} MysteryStarterEntry;

// Weights are integer units out of MYSTERY_STARTER_ROLL_RANGE (100).
static const MysteryStarterEntry sMysteryStarterTable[MYSTERY_STARTER_POOL_SIZE] = {
    { SPECIES_BULBASAUR, 3 },
    { SPECIES_CHARMANDER, 3 },
    { SPECIES_SQUIRTLE, 3 },
    { SPECIES_PIKACHU, 1 },
    { SPECIES_CHIKORITA, 10 },
    { SPECIES_CYNDAQUIL, 10 },
    { SPECIES_TOTODILE, 10 },
    { SPECIES_TREECKO, 10 },
    { SPECIES_TORCHIC, 10 },
    { SPECIES_MUDKIP, 10 },
    { SPECIES_TURTWIG, 10 },
    { SPECIES_CHIMCHAR, 10 },
    { SPECIES_PIPLUP, 10 },
};

u16 MysteryStarter_SpeciesFromRoll(u32 roll)
{
    u32 upperBound = 0;

    for (int i = 0; i < MYSTERY_STARTER_POOL_SIZE; i++) {
        upperBound += sMysteryStarterTable[i].weight;

        if (roll < upperBound) {
            return sMysteryStarterTable[i].species;
        }
    }

    GF_ASSERT(FALSE);
    return SPECIES_PIPLUP;
}

u16 MysteryStarter_Draw(void)
{
    u32 roll = LCRNG_Next() % MYSTERY_STARTER_ROLL_RANGE;

    return MysteryStarter_SpeciesFromRoll(roll);
}

u16 MysteryStarter_GetRivalBranch(u16 species)
{
    switch (species) {
    case SPECIES_BULBASAUR:
    case SPECIES_CHIKORITA:
    case SPECIES_TREECKO:
    case SPECIES_TURTWIG:
        return SPECIES_TURTWIG;

    case SPECIES_CHARMANDER:
    case SPECIES_CYNDAQUIL:
    case SPECIES_TORCHIC:
    case SPECIES_CHIMCHAR:
        return SPECIES_CHIMCHAR;

    case SPECIES_SQUIRTLE:
    case SPECIES_TOTODILE:
    case SPECIES_MUDKIP:
    case SPECIES_PIPLUP:
    case SPECIES_PIKACHU:
    default:
        return SPECIES_PIPLUP;
    }
}
