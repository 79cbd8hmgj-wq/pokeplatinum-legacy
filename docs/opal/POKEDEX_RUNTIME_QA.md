# Opal Pokédex — runtime QA record and on-device checklist

## What was verified, and how

| Layer | Evidence | Status |
| --- | --- | --- |
| Gameplay data parity | `tools/opal_pokedex/validate_gameplay_parity.py` — 7745 checks against the *compiled* tables of a Rev 0 and a Rev 1 build (`--build-dir`), 4784 source-level; mutation self-tests (trade evolution reintroduced, TM21 reverted) are caught | PASS |
| Integration guard | `validate_opal_integration.py` — 181 checks (link-script entries, screen-table sizes, asset order, tilemap bounds, string ids, built `zukan.narc` contents) on both revisions | PASS |
| Generated data freshness | `build_gameplay_data.py --check`, `opal_strings.py --check` | PASS |
| Builds | US Rev 0 and US Rev 1 `make rom` | PASS (local); CI via `build.yml` |
| Emulator rendering | DeSmuME 0.9.12 (headless, py-desmume) with a local boot harness, all-species seen/caught: all 8 pages rendered for Bulbasaur, Eevee and Luxray lines; tab/prev/next/up/down/back buttons laid out | PARTIAL — see below |
| On-device / melonDS / iOS | not performed | **PENDING — user** |

Screenshots: `docs/opal/runtime_evidence/desmume_pages_species_*.png` (frames sampled while stepping pages
with the D-pad; a few frames are captured mid-transition, so the species/page shown in a frame can lag
the key press — the per-species values are asserted by the validators, not by these images).

## Known limitations

* The pre-existing area-map habitat data (`zukan_enc_platinum`) is vanilla and does not reflect Opal
  encounter changes; the Opal **Locations** page is the accurate source and is generated from the encounter
  tables (`opal_locations.bin`). GBA dual-slot data is not shown.
* DeSmuME differs from melonDS/iOS emulators in timing and palette handling; do the checks below on the
  emulator you actually play on.
* Touch hold-repeat and stylus hit-testing were implemented to match the existing Info-sub conventions but
  stylus input was only exercised through DeSmuME's synthetic touch.

## Checks the user must run (emulator / hardware)

1. National Dex obtained save: open Pokédex → pick a caught species → Info tab → press **START** (or touch the
   OPAL DATA plate on the right strip). The Opal reference opens with the pearl/violet/gold palette.
2. For a caught species step through all 8 tabs with Left/Right, **A**, and by touching each tab button.
   Confirm: Overview (types/abilities/BST), Abilities (descriptions), Evolution (Opal methods, e.g. no trade
   evolutions), Moves (level-up table with Pow/Acc/PP, scrolls with Up/Down), TM/HM (Opal masks, reusable TMs),
   Stats (bars), Where (wild/egg/special sources), Forms.
3. Spot-check Opal changes: Luxray Electric/Dark, Sceptile Grass/Dragon, Milotic Water/Dragon, Raichu TM91
   Flash Cannon, Torkoal Yawn Lv52/Heat Wave Lv55, Banette Cursed Stitch Lv38.
4. A seen-only (not caught) species shows Overview + Locations and the "catch to unlock" message elsewhere;
   an unseen species shows no data.
5. Prev/Next and **L/R** change species while keeping the current tab; **B**/Back returns to the Info tab and
   the normal Info/Forms/Cry/Footprint/Height-Weight/Habitat/language tabs, search, sort and scroll still work;
   re-entering the Opal screen works repeatedly (no palette corruption on the main list afterwards).
6. Sinnoh Dex and National Dex lists both open the screen; screen fades and palette are restored on exit.
7. Look for text clipping on the learnset (long move names), TM/HM list (HM rows), and the Locations page
   for species with many places (scroll to the end).
