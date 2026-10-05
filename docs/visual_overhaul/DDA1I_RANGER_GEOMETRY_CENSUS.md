# DDA-1I — Ranger Geometry Census

## Full-render validation

The generalized Ranger renderer has now been exercised against the complete real
Pokémon donor pool.

- Real Pokémon/form packages: **296**
- Successful real packages: **296**
- Rendered NCER cells: **35,806**
- The only package that failed in the earlier 297-package run was p000_00_LZ.bin,
  which is not a real National Dex species and is now excluded from Pokémon census
  runs by default.

This closes the structural-generalization question for the currently available
Ranger Pokémon pool.

## Geometry methodology revision

The first compatibility census classified cells from their raw rendered canvas
dimensions and produced:

- fits_small: 26,163
- fits: 9,218
- geometry_close: 349
- oversize: 76

That is useful as a first pass but raw OAM canvas dimensions can include transparent
margin. DDA-1I therefore tightens the measurement contract:

> Compatibility is measured from the nontransparent pixel bounding box.

The revised auditor records:

- raw canvas width/height;
- occupied bounding box;
- occupied width/height;
- opaque pixel count;
- width/height/max-axis ratios versus Platinum's 80x80 cell;
- compatibility class;
- per-species class distribution.

## Policy

Do not derive automatic resize or anchor rules from raw canvas dimensions.

The opaque-bbox census is the authoritative geometry input for the next stage.

## Next stage

After the revised census is committed:

1. identify direct-fit candidate cells;
2. rank candidate groups/cells per species without assuming a01 is semantically
   the correct battle pose;
3. generate contact-sheet QA for representative candidates;
4. inspect group semantics before locking a preferred Ranger pose;
5. only then design Platinum 80x80 placement/scaling transforms.
