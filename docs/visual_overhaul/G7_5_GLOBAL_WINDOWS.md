# G7.5 — Global Window / Typography-Adjacent Polish

Status: **implemented (generator-backed art only); validated; owner runtime review pending**

Starting commit: `49aaf40b` (main, post-G7.4).

## 1. Ownership / resources

| Resource | Owner | Consumers | G7.5 result |
|---|---|---|---|
| `standard_system.png`, `standard_field.png` (24×24) | `generate_ui_foundation.py` | `LoadStandardWindowTiles` (system/field frames) | Audited: already navy outline `#1C2D42`, cool light fill, teal field. **No change** (no beige/olive left). |
| `message_box_00`–`04` (frames 1-5) | `generate_message_frames.py` (G7.2B) | Options > Frame; field, battle, party/bag help, egg hatch | Audited, **no change** |
| `message_box_05`–`19` (frames 6-20) | retail decorative art | player-selected only | **Untouched** (pinned by SHA in validator) |
| `scroll_cursor.png` | `generate_ui_foundation.py` | `DrawMessageBoxScrollCursor`, `TextPrinter_DrawScrollArrow` | **Rebuilt** |
| `wait_dial.png` | `generate_ui_foundation.py` | `Window_AddWaitDial` / `DrawWaitDial` | **Rebuilt** |

Key trace: the cursor/dial are blitted onto the message frame's right-hand bar
(frame tiles +10/+11, cell at `x+width+1..+2`, `y+2..+3`) and drawn with the
**frame palette** (bank passed to `Window_DrawMessageBox`), not the standard
window palette. No single bright palette index is safe across all 20 selectable
frames. Entries **1 and 10** form a complementary polarity pair instead: across
the full frame family, at least one of the two has >= 4.67:1 contrast against
the right-hand bar. The generated cursor/dial therefore use both indices in
their visible shape. The bar is 11 px wide; cols 11+ are the frame
outline/halo/transparent edge.

Tile layout: `scroll_cursor.NCGR` = 12 tiles = 3 frames × 2×2 tiles (printer
cycles frames 0,1,2,1; blit takes source cols 4.. → bar cols 1..). `wait_dial`
= 8 frames × 16×16 (tick every 16 frames).

## 2. Defects fixed (concrete)

* Pass G had authored the cursor as twelve independent 8×8 frames; at runtime
  those tiles are reassembled as three 16×16 frames, so the chevron was
  scattered/cropped across four tiles per frame. Now authored in 16×16 cell
  coordinates and scattered into the tile strip.
* The wait dial spanned cols 1-14, painting over the frame outline and the
  transparent edge. It is now confined to cols 0-9 and every visible dot uses
  the entry-1/entry-10 polarity pair so decorative frames cannot turn the
  spinner into a same-tone indicator.

## 3. Visual changes

* Scroll cursor: 9×6 two-tone triangle using entries 1 and 10; the same shape
  remains readable whether a selected frame maps entry 1 light/dark or uses a
  near-white right-hand bar. Three-frame 1 px bounce (y 4/5/6) is preserved.
* Wait dial: radius-4 ring at the same 8 positions/order. Head/trail/rest differ
  by pixel shape, while each visible dot includes both polarity colors.

## 4. Preserved

Image sizes/modes (`scroll_cursor` 96×8, `wait_dial` 16×128), frame counts,
animation timing, tile/palette contracts, C source, text field fill (entry 15),
frame entries 1-4, message speed, line capacity, font, encoding, printer.
No C, save, or gameplay change.

## 5. Files changed

* `tools/visual_overhaul/generate_ui_foundation.py`
* `res/graphics/windows/scroll_cursor.png`, `res/graphics/windows/wait_dial.png`
* `tools/visual_overhaul/validate_g7_global_windows.py` (new)
* `docs/visual_overhaul/G7_5_GLOBAL_WINDOWS.md` (this file)

## 6. Validators

`validate_g7_global_windows.py` (standard palette, cursor/dial tile geometry and
bounds, bounce, **all-20-frame polarity contrast**, frames 6-20 SHA pins); re-run of
`validate_g7_message_frames/battle_hud/battle_command_ui/core_menus`; generators
re-run with no diff.

Note: `validate_g7_core_menus.py` regenerates `.pal` files with LF endings where
the repo stores CRLF in this checkout; unrelated to G7.5, reverted before commit.

## 7. Builds

**Not run in the authoring sandbox.** `make rom` stopped at meson configure:
`wrapdb.mesonbuild.com` (rapidjson patch) returned 403 from the environment
network policy (metroskrew, `libc6-i386`, flex and arm gcc were installed
successfully). The change is PNG-only (same dimensions/mode, no C or meson
change), so the existing CI matrix (`.github/workflows/build.yml`, Rev 0 + Rev 1)
is the build evidence; both results are pending.

## 8. Deferred

* Battle-only vs field-only frame variants: frame art and palette are chosen
  once from Options > Frame for every consumer; separating them needs C changes.
* Cool text-field fill: font palette and frame fill must change together.
* Font/typography: untouched. Font palette is `PL_FONT` member 7 (bank 11); font
  glyph pipeline not changed.

## 9. Owner runtime checklist

Portrait stacked and landscape side-by-side, check: ordinary field dialog, sign,
Yes/No, battle message, party/bag/summary help panes, egg hatch (or other special
text), Frames 1-5, several of Frames 6-20, scroll cursor (all 3 bounce positions,
visible on each frame), wait dial (trade/Wi-Fi/save-style waits), long wrapped
messages. Confirm: no seams, no clipping, readable text, no palette clash,
cursor/dial visible and inside the bar, unchanged input/message timing.
