# Ranger renderer root cause (P1 reconstruction issues)

Follow-up to PR #63 (`LANE_A_P1_VISUAL_REVIEW`: 19,016 `decode_issue` /
`ranger_reconstruction_issue`). Donor validity and renderer failure stay separate:
nothing here rejects a donor asset, imports into Platinum, or selects usable/alternate.

## Method

Compact differential diagnostic (`tools/visual_overhaul/diagnose_ranger_structure.py`,
JSON only) over positive controls 421/422/465/490 and broken controls 006/025/094/167/445/448
(`RANGER_RENDERER_CONTROL_DIAGNOSTIC.json`); whole-corpus invariants and a per-group ledger in
`RANGER_RENDER_STRUCTURAL_VALIDATION.json`.

## Systematic difference found

| Field | Known-good groups | Broken groups |
|---|---|---|
| Character resource | NCGR, scan flag 0 (tile-ordered, 32x32-tile sheet) | NCBR only, scan flag 1 (**scanline raster**) |
| NCER mapping / cell type / affine / flips / 256-colour | identical everywhere (map 4, type 0, no affine) | identical |

The renderer read every NCBR as tile-ordered, and only the groups that also shipped an NCGR
(which won the stem collision by accident of sort order) rendered correctly. Packages with both
resources are the oracle: re-decoding the NCBR as a raster reproduces the NCGR render
**pixel-exactly for all 8 such groups (148 cells)**. Two secondary defects fixed on the way:

1. **Raster width is not stored.** The NCBR header's tile W/H only encode the tile count. The
   width is the 32-tile OBJ VRAM row, cropped to the rows the cell bank uses (tightest power-of-two
   width that holds every addressed column and row; 2 for the tiny p490_01 case). A first "smallest
   width" heuristic was rejected after it mis-rendered 5 groups; the final rule matches the oracle
   and those groups.
2. **OAM palette row ignored.** 4bpp OBJ palette number selects a 16-colour NCLR row (Charizard's
   blue wing membrane is palette row 1).

## Verification

- Positive controls: all 129 previously `valid_render` member frames are byte-identical.
- Corpus: 296/296 packages, 35,806 cells, 129,215 OAM objects; 72 objects (26 groups) still
  reference tiles that are absent from their own group's data (they live in another resource) and
  6 reference a palette row beyond the NCLR; those frames stay `decode_issue`.
- Sample contact sheets (006/025/094/167/445/448/190) inspected: clean sprites.

Result counts: `RANGER_RENDERER_RECOVERY.json`.
