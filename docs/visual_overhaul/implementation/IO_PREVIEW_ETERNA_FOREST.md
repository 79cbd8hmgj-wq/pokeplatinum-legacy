# IO-PREVIEW — Eterna Forest location card pilot

Baseline: `main` 20aad84f. Status: **source/asset implemented; static gates and CI ROM build verified (see §6); emulator/runtime QA and art-direction acceptance remain PENDING.**
No ARM/CodeWarrior toolchain is available in the authoring environment, so the ROM build is verified by CI only. The PNG→NCGR conversion was exercised locally and in CI with the repo's own `nitrogfx`.

Scope: one location (`MAP_HEADER_ETERNA_FOREST`), three time-of-day art variants, no new gameplay, no script, map-header, save or text changes. Reuses the existing cross-generation donor research (`CROSS_GEN_IMPLEMENTATION_PLAN.md` §4 `IO-PREVIEW`); no donor re-discovery was done.

## 1. Static gate results

| Gate | Evidence | Result |
|---|---|---|
| G1 Hook point | `FieldSystem_RequestLocationName` (`map_name_popup.c`) is called from `field_transition.c:176`, `field_map_change.c:864/995` (fly/warp) and `unk_02056B30.c:242`, right as the map fade-in starts; seamless header changes call `MapNamePopUp_Show` from `fieldmap.c:479`. Every path ends in `MapNamePopUp_Show` → `MapNamePopUp_DrawWindowFrame` (initial show, and re-show after a slide-out). | PASS: one choke point |
| G2 Geometry | Popup is a `Window` of **32×5 tiles** on `BG_LAYER_MAIN_3` (palette 7, base tile `BASE_TILE_MESSAGE_WINDOW - 160`); only tiles 0–16 are blitted (136 px sign). Tiles 17–31 are `Window_FillTilemap(…, 0)` transparent. | PASS: 15×5 tiles already allocated and unused |
| G3 Palette | Popup loads exactly one 16-colour bank (`GX_LoadBGPltt`, slot 7) from the style's NCLR; window text uses indices 2/3. A second bank would need per-tile palette bits that `Window` does not expose. | PASS with constraint: card must share `forest_popup` palette |
| G4 Layer/scroll | BG3 priority 0; slide uses `Bg_SetOffset(BG3, Y)` (38→0→38). A card on another row of BG3 would be visible while "hidden"; a card **inside the popup window rows 0–4** slides with the popup. | PASS only for in-window placement |
| G5 Time of day | Area lighting reads `GetTimeOfDay()` (RTC, `ov5_021F134C.c`); 2D BG palettes are never tinted. The popup has no day/night behaviour. | PASS: variants chosen at draw time from the same clock |
| G6 Teardown | Popup state is reset by `MapNamePopUp_Hide` (`Window_ClearAndCopyToVRAM`, offset 0), destroyed with the field map (`fieldmap.c:352`), and redrawn from `Window_FillTilemap` each show. | PASS: in-window pixels need no teardown of their own |
| G7 Vanilla preserved | Popup text, art, timing (slide 4 px/frame, 60-frame hold), hide-on-input and building suppression are untouched; the card only adds blits. | PASS |
| G9 Load failure | `Graphics_GetCharData` returns the buffer, or **NULL without writing `*outCharData`** if the NARC member cannot be loaded or `NNS_G2dGetUnpackedBGCharacterData` fails (`GetCharacterData` frees the buffer first). `Heap_Alloc` failure calls `AllocFail` and returns NULL. | PASS after repair: `charData` is initialised to NULL and the draw returns on `tiles == NULL \|\| charData == NULL` before any dereference (the first revision read an uninitialised pointer on that path) |
| G8 Asset pipeline | `res/graphics/map_popups/meson.build` builds `area_win_gra.narc` from an order file; the only reader (`MapNamePopUp_LoadAreaGfx`) indexes `windowID*2`, so appended members 18–20 are invisible to it. | PASS |

No blocker was found, so the pilot was implemented.

## 2. Design (bounded)

- **What it is:** a 104×40 px (13×5 tile) Platinum-native card to the right of the existing popup, in the same 2 px white border / 2 px black shadow / rounded-corner style, rising 9 px above the sign. Layout in the window: tiles 0–16 popup, 17 gap, **18–30 card**, 31 margin.
- **Hook:** `MapNamePopUp_DrawAreaCard()` called once in `MapNamePopUp_DrawWindowFrame`, after the popup blit and before `Window_CopyToVRAM`. No signature, struct, header, caller or script change.
- **Eligibility:** `entryID == LocationNames_Text_EternaForest && windowID == POPUP_STYLE_FOREST (4)`. The outside gate header shares the text ID but uses the route style, so it gets no card.
- **Time of day:** `GetTimeOfDay()` → day (morning/day), dusk (twilight), night (night/late night). Chosen once per show; the popup is on screen ~1.5 s so mid-display change is ignored. Variants differ only by which palette indices they use, never by palette.
- **Fail closed:** a short resource skips the blit (vanilla popup unchanged); temporary buffer is freed on every path.

### Artwork
Procedural and Platinum-native: `tools/visual_overhaul/io_preview/build_eterna_forest_card.py` writes `res/graphics/map_popups/card_eterna_forest_{day,dusk,night}.png`, using the 16 colours of `forest_popup.png` read from that file. **No HGSS or FireRed pixels** (Pixel use: none). Static mockup of popup + card: `io_preview/eterna_forest_card_mockup.png` (data-level composite, **not** an emulator capture; the popup's map name text is not drawn in it). The art is a first pass and **needs human art-direction review**; dusk/night are limited by the forest palette having only one true dark.

## 3. HGSS / FireRed references (from existing research, not re-read)

- **HGSS** (primary): area preview shown on map entry with time-of-day variants; provides the idea and the card-beside-name composition. HGSS uses a separate preview module/screen; that was **not** ported. Platinum already has a name popup host, so the pilot draws into it.
- **FireRed** (corroboration only): per-area style, visit-gated hold (120 vs 40 frames) and B-to-skip. **Not implemented**: the pilot must not change popup timing or input; those stay candidates for a later slice.
- `IO-CARD` soft dependency (shared still-card host) is not used: the field popup host is lighter and the still-card app is a separate child process.

## 4. Resource ownership

| Resource | Owner | Lifetime |
|---|---|---|
| BG3 tilemap rows 0–4, window pixels (32×5 tiles) | existing popup `Window` (`MapNamePopUp_CreateWindow`) | `MapNamePopUp_Create` … `_Destroy`; **no change** |
| BG palette slot 7 | existing `MapNamePopUp_LoadAreaGfx` (forest NCLR) | overwritten each show; card adds none |
| Card NCGR (2080 B + header) | temporary `Graphics_GetCharData`, `HEAP_ID_FIELD1` | allocated and freed inside `MapNamePopUp_DrawAreaCard` |
| NARC members 18–20 of `area_win_gra.narc` | build (`map_popup.order`) | static ROM data |
| OAM / other BG layers / VRAM banks / heaps | none | untouched |
| Persistent state | none (no new fields) | n/a |

## 5. Files

- `src/overlay005/map_name_popup.c` — card constants, eligibility/time-of-day selection, `MapNamePopUp_DrawAreaCard`, one call in `MapNamePopUp_DrawWindowFrame`.
- `res/graphics/map_popups/{meson.build,map_popup.order}` + three card PNGs.
- `tools/visual_overhaul/io_preview/{build_eterna_forest_card,validate_eterna_forest_card,render_mockup}.py`.
- `.github/workflows/validate-io-preview.yml` — builds `nitrogfx`, checks the committed PNGs match the generator, runs the static gates, uploads the mockup.
- This document; ledger row updated.

## 6. Validation performed (verified)

Repair commit on PR #86 (SHA and CI run IDs are in the PR description).

- **`validate-io-preview` failure cause (first commit):** the "Card art is reproducible" step died with `ModuleNotFoundError: No module named 'PIL'`. `pip install pillow` had succeeded, but the step ran `python -I`; isolated mode ignores the user site-packages where pip had installed it. This was a workflow bug, not an art/determinism problem. Fixed by dropping `-I` in the workflow (the checked-in tools are trusted repo code). Locally the same generate-then-compare step and all gates were rerun and pass.
- **Static gates** (`validate_eterna_forest_card.py --nitrogfx … --mockup …`): all pass, including NARC order/indices, style/header checks, hook order, palette identity, index range, the new NULL-handling gates, and NCGR tile stream == PNG tile order (65 tiles, 2080 B per variant).
- **Load-failure handling:** see G9; covered by two new gates.
- **`clang-format` 19.1.1:** clean.
- **ROM build / G7:** results recorded in the PR description from CI on the repaired commit. G7 `validate_g76_atmosphere` fails with `frozen gameplay/geometry data changed: res/field/scripts/scripts_solaceon_town_pokemon_news_press.s`. That check diffs against the pinned pre-G7.6 `BASE_REV` 89657070 and flags any change under `res/field/scripts/`; `main` itself differs from that base in exactly that file (IO-CARD, PR #81), and every g7-visual-validation run since the IO-CARD PR (runs 61–67, including docs-only PR #85) fails. This PR changes nothing under `res/field/`, so the failure is **pre-existing, not a regression**; it is deliberately not fixed here.

## 7. Runtime/visual QA still required (not run)

Record build SHA, ROM revision, emulator/version, steps and screenshots/video for each.

1. Enter Eterna Forest from Eterna Forest outside gate and via Fly/warp/Dig: card appears beside the name at day, dusk and night (change RTC/in-game clock); no card on the outside gate map, Fullmoon Island forest, or any other map.
2. Slide-in/out is smooth, card moves with the sign and fully disappears; map name text unchanged and not overlapped.
3. Walk between two popups quickly (re-show during hold and during slide-out): no stale card, no tile garbage; leave Eterna Forest for a non-card map and confirm the window is clean.
4. Press A / open menu / start a script during the popup: `MapNamePopUp_Hide` clears both.
5. Battle, menu, Poketch and map-change return: no BG3 leakage, text windows unaffected, no heap assert.
6. Rev 0 and Rev 1 ROMs.
7. Art-direction sign-off for the three variants; confirm card and sign read together (right edge not clipped on hardware/emulator overscan).

## 8. Rollback

Remove the `MapNamePopUp_DrawAreaCard` call (popup path is then byte-for-byte vanilla in behaviour); optionally drop the card members from `map_popup.order`/`meson.build`.

## 9. Not done / follow-ups

Visit-gated hold and skip; other locations; per-area art volume; any change to popup timing; Eterna Forest outside-gate card.
