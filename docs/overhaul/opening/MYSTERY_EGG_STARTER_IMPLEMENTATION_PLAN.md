# Pokémon Platinum Overhaul — Mystery Egg Starter Implementation Plan

Status: **LOCKED IMPLEMENTATION PLAN**

Authority:
- docs/overhaul/opening/MYSTERY_EGG_STARTER_SPEC.md
- merged Trainer Overhaul authority
- merged Breeding 2.0 authority
- current D7 integration/QA authority

Claude Code implements this feature. It must not redesign the locked odds, starter pool, Rival branch mapping, or opening flow.

## 1. Starting point

Implement from the current post-D7 mainline after merge commit:

2826e8cd207e01584798a97f49daa3b01f766ce6

Before editing, confirm main has not advanced. If it has, use the newer main SHA and record it in the implementation report.

## 2. Confirmed source reality

The current starter flow is centered on:

- res/field/scripts/scripts_route_201.s
- src/choose_starter/choose_starter_app.c
- include/choose_starter/choose_starter_app.h
- include/struct_defs/choose_starter_data.h

Current Route 201 behavior:
- player opens Rowan's briefcase;
- StartChooseStarterScene runs;
- SaveChosenStarter stores the choice;
- GetPlayerStarterSpecies retrieves Turtwig / Chimchar / Piplup;
- GivePokemon awards that species at level 5;
- Rowan/counterpart leave;
- Barry immediately initiates the first battle;
- the first Rival trainer branch is chosen from the starter species.

Therefore the special starter egg cannot rely on ordinary walking-based hatch progression. It must reveal/hatch before Barry's first battle.

## 3. Token/workflow rule

Work narrowly.

Do not:
- reread unrelated overhaul specs;
- dump entire script or UI files into chat;
- rebuild Rival teams;
- redesign breeding;
- alter starter stats/learnsets;
- expand this into general starter randomization.

Do:
- inspect only starter selection, egg creation/hatching, starter save state, Rival branch consumers, and directly affected text/assets;
- write audit details into repo docs;
- stop only for a genuine technical blocker that prevents the locked design.

## 4. S0 — targeted dependency audit

Before edits, trace:

1. StartChooseStarterScene
2. SaveChosenStarter
3. GetPlayerStarterSpecies
4. every active caller that branches on the original three starter species
5. GivePokemon behavior used by Route 201
6. native egg creation fields
7. native egg hatch-scene entry point
8. how egg species, hatch cycle/friendship, level, OT/met data, personality, ability and shiny state are represented
9. existing egg graphics/assets suitable for the selection UI
10. all trainer/story systems that consume the starter choice later

Create:

docs/overhaul/implementation/opening/MYSTERY_EGG_STARTER_SOURCE_AUDIT.md

Keep it concise.

The audit must explicitly list every active use of GetPlayerStarterSpecies or equivalent starter-state access so the three-branch assumption cannot silently survive elsewhere.

## 5. S1 — machine-readable manifest

Create:

docs/overhaul/implementation/opening/mystery_egg_starter_manifest.json

Include:
- 13-species pool;
- exact integer weights;
- total weight = 100;
- category;
- Rival branch mapping;
- visual-choice equivalence;
- selection timing;
- hatch timing;
- output level;
- source paths;
- before guards;
- target values;
- validation state.

Locked weight table:

- Bulbasaur 3
- Charmander 3
- Squirtle 3
- Pikachu 1
- Chikorita 10
- Cyndaquil 10
- Totodile 10
- Treecko 10
- Torchic 10
- Mudkip 10
- Turtwig 10
- Chimchar 10
- Piplup 10

Use integer weight units summing to exactly 100. Do not use floating-point probability logic.

## 6. S2 — selection UI conversion

Modify the starter-selection application so the three selectable positions are visually and mechanically identical Mystery Eggs.

Requirements:
- left / center / right use the same egg visual;
- no species sprite preview;
- no species name preview;
- no type clue;
- no hidden per-slot species assignment;
- same confirmation wording for every slot;
- cursor movement and confirmation controls remain stable.

Prefer an existing Pokémon Egg sprite/icon asset already shipped in Platinum.

If the current 3D Poké Ball presentation cannot safely display an egg asset:
- reuse the current navigation shell;
- render three identical 2D egg sprites in the choice positions;
- suppress the species-preview layers.

Do not introduce new artwork unless existing egg assets are genuinely unusable.

## 7. S3 — one-time weighted draw

The weighted species roll must happen exactly once after confirmation.

Preferred implementation:
- one helper/function owns the full 100-unit table;
- generate random value in [0, 99];
- map deterministic ranges to the 13 species;
- store the actual species immediately.

Example locked ranges:
- 0–2 Bulbasaur
- 3–5 Charmander
- 6–8 Squirtle
- 9 Pikachu
- 10–19 Chikorita
- 20–29 Cyndaquil
- 30–39 Totodile
- 40–49 Treecko
- 50–59 Torchic
- 60–69 Mudkip
- 70–79 Turtwig
- 80–89 Chimchar
- 90–99 Piplup

Equivalent ordering is allowed only if the exact weights remain identical and the manifest records it.

The selected screen position must not affect the RNG table.

Do not reroll after species selection.

## 8. S4 — separate actual starter from Rival branch

Preserve the actual rolled species as the player's starter identity.

Derive a separate three-way Rival branch:

Grass → Turtwig branch:
- Bulbasaur
- Chikorita
- Treecko
- Turtwig

Fire → Chimchar branch:
- Charmander
- Cyndaquil
- Torchic
- Chimchar

Water → Piplup branch:
- Squirtle
- Totodile
- Mudkip
- Piplup

Pikachu → Piplup branch.

Audit every consumer of the starter choice.

Preferred architecture:
- actual starter species remains queryable;
- one helper or script command returns the Rival branch representative;
- existing Rival scripts are changed to query the branch helper where they require branch selection.

Do not create 13 trainer branches.

Do not falsify the actual starter species globally merely to satisfy old branch comparisons.

If an existing save field can safely hold actual species while another existing field/var can represent branch state, reuse it. Avoid save-format expansion unless necessary.

## 9. S5 — special starter egg creation

After the draw, construct a genuine special egg where feasible using native Pokémon/egg data.

The egg should:
- contain the rolled species directly;
- permit Pikachu directly rather than Pichu;
- use normal legal generated personality/nature/gender/IV/ability behavior;
- not invoke parent inheritance;
- not alter global breeding rules.

This is a scripted starter egg, not an ordinary Day Care egg.

If a real party egg object cannot safely support the required immediate scripted hatch flow, use the native hatch scene with a temporary special egg object/data structure rather than changing global hatch behavior.

Do not make a global special case in Breeding 2.0.

## 10. S6 — immediate hatch reveal

The starter must be revealed before Barry's first Route 201 battle.

Required sequence:
- confirm Mystery Egg;
- roll species;
- bind species;
- return to field;
- run hatch reveal before Rival battle;
- resulting Pokémon enters party at level 5;
- story continues.

Reuse the native egg hatch presentation if it can be invoked safely from script/source.

The normal Day Care step counter and hatch-cycle constants must remain unchanged.

If the native hatch scene produces level 1 by default, apply a starter-specific post-hatch level correction to level 5 using the normal stat recalculation path.

Do not globally change hatch level.

Ensure:
- HP is valid/full after level correction;
- legal level-5 moves are present according to the normal generation path;
- no duplicate party insertion occurs.

## 11. S7 — Route 201 integration

Replace the current direct GivePokemon starter award in Route201_Briefcase with the special egg flow.

Preserve:
- briefcase event;
- Rowan/counterpart movement;
- Barry dialogue structure where it does not explicitly name the old starter choice;
- immediate first Rival battle;
- win/loss handling;
- heal and warp home;
- later Sandgem progression.

Update text only where the original wording explicitly says the player is choosing among Pokémon rather than eggs.

Do not rewrite the whole opening.

## 12. S8 — Rival integration

Update every active Rival branch selection point to use the derived three-way branch rather than direct equality against only Turtwig/Chimchar/Piplup.

Validate at minimum:
- Route 201 first battle;
- Route 203;
- Route 209;
- Pastoria;
- Canalave;
- Pokémon League;
- Fight Area / Survival Area variants used by the merged Trainer Overhaul.

The trainer IDs/teams themselves remain unchanged.

## 13. S9 — text and presentation

Use concise Platinum-style wording.

Conceptual text:
- Rowan/counterpart refers to three Pokémon Eggs or Mystery Eggs;
- player is told to choose one;
- confirmation does not reveal species;
- hatch reveals the result.

Do not add lengthy exposition.

Update only text banks directly used by the modified opening scene unless another active branch has stale starter-specific wording.

## 14. S10 — validator and deterministic model tests

Create:

tools/overhaul/validate_mystery_starter.py

Create deterministic tests under an appropriate tools/overhaul/opening/ location.

Validator must fail on:
- pool count != 13;
- weights not summing to 100;
- any locked weight mismatch;
- missing species;
- extra species;
- different table by egg position;
- species preview before confirmation;
- more than one RNG roll;
- missing persistence after roll;
- wrong category-to-Rival mapping;
- Pikachu not mapped to Piplup branch;
- output level != 5;
- ordinary breeding constants changed;
- 13-way Rival branch duplication;
- direct legacy Turtwig/Chimchar/Piplup-only branch checks remaining in active Rival flow;
- manifest/source drift.

Deterministic model tests must cover all 100 roll values and prove the exact histogram:
- Bulbasaur 3
- Charmander 3
- Squirtle 3
- Pikachu 1
- each other starter 10.

Also test all three UI positions produce the same mapping for a fixed RNG value.

## 15. S11 — regression coverage

Rerun all established overhaul validators, including:
- moves/C1
- C2 TM/HM
- species/C3
- evolution
- availability
- special acquisition
- trainers
- economy/EXP
- Poké Balls
- breeding
- Legendary/Mythical
- Frontier/postgame
- D7 master validator

Because this feature lands after D7 integration, regenerate/update any D7 completion graph, QA index, master report, or status artifact whose source SHA or starter-path assumptions are now stale.

Do not claim the previous D7 reports still describe current main without rerunning them.

## 16. S12 — clean builds

Required before opening implementation PR:
- US Rev 0 build
- US Rev 1 build
- format
- PR lint
- relevant generated-data checks

Record source SHA and CI run.

## 17. Runtime QA

At minimum:

1. left egg selection
2. center egg selection
3. right egg selection
4. deterministic common 10% result
5. deterministic Gen I 3% result
6. deterministic Pikachu 1% result
7. no preview before hatch
8. hatch animation completes
9. output is level 5
10. first Barry battle starts correctly
11. Grass-result Rival branch
12. Fire-result Rival branch
13. Water-result Rival branch
14. Pikachu Rival branch
15. save before choice can reroll after reset
16. save after completed selection does not reroll
17. ordinary Day Care egg still follows Breeding 2.0 behavior

If emulator/manual runtime testing is unavailable, mark these NOT RUN. Do not fabricate VERIFIED status.

## 18. Implementation reports

Create:

docs/overhaul/implementation/opening/MYSTERY_EGG_STARTER_IMPLEMENTATION_REPORT.md

Record:
- starting SHA;
- source files changed;
- UI implementation method;
- RNG implementation;
- actual-starter storage;
- Rival branch storage/derivation;
- hatch implementation;
- validator/test results;
- cross-system validation;
- Rev 0/Rev 1 results;
- runtime QA status;
- unresolved blockers.

## 19. Status integration

Update:
- docs/overhaul/STATUS.md
- docs/overhaul/DESIGN_PIPELINE.md
- docs/overhaul/qa/QA_INDEX.md where applicable

Add this feature as the post-core opening overhaul, preferably D8 or an equivalent explicit phase.

Do not mark the project RELEASE CANDIDATE again until D7 integration outputs have been rerun against the new feature.

## 20. Recommended commit order

1. source audit + manifest + validator skeleton
2. starter-choice UI conversion
3. weighted draw + actual starter storage
4. branch mapping
5. special egg + hatch flow
6. Route 201 integration
7. Rival branch consumers
8. text cleanup
9. tests + cross-system validation
10. D7 report refresh + status

## 21. Acceptance criteria

The feature is source-complete when:
- all three visible choices are identical eggs;
- all three call the same weighted 13-species table;
- locked probabilities are exact;
- result is rolled once only after confirmation;
- result is hidden until hatch;
- hatch occurs before Barry's first battle;
- starter enters battle at level 5;
- actual species remains truthful;
- existing three Rival branches are preserved through locked category mapping;
- ordinary breeding is unchanged;
- all subsystem and master validators pass;
- both supported ROM revisions build.

VERIFIED requires representative runtime evidence.
