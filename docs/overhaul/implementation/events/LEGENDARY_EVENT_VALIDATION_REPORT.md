# D5 Legendary / Mythical Event Validation Report

Base commit: `08092189cd4ea322a5b1b788a559a1ea2fbcbfd9` · validator: `tools/overhaul/validate_legendary_availability.py`

Status: **IMPLEMENTED** (source + validator + dual-revision builds). **Runtime event QA PENDING — nothing here is VERIFIED.**

## Result

**51 / 51 checks pass, 0 failure(s).**

| ID | Check | Result |
|---|---|---|
| A1 | locked species set == the 35 RESERVED_LATER_PHASE families (#001-#493) | PASS |
| A2 | every Legendary/Mythical has an in-save acquisition entry | PASS |
| A3 | exactly one acquisition owner per species | PASS |
| A4 | no manifest entry outside the locked species set | PASS |
| A5 | manifest entries complete (required fields, valid class, no premature VERIFIED) | PASS |
| A6 | no Legendary/Mythical in ordinary encounter JSON (single wild owner = habitat hook) | PASS |
| A7 | acquisition class matches the locked classification | PASS |
| A8 | locked static levels (Darkrai 50, Shaymin 30, Arceus 80, Regigigas 1, Heatran 50, Mew 50, Celebi 50, Jirachi 50, Deoxys 60) | PASS |
| A9 | capture flags are declared in generated/vars_flags.txt | PASS |
| B1 | no distribution / WFC / Slot-2 / event-Regigigas gate left in any field script or Azure Flute check | PASS |
| B2 | every acquisition script is free of external-dependency tokens | PASS |
| B3 | event_gate_removals.json: removed gates are absent from the listed files | PASS |
| B4 | no manifest entry declares a remaining external dependency | PASS |
| B5 | legendary acquisition scripts contain no multiplayer/trade checks | PASS |
| C1 | LegendaryHabitat table present in wild_encounters.c | PASS |
| C2 | no two legendaries share a (map, method) habitat | PASS |
| C3 | habitat manifest rows == C table rows (map, method, species, %, levels) | PASS |
| C4 | habitat rates/levels/methods equal the locked matrix (R2=2%, R1=1%) | PASS |
| C5 | each habitat map has an encounter table (non-zero rate) for its method | PASS |
| C6 | habitat hook checks the Hall-of-Fame flag before any roll | PASS |
| C7 | habitat hook is wired into WildEncounters_TryWildEncounter | PASS |
| C8 | hook is renewable: no flag/var written, no Radar/swarm/dual-slot input | PASS |
| C9 | habitat manifest entries: Hall of Fame required, RENEWABLE, no capture flag | PASS |
| D1 | one-time encounters: completion/consumed markers are written only on the captured path (defeat/flee/blackout never consume) | PASS |
| D2 | one-time encounters: defeat/flee/blackout restore the encounter (retry actions present on both branches) | PASS |
| D3 | one-time encounters: leave/re-enter paths (OnTransition/reset scripts) re-offer an uncaught encounter | PASS |
| D4 | one-time encounters: a captured encounter does not respawn (entry guard / Hall-of-Fame re-show guard) | PASS |
| D5 | roamers: only BATTLE_RESULT_CAPTURED_MON sets ROAMER_STATE_CAPTURED; HP-0 win sets DEFEATED (reset path exists) | PASS |
| D6 | no script activates the roaming legendary birds (habitat model owns them) | PASS |
| E1 | Hall-of-Fame gate present in the script of every HoF-locked static/event | PASS |
| F1 | caught-Pokédex check covers exactly species #001-#492 (forms not counted, Arceus excluded) | PASS |
| F2 | script command is registered (macro + table) | PASS |
| F3 | Rowan grants the Azure Flute only after the caught-Pokédex check succeeds (and after the Hall of Fame) | PASS |
| F4 | Hall of Origin re-checks Hall of Fame + the Pokédex prerequisite before showing Arceus | PASS |
| F5 | only Arceus depends on Pokédex completion | PASS |
| G1 | Member Card: Sailor Eldritch (Canalave) grants it after Hall of Fame + Cresselia/Lunar Wing child sequence | PASS |
| G2 | Member Card grant checks bag space and uses the common give-item script | PASS |
| G3 | Harbor Inn Darkrai start needs only the Member Card (Hall of Fame, National Dex, Lunar Wing sequence upstream) | PASS |
| G4 | Route 224: Oak appears after Hall of Fame + National Dex without a letter/distribution requirement | PASS |
| G5 | Oak gives Oak's Letter in-game (bag-space checked) | PASS |
| G6 | Flower Paradise Shaymin: Hall of Fame + National Dex + Oak's Letter (no distribution) | PASS |
| H1 | Manaphy Egg: one-time flag, party-space check before GiveEgg, received flag only after the grant | PASS |
| H2 | full party withholds the gift without setting the received flag | PASS |
| H3 | Manaphy Egg gate: Hall of Fame + Lunar Wing child sequence | PASS |
| H4 | Phione: Manaphy breeding special case preserved in the egg-species logic | PASS |
| H5 | Phione owned solely by Manaphy breeding | PASS |
| I1 | Rotom appliance room: all five forms and their move assignment preserved | PASS |
| I2 | Secret Key is guaranteed with the first Old Chateau Rotom capture (flag only after capture) | PASS |
| I3 | Rotom room usable permanently once the Secret Key is held (no distribution gate) | PASS |
| J1 | completion graph is acyclic and every species is reachable before Arceus | PASS |
| J2 | Arceus is the only species with a Pokédex-completion prerequisite and nothing depends on Arceus | PASS |

## Acquisition table (#001–#493 Legendary/Mythical, 35 species)

| Dex | Species | Class | Where | Level | Rate | Cadence | Capture marker |
|---:|---|---|---|---|---|---|---|
| 144 | Articuno | RARE_POSTGAME_HABITAT | Snowpoint Temple deep floors / Acuity cavern ecology | 55-60 | 2% | RENEWABLE | — |
| 145 | Zapdos | RARE_POSTGAME_HABITAT | Fuego Ironworks / Valley Windworks high-energy zone | 55-60 | 2% | RENEWABLE | — |
| 146 | Moltres | RARE_POSTGAME_HABITAT | Stark Mountain volcanic zone | 55-60 | 2% | RENEWABLE | — |
| 150 | Mewtwo | RARE_POSTGAME_HABITAT | deepest Turnback Cave rooms | 70 | 1% | RENEWABLE | — |
| 151 | Mew | HIDDEN_MYTHICAL_STATIC | Eterna Forest (north-east dead end, tile of the Ether item ball) | 50 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_MEW |
| 243 | Raikou | RARE_POSTGAME_HABITAT | Route 222 / Sunyshore electric coast | 55-60 | 2% | RENEWABLE | — |
| 244 | Entei | RARE_POSTGAME_HABITAT | Stark Mountain exterior volcanic zone | 55-60 | 2% | RENEWABLE | — |
| 245 | Suicune | RARE_POSTGAME_HABITAT | Lake Acuity / northern clear-water zone | 55-60 | 2% | RENEWABLE | — |
| 249 | Lugia | RARE_POSTGAME_HABITAT | deep postgame sea near Routes 226-230 | 65-70 | 1% | RENEWABLE | — |
| 250 | Ho_Oh | RARE_POSTGAME_HABITAT | upper Mt. Coronet / Spear Pillar-adjacent habitat | 65-70 | 1% | RENEWABLE | — |
| 251 | Celebi | HIDDEN_MYTHICAL_STATIC | Floaroma Meadow (north-west, tile of the Miracle Seed item ball) | 50 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_CELEBI |
| 377 | Regirock | NATIVE_RUIN | Rock Peak Ruins (statue puzzle) | 30 | static | ONE_TIME_UNTIL_CAPTURED | VAR_ROCK_PEAK_RUINS_STATE == RUINS_STATE_CAUGHT_REGI |
| 378 | Regice | NATIVE_RUIN | Iceberg Ruins (statue puzzle) | 30 | static | ONE_TIME_UNTIL_CAPTURED | VAR_ICEBERG_RUINS_STATE == RUINS_STATE_CAUGHT_REGI |
| 379 | Registeel | NATIVE_RUIN | Iron Ruins (statue puzzle) | 30 | static | ONE_TIME_UNTIL_CAPTURED | VAR_IRON_RUINS_STATE == RUINS_STATE_CAUGHT_REGI |
| 380 | Latias | RARE_POSTGAME_HABITAT | Routes 224-230 postgame coast | 55-60 | 2% | RENEWABLE | — |
| 381 | Latios | RARE_POSTGAME_HABITAT | Routes 224-230 postgame coast | 55-60 | 2% | RENEWABLE | — |
| 382 | Kyogre | RARE_POSTGAME_HABITAT | deep postgame ocean, Routes 226-230 | 70 | 1% | RENEWABLE | — |
| 383 | Groudon | RARE_POSTGAME_HABITAT | Stark Mountain deepest terrestrial zone | 70 | 1% | RENEWABLE | — |
| 384 | Rayquaza | RARE_POSTGAME_HABITAT | upper Mt. Coronet / Spear Pillar postgame zone | 70 | 1% | RENEWABLE | — |
| 385 | Jirachi | HIDDEN_MYTHICAL_STATIC | Mt. Coronet 6F (Spear Pillar approach, tile south of the summit warp) | 50 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_JIRACHI |
| 386 | Deoxys | HIDDEN_MYTHICAL_STATIC | Veilstone City meteorites (four existing BG events) | 60 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_DEOXYS |
| 480 | Uxie | NATIVE_STATIC | Acuity Cavern (object) | 50 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_UXIE |
| 481 | Mesprit | NATIVE_ROAMER | Verity Cavern activation + Sinnoh roaming | 50 | roamer | ONE_TIME_UNTIL_CAPTURED | VAR_ROAMING_MESPRIT_STATE == ROAMER_STATE_CAPTURED |
| 482 | Azelf | NATIVE_STATIC | Valor Cavern (object) | 50 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_AZELF |
| 483 | Dialga | NATIVE_STATIC | Spear Pillar Dialga rift (postgame) | 70 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_DIALGA |
| 484 | Palkia | NATIVE_STATIC | Spear Pillar Palkia rift (postgame) | 70 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_PALKIA |
| 485 | Heatran | NATIVE_STATIC | Stark Mountain room 3 (object, postgame) | 50 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_HEATRAN |
| 486 | Regigigas | NATIVE_STATIC | Snowpoint Temple B5F (object) | 1 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_REGIGIGAS |
| 487 | Giratina | NATIVE_STATIC | Distortion World story battle + Turnback Cave Giratina room | 47 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_GIRATINA |
| 488 | Cresselia | NATIVE_ROAMER | Fullmoon Island Forest activation (Lunar Wing) + Sinnoh roaming | 50 | roamer | ONE_TIME_UNTIL_CAPTURED | VAR_ROAMING_CRESSELIA_STATE == ROAMER_STATE_CAPTURED |
| 489 | Phione | BREEDING_ONLY | Daycare breeding (Manaphy + Ditto) | Egg | breeding | RENEWABLE | — |
| 490 | Manaphy | RESTORED_EVENT | Canalave City - Sailor Eldritch (Egg gift) | Egg (Lv1) | gift | ONE_TIME_GIFT | FLAG_RECEIVED_CANALAVE_CITY_MANAPHY_EGG |
| 491 | Darkrai | RESTORED_EVENT | Canalave Harbor Inn -> Newmoon Island Forest | 50 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_DARKRAI |
| 492 | Shaymin | RESTORED_EVENT | Route 224 (Oak, tablet) -> Seabreak Path -> Flower Paradise | 30 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_SHAYMIN |
| 493 | Arceus | RESTORED_EVENT | Veilstone Store B1F (Prof. Rowan, Azure Flute) -> Spear Pillar -> Hall of Origin | 80 | static | ONE_TIME_UNTIL_CAPTURED | FLAG_CAUGHT_ARCEUS |

## Completion order (prerequisite-respecting)

Articuno → Azelf → Celebi → Cresselia → Darkrai → Deoxys → Dialga → Entei → Giratina → Groudon → Heatran → Ho_Oh → Jirachi → Kyogre → Latias → Latios → Lugia → Manaphy → Mesprit → Mew → Mewtwo → Moltres → Palkia → Raikou → Rayquaza → Regice → Regirock → Registeel → Shaymin → Suicune → Uxie → Zapdos → Phione → Regigigas → Arceus

## Source facts audited

* Vanilla bug class fixed: after any non-capturing battle the object hide flag (Uxie, Azelf, Turnback Giratina, Regigigas), the encounter state (Dialga, Palkia, Heatran) or the statue state (Regirock, Regice, Registeel) stayed consumed until the next Hall of Fame (or forever, for the Regi statues).
* Regirock/Regice/Registeel statues no longer require an event-distributed Regigigas in the party.
* Gen I–III legendaries use one `LegendaryHabitat` table in `src/overlay006/wild_encounters.c`; exact 1%/2% (including Surf, whose slot weights are code-fixed at 60/30/5/4/1) is why a post-Hall-of-Fame roll replaces slot editing. Ordinary encounter JSON is untouched.
* Mew / Celebi / Jirachi are new BG-event tiles on existing item-ball / summit-approach tiles; Deoxys reuses the four existing Veilstone meteorite BG events.

## Runtime QA (not performed)

Required in-game checks (none run): Uxie/Azelf defeat-retry; Mesprit/Cresselia defeat-reset; Giratina retry; Dialga; Palkia; Heatran; Darkrai/Shaymin full unlock; Arceus prerequisite fail/success; Manaphy Egg empty/full party; Phione breeding; Rotom forms; Regis + Regigigas; renewable birds; one 2% and one 1% habitat; Mew; Celebi; Jirachi; Deoxys + form change. For every one-time static: encounter available → defeat/flee does not consume → leave/re-enter retries → capture sets completion → no respawn.

<!-- cross-system:begin -->
## Cross-system validators

| System | Command | Result | Summary |
|---|---|---|---|
| availability (ordinary + special + D5 Rotom update) | `tools/overhaul/availability/validate_availability.py` | PASS | RESULT: 0 failure(s), 0 warning(s) |
| evolution | `tools/overhaul/evolution/validate_evolutions.py` | PASS | PASS |
| C1 existing-move rebalance | `tools/overhaul/moves/validate_c1.py` | PASS | C1 validation: OK (0 problems, 82 edits) |
| C2 mechanics | `tools/overhaul/c2/validate_c2.py` | PASS | C2 validation: OK (0 problems) |
| breeding | `tools/overhaul/validate_breeding.py` | PASS | breeding validator: 107 pass, 0 fail, 0 pending -> docs/overhaul/implementation/breeding/BREEDING_VALIDATION_R |
| economy | `tools/overhaul/economy/validate_economy.py` | PASS | economy validation: 0 failure(s) |
| Poké Ball | `tools/overhaul/pokeballs/validate_pokeballs.py` | PASS | pokeball validation: 0 failure(s) |
| trainer | `tools/overhaul/trainers/validate_trainers.py` | PASS | trainer validation: 0 errors, 16 warnings, 13 notes |
| D5 Legendary/Mythical availability | `tools/overhaul/validate_legendary_availability.py` | PASS | 51/51 checks pass; failures: 0 |

Builds: US Rev 0 ROM and US Rev 1 ROM both build locally from this branch head (metroskrew + arm-none-eabi toolchain, `make rom ROM_REVISION=0|1`); CI build to be recorded on the PR.
<!-- cross-system:end -->
