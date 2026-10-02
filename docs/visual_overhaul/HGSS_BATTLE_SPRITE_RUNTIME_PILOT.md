# G3 HGSS Battle Sprite Runtime Pilot

Pinned donor: `pret/pokeheartgold@9d8b7591f09b65804da2fb2dfd56f320633e0d36`

This pilot is intentionally small. It includes only species that passed both:

1. the conservative two-frame geometry triage; and
2. the Platinum palette/index contract audit.

## Pilot species

- Venusaur
- Persian
- Hypno
- Lapras
- Tyranitar

For each species, only the HGSS **front** sprite source is replaced. Both male and
female source paths are updated where Platinum exposes them.

## Explicitly preserved

- Platinum `normal.pal`
- Platinum `shiny.pal`
- Platinum `sprite_data.json`
- back sprites
- gender/file archive ordering
- NARC structure and member IDs
- battle engine code

The selected donor PNGs are direct-index-safe: every non-transparent palette index
used by the HGSS art resolves to the same RGB color at the same index in Platinum's
normal palette. No palette remapping is applied.

## Runtime validation checklist

Each pilot species must be checked in Delta before the donor class is expanded:

- normal-color front sprite renders correctly
- shiny front sprite renders correctly
- entry animation completes without clipping or frame jumps
- idle frame transition remains coherent
- Y placement relative to the battle platform remains acceptable
- no left/right cropping
- gender-specific path still resolves correctly where applicable
- enemy/front presentation remains visually stable through common battle effects

## Lock rule

Do not expand the 28-species direct-index-safe pool until this five-species pilot
has passed runtime inspection. Compile/export success validates the resource
contract, but not animation presentation.
