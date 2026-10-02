# G6 — Secondary Showcase Integration Audit

Status: **objective source contracts wired**

The second G6 integration gate extends the same source-level consistency checks used for Eterna,
Snowpoint/Route 217, and Distortion World to the remaining showcase environments.

The shared validator is:

`tools/visual_overhaul/validate_g6_showcase_integration.py`

## Spear Pillar

Validated contract:
- map header: `MAP_HEADER_SPEAR_PILLAR`
- area data: `area_data_060`
- texture bank: `map_texture_set_059`
- prop set: `prop_model_set_056`
- lighting: `lighting_set_012`
- camera: `CAMERA_TYPE_SPEAR_PILLAR`
- battle background: `BACKGROUND_MOUNTAIN`
- weather: `OVERWORLD_WEATHER_CLEAR_13`

The special-fog integration is also asserted:
- `AREA_LIGHT_SET_SPEAR_PILLAR_GRADE`
- fog color `GX_RGB(16, 18, 22)`
- fog offset `0x6000`
- `sSpearPillarFogDensity`

This keeps the high-altitude lighting grade and fog path coupled without changing summit geometry,
legendary scripts, or camera logic.

## Sinnoh lakes

Representative Lake Verity integration is checked through:
- area data: `area_data_062`
- texture bank: `map_texture_set_061`
- prop set: `prop_model_set_058`
- lighting: `lighting_set_013`
- camera: `CAMERA_TYPE_ZOOMED_IN`
- battle background: `BACKGROUND_FOREST`

The validator also asserts the dedicated `AREA_LIGHT_SET_SINNOH_LAKES` family remains registered.

## Turnback Cave

Validated contract:
- map header: `MAP_HEADER_TURNBACK_CAVE_ENTRANCE`
- area data: `area_data_076`
- texture bank: `map_texture_set_075`
- prop set: `prop_model_set_052`
- lighting: `lighting_set_014`
- weather: `OVERWORLD_WEATHER_FOG`
- battle background: `BACKGROUND_CAVE_3`

This preserves the deliberate G4F restraint decision: Turnback receives isolated cooler/darker
lighting, but its texture bank remains otherwise conservative because several conspicuous palette
entries are likely special-purpose/key colors.

## Team Galactic interiors

Two representative contracts are checked:

### Eterna Galactic Building / main Galactic family
- area data: `area_data_058`
- texture bank: `map_texture_set_057`
- prop set: `prop_model_set_054`
- lighting: `lighting_set_006`
- interior orthographic camera
- `BACKGROUND_INDOORS_2`

### Veilstone Galactic Warehouse
- area data: `area_data_077`
- texture bank: `map_texture_set_076`
- prop set: `prop_model_set_027`
- lighting: retail `lighting_set_001`
- interior orthographic camera
- `BACKGROUND_INDOORS_2`

The Galactic grade report is part of the gate. The validator requires non-empty changed-palette and
visual-texture sets for the main, laboratory, and warehouse families so a missing/regenerated no-op
asset cannot silently pass.

## G6 integration state

The showcase validator now covers all locations named by the Pass G plan:
- Eterna Forest
- Snowpoint / Route 217
- Distortion World
- Spear Pillar
- Sinnoh lakes
- Turnback Cave
- Team Galactic interiors

At this point, new G6 source edits should be driven by validator/runtime failures or by concrete
rendered-frame defects. There is no justification for another broad palette or camera sweep solely
for novelty.
