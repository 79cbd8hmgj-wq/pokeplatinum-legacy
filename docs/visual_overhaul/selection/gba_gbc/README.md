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

## Donor set

Primary mining targets:

1. Emerald
2. FireRed / LeafGreen
3. PMD Red Rescue Team
4. Crystal
5. Ruby
6. Yellow

Ruby is delta-first against Emerald. Yellow is high-threshold. LeafGreen is treated as a FireRed sibling unless unique resources are found.

## Current state

Nine prior non-DS findings are already preserved in:
`../opportunities/deferred/non_ds_findings.json`.

They are leads, not active ranked findings. Most are low-confidence and require donor-checkout verification.

Setup artifacts in this directory define:
- donor scope and stop rules
- subsystem targets
- prior finding seed ledger
- source-availability matrix
- execution order

Do not modify Platinum assets/source during database collection.
