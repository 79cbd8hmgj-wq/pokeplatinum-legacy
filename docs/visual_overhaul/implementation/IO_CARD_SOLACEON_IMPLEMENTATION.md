# IO-CARD — Solaceon News Press implementation notes

Implements `IO_CARD_SOLACEON_PREFLIGHT.md`. Status: **source/build implemented; runtime and visual QA pending (not run)**.
No emulator or on-hardware validation has been performed; this environment had no ARM/CodeWarrior toolchain, so compilation is verified by CI only.

## What shipped

- `src/applications/still_card.c`, `include/applications/still_card.h` — reusable still-card child application. A card is a `StillCardDesc` (`sStillCardDescs[]`) listing the page/panel art, text bank, masthead message and per-state `{headline, article, illustration}` descriptors. Solaceon News Press is `STILL_CARD_SOLACEON_NEWS_PRESS` with four states.
- Script command `ShowStillCard cardID, startState` (`SCRCMD_SHOWSTILLCARD`, `ScrCmd_ShowStillCard`, `FieldSystem_ShowStillCard`).
- Art set `res/graphics/still_card/` → `graphic/still_card.narc` (`NARC_INDEX_GRAPHIC__STILL_CARD`), generated reproducibly by `tools/visual_overhaul/io_card/build_still_card_assets.py` from `res/items/icons/{dusk,heal,quick,dive}_ball.png` (2x nearest-neighbour). No Ranger 2 / PMD Sky pixels; Ranger 2 is a structural reference only (masthead, rules, illustration well, columns, state variants).
- `res/field/scripts/scripts_solaceon_town_pokemon_news_press.s`: the four article branches now set `VAR_0x8008` and `GoTo SolaceonTownPokemonNewsPress_ShowArticleCard`. The original message-box flows are kept as `..._ArticleFallback<Ball>` labels for one-line reversion. Menu, index mapping, `ReleaseAll` and the reward/assignment script are untouched.
- One new message appended to the same text bank: `SolaceonTownPokemonNewsPress_Text_CardMasthead` ("WEEKLY POKé BALL ROUNDUP", the existing top-story title).
- New overlay `still_card` (appended to `platinum.us/main.lsf`), heap `HEAP_ID_STILL_CARD` (appended before `HEAP_ID_MAX`), NARC path in `src/narc.c`, `platinum.us/filesys.csv`.

## The five bounded questions

1. **Command + pause/resume.** `ShowStillCard` follows `ScrCmd_ShowDiplomaSinnoh` (`src/scrcmd.c`): store the arg block in `SCRIPT_MANAGER_PARTY_MANAGEMENT_DATA`, start the app with `FieldSystem_ShowStillCard` (`src/unk_0203D1B8.c`, uses `FieldSystem_StartChildProcess`), then `ScriptContext_Pause(ctx, sub_02041CC8)`, which waits on `FieldSystem_IsRunningApplication` and frees the arg block. Registered in `include/data/scripts/scrcmd.h` and `asm/macros/scrcmd.inc`. No edit to `src/field_task.c` / `src/bg_window.c`. Script wraps it as `CloseMessage; FadeScreenOut; WaitFadeScreen; ShowStillCard; ReturnToField; FadeScreenIn; WaitFadeScreen; ReleaseAll` (same as the Sinnoh diploma).
2. **Host.** A full child application (not an overlay on field BGs): `FieldSystem_StartChildProcess` ends the field map and the app owns both engines' VRAM banks (`GX_VRAM_BG_128_B` / `GX_VRAM_SUB_BG_128_C`, same banks as `Diploma`); `ReturnToField` restores the field. No field BG/VRAM sharing.
3. **Input + text.** Article body is the existing message printed with the native printer (`Text_AddPrinterWithParamsAndColor`, `FONT_MESSAGE`, player text speed), so the existing `\r`/`\f` page breaks and scroll arrow work unchanged (A advances). Headlines/tab labels come from the existing `MenuEntries_Text_Article_*` strings; no English literal is duplicated in C. Inputs: Left/Right/Up/Down/L/R or touching a tab selects an article; B or the touch EXIT tab exits; A exits once printing has finished. The five touch targets are `sTouchRects` (4 articles + exit). The script menu still chooses the initial article.
4. **Icons.** Sources are `res/items/icons/{dusk,heal,quick,dive}_ball.png` (32x32, 4bpp-indexed, index 0 transparent). The generator upscales 2x into a 64x72 PNG (first tile row blank so tile 0 stays transparent), keeps the icon's own 16-colour palette, and meson converts with `ncgr_gen -sopc -version101` / `nclr_gen -bitdepth 4` exactly like `res/graphics/diploma`.
5. **Ownership/teardown.** `StillCard_Init` creates `HEAP_ID_STILL_CARD` (0x20000 under `HEAP_ID_APPLICATION`), BgConfig, three windows, two `MessageLoader`s and one `String`; `StillCard_Exit` cancels any active printer, clears the VBlank callback, removes windows, frees loaders/string, frees tilemap buffers + `BgConfig`, disables engine layers, frees app data and destroys the heap. The arg block is freed by `sub_02041CC8` in the script. Field controls stay locked (`LockAll` … `ReleaseAll`) in the script across the whole sequence.

## Layout / VRAM (main = top, sub = bottom)

| Layer | Content | Screen base | Char base | Palette |
|---|---|---|---|---|
| Main BG0 (prio 0) | masthead + headline window, article body window, message-frame/scroll-arrow tiles | 0x0000 | 0x10000 | 2 (font), 14 (frame) |
| Main BG1 (prio 1) | 64x64 illustration (8x8 tile block at tile 12,8) | 0x0800 | 0x0c000 | 1 |
| Main BG3 (prio 3) | 256x192 newspaper page (identity tilemap) | 0x1000 | 0x04000 | 0 |
| Sub BG0 | tab labels window | 0x0000 | 0x10000 | 2 |
| Sub BG3 | touch tab panel (active tab = palette 3 variant) | 0x1000 | 0x04000 | 0, 3 |

## Deviations from the preflight

- **Tabs live on the bottom (touch) screen** as large buttons rather than inside the 256x192 top page, so touch input is physically usable. The top page still has masthead, headline, illustration well, columns and article text.
- A masthead message had to be added to the text bank (the page needs a title; none existed). It reuses the existing top-story name.
- Four item-icon illustrations plus the page/panel are composited by the generator; there is no shimmer layer (optional in the spec).

## Validation performed

- `python3 tools/visual_overhaul/io_card/build_still_card_assets.py` — deterministic (two runs identical), all PNGs 4bpp with 16-entry palettes.
- `clang-format-18` clean on touched C files; text JSON parses.
- Full ROM build: **CI only** (no toolchain in the authoring environment).

## Manual QA still required (not run)

1. Card entry from the Solaceon PC after each of the four menu choices; fade in/out; field unlock and movement afterwards; repeated interactions in succession.
2. Exit via B, via touch EXIT, and via A after the article finishes; Exit menu choice still skips the card.
3. Each of the four states: illustration, palette, headline centring, active-tab highlight, switching with D-pad/L/R/touch mid-print.
4. Page-break behaviour: A advances `\r`/`\f` breaks (scroll arrow visible and correctly coloured at the right of the body window); text does not overflow the 27x6-tile body window.
5. Graphics cleanup: no BG/palette/OAM leakage on return to field; no heap leak/assert on repeated opens.
6. Human art-direction review of the generated page and illustrations (not signed off).
