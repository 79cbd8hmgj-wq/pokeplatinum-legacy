# G4A — Eterna Forest Environment Reconstruction

Status: first implementation batch

G4 begins with Eterna Forest as the environment quality benchmark.

## Batch 1: forest-specific lighting

Eterna Forest previously used the shared `lighting_set_004`. This batch gives
the area its own `lighting_set_010`, cloned from the original timing/direction
data and conservatively graded for a denser forest presentation.

The new set preserves:
- every time-of-day keyframe
- every light enable/disable state
- every light direction
- all map geometry, collision, props, textures, scripts, and encounters

Daylight keyframes receive only a small color-grade adjustment:
- slightly greener key and diffuse light
- slightly reduced blue/red in diffuse and ambient light
- a small green lift in specular light

Night/dawn lighting remains the original Platinum data.

This deliberately isolates the first G4 change to Eterna Forest instead of
changing a shared lighting bank used elsewhere.

## Next G4A batch

After build/runtime confirmation, continue on the same area with the actual
environment assets:
1. inspect `map_texture_set_053`
2. identify foliage/ground/water materials used by Eterna Forest
3. use HGSS forest assets as reference/donor only where format/material mapping
   is safe
4. replace or recolor only the specific Eterna-facing textures that materially
   improve the scene
5. leave map collision and progression geometry unchanged
