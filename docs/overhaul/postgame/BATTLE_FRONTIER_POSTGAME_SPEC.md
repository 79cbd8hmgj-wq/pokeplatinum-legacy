# Pokémon Platinum Overhaul — Battle Frontier, Rematches, and Postgame Rewards

Status: **LOCKED SPEC**

## 1. Design target

The postgame should feel substantially more rewarding without bypassing Platinum's Battle Frontier identity.

Core rules:
- preserve all five Frontier facilities and their distinct mechanics;
- preserve silver/gold boss streak milestones;
- reduce BP grind rather than shortening the actual challenge structure;
- rematches should be readily playable without real-world-week waiting;
- use the already-locked trainer rematch teams as authority;
- postgame conveniences should support experimentation, breeding, move testing, legendary hunting, and Frontier team-building;
- no species completion requirement may depend on Frontier streaks.

## 2. Frontier challenge structure

Preserve Platinum's native milestone structure.

### Battle Tower / Factory / Castle / Arcade
- rounds remain 7 battles;
- Silver boss battle remains at streak 21;
- Gold boss battle remains at streak 49.

### Battle Hall
- rounds remain 10 battles;
- Silver Argenta remains battle 50;
- Gold Argenta remains battle 170.

Do not reduce these thresholds in Core 1.0.

The challenge itself remains prestigious; the reward rate is what improves.

## 3. BP earnings

Apply a universal **2x multiplier** to Battle Point awards from all five Frontier facilities.

Examples:
- 1 BP → 2 BP;
- 3 BP → 6 BP;
- set/Frontier Brain awards double likewise.

Rules:
- multiply the final earned BP award, not internal facility score/rank values;
- do not alter Castle Points or other facility-specific internal currencies/mechanics unless they are converted to BP at payout;
- preserve existing records/streak logic;
- no BP is awarded for ordinary Battleground/Gym/Rival rematches.

This halves Frontier currency grind without trivializing streak achievements.

## 4. Frontier shop economy

### TMs

The previously locked TM BP prices remain authority:

- 32 → 16 BP
- 40 → 20 BP
- 48 → 24 BP
- 64 → 32 BP
- 80 → 40 BP

Specific locked TM prices remain exactly as defined in the TM/HM spec.

Because TMs are reusable, each Frontier TM is effectively a one-time unlock.

### Non-TM rewards

Keep vanilla BP prices for:
- competitive held items;
- berries;
- medicines/stat items;
- other non-TM Frontier merchandise,

unless a later live-source audit finds a clear duplicate of an item already made trivially purchasable elsewhere.

Do not globally halve both BP income requirements and every Frontier item price. The 2x payout already cuts ordinary item grind in half.

### Power items

Power items may remain sold for BP, but D4 also makes them available for money midgame.

The Frontier listing becomes an optional alternate source, not a breeding gate.

## 5. Frontier Pokémon-set audit

Do not rebuild every Frontier Pokémon from scratch.

Audit existing Frontier sets against the overhaul for:
- retyped Pokémon;
- significantly redistributed stats;
- changed abilities;
- C1 move behavior changes;
- C2/C2.5 created/changed moves;
- C3 learnset identity;
- obsolete or contradictory STAB choices.

Change only sets that are meaningfully broken, misleading, or no longer represent the Pokémon's locked identity.

Examples:
- Electric/Steel Raichu should have at least some sets capable of using its Steel identity;
- Water/Ground Blastoise sets should not all behave as vanilla pure Water;
- Electric/Dark Luxray should have Dark representation where appropriate;
- Electric/Fighting Electivire should have Fighting representation;
- Ice/Steel Glalie should have appropriate Steel/Ice sets;
- Water/Dragon Milotic should retain its special/tank identity rather than being overstuffed with physical Dragon coverage.

Do not force every retyped Pokémon to use both STAB types on every set.

Frontier legality is based on canonical overhaul data, not vanilla move assumptions.

## 6. Frontier Brains

Preserve:
- Tower Tycoon Palmer;
- Factory Head Thorton;
- Arcade Star Dahlia;
- Castle Valet Darach/Caitlin presentation;
- Hall Matron Argenta.

Keep their Silver/Gold encounter positions.

Their teams/sets may receive targeted overhaul-alignment edits, but not tournament-level redesigns beyond Platinum's intended Frontier difficulty.

The Frontier remains harder than the story campaign.

## 7. Battleground rematches

Use the existing Battleground infrastructure and the locked trainer-rematch teams.

Remove the **real-world daily waiting bottleneck** as the only way to access different rematches.

New behavior:
- Battleground still displays up to four trainers at a time;
- after the player defeats/declines the current set, the proprietor can reshuffle another set immediately;
- player may continue reshuffling and battling without waiting for the next calendar day;
- defeated state resets on reshuffle rather than relying solely on daily reset flags;
- random selection should avoid obvious immediate duplicates where practical.

Eligible pool:
- all eight Gym Leaders after their postgame unlock;
- Cheryl;
- Mira;
- Riley;
- Marley;
- Buck once their native prerequisites are satisfied.

Do not require real-world date manipulation to see a specific rematch.

## 8. Gym Leader rematches

The exact rematch teams in:
`docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md`
remain authority.

D6 controls access/repeatability, not team redesign.

Rules:
- all eight Gym Leaders become eligible after Battleground opens;
- levels remain within the locked postgame target band, later calibrated against D2 EXP simulation;
- rematches can be repeated through Battleground reshuffles;
- normal prize money/EXP applies.

## 9. Rival rematches

After Stark Mountain/Battleground progression:

- Rival becomes rematchable **once per in-game day**, regardless of day of week;
- remove Saturday/Sunday-only gating where present;
- preserve starter-dependent branches;
- use the locked postgame Rival teams;
- once defeated, the daily flag prevents immediate repeat farming until the next daily reset.

This preserves Rival as a recurring postgame benchmark without a weekly calendar wait.

## 10. Elite Four / Cynthia rematches

Preserve repeatable Pokémon League runs.

Use the locked rematch teams from the trainer spec.

Rules:
- rematch roster activates after the appropriate postgame/National Dex state;
- every full League clear remains repeatable;
- no real-time gating;
- normal prize/EXP applies;
- Frontier BP is not awarded for League clears.

## 11. Fight Area opening battle

Preserve the Rival + player versus Volkner + Flint tag battle.

Update all four teams to canonical trainer-overhaul data where required.

Do not turn it into a Frontier-level competitive battle; it is the narrative postgame introduction.

## 12. Postgame convenience hub

Fight Area / Battle Zone should function as the main endgame preparation hub.

Integrate already-locked convenience systems:
- D2 postgame Rare Candy source;
- breeding Power-item alternatives;
- Frontier BP shops;
- access to rematches;
- Battle Frontier;
- Super Rod/native postgame travel.

Do not duplicate every Sinnoh shop into one giant mart.

The hub should consolidate **postgame training conveniences**, not erase regional shop identity.

## 13. Frontier print bonuses

Preserve Silver/Gold Prints as the main achievement markers.

Add one-time BP bonuses:

### Per facility
- first Silver Print: **+10 BP**
- first Gold Print: **+30 BP**

These bonuses are in addition to the doubled battle payout and occur only once per print.

### All-facility milestones
After obtaining all five Silver Prints:
- one-time **+50 BP**
- one **PP Max**

After obtaining all five Gold Prints:
- one-time **+100 BP**
- one **Master Ball**

The Master Ball is a late optional completion reward and does not gate any legendary.

Reward flags must prevent duplicate claims.

## 14. Battle Hall / Factory special identity

Do not homogenize facilities.

### Factory
Rental mechanics remain the point.
- Update rental Pokémon sets only where canonical overhaul changes make vanilla sets invalid/contradictory.
- Do not let player-owned breeding/IV advantages bypass the rental format.

### Hall
Type-by-type progression and single-Pokémon challenge remain unchanged.
- Retyped Pokémon must be classified according to their actual overhaul types wherever facility type logic reads live species data.
- If Hall opponent pools are static by type, audit them for retype drift.

### Castle
Castle Points and internal healing/rental/rank economy remain intact.
- Only final BP payout receives 2x.

### Arcade
Roulette effects remain intact.
- BP roulette outcomes are doubled at actual BP award: 1→2 and 3→6.
- Do not alter non-BP roulette effects merely for difficulty.

### Tower
Preserve standard competitive rules and Palmer milestones.

## 15. Postgame encounter convenience boundary

D6 may add convenience access to postgame areas but does not redesign D5 legendary events or D0 availability.

No nonlegendary family may require a Frontier Print/BP purchase.

Postgame encounter tables may include evolved convenience encounters only according to the availability spec.

## 16. Completion rewards outside Frontier

Do not add a separate 493-Pokédex prize in D6.

Full Pokédex/completion rewards belong to D7 final integration once all acquisition systems are verifiably complete.

## 17. Validation targets

D6 must prove:
- all five facilities retain native milestone lengths;
- all BP awards are exactly doubled once;
- Castle internal currency is not accidentally doubled;
- locked TM BP prices remain exact;
- non-TM prices remain unchanged unless explicitly manifested;
- Silver/Gold Print bonuses are one-time;
- all-Gold Master Ball cannot be reclaimed;
- Battleground can cycle through all eligible trainers without calendar waiting;
- Rival is daily rather than weekend-only;
- trainer rematch teams match trainer authority;
- Frontier Pokémon sets remain legal under overhaul species/move data;
- no Frontier reward gates Pokédex completion.

This spec is the canonical D6 authority.
