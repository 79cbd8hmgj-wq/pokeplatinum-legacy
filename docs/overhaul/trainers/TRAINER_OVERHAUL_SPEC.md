# Pokémon Platinum Overhaul — Trainer Overhaul Spec

Status: **LOCKED SPEC**

## 1. Design target

The trainer overhaul is a moderate campaign difficulty upgrade, not a hardcore/Kaizo ruleset.

Core rules:

- no grinding expectation for a player who explores normally;
- difficulty comes first from better team composition, evolved-form timing, useful moves, and roster depth rather than blanket level inflation;
- Generations I–IV are all valid trainer pools;
- important trainers use coherent roles and held items selectively;
- ordinary trainers showcase the expanded world without becoming boss fights;
- all teams must respect the overhaul's locked species identities, stats, abilities, moves, evolutions, and compatibility;
- a Pokémon's effective strength at the battle's level matters more than raw species count.

## 2. Difficulty and level curve

Keep Platinum's broad level curve. Do not apply a global +5/+10 rule.

**Scaling authority:** all trainer-level tuning must begin from Platinum's actual vanilla level curve and expected campaign progression, then be re-evaluated against the overhaul's final team-wide EXP-sharing behavior. Do not import Emerald trainer levels or assume vanilla single-recipient EXP pacing. The target is that a normally exploring player using a rotating team remains competitive without deliberate grinding.

Main-story ace targets:

| Battle | Ace level |
|---|---:|
| Roark | 14 |
| Gardenia | 22 |
| Fantina | 27 |
| Maylene | 32 |
| Wake | 37 |
| Byron | 41 |
| Candice | 44 |
| Volkner | 50 |
| Rival before League | 51 |
| Aaron | 53 |
| Bertha | 55 |
| Flint | 57 |
| Lucian | 59 |
| Cynthia | 62 |

Ordinary trainers normally remain close to the vanilla Platinum area's level band. Adjust only obvious dips/spikes after the encounter/EXP curve is implemented.

Final trainer levels are therefore **provisional until the EXP-sharing/economy phase is locked and simulated**. Team composition, party-size rules, and relative boss ordering are locked; exact levels may receive small evidence-based adjustments if team-wide EXP materially changes the player's expected level at that point.

### Strength-budget rule

When adding party members, consider:

- BST and the overhaul's stat redistribution;
- evolution stage actually appropriate at that level;
- ability strength;
- STAB quality available by that level;
- coverage/status quality;
- held item;
- AI tier.

Do not compensate for a stronger species by blindly raising levels.

## 3. Party-size progression

- Gyms 1–3: 3 Pokémon.
- Gyms 4–6: 4 Pokémon.
- Gym 7: 4 Pokémon.
- Gym 8: 5 Pokémon.
- Early Commanders: 2 Pokémon.
- Midgame Commanders: 3 Pokémon.
- Late Galactic bosses: 4–5 Pokémon.
- Rival grows naturally from 2 → 4 → 5 → 6.
- Elite Four: 5.
- Cynthia: 6.
- Optional postgame Gym rematches: 5.
- Major postgame Rival/Champion battles: 6.

## 4. Theme rules

### Gyms

Use **mostly monotype**.

A Gym may use at most one thematic off-type Pokémon when it materially improves the battle identity. Do not add an off-type merely for coverage.

### Elite Four

Preserve:
- Aaron = Bug
- Bertha = Ground
- Flint = Fire
- Lucian = Psychic
- Cynthia = diverse Champion

Use the expanded Gen I–IV roster where it improves the theme.

### Team Galactic

- Grunts: common invasive/urban/night species, status, poison, dark, flying, normal.
- Commanders: signature species remain recognizable and scale with the story.
- Cyrus: fast, aggressive, emotionally cold team built around Dark/Flying/intimidating predators rather than a formal monotype.

### Rival

Preserve the existing Platinum identity:
- Staraptor core;
- starter-counter structure;
- Heracross;
- Snorlax late;
- complementary Roserade / Rapidash / Floatzel slots according to starter branch.

The Rival is improved mainly through move quality, evolution timing, and late held items rather than replacing the recognizable team.

## 5. AI and trainer items

Existing boss AI flags are already sufficient as the baseline:

- ordinary early trainers: basic/default AI;
- stronger route specialists/Ace Trainers/Veterans: attack-evaluation/expert where already supported;
- Rival, Commanders, Gym Leaders, Elite Four, Cynthia: BASIC + EVAL_ATTACK + EXPERT;
- use specialized existing AI flags only where the team actually benefits (for example screen/setup behavior).

Do not add new AI engine mechanics for Core 1.0 unless runtime testing proves a concrete deficiency.

Trainer bag healing remains restrained:
- early Gym Leaders: up to 2 era-appropriate heals;
- mid/late leaders: up to 2 stronger heals;
- Elite Four: 2 Full Restores;
- Cynthia: preserve 4 Full Restores unless playtesting proves excessive.

Held items:
- Gym 1: none;
- Gym 2 onward: ace may hold a berry;
- Gym 6 onward: at most one additional team member may hold a modest item if useful;
- no Choice items, Life Orb, Focus Sash, or Leftovers spam in the main story;
- postgame rematches may use stronger held items.

## 6. Main-story Gym teams

### Roark — Rock

Levels: 12 / 13 / 14

- Geodude 12 — Stealth Rock / Rock Throw / Tackle
- Onix 13 — Stealth Rock / Rock Throw / Screech / Bind
- Cranidos 14 — Headbutt / Pursuit / Focus Energy / Leer

Rationale: Cranidos already has 125 Attack. Three Pokémon are sufficient; no artificial fourth slot or level inflation.

### Gardenia — Grass

Levels: 20 / 20 / 22

- Turtwig 20 — Grass Knot / Razor Leaf / Reflect / Sunny Day
- Cherrim 20 — Magical Leaf / Leech Seed / Sunny Day / Growth
- Roserade 22 @ Sitrus Berry — Grass Knot / Magical Leaf / Poison Sting / Stun Spore

Rationale: redesigned Cherrim plus 515-BST Roserade already makes this substantially stronger than a normal second Gym.

### Fantina — Ghost

Levels: 24 / 25 / 27

- Duskull 24 — Will-O-Wisp / Shadow Sneak / Pursuit / Future Sight
- Haunter 25 — Ominous Wind / Hypnosis / Sucker Punch / Confuse Ray
- Mismagius 27 @ Sitrus Berry — Shadow Ball / Psybeam / Magical Leaf / Confuse Ray

Rationale: Mismagius is already a strong fully evolved ace at this stage. Keep the party at three.

### Maylene — Fighting

Levels: 28 / 29 / 30 / 32

- Meditite 28 — Drain Punch / Confusion / Rock Tomb / Fake Out
- Machoke 29 — Brick Break / Rock Tomb / Strength / Focus Energy
- Hitmonchan 30 — Mach Punch / Bullet Punch / Drain Punch / Ice Punch
- Lucario 32 @ Sitrus Berry — Drain Punch / Force Palm / Metal Claw / Bone Rush

Rationale: the fourth slot adds depth without needing higher levels. Hitmonchan is strong but not overpowered at 30.

### Crasher Wake — Water

Levels: 33 / 34 / 35 / 37

- Gyarados 33 — Waterfall / Bite / Twister / Leer
- Quagsire 34 — Mud Shot / Rock Tomb / Water Pulse / Yawn
- Kingler 35 — Crabhammer / Stomp / Metal Claw / Protect
- Floatzel 37 @ Sitrus Berry — Aqua Jet / Crunch / Ice Fang / Brine

Rationale: three of these are strong physical attackers, so levels remain essentially vanilla.

### Byron — Steel

Levels: 37 / 38 / 39 / 41

- Magneton 37 — Flash Cannon / Thunderbolt / Tri Attack / Metal Sound
- Steelix 38 — Earthquake / Rock Slide / Ice Fang / Sandstorm
- Scizor 39 — X-Scissor / Iron Head / Night Slash / Quick Attack
- Bastiodon 41 @ Sitrus Berry — Metal Burst / Rock Tomb / Iron Defense / Roar

Rationale: add Scizor rather than inflating levels. Bastiodon's extreme defenses remain the ace challenge.

### Candice — Ice

Levels: 40 / 40 / 42 / 44

- Weavile 40 — Ice Punch / Night Slash / Fake Out / Aerial Ace
- Piloswine 40 — Avalanche / Earthquake / Stone Edge / Hail
- Abomasnow 42 — Avalanche / Wood Hammer / Water Pulse / Focus Blast
- Froslass 44 @ Sitrus Berry — Blizzard / Shadow Ball / Double Team / Psychic

Rationale: Sneasel is no longer appropriate at Lv40 under the locked Lv38 Weavile evolution. Piloswine is intentionally retained as the slower bulky member rather than turning the whole team into 500+ BST final evolutions.

### Volkner — Electric

Levels: 46 / 46 / 47 / 48 / 50

- Lanturn 46 — Surf / Discharge / Thunder Wave / Signal Beam
- Jolteon 46 — Thunderbolt / Shadow Ball / Quick Attack / Thunder Wave
- Raichu 47 — Thunderbolt / Metal Ray / Focus Blast / Signal Beam
- Luxray 48 — Thunder Fang / Crunch / Ice Fang / Fire Fang
- Electivire 50 @ Sitrus Berry — Static Strike / Cross Chop / Ice Punch / Fire Punch

Rationale: final Gym gains a fifth Pokémon instead of excessive level inflation. The team's dual typings and physical/special split showcase the overhaul.

## 7. Rival progression

Retain the existing three starter branches and recognizable species progression.

Rules:
- Route 203 remains a 2-Pokémon introductory fight around Lv7–9.
- Route 209 reaches 4 Pokémon around Lv23–27.
- Pastoria remains 4 around Lv32–36.
- Canalave becomes the first 5-Pokémon fight around Lv35–38.
- Pokémon League is 6, levels 47–51.
- postgame Fight/Survival Area versions scale upward without replacing the core team.

League-final branch cores:

### Rival owns Empoleon
Staraptor 48 / Roserade 47 / Heracross 48 / Rapidash 47 / Snorlax 49 / Empoleon 51.

### Rival owns Torterra
Staraptor 48 / Floatzel 47 / Heracross 48 / Rapidash 47 / Snorlax 49 / Torterra 51.

### Rival owns Infernape
Staraptor 48 / Floatzel 47 / Heracross 48 / Roserade 47 / Snorlax 49 / Infernape 51.

Moves must be rebuilt from current locked learnsets and compatibility so the late Rival no longer carries obviously obsolete attacks such as weak starter-stage filler.

From Canalave onward, the starter may hold a Sitrus Berry. At the League, Snorlax may also hold a Chesto Berry for Rest synergy.

## 8. Team Galactic

### Mars — Valley Windworks
Keep Zubat 15 / Purugly 17. Purugly's redesign is only a moderate increase and remains her signature early difficulty spike.

### Jupiter — Eterna
Keep Zubat 21 / Skuntank 23. Skuntank's revised ability identity supplies the upgrade.

### Saturn — Valor
Keep Golbat 38 / Bronzor 38 / Toxicroak 40, but update Toxicroak to use Aura Burst at the appropriate late-game appearances where legal.

### Cyrus — Galactic HQ
- Weavile 44
- Crobat 44
- Houndoom 45
- Honchkrow 46 @ Sitrus Berry

Sneasel must evolve because the overhaul's Weavile evolution is Lv38 at night and Cyrus is an important late-game boss.

### Cyrus — Distortion World
Keep the five-species identity:
- Houndoom 45
- Crobat 46
- Gyarados 46
- Honchkrow 47
- Weavile 48 @ Sitrus Berry

Update moves to the current locked move data; no extra sixth Pokémon is needed before the eighth Gym.

Commanders' later Lake/Spear Pillar/Stark teams should evolve signatures naturally and gain at most one additional thematic species, with no global level inflation.

## 9. Elite Four and Cynthia

Main-story species compositions are already strong under the overhaul and should largely remain recognizable.

### Aaron
Yanmega 49 / Scizor 49 / Vespiquen 50 / Heracross 51 / Drapion 53.

Drapion is the allowed thematic off-type arthropod.

### Bertha
Whiscash 50 / Hippowdon 52 / Golem 52 / Gliscor 53 / Rhyperior 55.

### Flint
Houndoom 52 / Rapidash 53 / Flareon 55 / Infernape 55 / Magmortar 57.

### Lucian
Mr. Mime 53 / Bronzong 54 / Espeon 55 / Alakazam 56 / Gallade 59.

### Cynthia
Spiritomb 58 / Roserade 58 / Togekiss 60 / Lucario 60 / Milotic 58 / Garchomp 62.

Cynthia's species roster is iconic and already excellent. Improve it through the overhaul's actual move identities rather than replacing members.

Examples:
- Spiritomb may use Soul Siphon.
- Milotic uses its locked Water/Dragon identity and Dragon Pulse.
- Garchomp should use a clean physical Dragon/Ground set rather than Giga Impact filler.

## 10. Ordinary trainer archetypes

Do not hand-design every trainer independently.

### Beginners
Youngsters/Lasses/School Kids:
- 1–3 Pokémon;
- simple local/base-stage species;
- natural moves;
- no held items;
- basic AI.

### Habitat specialists
Hikers, Fishermen, Bird Keepers, Bug Catchers, etc.:
- use families fitting their class and current zone;
- 2–4 Pokémon;
- middle stages become common midgame;
- avoid repeated identical species unless class identity calls for it.

### Skilled route trainers
Ace Trainers / Veterans / Dragon Tamers:
- 3–5 Pokémon;
- coherent coverage;
- evolved forms appropriate to level;
- occasional held berry;
- expert AI;
- may showcase rarer families.

### Breeders
- broader cross-generation family variety;
- lower raw levels/strength than Aces;
- useful for showcasing obtainable families.

### Galactic grunts
- 2–4 Pokémon;
- poison/dark/flying/normal/urban scavenger pools;
- progressively evolve Zubat/Stunky/Croagunk-style lines;
- avoid endless duplicate Golbat teams.

### Double battles
- build actual pair synergy where existing doubles occur;
- weather, spread moves, helping/support, or complementary typings;
- do not convert the campaign broadly into doubles.

## 11. Availability fairness

Ordinary trainers should normally use species available in the same or an earlier availability band.

Important bosses may showcase at most one family up to one progression band before normal player access when strongly thematic.

No trainer team should depend on an evolution method that contradicts the locked evolution spec.

## 12. Postgame rematches

Optional rematches can be substantially stronger and use the National roster.

Target boss levels: roughly 62–70, tuned later against postgame EXP/economy.

Recommended five-Pokémon Gym rematches:

- Roark: Aerodactyl / Kabutops / Omastar / Rhyperior / Rampardos
- Gardenia: Jumpluff / Ludicolo / Breloom / Cherrim / Roserade
- Maylene: Hitmontop / Medicham / Heracross / Toxicroak / Lucario
- Wake: Kingdra / Gyarados / Quagsire / Feraligatr / Floatzel
- Fantina: Gengar / Banette / Spiritomb / Dusknoir / Mismagius
- Byron: Magnezone / Steelix / Scizor / Probopass / Bastiodon
- Candice: Weavile / Mamoswine / Glalie / Abomasnow / Froslass
- Volkner: Lanturn / Jolteon / Raichu / Luxray / Electivire

Elite Four rematches remain five Pokémon:
- Aaron: Yanmega / Scizor / Heracross / Pinsir / Vespiquen
- Bertha: Whiscash / Hippowdon / Golem / Gliscor / Rhyperior
- Flint: Houndoom / Arcanine / Rapidash / Infernape / Magmortar
- Lucian: Slowking / Bronzong / Espeon / Alakazam / Gallade

Cynthia rematch retains her six iconic members with stronger items/moves and a higher level band.

## 13. Validation requirements

Implementation must prove:

- all species IDs/forms are valid;
- levels are within intended battle bands;
- moves exist and are valid under current overhaul data;
- no superseded evolution assumptions;
- important trainers use the expected AI tier;
- party sizes meet the rules;
- no duplicate species on important teams unless explicitly allowed;
- ordinary trainer species are availability-compatible;
- boss power curve has no unexplained large level/BST spike;
- Rev 0 and Rev 1 builds succeed;
- representative boss battles receive runtime smoke tests.

This spec is approved authority for trainer implementation.
