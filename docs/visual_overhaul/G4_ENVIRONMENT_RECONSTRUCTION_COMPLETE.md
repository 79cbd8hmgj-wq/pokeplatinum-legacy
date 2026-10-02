# G4 — Environment Reconstruction Completion

Status: **SOURCE PASS COMPLETE / RUNTIME QA PENDING**

G4 is complete at the resource-safe level supported by the current Platinum
source tree. The pass focused on high-value environment families and preserved
gameplay geometry.

## Implemented environment work

- **G4A Eterna Forest**
  - isolated Eterna from shared area/texture resources
  - dedicated forest lighting
  - native ground/underbrush palette grade
  - texture dimensions and indexed texel maps preserved

- **G4B Snowpoint / Routes 216–217 / Acuity**
  - dedicated snow-region lighting
  - restrained snow-biome vegetation grade
  - snow/ice, weather behavior, geometry, and collision preserved

- **G4C Distortion World**
  - reviewed map and prop texture banks
  - refined harsh electric-blue/hot-magenta accents
  - both map and prop texel maps preserved
  - gravity/camera/scripts/progression untouched

- **G4D Spear Pillar**
  - dedicated high-altitude lighting
  - ancient stone palette cooled away from the retail yellow cast
  - native summit geometry preserved

- **G4E Sinnoh lakes**
  - dedicated lake-family daylight treatment
  - vegetation fluorescence reduced
  - lake water slightly deepened
  - shoreline/map geometry preserved

- **G4F Turnback Cave**
  - isolated from shared Solaceon/Celestic area resources
  - dedicated darker/cooler cave lighting
  - texture bank intentionally left pixel/palette-identical because special
    bright entries may be material/key colors

- **G4G Team Galactic interiors**
  - reviewed HQ, laboratory, and warehouse texture families
  - closed as a deliberate no-op because the HQ/lab presentation is already
    coherent and the warehouse materials are shared/generic

## G4 invariants

Across implemented G4 texture changes:
- no map collision was changed
- no scripts/warps/encounters/progression were changed
- no texture dimensions were changed
- no indexed texel maps were changed
- resource names/order were preserved
- changes are palette/lighting/resource-isolation work only

## Selective model-upgrade boundary

The remaining environment geometry is stored as compiled/binary Nitro model and
map data (for example `.nsbmd` prop models and `map_data_*.bin`). The current
repo has a reproducible NSBTX texture/palette pipeline, but no equivalent
source-authoring/round-trip pipeline for safely editing NSBMD/map geometry.

The available project NDS/ROM toolkits do not surface an NSBMD geometry authoring
tool by filename either.

Therefore **selective model upgrades are the G4 blocker**. They are deferred
rather than hex-editing opaque geometry and risking collision/material/model
breakage.

## Exit condition

G4 is considered source-complete for the current safe toolchain. Remaining work
is runtime visual inspection in Delta plus any future model work if a proven
NSBMD/map-geometry authoring pipeline becomes available.

Next visual phase: **G5 — Battle Presentation**.
