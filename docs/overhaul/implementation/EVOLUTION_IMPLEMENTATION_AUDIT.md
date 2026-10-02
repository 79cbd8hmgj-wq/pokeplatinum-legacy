# Evolution Implementation Audit

| Item | Value |
|---|---|
| Starting main SHA | `3b7b843e78ae3afcbd64c475816bfd4f3e83dc79` (PR #13 C1 + PR #14 C2 present) |
| Implementation branch | `claude/evolution-overhaul-wotzl1` |
| Manifest | `docs/overhaul/implementation/evolution_manifest.json` |
| Evolution-bearing species | 229 |
| Total evolution edges | 246 |
| Vanilla-kept edges (VANILLA_KEEP) | 201 |
| Locked, already matching vanilla (LOCKED_KEEP) | 24 |
| **Changed edges (LOCKED_CHANGED)** | **20** across 19 species tables (Slowpoke's table is also re-ordered for precedence; its Slowbro edge is unchanged) |
| Unresolved authority | 1 — Happiny → Chansey (held Oval Stone), left vanilla; see `EVOLUTION_RECOVERY_AUDIT.md` |

## Changed evolutions

| # | Species | Final evolution | Was (vanilla) | Authority key |
|---|---|---|---|---|
| 1 | SPECIES_CLAMPERL | SPECIES_HUNTAIL: `EVO_LEVEL_ATK_GT_SPATK 35` | `EVO_TRADE_WITH_HELD_ITEM ITEM_DEEPSEATOOTH` | STAT_BRANCH |
| 2 | SPECIES_CLAMPERL | SPECIES_GOREBYSS: `EVO_LEVEL_SPATK_GE_ATK 35` | `EVO_TRADE_WITH_HELD_ITEM ITEM_DEEPSEASCALE` | STAT_BRANCH |
| 3 | SPECIES_DUSCLOPS | SPECIES_DUSKNOIR: `EVO_LEVEL 45` | `EVO_TRADE_WITH_HELD_ITEM ITEM_REAPER_CLOTH` | ITEM_TRADE_REPLACEMENT |
| 4 | SPECIES_ELECTABUZZ | SPECIES_ELECTIVIRE: `EVO_LEVEL 42` | `EVO_TRADE_WITH_HELD_ITEM ITEM_ELECTIRIZER` | ITEM_TRADE_REPLACEMENT |
| 5 | SPECIES_GLIGAR | SPECIES_GLISCOR: `EVO_LEVEL_NIGHT 38` | `EVO_LEVEL_WITH_HELD_ITEM_NIGHT ITEM_RAZOR_FANG` | NIGHT_LEVEL |
| 6 | SPECIES_GRAVELER | SPECIES_GOLEM: `EVO_LEVEL 36` | `EVO_TRADE` | TRADE_REPLACEMENT_KANTO |
| 7 | SPECIES_HAUNTER | SPECIES_GENGAR: `EVO_LEVEL 36` | `EVO_TRADE` | TRADE_REPLACEMENT_KANTO |
| 8 | SPECIES_KADABRA | SPECIES_ALAKAZAM: `EVO_LEVEL 36` | `EVO_TRADE` | TRADE_REPLACEMENT_KANTO |
| 9 | SPECIES_MACHOKE | SPECIES_MACHAMP: `EVO_LEVEL 36` | `EVO_TRADE` | TRADE_REPLACEMENT_KANTO |
| 10 | SPECIES_MAGMAR | SPECIES_MAGMORTAR: `EVO_LEVEL 42` | `EVO_TRADE_WITH_HELD_ITEM ITEM_MAGMARIZER` | ITEM_TRADE_REPLACEMENT |
| 11 | SPECIES_ONIX | SPECIES_STEELIX: `EVO_LEVEL 35` | `EVO_TRADE_WITH_HELD_ITEM ITEM_METAL_COAT` | ITEM_TRADE_REPLACEMENT |
| 12 | SPECIES_POLIWHIRL | SPECIES_POLITOED: `EVO_LEVEL_SPATK_GT_ATK 35` | `EVO_TRADE_WITH_HELD_ITEM ITEM_KINGS_ROCK` | STAT_BRANCH |
| 13 | SPECIES_PORYGON | SPECIES_PORYGON2: `EVO_LEVEL 30` | `EVO_TRADE_WITH_HELD_ITEM ITEM_UPGRADE` | ITEM_TRADE_REPLACEMENT |
| 14 | SPECIES_PORYGON2 | SPECIES_PORYGON_Z: `EVO_LEVEL 45` | `EVO_TRADE_WITH_HELD_ITEM ITEM_DUBIOUS_DISC` | ITEM_TRADE_REPLACEMENT |
| 15 | SPECIES_PUPITAR | SPECIES_TYRANITAR: `EVO_LEVEL 50` | `EVO_LEVEL 55` | LEVEL_RETUNE |
| 16 | SPECIES_RHYDON | SPECIES_RHYPERIOR: `EVO_LEVEL 52` | `EVO_TRADE_WITH_HELD_ITEM ITEM_PROTECTOR` | ITEM_TRADE_REPLACEMENT |
| 17 | SPECIES_SCYTHER | SPECIES_SCIZOR: `EVO_LEVEL 38` | `EVO_TRADE_WITH_HELD_ITEM ITEM_METAL_COAT` | ITEM_TRADE_REPLACEMENT |
| 18 | SPECIES_SEADRA | SPECIES_KINGDRA: `EVO_LEVEL 42` | `EVO_TRADE_WITH_HELD_ITEM ITEM_DRAGON_SCALE` | ITEM_TRADE_REPLACEMENT |
| 19 | SPECIES_SLOWPOKE | SPECIES_SLOWKING: `EVO_LEVEL_SPDEF_GT_DEF 37` | `EVO_TRADE_WITH_HELD_ITEM ITEM_KINGS_ROCK` | STAT_BRANCH |
| 20 | SPECIES_SNEASEL | SPECIES_WEAVILE: `EVO_LEVEL_NIGHT 38` | `EVO_LEVEL_WITH_HELD_ITEM_NIGHT ITEM_RAZOR_CLAW` | NIGHT_LEVEL |

Poliwrath (Water Stone) and Slowbro (Lv37) are unchanged edges inside changed tables.  Edge order in `slowpoke`: Slowking (SpD > Def) first, then Slowbro.

## Engine methods added (appended; vanilla IDs 0–26 untouched)

| ID | Method | Semantics (level gate is `param <= level`) |
|---|---|---|
| 27 | `EVO_LEVEL_SPATK_GT_ATK` | SpA **>** Atk |
| 28 | `EVO_LEVEL_SPATK_GE_ATK` | SpA **>=** Atk (tie included) |
| 29 | `EVO_LEVEL_ATK_GT_SPATK` | Atk **>** SpA |
| 30 | `EVO_LEVEL_SPDEF_GT_DEF` | SpD **>** Def |
| 31 | `EVO_LEVEL_NIGHT` | `IsNight()`; no held item |

Five new methods in total.  Files: `generated/evolution_methods.txt` (appended lines only), `src/pokemon.c` (new `case`s inside `Pokemon_GetEvolutionTargetSpecies`, additions only),
`tools/dataproc/src/speciesproc.c` (param handler cases), `docs/datafiles/pokemon.md` (parameter doc).  The validator proves IDs 0–26 are byte-for-byte the vanilla order.

The engine returns the **first** eligible entry of a species' list, so branch precedence is by array order.

## Audit results

| Check | Result |
|---|---|
| No-trade audit (whole #001–#493 table) | PASS — no `EVO_TRADE` / `EVO_TRADE_WITH_HELD_ITEM` remains |
| No-held-item audit | PASS with one recorded exception: Happiny → Chansey `EVO_LEVEL_WITH_HELD_ITEM_DAY` (UNRESOLVED_AUTHORITY, see above). `EVO_LEVEL_WITH_HELD_ITEM_NIGHT` is gone. |
| No-non-stone-item audit | PASS — every `EVO_USE_ITEM*` consumes one of the 9 whitelisted Gen IV stones (Fire, Water, Thunder, Leaf, Moon, Sun, Shiny, Dusk, Dawn) |
| Branch exhaustiveness | PASS — Clamperl exactly-one over all 4-stat orderings/ties at Lv34–36; Slowpoke first-match gives Slowking iff SpD > Def else Slowbro; Poliwhirl Politoed iff SpA > Atk (Poliwrath only by stone); Tyrogue exactly-one (>, =, <); Gligar/Sneasel night × level |
| Comparison semantics | Static test parses `src/pokemon.c` for each new case (operator and operands) and unit-tests ties |
| C3 timing cross-check | `timing_crosscheck.py`: 10 C3-cited levels all agree with the manifest; 0 conflicts; no learnset edited. Per-evolution table printed by the script |
| Scope audit | `scope_audit_evolutions.py`: 0 out-of-scope files; species data files differ only in `evolutions`; 0 deletions in engine source |
| One-save achievability (static) | No final evolution needs trade, a second DS, WFC, another game or a nonexistent item. Level/friendship/time/location/gender/move/party/Beauty conditions are in-game. Stone evolutions need stones; Moon/Sun Stone currently have only Underground sources in vanilla — stone access is owned by the later item/economy phase ("reliable evolution-stone access"), not changed here. Happiny→Chansey needs a held Oval Stone (obtainable) pending the unresolved decision. |
| Kadabra / Everstone note | `Pokemon_GetEvolutionTargetSpecies` still exempts Kadabra from the Everstone block (vanilla, because Kadabra was a trade evolution). Kadabra now level-evolves, so an Everstone does not stop it. Left untouched (out of scope); flagged for the user. |

## Regression suite (all on this branch)

| Validator | Result |
|---|---|
| `validate_evolutions.py` | PASS (0 failures; 1 recorded UNRESOLVED note) |
| `test_validate_evolutions.py` | 18 tests OK (mutation cases listed in the PR) |
| `scope_audit_evolutions.py` | clean |
| `tools/overhaul/moves/validate_c1.py` | OK (0 problems, 82 edits) |
| `tools/overhaul/moves/test_validate_c1.py` | 24/24 rejecting, 4/4 forward-compatible |
| `tools/overhaul/c2/validate_c2.py` | OK (0 problems) — also covers the TM compatibility manifest and created-move plumbing it consumes |
| `tools/overhaul/c2/test_validate_c2.py` | 76/76 rejecting, 3/3 forward-compatible |
| `tools/overhaul/availability/validate_availability.py` | 0 failures, 0 warnings |
| `tools/overhaul/availability/test_validators.py` | 12/12 ordinary + 25/25 special-acquisition mutations detected |
| `tools/overhaul/availability/special_verify.py` | exit 0 |
| C1 / C2 / special-acquisition `scope_audit*` scripts | These audit the diff against *their own* historical base commits, so they report violations on any later PR (the special-acquisition one already reports 502 on untouched main); not applicable to this PR and not weakened. |
| `tools/overhaul/recover_c3h_ledgers.py` | runs; ledgers recovered |

No existing validator needed changes.

## Builds

| Revision | Result |
|---|---|
| US Platinum Rev 0 | PENDING_CI |
| US Platinum Rev 1 | PENDING_CI |

(A ROM build needs the Metroskrew toolchain and is verified by the `build` GitHub Actions workflow; it could not be run in this session's container.)

## Runtime status

**DEFERRED TO FINAL OVERHAUL PLAYTEST.**  No emulator work was performed.
