# G7.2A — Battle Healthbox Chrome

Status: **implemented (palette-only); build-verified locally; owner runtime review pending**

Parent: `G7_MODERN_DS_REMASTER_IMPLEMENTATION_PLAN.md` (G7.2, healthbox bullets).
Builds on G5's shared-palette healthbox refresh (`generate_battle_ui.py`).
Starting commit: `b32dd76b` (G7.1B).

## 1. Ownership trace

* A normal healthbox is **one sprite made of two 64×64 OAMs** (`tall_cell.json`
  for the player's single-battle box, `short_cell.json` for enemy and doubles),
  fed by `res/graphics/battle/healthbox/{player_singles,player_doubles,enemy}.png`.
  The PNGs are the source of truth: pixels → NCGR (1-D, 64-byte mapping),
  palette → `primary.NCLR` (generated from `player_singles.png`).
* Everything that changes at runtime is **blitted into fixed tile ranges of that
  sprite's VRAM** (`sBattlerNameVRAMTransfer`, `sLevelIconVRAMTransfer`,
  `sLevelNumberVRAMTransfer`, `sCurrent/MaxHPNumberVRAMTransfer`,
  `sHPGaugeVRAMTransfer`, status / caught / ball-count parts). Glyphs and gauge
  pieces come from `healthbox_parts.png` (embedded) or the font renderer, in the
  same 16-entry palette.
* Name text is `TEXT_COLOR(14, 2, 15)` — white letters, entry-2 shadow, entry-15
  field. HP numerals and gauge pieces use entries 14/5/3 and the HP-state ramps
  (6-10).
* The turn/target arrows (`arrows_wide`) load the same palette resource
  (`HEALTHBOX_MAIN_PALETTE_RESID`) and use entries 4 and 15.
* The Safari healthbox has its own palette (`safari.NCLR`) and is not touched.

## 2. What changed

Only five chrome entries of the shared healthbox palette, rewritten by
`tools/visual_overhaul/generate_battle_ui.py` (`CHROME_PALETTE_OVERRIDES`) in the
four embedded preview palettes (`player_singles`, `player_doubles`, `enemy`,
`healthbox_parts`):

| Entry | Role | G5 | G7.2A |
|---|---|---|---|
| 1 | cool edge highlight | 190,207,220 | 176,208,236 |
| 2 | outline / name shadow | 24,37,52 | 12,20,40 |
| 3 | rail / HP-numeral field | 62,89,112 | 46,70,98 |
| 4 | bright highlight / arrow edge | 232,241,247 | 236,244,250 |
| 15 | panel / name field / gauge track | 78,101,119 | 36,54,80 |

Result: a dark navy data panel with a thin cool-white rim. The white
name/level/HP glyphs now sit on the panel at 12.2:1 (was 6.1:1 on the G5 slate)
and on the HP-numeral rail at 9.7:1 (was 7.3:1). HP green/yellow/red, status colors, the white
glyph entry (14), black (5) and the transparent key (0) are byte-identical, and
the validator proves the HP/status ramps separate from the new rail and panel at
least as well as they did from the G5 chrome.

No pixel index, cell, animation, VRAM-transfer offset, C source or text-printer
code changed: `player_singles`, `player_doubles`, `enemy` and `healthbox_parts`
keep their exact index data (pinned by SHA-256 in
`validate_g7_battle_hud.py`), so name/level/gender/HP/status/ball-count layout,
numeric player HP and double-battle variants cannot overlap or clip more than
they did at G5.

## 3. Deferred (and why)

* **Slimmer geometry** (thinner outline bands, tighter plate): the frame bands
  are *static* tiles interleaved with runtime-blitted tiles per box type
  (singles / doubles / enemy, six VRAM-transfer tables). Thinning them needs a
  per-type tile-ownership map and re-seaming against `healthbox_parts.png`; this
  cannot be previewed or tested here without the runtime compositing. The darker
  field and thinner-reading rim already reduce visual weight; geometry is left
  for a later pass if the owner still finds the boxes heavy.
* **Low-HP urgency pulse** (plan: "audit; ship only if safe"). Audit result:
  a pulse can reuse the existing effects-palette swap used by
  `Healthbox_Task_LevelUpFlashAnimation` (`HEALTHBOX_EFFECTS_PALETTE_RESID`,
  `PaletteData_Blend`), triggered from the HP-gauge colour transition to
  `BARCOLOR_RED`. It is **not** shipped because that palette is shared with the
  level-up flash (two writers, one palette), needs lifecycle cleanup on KO /
  switch-out / battle end, and cannot be exercised without runtime testing here.
  Static improvement shipped: the red HP state now sits on a darker panel, which
  makes it read more urgently than at G5.
* Safari healthbox: left as-is, as the plan requires a separate audit.

## 4. Validation (local)

| Check | Result |
|---|---|
| `generate_battle_ui.py` rerun | no diff |
| `validate_g7_battle_hud.py` | pass |
| `validate_g7_battle_command_ui.py` | pass |
| `make rom ROM_REVISION=0` | success, ROM sha256 `024ad7aeb6589e8abce8c160a1f544f65b03131df859f1604300c369aee468c2` |
| `make rom ROM_REVISION=1` | success, ROM sha256 `16af28b691ac993b4e8676611236b7293f32461b4a51afd592bc498867e8461c` |

## 5. Owner runtime review

Portrait stacked + landscape side-by-side:

1. Single battle: player box (numeric HP) and enemy box — name, level, gender
   mark, HP numerals and gauge legible; rim not clipped.
2. Double battle: all four boxes; no HP/status/name overlap.
3. HP green → yellow → red on both sides; gauge track visible against the panel.
4. Each status condition icon; fainted box.
5. Level 100, a 10-letter species name, genderless species.
6. Level-up flash (palette blend) still reads and returns to the navy panel.
7. Turn arrows beside the boxes (they share this palette).
