# GBA/GBC donor mining setup

This directory is the staging area for the deferred GBA/GBC visual-donor phase.

## Purpose

Reduce repeated archaeology and agent context use before bulk mining begins. The existing DS opportunity pool remains authoritative and unchanged. GBA/GBC work stays separate until verified findings are ready for a combined cross-generation ranking.

Canonical opportunity classes remain those in `../OPPORTUNITY_CLASSES.json`:

- novel_capability
- novel_detail
- technique_donor
- component_donor
- enhancement_candidate
- replacement_candidate
- reference_only
- reject

Replacement is deliberately not the default outcome.

## Donor order

1. Emerald
2. FireRed / LeafGreen
3. PMD Red Rescue Team
4. Crystal
5. Ruby
6. Yellow

Ruby is delta-first against Emerald. Yellow is high-threshold. LeafGreen is treated as a FireRed sibling unless unique resources are found.

## Pinned sources

Exact repositories and revisions are recorded in:

- `SOURCE_AVAILABILITY.json`
- `GBA_GBC_SOURCE_MAP.md`

Verified repositories currently cover Emerald, FireRed, PMD Red, Crystal, Ruby and Yellow. No distinct LeafGreen checkout was found during preflight; FireRed is the shared baseline.

## Canonical setup artifacts

- `DONOR_SCOPE.json` — phase boundary, donor roles, stop conditions
- `SUBSYSTEM_TARGETS.json` — high-value subsystem search order
- `PRIOR_FINDINGS_SEED.json` — normalized prior hypotheses
- `SOURCE_AVAILABILITY.json` — pinned donor repositories/revisions
- `GBA_GBC_SOURCE_MAP.md` — human-readable source map
- `SOURCE_TARGETS.json` — exact source-path/symbol anchors for mining
- `GBA_GBC_TARGET_MAP.md` — concise human-readable target summary
- `SEED_VERIFICATION_STATUS.json` — preflight verification state
- `MINING_EXECUTION_PLAN.md` — token-efficient execution plan

## Preflight progress

The following prior hypotheses now have exact source anchors:

- Emerald field-action choreography
- Emerald environmental effect primitives
- FireRed area/location previews
- FireRed timed Pokémon League palette animation
- FireRed interactive Deoxys-rock visual states
- PMD Red battler status overlays
- Crystal battle-animation primitives/choreography
- Yellow Pikachu-specific presentation
- Ruby delta-only comparison policy

FireRed's preview, timed-palette and Deoxys-state hypotheses are source-verified. PMD Red's status-overlay render path and explicit status graphics mapping are source-verified. The remaining seeds have exact paths and need narrower semantic/evidence passes rather than repository rediscovery.

Nine prior non-DS findings remain preserved in:

`../opportunities/deferred/non_ds_findings.json`

They are not active ranked findings until re-derived/verified through this phase.

## Execution rule

Start at `SOURCE_TARGETS.json`; trace only referenced assets/functions first. Do not perform broad donor rescans unless a verified system exposes another high-value family.

Do not modify Platinum assets/source during database collection.
