# Pokémon Platinum Overhaul — Master Design Spec

## Scope and authority

This document records locked cross-system design rules. Detailed species-by-species and implementation manifests may live in subsystem files, but they must obey this spec unless an explicit amendment supersedes it.

## Core identity

- Single-save completion for #001–#493.
- Every non-legendary family obtainable before the Elite Four.
- No required trading, second DS, GBA cartridge, version exclusivity, WFC distribution, or multiplayer gate.
- Wild encounters favor the lowest practical evolutionary stage.
- Legendary/Mythical content uses proper encounters, restored events, quests, or gifts.
- Progression is less grind-heavy but remains meaningful.
- The project is not a pure hard-mode hack.
- Generation IV's physical/special split and move ecosystem remain central.
- Targeted enrichment is preferred over blanket stat/coverage inflation.

## Retype authority

The locked project includes the following established retype directions among its major carry-forward/Platinum identity changes:

- Blastoise — Water/Ground
- Raichu — Electric/Steel
- Psyduck — Water/Psychic
- Golduck — Water/Psychic
- Farfetch'd — Fighting/Flying
- Pinsir — Bug/Fighting
- Feraligatr — Water/Ground
- Sceptile — Grass/Dragon
- Vigoroth — Normal/Fighting
- Slaking — Normal/Fighting
- Milotic — Water/Dragon
- Glalie — Ice/Steel
- Shinx — Electric/Dark
- Luxio — Electric/Dark
- Luxray — Electric/Dark
- Electabuzz — Electric/Fighting
- Electivire — Electric/Fighting

Implementation must use the final guarded species ledgers/species authority rather than inferring missing stats/abilities from this summary.

## Species-design rules

### Stats

- Do not increase every weak Pokémon's BST indiscriminately.
- Prefer redistribution, targeted boosts, ability repair, and better move access.
- Strong/high-BST species should usually be repaired through role clarity, timing, or compatibility rather than additional raw stats.

### Abilities

- Ability changes must reinforce the intended role.
- Existing defining drawbacks remain when they are fundamental identity constraints; example: Slaking retains Truant.

### Level-up moves

Level-up learnsets provide basic campaign functionality.

A redesigned Pokémon should not require:

- breeding
- a late/postgame tutor
- a rare one-off move
- awkward evolution delay

to obtain ordinary STAB or express its locked role.

Evolution timing must be checked so important post-evolution moves occur after the evolution level or are otherwise naturally/reminder-accessible as designed.

### Stone/item/location evolution

Evolution should not punish the player by deleting the evolved species' core identity.

Do not duplicate every pre-evolution move automatically; preserve only what the evolved role actually needs.

## Existing move rework (C1)

Status: `LOCKED`.

Principles:

- revive weak/obsolete early and midgame moves
- keep useful niche effects
- avoid broad late-generation homogenization
- preserve meaningful differences between reliable moves, conditional moves, priority, multi-hit, crit, drain, setup, and coverage

Representative locked changes include:

- Fury Cutter: 20 BP / 100 Acc
- Leech Life: 40 BP
- Pin Missile: 20 BP / 95 Acc
- Twineedle: 30 BP per hit
- Silver Wind: 10 PP
- Giga Drain: 75 BP
- Iron Tail: 85 Acc
- Rock Tomb: 60 BP / 95 Acc
- Thief: 60 BP
- Steel Wing: 75 BP / 95 Acc
- Drain Punch: 75 BP / 10 PP
- Will-O-Wisp: 85 Acc
- Toxic: 90 Acc
- Power Gem: 80 BP

Detailed final move-data authority should be stored separately rather than reconstructed from this summary.

## TM system (C2)

### Reusable TMs

TMs are reusable.

First acquisition remains the progression gate; reusable does not mean globally unlocked.

### TM roster

Platinum retains 92 TM slots.

- TM21: Frustration → **Air Slash**
- TM78: Captivate → **Power Gem**
- the other 90 TM move assignments remain vanilla

Frustration and Captivate remain valid battle moves; they simply stop occupying those TM slots.

### Acquisition

Preserve vanilla first-acquisition progression by default:

- field pickups stay where practical
- Gym TM rewards remain their original moves/locations
- story/NPC rewards remain progression milestones
- TM21 Air Slash inherits TM21 sources
- TM78 Power Gem inherits the TM78 Victory Road source
- postgame Frontier exclusivity can remain where it does not break campaign functionality

### Economy

Department Store TM prices are not broadly reduced.

Game Corner TM prices are reduced substantially to eliminate excessive grind while preserving early-access tradeoffs.

Battle Frontier TM BP conversion is locked at:

- 32 BP → 16 BP
- 40 BP → 20 BP
- 48 BP → 24 BP
- 64 BP → 32 BP
- 80 BP → 40 BP

## HM system

Field-move decoupling: `DEFERRED` for Core 1.0.

Locked battle identities:

| HM | Final behavior |
|---|---|
| Cut | 70 BP / 100 Acc / 30 PP / high critical-hit ratio |
| Fly | 100 BP / 100 Acc / 15 PP / retain two-turn behavior |
| Surf | 95 BP / 100 Acc / 15 PP / vanilla targeting/effect |
| Strength | 80 BP / 100 Acc / 15 PP |
| Defog | target Evasion -1; hazards cleared from both sides; target-side screens/Safeguard/Mist cleared; overworld function retained |
| Rock Smash | 60 BP / 100 Acc / 15 PP / 50% Defense -1 |
| Waterfall | 80 BP / 100 Acc / 15 PP / 20% flinch |
| Rock Climb | 90 BP / 95 Acc / 20 PP / 20% confusion |

Defog requires focused behavior validation.

## Compatibility framework

### Baseline

For unchanged TMs, vanilla Platinum compatibility is the starting point.

Add compatibility only when role/anatomy/type identity provides a clear reason. Coverage requires stronger justification than appropriate STAB.

Retyping does not grant every same-type TM automatically.

### Evolution families

Pre-evolution compatibility normally carries forward unless there is a reason not to; evolved forms may gain additional logical access.

Babies may remain narrower.

### TM21 / TM78 replacement masks

Old slot compatibility must not survive.

- TM21 Air Slash: **49 locked recipients**
- TM78 Power Gem: **27 locked recipients**

The exact recipient lists belong in the compatibility manifest/spec and must be applied as authoritative whole sets.

### Retype-family additions

Design-locked additions:

- Farfetch'd: TM31 Brick Break; HM06 Rock Smash
- Electabuzz: TM08 Bulk Up; TM60 Drain Punch
- Electivire: TM08 Bulk Up; TM60 Drain Punch
- Vigoroth: TM60 Drain Punch
- Slaking: TM60 Drain Punch
- Shinx: TM66 Payback
- Luxio: TM66 Payback
- Luxray: TM66 Payback

Implementation reconciliation additionally requires Raichu TM91 Flash Cannon because the live source lacked the compatibility that the design assumed.

## Created moves (C2.5)

Status: `LOCKED`.

- 22 total
- 9 generic progression moves
- 13 identity moves
- no created move becomes a TM in Core 1.0
- no created move becomes a general tutor in Core 1.0
- no broad created-move egg-pool expansion

Detailed values/IDs live in `moves/CREATED_MOVES.md`.

## Tutor policy

Tutors provide:

1. specialized coverage
2. role-specific utility
3. recognizable techniques that do not belong in ordinary progression

Tutors do not repair missing baseline STAB.

Examples preserved by design:

- Psyduck/Golduck can keep optional Zen Headbutt tutor access after natural special-Psychic progression is improved.
- Sceptile keeps optional physical Dragon routes while natural Dragon Pulse supports its special role.
- Banette keeps Shadow Ball via TM while its natural route becomes physical Ghost.

## Egg-move policy

Vanilla Platinum egg pools are preserved by default.

Do not rewrite hundreds of egg moves merely because a natural learnset changed.

A natural/egg duplicate can remain when breeding provides earlier access.

Do not place evolved-state identity moves such as Magnet Volley, Soul Grip, or Cursed Stitch broadly into base-form egg pools.

## Final C3 audit authority

C3 design categories are complete:

- level-up learnsets
- evolution timing
- natural STAB/dead slots
- TM/HM compatibility
- tutors
- egg moves

The final audit found one authoritative correction:

**Banette**

- Shadow Sneak 20
- Shadow Ball 31
- Sucker Punch 35
- evolves from Shuppet at 37
- Cursed Stitch 38
- Shadow Claw 42

Earlier instructions replacing Shadow Ball 31 with Cursed Stitch are `SUPERSEDED`.

## World/availability design

Target:

- original 210 remain the regional story identity
- National Dex access occurs early enough to support the overhaul
- all nonlegendary families accessible before the Elite Four
- external/daily-only acquisition gates become optional bonus methods rather than mandatory barriers

Special systems such as swarms, Radar, Honey Trees, Trophy Garden, Great Marsh, and Underground should retain distinct identities even when no longer required for completion.

## Legendary/Mythical design

Prefer native Platinum events and infrastructure:

- Darkrai — Newmoon Island
- Shaymin — Seabreak Path
- Arceus — Hall of Origin
- Rotom forms — Secret Key room
- Regis/Regigigas — remove external event dependency
- Manaphy — Sinnoh-side acquisition
- Phione — breeding
- Dialga/Palkia — existing postgame structure
- legendary birds — roaming framework

## Economy, capture, breeding

Emerald is the starting design authority for systems already solved there, but Platinum values/mechanics require an explicit port audit before being marked `LOCKED`.

See `EMERALD_PORT_PLAN.md`.
