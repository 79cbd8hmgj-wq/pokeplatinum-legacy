# G4B — Snow Region Environment Reconstruction

Status: source-applied; runtime inspection pending.

This pass covers the shared snowy overworld family driven by `area_data_014`:
Snowpoint City, Routes 216/217, Acuity Lakefront/Lake Acuity, and the snowy Mt.
Coronet exterior maps.

## Lighting isolation

The region previously used shared `lighting_set_005`. G4B clones it to
`lighting_set_011` and points `area_data_014` at the new set so the snow
region can be tuned without changing unrelated maps that may also use the
original lighting bank.

## Snow grade

Daytime keyframes retain Platinum's timing and light directions, with a small
cold-weather grade:

- +1 blue to the primary light
- +1 blue to diffuse, ambient, and specular light
- -1 red from diffuse light

Dawn/night and the warm late-evening transition are left intact. This keeps
Snowpoint and Route 217 recognizably Platinum while making snow/ice read cleaner
and colder.

## Texture review

`map_texture_set_014` was exported and reviewed before source changes. The
snow/ice art already has useful blue/lavender shadow ramps and readable rock,
tree, and terrain silhouettes, so G4B deliberately does not replace texture
geometry merely to create churn.

The visible environment change in this batch is therefore lighting-led. Texture
replacement remains available later if runtime review identifies a specific weak
material.
