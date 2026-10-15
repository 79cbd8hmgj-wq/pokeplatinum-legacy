# UI-01C — Habitat reconciliation and final visual finish

Status: **implementation required**, PR #109 continuation. This is an executable, bounded specification, not a claim that the map has already been repaired.

## Observed source mismatch

- `tools/opal_pokedex/build_gameplay_data.py` generates `opal_locations.bin` and the 493-species gameplay manifest from current wild encounters and curated special acquisitions.
- `src/applications/pokedex/opal_data.c` reads this as the Opal Locations view.
- Vanilla habitat functionality instead uses the prebuilt archives under `res/prebuilt/application/zukanlist/zkn_data/` (Diamond/Pearl files copied by its Meson configuration). The legacy area map is not generated from Opal's encounters.
- `docs/opal/POKEDEX_RUNTIME_QA.md` expressly acknowledges the contradiction.

## Workstream A — habitat map correctness (must be real, no fake markers)

1. Trace the legacy habitat map loader, NARC variant selection and its species/landmark map bitfield contract. Inspect the original data format before changing any file. Preserve archive ordering and screen rendering infrastructure.
2. Derive map markers from the **same live wild encounter source** as `wild_entries()`, not from the text rows or from vanilla archives. Use a shared normalized intermediate data structure or generator to prevent future divergence.
3. Map encounter-file map headers to actual map marker coordinates/area IDs using the game's canonical map metadata. Where several map headers share a geographic marker, union their eligible habitat markers. Never make up coordinates or silently point to an adjacent zone.
4. Distinguish encounter methods explicitly. Ordinary wild LAND/SURF/ROD is map-eligible. RADAR/SWARM/LEGACY are conditional and must either have a legible condition indicator in the map UI or stay **out** of the unconditional map with a clear path to the accurate Locations page. STATIC/GIFT/FOSSIL/EGG/BREEDING/EVENT/ROAMER/RITUAL/FIXED_TILE must not be falsely drawn as ordinary random wild encounters. A special fixed-location marker is allowed only if the existing map supports a clearly differentiated legend.
5. Preserve time-of-day semantics by producing morning/day/night views from the same time flags already collected in `wild_entries()`. Keep unlock/seen/caught behavior unchanged.
6. If legacy NARC format cannot faithfully encode Opal map truth, implement an Opal map-data adapter/render bridge; do **not** overwrite unrelated Diamond/Pearl files with speculative records. Prefer a new generated Platinum/Opal resource and explicit ROM selection; retain original assets as a comparison fixture.
7. Add `--check` deterministic regeneration and parity validator: every normal habitat marker must have a source-verified encounter, and every geographically resolvable unconditional encounter must appear at the correct location/time. Emit explicit unresolved mapping diagnostics; fail CI for missing resolvable markers or stale generated data.
8. Confirm existing area-map display functions, zoom/region handling, time switching and Back navigation still work.

## Workstream B — visual cohesion (full art, not palette-only)

Keep Opal's pearl / mineral-violet / restrained-gold visual direction and native DS text legibility. Improve **installed** graphics and UI behavior in the complete vanilla Dex surfaces: main list and scroll strip, selected entry, Info, original habitat map, Forms, Cry, Height/Weight, Search, and the new eight-page Opal reference. The existing `docs/opal/ui01b-pokedex-layer-audit.md` is the layer contract.

- Make header, focused control, inactive control and scrolling affordances feel like one coherent UI; preserve screen-specific hierarchy.
- Match button focused/pressed/touch feedback across legacy and new views. Do not obscure existing controls or reduce hitbox accuracy.
- Retain all text contrast, icon readability and form/type indicators.
- Render real 256x192 captures for both displays and multiple states (list top/middle/end, Info, map times, forms, cry, height/weight, Opal locations with scroll), compare against existing previews; previews are evidence, not substitutes for installed assets.
- Respect 4bpp vs 8bpp and affine-layer distinctions, `pokedex.order` indices, NSCR tile bounds, palette bank contracts, OAM and VRAM budgets. No arbitrary recolor of `scroll_wheel.png` or SUB BG3.
- Fix demonstrated clipping/palette contamination rather than inventing cosmetic-only work.

## Acceptance gates

- US Rev0 and Rev1 ROM builds pass; original validator suites remain green.
- New habitat source-parity and map-location/time tests pass for representative routes, caves, surfing/fishing, swarms, Radar, special encounters, and 493-species coverage.
- Explicitly test Luxray, Sceptile, Milotic, Feebas fixed tile, roamers, fossils and gift/event-only species; absence of invented wild map markers is as important as their presence.
- Validate merged NARC asset placement and old/new Dex navigation, touch/button behavior, palette restoration and repeated entry/exit in DeSmuME, then obtain user verification on melonDS/iOS.
- Update `docs/opal/POKEDEX_RUNTIME_QA.md` and `docs/overhaul/STATUS.md` truthfully. Do not remove the existing limitation until a running ROM is checked. Do not merge PR #109 without runtime acceptance.

## Repository-scope and implementation discipline

Continue **PR #109** only; keep Bag V3 independent. Keep changes cohesive in two commits where practical (habitat data/rendering and visual assets/UX) and add source-driven tests. A new static report alone does not satisfy this task. Do not delete the accurate textual Locations page or make all special acquisition types display as wild habitats.
