# Pokémon Opal — post-Bag interface modernization inventory

**Audit basis:** Repository source/resource directory enumeration and merged PR #53 file list, 2026-10-10. These labels are *code-coverage assessments*, not emulator-reviewed visual-quality claims. The current draft PR #108 remains separate and unmerged.

## Verified foundations

- PR #53 (merged) modified Party menu button/cursor art, Summary move cursor/tab arrow/palette, Bag palettes, Start cursor, Shop palettes; generated tooling includes dedicated Party, Summary, Bag, Start, and Shop UI scripts.
- PRs #103–#105 (merged) cover animated Start/Bag focus, Party selection cursor and Bag/Party entry transitions.
- PR #108 (draft) implements Bag V3 artwork and layout work, with a runtime verification matrix under `docs/opal/mo1-4-bag-runtime-verification.md`.
- Dedicated code and graphic resource trees exist for Pokédex, Summary, Party, Pokétch and Town Map. Trainer Card has `src/applications/trainer_case`; PC boxes have `src/applications/pc_boxes`.
- **Not established:** Full-screen design coverage, runtime appearance, complete interaction correctness, and whether additional UI changes exist outside the PRs inspected.

## Ordered interface work queue

| ID | Interface | Repository evidence | Audit classification | Next implementation gate |
| --- | --- | --- | --- | --- |
| UI-01 | Pokédex | `src/applications/pokedex/`; `res/graphics/pokedex/` (128 entries); modules for search, sorting, panels, forms, maps, text and graphics | Dedicated baseline confirmed; no Pokédex assets in merged PR #53 | Inventory all Pokédex states/assets; specify Opal V3 navigation & screen contracts; implement a bounded first slice |
| UI-02 | Pokémon Summary | `src/applications/pokemon_summary_screen/`; PR #53 modified Summary cursor/arrow/palette | Partially refreshed by G7.4 | Audit all tabs, stat/type/move pages, decorations, touch controls and transitions before redesign |
| UI-03 | Party | `src/applications/party_menu/`; PR #53 and #104–105 | Previously modernized in part, animated transitions merged | Runtime coverage and any remaining panel inconsistencies |
| UI-04 | PC Boxes | `src/applications/pc_boxes/` including touch dial; art location still to map | Baseline code confirmed; asset ownership not yet established | Inspect box UI resource loading, deposits, withdrawals, move/summary menus, wallpapers |
| UI-05 | Trainer Card | `src/applications/trainer_case/` | Baseline code confirmed | Inventory front/back, badge interaction and text resources |
| UI-06 | Pokétch | `src/applications/poketch/` and `res/graphics/poketch/` (125 entries) | Dedicated baseline confirmed; numerous app modules | Separate shell/device redesign from per-app art; protect touch gestures |
| UI-07 | Town/Fly Map | `src/applications/town_map/`, `res/graphics/town_map/` (34 entries) | Dedicated baseline confirmed | Inventory map zoom/markers/Fly actions; preserve map coordinate contracts |
| UI-08 | Battle HUD | Merged PR #50 (battle command, moves, healthboxes, message frames); PR #101 battle animation | Modernization already merged in part | Audit healthbox/status/menus in battle before more graphic changes |
| UI-09 | Start/Shop | Merged PR #53; #103 animation | Modernization already merged in part | Runtime completeness and shared-modal consistency |
| UI-10 | Miscellaneous | `src/applications/options_menu.c`, `poffin_case`, `journal_display`, `mail_viewer.c`, `naming_screen.c`, `frontier`, `easy_chat` | Baseline code confirmed; visual modernization not assessed | Enumerate screens, prioritize by player frequency and mechanics risk |

## Recommended follow-on PRs

1. **UI-01A Pokédex contract and resource census**: enumerate main/sub states, resource loader references, sprite/window/touch ownership, source filenames, palettes and Nitro maps. Record current-versus-target V3 design and a no-regression matrix. Documentation-only first PR.
2. **UI-01B Pokédex first implementation**: bounded list/navigation/background prototype wired to source assets; exact target scope set by UI-01A. Both US ROM builds and asset validation mandatory.
3. **UI-01C Pokédex details/forms/search polish**: only after runtime screenshots of UI-01B.
4. **UI-02 Summary and UI-03 Party completion**: preserve existing G7/AV3 improvements and verify against Pokédex visual language.
5. **UI-04 onward**: PC storage, Trainer Card, Pokétch, Town/Fly maps, then global auxiliary screens; battle/menu audits can run in parallel as separate scopes.

## Mandatory gates

- Do not merge draft PR #108 solely because CI is green; obtain its runtime checklist evidence.
- Each new screen requires source/resource map, behavior contract, failure checklist, reversible asset changes and both-revision CI before runtime sign-off.
- Never assert that a screen is 'untouched' without reviewing actual merged changes. Treat listing a module/resource directory as existence evidence, not proof of completeness.
