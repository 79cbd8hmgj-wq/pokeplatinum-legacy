#ifndef POKEPLATINUM_BATTLE_ANIM_OPAL_CINEMATIC_MATH_H
#define POKEPLATINUM_BATTLE_ANIM_OPAL_CINEMATIC_MATH_H

// Pure integer helpers for the Opal cinematic layer. No engine types on purpose: the same header is compiled by the
// host-side property test tools/visual_overhaul/test_opal_cinematic_math.c (run in CI) and by opal_cinematic.c.

#define OPAL_MATH_UNIT 256

// Straight-line interpolation from `start` to `end`; t is clamped to [0, d]. Exact at both ends.
static inline int OpalMath_Lerp(int start, int end, int t, int d)
{
    if (d <= 0 || t >= d) {
        return end;
    }

    if (t <= 0) {
        return start;
    }

    return start + (end - start) * t / d;
}

// Parabolic arc offset in pixels (to subtract from Y): 0 at t = 0 and t = d, `height` at the midpoint.
static inline int OpalMath_Arc(int height, int t, int d)
{
    if (d <= 0 || t <= 0 || t >= d) {
        return 0;
    }

    return height * 4 * t * (d - t) / (d * d);
}

// Smoothstep on 0..OPAL_MATH_UNIT.
static inline int OpalMath_Ease(int num, int den)
{
    if (den <= 0 || num >= den) {
        return OPAL_MATH_UNIT;
    }

    if (num <= 0) {
        return 0;
    }

    int t = num * OPAL_MATH_UNIT / den;
    return t * t * (3 * OPAL_MATH_UNIT - 2 * t) / (OPAL_MATH_UNIT * OPAL_MATH_UNIT);
}

// Camera weight for frame `frame` of a cue. PAN: 0 -> UNIT -> hold -> 0. PUNCH: alternating sign with linearly decaying amplitude.
// Returns a value in [-UNIT, UNIT]; for frame >= total the result is exactly 0 so the caller restores its snapshot.
static inline int OpalMath_CameraWeight(int punch, int frame, int inFrames, int holdFrames, int outFrames)
{
    int total = inFrames + holdFrames + outFrames;

    if (frame >= total || total <= 0) {
        return 0;
    }

    if (punch) {
        int remaining = total - frame;
        int sign = (frame & 1) ? -1 : 1;
        return sign * OPAL_MATH_UNIT * remaining / total;
    }

    if (frame < inFrames) {
        return OpalMath_Ease(frame + 1, inFrames);
    }

    if (frame < inFrames + holdFrames) {
        return OPAL_MATH_UNIT;
    }

    return OPAL_MATH_UNIT - OpalMath_Ease(frame - inFrames - holdFrames + 1, outFrames);
}

// Clamp helper used for camera amplitudes.
static inline int OpalMath_Clamp(int value, int limit)
{
    if (value > limit) {
        return limit;
    }

    if (value < -limit) {
        return -limit;
    }

    return value;
}

// Scale in percent for an FX instance `local` frames into its life (duration frames long). popThird/shrinkThird: flag bits already tested by the caller.
static inline int OpalMath_FxScalePercent(int basePercent, int local, int duration, int pop, int shrink)
{
    int pct = basePercent;
    int third = duration / 3;

    if (pop && local < third) {
        if (local < 0) {
            local = 0;
        }

        pct = pct * (40 + 60 * local / (third + 1)) / 100;
    } else if (shrink && local > duration * 2 / 3) {
        int remaining = duration - local;
        if (remaining < 0) {
            remaining = 0;
        }

        pct = pct * (40 + 60 * remaining / (third + 1)) / 100;
    }

    return pct < 1 ? 1 : pct;
}

#endif // POKEPLATINUM_BATTLE_ANIM_OPAL_CINEMATIC_MATH_H
