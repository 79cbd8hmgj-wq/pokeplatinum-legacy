#ifndef POKEPLATINUM_CONSTANTS_DAYCARE_H
#define POKEPLATINUM_CONSTANTS_DAYCARE_H

// Parent compatibility scores
#define PARENTS_INCOMPATIBLE      0
#define PARENTS_LOW_COMPATIBILITY 20
#define PARENTS_MED_COMPATIBILITY 50
#define PARENTS_MAX_COMPATIBILITY 70

// Daycare state
#define DAYCARE_NO_MONS     0
#define DAYCARE_EGG_WAITING 1
#define DAYCARE_ONE_MON     2
#define DAYCARE_TWO_MONS    3

#define NUM_DAYCARE_MONS  2
#define NUM_INHERITED_IVS 4
#define EGG_GENDER_MALE   0x8000 // used to create a male egg from a female-only parent species (e.g. Nidoran)
#define MAX_EGG_MOVES     16

// An egg is checked for every DAYCARE_EGG_CHECK_INTERVAL steps (was 256); the hatch
// cycle length (255 steps) is unchanged.
#define DAYCARE_EGG_CHECK_INTERVAL  128
#define DAYCARE_EGG_CHECK_STEP_MASK (DAYCARE_EGG_CHECK_INTERVAL - 1)

#endif // POKEPLATINUM_CONSTANTS_DAYCARE_H
