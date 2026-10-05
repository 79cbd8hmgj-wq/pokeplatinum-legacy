# Ranger Sprite Tooling Rebuild

## Rebuild status

The lost Ranger batch tooling has now been reconstructed in-repo instead of being left as chat-only state.

Added:

- `tools/visual_overhaul/ranger_package.py`
- `tools/visual_overhaul/render_ranger_pokemon_batch.py`
- `tools/visual_overhaul/audit_ranger_render_compatibility.py`

### What is restored now

The batch layer can:

- discover all `p###_##_LZ.bin` Ranger Pokémon packages;
- preserve package variants;
- decompress Nintendo DS LZ10;
- extract NARC members;
- recover flat FNTB filenames when present;
- classify `.cac`, NCLR, NCBR, and NCER resources without hard-coded Pikachu suffixes;
- continue after per-package failures;
- emit deterministic JSON manifests;
- optionally invoke a Ranger cell-rendering backend per package.

The compatibility auditor can:

- consume backend render candidates;
- measure nontransparent bounding boxes;
- record native canvas size and opaque-pixel counts;
- calculate width/height/max-axis ratios against Platinum's 80x80 target;
- classify candidates as `fits_small`, `fits`, `geometry_close`, or `oversize`;
- emit JSON plus a compact Markdown report.

## Important boundary

The lower-level Ranger `.cac`/NCER cell-composition decoder is **not being guessed**.

The recovered prior work said a generalized renderer existed, but the implementation was not committed. The rebuilt batch tool therefore uses an explicit backend contract rather than fabricating undocumented Ranger cell semantics.

That leaves one concrete implementation task before the complete visual census can run:

> reconstruct the single-package Ranger cell renderer backend from the extracted `.cac` + NCBR + NCER + shared NCLR resources.

## Next execution

1. Run the structural census over all 296 real Ranger packages.
2. Use the resulting extracted resource layouts to reconstruct/validate the cell backend against the five-species regression fixture:
   - Charizard #006
   - Pikachu #025
   - Gengar #094
   - Spinarak #167
   - Garchomp #445
3. Run the full render census.
4. Run the 80x80 compatibility auditor.
5. Commit both manifests/reports before defining any automatic resize/anchor policy.
