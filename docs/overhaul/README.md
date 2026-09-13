# Pokémon Platinum Overhaul — Canonical Documentation

This directory is the source of truth for the Pokémon Platinum overhaul.

## Read order

1. `MASTER_PLAN.md` — roadmap, phase order, dependencies, completion criteria.
2. `STATUS.md` — exact current checkpoint and implementation state.
3. `MASTER_SPEC.md` — locked design rules and subsystem decisions.
4. `IMPLEMENTATION_PLAN.md` — how approved design is converted into guarded source changes.
5. `EMERALD_PORT_PLAN.md` — how finalized Emerald systems are reused in Platinum.
6. subsystem documents under this directory — detailed move/species/TM/HM/encounter/etc. authority.

## Authority rules

- Repository documentation is authoritative over chat history once a decision is captured here.
- `LOCKED` means the design must not be changed during implementation without an explicit design amendment.
- `SUPERSEDED` means an older ruling must not be implemented.
- `DEFERRED` means intentionally outside the current Core 1.0 scope.
- `IMPLEMENTED` means source changes exist but may still require validation.
- `VERIFIED` means the relevant build/runtime/semantic checks passed.
- Chat transcripts and recovery files are evidence used to reconstruct this documentation, not the long-term source of truth.

## Current project state

The Pokémon/move design work through C3 is closed. Implementation is in C2.5E/C3H, with created-move plumbing required before species ledgers that reference the new `MOVE_*` constants are applied.

The next planning-heavy work after the current implementation gate is an Emerald-to-Platinum port audit followed by world availability, trainers/economy, events/postgame, and full QA.
