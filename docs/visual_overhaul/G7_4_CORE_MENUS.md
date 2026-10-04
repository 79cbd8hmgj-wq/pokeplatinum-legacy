# G7.4 — Core Menu Modernization

Branch: `claude/visual-g7-core-menus-scr776` (from `origin/main` @ `d7c1ec09`). Resource-only; no C, gameplay or save changes.

## Ownership traced

| Surface | Generator | Resources |
|---|---|---|
| Party | `generate_party_menu_ui.py` | `res/graphics/party_menu/{cursor,button}.png`, `shared.pal` (banks 0/1) |
| Summary | `generate_summary_ui.py` | `pokemon_summary_screen/{tab_arrow,move_cursor}.png`, `tiles_main.pal`, `sprites.pal` |
| Bag | `generate_bag_ui.py` | `bag/bag_ui_main.pal`, `bag/ui_elements.pal` |
| Start | `generate_start_menu_ui.py` | `start_menu/cursor.png` |
| Shop | `generate_shop_ui.py` | `shop_menu/{default,frontier,sprites}.pal` |

`generate_ui_foundation.py` was not touched (no shared global chrome change needed).

## Visual changes

- **Party:** focused member-card cursors gain heavy gold corner brackets (shape cue, not color-only); focused buttons get an inset white ring; normal buttons get a deep base edge. Cell/OAM geometry, palette banks 0/1 unchanged.
- **Summary:** active move cursor gets heavy corner brackets (alternate stays thin); tab arrow is a bolder navy-rimmed chevron; shared chrome palette entries 2 (edge) and 15 (separator) firmed up in banks 0-9 for stronger section separation. Page-specific entries and the bank 7/8 entry-6 exceptions untouched.
- **Bag:** steel/rail ramp (entries 3-5) deepened for row/pocket separation; item/pocket focus frame (`ui_elements.pal` entry 1) moved from retail red to the G7 gold focus accent; blue accent entry 4 deepened. Pocket-specific colors untouched.
- **Start:** cursor frame gets a mirrored trailing chevron, corner studs and a dark rim so it reads as a focus plate.
- **Shop:** same steel ramp as Bag on both shop palettes (accent entries 9-15 keep normal vs Battle Frontier identity); selection cursor frame red → gold.

## Functionality preserved

Pixel dimensions/modes of all edited PNGs, palette entry counts, cell/anim JSON and tilemaps are unchanged; every page, pocket, menu entry and touch/button path is untouched.

## Validation

- `tools/visual_overhaul/validate_g7_core_menus.py` (new): PNG size/mode/index-range vs `d7c1ec09`, only-allowed-palette-entries-changed, and generator idempotency for all five generators — **passed**.
- All five generators re-run: no further diff.
- `validate_overhaul.py --no-write`: not run (no shared integration plumbing touched; note it rewrites two docs reports as a side effect).
- US Rev 0 / Rev 1 builds: **not run locally** — the container has no CodeWarrior/Wine toolchain. They run in the `build` workflow on PR.

## Deferred (invasive)

- Re-tiling Bag/Summary/Party tilemaps for fewer decorative elements and true tab pills.
- Recoloring Start menu icon banks / adding a panel plate behind icons.
- Rebuilding `item_highlight`/`pocket_highlight` as filled-plate focus states.
- Per-pocket accent recolors.

## Owner runtime checklist (portrait stacked + landscape side-by-side)

- **Party:** full team, single Pokémon, fainted/statused member, cursor on each slot and on buttons, touch buttons.
- **Summary:** every page, stats, moves (cursor on each, swap mode), contest moves, ribbons, long names, egg/shiny/Pokérus/marking states, tab arrows.
- **Bag:** every pocket, long item names, large quantities, item focus, touch pocket switching, item move mode.
- **Start:** all unlocked entries (incl. Underground variant), touch and button navigation.
- **Shop:** normal shop and Battle Frontier shop, long item names/prices, cursor and scroll arrow.
