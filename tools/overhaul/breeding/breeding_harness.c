// Host-side harness for include/overlay005/breeding_rules.h (see validate_breeding.py).
// Prints "key value" lines; the validator asserts on them.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;

enum { STAT_HP, STAT_ATTACK, STAT_DEFENSE, STAT_SPEED, STAT_SPECIAL_ATTACK, STAT_SPECIAL_DEFENSE, STAT_MAX };
enum { ITEM_NONE_, ITEM_POWER_WEIGHT, ITEM_POWER_BRACER, ITEM_POWER_BELT, ITEM_POWER_LENS, ITEM_POWER_BAND, ITEM_POWER_ANKLET, ITEM_EVERSTONE, ITEM_OTHER };
enum { ABILITY_NONE, ABILITY_MAGMA_ARMOR, ABILITY_FLAME_BODY, ABILITY_OVERGROW };
#define LEARNED_MOVES_MAX 4
#define NUM_DAYCARE_MONS  2
#define NATURE_COUNT      25
#include "constants/daycare.h"

static u32 gSeed = 1;
static u16 lcrng(void)
{
    gSeed = gSeed * 0x41C64E6D + 0x6073;
    return (u16)(gSeed >> 16);
}
#define BREEDING_RNG()                   lcrng()
#define BREEDING_NATURE_OF(personality)  ((personality) % NATURE_COUNT)
#define BREEDING_ARNG(personality)       ((personality) * 1812433253u + 1)
#include "overlay005/breeding_rules.h"

static u32 mt = 12345;
static u32 mtrng(void)
{
    mt = mt * 1664525u + 1013904223u;
    return mt;
}

int main(void)
{
    int i, n = 20000;

    printf("NUM_INHERITED_IVS %d\n", NUM_INHERITED_IVS);
    printf("EGG_CHECK_INTERVAL %d\n", DAYCARE_EGG_CHECK_INTERVAL);

    // --- Everstone: mask -> parent distribution
    for (int mask = 0; mask < 4; mask++) {
        int c[3] = { 0, 0, 0 };
        for (i = 0; i < n; i++) {
            c[BreedingRules_PickNatureParent(mask) + 1]++;
        }
        printf("everstone mask%d none %d p0 %d p1 %d\n", mask, c[0], c[1], c[2]);
    }

    // --- IV selection: every item pair
    u16 items[9] = { ITEM_NONE_, ITEM_POWER_WEIGHT, ITEM_POWER_BRACER, ITEM_POWER_BELT, ITEM_POWER_LENS, ITEM_POWER_BAND, ITEM_POWER_ANKLET, ITEM_EVERSTONE, ITEM_OTHER };
    for (int a = 0; a < 9; a++) {
        for (int b = 0; b < 9; b++) {
            u16 held[2] = { items[a], items[b] };
            int dup = 0, bad = 0, forced0 = 0, srcbad = 0, pickfirst = 0, picksecond = 0;
            int countStat[STAT_MAX] = { 0 };
            u8 pa = BreedingRules_PowerItemToStat(items[a]), pb = BreedingRules_PowerItemToStat(items[b]);
            for (i = 0; i < 3000; i++) {
                u8 st[NUM_INHERITED_IVS], src[NUM_INHERITED_IVS];
                BreedingRules_SelectInheritedIVs(held, st, src);
                for (int x = 0; x < NUM_INHERITED_IVS; x++) {
                    if (st[x] >= STAT_MAX || src[x] >= NUM_DAYCARE_MONS) bad++;
                    countStat[st[x] < STAT_MAX ? st[x] : 0]++;
                    for (int y = x + 1; y < NUM_INHERITED_IVS; y++) {
                        if (st[x] == st[y]) dup++;
                    }
                }
                if (pa != BREEDING_NO_STAT || pb != BREEDING_NO_STAT) {
                    // forced stat is entry 0 and comes from its holder
                    int ok = (pa != BREEDING_NO_STAT && st[0] == pa && src[0] == 0) || (pb != BREEDING_NO_STAT && st[0] == pb && src[0] == 1);
                    if (!ok) srcbad++;
                    if (pa != BREEDING_NO_STAT && pb != BREEDING_NO_STAT) {
                        if (src[0] == 0) pickfirst++; else picksecond++;
                    }
                    forced0++;
                }
            }
            printf("iv %d %d dup %d bad %d forcedbad %d forced %d pickfirst %d picksecond %d\n", a, b, dup, bad, srcbad, forced0, pickfirst, picksecond);
        }
    }
    // unforced: per-stat and per-source spread
    {
        u16 held[2] = { ITEM_OTHER, ITEM_EVERSTONE };
        int cs[STAT_MAX] = { 0 }, cp[2] = { 0 };
        for (i = 0; i < n; i++) {
            u8 st[NUM_INHERITED_IVS], src[NUM_INHERITED_IVS];
            BreedingRules_SelectInheritedIVs(held, st, src);
            for (int x = 0; x < NUM_INHERITED_IVS; x++) { cs[st[x]]++; cp[src[x]]++; }
        }
        printf("ivspread");
        for (int x = 0; x < STAT_MAX; x++) printf(" %d", cs[x]);
        printf(" src %d %d\n", cp[0], cp[1]);
    }

    // --- Ability slot
    for (int ps = 0; ps < 2; ps++) {
        int same = 0;
        for (i = 0; i < n; i++) same += (BreedingRules_PickAbilitySlot(ps) == ps);
        printf("ability parentslot %d same %d of %d\n", ps, same, n);
    }

    // --- Personality constraints: Everstone nature + ability slot survive N rerolls
    {
        int natureBad = 0, slotBad = 0, plainChanged = 0, total = 0;
        for (i = 0; i < 4000; i++) {
            u32 p = mtrng() | 1;
            int nat = BREEDING_NATURE_OF(p);
            int slot = mtrng() & 1;
            u32 q = p;
            if (!BreedingRules_PersonalityMatches(q, nat, slot)) q = BreedingRules_NextPersonality(q, nat, slot);
            for (int k = 0; k < 4; k++) q = BreedingRules_NextPersonality(q, nat, slot);
            total++;
            if ((int)BREEDING_NATURE_OF(q) != nat) natureBad++;
            if ((int)(q & 1) != slot) slotBad++;
            if (BreedingRules_NextPersonality(p, -1, -1) != BREEDING_ARNG(p)) plainChanged++;
        }
        printf("personality total %d naturebad %d slotbad %d vanillaarng_changed %d\n", total, natureBad, slotBad, plainChanged);
    }

    // --- Egg moves
    {
        u16 listed[4] = { 10, 20, 30, 40 };
        u16 out[BREEDING_MAX_GATHERED_EGG_MOVES];
        u16 f1[4] = { 20, 99, 0, 0 }, m0[4] = { 0, 0, 0, 0 };
        u16 f0[4] = { 0, 0, 0, 0 }, m1[4] = { 30, 99, 0, 0 };
        u16 fb[4] = { 20, 10, 0, 0 }, mb[4] = { 20, 40, 0, 0 };
        u8 c;
        c = BreedingRules_GatherEggMoves(f1, m0, listed, 4, out);
        printf("egg father_only %d first %d\n", c, out[0]);
        c = BreedingRules_GatherEggMoves(f0, m1, listed, 4, out);
        printf("egg mother_only %d first %d\n", c, out[0]);
        c = BreedingRules_GatherEggMoves(fb, mb, listed, 4, out);
        printf("egg both %d order %d %d %d\n", c, out[0], out[1], out[2]);
        u16 same1[4] = { 10, 20, 30, 40 }, same2[4] = { 40, 30, 20, 10 };
        c = BreedingRules_GatherEggMoves(same1, same2, listed, 4, out);
        printf("egg dup %d\n", c);
        c = BreedingRules_GatherEggMoves(f0, f0, listed, 4, out);
        printf("egg none %d\n", c);
    }

    // --- Interval / hatch
    {
        int hits = 0, firstHit = -1;
        for (u32 s = 1; s <= 1024; s++) {
            if (BreedingRules_IsEggCheckStep(s)) { hits++; if (firstHit < 0) firstHit = (int)s; }
        }
        printf("interval hits_in_1024 %d first %d\n", hits, firstHit);
        printf("subtract plain %d flame %d magma %d\n", BreedingRules_EggCyclesToSubtract(ABILITY_OVERGROW), BreedingRules_EggCyclesToSubtract(ABILITY_FLAME_BODY), BreedingRules_EggCyclesToSubtract(ABILITY_MAGMA_ARMOR));
        int steps1 = 0, steps2 = 0;
        for (u32 c = 10; c > 0; steps1++) c = BreedingRules_SubtractEggCycles(c, 1);
        for (u32 c = 10; c > 0; steps2++) c = BreedingRules_SubtractEggCycles(c, 2);
        printf("hatch cycles10 plain %d accelerated %d odd5 %u\n", steps1, steps2, BreedingRules_SubtractEggCycles(1, 2));
    }
    return 0;
}
