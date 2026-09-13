# Created Moves — C2.5 Canonical Spec

Status: `LOCKED DESIGN / IMPLEMENTING`

## Allocation

- Custom IDs: **468–489**
- Count: **22**
- Generic progression moves: **468–476**
- Identity moves: **477–489**
- Target `MAX_MOVES`: **490**

Implementation source authority currently reconstructed from the v3 created-move plumbing manifest.

## Generic progression moves

| ID | Constant | Move | Type | Class | Power | Acc | PP | Effect | Contact |
|---:|---|---|---|---|---:|---:|---:|---|---|
| 468 | `MOVE_STATIC_STRIKE` | Static Strike | Electric | Physical | 85 | 100 | 15 | 10% paralysis | Yes |
| 469 | `MOVE_FROST_RUSH` | Frost Rush | Ice | Physical | 80 | 100 | 15 | none | Yes |
| 470 | `MOVE_AURA_BURST` | Aura Burst | Fighting | Special | 70 | 100 | 15 | 10% Sp. Def -1 | No |
| 471 | `MOVE_DRAGON_SWIPE` | Dragon Swipe | Dragon | Physical | 60 | 100 | 20 | none | Yes |
| 472 | `MOVE_METAL_RAY` | Metal Ray | Steel | Special | 50 | 100 | 25 | none | No |
| 473 | `MOVE_RIPTIDE_RUSH` | Riptide Rush | Water | Physical | 65 | 100 | 20 | none | Yes |
| 474 | `MOVE_MIND_STRIKE` | Mind Strike | Psychic | Physical | 55 | 100 | 20 | 10% confusion | Yes |
| 475 | `MOVE_DREAD_WAVE` | Dread Wave | Dark | Special | 60 | 100 | 20 | 10% Sp. Def -1 | No |
| 476 | `MOVE_SPIRIT_WISP` | Spirit Wisp | Ghost | Special | 50 | 100 | 25 | none | No |

### Confirmed final generic distribution

| Move | Confirmed C3 recipients |
|---|---|
| Static Strike | Electabuzz, Electivire, Luxray |
| Frost Rush | Glalie, Delibird |
| Aura Burst | Toxicroak |
| Dragon Swipe | **Historical final recipient unresolved; do not invent one** |
| Metal Ray | Raichu |
| Riptide Rush | Feraligatr, Kingler, Seaking, Qwilfish, Whiscash, Crawdaunt, Huntail |
| Mind Strike | Medicham, Girafarig, Stantler, Solrock |
| Dread Wave | Shiftry, Cacturne |
| Spirit Wisp | Rotom and appliance forms through ordinary shared level-up progression |

`Dragon Swipe` remains part of the 22-move implementation even though no authoritative final C3 recipient was recovered. This is not a build blocker and must not be resolved by guessing during implementation.

## Identity moves

| ID | Constant | Move | Primary recipient | Type | Class | Power | Acc | PP | Effect | Contact |
|---:|---|---|---|---|---|---:|---:|---:|---|---|
| 477 | `MOVE_RESONANT_SLASH` | Resonant Slash | Kricketune | Bug | Physical | 60 | 100 | 20 | high critical-hit ratio; sound-based | Yes |
| 478 | `MOVE_SOLAR_PETAL` | Solar Petal | Cherrim | Grass | Physical | 100 | 100 | 10 | charges normally; skips charge in sun | Yes |
| 479 | `MOVE_VINE_SNARE` | Vine Snare | Carnivine | Grass | Physical | 65 | 100 | 15 | traps 2–5 turns | Yes |
| 480 | `MOVE_LUMINOUS_CURRENT` | Luminous Current | Finneon/Lumineon | Water | Special | 60 | 100 | 15 | guaranteed Speed -1 | No |
| 481 | `MOVE_SOUL_SIPHON` | Soul Siphon | Spiritomb | Ghost | Special | 60 | 100 | 10 | heals 50% of damage dealt | No |
| 482 | `MOVE_POLLEN_PULSE` | Pollen Pulse | Wormadam Plant | Grass | Special | 55 | 100 | 15 | guaranteed Sp. Atk -1 | No |
| 483 | `MOVE_EARTHEN_BASH` | Earthen Bash | Wormadam Sandy | Ground | Physical | 70 | 100 | 15 | 30% Defense -1 | Yes |
| 484 | `MOVE_SCRAP_GUARD` | Scrap Guard | Wormadam Trash | Steel | Status | — | — | 10 | Defense +1, Sp. Def +1 | No |
| 485 | `MOVE_MAGNET_VOLLEY` | Magnet Volley | Probopass | Steel | Special | 25 × 3 | 100 | 10 | exactly three equal-power hits | No |
| 486 | `MOVE_SOUL_GRIP` | Soul Grip | Dusknoir | Ghost | Physical | 70 | 100 | 15 | traps 2–5 turns | Yes |
| 487 | `MOVE_STALK_SLASH` | Stalk Slash | Farfetch'd | Fighting | Physical | 60 | 100 | 15 | high critical-hit ratio | Yes |
| 488 | `MOVE_CURSED_STITCH` | Cursed Stitch | Banette | Ghost | Physical | 75 | 100 | 15 | 20% confusion | Yes |
| 489 | `MOVE_STAR_JAB` | Star Jab | Ledian | Bug | Physical | 65 | 100 | 15 | 20% flinch; punching | Yes |

## Principal identity distribution

- Resonant Slash → Kricketune
- Solar Petal → Cherrim
- Vine Snare → Carnivine
- Luminous Current → Finneon and Lumineon
- Soul Siphon → Spiritomb
- Pollen Pulse → Plant Cloak Wormadam
- Earthen Bash → Sandy Cloak Wormadam
- Scrap Guard → Trash Cloak Wormadam
- Magnet Volley → Probopass
- Soul Grip → Dusknoir
- Stalk Slash → Farfetch'd
- Cursed Stitch → Banette at Lv38
- Star Jab → Ledian

Identity moves should remain strongly associated with their intended Pokémon. They do not become general TMs, general tutors, or broad egg moves in Core 1.0.

## Implementation effect mapping

Most created moves reuse existing battle effects.

Important special handling:

### Resonant Slash

- effect: high critical-hit ratio
- add to `sSoundMoves`
- Soundproof/sound-move interactions must recognize it

### Star Jab

- effect: flinch hit
- add to `sPunchingMoves`
- Iron Fist must recognize it

### Magnet Volley

The v3 plumbing spec allocates a dedicated effect identity for structural clarity:

`BATTLE_EFFECT_HIT_THREE_TIMES_EQUAL_POWER`

Target behavior:

- exactly three hits
- 25 BP per hit
- equal power on every hit
- non-contact
- no Triple Kick power escalation

Recovered implementation direction:

`SetMultiHit 3, SYSCTL_MULTI_HIT_MOVE`

with ordinary critical/damage calculation and normal multi-hit messaging.

## Resource/build requirements

The reconstructed v3 manifest requires:

- append `MOVE_STATIC_STRIKE` through `MOVE_STAR_JAB` to `generated/moves.txt`
- create `res/moves/<stem>/data.json`
- create each custom move animation resource
- create each custom move script resource
- adjust moveproc so IDs 468–489 are ordinary move-data records
- keep reserved retail-unused animation/script slots 490–500 after the custom moves
- append the Magnet Volley effect script to the battle-effect build
- audit all `MAX_MOVES` consumers

## Build gate

Do not apply species learnsets referencing these constants until:

1. enum generation passes
2. move-data processing passes
3. battle scripts build
4. full ROM build passes
5. structural count/range checks pass
6. Resonant Slash sound behavior is tested
7. Star Jab punching behavior is tested
8. Magnet Volley is verified as exactly three equal-power hits

## Final-audit constraints

- Banette Cursed Stitch is Lv38, not Lv31.
- Probopass Magnet Volley is a Probopass-specific evolved-state payoff.
- Dusknoir Soul Grip is an evolved-state payoff.
- Wormadam cloak moves are form-specific.
- Rotom appliance signature attacks remain handled by Platinum's native form-change system; Spirit Wisp is the shared early Ghost progression move.
