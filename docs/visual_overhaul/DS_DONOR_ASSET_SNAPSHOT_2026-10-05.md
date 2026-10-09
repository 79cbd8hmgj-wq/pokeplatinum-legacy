# DS Donor Asset Snapshot — 2026-10-05

## Purpose

This is the first source-backed inventory snapshot for the Nintendo DS-only donor program.

Counts below come from the current repository trees at these exact commits:

- Platinum: `3472ac90ce4f718dfcf4a6fa55a201f23e01baae`
- HeartGold/SoulSilver: `9d8b7591f09b65804da2fb2dfd56f320633e0d36`
- Diamond/Pearl: `5bc4b1a3d8f100f77a4c64e59a0d544a0e29b3ec`
- Explorers of Sky: `be11cacd78574257bb88116c36dfca8f0839feba`
- Shadows of Almia: `55b4e0cd4598bcbc966f64ad6a10eeab98f813e1`

The counts cover only the high-value roots currently listed in `ds_donor_manifest.json`; they are not whole-repository file counts.

## Pool summary

| Pool | Known-root files | Approx. bytes | Initial role |
|---|---:|---:|---|
| Platinum | 14,156 | 43.68 MB | native target/control |
| HeartGold/SoulSilver | 7,305 | 12.97 MB | primary direct donor |
| Diamond/Pearl | 7,872 | 3.67 MB | direct/control donor |
| Explorers of Sky | 2,071 | 29.19 MB | donor-specific conversion |
| Shadows of Almia | 2,588 | 23.07 MB | compressed/donor-specific conversion |
| **Total across known roots** | **33,992** | **112.56 MB** | |

These totals are deliberately conservative because only already-identified high-value roots are counted.

## Platinum target pool

### `res/pokemon/`

- 7,570 files
- 3,002 PNGs
- 1,084 palette files
- 1,014 JSON files
- 1,969 key files

This remains the authoritative Pokemon battle-sprite/icon/palette contract.

### `res/graphics/`

- 2,742 files
- 1,119 PNGs
- 338 JSON files
- 259 NSCR
- 218 palette files
- 27 NSBMD
- 26 BIN
- additional NCGR/NCLR/NCER/NANR/NSBCA/NSBTA/NSBMA resources

### `res/field/`

- 3,844 files
- 1,177 JSON
- 668 BIN
- 590 NSBMD
- 148 NSBTX
- 43 NSBTA
- 32 NSBCA
- 23 NSBTP

Platinum therefore already exposes a large native target surface. Donors should fit these contracts rather than forcing new formats into runtime.

## HeartGold/SoulSilver

### Pokemon graphics — `files/poketool/pokegra/`

- 4,118 files
- 2,137 PNGs
- 1,973 key files
- NARC/NCLR support files

This is the strongest immediately usable Pokemon-art donor pool.

### Pokemon icons — `files/poketool/icongra/`

- 554 files
- 544 PNGs
- shared palette/cell metadata

Existing Platinum HGSS icon auditing should remain authoritative.

### General graphics — `files/graphic/`

- 173 files
- 47 PNGs
- 47 NSCR
- 17 NCLR
- 16 NANR
- 16 NCER
- 9 NCGR

This is a strong direct pool for UI/Pokedex/general 2D resource comparison.

### Field data — `files/fielddata/`

- 2,460 files
- 493 JSON
- 289 BIN
- 76 PNG
- 76 NSCR
- 3 NARC

## Diamond/Pearl

### Pokemon graphics — `files/poketool/pokegra/`

- 7,112 files
- 1,812 PNGs
- 986 PAL files
- 2,279 BIN
- 137 NCGR
- 78 NCLR

Diamond/Pearl has a particularly useful mixture of editable source graphics and lower-level packed assets.

### Pokemon icons — `files/poketool/icongra/`

- 542 files
- 502 NCGR
- 31 PNG
- 6 JSON

### Trainer graphics — `files/poketool/trgra/`

- 216 files
- 106 PNGs
- matching key files

### Pokemon animation — `files/poketool/pokeanm/`

- one binary data payload plus metadata

Use Diamond/Pearl primarily as the closest structural control for what changed before Platinum.

## Explorers of Sky

### `files/MONSTER/`

- one `monster.bin`
- 5,688,128 bytes

Treat this as a container reverse-engineering target, not a first pilot.

### `files/GROUND/`

- 555 files
- 518 WAN resources
- 15 WTE
- 15 WTU
- 7 WAT

This is the best first PMD sprite/actor-format pool because resources are already split into discrete files.

### `files/EFFECT/`

- `effect.bin` — 3,886,448 bytes
- 2 WBA resources

### `files/MAP_BG/`

- 1,482 files
- 472 BPL
- 467 BMA
- 458 BPC
- 85 BPA

This is the strongest PMD environment/background conversion pool.

### `files/BACK/` + `files/TOP/`

- 30 BGP backgrounds total

## Shadows of Almia

### Pokemon resources — `res/prebuilt/data/poke/`

- 298 files
- 297 `*_LZ.bin` resources

### Pokemon object resources — `res/prebuilt/data/pokeOBJ/`

- 283 files
- 282 compressed BIN resources

### Effects — `res/prebuilt/data/effect/`

- 201 files
- 200 compressed BIN resources

### Interface — `res/prebuilt/data/interface/`

- 79 files
- 72 compressed BIN resources
- 3 NTFT
- 3 NTFP

### Menus — `res/prebuilt/data/menu/`

- 810 files
- 809 compressed BIN resources

### Field — `res/prebuilt/data/field/`

- 917 files
- 883 `.lz` resources
- 16 BIN
- 7 NTFT
- 7 NTFP

The Ranger pool is large enough to justify its own adapter. The immediate task is to decompress representative resources and identify internal format signatures before building target converters.

## First concrete pilots

The donor program should now proceed in this order:

1. **HGSS direct comparison**
   - reuse the existing battle-sprite/icon audits;
   - expand to trainer/UI candidates where target contracts are already known.

2. **Diamond/Pearl control comparison**
   - trainer graphics;
   - Pokemon/icon differences;
   - animation/resource differences that help explain Platinum ownership.

3. **PMD Sky format pilots**
   - one WAN actor resource;
   - one BGP background;
   - one BMA/BPC/BPL map-background set;
   - defer `monster.bin` until the discrete formats are understood.

4. **Ranger format pilots**
   - one explicit NTFT/NTFP interface resource;
   - one small `*_LZ.bin` resource;
   - decompress, fingerprint the payload, and identify whether it contains a standard Nitro resource, a Ranger container, or raw tile/palette data.

5. **Only then build conversion candidates**
   - every candidate must name its Platinum target contract;
   - no bulk conversion until the corresponding adapter is deterministic.

## Decision

There is no need to search for more donor games yet.

The current five pools already expose enough material to keep the asset program busy through:
- direct Gen-IV comparisons;
- Pokemon sprite/icon work;
- trainer art;
- UI;
- effects;
- backgrounds;
- environment resources;
- two independent custom-format reverse-engineering tracks.

Additional DS games should be decomposed only when a concrete asset need remains unmet after these pools are audited.
