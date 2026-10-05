# PMD Sky Donor Inventory — Locked Specification

**Status:** LOCKED SPEC  
**Subsystem:** Pass G / donor-source collection  
**Target game:** Pokémon Platinum  
**Donor:** Pokémon Mystery Dungeon: Explorers of Sky  
**Donor repository:** `79cbd8hmgj-wq/pmd-sky`

## 1. Goal and scope

Add Explorers of Sky as the next source in the source-agnostic donor asset catalog.

This pass is **inventory/catalog only**. It must not:

- replace Platinum resources;
- choose preferred donor assets;
- mark files usable solely because they exist or fit a size limit;
- port PMD rendering code into Platinum;
- create a Platinum replacement ledger.

The purpose is to preserve recoverable PMD Sky visual candidates so they can be reviewed later beside Ranger, HGSS, Diamond/Pearl, and Platinum-native candidates.

## 2. Existing locked authority

The following repo authority remains unchanged:

- `docs/visual_overhaul/DONOR_ASSET_DATABASE.md`
- `docs/visual_overhaul/CROSS_GAME_DONOR_MATRIX.md`
- `docs/visual_overhaul/DONOR_ASSET_CATALOG.schema.json`

The donor database requires collection before replacement work, source-specific normalization, preservation of alternatives, explicit review states, and provenance.

The cross-game matrix classifies PMD Sky primarily as an **effects / technique / convertible reference**, especially for:

- weather behavior;
- fog/mist;
- field particles;
- animated environmental overlays;
- foliage motion;
- water presentation;
- snow layering;
- Distortion World effects;
- battle particles;
- menus/UI frames;
- screen transitions.

This inventory does not upgrade that donor class by itself.

## 3. Verified PMD Sky source reality

The donor repository exposes a large NitroFS-backed visual corpus under `files/`.

Verified high-value families include:

| PMD Sky path | Inventory category | Intended target tags |
|---|---|---|
| `files/EFFECT` | effects | effect, battle_animation_frame, field_effect |
| `files/GROUND` | ground_sprites_effects | overworld, effect, transition |
| `files/MAP_BG` | map_backgrounds | environment, background, tile, palette |
| `files/MONSTER` | monster_graphics | pokemon, overworld, animation |
| `files/FONT` | ui_font_resources | ui, cursor, frame, icon |
| `files/BACK` | static_backgrounds | background, ui, scene |
| `files/TOP` | title_top_assets | ui, title, background |
| `files/DUNGEON` | dungeon_visuals | environment, background, effect |
| `files/SYSTEM` | system_visual_candidates | ui, icon, effect |

Confirmed visual/resource formats include PMD-specific containers/resources such as:

- `.wan`
- `.wte`
- `.wtu`
- `.wat`
- `.wba`
- `.bgp`
- `.bma`
- `.bpc`
- `.bpl`
- `.bpa`
- `.chr`
- `.pal`
- `.w16`
- `.kao`
- `.bin`
- `.dat`

The repository also has source PNG/NCGR/NCLR build rules where reconstructed source graphics are available. Inventory code must preserve source files and binary resources as separate records rather than assuming equivalence.

## 4. Inventory policy

The PMD Sky inventory must scan only configured visual roots, not every donor file.

Every accepted record must include:

- source-relative path;
- category;
- asset type;
- file size;
- suffix;
- target tags;
- review status.

Initial review status is `unreviewed`.

Binary/container presence alone must never produce `valid_render`, `usable`, or `alternate`.

Files that are clearly code/build metadata should be excluded from the inventory.

## 5. Normalized catalog identity

Use:

- `source_id = "pmd_sky"`
- `source_game = "Pokémon Mystery Dungeon: Explorers of Sky"`
- `source_repo = "79cbd8hmgj-wq/pmd-sky"`

Normalized asset IDs must be deterministic and source-path based, matching the existing source inventory pattern:

`pmd_sky:source:<colon-normalized-source-path>`

Do not infer National Dex numbers from filenames in this first pass unless a source-backed mapping is explicitly available and validated.

## 6. Required outputs

The implementation must produce:

- `docs/visual_overhaul/PMD_SKY_VISUAL_ASSET_INVENTORY.json`
- `docs/visual_overhaul/PMD_SKY_VISUAL_ASSET_INVENTORY.md`

and rebuild:

- `docs/visual_overhaul/DONOR_ASSET_CATALOG.json`
- `docs/visual_overhaul/DONOR_ASSET_CATALOG.md`

The donor catalog must retain all existing Ranger, HGSS, and Diamond/Pearl entries.

## 7. Implementation targets

Claude should add:

- `tools/visual_overhaul/inventory_pmd_sky_visual_assets.py`
- PMD Sky importer support in `tools/visual_overhaul/build_donor_asset_catalog.py`
- `.github/workflows/pmd-sky-asset-inventory.yml`

The workflow should:

1. check out the Platinum overhaul;
2. check out `79cbd8hmgj-wq/pmd-sky`;
3. generate PMD Sky inventory JSON + Markdown;
4. rebuild the unified donor catalog with Ranger + HGSS + DP + PMD Sky;
5. commit only generated inventory/catalog changes when they differ.

## 8. Validation and acceptance criteria

Implementation is accepted only when:

- the PMD Sky inventory script exits successfully on the current donor repo;
- every configured root is reported as present or explicitly listed under `missing_roots`;
- candidate count is greater than zero;
- category totals sum exactly to `candidate_files`;
- no source path occurs twice within the PMD Sky inventory;
- normalized catalog asset IDs are unique;
- existing donor source counts are preserved after catalog rebuild;
- unified catalog contains exactly one `pmd_sky` source record;
- all PMD Sky entries begin as `unreviewed` unless a separate validated review artifact says otherwise;
- the workflow is reproducible from clean checkouts;
- no Platinum graphic/resource file is modified.

## 9. Follow-on work

After PMD Sky lands, donor collection should continue only for sources already identified in the matrix when they offer distinct value. Bulk cross-source visual review remains deferred until collection is mature.

PMD Sky's first later review should prioritize effects/animation/background presentation rather than assuming its Pokémon sprites are direct Platinum replacements.
