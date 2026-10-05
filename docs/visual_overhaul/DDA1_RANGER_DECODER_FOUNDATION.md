# DDA-1 — Ranger Donor Decoder Foundation

## Result

The first custom-format donor adapter is now defined for Pokémon Ranger: Shadows of Almia.

Repository inspection confirmed that the high-value Ranger resource families under `res/prebuilt/data/` commonly use files named `*_LZ.bin`. Direct inspection of representative Pokémon, Pokémon-object, effect, and interface resources shows a Nintendo DS **LZ10 header (0x10)** followed by a decompressed **NARC** payload.

Representative files checked:
- `poke/p025_00_LZ.bin`
- `pokeOBJ/bp025_LZ.bin`
- `effect/e000_LZ.bin`
- `interface/i019_LZ.bin`

Their encoded prefixes are consistent with:
1. LZ10 stream header;
2. decompressed-size field;
3. NARC payload beginning with `NARC`.

This materially reduces Ranger from an opaque binary pool to a standard pipeline:

```
*_LZ.bin
   ↓ LZ10
NARC
   ↓ BTAF/BTNF/GMIF
members
   ↓ signature classification
NCGR / NCLR / NCER / NANR / NSCR / Nitro 3D / unknown
```

## Tool

`tools/visual_overhaul/inspect_ranger_assets.py`

The tool:
- scans selected Ranger asset roots;
- validates and decompresses LZ10 streams;
- identifies the decompressed payload;
- parses NARC member ranges;
- performs best-effort recovery of simple BTNF filenames;
- classifies standard Nitro resource signatures;
- writes a machine-readable JSON report;
- never modifies the Ranger checkout.

Default roots:
- `poke`
- `pokeOBJ`
- `effect`
- `interface`
- `menu`

Example:

```sh
python3 tools/visual_overhaul/inspect_ranger_assets.py \
  --ranger-root ../pokeranger2 \
  --write-json docs/visual_overhaul/RANGER_DONOR_RESOURCE_INVENTORY.json
```

A bounded pilot can be run first:

```sh
python3 tools/visual_overhaul/inspect_ranger_assets.py \
  --ranger-root ../pokeranger2 \
  --asset-root poke \
  --limit 25
```

## Interpretation

Ranger should no longer be treated as requiring a bespoke compression decoder.

The remaining unknown is mainly **member-level resource semantics**:
- which NARC members are graphics;
- which are palettes;
- which are cells/animations;
- how individual Pokémon packages map their members together;
- which packages are useful for Platinum targets.

Standard Nitro members can reuse existing Platinum/Nitro tooling after extraction. Unknown members remain donor-specific and are not eligible for import until their contracts are understood.

## Next Ranger gate

Before any Ranger asset is integrated into Platinum:

1. run the full inventory locally;
2. identify the dominant NARC member signatures by asset family;
3. select a small Pokémon package such as Pikachu;
4. extract its graphics/palette/cell/animation members;
5. render a deterministic preview;
6. compare the preview against a named Platinum target contract.

No bulk Ranger conversion is authorized yet.
