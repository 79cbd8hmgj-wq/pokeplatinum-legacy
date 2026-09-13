# Emerald → Platinum Port Plan

## Goal

The Platinum overhaul is a successor to the Emerald overhaul. Existing Emerald solutions should be reused wherever they still fit instead of being redesigned from zero.

The porting rule is behavioral/design reuse first, source-code reuse only when architectures actually match.

## Classification

Every Emerald feature must be assigned one of four labels before implementation.

### DIRECT PORT

The design and behavior transfer with little or no conceptual change. Implementation is rewritten against Platinum's source/resources as needed.

### ADAPT

The Emerald design is retained, but Sinnoh/Generation IV requires different data placement, mechanics, availability, or balance.

### PLATINUM-SPECIFIC

Do not force an Emerald implementation where Platinum already has better native infrastructure.

### DEFER

Useful later, but outside Core 1.0.

## Initial port matrix

| Emerald subsystem | Platinum class | Platinum direction |
|---|---|---|
| Single-save complete Pokédex | ADAPT | Extend 386 philosophy to #001–#493 and Sinnoh's encounter systems |
| No mandatory trade evolutions | DIRECT PORT / ADAPT | Same principle; extend to Gen IV held-item trade evolutions |
| Evolved-form encounter restraint | DIRECT PORT | Keep base-stage-first ecology rule |
| EXP rebalance | ADAPT | Use Emerald values as test baseline, tune against Platinum level curve |
| Mart/economy rebalance | ADAPT | Carry anti-grind philosophy; tune around Platinum prices/rewards |
| Wild battle money reward | ADAPT | Candidate; verify Platinum economy and engine path before locking |
| Poké Ball identity rebalance | ADAPT | Platinum already has more specialist balls, reducing slot-replacement work |
| Early specialist-ball access | DIRECT PORT / ADAPT | Preserve progression philosophy using Sinnoh shops/gifts |
| Breeding inheritance upgrades | ADAPT | Audit against Gen IV breeding before copying Emerald rules |
| Egg-group/egg-move cleanup | ADAPT | Use Platinum's richer breeding ecosystem; avoid making breeding mandatory for basic STAB |
| Curated hatch rewards | DEFER / ADAPT | Potential later feature; do not block Core 1.0 |
| Trade/version/external-game availability removal | ADAPT | Replace Diamond/Pearl/GBA/WFC/second-DS gates with Sinnoh-native acquisition |
| Legendary/Mythical accessibility | PLATINUM-SPECIFIC | Restore/use Platinum event infrastructure |
| Trainer difficulty philosophy | DIRECT PORT / ADAPT | Coherent teams, not a pure difficulty hack; rebuild actual Sinnoh teams |
| Grinding reduction | DIRECT PORT | Preserve design goal across EXP, money, items, breeding, Frontier |
| Battle facility economy | ADAPT | Translate to Platinum Battle Frontier BP/reward structure |
| Completion QA | DIRECT PORT | Extend checklist to 493 and Platinum events/forms |

## 1. Evolution system

### Target

No Pokémon required for completion should need trading, a second system, or an external game.

### Platinum adaptation

Level-based trade evolutions may remain level-based where that is the cleanest solution.

Trade-with-item evolutions should generally become direct item evolutions because Platinum already contains the relevant items.

Design examples already present in the Platinum plan include:

- Kadabra → Alakazam: level
- Machoke → Machamp: level
- Graveler → Golem: level
- Haunter → Gengar: level
- Onix → Steelix: Metal Coat
- Scyther → Scizor: Metal Coat
- Seadra → Kingdra: Dragon Scale
- Rhydon → Rhyperior: Protector
- Electabuzz → Electivire: Electrizer
- Magmar → Magmortar: Magmarizer
- Dusclops → Dusknoir: Reaper Cloth
- Porygon → Porygon2: Up-Grade
- Porygon2 → Porygon-Z: Dubious Disc
- Poliwhirl/Slowpoke branches: King's Rock
- Clamperl branches: Deep Sea Tooth / Deep Sea Scale

Location and friendship evolutions should generally remain because they fit Sinnoh, with tedious thresholds reviewed separately.

### Implementation task

Claude should compare the finalized Emerald evolution implementation with Platinum's evolution method tables/logic and produce a source-backed Platinum evolution manifest rather than blindly copying C code.

## 2. EXP and progression economy

The finalized Emerald economy plan used this first-pass package:

- wild EXP: ×1.6
- trainer EXP: ×1.3
- mart prices: ×0.6
- wild battles award money
- wild money: about 25% of trainer-equivalent scaling

### Platinum ruling

These values are **PORT TEST BASELINES**, not yet locked Platinum values.

Reason:

Platinum has a different level curve, trainer density, money economy, Exp. Share context, rematch structure, and Battle Frontier.

### Port test sequence

1. reproduce the Emerald behavior in a controlled Platinum branch
2. playtest through early/mid Sinnoh
3. compare levels at each Gym against intended trainer curve
4. compare available money against ball/healing/evolution-item needs
5. tune multipliers before locking

### Success criteria

- normal team rotation is viable
- catching/experimentation is affordable
- trainers still feel more valuable than wild battles
- progression does not become trivial
- basic supplies do not require grinding

## 3. Poké Ball system

Platinum already has most specialist-ball concepts natively, so this should be easier than Emerald.

### Emerald identities worth carrying forward

- Quick Ball — strong first-turn specialist
- Timer Ball — reaches useful/full power sooner
- Repeat Ball — collection/farming specialist
- Heal Ball — useful capture + healing identity
- Lure Ball/fishing specialist concept
- Level Ball/level-advantage concept if an appropriate Platinum implementation path is chosen
- Great Ball earlier
- Ultra Ball remains the dependable late default

### Known Emerald target values available as port references

- Repeat Ball: 3.5× if species already caught
- Level Ball preferred scale: 2.0× / 3.5× / 5.0× based on level advantage tiers
- fishing-specialist Lure behavior: 4.0× on fishing encounters
- Heal Ball: 1.5× plus full heal on capture

These are reference values from Emerald, not automatically locked Platinum values.

### Platinum-specific caution

Do not replace native Gen IV balls unnecessarily. Audit the existing Platinum ball roster/effects first, then only modify underused/overlapping behavior where it improves the decision tree.

## 4. Breeding

### Emerald inheritance candidates

The Emerald implementation plan included aggressive breeding improvements such as:

- 100% Everstone nature inheritance
- 4 inherited IVs
- no duplicate inherited-IV stat rolls
- predictable maternal ability-slot inheritance
- Ditto pairings using the non-Ditto parent for the applicable inheritance rule
- expanded role-driven egg moves
- selective curated hatch rewards

### Platinum ruling

These are **candidates requiring Gen IV audit**, not automatic locks.

Platinum already has a richer breeding ecosystem than Emerald, and the completed C3 design establishes a stricter rule:

> Egg moves are optional inherited techniques; they must not repair basic campaign functionality.

### Core 1.0 priority

1. reduced breeding friction
2. sensible inheritance improvements
3. earlier/practical Day Care use
4. egg-group consistency where needed
5. clear egg-move availability

### Deferred unless proven low-risk

- custom hatch-reward systems
- cross-type offspring/variant experiments
- other high-complexity breeding branches

## 5. Full Pokédex availability

### Direct philosophy port

Emerald's complete-save philosophy becomes 493-in-one-save.

### Platinum adaptation targets

Remove mandatory dependency on:

- Diamond/Pearl exclusivity
- GBA dual-slot encounters
- second DS/trading
- WFC event distributions
- mandatory daily rotation
- Poké Radar-only acquisition
- Trophy Garden-only acquisition
- Great Marsh-only rotation
- Honey Tree extreme rarity as the sole path
- event-Regigigas requirement for Regis
- Spiritomb multiplayer requirement

### Important rule

Special systems should remain useful bonus/farming methods even when no longer mandatory.

Example:

A Radar-exclusive species can gain a rare normal encounter while Radar remains the efficient hunting method.

## 6. Encounters

This is `ADAPT`, not a literal port.

Sinnoh maps/ecology differ completely from Hoenn.

### Encounter-zone design

- Early: Sinnoh species dominant; older species repair type scarcity.
- Midgame: broader National Dex expansion; Marsh/Underground/Honey/fishing/caves remain distinct.
- Late story: rare families and pseudo-legendaries accessible; all nonlegendary families obtainable by the pre-E4 target.
- Postgame: legendaries, optimization, collection cleanup, rematches.

### Wild evolution rule

- lowest practical stage is the default wild encounter
- middle stages only where ecologically/progression appropriate
- final evolutions usually earned
- babies/awkward families can use justified exceptions

## 7. Legendary and Mythical content

This is primarily `PLATINUM-SPECIFIC`.

Use/restore native Platinum infrastructure instead of porting Emerald event scripts.

Priority targets:

- Darkrai — Member Card/Newmoon Island
- Shaymin — Oak's Letter/Seabreak Path
- Arceus — Azure Flute/Hall of Origin
- Rotom forms — Secret Key room
- Regis — remove external event dependency
- Regigigas — require the three Regis, not an event distribution
- Manaphy — Sinnoh-side quest/restored gift
- Phione — breeding
- Dialga/Palkia — existing postgame structure
- legendary birds — existing roamers, optionally improved

## 8. Trainers

Port the Emerald philosophy, not teams.

### Keep

- important trainers use coherent teams
- levels assume exploration, not grinding
- bosses gain coverage and identity without perfect competitive sets
- ordinary trainers showcase the expanded ecosystem

### Rebuild for Platinum

- Gym Leaders
- Rival
- Galactic commanders/bosses
- Elite Four
- Cynthia
- rematches

## 9. Frontier/postgame

Emerald's anti-grind philosophy carries forward, but Platinum's Frontier is structurally different.

Already locked in C2:

Battle Frontier TM costs use a roughly half-cost conversion:

- 32 BP → 16 BP
- 40 BP → 20 BP
- 48 BP → 24 BP
- 64 BP → 32 BP
- 80 BP → 40 BP

Future Frontier work should preserve meaningful progression while avoiding excessive experimentation cost.

## Port-audit deliverable format

For each subsystem Claude audits, create a table with:

- Emerald design authority file
- Emerald implementation file/function/data path
- Platinum equivalent file/function/data path
- classification
- exact behavior to preserve
- Platinum-specific deviations
- risk level
- build/runtime test plan
- dependency order

Then update `STATUS.md` and this file when the classification becomes implementation-verified.
