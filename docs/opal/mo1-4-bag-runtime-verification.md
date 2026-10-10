# MO1-4 — Bag V3 integration and runtime verification

**Status:** CI/source inspection is not an emulator sign-off. Run on both US rev0 and US rev1 builds. Use a clean save and a save with populated pockets. Do not merge PR #108 as visually verified without checking screenshots and interactions.

## Source inspection (2026-10-10)

- Item list remains on MAIN BG2, 9 visible lines at 16-pixel pitch. Decorative main panel is MAIN BG1; item description window is MAIN BG0.
- Selection highlight and sorting bar remain sprites; item icon is another MAIN OAM sprite.
- Touchscreen ornament is SUB BG1, while the rotating dial is SUB BG3 and actual pocket buttons/touch controls are elsewhere. Background ornamentation must never be interpreted as a working touch target.
- Source contains dedicated normal browsing, item-selling, item-movement/sorting, D-pad and touch pocket switches.
- Several context menus share MAIN BG0 with the description area. These require visual inspection because compile-time tests do not establish alpha, window-clear, or layer behavior.

## Emulator execution matrix

Run this matrix for **both** supported ROM revisions. Mark individual cases PASS/FAIL and attach one screenshot per distinct screen state. Record any text clipping, ghost panels, misplaced indicator, sprite occlusion, or touch misalignment.

| ID | Setup / action | Acceptance criterion |
| --- | --- | --- |
| BG-01 | Open Bag with 8 available pockets | Nine rows visible; row separators do not interfere with names/counts, pocket name readable |
| BG-02 | Open Bag with 1, 4 and 7 accessible pockets, if reproducible | Only available pocket buttons appear actionable; no false permanent eight-button affordances |
| BG-03 | Switch each pocket with D-pad | Correct pocket name/icon; no stale list background or off-panel highlight |
| BG-04 | Switch each pocket with stylus | Touch regions agree with drawn controls; rotating dial still works |
| BG-05 | Scroll top, middle, bottom of a full pocket | Highlight follows row including last visible entry; nine-row pitch remains correct |
| BG-06 | Select item, inspect icon and 1-, 2-, 3-line descriptions | Icon/text are distinct, fully readable and contained within lower panel |
| BG-07 | Open TM/HM pocket; inspect power, accuracy, PP, type, category | Stats labels/values readable without clipping or item-icon collision |
| BG-08 | Open Berries pocket; inspect numbered entries and quantities | Number/icon/text/count columns fit |
| BG-09 | Register and deregister an eligible item | Registered marker does not clash with quantity or right edge |
| BG-10 | Sort/move item from first to middle to last entry | Sorting bar and selection highlight remain aligned; item order updates |
| BG-11 | Use, Give, Trash, Register and Cancel menus when available | Menu boxes obscure background cleanly; options readable and actions correct |
| BG-12 | Sell items in shop: select, adjust quantity, confirm/cancel | Money, sale count, arrows and quantity overlays readable; no stale description art |
| BG-13 | Use Close Bag and reopen | Transition exits and restores both panels cleanly |
| BG-14 | Open item/Poffin count and throw-away confirmations when available | All modal windows and counts display without off-screen clipping |
| BG-15 | Navigate the list while pocket buttons animate | No sprite flicker, text ghosts, or mismatched button feedback |

## Defect handling

For each failure record: ROM revision, emulator, game state, pocket, exact inputs, expected/actual rendering, top-and-bottom LCD screenshots and reproducibility. Distinguish visible art defects from mechanics bugs. Do not change input hitboxes or pocket counts solely to compensate for a decorative asset issue.

## Release gate

- CI: both US revisions build, asset regeneration is reproducible, all existing validators pass.
- Runtime: all reproducible matrix cases pass with screenshot evidence.
- Missing game states are **NOT TESTED**, not PASS.
- PR #108 stays draft until runtime observations are recorded and discrepancies are addressed.
