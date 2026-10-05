# Nintendo DS Donor Asset Program

## Scope

This program is the post-G7 asset expansion track for the Platinum overhaul.

The donor scope is now deliberately **Nintendo DS only**. GBA, Nintendo 64, GameCube, Wii, 3DS, and Switch sources are outside this track. Additional DS games may be added later if a useful public decomp/disassembly or a reproducible ROM-extraction path becomes available.

The goal is not to dump other games' artwork into Platinum. The goal is to build a repeatable pipeline that can answer:

1. what useful assets each donor exposes;
2. what Platinum target contract an asset could satisfy;
3. whether the asset is directly compatible, deterministically convertible, or reference-only;
4. whether the converted result survives the normal Platinum build and runtime path.

## Current asset pools

| Priority | Pool | Repository | Role |
|---|---|---|---|
| 0 | Pokemon Platinum | `79cbd8hmgj-wq/pokeplatinum-legacy` | target + native asset pool |
| 1 | Pokemon HeartGold/SoulSilver | `79cbd8hmgj-wq/pokeheartgold` | strongest direct donor |
| 2 | Pokemon Diamond/Pearl | `79cbd8hmgj-wq/pokediamond` | control/reference + direct donor |
| 3 | Pokemon Mystery Dungeon: Explorers of Sky | `79cbd8hmgj-wq/pmd-sky` | donor-specific conversion pool |
| 4 | Pokemon Ranger: Shadows of Almia | `79cbd8hmgj-wq/pokeranger2` | donor-specific conversion pool |

That is **five total asset pools: Platinum plus four external DS donors**.

## Verified high-value roots

### Platinum

The target already exposes source-backed Pokemon graphics under `res/pokemon/` and broader visual resources under `res/graphics/` and `res/field/`.

Existing G7 tooling already proves useful target contracts for:
- two-frame 80x80 Pokemon battle sprite cells;
- indexed Pokemon icon resources;
- palettes;
- sprite metadata;
- battle UI;
- menus;
- field graphics and textures.

Platinum remains authoritative for dimensions, palette/index behavior, archive order, animation metadata, and runtime ownership.

### HeartGold/SoulSilver

Verified donor roots include:
- `files/poketool/pokegra/`
- `files/poketool/icongra/`
- `files/graphic/`
- `files/fielddata/`

HGSS is the first-choice donor whenever a Platinum-equivalent contract exists. Existing HGSS battle-sprite and icon audit tools should be reused rather than replaced.

### Diamond/Pearl

Verified donor roots include:
- `files/poketool/pokegra/`
- `files/poketool/icongra/`
- `files/poketool/trgra/`
- `files/poketool/pokeanm/`

Diamond/Pearl is especially useful as a control for Gen-IV engine/resource lineage: it can tell us whether a resource or behavior changed between DP and Platinum before we reach for a more distant donor.

### Explorers of Sky

The decomp exposes large donor-specific pools rather than Platinum-like Pokemon directories.

Verified examples:
- `files/MONSTER/monster.bin` — large Pokemon sprite/resource container;
- `files/EFFECT/effect.bin` — large effects container;
- `files/GROUND/` — hundreds of `.wan` animated actor/sprite resources;
- `files/MAP_BG/` — `.bma`, `.bpc`, `.bpl`, and `.bpa` background/map resources;
- `files/BACK/` and `files/TOP/` — `.bgp` backgrounds.

PMD assets are **convertible**, not direct. PMD-specific parsers/adapters must decode them into an intermediate representation before any Platinum target conversion is attempted.

### Shadows of Almia

The Ranger decomp exposes a large prebuilt resource tree under `res/prebuilt/data/`.

Verified high-value groups include:
- `poke/` — hundreds of Pokemon resource binaries;
- `pokeOBJ/` — hundreds of Pokemon object resources;
- `effect/` — hundreds of effect resources;
- `interface/` — UI resources, including some explicit Nitro formats such as NCBR/NCLR plus NTFT/NTFP data;
- `menu/` — a very large UI/menu resource pool;
- `field/` — character, effect, and map subtrees.

Much of the Ranger material is currently stored as `*_LZ.bin`, so the first Ranger adapter is an **LZ/container identification and extraction pass**, not a blind importer.

## Compatibility vocabulary

Every candidate must end in one of these classes:

- **NATIVE** — already a Platinum resource.
- **DIRECT** — same or sufficiently close DS/Gen-IV contract; only trivial deterministic conversion is needed.
- **PALETTE_ONLY** — geometry/index structure fits and only palette treatment differs.
- **GEOMETRY_CLOSE** — plausible candidate but requires positioning/frame review.
- **CONVERTIBLE** — donor-specific decoding plus deterministic Platinum conversion is required.
- **MANUAL_ART_REQUIRED** — source material is useful, but an authored redraw/recomposition is necessary.
- **ENGINE_WORK_REQUIRED** — cannot fit the current Platinum resource contract without source/runtime changes.
- **REFERENCE_ONLY** — useful for design direction but not for asset transfer.
- **UNSUITABLE** — no worthwhile Platinum use identified.

## First implementation sequence

1. **Inventory the five pools**
   - record known resource roots;
   - count file types and compressed/container resources;
   - generate machine-readable and Markdown reports.

2. **Preserve Platinum target contracts**
   - existing Platinum/HGSS sprite and icon audits remain authoritative;
   - do not change Platinum dimensions or animation metadata merely to accommodate a donor.

3. **Direct-donor pass**
   - HGSS first;
   - Diamond/Pearl second;
   - identify assets that can be compared against Platinum without donor-specific reverse engineering.

4. **PMD adapter pass**
   - WAN;
   - MONSTER container;
   - BGP;
   - BMA/BPC/BPL/BPA;
   - EFFECT container.

5. **Ranger adapter pass**
   - LZ-compressed resource identification;
   - Nitro-format detection after decompression;
   - Pokemon/object resources;
   - effects;
   - interface/menu resources.

6. **Pilot conversion set**
   - use a small representative set before bulk work;
   - produce side-by-side previews;
   - build through normal Platinum resources;
   - runtime-test in actual battle/menu/field contexts.

7. **Scale only successful classes**
   - a converter must be deterministic and validated before it is allowed to process a whole asset family.

## Initial tooling

`tools/visual_overhaul/ds_donor_manifest.json` is the source-of-truth pool map.

`tools/visual_overhaul/inventory_ds_donor_pools.py` scans sibling/local donor checkouts and reports:
- known roots present/missing;
- file counts and byte totals;
- extension distribution;
- high-level resource classification;
- direct/Nitro/donor-specific/compressed/container counts.

Example with sibling repositories:

```sh
python3 tools/visual_overhaul/inventory_ds_donor_pools.py \
  --workspace .. \
  --write-json docs/visual_overhaul/DS_DONOR_ASSET_INVENTORY.json \
  --write-md docs/visual_overhaul/DS_DONOR_ASSET_INVENTORY.md
```

Individual roots can be overridden:

```sh
python3 tools/visual_overhaul/inventory_ds_donor_pools.py \
  --root hgss=/path/to/pokeheartgold \
  --root pmd_sky=/path/to/pmd-sky
```

## Import gate

No donor asset is accepted merely because it can be decoded.

Before integration it must have:
- a named Platinum target resource;
- known target dimensions and palette/index rules;
- known animation/cell/layout ownership where applicable;
- reproducible conversion;
- deterministic output;
- build verification;
- a runtime QA target.

This keeps the donor program additive without destabilizing the G7 visual foundation.
