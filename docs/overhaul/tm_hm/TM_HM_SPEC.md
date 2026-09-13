# TM/HM System — C2 Canonical Spec

Status: `LOCKED DESIGN / IMPLEMENTING`

## 1. Reusable TM behavior

- TMs are reusable.
- First acquisition remains the progression gate.
- Reusability must not imply automatic global unlocks.
- Existing field/story/NPC/Gym progression is preserved by default.
- Optional duplicate field copies may remain until the later item-placement pass.
- Repeatable vendors should preferably block purchase if the player already owns the TM; this is a UX preference, not a Core 1.0 blocker if disproportionately expensive to implement.

## 2. Final TM roster

Platinum keeps all 92 TM slots.

Changes:

- **TM21: Frustration → Air Slash**
- **TM78: Captivate → Power Gem**

All other TM01–TM92 assignments remain vanilla.

Frustration and Captivate remain valid moves; they simply cease to be TMs.

### TM21 Air Slash

- Flying / Special
- 75 BP
- 95 Acc
- 20 PP
- 30% flinch

### TM78 Power Gem

C1 final:

- Rock / Special
- 80 BP
- 100 Acc
- 20 PP

## 3. First-acquisition policy

### Preserve vanilla acquisition map

- field pickups retain their TM numbers/locations
- Gym rewards remain their original TM numbers/moves
- story/NPC awards remain progression milestones
- existing alternate sources remain valid
- no badge-gated TM shop layer is added
- no requirement that every TM be obtainable before the Elite Four

### Replacement-slot inheritance

TM21 Air Slash inherits TM21's vanilla sources, including:

- Team Galactic Warehouse
- Veilstone Game Corner

TM78 Power Gem inherits TM78's vanilla Victory Road placement.

### Gym rewards

- Oreburgh: TM76 Stealth Rock
- Eterna: TM86 Grass Knot
- Hearthome: TM65 Shadow Claw
- Veilstone: TM60 Drain Punch
- Pastoria: TM55 Brine
- Canalave: TM91 Flash Cannon
- Snowpoint: TM72 Avalanche
- Sunyshore: TM57 Charge Beam

No Gym TM replacement is required.

## 4. TM economy

### Veilstone Department Store

Keep vanilla TM prices.

### Veilstone Game Corner

| TM | Move | Final price |
|---|---|---:|
| TM90 | Substitute | 1,000 Coins |
| TM58 | Endure | 1,000 |
| TM75 | Swords Dance | 2,000 |
| TM32 | Double Team | 2,000 |
| TM44 | Rest | 2,500 |
| TM89 | U-turn | 3,000 |
| TM10 | Hidden Power | 3,000 |
| TM27 | Return | 3,000 |
| TM21 | Air Slash | 4,000 |
| TM35 | Flamethrower | 4,000 |
| TM24 | Thunderbolt | 4,000 |
| TM13 | Ice Beam | 4,000 |
| TM29 | Psychic | 4,000 |
| TM74 | Gyro Ball | 5,000 |
| TM68 | Giga Impact | 6,000 |

The general Game Corner coin-purchase exchange rate is not changed by C2.

### Battle Frontier

TM BP tiers are halved:

- 32 BP → 16 BP
- 40 BP → 20 BP
- 48 BP → 24 BP
- 64 BP → 32 BP
- 80 BP → 40 BP

Final Frontier TM prices:

| TM | Move | BP |
|---|---|---:|
| TM06 | Toxic | 16 |
| TM73 | Thunder Wave | 16 |
| TM61 | Will-O-Wisp | 16 |
| TM45 | Attract | 16 |
| TM40 | Aerial Ace | 20 |
| TM31 | Brick Break | 20 |
| TM89 | U-turn | 20 |
| TM08 | Bulk Up | 24 |
| TM04 | Calm Mind | 24 |
| TM81 | X-Scissor | 32 |
| TM30 | Shadow Ball | 32 |
| TM53 | Energy Ball | 32 |
| TM36 | Sludge Bomb | 40 |
| TM59 | Dragon Pulse | 40 |
| TM71 | Stone Edge | 40 |
| TM26 | Earthquake | 40 |

Frontier-exclusive moves are not automatically moved into the main story.

## 5. Compatibility philosophy

For the 90 unchanged TMs, vanilla Platinum compatibility is the baseline.

### Add compatibility only when

- new typing plus anatomy/concept makes it clearly appropriate
- it directly supports the locked role
- evolution/family consistency requires it
- a clear vanilla hole exists

### Remove compatibility only when

- it is clearly nonsensical under the redesign
- it undermines a deliberately narrow role
- it exists only because a replaced TM occupied that number

### Coverage restraint

Do not grant premium coverage merely because a Pokémon's stats would benefit.

Particularly restricted from casual expansion:

- Earthquake
- Ice Beam
- Thunderbolt
- Flamethrower
- Psychic
- Shadow Ball
- Stone Edge
- Sludge Bomb
- Dragon Pulse
- Energy Ball
- Focus Blast

### Evolution family rules

- ordinary evolutions generally retain sensible pre-evolution compatibility
- evolved forms may gain logical new compatibility
- baby forms may remain narrower
- form-specific identities should be handled independently when appropriate

## 6. TM21 Air Slash compatibility — rebuild from zero

Every vanilla TM21 flag must be cleared before applying this set.

**Recipient count: 49**

### Kanto

- Charizard
- Butterfree
- Pidgey
- Pidgeotto
- Pidgeot
- Zubat
- Golbat
- Farfetch'd
- Scyther
- Articuno
- Moltres
- Dragonite
- Mew

### Johto

- Crobat
- Hoothoot
- Noctowl
- Natu
- Xatu
- Yanma
- Murkrow
- Delibird
- Mantine
- Skarmory
- Lugia
- Ho-Oh

### Hoenn

- Taillow
- Swellow
- Wingull
- Pelipper
- Masquerain
- Beautifly
- Ninjask
- Tropius
- Swablu
- Altaria
- Salamence
- Rayquaza

### Sinnoh

- Mothim
- Vespiquen
- Drifloon
- Drifblim
- Honchkrow
- Chatot
- Mantyke
- Togetic
- Togekiss
- Yanmega
- Shaymin Sky Forme
- Arceus

Important exclusions/notes:

- Shaymin Land Forme does not receive TM21.
- Rotom-Fan does not gain TM21 through global Rotom compatibility; its appliance move remains form-change based.
- Starly/Staravia/Staraptor remain physical-focused and are intentionally excluded.
- Former Frustration compatibility has no authority after the replacement.

## 7. TM78 Power Gem compatibility — rebuild from zero

Every vanilla TM78 flag must be cleared before applying this set.

**Recipient count: 27**

- Persian
- Staryu
- Starmie
- Mareep
- Flaaffy
- Ampharos
- Slowking
- Misdreavus
- Mismagius
- Corsola
- Nosepass
- Probopass
- Sableye
- Spoink
- Grumpig
- Vespiquen
- Omanyte
- Omastar
- Slugma
- Magcargo
- Lunatone
- Lileep
- Cradily
- Dialga
- Palkia
- Mew
- Arceus

Intentional exclusions include many physical/defensive Rock species where Power Gem would conflict with role identity, including Tyranitar, Regirock, Bastiodon, Rhyperior, Aerodactyl, Kabutops, Rampardos, Armaldo, Relicanth, and Solrock.

Former Captivate compatibility has no authority after the replacement.

## 8. Explicit retype-family compatibility additions

### Design-locked additions

**Farfetch'd**
- TM31 Brick Break
- HM06 Rock Smash

**Electabuzz**
- TM08 Bulk Up
- TM60 Drain Punch

**Electivire**
- TM08 Bulk Up
- TM60 Drain Punch

**Vigoroth**
- TM60 Drain Punch

**Slaking**
- TM60 Drain Punch

**Shinx**
- TM66 Payback

**Luxio**
- TM66 Payback

**Luxray**
- TM66 Payback

### Implementation reconciliation

**Raichu**
- TM91 Flash Cannon

This addition exists because the live source lacked the Flash Cannon compatibility assumed by the locked Raichu design. It is an implementation reconciliation, not a reopening of the design.

## 9. Retyped species explicitly requiring no further machine expansion

The C2/C3 audits found no additional machine correction necessary for:

- Blastoise
- Psyduck
- Golduck
- Pinsir
- Feraligatr
- Sceptile
- Milotic
- Glalie

Their natural learnsets and/or existing machine access already provide appropriate role support.

## 10. HM battle spec

| HM | Final battle behavior |
|---|---|
| HM01 Cut | Normal / Physical / 70 BP / 100 Acc / 30 PP / high crit |
| HM02 Fly | Flying / Physical / 100 BP / 100 Acc / 15 PP / two-turn semi-invulnerable |
| HM03 Surf | Water / Special / 95 BP / 100 Acc / 15 PP / vanilla targeting/effect |
| HM04 Strength | Normal / Physical / 80 BP / 100 Acc / 15 PP |
| HM05 Defog | Evasion -1; remove hazards both sides; remove target-side Reflect/Light Screen/Safeguard/Mist; 15 PP |
| HM06 Rock Smash | Fighting / Physical / 60 BP / 100 Acc / 15 PP / 50% Defense -1 |
| HM07 Waterfall | Water / Physical / 80 BP / 100 Acc / 15 PP / 20% flinch |
| HM08 Rock Climb | Normal / Physical / 90 BP / 95 Acc / 20 PP / 20% confusion |

## 11. HM compatibility philosophy

HMs may be somewhat broader than premium TMs because field progression still uses moves in Core 1.0.

- Cut: claws/blades/pincers/sharp leaves/cutting anatomy
- Fly: genuine capable fliers/airborne transport
- Surf: broad aquatic/swimmer access
- Strength: strong-bodied/muscular/mechanical species
- Defog: Flying/wind/air/mystical dispersal users
- Rock Smash: Fighting/strong impact users
- Waterfall: narrower aquatic charging/swimming users
- Rock Climb: climbers/clawed/rugged quadrupeds

Evolution-family HM continuity should be preserved where the field action still makes sense.

## 12. Implementation invariants

- TM21 and TM78 must be cleared globally before recipient application.
- Mew must be explicitly present in both final sets.
- Shaymin Sky only for TM21.
- Rotom appliance move handling must remain intact.
- No created move becomes a TM.
- No accidental broad same-type compatibility expansion.
- Compatibility patch should be guarded against the pinned source and followed by semantic diff + build validation.
