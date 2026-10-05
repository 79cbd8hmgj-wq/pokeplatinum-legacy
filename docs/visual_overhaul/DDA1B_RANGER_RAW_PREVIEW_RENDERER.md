# DDA-1B — Ranger Raw Nitro Preview Renderer

The Ranger pipeline now reaches a first deterministic image output.

`tools/visual_overhaul/render_ranger_nitro_preview.py` renders extracted Ranger NCLR + NCGR/NCBR resources directly to indexed PNG.

## What was established from Pikachu

The main Pikachu graphics members use ordinary Nitro `RGCN` character data.

The RAHC geometry fields are internally consistent with their data sizes. Examples:

- `p025_00_a01.NCBR`: 4 × 16 tiles = 32 × 128 pixels, 2048 bytes of 4bpp data
- `p025_00_p01.NCBR`: 8 × 4 tiles = 64 × 32 pixels, 1024 bytes of 4bpp data
- larger Pikachu members similarly match width × height × 32-byte tile counts

The shared `p025_00.NCLR` is a normal 16-color Nitro palette.

This confirms we can get deterministic pixels from Ranger without reverse-engineering the graphics encoding itself.

## Usage

First extract a package:

```sh
python3 tools/visual_overhaul/inspect_ranger_assets.py \
  --ranger-root ../pokeranger2 \
  --asset-root poke \
  --limit 1 \
  --extract-dir /tmp/ranger_extract
```

Then render a package directory:

```sh
python3 tools/visual_overhaul/render_ranger_nitro_preview.py \
  --package-dir /tmp/ranger_extract/res/prebuilt/data/poke/p025_00_LZ \
  --output-dir /tmp/ranger_preview
```

## Current limitation

These PNGs are **raw tile-grid previews**, not final composed Ranger animation frames.

NCER cell geometry and the small `.cac` companion files still need to be interpreted for exact frame composition. The raw previews are nevertheless enough to:

- verify palette correctness;
- verify pixel decoding;
- identify which subresource contains useful art;
- reject unsuitable packages before deeper animation work.

The next Ranger task is NCER cell composition for the selected Pikachu groups.
