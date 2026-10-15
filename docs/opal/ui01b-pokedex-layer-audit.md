# UI-01B — Pokédex dual-screen layer audit

This is a source-based checkpoint for the *future* composition pass; it is **not** evidence that new full-screen artwork is installed.

## Confirmed background graph

From `src/applications/pokedex/pokedex_graphics.c::InitBackgrounds`:

| LCD | Layer | Priority | Mode | Implementation constraint |
| --- | --- | --- | --- | --- |
| Main | BG1 | 0 | Text, 16-color | Frontmost background among initialized main layers |
| Main | BG2 | 1 | Text, 16-color | Behind BG1 |
| Main | BG0 | 2 | Separately configured | Must preserve window/text plane |
| Main | BG3 | 3 | Text, 16-color | Rearmost initialized main layer |
| Sub | BG1 | 0 | Text, 16-color | Frontmost initialized sub background |
| Sub | BG3 | 1 | Affine, 256-color | Distinct pixel/rotation semantics |
| Sub | BG2 | 2 | Text, 16-color | Rearmost initialized sub layer |

The code initializes six BG templates with 256×256 screen size. BG0 is assigned priority rather than initialized in that function. Backgrounds and sprites have independent layering; this table does not establish OAM priority or visibility.

## Asset constraints

- `scroll_main_background.png` is an indexed 4bpp 256×64 strip; `scroll_sub_background.png` is indexed 4bpp 256×24. These are *not* full 256×192 backgrounds.
- `scroll_main_background.NSCR` and `scroll_sub.NSCR` are separately packed maps.
- `scroll_wheel.png` is built as 8bpp, and SUB BG3 is affine/256-color. Do **not** run an indiscriminate 4bpp recolor on these.
- Meson builds `zukan.narc` using `pokedex.order`, so archive asset positions must remain stable.

## Remaining before actual compositor/layout modification

1. Trace the per-state graphics calls in scroll module(s): source NARC member, palette slot, BG layer, tilemap offset, window clipping and OAM position.
2. Map scrolling/touch geometry separately for stylus and button inputs and compare to the rendered dial.
3. Decide which ornamental elements can be changed inside existing strip/tile budgets. The current main atlas contains 256 tiles (256×64 / 8×8); its NSCR highest observed tile index 197 fits within that capacity. The sub atlas contains 96 tiles (256×24 / 8×8) and its indices also fit. For changed artwork, still prove NSCR and VRAM safety before committing.
4. Implement the resulting art in a coordinated patch, rather than changing an isolated color bank and treating the screen as complete.
5. Emulator sign-off: compare list/scroll top, middle and bottom and Sinnoh/National transitions on both LCDs.

The automated `tools/opal_pokedex/validate_screen_contract.py` source guard protects the layer graph against accidental changes but does not substitute for actual rendering or input tests.
