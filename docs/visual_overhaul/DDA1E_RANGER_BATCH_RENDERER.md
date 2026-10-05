# DDA-1E — Ranger Batch Renderer

The Ranger Pokémon donor path is now batch-oriented.

## Tool

`tools/visual_overhaul/render_ranger_pokemon_batch.py`

It discovers `pNNN_VV_LZ.bin` packages under Ranger's `res/prebuilt/data/poke/`, runs the verified package renderer on each package, and writes a JSON summary.

This means the workflow is no longer one Pokémon at a time.

### Full donor pool

```sh
python3 tools/visual_overhaul/render_ranger_pokemon_batch.py \
  --ranger-root ../pokeranger2 \
  --output-dir /tmp/ranger_all \
  --write-json /tmp/ranger_all.json
```

### Shape-diverse pilot

The first structural pilot uses:

- #006 Charizard — large / winged
- #025 Pikachu — small / upright
- #094 Gengar — compact / round
- #167 Spinarak — low / wide
- #445 Garchomp — tall / irregular

```sh
python3 tools/visual_overhaul/render_ranger_pokemon_batch.py \
  --ranger-root ../pokeranger2 \
  --species 6 \
  --species 25 \
  --species 94 \
  --species 167 \
  --species 445 \
  --output-dir /tmp/ranger_pilot \
  --write-json /tmp/ranger_pilot.json
```

If these five packages render successfully with the same generic pipeline, Ranger Pokémon extraction is considered structurally generalized enough to proceed to a full-pool render.

## Output layout

```
output/
  006/
    00/
      <group>/cell_000.png
      ...
    01/
      ...
  025/
    00/
      ...
```

Multiple Ranger variants are preserved instead of silently choosing one.

## Failure policy

Batch rendering is strict:
- every package is attempted independently;
- errors are recorded with species/variant/package;
- successful outputs are retained;
- command exits non-zero when any selected package fails.

This makes unusual packages visible instead of hiding them behind a bulk conversion.

## What this does not do

It does not yet decide which Ranger cells are better than Platinum art.

The next stage is an automated compatibility/curation report over rendered cells:
- dimensions;
- bounding box;
- transparency;
- likely fit inside Platinum's 80x80 battle frame;
- group/frame count;
- duplicate detection;
- unusual outliers for manual review.
