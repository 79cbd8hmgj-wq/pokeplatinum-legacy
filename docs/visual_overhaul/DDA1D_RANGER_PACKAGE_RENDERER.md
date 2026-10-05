# DDA-1D — One-command Ranger Pokémon renderer

The Ranger donor path now has a single command that takes an original compressed Pokémon package and produces individual PNG cells.

## Pipeline

```
p025_00_LZ.bin
  -> LZ10
  -> NARC
  -> recovered named members
  -> shared NCLR
  -> each matching NCBR/NCGR + NCER pair
  -> transparent indexed PNG cells
```

Tool:

`tools/visual_overhaul/render_ranger_pokemon_package.py`

Example:

```sh
python3 tools/visual_overhaul/render_ranger_pokemon_package.py \
  --package ../pokeranger2/res/prebuilt/data/poke/p025_00_LZ.bin \
  --output-dir /tmp/ranger_pikachu
```

For Pikachu this automatically discovers the `a01`, `a02`, `p01`, `s`, `t`, and `w` graphics/cell pairs and renders every NCER cell.

The `.cac` companions are copied to an `_cac/` directory beside the previews so later animation-sequence research does not require re-extracting the package.

## Current boundary

This is a **visual recovery tool**, not a Platinum importer.

It intentionally:
- does not alter Platinum resources;
- does not guess what the Ranger suffix groups mean;
- does not interpret CAC animation sequencing;
- does not rescale or force Ranger artwork into Platinum's 80x80 battle contract.

The next decision is now based on actual rendered art, not binary structure.
