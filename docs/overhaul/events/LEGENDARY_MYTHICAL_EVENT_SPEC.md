# Pokémon Platinum Overhaul — Legendary/Mythical Availability & Events

Status: **LOCKED SPEC**

## 1. Core policy

The overhaul separates **legendary identity** from **legendary acquisition treatment**.

No Legendary or Mythical Pokémon is demoted statistically, retyped, made breedable, or otherwise stripped of its canonical species identity merely to simplify availability.

Instead:

1. **Sinnoh/Platinum-native Legendary and Mythical Pokémon** retain proper Platinum-native story, static, roaming, or restored-event treatment.
2. **Older Legendary Pokémon that already have usable Platinum encounter infrastructure** reuse that infrastructure with external/event requirements removed.
3. **Older Legendary Pokémon without meaningful Platinum-native event content** become ultra-rare postgame habitat encounters.
4. **Older Mythical Pokémon** become hidden, retry-safe special static encounters rather than requiring large new quest chains.
5. All #001–#493 must be obtainable in one save without distribution events, other games, external hardware, WFC, or multiplayer.

The ordinary availability rule requiring >=5% encounter rates does **not** apply to optional postgame legacy Legendary encounters.

## 2. Retry and completion rules

### Sinnoh native statics/events
- one successful capture per save unless otherwise specified;
- if defeated, fled from, or the player blacks out, the encounter must remain/reappear;
- do not permanently consume the encounter until capture is confirmed.

### Older hidden Mythical statics
- one successful capture per save;
- retry-safe until captured.

### Older rare-habitat Legendary encounters
- renewable after capture;
- no caught flag removes them from the habitat;
- intentionally shiny-huntable;
- retain their existing catch rates unless separately specified.

### Roamers
- preserve roaming when Platinum already provides the system;
- if a roamer is defeated before capture, provide a deterministic respawn/reset path after re-entering the relevant postgame trigger or defeating the Elite Four again.

## 3. Platinum-native Legendary structure

### Uxie — Lake Acuity
- preserve native static encounter;
- post-Distortion World/native story timing;
- retry-safe until captured;
- retain approximately vanilla level 50.

### Azelf — Lake Valor
- preserve native static encounter;
- retry-safe until captured;
- retain approximately vanilla level 50.

### Mesprit — Lake Verity / roaming
- preserve the native encounter introduction and roaming identity;
- remove any unnecessary National Dex dependency;
- retry-safe roaming reset if defeated;
- retain approximately vanilla level 50.

### Giratina
- Distortion World remains the primary story encounter.
- Preserve Turnback Cave as the fallback/post-story Giratina space.
- A failed/defeated encounter must never permanently remove access.
- Preserve Origin Forme / Griseous Orb infrastructure.
- Main-story level remains aligned to Platinum's existing ~47 encounter rather than being inflated simply because it is legendary.

### Dialga and Palkia
- preserve Platinum's postgame Spear Pillar rift encounters;
- both obtainable in one save;
- level 70;
- retry-safe until captured;
- remove any unnecessary National Dex requirement if it blocks the approved one-save progression.

### Heatran
- preserve the Stark Mountain/Buck postgame quest and native static encounter;
- retry-safe until captured;
- keep the quest recognizable rather than replacing it with a random wild encounter.

### Cresselia
- preserve Fullmoon Island and roaming setup;
- preserve Lunar Wing / sailor's-son story;
- retry-safe if the roamer is defeated;
- the completed Cresselia story becomes a prerequisite for the in-game Darkrai/Manaphy follow-up described below.

### Regigigas
- preserve Snowpoint Temple encounter;
- remove the external event-Regigigas requirement;
- unlock once Regirock, Regice, and Registeel are caught in the same save;
- target level **70**;
- retry-safe until captured.

## 4. Restored Platinum Mythical content

### Darkrai

Use the existing Member Card / Harbor Inn / Newmoon Island infrastructure.

Unlock:
1. Hall of Fame achieved;
2. Cresselia/Lunar Wing sailor-child sequence completed.

Then:
- award or enable the Member Card through an in-game Canalave interaction;
- remove `DISTRIBUTION_EVENT_DARKRAI` as a requirement;
- keep the Harbor Inn/Newmoon Island presentation;
- Darkrai remains level 50 unless runtime balance gives a strong reason for a small adjustment;
- retry-safe until captured.

This makes Darkrai a direct narrative follow-up to the nightmare/Cresselia storyline.

### Shaymin

Use the existing Oak's Letter / Route 224 / Seabreak Path / Flower Paradise infrastructure.

Unlock:
1. Hall of Fame achieved;
2. Route 224 is accessible.

Then:
- Professor Oak provides Oak's Letter through an in-game interaction;
- remove `DISTRIBUTION_EVENT_SHAYMIN`;
- preserve Seabreak Path and Flower Paradise;
- Shaymin remains level 30;
- retry-safe until captured.

### Arceus

Use the existing Azure Flute / Spear Pillar / Hall of Origin infrastructure.

Unlock:
1. Hall of Fame achieved;
2. Dialga captured;
3. Palkia captured;
4. Giratina captured.

Then:
- Professor Rowan/Cynthia provides the Azure Flute through an in-game postgame interaction;
- remove `DISTRIBUTION_EVENT_ARCEUS`;
- preserve the Hall of Origin sequence;
- Arceus remains level 80;
- retry-safe until captured.

Arceus is the capstone of the Sinnoh creation-trio arc rather than a random postgame encounter.

### Manaphy

Manaphy receives a proper one-save Sinnoh gift rather than becoming a random wild Pokémon.

Unlock:
1. Hall of Fame achieved;
2. Cresselia/Lunar Wing sailor-child sequence completed.

Then:
- Sailor Eldritch in Canalave gives the player a **Manaphy Egg** as a one-time reward/thanks;
- use the existing Manaphy Egg graphics/data;
- if the party is full, do not consume the reward flag; allow the player to return.

### Phione

Preserve Manaphy breeding:
- Manaphy + Ditto → Phione;
- no separate wild/static Phione is required;
- D4 Breeding 2.0 must preserve this special case.

## 5. Rotom special content

Rotom is not Legendary but remains part of this event-restoration phase because its forms use event infrastructure.

- preserve Old Chateau Rotom encounter;
- preserve the Secret Key room and appliance-form mechanics;
- remove `DISTRIBUTION_EVENT_ROTOM` as a requirement;
- Secret Key becomes obtainable in-game immediately following the Old Chateau Rotom encounter or through a guaranteed pickup in the same room;
- once the player has Rotom + Secret Key, appliance access works permanently;
- preserve the five appliance moves/forms and recall behavior;
- no WFC/distribution dependency.

## 6. Older Legendary Pokémon — existing Platinum infrastructure

### Articuno / Zapdos / Moltres
Platinum already supports the legendary-bird roaming framework.

- preserve roaming identity rather than moving them into ordinary grass;
- unlock all three through the existing Oak/postgame roaming trigger;
- remove National Dex/distribution/external-game restrictions that are unnecessary to the overhaul;
- all three may coexist as active/obtainable roamers;
- defeated uncaught birds receive a deterministic reset path.

These are treated as rare migratory Pokémon in Sinnoh, not bespoke quest bosses.

### Regirock / Regice / Registeel
Platinum contains dedicated Regi encounter spaces.

Reuse those spaces:
- Regirock → Rock Peak Ruins;
- Regice → Iceberg Ruins;
- Registeel → Iron Ruins.

Remove the requirement to bring an event-distributed Regigigas.

Unlock:
- Hall of Fame;
- relevant ruins accessible.

Each Regi:
- one successful capture per save;
- retry-safe until captured;
- native room/puzzle presentation retained.

They then unlock Regigigas as described above.

## 7. Older Legendary Pokémon — rare postgame habitats

These species do **not** receive new multi-step quest lines.

They become renewable, ultra-rare postgame encounters once Hall of Fame is achieved.

Two rarity tiers:
- **Legacy Rare:** 2%
- **Legacy Apex:** 1%

Exact map slot/level manifests are implementation data, but the following habitat assignments are locked.

| Species | Tier | Locked habitat | Method | Target level band |
|---|---:|---|---|---:|
| Mewtwo | Apex 1% | deepest Turnback Cave rooms | cave | 68–72 |
| Raikou | Rare 2% | Route 222 / Sunyshore electric coast | grass | 55–60 |
| Entei | Rare 2% | Route 227 / Stark Mountain approach | grass | 55–60 |
| Suicune | Rare 2% | Route 230 outer water | Surf | 55–60 |
| Lugia | Apex 1% | Route 230 deep sea | Surf | 65–70 |
| Ho-Oh | Apex 1% | Route 225 highland | grass | 65–70 |
| Latias | Rare 2% | Route 229 | grass | 55–60 |
| Latios | Rare 2% | Route 229 | grass | 55–60 |
| Groudon | Apex 1% | Route 228 desert | grass | 65–70 |
| Kyogre | Apex 1% | Route 223 deep water | Surf | 65–70 |
| Rayquaza | Apex 1% | Route 224 highland/coastal terminus | grass | 68–72 |

Rules:
- only active after Hall of Fame;
- renewable indefinitely;
- no caught flag suppresses the wild slot;
- day/time may improve rates but cannot be required;
- no swarm/Radar/dual-slot dependency;
- do not exceed the encounter-table density budget without replacing other postgame convenience slots;
- retain normal legendary catch rates.

## 8. Older Mythical Pokémon — hidden postgame statics

Older Mythicals are not ordinary grass encounters and do not receive full custom quest chains.

They use concise environmental discoveries.

### Mew
- hidden static in a secluded Eterna Forest clearing;
- appears only after Hall of Fame;
- level 50;
- retry-safe until captured.

### Celebi
- hidden static in Floaroma Meadow;
- appears only after Hall of Fame;
- level 50;
- retry-safe until captured.

### Jirachi
- hidden static on the upper Mt. Coronet/Spear Pillar approach at night;
- Hall of Fame required;
- level 50;
- night controls presentation only after unlock; if implementing a strict night-only spawn risks availability, provide an all-day retry path once discovered;
- retry-safe until captured.

### Deoxys
- hidden static associated with the Veilstone meteorites;
- Hall of Fame required;
- level 60;
- preserve Platinum's meteorite form-change infrastructure;
- retry-safe until captured.

These encounters should use minimal dialogue/visual scripting. They are discoveries, not elaborate quest chains.

## 9. Catching and battle philosophy

- Do not raise catch rates globally for Legendary/Mythical Pokémon in D5.
- D3 Poké Ball improvements already reduce capture friction.
- Do not give these Pokémon custom boss-only stats or movesets.
- Wild/static levels should fit the postgame level curve without forcing grinding.
- Renewable older Legendary encounters make accidental KO/shiny hunting non-destructive.
- Sinnoh native one-per-save statics remain special but must be retry-safe.

## 10. Pokédex/completion

No Legendary/Mythical acquisition may require:
- event distribution;
- WFC;
- other cartridge;
- Slot-2;
- Pal Park migration;
- Ranger;
- another save/system;
- multiplayer;
- trading.

Every #001–#493 species must have an in-save path.

Legendary/Mythical species do not need to be obtainable pre-Elite Four.

## 11. Event priority

Implementation order:
1. remove distribution checks from existing Sinnoh event infrastructure;
2. fix retry safety of native encounters;
3. restore Rotom form access;
4. implement Darkrai/Shaymin/Arceus unlocks;
5. implement Manaphy Egg reward;
6. free the Regi rooms from event-Regigigas dependency and connect Regigigas;
7. normalize legendary-bird roaming;
8. add legacy rare-habitat encounter slots;
9. add four older Mythical statics;
10. validate all #001–#493 coverage.

This spec is the canonical D5 authority.
