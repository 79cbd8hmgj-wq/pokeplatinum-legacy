# DDA-2 — PMD Sky Donor Format Foundation

## Result

The PMD: Explorers of Sky pool has now been separated into concrete resource families rather than being treated as a generic custom-format bucket.

Representative repository files were inspected directly.

### Confirmed headers

- `files/GROUND/a001.wan`
  - begins with `SIR0`
  - classify as a SIR0-wrapped PMD resource
- `files/BACK/s01p04a0.bgp`
  - begins with `AT4PX`
  - classify as an AT4PX-compressed PMD background resource
- `files/MAP_BG/d00p01.bma`
  - no standard magic in the leading bytes
- `files/MAP_BG/d00p01.bpc`
  - no standard magic in the leading bytes
- `files/MAP_BG/d00p01.bpl`
  - no standard magic in the leading bytes

This establishes that PMD Sky requires a donor-specific decoder path and cannot be treated like HGSS/DP Nitro graphics.

## Tool

`tools/visual_overhaul/inspect_pmd_sky_assets.py`

The tool performs a non-destructive first-pass inventory of:

- `GROUND`
- `MAP_BG`
- `BACK`
- `TOP`
- `MONSTER`
- `EFFECT`

It records:

- extension;
- byte size;
- first 16 bytes;
- known PMD wrapper/compression class;
- MAP_BG sibling groups sharing the same stem.

Known header classes currently recognized:

- `SIR0`
- `AT4PX`
- `PKDPX`
- raw/unknown

Example:

```sh
python3 tools/visual_overhaul/inspect_pmd_sky_assets.py \
  --pmd-root ../pmd-sky \
  --write-json docs/visual_overhaul/PMD_SKY_DONOR_RESOURCE_INVENTORY.json
```

## MAP_BG handling

PMD Sky backgrounds are not single-file assets. The inventory groups files with matching stems so a future decoder can preserve relationships among:

- `.bma`
- `.bpc`
- `.bpl`
- optional `.bpa`

The converter must understand the family together rather than converting files independently.

## Current compatibility status

- WAN / SIR0: **CONVERTIBLE — decoder required**
- BGP / AT4PX: **CONVERTIBLE — decompressor + renderer required**
- BMA/BPC/BPL/BPA: **CONVERTIBLE — family contract required**
- MONSTER container: **CONVERTIBLE — container parser required**
- EFFECT container: **CONVERTIBLE — container parser required**

Nothing in this batch authorizes asset transplantation.

## Next PMD gate

The next PMD implementation should provide:

1. deterministic SIR0 parsing;
2. AT4PX decompression;
3. WAN frame/animation extraction;
4. BGP image rendering;
5. a MAP_BG family renderer;
6. only then, Platinum target conversion.

A small rendered preview set should be produced before any bulk conversion.
