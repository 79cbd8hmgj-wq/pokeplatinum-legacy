# Pokémon Platinum Overhaul — Legendary & Mythical Event Spec

Status: **LOCKED SPEC**

## 1. Goal

Every Legendary and Mythical Pokémon in #001–#493 must be obtainable in one Platinum save through an in-game encounter, quest, gift, or breeding path.

No acquisition may require:
- WFC/distribution flags;
- another game;
- GBA Slot-2;
- trading;
- a second DS/save;
- Pal Park transfer data;
- multiplayer.

Legendary/Mythical species remain special encounters. They are not added as ordinary wild-table filler.

## 2. Global event rules

- Preserve native Platinum event infrastructure whenever it exists.
- Remove external/distribution prerequisites rather than recreating the event from scratch.
- Important statics are retry-safe until captured.
- Defeating or fleeing a static must not permanently lose it.
- Roamers that are accidentally defeated must have a deterministic reactivation path.
- Capture flags are set only after successful capture.
- Event items become normal in-save key-item rewards.
- Do not require every Mythical to unlock another Mythical.
- Core Sinnoh legends may gate Arceus; optional cross-region legend completion may not.
- Legendary encounters are primarily postgame unless Platinum already places them naturally in the main story.

## 3. Native Sinnoh authority

### Lake trio

**Uxie / Azelf**
- Preserve their normal Lake Acuity/Lake Valor static encounters.
- Preserve story timing.
- Retry until caught.

**Mesprit**
- Preserve the Lake Verity introduction and roaming identity.
- Preserve Lv50.
- If defeated, Professor Rowan can reactivate Mesprit after the player returns to the lab.

### Giratina
- Preserve the Distortion World story encounter.
- If not captured in the story, preserve Turnback Cave as the deterministic retry encounter.
- Preserve form/Griseous Orb infrastructure.

### Cresselia
- Preserve Fullmoon Island and Lunar Wing quest.
- Preserve roaming at Lv50.
- If defeated, Sailor Eldritch/Fullmoon quest state can deterministically reactivate it after the Lunar Wing story is complete.

### Heatran
- Preserve Stark Mountain/Buck quest and static encounter.
- Preserve Lv50.
- Retry until captured.

### Dialga / Palkia
- Preserve Platinum's postgame Spear Pillar rifts.
- Both are obtainable in the same save.
- Preserve Lv70.
- A defeated, uncaught rift resets after leaving/re-entering Spear Pillar.

### Rotom
Rotom is not counted as Legendary/Mythical, but its event dependency is owned here:
- preserve Old Chateau encounter;
- make Secret Key/form-room access permanently obtainable in-game;
- remove distribution-event checks from the appliance room;
- existing appliance/form move system remains intact.

## 4. Event item restoration

### Member Card / Darkrai

Unlock:
- Hall of Fame;
- Lunar Wing/Cresselia child quest completed.

After the child is cured, Sailor Eldritch's family provides the **Member Card** with dialogue about an item found among the child's nightmare-related belongings.

Then preserve Platinum's native:
Harbor Inn → nightmare sequence → Newmoon Island → Darkrai.

Changes:
- remove `DISTRIBUTION_EVENT_DARKRAI` gate;
- Member Card is obtained normally;
- Darkrai static = **Lv50**;
- event remains retry-safe until captured.

### Oak's Letter / Shaymin

Unlock:
- Hall of Fame;
- Route 224 accessible.

Professor Oak gives **Oak's Letter** on Route 224 as part of his existing tablet research.

Preserve:
Route 224 gratitude/tablet scene → Seabreak Path → Flower Paradise → Shaymin.

Changes:
- remove `DISTRIBUTION_EVENT_SHAYMIN` gate;
- no external item delivery;
- preserve Shaymin **Lv30**;
- retry until captured.

### Azure Flute / Arceus

Unlock requires:
- Hall of Fame;
- Uxie caught;
- Mesprit caught;
- Azelf caught;
- Dialga caught;
- Palkia caught;
- Giratina caught.

After those six Sinnoh cosmology encounters are complete, Cynthia appears in **Celestic Town** and gives the **Azure Flute**, explaining that the myths now point back to Spear Pillar.

Preserve:
Azure Flute → Spear Pillar/Hall of Origin → Arceus.

Changes:
- remove `DISTRIBUTION_EVENT_ARCEUS` gate;
- preserve Arceus **Lv80**;
- Darkrai/Shaymin/Manaphy and cross-region legends are not prerequisites;
- retry until captured.

### Secret Key / Rotom

After the player encounters/catches Rotom in the Old Chateau, Professor Rowan provides the **Secret Key** through the Eterna Galactic-building/Rotom-room follow-up.

Remove `DISTRIBUTION_EVENT_ROTOM` checks.

## 5. Regi chain

Platinum already contains:
- Rock Peak Ruins;
- Iceberg Ruins;
- Iron Ruins;
- dot puzzles;
- Regirock/Regice/Registeel battle scripts;
- Snowpoint Temple Regigigas check.

Use that infrastructure.

### Regirock / Regice / Registeel

Unlock:
- Hall of Fame.

Remove:
- fateful-encounter Regigigas requirement.

Keep:
- each ruin's dot puzzle;
- statue activation;
- separate capture state.

Raise each Regi from Lv30 to **Lv50** because these are postgame encounters.

Locations remain:
- Regirock — Rock Peak Ruins / Route 228;
- Regice — Iceberg Ruins / Mt. Coronet;
- Registeel — Iron Ruins / Iron Island.

Retry until captured.

### Regigigas

Snowpoint Temple awakens when the player has Regirock, Regice, and Registeel in the party, using the existing check.

Keep **Lv1**.

The Lv1 encounter is an intentional Platinum identity and is not raised for conventional postgame scaling.

## 6. Manaphy / Phione

### Manaphy

After the player completes the Lunar Wing quest and cures Sailor Eldritch's child, the sailor later receives a mysterious Egg recovered at sea.

Reward:
- **Manaphy Egg**.

No Pokémon Ranger/external save requirement.

The egg uses normal egg-hatching mechanics.

This quest is available once the Lunar Wing sequence is complete; Hall of Fame is not an additional requirement if the native quest becomes reachable earlier.

### Phione

Preserve:
- breed Manaphy with Ditto → Phione.

Breeding 2.0 must preserve this special case.

## 7. Kanto legendary chain

### Articuno / Zapdos / Moltres

Preserve Platinum's native roaming implementation:
- Articuno Lv60;
- Zapdos Lv60;
- Moltres Lv60.

Professor Oak activates the bird sightings after Hall of Fame/National research begins.

Keep all three trackable through the existing roaming/Pokétch infrastructure.

If one is defeated, Oak can reactivate only that uncaught bird.

### Mewtwo

Unlock:
- Articuno, Zapdos, and Moltres caught.

Professor Oak then reports an exceptionally powerful foreign Psychic Pokémon within the now-independent **Pal Park Research Preserve**.

Encounter:
- Pal Park mountain/field sector;
- static **Mewtwo Lv70**.

No transfer data is used.

### Mew

Unlock:
- Mewtwo caught;
- Hall of Fame.

Oak's final Kanto research note causes a rare Pokémon to appear in the secluded Pal Park forest sector.

Encounter:
- static **Mew Lv30**.

Mew is a quest reward encounter, not a random Pal Park spawn.

## 8. Johto legendary chain

Professor Oak's postgame research introduces three unusual migrating Pokémon. They are fixed quest encounters rather than adding three more roaming slots.

### Raikou
- Valley Windworks exterior;
- static **Lv50**.

### Entei
- Stark Mountain exterior, separate from Heatran's inner-room quest;
- static **Lv50**.

### Suicune
- Lake Acuity shoreline;
- static **Lv50**.

Each encounter receives a short Oak/sighting clue and independent capture flag.

### Lugia

Unlock:
- Raikou, Entei, Suicune caught.

A severe offshore disturbance is reported from the Pal Park coastal/water sector.

Encounter:
- static **Lugia Lv70**.

### Ho-Oh

Unlock:
- Raikou, Entei, Suicune caught.

A rainbow-colored Pokémon is reported over the summit after the player returns to Spear Pillar.

Encounter:
- static **Ho-Oh Lv70** at Spear Pillar, separate from the Dialga/Palkia rifts.

Lugia and Ho-Oh do not gate one another.

### Celebi

Unlock:
- Hall of Fame;
- Eterna Forest accessible.

Oak asks the player to investigate unusual time-related growth around the Moss Rock area.

Encounter:
- static **Celebi Lv30** in Eterna Forest.

Celebi does not require catching the Johto beasts or towers.

## 9. Hoenn legendary chain

### Regirock / Regice / Registeel
Handled by the native Platinum Regi chain above.

### Latias / Latios

After Cresselia and Darkrai have both been encountered/caught, Sailor Eldritch reports two dragonlike Pokémon repeatedly crossing the island routes.

Use fixed island encounters rather than expanding roamer storage:

- **Latias Lv50** — Fullmoon Island after Cresselia is caught.
- **Latios Lv50** — Newmoon Island after Darkrai is caught.

They remain independent encounters and do not replace the original Cresselia/Darkrai events.

### Weather trio — Groudon / Kyogre / Rayquaza

Professor Oak/Pal Park becomes the quest hub for foreign climate disturbances.

#### Groudon
Unlock:
- Hall of Fame;
- Pal Park research quest begun.

Static **Groudon Lv70** in the Pal Park mountain/land sector after completing a short severe-drought investigation.

#### Kyogre
Unlock:
- Hall of Fame;
- Pal Park research quest begun.

Static **Kyogre Lv70** in the Pal Park water/coastal sector after completing a short heavy-rain investigation.

#### Rayquaza
Unlock:
- Groudon caught;
- Kyogre caught.

Oak/Cynthia directs the player to the highest accessible point connected to the disturbance.

Static **Rayquaza Lv70** at Spear Pillar.

Rayquaza is separate from Ho-Oh and the creation-trio rifts through independent flags/object positions.

### Jirachi

Unlock:
- Hall of Fame.

A meteor observation from the Oreburgh Museum/Celestic research points to Mt. Coronet.

Static **Jirachi Lv30** at an upper Mt. Coronet exterior/summit alcove.

No real-time date requirement.

### Deoxys

Use Platinum's existing Veilstone meteorites/form system.

Unlock:
- Hall of Fame;
- player completes a short meteor-fragment research handoff between Oreburgh Museum and Veilstone.

Static **Deoxys Lv50** appears at the Veilstone meteorite site.

After capture, existing meteorites remain the form-change mechanism.

## 10. Pal Park repurpose

Pal Park must no longer imply that GBA transfers are required for Pokédex completion.

Postgame role:
**Pal Park Research Preserve**.

Use its existing lobby/field as a quest hub and habitat for a small number of foreign legendary research encounters:
- Mewtwo;
- Mew;
- Groudon;
- Kyogre;
- Lugia.

Do not turn Pal Park into a legendary zoo.

Professor Oak/research staff provide clues and gate each encounter.

Disable or bypass transfer prerequisites for these quests while preserving unrelated map functionality where safe.

## 11. Legendary level table

| Species/group | Level |
|---|---:|
| Uxie / Mesprit / Azelf | preserve native |
| Rotom | preserve native |
| Shaymin | 30 |
| Mew / Celebi / Jirachi | 30 |
| Regirock / Regice / Registeel | 50 |
| Cresselia | 50 |
| Heatran | 50 |
| Darkrai | 50 |
| Raikou / Entei / Suicune | 50 |
| Latias / Latios | 50 |
| Deoxys | 50 |
| Articuno / Zapdos / Moltres | 60 |
| Dialga / Palkia | 70 |
| Mewtwo | 70 |
| Lugia / Ho-Oh | 70 |
| Groudon / Kyogre / Rayquaza | 70 |
| Arceus | 80 |
| Regigigas | 1 |
| Manaphy | Egg / Lv1 hatch |
| Phione | Egg / Lv1 hatch |

## 12. Retry semantics

### Statics
If the player defeats/flees from an uncaught Legendary/Mythical:
- do not set caught/completion flag;
- restore the encounter after leaving/re-entering the map or re-triggering its quest object;
- blackout must not consume the encounter.

### Roamers
Mesprit, Cresselia, and the Kanto birds:
- preserve HP/status persistence while roaming;
- if captured, permanently close;
- if defeated, the relevant quest NPC can reactivate that species at full HP;
- no species requires an Elite Four rematch to respawn.

### Eggs/gifts
Manaphy Egg:
- only mark claimed after successfully added to party/PC;
- full party/bag state must not destroy the reward.

## 13. Completion rules

A one-save Legendary/Mythical validator must classify every special species #001–#493 as exactly one of:
- native story encounter;
- restored native event;
- new Sinnoh quest/static;
- native roamer;
- restored roamer;
- egg/gift;
- breeding result.

No species may remain classified as:
- distribution-only;
- transfer-only;
- version-only;
- second-game-only;
- WFC-only.

This spec is the canonical D5 event authority.
