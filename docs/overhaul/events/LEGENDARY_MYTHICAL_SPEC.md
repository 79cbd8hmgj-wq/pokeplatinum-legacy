# Pokémon Platinum Overhaul — Legendary/Mythical Availability Spec

Status: **LOCKED SPEC**

## 1. Design target

All Pokémon #001–#493 must be obtainable in one save without WFC, external distribution, trading, Slot-2, a second game/system, or event-only hardware.

D5 deliberately avoids building a bespoke quest for every older legendary.

### Core rule

Use the lightest treatment that preserves identity:

1. **Sinnoh / Platinum-native legends and mythicals** keep their native Platinum story, map, roaming, static, or restored-event presentation.
2. **Older legends with useful Platinum-native infrastructure** may reuse that infrastructure if it is simpler than replacing it.
3. **Other Gen I–III legends** become renewable ultra-rare postgame habitat encounters.
4. **Older Gen I–III mythicals** use lightweight hidden/retry-safe statics rather than large custom quest chains.

"Legendary" status in species data is not removed. The simplification is acquisition treatment, not stats/species identity.

## 2. Global acquisition rules

- No external distribution checks may block completion.
- No event item may require WFC.
- All one-time static/event encounters must be retry-safe after defeat or blackout.
- Catch flags hide a one-time native legendary only after successful capture.
- Older legendary habitat encounters are renewable.
- Older legendary habitat encounter rates may be below the normal 5% family-availability floor because they are optional postgame apex encounters.
- Use 1–3% rates depending on tier.
- Do not place these species pre-Elite Four unless already required by Platinum's main story.
- Do not alter legendary BST, catch rate, typing, or ability merely because acquisition is simplified.
- Legendary/Mythical placement must not crowd ordinary encounter tables; use dedicated postgame/deep-area slots where possible.

## 3. Platinum-native / Sinnoh legendary treatment

### Main-story / native statics

Preserve the existing story structure unless a retry fix is required:

| Species | Treatment | Level |
|---|---|---:|
| Giratina | Distortion World native story encounter | native/current story level |
| Uxie | Lake Acuity static | native/current level |
| Azelf | Lake Valor static | native/current level |
| Mesprit | Lake Verity activation + roaming | native/current level |
| Heatran | Stark Mountain native postgame static | 50 |
| Cresselia | Fullmoon Island activation + roaming | native/current level |
| Dialga | Spear Pillar postgame native static | native/current level |
| Palkia | Spear Pillar postgame native static | native/current level |
| Regigigas | Snowpoint Temple native static after the three Regis | 1 |

Regigigas remains Lv1. This is a distinctive Platinum identity and is not a difficulty gate.

### Retry behavior

For Uxie, Azelf, Heatran, Dialga, Palkia, Regigigas, and other one-time statics:
- defeat without capture must not permanently delete the encounter;
- blackout must not permanently delete it;
- only successful capture sets the permanent caught/hide state.

Mesprit/Cresselia roaming state must remain recoverable and not become permanently lost through a failed battle.

## 4. Restored Platinum event content

### Darkrai

Keep the Harbor Inn → Newmoon Island → Darkrai event.

Current source already has:
- Newmoon Island;
- Darkrai object/script;
- Lv50 battle;
- Member Card check;
- distribution-event check.

Overhaul:
- remove the WFC/distribution requirement;
- make Member Card obtainable permanently in-game after completing the Cresselia/Lunar Wing sequence and Hall of Fame;
- retain Lv50 Darkrai;
- preserve Newmoon Island/Harbor Inn presentation;
- defeat without capture must allow retry.

### Shaymin

Keep Route 224 / Seabreak Path / Flower Paradise.

Current source already has:
- Flower Paradise;
- Shaymin object/script;
- Lv30 fateful encounter;
- Oak's Letter check;
- distribution-event check.

Overhaul:
- remove the WFC/distribution requirement;
- Oak gives Oak's Letter at Route 224 after Hall of Fame and National Dex access;
- preserve Seabreak Path and Flower Paradise;
- retain Lv30 Shaymin;
- defeat without capture must allow retry.

### Arceus

Keep Azure Flute / Hall of Origin.

Current source already has:
- Hall of Origin map/script;
- Arceus object;
- Lv80 legendary battle;
- distribution-event check.

Overhaul:
- remove the distribution requirement;
- Azure Flute becomes the 493-completion capstone trigger:
  - player must have caught all other obtainable species #001–#492;
  - Arceus itself is excluded from the prerequisite;
- after satisfying that condition, Professor Rowan/Oak provides the Azure Flute;
- preserve Hall of Origin and Lv80 Arceus;
- defeat without capture must allow retry.

This makes Arceus the final Pokédex completion encounter rather than a random external event.

### Rotom forms

Rotom is not legendary, but its event infrastructure belongs here.

Keep the existing appliance room and form-change scripts.

Overhaul:
- remove the Rotom distribution-event requirement from the appliance room;
- make the Secret Key obtainable permanently in-game after the player first catches Rotom;
- preserve appliance moves and Rowan room scene;
- do not require WFC.

## 5. Manaphy and Phione

### Manaphy

Use a lightweight restored-gift style acquisition rather than a new multi-stage quest.

After Hall of Fame:
- the Canalave sailor/family sequence gains a one-time Manaphy Egg gift after the Cresselia/Lunar Wing event is completed;
- no Ranger game or external transfer is required;
- the egg is retry-safe if the party is full by simply withholding the gift until space exists.

This ties the Sea Guardian to Canalave and an existing island/sailor storyline with minimal new scripting.

### Phione

Retain Manaphy breeding → Phione.

No separate wild Phione or gift is required.

Breeding 2.0 must preserve this special case.

## 6. Regi line

Regirock, Regice, and Registeel are older legends but Platinum already contains dedicated ruin infrastructure.

Use it rather than replacing them with grass encounters.

Overhaul:
- remove the requirement for an event-distributed Regigigas;
- unlock the three Platinum Regi ruins permanently in postgame;
- each Titan remains a retry-safe static in its existing ruin;
- after all three are caught/owned, Snowpoint Temple Regigigas can awaken using the native party check;
- no external Regigigas is required.

No new Regi quest chain is needed.

## 7. Renewable Gen I–III legendary habitats

These species are treated as rare postgame apex fauna.

### Rate tiers

- **R2** = 2% renewable encounter
- **R1** = 1% renewable encounter

They appear only after Hall of Fame unless a map already has a stricter postgame gate.

| Species | Habitat | Method | Tier | Level band |
|---|---|---|:---:|---:|
| Articuno | Snowpoint Temple deep floors / Acuity cavern ecology | cave | R2 | 55–60 |
| Zapdos | Fuego Ironworks / Valley Windworks high-energy zone | land | R2 | 55–60 |
| Moltres | Stark Mountain exterior/deep volcanic zone | land/cave | R2 | 55–60 |
| Mewtwo | Turnback Cave deepest valid encounter zone | cave | R1 | 70 |
| Raikou | Route 222 / Sunyshore electric coast | land | R2 | 55–60 |
| Entei | Stark Mountain exterior volcanic zone | land | R2 | 55–60 |
| Suicune | Lake Acuity / northern clear-water zone | Surf | R2 | 55–60 |
| Lugia | deep postgame sea/cavern habitat near Routes 226–230 | Surf/cave | R1 | 65–70 |
| Ho-Oh | upper Mt. Coronet / Spear Pillar-adjacent postgame habitat | land/cave | R1 | 65–70 |
| Latias | Routes 224–230 postgame coast | land/Surf as source permits | R2 | 55–60 |
| Latios | Routes 224–230 postgame coast | land/Surf as source permits | R2 | 55–60 |
| Kyogre | deep postgame ocean, Routes 226–230 | Surf | R1 | 70 |
| Groudon | Stark Mountain deepest terrestrial zone | cave | R1 | 70 |
| Rayquaza | upper Mt. Coronet / Spear Pillar postgame encounter zone | cave/land | R1 | 70 |

Exact map/slot selection is implementation work and must respect encounter-table budgets.

### Duplicate habitat rule

Where two legendary species share a region:
- do not put both into the same 1% slot if a neighboring/deeper map can separate them;
- use map identity to keep each hunt legible;
- ordinary species density remains the priority.

## 8. Older Mythicals — lightweight hidden statics

Do not create full bespoke quest chains.

Each is:
- postgame;
- one-time but retry-safe;
- unlocked by simple local condition;
- no distribution item.

### Mew — Eterna Forest hidden grove

- postgame hidden static in an existing secluded Eterna Forest zone;
- Lv50;
- appears after National Dex / Hall of Fame;
- no custom dungeon.

### Celebi — Eterna Forest / Old Chateau forest shrine

- postgame hidden static tied to a forest shrine/clearing;
- Lv50;
- simple interaction trigger;
- distinct location from Mew.

### Jirachi — Mt. Coronet summit-side star event

- postgame hidden static at a summit/meteor-associated Coronet location;
- Lv50;
- simple night-agnostic trigger; no real-time/day restriction.

### Deoxys — Veilstone meteorite area

- postgame hidden static near Veilstone's existing meteorites;
- Lv60;
- form-changing meteorite infrastructure remains available;
- no external event.

If an exact static object placement would require disproportionate map editing, implementation may use an interactable tile/NPC-less script trigger in the same approved location.

## 9. Species intentionally not converted to rare wild encounters

Keep bespoke/native treatment for:
- Uxie
- Mesprit
- Azelf
- Dialga
- Palkia
- Giratina
- Heatran
- Regigigas
- Cresselia
- Phione
- Manaphy
- Darkrai
- Shaymin
- Arceus
- Regirock
- Regice
- Registeel

Reason: Platinum already supplies useful native infrastructure or the species has a direct Sinnoh narrative role.

## 10. Roaming policy

Do not add new roamers for Gen I–III legends.

Older legends that vanilla Platinum may have used as roamers can be moved to the renewable habitat model.

Mesprit and Cresselia keep roaming because it is part of their native Sinnoh presentation.

No legendary completion path may depend on a roamer permanently disappearing.

## 11. Pokédex / completion policy

The final one-save graph must classify every legendary/mythical #001–#493 as one of:

- NATIVE_STATIC
- NATIVE_ROAMER
- RESTORED_EVENT
- NATIVE_RUIN
- RARE_POSTGAME_HABITAT
- HIDDEN_MYTHICAL_STATIC
- BREEDING_ONLY (Phione)

Arceus is the only species allowed to depend on near-complete Pokédex capture progress.

The validator must prove every other species can be obtained before Arceus.

## 12. Acceptance

D5 is complete when:
- every legendary/mythical #001–#493 has a one-save path;
- no distribution/WFC/external-game check remains required;
- native Sinnoh events retain their identity;
- older legends do not require bespoke new quest chains;
- older legendary habitat encounters are renewable;
- older mythical statics are retry-safe;
- Arceus is obtainable after all #001–#492 are caught;
- Manaphy and Phione are obtainable without Pokémon Ranger;
- Regigigas no longer depends on an event Regigigas to unlock its own prerequisite Regis;
- Rotom forms no longer depend on Secret Key distribution.
