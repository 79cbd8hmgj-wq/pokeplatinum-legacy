# Donor Curation Handoff — decode recovery through Lanes A–E

Nothing here imports donor assets into Platinum and no preferred/alternate donor has been selected.

## State (see `DONOR_CURATION_STATUS.json/.md`)

All **64,841** catalog assets have exactly one curation record (no missing, extra, duplicate or `unreviewed`).

| Status | Assets |
|---|---:|
| usable | 55,157 |
| reject | 9,578 |
| decode_issue | 106 |

Current ledgers (baseline → overlays → recovered state):

| Lane | Baseline | Recovered (current authority) |
|---|---|---|
| A | `LANE_A_FINAL_CURATION` + `LANE_A_RESIDUAL_RECOVERY` | `LANE_A_RECOVERED_CURATION` |
| B | `LANE_B_FINAL_CURATION` + 7 recovery ledgers | `LANE_B_RECOVERED_CURATION` |
| C/D/E | `LANE_CDE_BASELINE_CURATION` + 3 recovery ledgers | `LANE_CDE_RECOVERED_CURATION` |

`LANE_B_DECODE_RECOVERY_PLAN` groups the original 7,183 Lane B `decode_issue` records by
source / type / group / kind / path family with their current disposition.
`DONOR_CURATION_UNRESOLVED` lists the 106 records still unresolved.

## Recovery methods (each ledger carries per-record evidence)

* **Ranger LZ10→NARC packages** (`recover_lane_b_ranger_embedded.py`, used for Lane B and C/D/E): NCER cell render
  (2D stride-32 sheet, 1D OBJ mapping, sentinel-0xFFFF NCGR geometry), NSCR+NCGR screen composition,
  256×192 RGB555 `.nbfs`, `.ntft/.ntfp` DS textures (A3I5/A5I3, format proven by palette index coverage), NFTR glyph sheets,
  NCBR/NCGR twins, shared `um_LZ` tile resources, PMD-style companions (`.cac`, NANR).
* **Ranger field maps** (`ranger_map_compose.py`, `recover_lane_b_ranger_maps.py`): the overlay-0 loader shows the
  `0xd`/`5` layers are textured-quad lists drawn from 4bpp atlas chips (DS texture repeat ⇒ source wraps). All 441 maps
  compose with every quad in range and exact layer-size match. Sample: `LANE_B_RANGER_MAP_COMPOSITES_SAMPLE.png`.
  Blending is simplified (all quad layers opaque, file order).
* **Diamond `otherpoke`**: NCGR↔NCLR pairing taken from `arm9/src/pokemon.c`; sprite data is back-to-front LCG encrypted
  (`recover_lane_b_nitro2d_pairs.py`).
* **PMD Sky**: SkyTemple reference decoder (`skytemple-files 1.8.5`) for WAN/WTE/WTU/BMA+BPC+BPL(+BPA)/BGP/KAO/CHR/W16/FontDat.
* **HGSS plist/zukan**: pairing read from the decomp's own load calls (`recover_lane_cde_hgss_graphic.py`).
* **Rejects are evidence-based**: zero-byte placeholders, build-list text, stray svn property text, structured tables
  with no pixel payload, blank maps/screens/packages (every referenced tile in range and zero), uniform palettes.

Reason codes make weaker evidence filterable for the later preferred/alternate ranking:
`*_companion_*` (animation/palette/screen companions, `hgss_game_paired_companion` is **not independently rendered**),
`*_standalone_palette_color_reference` (palettes only), `ranger_tiles_in_sibling_resource`.

## Known weaknesses

* Ranger map quad layers are drawn opaque in file order; some interiors show unfilled (colour-key) areas and
  overlay/collision-style patterns that the game blends differently.
* Uncertain-geometry renders: A3I5/A5I3 widths are chosen by row continuity (noise textures are ambiguous).
* The earlier Nitro structural audit (`LANE_B_NITRO2D_STRUCTURAL_RECOVERY`) was necessary but not sufficient — the
  Diamond sprites were encrypted and "nonblank" noise passed it; the pairing pass added decryption and visual checks.

## Remaining 106 (`DONOR_CURATION_UNRESOLVED.md`)

PMD `.wan/.wat/.wba` (26: SkyTemple's strict parser rejects them — first fragment flagged "reuse previous image";
needs a lenient WAN reader), PMD `hsd_*/ses_*.dat` (AT4P-compressed 49,152-byte images, format unknown) and font data,
HGSS GF bitmap fonts (11) and 3D building-model NARCs (`bm_field`, `bm_room`: BMD0 — needs an NSBMD renderer),
20 Lane A Ranger cells (OAM tiles exist in no resource of the package, or candidates disagree), and ~35 Ranger oddities
(NCER palette rows beyond the NCLR, loose NCBR rasters of unknown width, `sendbin`, `encyclopedia.bin`).

## Rebuild

`tools/visual_overhaul/` scripts take donor checkouts as arguments (`pokeranger2`, `pmd-sky`, `pokeheartgold`, `pokediamond`),
so recovery passes ran locally; `lane-b-recovered-curation.yml` and `donor-curation-status.yml` regenerate the recovered
ledgers/status from the committed overlay ledgers and assert the coverage invariants.
