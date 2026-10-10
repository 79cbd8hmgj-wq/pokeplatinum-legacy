# UI-01 — Approved expanded Pokédex information pages

**Decision:** Approved 2026-10-10. Gameplay accuracy is the first priority; the modernized Opal visuals support these new information pages.

## Pages and their authoritative sources

| Page | Content | Source | Gate |
| --- | --- | --- | --- |
| Overview | Dex index, name, forms and reworked types | Species personal data, current form and existing seen/caught state | Preserve vanilla reveal logic |
| Abilities | Standard ability slot(s), descriptions, and when applicable unlock conditions | Compiled species personal tables and ability description bank | Do not misidentify a species-possible ability as the inspected Pokémon's actual ability |
| Evolution | Full family, level/item/time/location/conditional method(s), including no-trade methods | Compiled evolution table and custom evolution condition implementation | Never show vanilla trading for an evolution whose method changed |
| Learnset | Current level-up moves, levels and post-rebalance BP/accuracy/PP/category | Compiled species learnset and move table | Match Opal move behavior; special effects may need short extra explanation |
| TM/HM | Actual species compatibility and resulting move information | Compiled TM/HM species bitfields and move mapping | Validate against existing C3H TM compatibility changes |
| Base stats | Six species base statistics, optionally visualized | Compiled personal species stat table | Label explicitly as *base* rather than trained/individual stats |
| Locations | Wild habitat, overworld/event/gift/legendary source and relevant progression gate | Encounter configuration and script/event/gift sources | Distinguish wild from one-time encounters; never imply inaccessible content is available |
| Forms | Form differences in types, stats, ability, moves and special conditions | Form data, relevant code and save-state availability | Preserve existing form gating and display behavior |

## Interaction rules

- Provide explicit tabs or pages reachable with DS buttons and touchscreen controls, preserving existing search/scroll/dial functions.
- A new information view may require an extra sub-state; do not overload a vanilla background or touch rectangle without a source-level geometry map.
- Prefer compact tab headings and readable values to crowded data tables.
- Mark unavailable data as locked/unknown rather than inventing values.
- Once caught, offer the full mechanics reference that is genuinely available at that save/progression state; seen-only remains appropriately limited.
- Preserve foreign-language descriptions, form entries, cry, footprint, height/weight and location features.

## Technical implementation sequence

1. **Gameplay truth adapter:** enumerate compiled personal, evolution, learnset, move and TM records and availability sources; define stable per-species data access without hand-copying values.
2. **Page/navigation framework:** extend existing Pokédex state/UI with bounded page IDs and dedicated input handling, retaining all original functionality.
3. **Overview + stats + abilities:** integrate and cross-check representative Opal retypes and stat/ability repairs.
4. **Evolution + learnset + TM/HM:** wire real revised tables and render methods in player-readable text.
5. **Locations + forms:** validate availability and gating versus wild tables and event scripts.
6. **Regression/runtime:** dual-LCD screenshots and button/touch flow, both ROM revisions, caught/seen/unseen cases, multiple forms, revised evolution methods and level-up learnsets.

**Scope note:** This file records approved design, not completed implementation. Gameplay table format and exact page ownership require the implementation audit before coding.
