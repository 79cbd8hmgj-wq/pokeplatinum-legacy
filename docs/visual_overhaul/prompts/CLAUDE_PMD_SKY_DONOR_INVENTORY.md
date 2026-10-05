# Claude Handoff — PMD Sky Donor Asset Inventory

**Authority:** `docs/visual_overhaul/PMD_SKY_DONOR_INVENTORY_SPEC.md`  
**Status:** APPROVED IMPLEMENTATION HANDOFF

Implement the locked Explorers of Sky donor inventory without redesigning donor policy.

## Read first

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/visual_overhaul/DONOR_ASSET_DATABASE.md`
4. `docs/visual_overhaul/CROSS_GAME_DONOR_MATRIX.md`
5. `docs/visual_overhaul/PMD_SKY_DONOR_INVENTORY_SPEC.md`
6. `tools/visual_overhaul/inventory_dp_visual_assets.py`
7. `tools/visual_overhaul/build_donor_asset_catalog.py`
8. `.github/workflows/dp-asset-inventory.yml`

## Starting state already verified

Diamond/Pearl is not missing. Current `main` contains:

- `tools/visual_overhaul/inventory_dp_visual_assets.py`
- `.github/workflows/dp-asset-inventory.yml`
- `docs/visual_overhaul/DP_VISUAL_ASSET_INVENTORY.json`
- `docs/visual_overhaul/DP_VISUAL_ASSET_INVENTORY.md`
- DP importer support in `build_donor_asset_catalog.py`
- rebuilt unified donor catalog artifacts

Do not reconstruct or replace the DP implementation.

## Implementation sequence

### A. Inventory script

Create `tools/visual_overhaul/inventory_pmd_sky_visual_assets.py`.

Model its output contract after the DP/HGSS source inventory scripts, but use PMD Sky-specific roots and suffix classification from the locked spec.

Required CLI:

- `--pmd-root`
- `--write-json`
- `--write-md`

Required report fields:

- `schema_version`
- `source_id`
- `source_game`
- `candidate_files`
- `missing_roots`
- `category_counts`
- `type_counts`
- `suffix_counts`
- `bytes_by_category`
- `records`

Each record must preserve path/category/type/size/suffix/tags/review status.

### B. Unified catalog importer

Extend `build_donor_asset_catalog.py` with:

- `PMD_SKY_SOURCE_ID = "pmd_sky"`
- `pmd_sky_inventory_assets(...)`
- CLI option `--pmd-sky-inventory`
- source metadata pointing to `79cbd8hmgj-wq/pmd-sky`

Do not change existing Ranger/HGSS/DP asset normalization.

### C. GitHub Actions

Create `.github/workflows/pmd-sky-asset-inventory.yml`.

The workflow must check out:

- the current Platinum repo as `platinum`;
- `79cbd8hmgj-wq/pmd-sky` as `pmd-sky`.

Generate:

- `PMD_SKY_VISUAL_ASSET_INVENTORY.json`
- `PMD_SKY_VISUAL_ASSET_INVENTORY.md`

Then rebuild the unified donor catalog while passing all currently available donor inventories.

### D. Validation

Before push:

1. run the PMD inventory locally in CI;
2. assert `candidate_files > 0`;
3. assert category total == candidate count;
4. assert no duplicate `source_path`;
5. rebuild donor catalog;
6. assert unique `asset_id`;
7. assert sources include Ranger, HGSS, Diamond, PMD Sky exactly once each;
8. assert no Platinum visual resource files changed.

### E. Generated report review

The generated Markdown should expose:

- candidate total;
- missing root count;
- category counts + bytes;
- asset-type counts;
- suffix counts if useful;
- explicit policy that all entries remain unreviewed pending cross-source review.

## Hard boundaries

Do not:

- import PMD assets into Platinum;
- mark candidates usable automatically;
- decode/convert every proprietary PMD format in this pass;
- invent species mappings;
- replace the donor database schema;
- broaden this into PMD engine porting.

If the live source layout contradicts the locked roots, report the discrepancy rather than silently redefining scope.

## Completion report

Return:

1. files changed;
2. commit SHA;
3. PMD candidate count;
4. counts by category;
5. missing roots;
6. unified catalog source count and asset count;
7. validation commands/results;
8. workflow run result;
9. any source-layout discrepancy.
