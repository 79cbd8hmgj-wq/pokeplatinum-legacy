# Pokémon Platinum Overhaul — Poké Ball Rebalance

Status: **LOCKED SPEC**

## 1. Design target

Poké Balls should have distinct, intuitive jobs without one specialist ball invalidating the rest.

Platinum's existing Gen IV ball roster is the baseline. Emerald is precedent only where it improves identity.

Core rules:
- Poké / Great / Ultra remain the general-purpose progression line.
- Specialist balls should reward their intended situation.
- No specialist should dominate unrelated situations.
- Dusk Ball is toned down slightly because cave/night coverage is too broad.
- Quick Ball remains the strongest immediate-catch specialist.
- Timer Ball reaches full strength much sooner.
- Repeat Ball is improved for collection/completion.
- Heal Ball receives a modest capture buff while preserving its healing identity.
- Nest Ball becomes the level-difference specialist; no new Level Ball item slot is needed.
- Dive Ball becomes the strongest water-environment specialist.
- Luxury/Premier preserve their non-rate identities.
- Master Ball remains guaranteed.

## 2. Final catch modifiers

All values below are relative multipliers.

| Ball | Vanilla Platinum | Overhaul |
|---|---:|---:|
| Poké Ball | 1.0x | **1.0x** |
| Great Ball | 1.5x | **1.5x** |
| Ultra Ball | 2.0x | **2.0x** |
| Heal Ball | 1.0x | **1.5x** |
| Net Ball | 3.0x Water/Bug | **3.5x Water/Bug** |
| Nest Ball | level-based | **level-ratio model below** |
| Repeat Ball | 3.0x caught species | **3.5x caught species** |
| Timer Ball | 1.0x + 0.1/turn, max 4.0x at 30 turns | **1.0x + 0.3/turn, max 4.0x at 10 turns** |
| Dusk Ball | 3.5x night/cave | **3.0x night/cave** |
| Quick Ball | 4.0x turn 1 | **5.0x turn 1** |
| Dive Ball | 3.5x water terrain | **4.0x water terrain** |
| Luxury Ball | 1.0x | **1.0x** |
| Premier Ball | 1.0x | **1.0x** |
| Safari Ball | existing Safari mechanics | **unchanged** |
| Master Ball | guaranteed | **unchanged** |

## 3. Nest Ball level-ratio model

Nest Ball becomes the practical Gen IV equivalent of the project's earlier Level Ball concept while preserving Nest Ball's original "weaker Pokémon" identity.

Compare the player's active Pokémon level to the wild target:

- player level < target level: **1.0x**
- player level >= target level: **2.0x**
- player level >= 2 × target level: **3.5x**
- player level >= 4 × target level: **5.0x**

Use the active battler's level at throw time.

This makes Nest Ball excellent for backtracking and Pokédex cleanup without making it a generic boss-catching ball.

## 4. Quick / Timer relationship

Quick and Timer should reward opposite strategies:

### Quick Ball
- 5.0x only on the first turn.
- falls to 1.0x afterward.

### Timer Ball
- turn 0: 1.0x
- turn 1: 1.3x
- turn 2: 1.6x
- ...
- turn 10+: 4.0x cap.

This prevents drawn-out 30-turn waiting while preserving the intended long-battle identity.

## 5. Dusk Ball balance

Dusk Ball remains:
- cave;
- night;
- late night.

Multiplier becomes **3.0x**.

Reason:
- its trigger is extremely broad in Platinum;
- 3.5x made it compete too closely with more situational balls;
- at 3.0x it remains excellent without replacing Net/Dive/Repeat/Timer in their niches.

## 6. Heal Ball

Heal Ball becomes **1.5x** universally.

Its post-capture effect remains:
- restore HP;
- cure status.

Do not alter that utility behavior.

This makes Heal Ball a legitimate early-game alternative rather than a cosmetic 1.0x ball.

## 7. Net Ball

Net Ball becomes **3.5x** against Water- or Bug-type Pokémon.

It remains type-based rather than environment-based.

This creates a clean distinction:
- Net = target type;
- Dive = water environment.

## 8. Dive Ball

Dive Ball becomes **4.0x** when the battle terrain is water.

Do not require literal underwater maps.

If the battle engine exposes a reliable "fishing encounter" flag, Claude may add fishing as an additional valid trigger, but fishing-specific behavior is not required for Core 1.0.

## 9. Repeat Ball

Repeat Ball becomes **3.5x** when the species has already been caught.

This is specifically intended to support:
- breeding catches;
- nature/ability hunting;
- replacement team members;
- collection cleanup.

## 10. Prices

Keep existing Platinum item prices unless noted by a future economy audit.

Locked:
- Poké Ball 200
- Great Ball 600
- Ultra Ball 1200
- Heal Ball 300
- Net/Nest/Dusk/Quick/Timer/Repeat/Dive/Luxury 1000
- Premier Ball 200 internal price

Do not raise Quick Ball's price merely because its first-turn multiplier increases; its situational limitation is the balancing factor.

## 11. Availability

General progression:
- Poké Ball: opening game.
- Great Ball: available immediately after first badge.
- Ultra Ball: available by midgame, around 4 badges.
- Heal Ball: Jubilife/Oreburgh/Floaroma as currently thematic.
- Net Ball: Oreburgh/Floaroma onward.
- Nest Ball: Eterna onward.
- Dusk Ball: Solaceon onward.
- Quick Ball: Pastoria onward.
- Timer Ball: Celestic/Snowpoint onward.
- Repeat Ball: Canalave onward.
- Dive Ball: Pastoria or Canalave onward.
- Luxury Ball: Sunyshore onward.
- League shop: broad specialist selection.

Exact badge/vendor flags are implementation data, but no specialist should be postgame-only if its use case is relevant during the campaign.

## 12. Catching philosophy

The overhaul should make catching less tedious without trivializing rare species.

Do not:
- globally increase every species catch rate;
- globally increase the base catch formula;
- make all specialist balls 4–5x;
- weaken status bonuses;
- change Master Ball behavior.

The specialist-ball system is the primary capture QoL mechanism.

## 13. Compatibility with availability overhaul

Encounter availability and capture balance are linked.

Rare-but-required families should not rely on:
- <5% appearance rates;
- extreme catch-rate frustration;
- one-time missable captures.

Ball strength should help collection, not compensate for bad encounter design.

## 14. Validation targets

Implementation must verify exact modifier behavior for:
- Water/Bug Net Ball cases;
- Nest Ball at each threshold;
- Repeat Ball caught/uncaught;
- Timer turns 0, 1, 5, 10, 20;
- Dusk day/night/cave;
- Quick turn 1 vs later;
- Dive water vs non-water;
- Heal 1.5x plus post-capture healing;
- standard balls unchanged;
- Master guaranteed;
- Safari unchanged.

This is canonical D3 authority.
