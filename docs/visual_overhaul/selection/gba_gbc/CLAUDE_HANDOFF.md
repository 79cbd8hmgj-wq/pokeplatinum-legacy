# Claude handoff — GBA/GBC donor mining

Use this file instead of re-reading old chats.

## Phase

Database collection only. Do **not** implement Platinum visual changes yet.

The DS donor database and PR #70 planning artifacts are already complete enough to pause. This branch prepares the deferred GBA/GBC phase.

## Read only these setup files first

1. `gba_gbc/README.md`
2. `gba_gbc/SOURCE_AVAILABILITY.json`
3. `gba_gbc/SOURCE_TARGETS.json`
4. `gba_gbc/SEED_VERIFICATION_STATUS.json`
5. `gba_gbc/MINING_EXECUTION_PLAN.md`

Read `OPPORTUNITY_CLASSES.json` only if a taxonomy detail is unclear.

Do **not** reread the full DS catalogs, old chat exports, or donor repos broadly during orientation.

## Canonical taxonomy

- novel_capability
- novel_detail
- technique_donor
- component_donor
- enhancement_candidate
- replacement_candidate
- reference_only
- reject

Replacement is not the default.

## Pinned donors

Use only the exact revisions in `SOURCE_AVAILABILITY.json`.

## First execution tranche

Start with **seed verification**, not bulk inventory.

Order:

1. Emerald
   - formalize `field_action_choreography`
   - formalize `environment_effect_primitives`
   - begin from exact functions/paths in `SOURCE_TARGETS.json`
   - trace only directly referenced graphics/assets
2. FireRed
   - the map-preview, timed-palette, and Deoxys-state seeds already have strong source verification
   - bind exact evidence/provenance and promote/reject them into the separate GBA/GBC layer
3. PMD Red
   - status-overlay render path is already identified
   - close this seed before touching the broader effect archive
4. Crystal
   - bind unusual primitive graphics to specific move scripts/framesets
5. Ruby
   - semantic delta against Emerald only
6. Yellow
   - high-threshold specialized review only

## Output rule

Keep GBA/GBC records separate from the DS pool until the GBA/GBC layer is stable.

Expected phase outputs remain:

- `GBA_GBC_CATALOG_STATUS.md`
- `GBA_GBC_OPPORTUNITY_POOL.json`
- `GBA_GBC_OPPORTUNITY_POOL_SUMMARY.md`
- `GBA_GBC_NEEDS_EVIDENCE.json`
- donor/subsystem/component/technique summaries

Do not rewrite DS opportunity records.

## Context discipline

- source/system first
- referenced assets second
- broad decode only if a verified family proves worthwhile
- repository artifacts hold detailed evidence
- chat reports only counts, decisions, blockers, and next action

## First stop point

After Emerald + FireRed + PMD Red seed verification, stop and report:
- seeds verified/promoted/rejected
- exact new evidence artifacts
- counts by class
- any new high-value family discovered
- whether Crystal/Ruby/Yellow scope should change

Then continue only if no design blocker exists.
