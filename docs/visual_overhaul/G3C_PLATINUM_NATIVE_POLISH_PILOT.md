# G3C Platinum-Native Polish Pilot

Status: selected / manual pixel-art pass next

The automated cleanup audits are complete enough to define the first real native
art-polish pilot.

## Audit conclusions

- The 15 isolated-pixel files were visually reviewed. Their detached pixels are
  intentional flame, gas, heat, or silhouette details, so that pass is a no-op.
- The palette audit found no species with a globally weak luminance span.
- Exact duplicate palette colors mostly represent intentional multi-ramp/index
  structure rather than obvious visual defects.
- Lairon, Dusclops, and Glalie have crowded ramps worth visual inspection, but
  no automatic recolor is approved.
- Burmy, Wormadam, Shellos, and Gastrodon require form-routing/shiny-specific
  review before any palette change.

## First visual-polish targets

The first manual Platinum-native art pilot is:

- Pikachu
- Charizard
- Gyarados
- Snorlax
- Eevee
- Gengar
- Dragonite

Mewtwo was inspected as a control and is effectively the same underlying front
art in the HGSS reference, so it is not prioritized.

## Editing rules

For this pilot:

1. Platinum PNGs remain the source of truth.
2. HGSS may be viewed only as official visual reference.
3. Keep each source sheet at 160x80 indexed mode.
4. Keep palette indices within 0..15.
5. Do not change normal.pal, shiny.pal, or sprite_data.json in the first art pass.
6. Do not materially move the baseline or center of either 80x80 frame.
7. Prefer a handful of deliberate contour/anatomy/shading fixes over a redraw.
8. Every changed pixel must be reviewable and reversible.

## Deterministic edit tooling

`tools/visual_overhaul/apply_platinum_sprite_pixel_patch.py` applies small
coordinate/index changes from JSON manifests and verifies the expected original
pixel value before writing. This makes native polish batches auditable instead of
silently replacing complete sprite sheets.

The pilot should move species-by-species, beginning with Pikachu, and only expand
after build/export and Delta inspection remain clean.
