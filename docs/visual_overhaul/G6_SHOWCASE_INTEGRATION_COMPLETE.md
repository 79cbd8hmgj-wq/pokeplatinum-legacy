# G6 — Showcase Integration Completion

Status: **SOURCE-SIDE COMPLETE / DELTA VISUAL REVIEW REMAINS**

G6 closes the source-side visual integration pass by validating the project's showcase environments
as complete systems rather than as isolated palette, lighting, camera, weather, or renderer edits.

## Objective showcase gate

The canonical validator is:

`tools/visual_overhaul/validate_g6_showcase_integration.py`

It now covers every G6 showcase family:

### Primary benchmarks
- Eterna Forest
- Snowpoint / Route 217
- Distortion World

### Secondary benchmarks
- Spear Pillar
- Sinnoh lakes
- Turnback Cave
- Team Galactic interiors

For each family, the validator cross-checks the relevant map-header routing, area-data record,
texture bank, lighting set, weather/camera/background contract, and any special renderer/fog path
that gives the scene its identity.

## Primary benchmark results

### Eterna Forest
Locked integration:
- `area_data_075`
- `map_texture_set_074`
- `lighting_set_010`
- `OVERWORLD_WEATHER_CANOPY`
- `CAMERA_TYPE_ETERNA_FOREST`
- `BACKGROUND_FOREST`
- deep-forest renderer routing
- forest ambience renderer
- canopy mist/fog constants

The dedicated resource namespace prevents the Eterna grade from leaking into the other forest maps.

### Snowpoint / Route 217
Locked integration:
- `area_data_014`
- `map_texture_set_014`
- `lighting_set_011`
- Snowpoint seasonal snow weather
- Route 217 blizzard weather
- `BACKGROUND_SNOW`
- cool snow/heavy-snow/blizzard atmosphere constants

The existing snow systems are retained; G6 verifies that the environment grade and weather language
remain coherent rather than replacing native weather behavior.

### Distortion World
Locked integration:
- `area_data_074`
- `map_texture_set_073`
- `prop_model_set_070`
- `lighting_set_009`
- `BACKGROUND_DISTORTION_WORLD`
- Distortion World field-renderer path
- Distortion-specific fog path

The lighting is asserted to remain time-invariant and the area stays on its dedicated dynamic-map
feature path rather than normal overworld weather.

## Secondary benchmark results

### Spear Pillar
Locked integration:
- `area_data_060`
- `map_texture_set_059`
- `lighting_set_012`
- `CAMERA_TYPE_SPEAR_PILLAR`
- `BACKGROUND_MOUNTAIN`
- Spear Pillar graded area-light/fog path

### Sinnoh lakes
Locked integration:
- `area_data_062`
- `map_texture_set_061`
- `lighting_set_013`
- zoomed-in lake camera
- forest battle background family
- dedicated lake area-light identity

### Turnback Cave
Locked integration:
- `area_data_076`
- `map_texture_set_075`
- `lighting_set_014`
- native fog weather
- cave battle background

The texture bank remains intentionally conservative because the unusual bright entries include
special-purpose material/key colors; G6 preserves the earlier no-op decision rather than risking a
blind recolor.

### Team Galactic interiors
Locked integration:
- main Eterna/HQ family on `area_data_058` / `map_texture_set_057`
- warehouse isolated on `area_data_077` / `map_texture_set_076`
- orthographic interior camera
- indoor battle background family
- grade report must retain non-empty main/lab/warehouse palette and rendered-texture changes

## CI result

The G6 showcase contract now runs before external build-tool downloads in the runtime workflow, so
source-integration regressions fail fast.

The gate is green on both US revision matrix legs at the current source checkpoint.

The runtime workflow also retries the Metroskrew download up to three times. This addresses the
previous rev-1 failure that was caused by a transient external `wget` failure rather than by the ROM
source.

## Source-side exit condition

G6 source expansion is closed unless one of the following produces a specific defect:

1. Delta rendered-frame review
2. objective runtime probe failure
3. readability conflict between two completed visual systems
4. reproducible resource-contract regression

Absent one of those findings, additional palette/camera/fog/effect changes would be churn rather
than evidence-based polish.

## Remaining manual Delta review

The final subjective review should check these scenes in actual Delta rendering:

- Eterna Forest: canopy density, player readability, ambience frequency, camera framing
- Snowpoint: snow/terrain separation in daylight and evening
- Route 217: visibility under blizzard conditions
- Distortion World: dark-value separation and magenta/blue restraint
- Spear Pillar: summit silhouette/readability against fog
- lakes: shoreline/water separation
- Turnback Cave: fog visibility without flattening cave depth
- Galactic interiors: cool industrial grade without losing floor/wall/object separation

Battle presentation should receive a separate short spot-check for the G5 move-impact and scene-grade
work, but no more source changes are required unless Delta reveals a concrete issue.

## Next phase

Pass G is now source-side complete. The remaining work is validation/polish:
- finish CI on the current branch
- perform the Delta rendered-frame sanity review
- fix only observed defects
- merge the visual-overhaul branch when those checks are satisfactory
