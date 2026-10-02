# Pokémon Platinum Overhaul — Evolution System

> **Design status: LOCKED**
> **Design status (canonical): LOCKED / CANONICALIZED**
> **Implementation status: IMPLEMENTED** — 21 changed edges + 6 appended engine methods; manifest `implementation/evolution_manifest.json`.
> **Verification: source + validator + mutation tests + dual-revision (Rev 0 / Rev 1) build verified.**
> **Runtime: DEFERRED TO FINAL OVERHAUL PLAYTEST.**
> **Open items:** none (Happiny → Chansey recovered: Lv20, daytime, no item).
> **Provenance:** the original locked #001–#493 Pass A master workbook is not in the repo; the manifest was reconstructed from this spec, the Emerald port plan, C3 timing and git history (`implementation/EVOLUTION_RECOVERY_AUDIT.md`).

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

## Implementation (landed)

- Manifest: `docs/overhaul/implementation/evolution_manifest.json` (229 evolution-bearing species, 246 edges; 21 LOCKED_CHANGED, 24 LOCKED_KEEP, 201 VANILLA_KEEP, 0 UNRESOLVED_AUTHORITY).
- Engine methods appended (vanilla IDs 0–26 unchanged; IDs 27–32): 27 `EVO_LEVEL_SPATK_GT_ATK`, 28 `EVO_LEVEL_SPATK_GE_ATK`, 29 `EVO_LEVEL_ATK_GT_SPATK`, 30 `EVO_LEVEL_SPDEF_GT_DEF`, 31 `EVO_LEVEL_NIGHT`, 32 `EVO_LEVEL_DAY`.
- Branch rules: Clamperl Huntail = Atk > SpA, Gorebyss = SpA ≥ Atk; Poliwhirl→Politoed = SpA > Atk (Poliwrath stays Water Stone); Slowking = SpD > Def listed before the unchanged Lv37 Slowbro, so SpD ≤ Def → Slowbro (the engine takes the first eligible entry).
- Gligar/Sneasel evolve at Lv38 at night with no held item (`EVO_LEVEL_NIGHT`).
- Tooling: `tools/overhaul/evolution/` (`build_manifest.py`, `apply_evolutions.py`, `validate_evolutions.py`, `test_validate_evolutions.py`, `scope_audit_evolutions.py`, `timing_crosscheck.py`).
- Audits: `implementation/EVOLUTION_RECOVERY_AUDIT.md`, `implementation/EVOLUTION_IMPLEMENTATION_AUDIT.md`.

### Happiny → Chansey (resolved)

Recovered locked Pass A history: Happiny evolves into Chansey at **Lv20 during the daytime, with no held Oval Stone** (`EVO_LEVEL_DAY`, `IsNight() == FALSE && param <= level`).

### Kadabra and Everstone

The vanilla Kadabra exemption from the Everstone evolution block was removed, since Kadabra now evolves by level like any other species (Everstone blocks it).
