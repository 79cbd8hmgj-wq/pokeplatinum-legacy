# Ranger Tooling Recovery

## Correction

The Ranger renderer tooling was not actually lost.

While reconstructing it, an open feature branch was found:

- branch: `feature/ds-donor-asset-framework`
- pull request: **#62 — Add DS donor asset compatibility framework**

That branch already contained the original Ranger decoder/render pipeline and the DDA-1A through DDA-1F documentation.

The temporary reconstruction has therefore been removed and the original implementation has been recovered onto `main`.

## Recovered tools

- `tools/visual_overhaul/nitro_narc.py`
- `tools/visual_overhaul/inspect_ranger_assets.py`
- `tools/visual_overhaul/render_ranger_nitro_preview.py`
- `tools/visual_overhaul/render_ranger_ncer_preview.py`
- `tools/visual_overhaul/render_ranger_pokemon_package.py`
- `tools/visual_overhaul/render_ranger_pokemon_batch.py`
- `tools/visual_overhaul/audit_ranger_render_compatibility.py`

## Recovered documentation

- `DDA1_RANGER_DECODER_FOUNDATION.md`
- `DDA1A_RANGER_PIKACHU_PACKAGE_MAP.md`
- `DDA1B_RANGER_RAW_PREVIEW_RENDERER.md`
- `DDA1C_RANGER_NCER_CELL_RENDERER.md`
- `DDA1D_RANGER_PACKAGE_RENDERER.md`
- `DDA1E_RANGER_BATCH_RENDERER.md`
- `DDA1F_RANGER_STRUCTURAL_GENERALIZATION.md`

## Verified pre-census state

The original DDA-1F checkpoint had already validated the generalized pipeline on:

- Charizard #006
- Pikachu #025
- Gengar #094
- Spinarak #167
- Garchomp #445

The original single-package renderer already implements:

`LZ10 -> NARC -> named members -> shared NCLR + NCBR/RGCN + NCER -> rendered PNG cells`

The batch renderer dynamically discovers graphics/cell pairs and preserves Ranger package variants.

## Active next step

A GitHub Actions census now runs the original renderer against the complete `pokeranger2` Pokémon donor pool and commits:

- `RANGER_FULL_RENDER_CENSUS.json`
- `RANGER_FULL_RENDER_CENSUS.md`
- `RANGER_RENDER_COMPATIBILITY.json`
- `RANGER_RENDER_COMPATIBILITY.md`

Rendered PNG cells are retained as an Actions artifact for visual QA rather than committed wholesale.

The full-corpus results, not provisional assumptions, will drive the next resize/anchor and candidate-selection work.
