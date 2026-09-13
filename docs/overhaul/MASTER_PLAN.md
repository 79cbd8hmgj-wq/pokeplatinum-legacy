# Pokémon Platinum Overhaul — Master Plan

## Project identity

Build a single-player-complete, enriched version of Pokémon Platinum that succeeds the Emerald overhaul instead of merely copying it.

Core targets:

- All Pokémon #001–#493 obtainable in one save.
- Every non-legendary evolutionary family obtainable before the Elite Four.
- No required trading, second DS, GBA cartridge, version exclusivity, WFC distribution, or multiplayer gate.
- Evolved forms are primarily earned through evolution rather than saturating wild encounter tables.
- Legendary and Mythical Pokémon use proper encounters, restored events, quests, or gifts.
- Trade evolutions are replaced with logical level/item/friendship/location methods.
- Pokémon identities are strengthened through typing, stats, abilities, moves, evolution timing, and selective compatibility changes.
- Progression is faster and less grind-heavy without flattening the campaign.
- Trainer difficulty is improved through coherent teams and better progression, not by turning the game into a restrictive difficulty hack.
- Breeding, capture, economy, Frontier, Underground, and event systems should become meaningful single-player systems.

## Status vocabulary

- `PLANNED` — scope defined; design not locked.
- `LOCKED` — design authority is final unless explicitly amended.
- `IMPLEMENTING` — source work active.
- `IMPLEMENTED` — source changes exist.
- `VERIFIED L2` — supported builds pass.
- `VERIFIED L4` — targeted runtime behavior verified.
- `DEFERRED` — intentionally outside Core 1.0.

## Phase 0 — Repository foundation

**Status: IMPLEMENTING**

Goals:

- Keep project authority in Git rather than chat history.
- Maintain canonical docs under `docs/overhaul/`.
- Give Claude/other implementation agents a single read order and explicit supersession rules.
- Preserve provenance for recovered historical work.
- Use guarded edits, semantic diffs, build gates, and narrow commits.

Current vehicle: `overhaul/canonical-docs` / draft PR #8.

## Phase 1 — Pokémon and move foundation

### A. Species identity

**Design: LOCKED**
**Implementation: IMPLEMENTED through C3H**
**Verification: L2 build**

Includes selected retypes, stat redistribution/repair, ability changes, species roles, and related learnset identity work.

### B. Existing move rework (C1)

**Design: LOCKED**
**Implementation: NOT YET APPLIED**
**Recovery: 82/82 edit membership recovered; five Batch 9F final values still unresolved**

C1 remains the one major completed design package that must be fully canonicalized before implementation.

Do not implement from proposal spreadsheets or Emerald move specs.

### C. TM/HM system (C2)

**Design: LOCKED**
**Implementation: PARTIAL**

Locked design includes:

- reusable TMs;
- TM21 Air Slash;
- TM78 Power Gem;
- acquisition/source policy;
- TM economy;
- HM battle rework;
- compatibility framework.

The C3H compatibility portion is already implemented and L2 build-verified. Reusable-TM behavior, HM battle changes, TM economy/source changes, and related C2 mechanics require separate implementation/audit.

### D. Created move ecosystem (C2.5)

**Design: LOCKED**
**Implementation: IMPLEMENTED**
**Verification: L2 build**

Mainline implementation:

`071b8c7976801e64af5296f30b7437d7da2d8632`

- 22 custom moves;
- IDs 468–489;
- target/current `MAX_MOVES = 490`;
- mod-aware CI for US Rev 0 / Rev 1;
- build run `33981291318`: success.

Focused runtime tests remain necessary before L4 verification.

### E. Species learnsets and compatibility (C3)

**Design: LOCKED**
**Implementation: IMPLEMENTED**
**Verification: L2 build**

Mainline implementation:

`8a74452654e1552b78bfb329afcb351a2caec5cf`

This applies:

- C3H compatibility rebuild;
- 225 guarded species operations;
- final Torkoal correction;
- final Seviper correction.

Build run `33995072848`: success.

Historical ledgers remain audit/provenance material and must not be reapplied over current main.

## Phase 2 — Foundation verification + remaining C1/C2 implementation

**Status: ACTIVE NEXT PHASE**

This replaces the obsolete plan to implement C2.5E/C3H from scratch.

Order:

1. Finish C1 canonical recovery.
2. Generate and validate the complete 82-edit C1 manifest against current main.
3. Apply C1 with guards.
4. Build both supported US revisions.
5. Audit/implement remaining C2 mechanics:
   - reusable TMs;
   - HM battle values/Defog behavior;
   - TM economy/source changes where not yet landed.
6. Perform focused runtime tests for custom moves and high-risk mechanics.
7. Semantic-audit current C3H state against canonical design.
8. Update status evidence before moving into world-scale work.

## Phase 3 — Emerald-to-Platinum system port

**Status: PLANNED / ready after foundation stabilization**

Default rule:

> Reuse finalized Emerald design/behavior whenever it still serves Platinum goals; translate implementation into Platinum architecture instead of redesigning from scratch.

Classify each subsystem as:

- `DIRECT PORT`
- `ADAPT`
- `PLATINUM-SPECIFIC`
- `DEFER`

Priority:

- evolution/trade-evolution removal;
- EXP/progression economy;
- mart/item economy;
- Poké Ball rebalance;
- breeding improvements;
- grind reduction/QoL.

Detailed policy: `EMERALD_PORT_PLAN.md`.

## Phase 4 — Evolution system + one-save evolution accessibility

**Status: PARTIAL DESIGN / PLANNED IMPLEMENTATION**

Before encounter placement, lock and implement a complete evolution manifest:

- all trade evolutions replaced;
- Gen IV held-item trade evolutions adapted;
- friendship/location methods reviewed for tedium/access;
- required items deliberately obtainable;
- every evolution possible in one save;
- no evolution timing conflicts with finalized learnsets.

## Phase 5 — World and #001–#493 availability

**Status: PLANNED**

Goals:

- early National Dex access while preserving the 210-species regional story identity;
- all non-legendary base families before the Elite Four;
- normal alternatives for version exclusives, dual-slot species, and hard daily/rotation gates;
- Honey Tree improvements;
- both fossil paths available;
- Spiritomb obtainable through single-player Underground progression;
- deliberate evolution-item distribution;
- rare encounters meaningful without excessive 1% frustration.

## Phase 6 — Trainers, items, and economy

**Status: PLANNED**

Trainer targets:

- coherent important-trainer teams;
- improved Rival/Galactic progression;
- stronger Gym/Elite Four/Cynthia progression;
- rematches;
- ordinary trainers showcasing new availability and mechanics.

Economy targets:

- less grinding without making money meaningless;
- practical healing/catching/team experimentation;
- reliable evolution-item access;
- sensible repeatable money/BP sources.

Emerald numerical settings are starting evidence, not automatic Platinum locks.

## Phase 7 — Mechanical and breeding systems

**Status: PLANNED / partly designed**

Includes:

- EXP changes;
- capture/Poké Ball behavior;
- breeding improvements;
- AI improvements where justified;
- any remaining QoL engine work.

Baseline campaign functionality must not depend on breeding.

Field-move decoupling remains `DEFERRED` for Core 1.0 unless later proven unusually low-risk.

## Phase 8 — Legendary, Mythical, and event restoration

**Status: PLANNED**

Prefer Platinum-native infrastructure:

- Darkrai — Member Card/Newmoon Island;
- Shaymin — Oak's Letter/Seabreak Path;
- Arceus — Azure Flute/Hall of Origin;
- Rotom forms — Secret Key room;
- Regis/Regigigas — remove event-Regigigas dependency;
- Manaphy/Phione — one-save accessible path;
- Dialga/Palkia — preserve native postgame encounter structure;
- other migration/version-exclusive legendaries — dedicated Platinum-native encounters/quests.

## Phase 9 — Postgame and Battle Frontier

**Status: PLANNED**

Includes Frontier economy, rematches, postgame encounter cleanup, optimization resources, and completion rewards.

## Phase 10 — Full QA

**Status: PLANNED**

Release-blocking checks:

- #001–#493 obtainable;
- every evolution achievable;
- no external hardware/service requirement;
- no progression softlocks;
- TM/key-item completeness;
- trainer legality/progression;
- move/learnset validation;
- custom-move runtime behavior;
- encounter-rate audit;
- economy/progression playtest;
- event-state validation;
- Rev 0 + Rev 1 builds;
- semantic diff against intended design.

## Phase 11 — Release

**Status: PLANNED**

Outputs:

- versioned source tag;
- release notes/changelog;
- patch generation;
- player-facing documentation;
- known-issues list;
- reproducible build/verification instructions.

## Immediate execution order

1. Finish canonical repo documentation/recovery.
2. Resolve the final five C1 Batch 9F values and produce the exact 82-edit manifest.
3. Implement/build C1.
4. Audit/implement remaining C2 mechanics.
5. Run targeted L4 runtime QA on created moves + C3 high-risk cases.
6. Perform Emerald-to-Platinum port audit and implement evolution system.
7. Build the 493 availability plan and encounter tables.
8. Trainers/economy/events/postgame.
9. Full QA and release.
