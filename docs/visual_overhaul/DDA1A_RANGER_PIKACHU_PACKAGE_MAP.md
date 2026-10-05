# DDA-1A — Ranger Pikachu Package Map

The first concrete Pokémon donor package has now been mapped from Pokémon Ranger: Shadows of Almia.

## Source packages

- `res/prebuilt/data/poke/p025_00_LZ.bin`
- `res/prebuilt/data/pokeOBJ/bp025_LZ.bin`

Both are Nintendo DS LZ10 streams whose decompressed payload is a NARC archive.

## Main Pikachu package

`p025_00_LZ.bin` decompresses to a 19-member NARC.

Recovered member names:

| Index | Member | Kind | Size |
|---:|---|---|---:|
| 0 | `p025_00.NCLR` | palette | 72 |
| 1 | `p025_00_a01.cac` | Ranger metadata/animation companion | 108 |
| 2 | `p025_00_a01.NCBR` | Nitro character graphics (RGCN) | 2096 |
| 3 | `p025_00_a01.NCER` | Nitro cell data | 336 |
| 4 | `p025_00_a02.cac` | Ranger metadata/animation companion | 268 |
| 5 | `p025_00_a02.NCBR` | Nitro character graphics (RGCN) | 2096 |
| 6 | `p025_00_a02.NCER` | Nitro cell data | 336 |
| 7 | `p025_00_p01.cac` | Ranger metadata/animation companion | 140 |
| 8 | `p025_00_p01.NCBR` | Nitro character graphics (RGCN) | 1072 |
| 9 | `p025_00_p01.NCER` | Nitro cell data | 232 |
| 10 | `p025_00_s.cac` | Ranger metadata/animation companion | 140 |
| 11 | `p025_00_s.NCBR` | Nitro character graphics (RGCN) | 4144 |
| 12 | `p025_00_s.NCER` | Nitro cell data | 488 |
| 13 | `p025_00_t.cac` | Ranger metadata/animation companion | 108 |
| 14 | `p025_00_t.NCBR` | Nitro character graphics (RGCN) | 2096 |
| 15 | `p025_00_t.NCER` | Nitro cell data | 336 |
| 16 | `p025_00_w.cac` | Ranger metadata/animation companion | 108 |
| 17 | `p025_00_w.NCBR` | Nitro character graphics (RGCN) | 4144 |
| 18 | `p025_00_w.NCER` | Nitro cell data | 296 |

The important result is that the core visual members are already standard Nitro resources:
- NCLR palette
- RGCN character graphics
- NCER cell data

The only still-opaque part of this package family is the small `.cac` companion metadata.

## Pikachu object package

`bp025_LZ.bin` decompresses to a 4-member NARC:

| Index | Member | Kind | Size |
|---:|---|---|---:|
| 0 | `bp025.cac` | Ranger metadata/animation companion | 20 |
| 1 | `bp025.NCER` | Nitro cell data | 99 |
| 2 | `bp025.NCGR` | Nitro character graphics | 560 |
| 3 | `bp025.NCLR` | palette | 72 |

This package is even closer to a normal Nitro sprite bundle.

## Consequence

Ranger Pokémon resources are now much less exotic than they initially appeared.

The practical conversion path is:

```
Ranger *_LZ.bin
    ↓ LZ10
NARC
    ↓
NCLR + NCGR/NCBR + NCER + optional CAC
    ↓
rendered Ranger sprite/cell preview
    ↓
Platinum target comparison
```

No custom Ranger graphics decoder should be written for standard NCLR/RGCN/NCER members. Existing Nitro decoding should be reused.

## Tooling update

`inspect_ranger_assets.py` now supports:

```sh
--extract-dir PATH
```

When supplied, NARC members are written to an external output directory using their recovered BTNF filenames. This keeps raw donor files outside the Platinum repository while making local preview/render work straightforward.

Example:

```sh
python3 tools/visual_overhaul/inspect_ranger_assets.py \
  --ranger-root ../pokeranger2 \
  --asset-root poke \
  --limit 1 \
  --extract-dir /tmp/ranger_extract \
  --write-json /tmp/ranger_pikachu.json
```

## Next gate

The next Ranger task is not decompression anymore. It is **rendering**:

1. decode the 72-byte NCLR palette;
2. decode the RGCN/NCBR pixel data;
3. apply NCER cell geometry;
4. generate a PNG contact sheet for the five Pikachu visual groups;
5. determine which group(s) are useful as Platinum donor art;
6. only then attempt a Platinum conversion pilot.
