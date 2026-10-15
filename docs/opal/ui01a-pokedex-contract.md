# UI-01A — Pokémon Opal Pokédex screen and asset contract

**Status:** Source-backed preimplementation census. No in-game redesign has been applied. Based on `main` as of 2026-10-10; kept independent of draft Bag PR #108.

## Code ownership

- App lifecycle, touch initialization and transitions: `src/applications/pokedex/pokedex_main.c`; explicit states `POKEDEX_STATE_TRANSITION_IN`, `POKEDEX_STATE_USE`, `POKEDEX_STATE_TRANSITION_OUT`, `POKEDEX_STATE_WAIT_EXIT`.
- Backgrounds, cursors, sprite graphics, text manager and resource NARC: `src/applications/pokedex/pokedex_graphics.c`; loads `NARC_INDEX_RESOURCE__ENG__ZUKAN__ZUKAN`.
- Browsing/list: `pokedex_panel.c`, `pokedex_updater.c`, `pokedex_text.c`, `pokedex_text_manager.c`; navigation implementation additionally distributed across `ov21_*.c` files and needs finer trace before source edits.
- Search user flow: `pokedex_search.c`, including `SS_MENU`, `SS_SEARCH`, `SS_LOADING`, `SS_RETURN`, `SS_EXIT`.
- Sorting/filtering data: `pokedex_sort.c`; includes National/Sinnoh order, alphabetic, height, weight, type, body shape, form and caught/unseen filtering paths.
- Species information and alternate screens: `infomain.c`, `infomain_foreign.c`, `formmain.c`, `formsub.c`, `crysub.c`, `footprint.c`, `pokedex_height_check.c`, `pokedex_field_map.c`.

## Graphics archive map

`res/graphics/pokedex/` has 128 directory entries and its own `meson.build` and `pokedex.order`. Categories below are **file-group evidence**, not verified layer ownership.

| Screen group | Examples of resources | Integration hazards |
| --- | --- | --- |
| Scroll/list | `scroll_main_background.png`, `scroll_main_background.NSCR`, `scroll_sub_background.png`, `scroll_sub.NSCR`, `scroll_wheel.png`, `scroll_wheel.NSCR`, `cursor.png` | 4bpp backgrounds versus 8bpp wheels; scroll and touch geometry |
| Sinnoh/National selection | `background_scroll_sinnoh.pal`, `background_scroll_national.pal`, `banner_sinnoh.NSCR`, `banner_national.pal` | Distinct dex modes and palette bindings |
| Search/filter | `search_main.NSCR`, `search_sinnoh.NSCR`, `search_national.NSCR`, `search_filter*.NSCR`, `search_buttons.png`, `search_body_shapes.png` | Interactive filtering and empty/searching states |
| Species information | `info_main.NSCR`, `info_sub.NSCR`, `info_entry_window.NSCR`, `info_species_window.NSCR`, `entry_main.png`, `entry_sub.png` | Main/sub synchronization, seen/caught text masks |
| Forms/languages | `forms_sub.NSCR`, `form_display_box.png`, `foreign_entry_window.NSCR`, `info_language_buttons.png` | Form unlocks, alternate-language presentation |
| Cry and comparisons | `cry_sub.NSCR`, `cry_wheel.png`, `cry_dials.png`, `height_check_main.NSCR`, `weight_check_main.NSCR`, `weight_scale.png` | Audio/touch callbacks and special sprite representations |
| Area/encounters | `area_map.NSCR`, `area_sub.NSCR`, time-of-day palettes, special-location NSCR files | Location maps and time-dependent data |
| Shared navigation art | `page_buttons.png`, `scroll_buttons.png`, `type_icons.png`, `name_tag.png`, `unseen_icon.png` | Hitboxes, sprite cells/animations, palette compatibility |

## Required design and engineering constraints

1. Use the established Opal V3 vocabulary: pearl/off-white surfaces, mineral violet, subtle opalescence and restrained gold; preserve DS readability and avoid neon effects.
2. Keep National/Sinnoh mode, seen/caught masking, sorting, searching, filters, forms, foreign-language details, footprint, cries, height/weight and location views functional.
3. Treat MAIN and SUB display elements separately; confirm actual BG layer and OAM order from loader paths before repositioning any interface content.
4. Preserve touch rectangles, scroll wheel sensitivity, page movement and cursor behavior unless an intentional interaction redesign is separately specified.
5. Keep existing `pokedex.order` archive position relationships and 4bpp/8bpp encodings. Use source-controlled deterministic asset generation and tilemap checks; validate PNG signature, chunk integrity, palette cardinality and Nitro tile index budgets before upload.
6. Preserve native Sinnoh/National selection and relevant international form functionality. Do not infer that source module existence means its visual design is complete.

## Bounded implementation sequence

**UI-01B:** Scroll/list presentation on both LCDs, including banner, list frame and focus/cursor. First audit direct graphics-loading calls and pixel-coordinate contracts; prototype **only** scroll assets without modifying shared search/info resources. Run both ROM revisions, verify asset generation, then emulator test empty/populated lists, top/bottom scrolling and Sinnoh/National transition.

**UI-01C:** Species entry/information panels, caught/seen masking, forms and foreign descriptions; independently audit alternative screens before implementation.

**UI-01D:** Search/filter UI and all selector cases, including results/no-results and sorting.

**UI-01E:** Area/cry/footprint/height/weight screens; final two-screen cohesion audit and comprehensive runtime test matrix.

## Required sign-off matrix

| ID | Runtime scenario | Expected behavior |
| --- | --- | --- |
| DEX-01 | Open/close Dex; transition in/out | No blank LCD, sprite remnants or frozen input |
| DEX-02 | Browse seen versus unseen and caught entries | Correct masking and display labels |
| DEX-03 | Scroll first/middle/last species and switch National/Sinnoh | Focus, index, sprite and list match |
| DEX-04 | Search by type, name, form and sort modes | Correct displayed results and responsive controls |
| DEX-05 | Zero-result search and cancel | No stale search banners/windows |
| DEX-06 | Open species description pages | Text/graphics readable on both displays |
| DEX-07 | View alternate forms and available foreign entries | Correct forms and unlock conditions |
| DEX-08 | Inspect cry page and touch wheel | Sound interaction preserved and visual cues aligned |
| DEX-09 | Height/weight and footprint views | Comparison sprite/labels unclipped |
| DEX-10 | Habitat/area pages, time variants, special maps | Accurate map state and palette |
| DEX-11 | Navigate with buttons and stylus across screens | Correct touch affordances and focus feedback |
| DEX-12 | Repeat on US rev0 and US rev1 | Builds and state transitions work on both |

**Gate:** UI-01A is documentation, not an implementation or runtime certification. Require all asset owners and touch/BG geometry traced before the first source or graphical patch. Keep Bag PR #108 independent until it receives runtime sign-off.
