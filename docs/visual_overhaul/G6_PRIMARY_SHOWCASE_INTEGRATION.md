# G6 — Primary Showcase Integration Audit

Status: **source-side complete / objective integration gate green**

G6 is the final holistic visual pass. It does not rebuild the G4 environments from scratch.
Instead it verifies that the environment, atmosphere, camera, lighting, texture, renderer, UI, and
battle-presentation work now coexist cleanly at the project's primary showcase locations.

The first objective integration gate covers:
1. Eterna Forest
2. Snowpoint / Route 217
3. Distortion World

A reproducible validator now lives at:

`tools/visual_overhaul/validate_g6_showcase_integration.py`

and is wired into the runtime QA workflow.

## Eterna Forest

The source contract is now explicit and cross-checked as one integrated scene:

- map header: `MAP_HEADER_ETERNA_FOREST`
- area data: `area_data_075`
- texture bank: `map_texture_set_074`
- lighting: `lighting_set_010`
- weather: `OVERWORLD_WEATHER_CANOPY`
- camera: `CAMERA_TYPE_ETERNA_FOREST`
- battle background: `BACKGROUND_FOREST`
- field renderer path: `sForestFieldEffectRenderers`
- ambience renderer: `FIELD_EFFECT_RENDERER_FOREST_AMBIENCE`

The validator also checks the authored camera profile:
- distance 545
- pitch 58 degrees
- vertical FOV 10.9 degrees
- normal near/far clipping

and the canopy-atmosphere contract:
- mist alpha 8
- fog offset `0x6F6F - 1900`
- muted forest fog `GX_RGB(20, 24, 22)`
- 0.75 camera/player scroll response

The Eterna texture bank remains geometry/index preserving. The lighting and texture isolation means
Eterna-specific grading cannot silently spill into Fullmoon/Newmoon forests.

## Snowpoint / Route 217

The primary snow-region contract is likewise checked as a single system:

- shared overworld area data: `area_data_014`
- texture bank: `map_texture_set_014`
- lighting: `lighting_set_011`
- Snowpoint weather: `OVERWORLD_WEATHER_SNOWPOINT_CITY`
- Route 217 weather: `OVERWORLD_WEATHER_BLIZZARD`
- battle background: `BACKGROUND_SNOW`

The validator checks that the snow-region lighting remains a valid full-day cycle and that the
native snow weather paths retain the authored cool fog families:
- light snow: `GX_RGB(21, 26, 31)`
- heavy snow: `GX_RGB(19, 24, 31)`
- blizzard: `GX_RGB(18, 23, 31)`

This keeps the existing weather density/behavior while ensuring the environment grade and fog
language stay aligned.

## Distortion World

The Distortion World contract is checked independently from normal overworld weather:

- area data: `area_data_074`
- texture bank: `map_texture_set_073`
- prop set: `prop_model_set_070`
- lighting: `lighting_set_009`
- battle background: `BACKGROUND_DISTORTION_WORLD`
- dedicated field renderer path: `sDistWorldFieldEffectRenderers`

The validator asserts that the lighting remains time-invariant, matching the intended surreal
presentation, and that the special fog path remains active through:
- `AREA_LIGHT_SET_DISTORTION_WORLD`
- fog color `GX_RGB(14, 8, 22)`
- fog offset `0x5000`
- `sDistortionFogDensity`

Distortion World deliberately bypasses the ordinary overworld weather manager; its environment
behavior continues through the dynamic-map feature path.

## CI hardening

The G4/G6 runtime workflow now:
- runs the showcase-integration validator on both supported revisions
- watches the camera, map-header, weather, field-renderer, area-data, and lighting sources that
  define these contracts
- retries Metroskrew installation up to three times, preventing a transient GitHub release download
  failure from masquerading as a source regression

The retry was added after a prior rev-1 runtime-symbol job failed solely because `wget` could not
download Metroskrew; the corresponding rev-0 source/runtime-symbol leg passed.

## G6 decision rule

Do not make further palette, fog, shake, or camera changes simply because G6 is a "polish" pass.

A new source edit now requires one of:
- an objective integration mismatch found by validation/runtime QA
- a rendered-frame defect visible in Delta
- a readability problem caused by two previously independent visual layers interacting badly
- a reproducible resource-contract issue

If none of those is present, the showcase is locked as-is.

## Next

After the primary showcase validator is green:
1. extend the same integration contract to Spear Pillar
2. Team Galactic interiors
3. Sinnoh lakes
4. Turnback Cave
5. close Pass G source-side work and leave only rendered-frame subjective tuning
