// Host-side property test for include/battle_anim/opal_cinematic_math.h (compiled and run by the Opal CI workflow).
// Proves the camera/FX math that decides "everything is restored": exact zero at the end of every cue, bounded weights,
// exact endpoints for travel, zero arc at the endpoints, and scale never reaching 0.
#include <stdio.h>
#include <stdlib.h>

#include "battle_anim/opal_cinematic_math.h"

#define CHECK(cond, ...)                                  \
    do {                                                  \
        if (!(cond)) {                                    \
            fprintf(stderr, "FAIL %s:%d: ", __FILE__, __LINE__); \
            fprintf(stderr, __VA_ARGS__);                 \
            fprintf(stderr, "\n");                        \
            exit(1);                                      \
        }                                                 \
    } while (0)

int main(void)
{
    long cases = 0;

    // Camera: every legal cue (in/out >= 1, total <= 90) for PAN and PUNCH
    for (int punch = 0; punch <= 1; punch++) {
        for (int in = 1; in <= 30; in++) {
            for (int hold = 0; hold <= 30; hold += 3) {
                for (int out = 1; out <= 30; out++) {
                    if (in + hold + out > 90) {
                        continue;
                    }

                    int total = in + hold + out;
                    int prev = 0;
                    for (int f = 0; f < total + 5; f++) {
                        int w = OpalMath_CameraWeight(punch, f, in, hold, out);
                        CHECK(w >= -OPAL_MATH_UNIT && w <= OPAL_MATH_UNIT, "weight %d out of range", w);
                        if (f >= total) {
                            CHECK(w == 0, "weight must be exactly 0 after the cue (punch=%d in=%d hold=%d out=%d f=%d)", punch, in, hold, out, f);
                        }

                        if (!punch) {
                            CHECK(w >= 0, "pan weight negative");
                            if (f < in) {
                                CHECK(w >= prev, "pan ease-in not monotonic");
                            }
                        }

                        prev = w;
                        cases++;
                    }

                    if (!punch) {
                        CHECK(OpalMath_CameraWeight(0, in - 1, in, hold, out) == OPAL_MATH_UNIT, "pan must reach full amplitude");
                    }
                }
            }
        }
    }

    // Travel: exact endpoints, monotonic along straight lines, arc zero at the ends
    for (int d = 1; d <= 90; d++) {
        for (int s = -40; s <= 280; s += 40) {
            for (int e = -40; e <= 280; e += 40) {
                CHECK(OpalMath_Lerp(s, e, 0, d) == s, "lerp start");
                CHECK(OpalMath_Lerp(s, e, d, d) == e, "lerp end");
                CHECK(OpalMath_Lerp(s, e, d + 7, d) == e, "lerp clamps past the end");
                CHECK(OpalMath_Lerp(s, e, -3, d) == s, "lerp clamps before the start");
                int lo = s < e ? s : e;
                int hi = s < e ? e : s;
                for (int t = 0; t <= d; t++) {
                    int v = OpalMath_Lerp(s, e, t, d);
                    CHECK(v >= lo && v <= hi, "lerp left the segment");
                    cases++;
                }
            }
        }

        CHECK(OpalMath_Arc(24, 0, d) == 0 && OpalMath_Arc(24, d, d) == 0, "arc must vanish at both ends (d=%d)", d);
        for (int t = 0; t <= d; t++) {
            int a = OpalMath_Arc(24, t, d);
            CHECK(a >= 0 && a <= 24, "arc out of range");
        }
    }

    // FX scale: never below 1 percent, pop/shrink bounded by the base, plain scale untouched
    for (int base = 20; base <= 400; base += 20) {
        for (int duration = 1; duration <= 180; duration += 7) {
            for (int local = -9; local <= duration + 9; local++) {
                for (int flags = 0; flags < 4; flags++) {
                    int pct = OpalMath_FxScalePercent(base, local, duration, flags & 1, flags & 2);
                    CHECK(pct >= 1 && pct <= base, "scale %d outside [1,%d]", pct, base);
                    if (flags == 0) {
                        CHECK(pct == base, "plain scale must not change");
                    }

                    cases++;
                }
            }
        }
    }

    CHECK(OpalMath_Clamp(99, 12) == 12 && OpalMath_Clamp(-99, 12) == -12 && OpalMath_Clamp(5, 12) == 5, "clamp");
    printf("PASS: opal_cinematic_math properties hold over %ld cases\n", cases);
    return 0;
}
