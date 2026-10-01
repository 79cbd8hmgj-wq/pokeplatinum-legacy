# Pokémon Platinum Overhaul — Legendary/Mythical Event Spec

Status: **LOCKED SPEC**

## 1. Goal

Every Legendary/Mythical species #001–#493 must be obtainable in one Platinum save without:
- external distribution;
- another version/game;
- Pal Park migration;
- WFC;
- trading;
- multiplayer;
- event Pokémon prerequisites.

Use Platinum-native maps/scripts whenever possible. New scripting should extend existing Sinnoh locations rather than create disconnected menu gifts.

All one-time encounters must be retry-safe until captured.

## 2. Native Sinnoh encounters retained

Retain and ungate native content where appropriate:
- Uxie, Mesprit, Azelf;
- Giratina;
- Heatran;
- Cresselia;
- Dialga;
- Palkia;
- Regigigas;
- Articuno, Zapdos, Moltres;
- Rotom;
- Darkrai;
- Shaymin;
- Arceus.

Native encounter identities should remain recognizable.

## 3. Distribution-event restoration

### Darkrai
Use the Member Card / Harbor Inn / Newmoon Island sequence.

Progression:
- Hall of Fame required;
- complete the Fullmoon Island / Lunar Wing / sailor's child sequence;
- receive Member Card through the Canalave sailor/family follow-up;
- Harbor Inn sequence becomes permanently accessible;
- Newmoon Island Darkrai remains a static encounter.

Remove WFC/distribution checks.

Darkrai must respawn after defeat/blackout until captured.

### Shaymin
Use Oak's Letter / Route 224 / Seabreak Path / Flower Paradise.

Progression:
- Hall of Fame;
- meet Professor Oak through normal postgame/National Dex progression;
- Oak gives Oak's Letter;
- Route 224 event opens Seabreak Path;
- Flower Paradise Shaymin static remains Lv30 unless later global legendary-level audit changes it.

Remove distribution-event requirement.

Shaymin remains retry-safe until captured.

### Arceus
Use Azure Flute / Spear Pillar / Hall of Origin.

Progression:
- Hall of Fame;
- capture Dialga, Palkia, and Giratina;
- Cynthia/Celestic Elder provides Azure Flute after the trio condition;
- flute enables Hall of Origin at Spear Pillar;
- Arceus remains the capstone Legendary encounter.

Remove distribution-event requirement.

Keep Arceus as the highest-level static encounter.

### Rotom forms
Preserve Old Chateau Rotom encounter and existing appliance room.

After defeating Jupiter in the Eterna Galactic Building and obtaining/catching Rotom:
- Secret Key becomes obtainable in-game in the Eterna Galactic Building;
- Rotom's Room opens normally;
- remove distribution-event checks from room/appliance functionality;
- preserve appliance moves/form machinery.

No external event item required.

## 4. Regi chain

### Regirock / Regice / Registeel
Preserve Platinum's three native Regi ruin puzzles.

Requirements:
- Hall of Fame only;
- remove the fateful-encounter Regigigas prerequisite;
- activate floor-dot puzzle as normal;
- each Regi remains retry-safe until captured.

### Regigigas
Preserve Snowpoint Temple.

Requirement:
- player must have captured the three Regis in the save;
- do not require them to have originated from an external event.

Prefer checking caught flags/dex ownership rather than requiring all three physically in the active party if source implementation is clean; if party checking is retained for presentation, all three must be obtainable internally first.

Raise Regigigas from vanilla Lv1 to **Lv70** for the postgame encounter.

## 5. Sinnoh native roamers

### Mesprit / Cresselia
Preserve roaming identity.

If defeated rather than captured:
- restore/reactivate after the player next enters the Hall of Fame or via a deterministic postgame reset NPC;
- never become permanently missable.

### Articuno / Zapdos / Moltres
Preserve Platinum's native postgame roaming system and Oak introduction.

All three remain available in one save.

Same retry rule as Mesprit/Cresselia.

Do not convert the birds to arbitrary static gifts.

## 6. Dialga / Palkia / Giratina / Heatran

### Dialga / Palkia
Preserve Platinum's postgame Spear Pillar rifts.

Both obtainable in one save.

Make defeat non-final until capture.

### Giratina
Preserve story Distortion World encounter and Turnback Cave/postgame infrastructure.

If the player defeats rather than catches Giratina during the story, provide a deterministic retry encounter at Turnback Cave after Hall of Fame.

### Heatran
Preserve Stark Mountain/Buck sequence.

Make encounter retry-safe until capture.

## 7. Imported Kanto/Johto/Hoenn legends

These species require new Sinnoh-side acquisition because vanilla Platinum otherwise depends on external games/migration.

### Mewtwo
**Location:** abandoned Galactic laboratory room in Veilstone HQ, postgame.

Unlock:
- Hall of Fame;
- Team Galactic story complete;
- obtain a research key/clearance from Looker during postgame cleanup.

Presentation:
- abandoned cloning/research notes;
- static Mewtwo Lv70.

### Mew
**Location:** Floaroma Meadow.

Unlock:
- capture Mewtwo;
- complete Shaymin/Oak's Letter event.

Presentation:
- Professor Oak notes a rare Pokémon appearing where flowers recovered;
- static Mew Lv50.

### Raikou / Entei / Suicune
Do not expand the fixed roamer table in Core 1.0.

Use three static Sinnoh shrines/landmarks:
- Raikou — Valley Windworks exterior/postgame storm event, Lv60;
- Entei — Stark Mountain outer chamber after Heatran quest, Lv60;
- Suicune — Lake Acuity waterfront/cavern after Hall of Fame, Lv60.

All retry-safe.

### Lugia
**Location:** Route 230 / Battle Zone sea-side cavern or nearest existing deep-sea map confirmed usable by source audit.

Unlock:
- Hall of Fame;
- obtain Silver Wing from Canalave sailor after completing Cresselia/Darkrai chain.

Static Lv70.

If no suitable existing map exists, reuse a coherent coastal cavern before creating a new map.

### Ho-Oh
**Location:** Mt. Coronet/Spear Pillar postgame summit context.

Unlock:
- Hall of Fame;
- obtain Rainbow Wing from Celestic Elder after completing the three Johto beasts.

Static Lv70.

Do not interfere with Dialga/Palkia/Arceus triggers.

### Celebi
**Location:** Eterna Forest clearing/Old Chateau forest edge.

Unlock:
- Hall of Fame;
- complete Shaymin;
- receive GS-style relic/forest blessing from Professor Oak.

Static Lv50.

Use an existing forest map if possible.

### Latias / Latios
Static pair rather than new roaming slots.

- Latias — Fullmoon Island after Cresselia captured, Lv60.
- Latios — Newmoon Island after Darkrai captured, Lv60.

Each appears only after its native island's original legendary chain is complete.

### Kyogre
**Location:** a deep-water/coastal cavern in the Battle Zone or Route 230 area.

Unlock:
- Hall of Fame;
- obtain Blue Orb from a postgame researcher/sailor quest.

Static Lv70.

### Groudon
**Location:** Stark Mountain deep chamber after Heatran captured.

Unlock:
- Hall of Fame;
- obtain Red Orb through the same postgame weather-legend quest.

Static Lv70.

### Rayquaza
**Location:** Spear Pillar.

Unlock:
- capture Kyogre and Groudon;
- return to summit;
- static Rayquaza Lv75.

Do not overlap active Dialga/Palkia/Arceus event states.

### Jirachi
**Location:** Mt. Coronet summit/meteorite observation point.

Unlock:
- Hall of Fame;
- interact with a recovered meteorite item from the postgame route/Underground quest;
- static Jirachi Lv50.

### Deoxys
Use Veilstone's existing meteorite/form-change identity.

Unlock:
- capture Jirachi;
- inspect the Veilstone meteorites with the Meteorite item/state active;
- static Deoxys Lv60;
- preserve existing meteorite form-change functionality after capture.

## 8. Manaphy / Phione

### Manaphy
Add a Sinnoh-side Manaphy Egg quest.

Recommended flow:
- Hall of Fame;
- complete Canalave sailor/Cresselia sequence;
- complete Iron Island;
- sailor reports a rare Egg recovered at sea;
- receive Manaphy Egg if party has room, otherwise allow later pickup;
- never permanently missable.

No Pokémon Ranger dependency.

### Phione
Preserve Manaphy + Ditto breeding outcome.

No separate Phione static/gift required.

## 9. Encounter-level bands

Guideline:
- Mythicals intended as flavor/utility: Lv50;
- standard imported legendaries: Lv60;
- major box/ancient legends: Lv70;
- capstone Rayquaza: Lv75;
- Arceus: preserve Lv80.

Native encounter levels may remain when they are deliberately tied to Platinum's original presentation, but any extreme anomaly such as Regigigas Lv1 is corrected.

## 10. Retry safety

Every one-time static must satisfy:
- captured flag only on capture;
- defeat does not permanently set completion;
- blackout does not remove encounter;
- leaving/re-entering restores the encounter if uncaught.

Roamers must have deterministic reactivation after defeat.

Gifts/Eggs must:
- check party capacity;
- remain claimable if refused/full;
- set received flag only after successful grant.

## 11. Event items

Make these permanently obtainable in-game:
- Member Card;
- Oak's Letter;
- Azure Flute;
- Secret Key;
- Silver Wing;
- Rainbow Wing;
- Red Orb;
- Blue Orb;
- Meteorite/research-key equivalents where implemented.

Reuse existing item IDs where available.

For new quest keys, prefer unused/non-obtainable key-item slots only after an ID/source audit.

Do not repurpose ordinary held battle items.

## 12. External-dependency removal

Remove or bypass:
- distribution-event checks for Darkrai/Shaymin/Arceus/Rotom;
- fateful external Regigigas check for the three Regis;
- Pal Park/migration dependency for imported legends;
- event-only Manaphy Egg dependency.

Do not remove unrelated distribution infrastructure globally if local ungating is sufficient.

## 13. Completion order

Recommended postgame chain:

1. native lake trio / Cresselia / birds / Heatran;
2. Regi trio → Regigigas;
3. Dialga + Palkia + Giratina;
4. Darkrai + Shaymin;
5. Manaphy → Phione;
6. Johto beasts → Ho-Oh / Lugia;
7. Mewtwo → Mew;
8. Kyogre + Groudon → Rayquaza;
9. Jirachi → Deoxys;
10. Arceus as final Sinnoh capstone.

This is progression ordering, not a requirement to capture every earlier legendary unless explicitly stated above.

## 14. Validation

Create a legendary completion graph proving every Legendary/Mythical #001–#493 has:
- an internal one-save source;
- a reachable prerequisite chain;
- no circular prerequisite;
- no external dependency;
- retry semantics;
- unique captured/received state;
- correct map/event ownership.

This spec is approved authority for Legendary/Mythical events.
