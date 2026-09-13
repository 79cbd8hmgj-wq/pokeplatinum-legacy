# Pokémon Platinum Overhaul — Evolution System

> **Design status: LOCKED**
> **Implementation status: NOT YET CANONICALIZED/APPLIED AS A COMPLETE SYSTEM**
> **Recovery status: global rules and many exact decisions recovered; original locked #001–#493 Pass A master workbook is not currently checked into the repo.**

## Important status distinction

The evolution overhaul is **not undesigned future work**.

Pass A explicitly covered **Identity & Evolution** across all #001–#493 and was later consolidated into a locked 493-species master containing **50 consolidated type/evolution decisions** plus global evolution rules.

What remains is:

1. reconstruct/check in the complete machine-readable evolution manifest from the locked Pass A authority/current downstream evidence;
2. map those locked decisions to Platinum's source evolution methods;
3. implement and validate them.

Do not redesign the evolution system from scratch.

## Final global evolution rules

These rules supersede earlier proposals that used direct non-stone items or held evolution items.

### 1. No trade evolutions

No Pokémon may require trading, a second DS, or another game to evolve.

### 2. Evolution stones are the only evolution items

- No held-item evolutions.
- No direct use of Protector, Electirizer, Magmarizer, Reaper Cloth, Up-Grade, Dubious Disc, Razor Fang, Razor Claw, Metal Coat, King's Rock, Dragon Scale, Deep Sea Tooth, or Deep Sea Scale as evolution requirements.
- Genuine evolution stones remain valid.
- Non-stone items with battle value may remain as battle items but lose their evolution function.
- Pure evolution-only non-stone items may be removed from ordinary reward/shop progression where they serve no remaining purpose.

### 3. Natural conditions replace removed item/trade gates

Approved condition families include:

- level;
- stats;
- friendship;
- time of day;
- location;
- gender;
- known move;
- party condition;
- other existing natural evolution conditions where they preserve species identity.

### 4. Preserve distinctive evolutions when they add identity rather than friction

Examples intentionally retained include:

- Wurmple's split;
- Shedinja's special evolution;
- Feebas → Milotic via Beauty, with Beauty/Feebas acquisition made practical;
- Sinnoh location evolutions where appropriate;
- genuine evolution-stone branches;
- Tyrogue's Attack/Defense split.

## Recovered locked altered evolutions

The following exact rulings are recovered from the locked Pass A/C3 history and should be treated as design authority unless a later canonical source explicitly supersedes them.

| Evolution | Locked method |
|---|---|
| Kadabra → Alakazam | Lv. 36 |
| Machoke → Machamp | Lv. 36 |
| Graveler → Golem | Lv. 36 |
| Haunter → Gengar | Lv. 36 |
| Onix → Steelix | Lv. 35 |
| Scyther → Scizor | Lv. 38 |
| Seadra → Kingdra | Lv. 42 |
| Electabuzz → Electivire | Lv. 42 |
| Magmar → Magmortar | Lv. 42 |
| Rhydon → Rhyperior | Lv. 52 |
| Porygon → Porygon2 | Lv. 30 |
| Porygon2 → Porygon-Z | Lv. 45 |
| Dusclops → Dusknoir | Lv. 45 |
| Gligar → Gliscor | Lv. 38 at night |
| Sneasel → Weavile | Lv. 38 at night |
| Poliwhirl → Politoed | Lv. 35 with SpA > Atk |
| Slowpoke → Slowking | Lv. 37 with SpD > Def |
| Clamperl → Huntail | Lv. 35 with Atk > SpA |
| Clamperl → Gorebyss | Lv. 35 with SpA ≥ Atk |
| Pupitar → Tyranitar | Lv. 50 |
| Snorunt → Glalie | Lv. 42 |
| Female Snorunt → Froslass | Dawn Stone |
| Kirlia → Gardevoir | Lv. 30 |
| Male Kirlia → Gallade | Dawn Stone |
| Nosepass → Probopass | Level in Mt. Coronet |
| Roselia → Roserade | Shiny Stone |

Tyrogue retains its vanilla three-way Attack/Defense split.

## No-incense breeding/evolution-family rule

Pass A also documented cross-generation baby families under a **no-incense breeding rule**. Examples specifically cited include Azurill, Wynaut, Bonsly, and Mantyke.

This interacts with the later breeding port and must be preserved when the breeding system is canonicalized.

## Learnset synchronization dependency

C3 explicitly synchronized learnsets around altered evolution levels. Therefore evolution implementation must not casually retune these levels without reopening C3 timing decisions.

Recovered examples used by C3 include:

- Alakazam Lv36;
- Machamp Lv36;
- Golem Lv36;
- Gengar Lv36;
- Steelix Lv35;
- Scizor Lv38;
- Electivire Lv42;
- Kingdra Lv42;
- Porygon2 Lv30;
- Porygon-Z Lv45.

Changing these levels would potentially invalidate locked learnset timing and requires an explicit design amendment.

## Superseded evolution concepts

The following older concepts are **not authority**:

- trade-with-item → direct item use;
- trade-with-item → hold item + level;
- using Metal Coat/King's Rock/Dragon Scale/etc. as evolution requirements;
- the earliest provisional trade-evolution level suggestions where later Pass A/C3 values differ.

The final global rule is:

> **Evolution stones are the only evolution items. No trade or held non-stone item is required for evolution.**

## Remaining recovery/implementation task

The historical locked Pass A master contained **50 consolidated type/evolution decisions** across #001–#493. The original workbook itself is not currently in the repository.

Before implementation is called complete, Claude should:

1. generate a current-source #001–#493 evolution table;
2. overlay all recovered locked Pass A evolution decisions;
3. recover any remaining entries from surviving Pass A project history rather than inventing them;
4. produce `docs/overhaul/implementation/evolution_manifest.json`;
5. verify no decision conflicts with locked C3 evolution timing;
6. implement against Platinum evolution tables/logic with before-state guards;
7. build Rev 0 and Rev 1;
8. verify every evolution is achievable in one save.

Until the 50-decision manifest is reconstructed, the task is **manifest recovery + implementation mapping**, not new evolution design.
