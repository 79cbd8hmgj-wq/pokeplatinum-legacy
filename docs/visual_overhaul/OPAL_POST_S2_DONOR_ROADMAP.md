# Pokémon Opal — Visual Donor Roadmap (post-S2)

Status: **planning / donor-alignment audit**, not approval to modify game source.
Updated: 2026-10-09. Target repository: `79cbd8hmgj-wq/pokeplatinum-legacy`.
This document preserves the complete post-S2 opportunity set so the first forest task does not erase other mined opportunities.

## Binding project scope

- Pokémon Opal is a distinct game on the Platinum decompilation; do not presume it is simply a Platinum overhaul.
- Core game systems and Pokémon systems are **not being reconsidered**.
- Trainer-related enhancement/redesign is **deferred**.
- Previous S3/S4 queue is **not** automatic execution order.
- The owner performs all emulator, gameplay, runtime and visual acceptance tests. Claude Code handles only source implementation, static/automated validation, ROM rev0/rev1 builds, CI, documentation and PRs. Runtime QA is not a Claude task or PR gate.
- Apply `POKEMON_OPAL_ASSET_DIRECTION.md`: preserve, replace, enhance, composite, animate, create, or discard. Avoid mandatory full-library imports and speculative binary edits.
- Prioritize concrete host assets and visual gain over unbounded donor research or infrastructure.

## Existing evidence — retain these source records

- `docs/visual_overhaul/CROSS_GAME_DONOR_MATRIX.md`
- `docs/visual_overhaul/selection/OPPORTUNITY_POOL_SUMMARY.md`
- `docs/visual_overhaul/selection/OPPORTUNITY_POOL.json`
- `docs/visual_overhaul/selection/IMPLEMENTATION_QUEUE.json`
- `docs/visual_overhaul/selection/CROSS_GEN_IMPLEMENTATION_PLAN.md`
- `docs/visual_overhaul/selection/DS_FIELD_3D_EXTENSION.md`
- `docs/visual_overhaul/selection/DS_OPPORTUNITY_REASSESSMENT.md`
- `docs/visual_overhaul/PASS_G_VISUAL_OVERHAUL.md`
- `docs/visual_overhaul/HGSS_VISUAL_ASSET_INVENTORY.md`
- `docs/visual_overhaul/RANGER_DEEP_VISUAL_PACKAGE_INVENTORY.md`
- `docs/visual_overhaul/POKEMON_OPAL_ASSET_DIRECTION.md`
- `docs/visual_overhaul/implementation/IO_PAL_CYCLE_S2D_TERRAINS.md`

Evidence snapshot: DS pool contains 9,821 processed candidate groups, 3,185 mined opportunity records and 84 donor libraries (these are **not** implemented features). HGSS field-3D extension catalogs 562 model assets, 106 texture sets / 3,659 textures (3,647 usable), and 572 follower sheets (ingredient/export source, **not** follower-mechanic obligation). Ranger inventory contains 3,057 compressed packages and 10,157 embedded NARC resources. All figures are catalog counts, not confirmed native drop-in compatibility.

## Post-S2 opportunity ledger (proposal, not fixed implementation order)

| ID | Candidate | Donor/evidence | Intended Opal host/use | Status | Next bounded evidence need |
|---|---|---|---|---|---|
| V01 | Forest ambient foliage | Platinum trap-effect leaf/petal resources; HGSS foliage, PMD Sky effects and Ranger timings as reference | Deep-forest dedicated field-renderer path, conservative drifting leaves | **Feasibility done: NO-GO / blocked** (no code changed) | Leaf is 2D OAM; field effects are 3D billboards from opaque prebuilt `fldeff.narc`. See `implementation/V01_FOREST_FOLIAGE_FEASIBILITY.md`; proceed to V02 |
| V02 | Eterna material composite | HGSS foliage-ground, bark/ground/wall texture regions | Platinum Eterna `map_texture_set_074` | **Targeted comparison** | Exact Platinum texture-region identities, donor subregions and export/conversion contract |
| V03 | Forest prop details | HGSS building/field model components | `prop_model_set_050`, forest map geometry | **Conditional** | Demonstrate a material visual gain; avoid generic model imports |
| V04 | Other overworld atmospheres | PMD Sky environmental palette/effect techniques; Ranger effects; Emerald weather references | Platinum field weather/fog/particle subsystems in snow, caves, coasts, industrial/Distortion areas | **Candidate** | Exclude Pass G completed lighting/fog before choosing one effect |
| V05 | Animated field detail | HGSS field sprites/map animations; PMD Sky field effects | Specific water, vegetation, prop or interior host chosen later | **Candidate** | Name one Opal host asset and animation interface |
| V06 | Battle particle composites | Ranger 2 effect primitives `ranger_effect/e`, sequencing (e.g. e010/e100); GBA timing | Platinum native battle animation scripts/effects | **Candidate** | Identify a specific move/scene and reusable component; do not rebalance moves |
| V07 | HGSS architecture/props | HGSS `hgss_bm_field_building_exterior`, rooms, texture regions | Specific Opal town/interior/landmark | **High-cost candidate** | Real matched target, geometry/palette/material compatibility |
| V08 | Location/scene presentation | HGSS area-preview module; Ranger event composition | Area/location preview or original scene card | **Optional** (old S3/S4 not binding) | Confirm creative utility and pick a concrete scene |
| V09 | UI and transitions | Ranger interface components, HGSS UI, PMD Sky presentation techniques | Specific Opal window/menu/transition | **Candidate** | Evidence of improvement beyond existing G7 work |
| V10 | HGSS overworld Pokémon sheet ingredients | 572-sheet donor exporter (PR #93) | Selected authored events or set dressing ONLY if separately approved | **Donor pipeline available** | Explicit scene + compatible field object/frame contract; no blanket follower implementation |
| V11 | Visual battle staging | Platinum native camera; Stadium 1/2 framing and impact timing (reference only) | Existing battle presentation code | **Reference candidate** | One bounded camera/impact use case and effect budget |

Exclusions: core/Pokémon gameplay mechanics, trainer work, universal follower system, bulk donor import, indiscriminate whole-asset replacement, opaque `weather_sys.narc`/`fldeff.narc` patching. Keep Ruby as previously skipped, and Crystal angels motif deferred, per cross-gen plan. No proposal overrides the existing native game behavior by default.

## Verified deep-forest baseline — do NOT repeat Pass G

G4A subsequently isolated Eterna into `res/field/area_data/area_data_075.json`:
- `mapTextureSet: map_texture_set_074` (initially a byte-identical clone of set 053)
- `mapPropSet: prop_model_set_050`
- `lightingSet: lighting_set_010` (Eterna-only grading)

Shared `area_data_054.json` remains set 053 / lighting 004 for other forest maps.

Pass G documents existing deep-forest lighting, native canopy/weather mist, fog differentiation, dedicated Eterna perspective, and dedicated forest renderer selection. `src/overlay005/fieldmap.c` currently selects `sForestFieldEffectRenderers` when `FieldMap_IsDeepForest` matches Eterna, Fullmoon Island Forest or Newmoon Island Forest. The current fog-helper path uses `FieldMap_ApplySpecialAreaFog`; historic docs sometimes use older names. Confirm current source rather than pasting stale helper names. Do not revert G4A isolation: Eterna's area-data 075 was created precisely to avoid modifying the other forests. The current `sForestFieldEffectRenderers` remains shared by Eterna, Fullmoon and Newmoon, so renderer modifications **do** affect all three unless explicitly scoped.

Crucial source finding: `src/overlay005/field_effect_renderer.c` already implements `ForestAmbienceRenderer` and registers `FIELD_EFFECT_RENDERER_FOREST_AMBIENCE` in the shared forest renderer list. Its SysTask currently emits `BerryPatchGraphics_NewSparkleEffectAt` every 90 frames using six rotating offsets near the player; this is **not** drifting leaf artwork. It has a matching Free hook. The next investigation must prioritize safely replacing/extending this existing ambience rather than creating a second renderer or duplicative task. `res/graphics/trap_effects/leaf.png`, `leaf_cell.json`, and `leaf_anim.json` are source-exposed; the leaf animation presently has one frame (delay 4), and its cell uses one 16×16, 16-colour OAM sprite. Build path is `res/graphics/trap_effects/meson.build` -> `trap_effects.narc`. The field runtime needs a verified way to read that resource without coupling to Underground trap state.

Pass G identifies editable Nitro leaf/petal resources at `res/graphics/trap_effects/`. The Underground leaf runtime is trap/input-coupled, **not** appropriate for direct transplant. Forest effects assets `fldeff.narc` and weather archive are prebuilt/opaque in current documentation. Do not guess resource IDs or patch binary archives.

## V01 bounded feasibility protocol (next task; NOT yet authorized runtime feature)

1. Inspect existing `ForestAmbienceRenderer` in `src/overlay005/field_effect_renderer.c`, including its berry-sparkle task, matching Free hook, shared renderer list and field manager lifecycle. Do **not** introduce another ambience task by default. Check current map-specific scoping if a leaf effect should only appear in Eterna.
2. Identify specific editable leaf frames/palette/cell/animation definitions in `res/graphics/trap_effects/`; record dimensions, indexed-color budget, animation footprint.
3. Determine whether resources can be loaded through already source-exposed sprite/field effect APIs with correct ownership, unload and fade/map transitions **without** editing opaque NARCs.
4. Review donor **specific components** as animation/appearance references; preserve identifiers/provenance. Do not invent donor-compatible files.
5. Deliver a compact go/no-go with the exact source/resource files, safe binding point, likely VRAM budget, fallback if no safe route, and design recipe (subtle low-density leaves; no occlusion of player/UI).
6. If green, implement as a separate small PR with source/static checks and US ROM rev0/rev1 builds. If blocked by opaque archive/new costly infrastructure, **stop at documented feasibility**, return to V02 texture comparison instead.
7. **Never** launch emulators or conduct in-game/visual testing; owner does that, not Claude.

## Future decision hygiene

Every subsequent visual PR should link an opportunity ID, baseline resource, donor component(s) and source refs, visual intention, modified files, lifecycle/format safety, static checks/build outcomes, and known untested runtime behavior. Do not mark a visual candidate "finished in-game" based only on compilation. Preserve this ledger and update individual statuses rather than rewriting the roadmap around the latest pilot.

## Later evidence correction — G4A baseline and already-present ambience

The earlier Pass G general forest description alone was insufficient: `docs/visual_overhaul/G4A_ETERNA_FOREST.md` documents two implementation batches creating Eterna-only area-data 075 and texture-set 074, while keeping the shared forest 054 unchanged. A source read of `field_effect_renderer.c` independently confirms `ForestAmbienceRenderer` already emits berry sparkle every 90 frames. Therefore V01 is a **refactor/replacement review** for a pre-existing ambient effect, not an empty-slate renderer build. The exact compatibility of the trap-effect leaf graphics with the field resource loader is unverified. A change to the forest renderer list is globally shared; make map-specific behavior deliberate. `docs/visual_overhaul/implementation/IO_PREVIEW_ETERNA_FOREST.md` also confirms an Eterna preview-card pilot is already source-implemented, so V08 cannot duplicate that host without a separate improvement case.
