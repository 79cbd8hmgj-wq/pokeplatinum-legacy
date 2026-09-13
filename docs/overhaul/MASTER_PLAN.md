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

- `PLANNED` — scope is defined but design is not locked.
- `LOCKED` — design authority is final unless explicitly amended.
- `IMPLEMENTING` — source work is active.
- `IMPLEMENTED` — source changes exist.
- `VERIFIED` — build/runtime/semantic verification passed.
- `DEFERRED` — intentionally outside Core 1.0.

## Phase 0 — Repository foundation

**Status: PARTIAL / ongoing**

Goals:

- Keep the overhaul in Git, not in chat history.
- Maintain canonical docs under `docs/overhaul/`.
- Use guarded edits, semantic diffs, and build gates.
- Preserve clean checkpoints and narrowly scoped commits.
- Verify both supported US Platinum revisions before release.

Required outputs:

- master plan
- status file
- master design spec
- implementation plan
- Emerald port plan
- subsystem specs/manifests

## Phase 1 — Pokémon and move foundation

### A. Species identity

**Design status: LOCKED**

Includes:

- selected retypes
- stat redistribution/repair
- ability changes
- species roles
- evolution identity rules

### B. Existing move rework (C1)

**Design status: LOCKED**

Goals already completed:

- revive weak/obsolete moves without broad modern-power inflation
- preserve Generation IV character
- repair physical/special progression gaps
- keep useful niche identities rather than turning every attack into an 80-BP clone

### C. TM/HM system (C2)

**Design status: LOCKED**

Key rulings:

- TMs are reusable.
- 90 of 92 TM move assignments remain vanilla.
- TM21 becomes Air Slash.
- TM78 becomes Power Gem.
- First acquisition still gates access.
- Game Corner/Frontier TM economies are reduced where grind was excessive.
- HM field use remains coupled to moves for Core 1.0.
- HMs are made respectable battle moves.

### D. Created move ecosystem (C2.5)

**Design status: LOCKED**
**Implementation status: IMPLEMENTING**

- 22 custom moves total.
- 9 generic progression moves.
- 13 species/family identity moves.
- IDs 468–489 reserved.
- `MAX_MOVES` target: 490.
- Created-move plumbing must build before species ledgers referencing the new constants are applied.

### E. Species learnsets and compatibility (C3)

**Design status: LOCKED**
**Implementation status: IMPLEMENTING**

Completed design categories:

- level-up learnsets
- evolution timing audit
- natural-STAB/dead-slot audit
- TM/HM compatibility consolidation
- tutor consolidation
- egg-move consolidation

Known final correction:

- Banette keeps Shadow Ball at Lv31, evolves at Lv37, gains Cursed Stitch at Lv38, and Shadow Claw at Lv42.

## Phase 2 — Core implementation gate

**Status: IMPLEMENTING**

This phase turns the locked Phase 1 design into verified source.

Order is mandatory:

1. Implement all 22 custom moves and resource plumbing.
2. Build and validate the move layer.
3. Apply guarded species type/stat/ability/learnset ledgers.
4. Apply TM/HM compatibility patch.
5. Build again.
6. Run semantic diff and invariant checks.
7. Runtime-test representative/high-risk mechanics.
8. Mark completed batches `VERIFIED` only after evidence exists.

Do not apply learnset operations referencing new `MOVE_*` constants before the custom-move build gate passes.

## Phase 3 — Emerald-to-Platinum system port

**Status: PLANNED**

Default rule:

> Reuse the finalized Emerald design/behavior whenever it still serves the Platinum goals; translate the implementation into Platinum's architecture instead of redesigning from scratch.

Classify every Emerald subsystem as:

- `DIRECT PORT` — behavior/design can transfer essentially unchanged.
- `ADAPT` — keep the design but translate for Sinnoh/Gen IV systems.
- `PLATINUM-SPECIFIC` — use native Platinum infrastructure instead.
- `DEFER` — not needed for Core 1.0.

Priority systems:

- trade-evolution removal and evolution accessibility
- EXP/progression economy
- mart/item economy
- Poké Ball rebalance
- breeding improvements
- full-dex availability philosophy
- grind reduction/QoL

Detailed policy lives in `EMERALD_PORT_PLAN.md`.

## Phase 4 — World and 493 availability

**Status: PLANNED**

Goals:

- early National Dex access while preserving the 210-species regional story identity
- all non-legendary base families before the Elite Four
- normal alternatives for Diamond/Pearl exclusives
- normal alternatives for GBA dual-slot species
- normal alternatives for mandatory swarm/Radar/Trophy Garden/Great Marsh rotations
- Honey Tree improvements
- both fossil paths available
- Spiritomb obtainable through single-player Underground progression
- evolution items deliberately distributed
- rare encounters meaningful without excessive 1% frustration

Encounter philosophy:

- Early game: Sinnoh remains dominant; older families supplement weak type variety.
- Midgame: National Dex breadth expands through distinct ecological systems.
- Late story: rare/pseudo-legendary families become available.
- Postgame: legendary quests, optimization, rematches, Frontier, collection cleanup.

## Phase 5 — Trainers, items, and economy

**Status: PLANNED**

Trainer targets:

- coherent important-trainer teams
- fuller Gym teams where appropriate
- improved Rival development
- stronger Galactic identities
- Elite Four/Cynthia as the main-story benchmark
- National Dex rematches
- ordinary trainers showcasing newly available species/mechanics

Economy targets:

- less grinding without making money meaningless
- practical healing/catching/team experimentation
- reliable evolution-item access
- cheaper vitamins and practical move services
- controlled repeatable money sources
- improved BP economy

Emerald numerical settings are starting points for testing, not automatic Platinum locks.

## Phase 6 — Mechanical and breeding systems

**Status: PLANNED / partly designed**

Includes:

- evolution logic changes
- capture/Poké Ball behavior
- EXP changes
- reusable-TM runtime behavior if not already completed
- Defog battle-effect correction
- AI improvements where justified
- breeding improvements

Breeding rule for Platinum:

- baseline campaign functionality comes from level-up moves, not breeding
- vanilla Platinum egg pools remain the default unless a specific locked change exists
- broader Emerald breeding innovations are port candidates, but must be reviewed against Platinum's richer native breeding system

Field-move decoupling remains `DEFERRED` for Core 1.0 unless implementation cost proves unexpectedly low and safe.

## Phase 7 — Legendary, Mythical, and event restoration

**Status: PLANNED**

Prefer Platinum-native infrastructure:

- Darkrai — Member Card/Newmoon Island sequence
- Shaymin — Oak's Letter/Seabreak Path
- Arceus — Azure Flute/Hall of Origin
- Rotom forms — Secret Key room
- Regirock/Regice/Registeel — no event-Regigigas dependency
- Regigigas — after obtaining the three Regis
- Manaphy — Sinnoh-side quest or restored gift
- Phione — breeding
- Dialga/Palkia — existing postgame encounters
- legendary birds — existing roaming framework, improved if needed
- other version/migration-exclusive legendaries — dedicated quests/encounters

## Phase 8 — Postgame and Battle Frontier

**Status: PLANNED**

Includes:

- Frontier economy
- rematches
- postgame encounter cleanup
- optimization resources
- completion rewards
- optional late-game collection methods

## Phase 9 — Full QA

**Status: PLANNED**

Release-blocking checks:

- every species #001–#493 obtainable
- every evolution achievable in one save
- no external hardware/service requirement
- no progression softlocks
- every TM/key item obtainable
- trainer legality checks
- learnset and move-ID validation
- encounter-rate audit
- economy/progression playtest
- event-state validation
- save compatibility testing where supported
- Rev 0 and Rev 1 builds
- custom-move runtime tests
- TM/HM compatibility checks
- complete semantic diff against intended design

## Phase 10 — Release

**Status: PLANNED**

Outputs:

- versioned source tag
- release notes/changelog
- patch generation
- player-facing documentation
- known-issues list
- reproducible build/verification instructions

## Immediate execution order

1. Finish canonical repo documentation.
2. Finish and verify created-move plumbing.
3. Apply/verify C3 species + compatibility implementation.
4. Run the Emerald-to-Platinum port audit.
5. Implement evolution/economy/capture/breeding ports in dependency order.
6. Build the 493 availability plan and encounter tables.
7. Continue through trainers/economy/events/postgame.
8. Full QA and release.
