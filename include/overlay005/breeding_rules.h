#ifndef POKEPLATINUM_OVERLAY005_BREEDING_RULES_H
#define POKEPLATINUM_OVERLAY005_BREEDING_RULES_H

// Breeding 2.0 decision logic (docs/overhaul/breeding/BREEDING_SPEC.md).
//
// These helpers are pure: they touch no game state, so tools/overhaul/validate_breeding.py
// can compile them on the host. The including file must provide u8/u16/u32, the ITEM_*
// and STAT_* constants, NUM_DAYCARE_MONS, NUM_INHERITED_IVS, LEARNED_MOVES_MAX, and a
// BREEDING_RNG() macro returning a 16-bit random value, plus BREEDING_NATURE_OF(personality)
// and BREEDING_ARNG(personality) for the personality helpers.

#define BREEDING_NO_STAT                 0xff
#define BREEDING_NO_PARENT               (-1)
#define BREEDING_ABILITY_INHERIT_PERCENT 80
#define BREEDING_MAX_GATHERED_EGG_MOVES  (LEARNED_MOVES_MAX * NUM_DAYCARE_MONS)

// Everstone: bit i of everstoneMask is set when parent slot i holds an Everstone.
// Returns the parent slot whose nature is inherited, or BREEDING_NO_PARENT.
static inline int BreedingRules_PickNatureParent(u8 everstoneMask)
{
    switch (everstoneMask & 3) {
    case 1:
        return 0;
    case 2:
        return 1;
    case 3:
        return (BREEDING_RNG() >= (0xffff / 2)) ? 0 : 1;
    }

    return BREEDING_NO_PARENT;
}

static inline u8 BreedingRules_PowerItemToStat(u16 item)
{
    switch (item) {
    case ITEM_POWER_WEIGHT:
        return STAT_HP;
    case ITEM_POWER_BRACER:
        return STAT_ATTACK;
    case ITEM_POWER_BELT:
        return STAT_DEFENSE;
    case ITEM_POWER_LENS:
        return STAT_SPECIAL_ATTACK;
    case ITEM_POWER_BAND:
        return STAT_SPECIAL_DEFENSE;
    case ITEM_POWER_ANKLET:
        return STAT_SPEED;
    }

    return BREEDING_NO_STAT;
}

// Chooses NUM_INHERITED_IVS distinct stats and the parent slot each is copied from.
// A held Power item reserves entry 0 (one guarantee only; if both parents hold one,
// a holder is picked at random).
static inline void BreedingRules_SelectInheritedIVs(const u16 heldItems[NUM_DAYCARE_MONS], u8 stats[NUM_INHERITED_IVS], u8 sources[NUM_INHERITED_IVS])
{
    u8 available[STAT_MAX];
    u8 powerStat[NUM_DAYCARE_MONS];
    u8 count = STAT_MAX;
    u8 start = 0;
    u8 i, j, pick;
    u8 qualifying = 0;

    for (i = 0; i < STAT_MAX; i++) {
        available[i] = i;
    }

    for (i = 0; i < NUM_DAYCARE_MONS; i++) {
        powerStat[i] = BreedingRules_PowerItemToStat(heldItems[i]);

        if (powerStat[i] != BREEDING_NO_STAT) {
            qualifying++;
        }
    }

    if (qualifying != 0) {
        pick = 0;

        if (qualifying == NUM_DAYCARE_MONS) {
            pick = BREEDING_RNG() % NUM_DAYCARE_MONS;
        } else if (powerStat[1] != BREEDING_NO_STAT) {
            pick = 1;
        }

        stats[0] = powerStat[pick];
        sources[0] = pick;
        start = 1;

        for (j = 0; j < count; j++) {
            if (available[j] == stats[0]) {
                break;
            }
        }

        for (; j + 1 < count; j++) {
            available[j] = available[j + 1];
        }

        count--;
    }

    for (i = start; i < NUM_INHERITED_IVS; i++) {
        pick = BREEDING_RNG() % count;
        stats[i] = available[pick];

        for (j = pick; j + 1 < count; j++) {
            available[j] = available[j + 1];
        }

        count--;
    }

    for (i = start; i < NUM_INHERITED_IVS; i++) {
        sources[i] = BREEDING_RNG() % NUM_DAYCARE_MONS;
    }
}

// 80% the offspring keeps the species parent's ability slot (0/1), 20% the other one.
static inline u8 BreedingRules_PickAbilitySlot(u8 parentSlot)
{
    if ((BREEDING_RNG() % 100) < BREEDING_ABILITY_INHERIT_PERCENT) {
        return parentSlot;
    }

    return parentSlot ^ 1;
}

// Collects listed egg moves known by the father, then the mother, in move-slot order,
// without duplicates. Returns the number of moves written to out.
static inline u8 BreedingRules_GatherEggMoves(const u16 fatherMoves[LEARNED_MOVES_MAX], const u16 motherMoves[LEARNED_MOVES_MAX], const u16 *listed, u8 listedCount, u16 out[BREEDING_MAX_GATHERED_EGG_MOVES])
{
    const u16 *parents[NUM_DAYCARE_MONS];
    u8 count = 0;
    u8 p, i, j, k;

    parents[0] = fatherMoves;
    parents[1] = motherMoves;

    for (p = 0; p < NUM_DAYCARE_MONS; p++) {
        for (i = 0; i < LEARNED_MOVES_MAX; i++) {
            u16 move = parents[p][i];

            if (move == 0) {
                break;
            }

            for (j = 0; j < listedCount; j++) {
                if (move != listed[j]) {
                    continue;
                }

                for (k = 0; k < count; k++) {
                    if (out[k] == move) {
                        break;
                    }
                }

                if (k == count) {
                    out[count++] = move;
                }

                break;
            }
        }
    }

    return count;
}

// Personality constraints for an egg: the inherited nature (-1 = any) and the ability
// slot, i.e. personality bit 0 (-1 = any).
static inline int BreedingRules_PersonalityMatches(u32 personality, int nature, int abilitySlot)
{
    if (nature >= 0 && (int)BREEDING_NATURE_OF(personality) != nature) {
        return 0;
    }

    if (abilitySlot >= 0 && (int)(personality & 1) != abilitySlot) {
        return 0;
    }

    return 1;
}

// Next ARNG personality that satisfies the constraints. With no constraint this is
// exactly the vanilla Masuda reroll (a single ARNG step).
static inline u32 BreedingRules_NextPersonality(u32 personality, int nature, int abilitySlot)
{
    int tries = 0;

    do {
        personality = BREEDING_ARNG(personality);
    } while (!BreedingRules_PersonalityMatches(personality, nature, abilitySlot) && ++tries <= 2400);

    return personality;
}

// True on the steps where the Day Care rolls for an egg.
static inline int BreedingRules_IsEggCheckStep(u32 steps)
{
    return (steps & DAYCARE_EGG_CHECK_STEP_MASK) == DAYCARE_EGG_CHECK_STEP_MASK;
}

// Flame Body / Magma Armor in the party halve the hatch walk.
static inline int BreedingRules_EggCyclesToSubtract(u8 ability)
{
    return (ability == ABILITY_MAGMA_ARMOR || ability == ABILITY_FLAME_BODY) ? 2 : 1;
}

// eggCycles must be non-zero.
static inline u32 BreedingRules_SubtractEggCycles(u32 eggCycles, int toSubtract)
{
    return (eggCycles >= (u32)toSubtract) ? eggCycles - toSubtract : eggCycles - 1;
}

#endif // POKEPLATINUM_OVERLAY005_BREEDING_RULES_H
