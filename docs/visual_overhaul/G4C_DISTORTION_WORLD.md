# G4C — Distortion World Environment

Status: review pipeline active.

The Distortion World family uses `area_data_074`, with:
- `map_texture_set_073`
- `prop_model_set_070`
- `lighting_set_009`

G4C treats the Distortion World as a single visual family. The first step exports
the map and prop texture banks so any changes can stay narrowly targeted to
materials that are visibly weak. Geometry, gravity scripting, collision, camera
behavior, and progression are outside this texture pass and remain unchanged.
