# IO-PREVIEW — Sinnoh expansion (5 locations)

Baseline: `main` 6d00bcde (includes PR #86). Status: **source/asset implemented; static gates and CI are the only validation. Emulator/runtime QA and art-direction acceptance are DEFERRED to the project owner** (none was run or required for this PR).

Scope: extends the Eterna Forest architecture (`IO_PREVIEW_ETERNA_FOREST.md`, gates G1–G9 unchanged) from one hard-coded location to a table of five more. No map-header, script, save, text, timing or input change. No donor research was repeated; no HGSS/FireRed pixels are used (procedural Platinum-native art, same as the pilot).

## 1. Location selection (from `include/data/map_headers.h`)

A card is gated on **(location-name text ID, popup style)**, the only two values the popup receives. Indoor headers (`MAP_TYPE_INDOORS`/`POKECENTER`) never reach the popup (`FieldSystem_RequestLocationName` skips buildings).

| Location | Gate | Headers that show the card | Same name, no card | Why chosen |
|---|---|---|---|---|
| Route 217 | `Route217` + ROUTE | `ROUTE_217` (blizzard) | West / Northeast houses (indoors: no popup) | snowy route |
| Mt. Coronet | `MtCoronet` + CAVE | 14 headers: 1F–6F, B1F, tunnel/north rooms, both outside maps (heavy snow), iceberg ruins | none | snow-capped mountain |
| Lake Verity | `LakeVerity` + LAKE | `LAKE_VERITY`, `_LOW_WATER` | Verity Cavern / Lakefront (different text) | lake style |
| Lake Acuity | `LakeAcuity` + LAKE | `LAKE_ACUITY`, `_LOW_WATER` | Acuity Cavern / Lakefront (different text) | icy lake |
| Distortion World | `DistortionWorld` + CAVE | 12 headers (all floors, Giratina and Turnback Cave rooms, two unnamed headers) | none | Distortion World |
| Eterna Forest (pilot) | `EternaForest` + FOREST | `ETERNA_FOREST` | `ETERNA_FOREST_OUTSIDE` (route style) | unchanged |

Lake Valor, Acuity Lakefront, Snowpoint City and Turnback Cave were left out to keep the slice bounded (Snowpoint's headers are mostly buildings; the others add art volume, not new mechanism).

## 2. What changed

- `map_name_popup.c`: the hard-coded Eterna check became a `static const AreaCard sAreaCards[]` table (`textID`, `popupStyle`, first NARC member, has-time-of-day-variants) plus `MapNamePopUp_GetAreaCardVariant()` (the unchanged twilight → dusk / night, late night → night mapping). `MapNamePopUp_DrawAreaCard`, the single hook, the NULL/short-resource handling and all teardown paths are unchanged.
- Style constants: `POPUP_STYLE_ROUTE 2`, `CAVE 3`, `FOREST 4`, `LAKE 7` (header `MAP_LABEL_WINDOW_*` minus one; checked by the validator).
- NARC: 13 new members 21–33 appended after the pilot's 18–20 (`map_popup.order`, `meson.build`). The only reader indexes `windowID*2`, so appended members stay invisible to it.
- 13 new 104×40 PNGs: three time-of-day variants for each of Route 217 / Mt. Coronet / Lake Verity / Lake Acuity, and **one** for Distortion World.

## 3. Resource ownership, palette and time of day

- **Ownership: identical to the pilot** (§4 there). Card pixels live in the existing popup `Window` (tiles 18–30), its tilemap rows and BG3; the only allocation is the temporary NARC buffer, allocated and freed inside `MapNamePopUp_DrawAreaCard`. No new palette, OAM, VRAM bank, heap object or persistent state.
- **Palette:** the popup loads the *style's* NCLR into BG palette slot 7 on every show, so each card must use that style's 16 colours: Route 217 → `route_popup`, Mt. Coronet and Distortion World → `cave_popup`, lakes → `lake_popup`. The generator reads each palette from the style PNG; the validator asserts byte equality per card. Index 0 differs between styles but is transparent for blits.
- **Time of day:** same clock as the pilot and as area lighting (`GetTimeOfDay()`), chosen once per show. **Distortion World deliberately has a single card** for all hours: it is outside normal time and has no sky, so day/dusk/night variants would be wrong rather than merely unnecessary. Mt. Coronet's cave floors also show the snowy-peak card; the popup has no per-header information, so one card per name is the design.
- **Map-name functionality:** the popup text, sign art, slide timing, hide-on-input, building suppression and `fieldmap.c` seamless re-show are untouched; `Show`, `Hide`, `Create`, `Destroy` and `FieldSystem_RequestLocationName` are asserted free of card code by the validator.

## 4. Validation (source/asset level)

`tools/visual_overhaul/io_preview/validate_area_cards.py` (renamed from `validate_eterna_forest_card.py`) now derives every gate from the C table and cross-checks `map_headers.h`, `map_popup.order`, `meson.build` and the PNGs: table keys unique; enum contiguous and owned by table entries; variants are consecutive day/dusk/night in order; each key reaches ≥1 non-building header; palette identity per style; index range; transparent top rows; `nitrogfx` NCGR tile stream == PNG tile order for every card (65 tiles, 2080 B); hook order, NULL handling, single call site. Mutation checks (wrong style, removed style test) fail as expected. One heuristic was recalibrated: "more than 6 indices used" became "at least 5", because the cave and lake palettes have a single true dark so their night scenes use 5–6 indices; it still rejects flat art. `build_sinnoh_area_cards.py` output was verified byte-identical on regeneration and the pilot's PNGs are unchanged. CI (`validate-io-preview`, ROM build) results are recorded in the PR.

No ARM toolchain exists in the authoring environment, so the ROM build is verified by CI only. The G7 `validate_g76_atmosphere` failure documented in the pilot (pre-existing, caused by the Solaceon script change) is unrelated and not touched.

Mockup (data-level composite, **not** an emulator capture, text not drawn): `io_preview/sinnoh_area_cards_mockup.png`.

## 5. DEFERRED to the project owner (not run)

Record build SHA, ROM revision (Rev 0 and Rev 1), emulator/version, steps and screenshots/video.

1. Each location at day, dusk and night (change the clock): card beside the name, readable, not clipped; Distortion World identical at all hours.
2. Negative cases: no card on Route 217 houses, Eterna Forest outside gate, Verity/Acuity Cavern and Lakefront, other routes/caves.
3. Slide in/out, re-show during hold and slide-out, fast map changes (e.g. Mt. Coronet floors, Distortion World floors): no stale card or tile garbage; card gone after leaving.
4. A / menu / script during the popup; battle, menu and field return; no BG3 leakage or heap assert.
5. Art-direction sign-off for all 16 cards; the cave/lake night variants are palette-limited first passes.

## 6. Rollback

Remove entries from `sAreaCards` (a table with only the pilot row is the previous behaviour), or the single `MapNamePopUp_DrawAreaCard` call for fully vanilla popups. The PNGs/NARC members can then be dropped from `map_popup.order`/`meson.build` (keep order contiguous; the validator enforces it).
