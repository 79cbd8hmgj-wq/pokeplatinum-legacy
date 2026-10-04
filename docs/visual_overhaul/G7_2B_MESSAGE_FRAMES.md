# G7.2B — Battle Text-Window Frame (plain frame family)

Status: **implemented (palette-only); build-verified locally; owner runtime review pending**

Parent: `G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md` (G7.2, text-window bullets;
also the first slice of G7.5 because the frame is global).
Starting commit: `a2453670` (G7.2A).

## 1. Ownership trace

* The battle message window is `Window_Add(..., 27 × 4 tiles ...)` +
  `Window_DrawMessageBoxWithScrollCursor(window, 0, 1, 10)`. Its **frame art and
  frame palette come from the player's Options > Frame setting**:
  `BattleSystem_GetOptionsFrame` → `ReplaceTransparentTiles(..., frame)` and
  `PaletteData_LoadBufferFromFileStart(PL_WINFRAME, GetMessageBoxPaletteNARCMember(frame), …, PLTT_DEST(10))`.
  Text itself is printed with the font palette (`PL_FONT` member 7, bank 11),
  letter/shadow/field = 1/2/15.
* `Options_Init` defaults to `OPTIONS_FRAME_1` → `res/graphics/windows/message_box_00.png`,
  the muddy brown/beige-gradient frame that gave battle (and every field dialog)
  the retail look. Frames 2-5 (`message_box_01`-`04`) are the other plain-field
  frames (olive-gray, blue, red, green). Frames 6-20 are decorative, explicit
  player choices.
* The same frame resource is used by the field message box, battle party/bag
  text panes and egg-hatch — so this change is **global by construction**; the
  battle text window cannot be restyled separately without C changes.

## 2. What changed

`tools/visual_overhaul/generate_message_frames.py` (palette-only, idempotent)
rewrites, in `message_box_00`…`04.png`:

* entry 14 (outline, was green-black `#293129`) → deep navy `#0C1428`, all five;
* the three gradient entries (11-13) → frame 1 navy, frame 2 steel, frame 3 vivid
  blue, frame 4 crimson, frame 5 emerald (same hue families as retail, minus the
  beige/olive muddiness).

Entry 15 (field fill / 1 px halo, pure white) is **deliberately untouched**:
battle and field windows fill their interior with the font palette's white, so
changing the frame's own fill would create a visible seam. Entries 0-10 are
retail (including per-frame entry 2), and pixel indices are pinned by SHA-256.

Not changed: window geometry (still 27×4 tiles → same line capacity),
`TextPrinter`/message speed, scroll cursor, frames 6-20.

## 3. Validation (local)

| Check | Result |
|---|---|
| `generate_message_frames.py` rerun | no diff |
| `validate_g7_message_frames.py` | pass |
| `validate_g7_battle_hud.py`, `validate_g7_battle_command_ui.py` | pass |
| `make rom ROM_REVISION=0` | ROM sha256 `3c2380aa536472505154d9b4a8b1998886a86640edbef30ff4e09ac59853435d` |
| `make rom ROM_REVISION=1` | ROM sha256 `2268ab8158ee65bd76a76aab5ca66787cc0dc1d5523e7e6ebf612318d17a32ec` |

## 4. Deferred

* A battle-only cooler/darker text field (e.g. cool-white fill instead of pure
  white) needs the font palette's field entry and the frame fill to change
  together and a per-context choice between battle and field — a C-side change
  to palette loading, left until the owner has judged this pass.
* Decorative frames 6-20: untouched by design.

## 5. Owner runtime review

Check each of Options > Frame 1-5 in portrait and landscape:

1. Battle text window (wild intro, move messages, 4-line wrap) — gradient edge,
   navy outline, no seam between frame and text field.
2. A field dialog, a sign, the party-screen help pane, and a Yes/No box.
3. Scroll-cursor wait arrow position/colour on the new frame.
