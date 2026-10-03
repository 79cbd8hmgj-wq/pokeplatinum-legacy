# Pokédex #001–#493 Completion Report (D7 Phase 3/16)

Authority: `FINAL_INTEGRATION_QA_SPEC.md` s4 and s16. Two separate things are recorded here and must not be conflated:

1. **Static reachability proof** (done): `tools/overhaul/qa/build_qa_graphs.py` over live source + locked manifests. A species counts only when a manifest-declared,
   validator-checked acquisition path reaches it (wild / scripted gift / D5 event / breeding / evolution). No save editing or Pokédex-bit injection is counted.
2. **In-game 493 completion run** (NOT EXECUTED): required before release; checklist and evidence fields below.

## 1. Static proof (generated from source)

Artifacts: `pokedex_493_graph.json` (all 493 species with acquisition source, band, evolution requirements, breeding dependency, external-dependency flags),
`evolution_graph.json` (246 edges), `event_dependency_graph.json`, `progression_gates.json`.

| Check | Result |
|---|---|
| Species reachable in one save (#001–#493) | **493 / 493** |
| Nonlegendary evolutionary families with a deterministic pre-Elite Four entry | **212 / 212** (184 wild + 28 special acquisition) |
| Nonlegendary families first available after Hall of Fame (P1) | **0** |
| Families whose only wild source is a bonus system or Super Rod | **0** (Unown: vanilla Solaceon Ruins table retained, documented) |
| Evolution edges using trade or held-item methods | **0** of 246 |
| Item evolutions using a non-stone item | **0** (all 26 stone edges use the 9 stones sold at Veilstone Dept. Store 2F, verified in live stock) |
| Move-known evolutions whose move the species cannot learn (level/tutor/egg) | **0** of 7 |
| External dependency flags (trade / WFC / multiplayer / another game / Slot-2) | **0** |
| Circular event dependencies | **0** |
| Arceus is the terminal capstone (#493) | **yes** — sole consumer of the "#001–#492 caught" gate; nothing depends on Arceus |
| Legendary/Mythical species with an in-save source | **35 / 35** (17 native/restored/breeding, 14 legacy habitats, 4 mythical statics) |

Scope limits of the static proof: it trusts the manifests for per-map encounter placement (the availability validator proves manifest ≡ live source); it does not simulate
rates, time of day, the "party has a free slot" conditions, or in-game script reachability — those are the runtime cases `WD-*`, `EVT-*`, `EV-*`, `BR-*`.

## 2. In-game completion run — PENDING

Rules: one save; real acquisition flags and legal evolution paths only; debug tooling may accelerate repeated captures/hatches but must not set Pokédex bits or flags.

| Field | Value |
|---|---|
| ROM revision / build SHA | |
| Tester / dates | |
| Save / evidence folder | |
| Methods used per species | (per-species table below) |
| Result | **NOT EXECUTED** |

Per-species evidence: for each #001–#493 record *method (wild map+method / gift / event / breeding / evolution), where/when, evidence reference*. The expected method and band for
every species are pre-filled in `pokedex_493_graph.json` (`species[].acquisition`); the run must confirm each in-game and record the reference in a copy of that file
(`pokedex_493_run_evidence.json`, not yet created).
