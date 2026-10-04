# G7.1A — Battle Command Menu

Status: **implemented; build-verified; owner runtime review pending**

Parent plan: `G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md` (G7.1, first task).
Source commit the batch started from: `7962fb89` (current `main`).

## 1. Ownership trace (before any edit)

The Fight / Bag / Pokémon / Run interface is a **mixed** surface owned entirely
by `src/battle/battle_subscreen.c`:

| Visible component | Mechanism | Resource |
|---|---|---|
| Big red FIGHT key, orange BAG, green POKéMON, blue RUN | **BG tilemap** on sub-engine BG0 (`BG_LAYER_SUB_0`), prio 2 | tilemap `pl_batt_bg.narc` #0x2A (42); tiles #28 (`0x6000` bytes, 4bpp); palette banks 1-4 of #242 |
| Gray "ghost" move wells behind FIGHT | **BG tilemap** on BG1 (`BG_LAYER_SUB_1`), prio 3, alpha-blended 8/12 (`G2S_SetBlendAlpha(BG1…)`) | tilemap #0x2F (47), bank 13 |
| Deck backdrop, header/footer bands, emblem | **BG tilemap** on BG2, prio 3 | tilemap #0x31 (49), bank 0 (per-terrain, see below) |
| FIGHT / BAG / POKéMON / RUN labels | **sprites** (font-OAM text, white with a dark button-hue outline) | text palette bank 2 of `res/graphics/battle/interface/shared.pal` (source-backed, unchanged) |
| Focus brackets | **sprite** (4 flips of one 16×16 cell, bounce animation) | `res/graphics/battle/interface/cursor.png` (generator-owned) |
| Pressed state | **BG tile swap**: `ApplyMoveSlotTilemap` re-points the tilemap rect at the +0xC0 / +0x180 tile variants and the label sprite nudges 2 px | variant tile blocks in tile member #28 |
| Party ball strip / Poké icon | sprites | unchanged |

`pl_batt_bg.narc` is a **prebuilt** archive (342 members). There is no
source form of its tiles/tilemaps, so G7 treats the committed archive as the
edit target and owns the edited members through a deterministic generator
(`tools/visual_overhaul/generate_battle_command_ui.py`, helpers in
`nitro_narc.py`). The NARC writer round-trips the retail archive
byte-for-byte; only the members listed below are rewritten.

Palette plumbing relevant to the deck backdrop:

* `BattleSubscreen_New` loads all 16 banks from #242, then overwrites **bank 0
  only** with the per-terrain palette (`sSubscreenBgPlttIndices`, 17 members
  `0xF3-0x103`, `0x11C`; backgrounds `BACKGROUND_PLAIN`..`BACKGROUND_DISTORTION_WORLD`).
  Backgrounds ≥ 18 (Battle Tower/Factory/Arcade/Castle/Hall) have no terrain
  member and keep bank 0 from #242, which now holds the neutral deck. Battles
  carrying `BATTLE_TYPE_FRONTIER` load #340 / tiles #169 / tilemap #170 instead.
* `SysTask_UpdateSpeedUpPalette` swaps bank-0 entries 8-15 for the matching
  "speed-up" palette (`0x10B-0x11B`, `0x11D`; default `267`) while the touch
  fast-forward is held. These had to be retuned together with the normal
  palettes or the screen would flash back to the retail light backdrop.

## 2. Touch hitboxes and controller semantics (unchanged)

`sActionMenuTouchRects` (`{top, bottom, left, right}` in pixels):

| Result | Action | Rect |
|---|---|---|
| 1 | FIGHT | y 0x18-0x90, x 0x00-0xFF (full width) |
| 2 | BAG | y 0x90-0xC0, x 0x00-0x50 |
| 3 | POKéMON | y 0x90-0xC0, x 0xB0-0xFF |
| 4 | RUN / Cancel | y 0x98-0xC0, x 0x58-0xA8 |

* Touch is checked first (`TouchScreen_CheckRectanglePressed`), then the
  D-pad/button cursor (`BattleSystem_MenuKeys` → `BattleSystem_Cursor_Menu`,
  layout `sBattleMenuButtonLayout`).
* The focus cursor is drawn at the **touch rect** corners (rect ± 8 px), so
  the brackets frame the hit area, not just the painted key.
* `BattleSubscreen_ProcessActionInput` maps results 1-4 to the press
  animation; none of it was modified.

## 3. What changed

Asset-only. **No C source, no tilemap, no tile pixel, no cell/anim and no
touch-rect change.** Gameplay, input mapping, controller flow, save data and
battle calculations are untouched.

| File | Change |
|---|---|
| `res/prebuilt/battle/graphic/pl_batt_bg.narc` | 37 NCLR members rewritten by the generator (see below); every other member byte-identical to retail |
| `res/graphics/battle/interface/cursor.png` | focus bracket rebuilt (see below) |
| `tools/visual_overhaul/generate_battle_command_ui.py` | new — owner of the NARC edits |
| `tools/visual_overhaul/nitro_narc.py` | new — deterministic NARC / LZ10 / NCGR / NCLR / NSCR helpers |
| `tools/visual_overhaul/generate_battle_ui.py` | `make_battle_cursor()` redesigned (cursor palette is private to `cursor.png`) |
| `tools/visual_overhaul/validate_g7_battle_command_ui.py` | new — objective gate |

### Command keys (palette banks 1-4 of member #242)

* Entries 2-9 (light→dark ramp) and 10 (structural outline) retuned;
  entries 0, 1, 11-15 (transparent key, white, accent, greys, black) are
  retail values.
* FIGHT crimson, BAG amber, POKéMON emerald, RUN azure: higher saturation,
  deeper shade steps (stronger bevel/side-wall depth), and a deep-navy
  outline (`#0A1230`) replacing the retail `#313131` gray keyline.
* Keys are the same tiles as before, so FIGHT stays the dominant 224×88
  surface and the three secondary keys keep their retail footprint.
* Label legibility: the label outline colors in `shared.pal` bank 2 were
  already hue-matched to each key; the validator asserts ≥ 3:1 contrast
  between each label outline and its key fill.
* These banks are shared with the Yes/No, forget-move, switch-prompt and
  target-select keys, so the same language carries across every
  command-style sub-menu.

### Deck backdrop (bank 0)

* Retail light-gray field + pale emblem replaced by a dark, terrain-tinted
  navy "deck": field `v=0.17`, bands `v=0.09`, light edge lines, subtle
  lighter emblem. The tint hue/saturation per terrain comes from the retail
  palettes (recorded in the generator, not read back), so grass, water,
  snow, cave, etc. keep a recognisable accent.
* Speed-up palettes use the same hues, lifted, so the fast-forward cue is
  preserved (the screen brightens while held, as in retail).
* The BG1 alpha-blended ghost wells now read as slate recesses behind the
  keys instead of faint white outlines — this removes the empty-white
  filler without touching any tilemap.
* All text on this screen is drawn on keys (font-OAM), never directly on the
  backdrop, so the darker field cannot reduce text contrast. The Stop
  Recording prompt draws its own window frame.

### Focus bracket (`cursor.png`)

Retail was a 2 px red L on a light screen. It is now a 3 px **amber fill with a
white outer highlight and a navy keyline** (palette indices 14/15/1 of the
cursor's private palette). The shape is heavier than before so focus is not
carried by color alone, and the keyline keeps it readable over the dark deck,
over the red FIGHT key, and on the lighter Bag/Party sub-screens that share
the sprite. Cell, animation, OAM and palette allocation are unchanged.

### Pressed state

Already shape-based in retail and kept: pressing swaps in the +0x180 tile
variant (art compresses, top highlight removed, bottom lip shortened) and the
label sprite shifts, then settles through the +0xC0 variant. The new ramps keep
these frames distinct by luminance as well as geometry.

## 4. Validation

```
python3 tools/visual_overhaul/generate_battle_ui.py                 # cursor, no diff on rerun
python3 tools/visual_overhaul/generate_battle_command_ui.py         # first run updates, rerun: "no changes"
python3 tools/visual_overhaul/generate_battle_command_ui.py --check
python3 tools/visual_overhaul/validate_g7_battle_command_ui.py
python3 tools/visual_overhaul/validate_g6_showcase_integration.py
python3 tools/visual_overhaul/validate_area_light_contract.py
python3 tools/overhaul/validate_overhaul.py --no-write
make rom ROM_REVISION=0 / ROM_REVISION=1
```

### Evidence (local, this batch)

| Check | Result |
|---|---|
| `generate_battle_command_ui.py` rerun | `no changes` (idempotent) |
| `generate_battle_ui.py` rerun | cursor.png byte-identical |
| `validate_g7_battle_command_ui.py` | pass |
| `validate_g6_showcase_integration.py`, `validate_area_light_contract.py` | pass |
| `validate_overhaul.py --no-write` (core master validator) | `MASTER VALIDATION: PASS (33/33 children passed)` |
| `make rom ROM_REVISION=0` | success — ROM sha256 `5ba2ab8782bfd06558c0e4efff3874d69677d6be1f82b38e3237e4567a2c301e` (contains the generated `pl_batt_bg.narc`, sha256 `ed24fada…a6e`) |
| `make rom ROM_REVISION=1` | success — ROM sha256 `b8813153bae51f9867f492d021da3fa756bb7d29d1ca2e694a40d074b778ca76` |

These are local builds from the commit that carries this document; the CI
`build` workflow is the authoritative matrix run. Runtime review is the
owner's (section 6).

The validator pins an aggregate SHA-256 over the 305 members the generator
does not own (all tile art, all tilemaps, all cells), proving geometry and
tile data are untouched, and checks palette index contracts and ramp
monotonicity.

## 5. Deferred / not in G7.1A

* **Tile-shape work** (chamfered corners, interior panel texture, a second
  lip row). Tiles of these blocks are shared by Yes/No, target-select and the
  move slots through tile-equivalence classes; reshaping them safely needs the
  G7.1B tile-block pass so the move slots are redrawn in the same step.
* **`BATTLE_TYPE_FRONTIER` battles** keep retail art (separate tile member
  #169, tilemap #170, palette #340, speed-up #341); none of those members is
  edited. Frontier-facility backgrounds have no terrain-palette member, so no
  deck palette reaches them.
* Label outline hues in `shared.pal` could be nudged toward the new ramps; left
  alone to avoid shifting unrelated UI that shares that palette.
* The `generate-visual-ui.yml` workflow still targets the historical
  `visual-overhaul-g2a` branch; the new generator is added to its step list
  but the branch filter is not changed.

## 6. Owner runtime review (not performed here)

Please capture, in **portrait stacked** and **landscape side-by-side**:

1. Singles command menu on grass, water, cave, snow and a dark/Distortion arena
   — keys readable, deck tint acceptable, emblem not distracting.
2. Doubles command menu (second Pokémon, RUN → CANCEL label).
3. D-pad focus on all four keys: bracket visible over the red FIGHT key and the
   bottom keys; no clipping at the emulator overlay edge.
4. Touch press on each key: pressed frame, label shift, no leftover tile
   fragments.
5. Hold touch during animation fast-forward: backdrop brightens, then returns.
6. Yes/No, forget-move, switch prompt, target select: new key colors, labels
   legible.
7. Safari Zone / Pal Park command menus (Ball / Bait / Mud labels).
8. Battle Frontier command menu: confirm it is unchanged (retail look); Battle
   Tower-style battles that are not flagged `BATTLE_TYPE_FRONTIER` should show
   the neutral navy deck.
