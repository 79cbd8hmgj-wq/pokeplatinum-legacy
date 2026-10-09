# Pokémon Opal — Asset Direction and Creative Integration Policy

**Authoritative direction clarification (2026-10-09).**

## Product identity

Pokémon Opal is a distinct game built on the Pokémon Platinum decompilation and its technical/asset foundation. It is **not** merely an overhauled Platinum, nor a project to import complete donor libraries into Platinum. Earlier Platinum redesign decisions remain useful project material, but must be evaluated in the context of Opal rather than presumed to define its finished identity.

Assets from available Pokémon games are a curated collection of creative ingredients, not a checklist of assets that must be imported.

## Allowed asset treatment

- **Preserve:** retain the Platinum component if it already best serves Opal.
- **Replace:** use a stronger donor asset where visual and technical fit warrants it.
- **Enhance:** improve a Platinum asset using donor detailing, palette/shading, motion, texture, or presentation techniques.
- **Composite:** blend selected parts from multiple games and original work into one Opal-specific asset.
- **Animate:** derive new movement, timing, effects, or layered behavior from donor examples.
- **Create:** design original Opal assets using source components or concepts as references.
- **Discard:** ignore donor material that does not improve the finished experience.

A donor sprite's silhouette, palette, expression, highlights, specific frames, timing or animation can be useful even if its original sprite is never shipped. A finished effect may combine a Platinum base, HGSS detail, Emerald particles, Ranger effects, and newly authored frames where appropriate.

## Revised IO-FOL-SHEETS interpretation

PR #93 is a **catalog/export and validation capability** for 572 HGSS follower sprite sheets. The 572 count is *not* a requirement to add 572 followers to Pokémon Opal; 9,152 exported PNG frames are a **reference/ingredient output**, not an in-game resource requirement.

The previous `IO-FOL-SHEETS_FIELD_LOADER_INTEGRATION.md` is a **conditional technical investigation only**. Its full-library packaging, ID registration, map object loading, and 572-entry integration gates are NOT global Opal project completion gates. Use it only if a specific approved Opal asset actually requires Platinum field-sprite integration.

Do not make universal HGSS follower support the automatic follow-up to PR #93. A successful exporter/catalog can stand as a donor tool without any runtime import.

## Opal asset workflow

1. **Pick a specific Opal host asset, scene, animation, UI element, battle effect, environment, or mechanic** that would benefit from improvement.
2. **Inspect donor candidates** across relevant Pokémon titles. Capture exact donor source, usable subcomponents, formats, technical constraints, and duplication risks.
3. **Make a creative decision**: preserve, replace, enhance, composite, animate, create, or discard. Choose what contributes to the finished Opal experience rather than the maximum import count.
4. **Write a small bounded asset recipe**: Platinum baseline, specific donor ingredients, original additions, expected appearance/motion, exact affected Opal files, and exclusions.
5. **Technical preflight only for selected implementation**: palette limits, frame/memory footprint, build resource hooks, runtime lifetime, screen/layout constraints.
6. **Implement a targeted change**, with source attribution and provenance notes where possible; ask Claude Code only for bounded execution or compilation problems.
7. **Build, visually compare, and playtest** the changed asset in Opal. Judge the in-game result, not the number of reused assets.
8. **Keep a ranked opportunity ledger** and close individual features when they are demonstrated rather than closing entire donor catalogs as if they were features.

## Scope cautions

- Do not assume all Platinum features, regions, story structure, or graphics must remain unchanged; those are game-design decisions for Opal.
- Do not invent a complete Opal story/world/region identity before it is specified.
- Research and prototype asset compatibility selectively; never sink time into bulk loading simply because exporter tooling exists.
- Donor work may have copyright/distribution implications; track provenance and review release rights before distributing compiled materials.
- Keep documentation and implementation specifications in GitHub, not standalone downloaded checkpoints.

## Next work item

Reclassify IO-FOL-SHEETS as a reusable **donor source pipeline** and select the highest-value concrete Opal visual improvement from the existing visual opportunity catalog for a bounded composite recipe. Avoid blanket 'support all follower sprites' milestones.
