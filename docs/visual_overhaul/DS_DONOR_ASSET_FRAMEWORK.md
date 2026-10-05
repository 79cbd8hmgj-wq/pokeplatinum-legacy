# DS Donor Asset Compatibility Framework

## Scope

This project treats Pokémon Platinum as the target engine and limits donor research to Nintendo DS Pokémon games with accessible source/disassembly repositories.

Active pools:
- Pokémon Platinum — target/native control
- Pokémon Diamond/Pearl — direct Gen IV control donor
- Pokémon HeartGold/SoulSilver — primary external direct donor
- Pokémon Mystery Dungeon: Explorers of Sky — custom-format 2D/effects donor
- Pokémon Ranger: Shadows of Almia — custom-format graphics/effects donor

GBA, N64, GameCube, and later-platform assets are out of scope for this pass.

## Goal

Build a reproducible donor -> Platinum pipeline rather than manually copying assets.

Every imported candidate must be traceable to:
1. donor repository and path;
2. donor asset class/format;
3. Platinum target contract;
4. deterministic conversion, if required;
5. static validation;
6. runtime validation before final acceptance.

## Compatibility classes

- DIRECT — same or trivially compatible Gen IV resource contract.
- PALETTE_ONLY — artwork geometry is compatible; palette/index handling differs.
- GEOMETRY_CLOSE — dimensions/footprint are close enough for a staged runtime pilot.
- CONVERTIBLE — known donor format can be deterministically transformed to a Platinum source asset.
- TECHNIQUE_ONLY — useful animation/composition/effect reference but not an asset transplant.
- ENGINE_WORK — useful donor requires new or unresolved target-engine support.
- UNSUITABLE — conversion cost or visual mismatch exceeds expected value.

## Platinum target contracts

### Pokémon battle sprites
- source-backed PNGs under `res/pokemon/<species>/`
- female/male front and back views
- Platinum two-frame 80x80-cell assumptions remain authoritative
- normal/shiny palettes and `sprite_data.json` remain part of the target contract
- do not overwrite animation metadata solely to accommodate donor art

### Pokémon icons
- indexed 32x64 PNG contract already covered by the HGSS icon auditor
- shared palette/cell contract must remain valid

### UI / effects / environments
- target dimensions, indexed mode, palette banks, cell/animation references, archive ordering, and transparency rules must be discovered per target resource before import
- G7 ownership/generator rules remain authoritative

## Current donor findings

### Diamond/Pearl
High-confidence direct pool. The decomp exposes `files/poketool/` families including:
- `pokegra`
- `icongra`
- `pokeanm`
- `pokefoot`
- `pokezukan`
- `trainer`
- `trgra`

Pokémon graphics are already exposed as editable PNG-oriented source resources. Treat Diamond primarily as a control/reference for what Platinum changed.

### HeartGold/SoulSilver
Highest-value direct external donor. The repository exposes:
- `files/poketool/pokegra`
- `files/poketool/icongra`
- trainer and Pokédex-related resources
- explicit PNG -> NCGR/NCLR build rules through nitrogfx

Existing Platinum tooling already audits HGSS battle sprites, palettes, and icons. Extend these tools rather than creating a second HGSS pipeline.

### Mystery Dungeon: Explorers of Sky
Large but custom-format donor.

Confirmed pools include:
- `files/MONSTER/monster.bin`
- `files/GROUND/*.wan` (hundreds of entries)
- `files/EFFECT/effect.bin`
- `files/MAP_BG/` with BMA/BPC/BPL/BPA families
- `files/BACK/*.bgp`
- `files/TOP/*.bgp`

This is not a direct Gen IV transplant source. First objective is decoder/inventory coverage, then conversion into explicit Platinum target contracts.

### Pokémon Ranger: Shadows of Almia
Large custom-format pool already exposed in the fork under `res/prebuilt/data/`.

Confirmed buckets include:
- `poke/` — hundreds of compressed Pokémon resources such as `p025_00_LZ.bin`
- `pokeOBJ/` — hundreds of compressed Pokémon object resources
- `effect/` — 200+ compressed effect resources
- `interface/`
- `menu/`
- `field/`
- `npc/`
- `event/`
- `encyclo/`

The current fork keeps much of this material as prebuilt compressed binaries. Classify Ranger as CONVERTIBLE pending deterministic LZ/container decoding and resource-contract identification.

## Work order

1. Preserve and reuse the existing HGSS audits as the direct-donor baseline.
2. Add a cross-repository inventory report for all five pools.
3. Add PMD Sky decoders/inventory for WAN/BGP/MAP_BG families or integrate proven tooling if already present.
4. Add Ranger LZ resource inspection and identify the internal graphics/container contracts.
5. Build small conversion pilots before bulk conversion.
6. Only after a class has a deterministic converter should it become eligible for broad asset review.

## Pilot policy

Do not bulk-import hundreds of assets first.

For Pokémon-specific pilots, use a shape-diverse set such as:
- Pikachu
- Gengar
- Spinarak
- Charizard
- Steelix

A pilot is successful only when:
- donor extraction is reproducible;
- target source files build cleanly;
- static contract checks pass;
- the result is reviewed in Platinum runtime;
- no source-order/palette/animation regression is introduced.

## Repository policy

Raw donor ROMs are never committed.

External donor repositories remain external inputs. Platinum stores:
- manifests;
- converters;
- compatibility reports;
- approved converted source assets only when intentionally integrated.

This keeps donor provenance and conversion reproducible without turning the Platinum repository into a raw asset dump.
