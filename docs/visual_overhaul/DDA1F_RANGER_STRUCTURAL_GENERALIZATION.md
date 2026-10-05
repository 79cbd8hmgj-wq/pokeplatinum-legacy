# DDA-1F — Ranger Structural Generalization Audit

The Ranger Pokémon package hypothesis has now been checked against a shape-diverse set rather than Pikachu alone.

## Species checked

| Species | Package | Compressed | Decompressed | NARC members | Graphics/cell pairs |
|---|---|---:|---:|---:|---:|
| Charizard #006 | `p006_00_LZ.bin` | 50,654 B | 117,028 B | 22 | 7 |
| Pikachu #025 | `p025_00_LZ.bin` | 6,974 B | 19,116 B | 19 | 6 |
| Gengar #094 | `p094_00_LZ.bin` | 11,928 B | 39,604 B | 19 | 6 |
| Spinarak #167 | `p167_00_LZ.bin` | 6,356 B | 18,712 B | 13 | 4 |
| Garchomp #445 | `p445_00_LZ.bin` | 35,470 B | 100,760 B | 19 | 6 |

## Shared package contract

All five checked species follow the same high-level package grammar:

```
one NCLR palette
+ one or more groups:
    <group>.cac
    <group>.NCBR  (RGCN)
    <group>.NCER  (RECN)
```

Confirmed recurring groups include:
- attack/action groups such as `a01`, `a02`, etc.;
- `s`;
- `t`;
- `w`.

The number of action groups varies by Pokémon. The renderer therefore discovers matching NCBR/NCER pairs dynamically instead of assuming a fixed group count.

## Species-specific variation

- Charizard exposes four `a0x` groups plus `s/t/w`.
- Pikachu exposes `a01/a02/p01/s/t/w`.
- Gengar exposes three `a0x` groups plus `s/t/w`.
- Spinarak exposes only `a01/s/t/w`.
- Garchomp exposes three `a0x` groups plus `s/t/w`.

This variation validates the design choice to avoid hardcoded suffix sets.

## Conclusion

The compression/archive/resource structure is now generalized across:
- small upright Pokémon;
- large winged Pokémon;
- compact/round Pokémon;
- low/wide Pokémon;
- tall/irregular Pokémon.

Therefore the correct next step is **full-pool batch rendering with exception reporting**, not manual species-by-species reverse engineering.

Any failures in the full pool should be treated as outlier package contracts and investigated separately rather than blocking the common path.
