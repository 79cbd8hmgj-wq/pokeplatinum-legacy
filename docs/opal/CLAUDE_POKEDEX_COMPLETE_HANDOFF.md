# Claude Code execution handoff — finish Pokémon Opal Pokédex

**Objective:** Deliver the **complete, functional, gameplay-accurate** Pokémon Opal Pokédex enhancement in the repository, not a design-only or palette-only milestone. Work in substantial contiguous batches, fix failures autonomously, and do not stop after writing a plan.

## Starting point

- Repository: `79cbd8hmgj-wq/pokeplatinum-legacy`.
- Active draft PR **#109**, branch `docs/ui01a-pokedex-contract`, targeting `main`. Continue the existing PR/branch; do not recreate committed work.
- Starting head when handoff written: `12ec80f60cd842ee5de1e49e257c4125c0fca623`. Re-fetch head before work; never reset concurrent changes.
- Keep **PR #108 Bag V3** separate. It is draft and unmerged. Do not base Pokédex changes on Bag work or merge unrelated PRs.
- Existing PR #109 already includes palette revisions, sub/main scrolling atlas tweaks, preview builders, tilemap audit/validators, and design requirements. These are **partial foundational work**, not finished Pokédex pages.
- PR #109 CI checks are not a substitute for runtime proof; capture latest results before saying complete.

## Design authority (read these first)

1. `docs/opal/ui01-pokedex-expanded-information-contract.md` — user-approved eight gameplay information views.
2. `docs/opal/ui01-pokedex-gameplay-parity.md` — truth and source-of-data rules.
3. `docs/opal/ui01a-pokedex-contract.md` — module/resource inventory, UX preserving constraints.
4. `docs/opal/ui01b-pokedex-layer-audit.md` — layered BG/OAM structure.
5. `docs/overhaul/MASTER_SPEC.md`, `docs/overhaul/STATUS.md`, and the canonical locked ledgers under `docs/overhaul/` — actual overhaul authority.
6. Read existing `src/applications/pokedex/`, `res/graphics/pokedex/meson.build`, `res/graphics/pokedex/pokedex.order`, existing generated `zukan.narc` indices, and validators under `tools/opal_pokedex/`.

**Highest-priority user requirement:** The Pokédex must explain the **real Pokémon Opal gameplay changes**, not merely look nicer. Avoid writing vanilla assumptions or manually invented data.

## Deliverables — implement all, not just plans

1. **Gameplay source-of-truth layer:** Establish authoritative access to compiled species data (type, abilities, base stats), evolution conditions (including appended custom evolution methods), level-up learnsets, move stats/descriptions, TM/HM compatibility, forms, and actual encounter/event/gift availability. Use existing tables or reproducible build-time generation, not manually hardcoded 493-species content. Record where scripted encounter truth cannot be automatically resolved and provide conservative behavior instead of false claims.
2. **Eight integrated information pages** (native DS, both LCDs): Overview; Abilities; Evolution; Learnset; TM/HM; Base Stats; Locations; Forms. In particular, evolution methods must display Opal's revised requirements; move and TM information must use current Opal mechanics. Include seen/caught/unknown gating and preserve meaningful progress.
3. **Graphical integration:** Make the Opal V3 pearl/mineral-violet/restrained-gold design consistent across navigation, information, search, forms, habitat, cries, footprint, height/weight and Sinnoh/National modes. Change actual assets and UI code; do not count preview-only art as installed graphics.
4. **Controls:** Add page switching with buttons and/or stylus with obvious feedback. Preserve vanilla scrolling, search/sort, cry controls, forms, foreign-language details, existing touch hitboxes where unchanged, and exit/back behavior.
5. **Validation:** Integrate deterministic assets/manifests, regression validators for fields and display source, asset palette/tilemap limits, both US ROM revisions, CI and a state-by-state emulator QA sheet. Demonstrate representative species retypes (Luxray Electric/Dark, Sceptile Grass/Dragon, Milotic Water/Dragon) from *actual current tables*, trade-free evolutions, new move learn timing/compatibility and legendary/event sources.
6. **Evidence:** Commit source, assets, tests, and implementation notes to PR #109. Document changes and remaining non-automatable emulator checks; never claim full runtime validation without running an emulator or obtaining user confirmation.

## Working method

- Phase 0: Audit current branch vs `main`; identify actual Pokédex view logic and resource owner for each interface state. Inventory personal/evolution/move/learnset/TM/encounter source formats. Resolve any contradictory documentation using **compiled implementation** as authority; do not fabricate.
- Phase 1: Implement data and page/navigation architecture. Build and test source-level proof on representative species and all expected data categories.
- Phase 2: Implement Overview, Abilities, Stats, Evolution, Learnset, TM/HM with real data and correct access rules. Use proper pagination/text clipping handling.
- Phase 3: Implement encounter sources/locations, forms, visual cohesion, and compatible search/extra pages. Event-only locations may require curated validated mappings with provenance.
- Phase 4: Full CI, two ROM revisions, static tests, in-emulator visual/control checks if available, fix failures, finish documentation and handoff reproducible emulator acceptance steps where not available.

**Batch commits by coherent functionality**, not one color per commit. Run local checks before pushing when possible. Diagnose and repair CI failures in the same session. Continue automatically across phases; only stop for an actual design ambiguity that cannot be safely resolved, a permission/tool limitation, or non-automatable emulator review. Do not rewrite or disable existing tests to conceal broken implementation.

## Definition of done

- Each of the eight new views opens, renders *current implemented gameplay values*, paginates and exits correctly.
- All original Dex behavior remains available and functional.
- Updated art is really shipped inside the ROM, not merely exported as previews.
- Both supported US revision builds and relevant validators pass at PR head.
- Static parity/regression tests include representative implemented changes; no unsupported false availability/method claims.
- Runtime test evidence exists **or** missing emulator verification is openly and explicitly flagged; do not mark complete/merge-ready on CI alone.
- PR #109's description accurately records finished code, artifacts, tests, outstanding issues and runtime sign-off status.

## Reporting

When finished, report in one concise handoff: commits and PR link, implemented feature matrix, build/test evidence, unresolved blockers, and exact emulator checks the user must run. Do **not** ask for approval after each ordinary implementation batch.
