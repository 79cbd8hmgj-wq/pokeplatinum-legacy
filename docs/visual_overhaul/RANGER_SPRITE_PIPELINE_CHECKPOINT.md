# Ranger Sprite Pipeline Checkpoint

## Status

This file is the persistent checkpoint for the Pokémon Ranger -> Pokémon Platinum sprite-donor investigation.

The renderer work preceding this checkpoint established that the Ranger Pokémon package renderer is no longer Pikachu-specific. Structural validation was performed against a deliberately varied sample:

- Charizard #006
- Pikachu #025
- Gengar #094
- Spinarak #167
- Garchomp #445

The generalized renderer is expected to discover variable resource groups dynamically rather than assume one fixed suffix layout.

The next real execution step is the full Ranger `poke/` batch render followed by the Platinum battle-sprite geometry audit. Do not design global resize or placement rules before that census exists.

## Verified Ranger corpus

Source repository:

`79cbd8hmgj-wq/pokeranger2`

Source directory:

`res/prebuilt/data/poke/`

Verified package inventory from the repository tree:

- 297 total `p###_##_LZ.bin` package files including `p000`
- 296 real Pokémon/form package files after excluding `p000`
- 282 unique real National Dex species represented
- approximately 5.49 MB total compressed package data including `p000`

Unique represented species by generation:

- Generation I: 78
- Generation II: 43
- Generation III: 60
- Generation IV: 101

Package-file counts including alternate variants:

- Generation I: 79
- Generation II: 43
- Generation III: 60
- Generation IV: 114

## Multi-variant packages

Twelve National Dex IDs have more than one Ranger package and therefore prove that the batch renderer must preserve package variants rather than assume one package per species.

| Dex | Variants |
|---:|---|
| 006 | 00, 01 |
| 412 | 00, 01, 02 |
| 413 | 00, 01, 02 |
| 421 | 00, 01 |
| 422 | 00, 01 |
| 423 | 00, 01 |
| 447 | 00, 01 |
| 448 | 00, 01 |
| 485 | 00, 01 |
| 488 | 00, 01 |
| 490 | 00, 01 |
| 491 | 00, 01 |

## Immediate execution target

Run the generalized Ranger batch renderer over all 296 real package files under:

`res/prebuilt/data/poke/`

Expected prior tooling:

- `render_ranger_pokemon_batch.py`
- `audit_ranger_render_compatibility.py`

The batch renderer should:

1. discover package/group structure dynamically;
2. preserve every package variant;
3. render every valid cell/group;
4. continue after per-package failures;
5. emit a machine-readable manifest;
6. record failed packages with reasons instead of aborting the entire run.

Then run the compatibility auditor against Platinum's 80x80 battle-sprite geometry using the existing classification vocabulary:

- `fits_small`
- `fits`
- `geometry_close`
- `oversize`

## Current boundary

The corpus inventory above is verified.

The 296-package full render is **not yet claimed complete** at this checkpoint. The next checkpoint must record the actual batch-render results: success count, failure count, rendered candidate count, variant preservation, and compatibility-class distribution.

## Workflow rule

Future Ranger/visual-overhaul investigation checkpoints and material progress should be committed to this repository rather than left only in chat.
