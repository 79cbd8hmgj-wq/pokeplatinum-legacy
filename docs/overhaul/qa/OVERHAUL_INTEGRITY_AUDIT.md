# Pokémon Platinum Overhaul — Design/Implementation Integrity Audit

Status: **IN PROGRESS**

Purpose: detect cases where implementation, manifests, validators, or reconstructed "locked" specifications agree with each other but have drifted from the originally approved overhaul design.

This audit does **not** treat a green validator as proof of design correctness. Each subsystem is reconciled through three layers:

1. strongest surviving original design evidence;
2. canonical/current repo specification or historical implementation authority;
3. actual source on `main`.

Findings are classified as:

- **MATCH** — original design, authority, and current source agree;
- **IMPLEMENTATION BUG** — authority/design agree but current source differs;
- **SPEC DRIFT** — current canonical spec differs from stronger original design evidence;
- **AUTHORITY CONFLICT** — surviving approved sources conflict and need owner resolution;
- **MISSING IMPLEMENTATION** — approved design exists but is not present;
- **UNPROVEN** — surviving evidence is insufficient to establish intent.

The Poké Ball distribution issue discovered before this audit is the motivating example: the implementation and validator matched a later locked spec, but the later spec itself had drifted from the intended early-availability design.

---

## Audit order

1. Pass A / Pass B species core — types, stats, abilities, roles
2. Evolution methods and timing
3. C1 existing move rebalance
4. C2 TM/HM mechanics and TM distribution
5. C2.5 created moves and distribution
6. C3 level-up learnsets and TM compatibility
7. Wild encounters / #001–#493 availability
8. Special acquisitions and gifts
9. Trainers and progression
10. EXP / economy / items / shops
11. Poké Ball system
12. Breeding 2.0
13. Legendary / Mythical events
14. Battle Frontier / postgame
15. Mystery starter / opening flow

---

# 1. Pass A / Pass B species core

## 1A. Locked retype identity group — COMPLETE

The original Pass A/Pass C history identifies exactly 17 retyped species/family members:

- Blastoise — Water/Ground
- Raichu — Electric/Steel
- Psyduck — Water/Psychic
- Golduck — Water/Psychic
- Farfetch'd — Fighting/Flying
- Electabuzz — Electric/Fighting
- Electivire — Electric/Fighting
- Pinsir — Bug/Fighting
- Feraligatr — Water/Ground
- Sceptile — Grass/Dragon
- Vigoroth — Normal/Fighting
- Slaking — Normal/Fighting
- Milotic — Water/Dragon
- Glalie — Ice/Steel
- Shinx — Electric/Dark
- Luxio — Electric/Dark
- Luxray — Electric/Dark

### Historical implementation authority

Compared:
- baseline: `0fee7dc526f3220dc6a3b58986415446423f83de`
- authoritative C3 species snapshot: `887c0d8a17104cebfab2d66b284b1ee7feae7f20`
- current: `main`

Owned fields checked:
- `types`
- `base_stats`
- `abilities`

### Result

**17 / 17 MATCH. 0 mismatches.**

All 17 current `main` species records exactly match the authoritative historical C3 snapshot for type, base stats, and abilities.

The major Pass B identity values also agree with the surviving approved design evidence, including:

- Blastoise — 79/83/110/90/105/63, Torrent
- Raichu — 60/70/75/100/80/90, Static
- Farfetch'd — 62/95/70/58/75/70, Super Luck / Inner Focus
- Feraligatr — vanilla Platinum stats, Torrent
- Sceptile — vanilla Platinum stats, Overgrow
- Vigoroth — vanilla Platinum stats, Vital Spirit
- Slaking — vanilla Platinum 670 BST, Truant preserved
- Milotic — vanilla Platinum stats, Marvel Scale
- Glalie — 80/90/100/70/90/50, Inner Focus / Ice Body
- Shinx/Luxio/Luxray — Electric/Dark with existing Rivalry / Intimidate chassis

### Classification

**MATCH**

No source correction is required for the 17-species retype identity block.

### Important limitation

This clears only the retyped identity group. It does **not** prove the full Pass B 493-species stats/abilities layer is correct. The next audit block is the explicit **Role Repair** population, followed by **Light Enrichment**, then the 337 auto-preserved species.

---

## Next active block

**1B — Pass B Role Repair reconciliation**

Target:
- recover the approved role-repair assignments from surviving project history;
- compare exact stats/abilities against current `main`;
- flag any reconstructed-spec or implementation drift;
- do not use current validator/manifests as sole authority.


---

## 1C. Pass B Light Enrichment — Gen I — COMPLETE

Strong surviving project-history evidence marks the Gen I Light Enrichment stage **approved and locked**.

Seven explicit changes were required:

| Species | Locked Pass B change | Current main before recovery | Finding |
|---|---|---|---|
| Butterfree | Compound Eyes / Tinted Lens | Compound Eyes / None | MISSING IMPLEMENTATION |
| Fearow | Keen Eye / Sniper | Keen Eye / None | MISSING IMPLEMENTATION |
| Sandslash | 75/100/110/35/65/65 | vanilla 75/100/110/45/55/65 | MISSING IMPLEMENTATION |
| Vileplume | Chlorophyll / Effect Spore | Chlorophyll / None | MISSING IMPLEMENTATION |
| Dugtrio | Attack 90 | vanilla Attack 80 | MISSING IMPLEMENTATION |
| Dodrio | Tangled Feet / Early Bird | Run Away / Early Bird | MISSING IMPLEMENTATION |
| Muk | Liquid Ooze / Sticky Hold | Stench / Sticky Hold | MISSING IMPLEMENTATION |

### Result

**0 / 7 were present on main.**

This is a major integrity finding: the approved Pass B design was not fully carried into the historical C3 species implementation snapshot, so later validators could pass while the intended species redesign was incomplete.

### Recovery

A dedicated source-fix branch/PR restores all seven locked changes and was rechecked against the approved values: **7 / 7 match, 0 mismatches after patching**.

This proves the full Pass B layer cannot be considered trustworthy solely because C3/source validators pass.

### Classification

**MISSING IMPLEMENTATION — CONFIRMED AND PATCHED**

---

## Revised next active block

Continue Pass B reconciliation generation by generation:

1. Gen II Light Enrichment
2. Gen III Light Enrichment
3. Gen IV Light Enrichment
4. Role Repair groups across Gen I–IV
5. auto-preserved/restraint population spot-check and count reconciliation

Any missing locked changes should be repaired in dedicated recovery PRs rather than folded silently into the audit document.


---

## 1D. Pass B Light Enrichment — Generations II–IV — COMPLETE

The surviving project history marks the Gen II, Gen III, and Gen IV Light Enrichment blocks locked.

### Gen II
Explicit locked changes:
- Sudowoodo — Solid Rock / Rock Head
- Forretress — Sturdy / Shell Armor
- Mantine — HP 75

**0 / 3 were present on current main.**

### Gen III
Explicit locked changes:
- Swellow — Guts / Scrappy
- Pelipper — Keen Eye / Rain Dish
- Wailord — Water Veil / Pressure
- Armaldo — Battle Armor / Swift Swim
- Huntail — 55/114/105/84/75/52

**0 / 5 were present on current main.**

### Gen IV
Explicit locked changes:
- Vespiquen — Pressure / Swarm
- Skuntank — White Smoke / Aftermath

**0 / 2 were present on current main.**

### Light Enrichment total

Across Generations I–IV, **17 / 17 explicit locked Light Enrichment changes were absent from main** before recovery.

A dedicated recovery PR restores all 17 and validates exact agreement with the approved values.

### Classification

**MISSING IMPLEMENTATION — SYSTEMATIC**

This is no longer an isolated omission. The entire explicit Light Enrichment change set failed to propagate into the canonical source state.

---

## 1E. Pass B Role Repair — Gen II — COMPLETE

The approved Gen II role-repair block contains 14 species.

Current-main reconciliation found:
- Xatu, Qwilfish, Octillery — correctly unchanged restraint cases
- Ledian — correct
- Delibird — correct
- **9 / 14 species missing locked Pass B changes**

Missing and recovered:
- Furret
- Noctowl
- Ariados
- Sunflora
- Girafarig
- Dunsparce
- Magcargo
- Corsola
- Stantler

After recovery, the complete Gen II role-repair block matches **14 / 14, 0 mismatches**.

### Classification

**MISSING IMPLEMENTATION — CONFIRMED AND PATCHED**

---

## 1F. Pass B Role Repair — Gen III — COMPLETE

The Gen III role-repair design consists of:
- 10-species priority block
- 18-species remainder block

### Priority block

**All 10 / 10 explicit role-repair changes were absent from main:**
- Delcatty
- Plusle
- Minun
- Volbeat
- Illumise
- Castform
- Kecleon
- Tropius
- Chimecho
- Luvdisc

### Remaining block

Of the 11 species with explicit stat changes:
- 7 were already correct
- **4 were missing:** Spinda, Lunatone, Solrock, Whiscash

The 7 explicit restraint species in the remainder correctly remained unchanged.

### Result

**14 Gen III role-repair records required recovery.**

The recovery branch has been checked against the locked values for all 14 restored records: **14 / 14 match, 0 mismatches**.

### Classification

**MISSING IMPLEMENTATION — CONFIRMED AND PATCHED**

---

## Current Pass B integrity picture

Confirmed missing approved species-core changes so far:
- Light Enrichment: **17**
- Gen II Role Repair: **9**
- Gen III Role Repair: **14**

**Total confirmed missing Pass B source changes recovered so far: 40.**

This establishes a systemic propagation failure between approved Pass B design and the later C3/current source snapshot.

---

## Next active block

**Gen IV Role Repair**, followed by the Gen I Role Repair reconciliation.

The audit remains source-history-first: current validators and C3 provenance are evidence of implementation state, not proof that all earlier approved Pass B decisions were propagated.


---

## 1D. Pass B Role Repair — recovery status

The reconciliation has now confirmed that missing Pass B implementation was widespread rather than isolated.

### Gen I

Recovered locked assignments for Beedrill, Pidgeot, Arbok, Wigglytuff, Parasect, Primeape, Poliwrath, Golem, Rapidash, Hypno, and Marowak.

The intended restraint/unchanged cases inspected alongside them remain consistent with the surviving design evidence.

### Gen II

Nine locked assignments were missing. After recovery the complete 14-species role-repair block matches the approved design.

### Gen III

Fourteen locked assignments were missing. After recovery all 21 explicit non-restraint assignments checked against surviving design evidence match; the seven restraint cases remain intentionally unchanged.

### Gen IV

Confirmed exact recovery has been applied for Kricketune, Rampardos, Bastiodon, all three Wormadam cloaks, Pachirisu, Purugly, Chatot, and Carnivine.

Probopass, Dusknoir, Lopunny, and the five restraint cases were already correct.

Mothim, Cherrim, and Lumineon remain **UNPROVEN / PENDING EXACT SOURCE RECOVERY**. Surviving evidence establishes their intended BST/role and some key stats, but not every stat field. They must not be guessed.

---

# 2. Evolution methods and timing — first reconciliation block

The strongest surviving Pass A evidence establishes the global rule that trade and non-stone evolution-item requirements were removed, while genuine evolution stones and meaningful natural conditions remain.

The following current-source evolution records were checked directly and match the locked design:

- Kadabra -> Alakazam: Lv36
- Machoke -> Machamp: Lv36
- Graveler -> Golem: Lv36
- Haunter -> Gengar: Lv36
- Onix -> Steelix: Lv35
- Scyther -> Scizor: Lv38
- Seadra -> Kingdra: Lv42
- Electabuzz -> Electivire: Lv42
- Magmar -> Magmortar: Lv42
- Rhydon -> Rhyperior: Lv52
- Porygon -> Porygon2: Lv30
- Porygon2 -> Porygon-Z: Lv45
- Dusclops -> Dusknoir: Lv45
- Gligar -> Gliscor: Lv38 at night
- Sneasel -> Weavile: Lv38 at night
- Poliwhirl: Lv35 stat split, Politoed when SpA > Atk and Poliwrath otherwise
- Slowpoke: Lv37 stat split, Slowking when SpD > Def and Slowbro otherwise
- Clamperl: Lv35 attack/special-attack split
- Pupitar -> Tyranitar: Lv50
- Snorunt -> Glalie: Lv42; female Snorunt -> Froslass via Dawn Stone
- Kirlia -> Gardevoir: Lv30; male Kirlia -> Gallade via Dawn Stone
- Nosepass -> Probopass: magnetic-field level-up
- Roselia -> Roserade: Shiny Stone
- Feebas -> Milotic: Beauty evolution retained

### Classification

**MATCH — first evolution reconciliation block**

No correction is required for these evolution records.
