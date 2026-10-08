# GBA/GBC mining execution plan

## Objective

Finish the donor database before any Platinum implementation. Reuse the existing opportunity taxonomy and keep GBA/GBC provenance separate from the DS pool.

## Token-efficient execution order

### 0. Preflight
For each donor, locate the checkout/source tree, pin the revision, and record the usable tooling. Do not infer availability from old chat history alone.

### 1. Source-code/system pass
Search readable source first for the systems named in `SUBSYSTEM_TARGETS.json`.

This is deliberately earlier than bulk asset extraction. A known system/function can reveal:
- exact referenced graphics
- palette tables
- animation frames
- state transitions
- event triggers
- timing
- sound/effect relationships

Only assets referenced by promising systems should move into the first decode queue.

### 2. Seed verification
Resolve the hypotheses in `PRIOR_FINDINGS_SEED.json` before broadening scope.

For each seed:
- verify donor path/function/table
- pin provenance
- record representative assets
- confirm or revise classification
- reject if prior-session memory does not survive source verification

### 3. High-value subsystem mining
Process donor-by-donor, subsystem-by-subsystem:
1. Emerald
2. FireRed/LeafGreen
3. PMD Red
4. Crystal
5. Ruby deltas
6. Yellow specialized pass

### 4. Minimum decoding
Build only narrow decoders/renderers that unlock a high-value family. Prefer family-level evidence over exhaustive manual review.

### 5. Separate opportunity layer
Create GBA/GBC outputs without modifying the DS opportunity pool. Combined ranking comes only after GBA/GBC records are stable.

## Per-donor search plan

### Emerald
Start in field-move/field-effect source and battle animation scripts. Trace referenced graphics second. Highest-value questions:
- Which field actions have explicit Pokemon-assisted choreography?
- Which environmental effects provide reusable primitives?
- Which battle script structures add timing/layering ideas Platinum does not already exploit?

### FireRed / LeafGreen
Start with map preview, palette animation, and interactive-object/event source. Highest-value questions:
- How are location previews associated with maps and visited state?
- How are timed palette sequences represented?
- Which events combine object position, palette, sound and effect state?

### PMD Red
Start with dungeon/UI status rendering and condition-display code. Trace exact symbol assets and cycling behavior. Do not catalog generic dungeon art until this is resolved.

### Crystal
Start with battle animation command/data tables and their referenced graphics. Focus on primitives/choreography, not engine backporting.

### Ruby
First compute source/resource deltas against Emerald for the target subsystems. Only unique material proceeds.

### Yellow
Search only the already-identified battle transition/effect and Pikachu-specific presentation areas. Stop quickly when material is superseded by later donors.

## Evidence tiers

1. **Source verified** — exact path/function/table at pinned revision.
2. **Asset linked** — system references exact graphic/palette/frames.
3. **Rendered** — representative deterministic render/contact sheet.
4. **Reviewed** — agent/human review confirms usefulness.

Opportunity confidence must reflect the strongest completed tier.

## Output contract

Future mining should populate:
- `GBA_GBC_SOURCE_MAP.md`
- `GBA_GBC_CATALOG_STATUS.md`
- `GBA_GBC_OPPORTUNITY_POOL.json`
- `GBA_GBC_OPPORTUNITY_POOL_SUMMARY.md`
- `GBA_GBC_NEEDS_EVIDENCE.json`
- donor/subsystem/component/technique summaries

Do not activate or rank these against DS until provenance and validation are complete.

## Context discipline

Detailed evidence belongs in repository artifacts. Chat status should contain counts, promoted/rejected seeds, blockers and next actions only.
