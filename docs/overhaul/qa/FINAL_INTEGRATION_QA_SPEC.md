# Pokémon Platinum Overhaul — Final Integration & QA Spec

Status: **LOCKED SPEC**

## 1. Release target

The overhaul is release-ready only when all locked subsystems are integrated, machine-validated, dual-revision buildable, and runtime-tested across the main story and postgame.

Fresh-save play is the canonical support target.

Existing vanilla Platinum saves should remain loadable where the unchanged save structure permits, but round-tripping an overhaul save back into vanilla is not supported once custom moves, new flags, or altered systems have been used.

Supported ROM revisions:
- Pokémon Platinum US Rev 0
- Pokémon Platinum US Rev 1

Both must remain first-class build targets.

## 2. Canonical authority order

Final QA resolves discrepancies using:

1. current locked subsystem machine-readable manifests;
2. current locked subsystem specs;
3. current source on `main`;
4. implementation validation reports;
5. historical provenance only when needed to explain earlier changes.

Never silently revive superseded chat decisions or historical ledgers over current canonical authority.

## 3. Integration gates

### Q0 — Documentation/source consistency

Before full playtesting:
- every designed subsystem has a locked spec;
- every implemented subsystem has a Claude-ready implementation plan;
- `STATUS.md` accurately reflects actual source state;
- no implemented feature is documented as merely planned;
- no locked feature is falsely marked implemented.

### Q1 — Clean builds

Both US revisions must:
- configure cleanly;
- build from a clean checkout;
- produce expected ROM artifacts;
- pass all repository validation scripts;
- contain no untracked manual binary patch requirement.

### Q2 — Static semantic validation

Run validators for:
- C1 moves;
- created moves;
- species/types/stats/abilities;
- evolutions;
- TM/HM compatibility;
- availability/encounters;
- trainer teams;
- EXP/economy;
- Poké Balls;
- breeding;
- Legendary/Mythical events;
- Frontier/postgame.

No blocking validation errors are allowed.

Warnings must be reviewed and either:
- fixed; or
- explicitly accepted/documented.

## 4. Pokédex completion validation

Create a canonical #001–#493 completion graph.

For every species record:
- acquisition family/source;
- earliest progression gate;
- evolution path;
- required item/location/time/move/stat/gender condition;
- breeding dependency if any;
- legendary/event source if applicable;
- form-specific note where relevant;
- external dependency flags.

Required proofs:
- all 493 species are reachable in one save;
- every nonlegendary evolutionary family has a deterministic pre-Elite Four entry;
- no required source depends on trade, WFC, multiplayer, another game, Slot-2, version exclusivity, or an unbounded random rotation;
- every evolution can be completed internally;
- all required evolution stones are renewable pre-E4;
- no non-stone trade-evolution item is required.

## 5. Move-system validation

Prove:
- all move IDs referenced anywhere exist;
- created moves 468–489 are correctly registered;
- no trainer/frontier/learnset references an invalid move;
- C1 exactly matches its canonical 82-edit manifest;
- TM21/TM78 masks match canonical recipient counts;
- all HM battle effects match the locked spec;
- reusable TMs work without item loss;
- move descriptions match actual behavior.

Focused runtime checks remain mandatory for:
- Resonant Slash sound/Soundproof;
- Star Jab Iron Fist/punching;
- Magnet Volley exactly three equal 25-BP hits;
- Razor Wind single-turn high-crit behavior;
- Defog hazard/screen removal behavior;
- created-move representative animations/text.

## 6. Pokémon identity validation

For all #001–#493:
- type matches locked authority;
- base stats match locked authority;
- ability slots match locked authority;
- evolution method matches locked authority;
- level-up learnset matches canonical C3 result;
- TM/HM compatibility matches canonical masks/additions;
- no unintended later-generation mechanic leaked into Core 1.0.

Spot-check every retyped/role-repair family in runtime.

## 7. Encounter/world validation

Machine checks:
- every nonlegendary family has pre-E4 acquisition;
- required wild rate is >=5% unless acquisition is retry-safe guaranteed;
- encounter-table density remains within architecture limits or has documented exception;
- no sole daily/Radar/Honey/Marsh/Garden/dual-slot dependency;
- both D/P exclusives are available;
- no inaccessible fishing/surf/field-method source.

Runtime route sampling:
- at least one representative map from every availability band E0–P1;
- representative land/cave/Surf/Old Rod/Good Rod/Super Rod;
- day/night fallback;
- Honey/Marsh/Radar/swarm/Garden bonus behavior;
- former dual-slot families.

## 8. Progression and trainer validation

Use D2 progression simulation and trainer manifests together.

Primary profile:
- 5–6 Pokémon rotating team;
- normal exploration;
- most mandatory and reasonable optional trainers;
- no deliberate grass grinding.

Validate:
- player median level stays within target boss bands;
- no repeated >2-level overage over boss ace for normal play;
- no repeated >3-level deficit to boss non-ace average;
- early strong species do not create unexplained difficulty spikes;
- ordinary trainers remain below boss difficulty;
- Elite Four/Cynthia remain the main-story peak.

Runtime battle checks:
- all eight Gyms;
- representative Rival battles early/mid/League;
- Mars/Jupiter/Saturn/Cyrus;
- Elite Four/Cynthia;
- representative rematches.

## 9. EXP/economy validation

Prove:
- 60/40 conserved team EXP distribution is exact;
- no modern-style multiplicative party EXP inflation;
- Exp. Share priority behavior matches spec;
- team-share-only recipients do not gain EVs;
- trainer/traded/Lucky Egg modifiers remain correct;
- item prices match economy manifest;
- free Move Reminder works;
- shard tutor costs match locked half-cost rule;
- evolution stones are renewable;
- postgame Rare Candy source is correctly gated;
- no Poké Ball prices were accidentally changed outside D3.

Run numeric runtime checks with 1, 3, and 6 eligible Pokémon.

## 10. Poké Ball validation

For every ball:
- correct base modifier;
- correct conditional modifier;
- correct item identity;
- correct availability/price;
- no unsupported later-generation behavior beyond locked D3 design.

Runtime statistical/forced-state tests for:
- Quick Ball first turn and later;
- Timer progression;
- Repeat caught/uncaught;
- Dusk cave/night;
- Net Water/Bug;
- Dive water-terrain logic;
- Heal Ball multiplier + post-capture healing;
- Nest/level-ratio behavior;
- standard Great/Ultra baseline.

## 11. Breeding validation

Prove:
- Everstone 100% inheritance;
- four distinct inherited IV stats;
- Power-item forcing;
- ability inheritance per locked D4 behavior;
- either-parent egg moves;
- all nine no-incense babies;
- 128-step egg checks;
- half hatch cycles/minimum 5;
- Flame Body/Magma Armor;
- Masuda regression;
- special species cases;
- every egg move has a one-save legal chain.

No broad egg-group/move expansion may appear without manifest authority.

## 12. Legendary/Mythical validation

For all Legendary/Mythical #001–#493:
- internal source exists;
- no external distribution/migration dependency;
- prerequisite graph is acyclic;
- static/gift encounter is retry-safe;
- roamer faint/reset behavior works;
- event item source exists;
- captured/received flag is unique and correct.

Runtime-test every event class and all restored signature events:
- Darkrai;
- Shaymin;
- Arceus;
- Rotom forms;
- Regis/Regigigas;
- Manaphy Egg;
- imported Kanto/Johto/Hoenn chains.

## 13. Frontier/postgame validation

Prove:
- native Frontier challenge milestones unchanged;
- final BP payout doubled exactly once;
- Castle Points untouched;
- locked TM BP prices exact;
- non-TM BP shop prices unchanged unless manifested;
- Battleground can reshuffle without calendar waiting;
- Rival rematch is daily rather than weekend-only;
- rematch teams match trainer authority;
- Frontier sets remain coherent under retypes/move changes;
- Print milestone rewards are one-time and retry-safe.

Runtime-test all five facilities at least through one ordinary completed set, plus representative Silver/Gold reward paths.

## 14. Field progression and softlock audit

Perform a script/flag audit for:
- badge gates;
- HM/field move progression;
- National Dex checks;
- event item flags;
- story warps;
- legendary quest prerequisites;
- postgame route unblock;
- Day Care;
- marts;
- gifts/full-party handling.

No locked system may introduce:
- impossible required flag order;
- one-time gift loss;
- required item consumed before success;
- unreachable map;
- field-move dead end;
- save-state corruption path.

## 15. Full campaign playthrough requirement

At least one fresh-save full campaign playthrough must cover:

- start → Hall of Fame;
- normal 5–6 Pokémon rotating team;
- no debug progression skips for the canonical run;
- representative catching/breeding/TM use;
- all eight Gyms;
- Galactic story;
- Distortion World;
- League.

Record:
- party levels at each boss;
- money at each Gym;
- major purchases;
- notable difficulty spikes;
- bugs/softlocks;
- approximate playtime;
- any required grinding.

A second targeted/debug-assisted completion run may be used for exhaustive postgame/event coverage.

## 16. 493 completion run

Before final release, prove all 493 obtainable on one save.

This may use debug tooling to accelerate repeated capture/hatching, but must follow real acquisition flags and legal evolution paths.

No direct Pokédex-bit injection counts as proof.

Output:
`docs/overhaul/qa/POKEDEX_493_COMPLETION_REPORT.md`

Include every species and acquisition proof.

## 17. Save compatibility

Test:
- fresh overhaul save;
- vanilla US Rev 0 save loaded by matching overhaul revision;
- vanilla US Rev 1 save loaded by matching overhaul revision;
- normal save/load after acquiring created moves;
- normal save/load after new event flags;
- normal save/load after Frontier/breeding activity.

Do not promise compatibility with loading an overhaul-modified save back into unmodified vanilla.

If save structure is changed during implementation, explicitly version/document the break before release.

## 18. Regression policy

Any late fix must:
- identify owning subsystem;
- update its canonical manifest/spec if design changes;
- add a regression test;
- rerun affected validators;
- rebuild both revisions.

Do not make undocumented release-only source tweaks.

## 19. Release blockers

Release is blocked by any:
- build failure in either supported revision;
- species not obtainable;
- impossible evolution;
- main-story softlock;
- invalid move/species/item ID;
- repeatable crash;
- save corruption;
- missing required event retry;
- major progression over/under-leveling;
- validator blocking error;
- undocumented canonical contradiction.

Cosmetic text/animation imperfections may be separately triaged only if they do not misrepresent gameplay behavior.

## 20. Release package

Final release preparation should produce:
- clean source commit/tag;
- Rev 0 and Rev 1 patch artifacts using the repository's supported patch workflow;
- checksums;
- installation/readme instructions;
- feature summary;
- known limitations;
- save-compatibility statement;
- verification report index.

Do not distribute copyrighted base ROM data.

## 21. Final sign-off

The project may be marked **CORE 1.0 VERIFIED / RELEASE CANDIDATE** only when:
- all subsystem validators pass;
- both revisions build;
- full campaign run passes;
- 493 completion proof passes;
- high-risk runtime matrix passes;
- all release blockers are closed;
- `STATUS.md` and release documentation match actual evidence.

This spec is the canonical D7 final-integration authority.
