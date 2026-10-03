# Pokémon Platinum Overhaul — Current Status

Last verified against repository/project history: 2026-10-03.

## Executive status

- **Design:** Pokémon/move design through C3 is closed.
- **C2.5E created moves:** IMPLEMENTED + L2 BUILD VERIFIED on `main`.
- **C3H species + TM compatibility:** IMPLEMENTED + L2 BUILD VERIFIED on `main`.
- **C1 existing-move rebalance:** LOCKED and **IMPLEMENTED (source + validator verified; Rev 0/Rev 1 build verification via CI; battle runtime QA pending)** — 82/82 edits applied on branch `claude/c1-move-rebalance-implementation-4l7umd`, see `implementation/C1_IMPLEMENTATION_AUDIT.md`.
- **Evolution (Pass A):** design **LOCKED / CANONICALIZED**; implementation **IMPLEMENTED (22 changed edges + 6 appended engine methods; source + validator + mutation tests verified; Rev 0/Rev 1 build via CI)**; runtime **DEFERRED TO FINAL OVERHAUL PLAYTEST**. Happiny → Chansey is explicitly approved as **Lv20 during daytime, no Oval Stone**. Manifest: `implementation/evolution_manifest.json`; audit: `implementation/EVOLUTION_IMPLEMENTATION_AUDIT.md`.
- **World/#001–#493 ordinary availability:** IMPLEMENTED on `main` via PR #10; manifests/validators landed; Rev 0 + Rev 1 CI build verified; runtime availability QA pending. The 28 reserved special-acquisition families are resolved by the follow-up special-acquisition pass (see `implementation/SPECIAL_ACQUISITION.md`).
- **Known design blockers:** 0.
- **C2 TM/HM mechanics (HM battle rework, reusable TMs, TM acquisition/economy):** IMPLEMENTED (source + validator verified; Rev 0/Rev 1 build via CI on the C2 PR); see `implementation/C2_MECHANICS_IMPLEMENTATION_AUDIT.md`. Focused runtime QA pending.
- **EXP/economy port:** IMPLEMENTED (conserved 60/40 team EXP, participant-only EVs, prize/price cleanup, free Move Reminder, half-cost tutors, Veilstone evolution-stone vendor, postgame Rare Candy; source + validator + mutation tests; Rev 0/Rev 1 build via CI); runtime **DEFERRED TO FINAL OVERHAUL PLAYTEST**. Audit: `implementation/economy/ECONOMY_IMPLEMENTATION_AUDIT.md`.
- **Poké Ball rebalance:** IMPLEMENTED and merged (PR #17; source + validator verified, build via CI; capture runtime QA pending).
- **Breeding 2.0:** IMPLEMENTED and merged (PR #18; source + host-compiled rules harness + validator + mutation tests verified; Rev 0/Rev 1 build via CI); **runtime breeding QA PENDING — not VERIFIED**. Audit/manifests: `implementation/breeding/`. Egg-move legality audit: 0 unreachable / 0 pending after the owner ruling below.
- **Trainer overhaul (D1):** **IMPLEMENTED and merged** (PR #19, merge commit `08092189`; source + validator + Rev 0/Rev 1 CI build success, PR head `1497736a`) (393 records changed: 8 Gyms, 33 Rival, 11 Galactic, Elite Four, Cynthia, 13 rematches, 332 ordinary/ordinary-rematch via archetype rules); trainer runtime QA **PENDING — not VERIFIED**. Manifests/report: `implementation/trainers/`; validator: `tools/overhaul/trainers/validate_trainers.py`.
- **Legendary/Mythical events (D5):** **IMPLEMENTED and merged** (PR #20, merge commit `98f9cbdf`; source + validator + dual-revision builds); runtime event QA **PENDING — not VERIFIED**. All 35 Legendary/Mythical species #001–#493 have an in-save path: native retry-safe Sinnoh events, Rotom/Darkrai/Shaymin/Arceus without distribution gates, Manaphy Egg gift (+ Phione breeding), Regis/Regigigas without the event Regigigas, 14 renewable post-Hall-of-Fame legacy habitats (1%/2% roll in `src/overlay006/wild_encounters.c`), Mew/Celebi/Jirachi/Deoxys retry-safe statics. Manifests/report: `implementation/events/`; validator: `tools/overhaul/validate_legendary_availability.py`. The availability phase's Rotom special-acquisition verifier was updated because D5 removed `DISTRIBUTION_EVENT_ROTOM` (Secret Key alone gates the form room).
- **Battle Frontier / postgame (D6):** **IMPLEMENTED and merged** (PR #21, merge commit `19cbadaa`; source + validator + mutation tests; Rev 0/Rev 1 CI build recorded on the PR); runtime QA **PENDING — not VERIFIED**. Exact 2x BP at every payout point (Tower/Factory/Castle/Hall/Arcade round + roulette + Hall record keeper; Castle Points untouched), locked TM BP prices confirmed already live (no shop edit), 15 targeted Frontier set fixes + 17 Hall type-pool retype corrections (Brains audited, 0 edits), Battleground proprietor reshuffle without calendar wait, Survival Area Rival daily (weekend gate removed), Print milestone rewards (+10/+30 BP per facility; all-Silver +50 BP + PP Max; all-Gold +100 BP + Master Ball; retry-safe on full Bag), Fight Area/League/Rival rematch trainer references audited. Manifests/report: `implementation/postgame/`; validator: `tools/overhaul/postgame/validate_postgame.py`.
- **Final integration QA (D7):** **STATIC/FRAMEWORK COMPLETE and merged via PR #22**; master validator, completion graphs, runtime matrix and QA reports are on `main`. Project state remains **CORE 1.0 SOURCE-COMPLETE — RUNTIME QA PENDING** (not VERIFIED, not a release candidate); see `qa/QA_INDEX.md`, `qa/MASTER_VALIDATION_REPORT.md`, `qa/RELEASE_BLOCKERS.md`.
- **Mystery Egg starter (D8):** chooser + random starter **IMPLEMENTED** (source + validator + mutation suite + host-compiled exhaustive 0–99 test); **native hatch presentation DEFERRED / DISABLED** pending a runtime-safe implementation; runtime **PENDING — not VERIFIED** (OP-* cases NOT RUN). Three identical Mystery Egg preview sprites inside an otherwise vanilla chooser lifecycle (no species/name/type/cry before confirmation); one weighted 13-species draw (`LCRNG_Next() % 100`, ranges 0–2/3–5/6–8 Gen I, 9 Pikachu, 10–19 … 90–99 Gen II–IV) performed once in `ScrCmd_SaveChosenStarter` and persisted to the existing `VAR_PLAYER_STARTER`; `ChooseStarterData` carries `options` only. Route 201 uses the vanilla award path (`StartChooseStarterScene`, `SaveChosenStarter`, `ReturnToField`, `FadeScreenIn`, `WaitFadeScreen`, `GetPlayerStarterSpecies`, `GivePokemon` Lv5); `GiveMysteryStarterEgg` / `HatchMysteryStarterEgg` code is retained but no longer called. The three Rival campaigns are preserved by a pure branch helper (`GetPlayerStarterBranch`), 19 script call sites converted; ordinary Breeding 2.0 hatch (Lv1, TV segment) unchanged. The Mystery Egg black-screen blocker (C-1) is *expected* to be removed by returning to the vanilla award flow but is **NOT VERIFIED** until runtime testing resumes. Manifest/audit/report: `implementation/opening/`; validator: `tools/overhaul/validate_mystery_starter.py`. Project state is still **CORE 1.0 SOURCE-COMPLETE — RUNTIME QA PENDING**, not a release candidate.

## Mainline implementation evidence

### Created moves

Commit `071b8c7976801e64af5296f30b7437d7da2d8632` — **Implement Platinum overhaul custom moves and mod-aware CI**

Implements all 22 created moves, IDs 468–489, move-table plumbing / `MAX_MOVES = 490`, text/scripts/animations, Resonant Slash sound registration, Star Jab punching registration, Magnet Volley exact-three-hit support, and a Rev 0/Rev 1 CI matrix.

GitHub Actions run `33981291318`: **SUCCESS**.

Status: source implemented; L2 build verified; focused L4 runtime behavior still pending.

### Species + TM compatibility

Commit `8a74452654e1552b78bfb329afcb351a2caec5cf` — **Apply C3H species and TM compatibility overhaul**

Applies the TM21/TM78 compatibility rebuild, explicit compatibility additions, 225 guarded C3 species operations, and final Torkoal/Seviper corrections.

GitHub Actions run `33995072848`: **SUCCESS**.

Status: source implemented; L2 build verified; runtime/campaign QA still pending.

## Canonical documentation

Historical: the canonical documentation landed on `main`; branch `overhaul/canonical-docs` / PR #8 are no longer working targets (`main` is the source of truth).

Historical recovery branches:

- `overhaul/c3h-species-compat`
- `overhaul/c3h-ledger-archive`

They are provenance sources, not current implementation targets.

## Completion matrix

| Area | Design | Implementation | Verification |
|---|---|---|---|
| Core project identity | LOCKED | n/a | n/a |
| Types/stats/abilities/roles | LOCKED | IMPLEMENTED through C3H | L2 build |
| Existing move rework (C1) | LOCKED / CANONICALIZED | IMPLEMENTED (source/validator verified; CI build; runtime QA pending) | validators pass; see C1_IMPLEMENTATION_AUDIT.md |
| Created moves (C2.5E) | LOCKED | IMPLEMENTED | L2 build |
| C3 learnsets/species edits | LOCKED | IMPLEMENTED | L2 build |
| TM21/TM78 compatibility | LOCKED | IMPLEMENTED | L2 build |
| Retype compatibility additions | LOCKED | IMPLEMENTED | L2 build |
| Reusable TMs | LOCKED | IMPLEMENTED | source + validator verified; CI build; runtime QA pending |
| HM battle rework | LOCKED | IMPLEMENTED | source + validator verified; CI build; runtime QA pending |
| TM acquisition/economy | LOCKED | IMPLEMENTED (TM21/TM78 item assignment, Game Corner + Frontier prices, duplicate-vendor guard) | source + validator verified; CI build; runtime QA pending |
| Tutor consolidation | LOCKED | baseline retained | audit pending |
| Egg-move consolidation | LOCKED | baseline retained | audit pending |
| Evolution-method overhaul | LOCKED / CANONICALIZED | IMPLEMENTED (22 changed edges; methods 27–32 appended; zero unresolved authority) | source + validator + mutation tests + dual-revision CI build; runtime DEFERRED TO FINAL OVERHAUL PLAYTEST |
| World/#001–#493 availability — ordinary wild distribution | APPROVED ARCHITECTURE | IMPLEMENTED on `main` via PR #10 | L2 dual-revision CI build + manifest/validator evidence; runtime pending |
| World/#001–#493 availability — special acquisitions (starters, fossils, Spiritomb, Rotom, Tyrogue, Happiny, Eevee, Porygon, Riolu, Castform, Feebas) | LOCKED/RESERVED BY OWNING SPECS WHERE APPLICABLE | IMPLEMENTED on main via PR #11 | source + L2 build + validator (S1–S5 + 25 mutation cases); runtime pending |
| Trainer overhaul (D1) | LOCKED | IMPLEMENTED and merged (PR #19; source + validator + dual-revision CI build) | validator 0 errors + 19 mutation tests; cross-system validators pass; runtime trainer QA pending; see `implementation/trainers/TRAINER_VALIDATION_REPORT.md` |
| Economy/EXP port | LOCKED | IMPLEMENTED | source + validator + mutation tests + dual-revision CI build; runtime DEFERRED TO FINAL OVERHAUL PLAYTEST |
| Capture/Poké Ball port | LOCKED | IMPLEMENTED (merged, PR #17) | validators pass; CI build; runtime QA pending; see `capture/POKE_BALL_FEASIBILITY_AUDIT.md`, `tools/overhaul/pokeballs/` |
| Breeding 2.0 | LOCKED | IMPLEMENTED and merged (PR #18) | source + harness + validator verified; CI build; runtime QA pending; see `implementation/breeding/BREEDING_VALIDATION_REPORT.md` |
| Legendary/Mythical events (D5) | LOCKED | IMPLEMENTED and merged (PR #20) (source + validator + dual-revision builds) | validator 51/51 + 46 mutation cases + baseline; cross-system validators pass; runtime event QA pending; see `implementation/events/LEGENDARY_EVENT_VALIDATION_REPORT.md` |
| Battle Frontier/postgame (D6) | LOCKED | IMPLEMENTED (source + validator + dual-revision build) | validator 119 checks + 12 mutation cases; cross-system validators pass; runtime Frontier/rematch/Print QA pending — not VERIFIED; see `implementation/postgame/POSTGAME_VALIDATION_REPORT.md` |
| Battle Frontier/postgame merge record | n/a | merged via PR #21 (`19cbadaa`) | see row above |
| Full QA/release (D7) | LOCKED | STATIC/FRAMEWORK COMPLETE and merged via PR #22; runtime campaign/493 run NOT performed | **CORE 1.0 SOURCE-COMPLETE — RUNTIME QA PENDING**; not VERIFIED / not a release candidate |
| Mystery Egg starter (D8) | LOCKED | not implemented | Design + Claude implementation plan committed on `design/mystery-egg-starter`; runtime QA pending after implementation |

## C1 authority

C1 final audit contains exactly **82 edited existing moves**.

Canonical authority:

- human-readable: `moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`
- machine-readable: `implementation/c1_move_changes_manifest.json`
- membership/provenance: `implementation/c1_move_edit_membership_recovery.json`
- recovery evidence: `moves/C1_RECOVERED_BATCHES_SUPPLEMENT.md`

The machine manifest contains exactly **82 entries** and changes only listed fields.

### Final Batch 9F values

- Bind — 30 / 90 / 20
- Wrap — 30 / 90 / 20
- Fire Spin — 35 / 90 / 15
- Whirlpool — 35 / 90 / 15
- Sand Tomb — 35 / 90 / 15
- Clamp — 35 / 90 / 10
- Magma Storm — KEEP 120 / 70 / 5

Trapping duration/residual behavior is unchanged.

The previously surfaced Sand Tomb 50/95 value came from an unrelated Emerald move-rework spec and is **not Platinum C1 authority**.

### C1 implementation state

C1 is applied on the implementation branch (base `9034963728913416f2968b56f7dab8ac61b19c07`): 82/82 edits, guards in `implementation/c1_move_guards.json`, tooling in `tools/overhaul/moves/`. Battle runtime QA is still pending.

Next implementation procedure:

1. inspect current move files;
2. generate before-value/source guards;
3. apply `implementation/c1_move_changes_manifest.json`;
4. assert exact edit count = 82;
5. update Razor Wind's description alongside its effect reassignment;
6. semantic-diff the move table;
7. build Rev 0 and Rev 1;
8. record evidence in this file.

## Evolution authority

Evolution was part of **Pass A: Identity & Evolution**, not an undesigned future phase.

Canonical recovery entry:

`evolution/EVOLUTION_SPEC.md`

Final global rule:

> **Evolution stones are the only evolution items. No trade or held non-stone item is required for evolution.**

Recovered locked examples include:

- Kadabra/Machoke/Graveler/Haunter → Lv36 final evolutions;
- Onix → Steelix Lv35;
- Scyther → Scizor Lv38;
- Seadra → Kingdra Lv42;
- Electabuzz/Magmar → Lv42 final evolutions;
- Rhydon → Rhyperior Lv52;
- Porygon → Porygon2 Lv30 → Porygon-Z Lv45;
- Dusclops → Dusknoir Lv45;
- Gligar/Sneasel → Lv38 at night;
- Poliwhirl/Slowpoke/Clamperl branch logic uses stat comparisons;
- genuine stones, location evolutions, Beauty, Wurmple/Shedinja, and other identity-positive mechanics are retained.

The historical locked Pass A master contained **50 consolidated type/evolution decisions** (the typing decisions were implemented in earlier phases). The evolution subset was recovered and implemented: **22 changed edges** over 20 species tables, plus six appended engine methods (IDs 27–32). The original workbook remains reconstructed provenance rather than a checked-in artifact; recovery uses the canonical spec, surviving project history, the Emerald plan and C3 timing. Happiny → Chansey lacked surviving primary-source proof for the exact replacement, so the user explicitly approved **Lv20 during daytime, no Oval Stone** on 2026-10-02. See `implementation/EVOLUTION_RECOVERY_AUDIT.md` and `implementation/EVOLUTION_IMPLEMENTATION_AUDIT.md`.

## C3 provenance

Exact historical species payload:

`implementation/archive/c3h-apply-species-original.yml`

- historical commit: `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob: `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- ledger counts: `67 / 27 / 40 / 53 / 38 = 225`

Verifier/extractor:

`tools/overhaul/recover_c3h_ledgers.py`

These ledgers are provenance only. Do **not** reapply them over current main.

Final corrections visible on main:

- Banette: Shadow Ball 31; Cursed Stitch 38; Shadow Claw 42.
- Torkoal: Yawn 52; Heat Wave 55.
- Seviper: Sludge Bomb 55.

## Runtime QA deferred to final overhaul playtest

High-priority L4 checks:

- Resonant Slash sound/Soundproof interaction;
- Star Jab punching/Iron Fist interaction;
- Magnet Volley exactly 3 equal-power hits (`25 + 25 + 25` before normal modifiers);
- representative custom move effects/text/animations;
- Defog behavior once C2 HM work is implemented/audited;
- representative C3 evolution-timing and compatibility cases.

## Historical unresolved design item

`Dragon Swipe` is implemented as a finalized move, but recovered C3 documentation does not prove a final recipient.

Do not invent one. This is not a build blocker.

## Immediate next actions

1. Implement D8 Mystery Egg starter from `opening/MYSTERY_EGG_STARTER_SPEC.md` and `opening/MYSTERY_EGG_STARTER_IMPLEMENTATION_PLAN.md`.
2. Rerun the D7 master/static QA outputs after D8 lands, because the opening and Rival-branch assumptions will have changed.
3. Complete human/emulator runtime QA (`qa/RUNTIME_TEST_MATRIX.md`), the full campaign (`qa/FULL_CAMPAIGN_REPORT.md`), the 493 completion run (`qa/POKEDEX_493_COMPLETION_REPORT.md`) and save-import testing (`qa/SAVE_COMPATIBILITY_REPORT.md`) before VERIFIED / release-candidate status.

## Rule for future sessions

Do not reconstruct status from memory when this file answers the question. Update this file in the same branch/PR that materially changes project state.


## EXP / economy

Status: **IMPLEMENTED** (see `implementation/economy/ECONOMY_IMPLEMENTATION_AUDIT.md`; runtime DEFERRED TO FINAL OVERHAUL PLAYTEST)

Canonical authority:
- `docs/overhaul/economy/EXP_ECONOMY_SPEC.md`
- `docs/overhaul/economy/EXP_ECONOMY_IMPLEMENTATION_PLAN.md`

Key locks: Platinum-native EXP pool, conserved 60/40 team-wide distribution, Exp. Share as priority weighting without creating extra base EXP, participant-only EVs, targeted payout cleanup, lower healing/vitamin costs, free Move Reminder, half-cost shard tutors, reliable evolution-stone access, and postgame-only unlimited Rare Candy stock.


## Poké Ball rebalance

Status: **IMPLEMENTED — merged via PR #17 (runtime QA pending)**

Canonical authority:
- `docs/overhaul/pokeballs/POKE_BALL_REBALANCE_SPEC.md`
- `docs/overhaul/pokeballs/POKE_BALL_IMPLEMENTATION_PLAN.md`

Design locks include Quick 5x first-turn, Timer 4x by turn 10, Repeat 3.5x, Dusk 3x, Net 3.5x Water/Bug, Dive 4x water terrain, Heal 1.5x with healing preserved, and Nest Ball converted to a level-ratio specialist rather than introducing a new ball slot.


## Breeding 2.0

Status: **IMPLEMENTED — source + validator verified; Rev 0/Rev 1 build via CI; runtime breeding QA PENDING (not VERIFIED)**

Canonical authority:
- `docs/overhaul/breeding/BREEDING_SPEC.md`
- `docs/overhaul/breeding/BREEDING_IMPLEMENTATION_PLAN.md`

Started from `e2d73d33a702bc151ae283a1245ebf64575476ed`. Implemented: 100% Everstone (either parent, no gender restriction), four distinct inherited IVs (also fixes vanilla's repeatable-stat bug), six Power items, 80/20 ability slot, either-parent egg moves, no-incense babies (9), 128-step egg check, halved hatch cycles (454 edits, min 5), Veilstone 2F battle-item counter stocks Everstone ₽200 + six Power items ₽3,000. Engine rules live in `include/overlay005/breeding_rules.h` (host-testable); manifests/report in `implementation/breeding/`; validator `tools/overhaul/validate_breeding.py`.

Normalization: the 255/230-step constant in `Daycare_GetEggCycleLength` is the *hatch-cycle* length, not the egg-roll cadence, and is left unchanged (halving it would also quarter hatch time, contradicting spec #11). The egg roll (day-care step counter `& 0xff`) became `& 0x7f`.

Owner ruling applied (PR #18): the 9 egg moves orphaned by the no-incense change were migrated (Marill→Azurill: Light Screen, Present, Amnesia, Future Sight, Belly Drum, Perish Song, Supersonic, Aqua Jet; Snorlax→Munchlax: Fissure) and 5 donorless entries were removed (Cleffa Belly Drum, Igglybuff Perish Song, Geodude Mega Punch, Mankey Meditate, Shellder Take Down). No other egg-move/egg-group/learnset changes. Unresolved breeding blockers: 0.

## Legendary / Mythical events

Status: **IMPLEMENTED — source + validator + dual-revision builds; runtime event QA PENDING (not VERIFIED)**

Canonical authority:
- `docs/overhaul/events/LEGENDARY_MYTHICAL_SPEC.md`
- `docs/overhaul/events/LEGENDARY_MYTHICAL_IMPLEMENTATION_PLAN.md`

Key locks: see the availability section below (the earlier "internal migration chain" wording was superseded by the rare-habitat model).


## Battle Frontier / postgame

Status: **IMPLEMENTED** (D6; runtime QA pending — not VERIFIED). Record: `implementation/postgame/` (five manifests, `FRONTIER_SET_AUDIT.md`, `POSTGAME_VALIDATION_REPORT.md`); validator `tools/overhaul/postgame/validate_postgame.py`.

Canonical authority:
- `docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md`
- `docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_IMPLEMENTATION_PLAN.md`

Key locks: preserve native Frontier silver/gold streak milestones, double final BP awards, retain locked reduced TM BP prices while leaving ordinary non-TM BP prices intact, audit rather than rebuild Frontier sets, make Battleground rematches reshuffleable without calendar waiting, make Rival rematches daily rather than weekend-only, and add one-time Silver/Gold Print BP/item milestone rewards.


## Final integration / QA

Status: **LOCKED SPEC — D7 IN PROGRESS: CORE 1.0 SOURCE-COMPLETE — RUNTIME QA PENDING** (static master validation + completion graphs + QA framework landed; no runtime/campaign/493/save-import evidence yet, so NOT `VERIFIED` and NOT a release candidate). Index: `qa/QA_INDEX.md`; blockers: `qa/RELEASE_BLOCKERS.md`.

Canonical authority:
- `docs/overhaul/qa/FINAL_INTEGRATION_QA_SPEC.md`
- `docs/overhaul/qa/FINAL_INTEGRATION_QA_IMPLEMENTATION_PLAN.md`

Release gates are now defined for clean Rev 0/Rev 1 builds, subsystem validators, #001–#493 completion proof, evolution legality, progression simulation, runtime boss/event/frontier tests, full fresh-save campaign completion, save compatibility, release blockers, and legal patch packaging. The project may only be marked CORE 1.0 VERIFIED / RELEASE CANDIDATE when the evidence is recorded in-repo.

D7 evidence recorded so far (all static; see `qa/QA_INDEX.md`):

- Master validator `python3 tools/overhaul/validate_overhaul.py`: 18 validators + 13 mutation/regression suites, all PASS (`qa/MASTER_VALIDATION_REPORT.md`).
- Completion graphs: 493/493 species reachable in one save, 212/212 nonlegendary families with a pre-E4 entry, 0 trade/held-item/external dependencies, 0 event cycles, Arceus the terminal #493 capstone (`qa/POKEDEX_493_COMPLETION_REPORT.md`).
- Proven integration fix: Solar Petal contact flag (created-move manifest mismatch). Test-harness baselines for economy/trainers/postgame refreshed. No gameplay redesign.
- Progression simulation: model-flagged calibration items, unproven, no trainer/EXP change (`qa/PROGRESSION_SIMULATION_REPORT.md`, `qa/RELEASE_BLOCKERS.md` B-1).
- Runtime matrix: 120 cases × 2 revisions (103 D7 + 17 D8 `OP-*`), **0 PASS / 0 FAIL / 240 NOT RUN**; full campaign, 493 in-game run and save-import tests **not executed**.
- Builds: CI only; baseline `main` Rev 0/Rev 1 success; D7 PR run in `qa/BUILD_MATRIX.md`. No patch tooling exists in the repo, so no artifacts were produced (`qa/RELEASE_ARTIFACTS.md`).


## Legendary / Mythical availability

Status: **IMPLEMENTED — see "Legendary / Mythical events" above and `implementation/events/`; runtime QA PENDING (not VERIFIED)**

Canonical authority:
- `docs/overhaul/events/LEGENDARY_MYTHICAL_SPEC.md`
- `docs/overhaul/events/LEGENDARY_MYTHICAL_IMPLEMENTATION_PLAN.md`

Key locks: Sinnoh/Platinum-native legends retain native story/event treatment; Darkrai/Shaymin/Arceus/Rotom distribution gates are replaced by permanent in-game access; Manaphy becomes an in-save Canalave egg gift with Phione through breeding; Regis use Platinum's native ruins without event-Regigigas dependency; older Gen I–III legends become renewable 1–2% postgame habitat encounters; older Mythicals use lightweight retry-safe statics; Arceus is the #493 capstone after catching #001–#492.


## Availability implementation — merged PR #10

Merged as `f89dfc792efe5955acac89e07c866e9f98f6aa4a`.

Canonical implementation evidence:
- `docs/overhaul/implementation/AVAILABILITY_SOURCE_AUDIT.md`
- `docs/overhaul/implementation/AVAILABILITY_IMPLEMENTATION_REPORT.md`
- `docs/overhaul/implementation/availability_families.json`
- `docs/overhaul/implementation/encounter_zones.json`
- `docs/overhaul/implementation/wild_encounters.json`
- `docs/overhaul/implementation/special_systems.json`
- `tools/overhaul/availability/`

Implemented scope:
- E0–P0 ordinary land/cave distribution;
- required Surf / Old Rod / Good Rod distribution;
- dual-slot neutralization;
- Great Marsh before/after-Dex array unification;
- fixed fallback paths for Radar / swarm / Honey / Trophy Garden / Great Marsh species;
- guarded application and semantic-diff tooling;
- availability validators and mutation tests.

PR #10 deliberately does **not** implement its reserved special-acquisition families or Legendary/Mythical content.

Validation:
- branch-local availability validators: 0 failures / 0 warnings for the implemented ordinary-wild scope;
- mutation validator tests: 12/12 expected bad states rejected;
- GitHub Actions run `36907831401`: **SUCCESS** for US Rev 0 and US Rev 1;
- runtime/L4 encounter QA remains pending.


## Special acquisition closure (28 families)

Branch `claude/platinum-availability-impl-c651fe` (follow-up to PR #10). Canonical docs/data:
`implementation/SPECIAL_ACQUISITION.md`, `implementation/special_acquisitions.json`, `tools/overhaul/availability/special_verify.py`.

- 12 starters: Sandgem Lab assistant gifts (badges 2/3/4/5 for Sinnoh-unchosen/Kanto/Johto/Hoenn), per-starter flags, party-full retry.
- 7 fossils: Underground weights made Trainer-ID- and National-Dex-independent.
- Spiritomb: single-player ritual (counter from Underground mining, retry if uncaught); Rotom: no daily cap, Secret Key + form unlock on capture;
  Tyrogue/Happiny: Celestic Town Black Belt; Castform: Veilstone parasol woman; Feebas: four fixed tiles;
  Eevee/Porygon/Riolu: existing gifts verified unchanged.
- Nonlegendary families with a verified pre-E4 path: 212/212 (184 wild + 28 special). USER_DECISION_REQUIRED families: 0.
- Runtime/L4 QA pending. The nonlegendary world-availability phase is source/build/validator complete.


## Mystery Egg starter (D8)

Status: **LOCKED SPEC — awaiting implementation**

Canonical authority:
- `docs/overhaul/opening/MYSTERY_EGG_STARTER_SPEC.md`
- `docs/overhaul/opening/MYSTERY_EGG_STARTER_IMPLEMENTATION_PLAN.md`

Locked design:
- Route 201 presents three visually identical Mystery Eggs;
- all three positions use the same weighted draw;
- Bulbasaur/Charmander/Squirtle are 3% each;
- Pikachu is 1%;
- Chikorita/Cyndaquil/Totodile, Treecko/Torchic/Mudkip and Turtwig/Chimchar/Piplup are 10% each;
- species is rolled exactly once after confirmation and hidden until the hatch/reveal;
- starter enters play at level 5 before Barry's first battle;
- existing three Rival branches are preserved by species-category mapping (Grass→Turtwig branch, Fire→Chimchar branch, Water→Piplup branch, Pikachu→Piplup branch);
- ordinary Breeding 2.0 egg behavior and later starter availability remain unchanged.

Interim architecture (current): the egg presentation lives entirely inside the chooser; after returning to Route 201 the rolled species is awarded directly at Lv. 5 through the vanilla `GivePokemon` path. The native hatch cutscene (`GiveMysteryStarterEgg` / `HatchMysteryStarterEgg`) is DEFERRED / DISABLED until a runtime-safe implementation exists; its code remains in source but is not called. "Hidden until the hatch/reveal" above is therefore satisfied by hiding the species until the award message.

Because D8 is post-D7, the D7 static/master reports must be regenerated after implementation and release-candidate status remains blocked on runtime QA.
