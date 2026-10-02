# G3C Native Isolated-Pixel Review

Status: reviewed / no-op

The first low-risk native cleanup pass inspected all 15 Platinum battle-sprite
files flagged for isolated opaque pixels.

The detector is useful, but this batch did **not** reveal accidental garbage
pixels. The flagged pixels are part of intentional sprite effects or silhouette
details and are retained.

## Reviewed candidates

- Charmander front (female/male): detached flame detail in animation frame 1 — retain.
- Charmeleon front (female/male): detached tail-flame particles/details — retain.
- Charizard front (female/male): detached flame detail near the tail flame — retain.
- Weedle back (female/male): intentional small silhouette/detail pixel — retain.
- Gloom front (female/male): intentional low silhouette/detail pixel in frame 1 — retain.
- Gastly back (female/male): detached gaseous aura particles — retain.
- Moltres front: detached flame particles — retain.
- Magcargo front (female/male): detached flame/heat details — retain.

## Conclusion

No native sprite is changed by the isolated-pixel pass.

This is an important guardrail for G3C: automated structural signals are used to
find review targets, not to erase stylistic pixels automatically.

The next native optimization pass moves to palette/readability analysis, where
we can identify exact duplicate colors, near-duplicate ramps, weak luminance
separation, and unused palette capacity without disturbing Platinum animation
geometry.
