# MO1-1 — Bag Rendering / Input Map and Implementation Boundary

Status: SOURCE-MAPPED DESIGN HANDOFF (not implemented or runtime verified)
Parent: PR #107, `MO1_BAG_OVERHAUL_SPEC.md`
Baseline: main branch at 3f94034bf0da6173d1677b215d26e05daad46e1b
Scope: avoid changing inventory semantics or shipping a cosmetic-only Bag patch.

## Source-grounded screen ownership

### Main engine (currently item browsing and descriptions)
- `src/applications/bag/main.c:SetupBGLayers` initializes MAIN BG0, BG1, BG2, BG3 in mode 0.
- `windows.c:BagUI_CreateWindows`: item list on MAIN BG2, tilemap origin (14,0), width 17 tiles, height `TEXT_LINES_TILES(BAG_UI_NUM_VISIBLE_ITEMS)`.
- Description on MAIN BG0, tilemap origin (0,18), full 32-tile width, 3 text lines.
- Pocket names on MAIN BG2 at (0,13), pocket indicator on MAIN BG0 at (0,11).
- Message windows, item actions, count/quantity, money and Poffin windows all use MAIN BG0 and may overlap or replace normal-mode presentation.
- MAIN BG1 renders `bag_ui_main_tileset.png` with `bag_ui_main.NSCR`; MAIN BG3 renders `item_list_border.NSCR`.
- `ItemListMenuCursorCB` already refreshes description and selected item sprite; guard `isMovingItem` stops routine refresh during sorting.
- `ItemListMenuPrintCB` specializes TM/HM numbering, berry numbering, registered-item marker and item quantity: preserve those formats.
- `BagUI_PrintTMHMMoveStats` and existing move type/category sprite resources already provide TM/HM context. Recompose; do not reimplement move calculations.

### Sub engine (currently touch-driven pocket controls)
- `SetupBGLayers`: SUB BG0 and BG1 static, SUB BG3 affine; SUB BG2 is not initialized here.
- `LoadGraphics` loads `pokeball_borders_tileset.png` / `pokeball_borders.NSCR` onto SUB BG1, `pokeball_inside.png` / `pokeball_inside.NSCR` onto SUB BG3, `buttons.png` onto SUB BG0.
- SUB BG3 is rotated about DIAL_CENTER_X/Y and is actively used for dial-based scrolling.
- Touch pocket buttons use explicit rectangles. Eight-pocket layout covers multiple side and lower portions (e.g. 8-47/32-71, 80-119/144-183, 208-247/32-71), with separate layouts for 1, 4 and 7 pockets.
- The dial has separate pressed and held zones and is also used during sorting and quantity workflows. Touch overlay space is NOT vacant.
- In `sprites.c`, most bag assets, item icon, type/category icons and highlights are MAIN OAM; a limited button sprite is SUB OAM.
- Current allocated VRAM banks: MAIN BG 128K A, MAIN OBJ 128K B, SUB BG 128K C, SUB OBJ 16K I. These are reservations, not evidence of free budget.

## Architectural ruling: two-stage screen redesign

The original MO1 concept suggests top details and bottom item list. This is **not** a graphics-only change: migrating `ListMenu` onto the sub engine requires relocating windows/font resources, changing sprite display engine, moving pocket hitboxes, and replacing/reworking dial gestures. Do not claim screen inversion is feasible until a minimal sub-screen text/list prototype has been compiled and tested.

**Recommended MO1-1 implementation first:** retain list/menu/confirmations on MAIN, recompose MAIN list/description/pocket indicator into legible Opal panels, and restyle SUB pocket/dial visualization without changing touch geometry. This delivers a redesigned Bag and preserves working interaction semantics, while independently prototyping eventual touch-list browsing. If the touch-list prototype passes every guard, a separate MO1-2 architecture decision may promote it.

## Proposed MO1-1 work units (implementation, not approval theater)

1. **Layout constraints + graphics:** change `res/graphics/bag/bag_ui_main_tileset.png`, `bag_ui_main.NSCR`, `bag_ui_main.pal`, `item_list_border.NSCR`, selected button/border graphics and palettes; retain existing archive order/IDs. Establish a coherent Opal panel system with visible active-pocket, selected-row, item-count, description and TM/HM hierarchy. Avoid wasting limited pixels on decorative headers.
2. **Window recomposition:** change `src/applications/bag/windows.c` positions and sizes only after accounting for menu messages, item sorting, sell count, quantity, Poffin and TM/HM output; update base-tile budget arithmetic if dimensions change. Keep at least retail-equivalent visible rows and readable wrapped descriptions. Confirm duplicate tile reservations are used in mutually exclusive states before reuse.
3. **Sprite consistency:** adjust `src/applications/bag/sprites.c` only for necessary alignment of item icon, highlight, selected pocket and TM/HM icons. No new resource loaders unless an actual art composition requires them.
4. **Refresh safety:** in `main.c`, use `ItemListMenuCursorCB`'s existing scheduled updates for normal selection redraws. Avoid per-frame full window redraws, new blocking transitions or item-effect code changes.
5. **Conditional touch-list feasibility spike:** create an isolated prototype branch (no merge into MO1-1) that tests readable item list on SUB with D-pad and stylus hitboxes, while preserving dial/sorting/quantity behavior; record VRAM/OAM/window usage, build success and emulator screenshots. Only then reconsider the top-details/bottom-list split.

## Acceptance and regression matrix

- Normal pockets: empty, one item, overflow list, long names, 1/4/7/8 accessible pocket variants; select, move/sort, cancel, repeat pocket switch, saved cursor restoration.
- Item-specific: normal Use, Give, Register/Unregister, key item, Berry, TM and HM, held item, inaccessible/disabled command, trash confirmation.
- Special modes: shop sell and sell quantity, gardening, Poffin, multiplayer, give-to-Pokémon, move-related prompt, item count dialog, message/Yes-No.
- Input: D-pad and shoulders (where provided), stylus pocket buttons, dial press/hold/rotate, rapid repeated inputs, touch edges.
- Rendering: item icon palette, long desc lines, 3-line description, move type/category data, registered-item marker, empty-list Cancel, top/bottom palette integrity.
- Builds: both US Platinum revisions; capture top/bottom screenshots in emulator and record real measured input count before/after. Static lint and build success are necessary but not runtime proof.

## Non-goals for MO1-1
- Do not change `MakeItemActionsMenu`, item permission checks, inventory data format, capacity, item effects or special Bag state logic.
- Do not advertise quick-action touch buttons in MO1-1; they belong to MO1-2 after feasibility and eligibility checks.
- Do not flatten dial controls or hide existing special-mode dialogs.
- Do not claim the two-screen layout was reversed, or that an emulator test was done, until evidence exists.

## Implementation handoff (bounded)
Inspect these first: `src/applications/bag/{main.c,windows.c,sprites.c}`, `res/graphics/bag/{bag_ui_main_tileset.png,bag_ui_main.NSCR,bag_ui_main.pal,item_list_border.NSCR,buttons.png,pokeball_borders.NSCR,pokeball_inside.NSCR,meson.build}`. Preserve archive order and unused assets. Recompose the existing MAIN layout and SUB frame within current hardware allocations. Do not investigate unrelated subsystems. Produce both-revision builds and before/after captures; stop and report genuine VRAM/window/input blockers rather than silently weakening the design.
