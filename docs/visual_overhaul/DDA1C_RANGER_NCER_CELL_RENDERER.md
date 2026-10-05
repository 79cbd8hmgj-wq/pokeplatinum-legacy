# DDA-1C — Ranger NCER Cell Renderer

The Ranger Pikachu pilot now has a deterministic **cell-composition renderer**, not just raw tile sheets.

## Confirmed NCER structure

The first Pikachu NCER package follows the standard Nitro cell-bank organization closely enough to recover individual cell OAM lists:

- `RECN` file header
- `KBEC` / CEBK block
- cell count at the bank header
- 8-byte cell records
  - OAM count
  - cell attributes
  - byte offset into the OAM table
- 6-byte OAM entries
  - attr0
  - attr1
  - attr2

For `p025_00_a01.NCER`, the archive contains 8 cells. Its first cell contains three OAM objects whose signed positions and sizes form a coherent Pikachu composition.

The package uses ordinary DS OAM shape/size semantics.

## 2D character mapping

The Pikachu NCBR resources use 2D OBJ character mapping.

This explains apparent tile indices larger than the number of sequential source tiles. For example, tile indices such as 32 and 96 represent VRAM positions using a 32-tile row stride rather than simple sequential indices.

The renderer maps:

```
logical tile -> row/column in 32-tile OBJ VRAM
             -> source tile in the NCBR sheet
```

This resolves the apparent out-of-range tile references without inventing Ranger-specific graphics rules.

## Tool

`tools/visual_overhaul/render_ranger_ncer_preview.py`

Inputs:
- extracted NCGR/NCBR;
- extracted NCLR;
- paired NCER.

Outputs:
- one transparent indexed PNG per NCER cell.

Example:

```sh
python3 tools/visual_overhaul/render_ranger_ncer_preview.py \
  --graphics /tmp/ranger_extract/.../p025_00_a01.NCBR \
  --palette /tmp/ranger_extract/.../p025_00.NCLR \
  --cells /tmp/ranger_extract/.../p025_00_a01.NCER \
  --output-dir /tmp/ranger_pikachu_a01
```

The default VRAM stride is 32 4bpp tiles, matching the first Ranger pilot. It is exposed as an argument rather than buried as an unexplained constant.

## What remains unknown

The small `.cac` files are still not interpreted.

They likely describe animation sequencing or other Ranger-specific composition metadata, but that is **not required to recover the individual NCER visual cells**.

Therefore the next decision can be made from actual rendered Pikachu cells:

1. determine what the suffix groups `a01`, `a02`, `p01`, `s`, `t`, and `w` visually represent;
2. identify which cells are worthwhile donor candidates;
3. compare them against Platinum's 80×80 two-frame battle-sprite contract and other possible Platinum targets;
4. reverse the CAC format only if animation sequencing provides additional value.

This is the first point where Ranger can move from file-format research into actual visual curation.
