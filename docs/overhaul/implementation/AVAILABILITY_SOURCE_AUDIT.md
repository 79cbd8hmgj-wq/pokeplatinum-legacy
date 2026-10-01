# Availability — Phase A Source Audit

Base commit audited: `cb420c0d` (main at the start of the availability implementation).
Scope: where Platinum's source/data decides wild availability. Nothing here changes design; it records the
mechanics the manifests and validators in `tools/overhaul/availability/` rely on.

## 1. Encounter tables

| Item | Source of truth | Notes |
|---|---|---|
| Per-map encounter data | `res/field/encounters/encounters_<map>.json` (185 files) | Compiled by `tools/jsoncnv/encounter.py` into `pl_enc_data.narc` (183 files; `honey_tree` and `great_marsh_lookout` live in `encdata_ex`). File list/order: `res/field/encounters/meson.build`, `encounters.order`. |
| Land / cave | `land_rate`, `land_encounters[12]` (level + species) | Slot probabilities are **code-fixed** (`GetGroundEncounterSlot`, `src/overlay006/wild_encounters.c`): `20,20,10,10,10,10,5,5,4,4,1,1`. |
| Surf | `surf_rate`, `surf_encounters[5]` (min/max level) | `GetWaterEncounterSlot`: `60,30,5,4,1`. |
| Old / Good / Super Rod | `old_rod_*`, `good_rod_*`, `super_rod_*` | `GetRodEncounterSlot`: Old `60,30,5,4,1`; Good and Super `40,40,15,4,1`. |
| Time of day | `day[2]`, `night[2]` | `WildEncounters_ReplaceTimedEncounters`: the table's slots 2/3 are the *morning* default; day/twilight use `day`, night/late night use `night`. Three states, not two. |
| Swarms | `swarms[2]` + `src/overlay006/swarm.c` | Replaces slots 0/1 only on the single active swarm map (22 swarm maps in `sSwarmMapIdTable`). Species come from the *map's* `swarms` array. |
| Poké Radar | `radar[4]`, `src/pokeradar.c` | In a rare-shake patch (`shakeType == 1`) slots 4, 5, 10, 11 are replaced by `radar[0..3]` (`TryGenerateGrassEncounter_WithRadar`). Ordinary grass encounters are unaffected, so slots 4/5 stay stable. |
| Dual-slot | `ruby/sapphire/emerald/firered/leafgreen[2]`, `src/overlay006/dual_slot_encounters.c` | **Only after the National Dex**, and only with the matching cartridge in `gSystem.gbaCartridgeVersion`, slots 8/9 are replaced. Slots 8/9 are 4 % each, i.e. below the 5 % floor even before replacement. |
| Trophy Garden dailies | `encounters_trophy_garden.json` `daily_encounters[16]`, `trophy_garden_daily_encounters.c`, `WildEncounters_ReplaceTrophyGardenEncounters` | Replaces slots 6/7 **only after the National Dex**. |
| Great Marsh | `encounters_great_marsh_1..6.json`, `encounters_great_marsh_lookout.json` (`before_national_dex[32]`, `after_national_dex[32]`), `great_marsh_daily_encounters.c`, `great_marsh_binoculars.c` | While the Safari game is active, slots 6/7 of every Marsh map are replaced by one daily species chosen from the before/after-Dex array (5-bit per-area index of the daily seed). Group 9 = after Dex, group 10 = before Dex. |
| Honey Trees | `encounters_honey_tree.json` (`common/uncommon/rare`, 6 each), `src/overlay005/honey_tree.c`, `CreateWildMon_HoneyTree` | Lv 5–15, tier chosen by the tree state. Munchlax trees chosen from the daily seed. |
| Feebas | `encounters_mt_coronet_b1f.json` `elusive_rod_encounter` + tile table, `src/overlay006/feebas_fishing.c` | Random tiles seeded from `RecordMixedRNG` (mixed-record data). Current implementation = random-tile dependency (USER_DECISION_REQUIRED). |
| Unown forms | `rate_form0..4`, `unown_table` | Untouched. |
| National Dex gates | `WildEncounters_ReplaceDualSlotEncounters`, `WildEncounters_ReplaceTrophyGardenEncounters`, `ReplaceGreatMarshDailyEncounters` (all take `nationalDexObtained`) | Plus UI/story uses (`pokedex.c`, `main_menu.c`, `scrcmd.c`…) that this task does **not** touch (UI timing is USER_DECISION_REQUIRED). |
| Level progression | per-slot level in the JSON; `GetWildMonLevel` rolls min..max for water and applies Hustle/Vital Spirit/Pressure | Land slots have a single fixed level. The route level curve therefore lives in the slot levels; the plan keeps the base level of each slot. |
| Pokédex area data | `tools/scripts/make_pokedex_enc_platinum.py` (reads the same JSON) | Regenerates automatically; no manual edit. |

## 2. Gifts, statics, fossils, Spiritomb, Rotom (read-only audit; nothing here is modified)

| Acquisition | Location |
|---|---|
| Starters | `res/field/scripts/scripts_route_201.s` (`GivePokemon VAR_0x8000, 5`) |
| Eevee gift | `scripts_hearthome_city_northwest_house.s:38` (Lv 20) |
| Porygon gift | `scripts_veilstone_city_northeast_house.s:39` (Lv 25) |
| Togepi egg | `scripts_eterna_city.s:1089` (Cynthia) |
| Riolu egg | `scripts_iron_island_b2f_left_room.s:245` |
| Drifloon static (Fridays) | `scripts_valley_windworks_outside.s:146`, daily flag `FLAG_DAILY_WON_AGAINST_VALLEY_WINDWORKS_OUTSIDE_DRIFLOON` |
| Rotom | `scripts_old_chateau_back_middle_west_room.s:24` (`StartWildBattle`, Lv 20); forms `scripts_rotoms_room.s`, `scripts_init_rotoms_room.s` |
| Spiritomb | `scripts_route_209.s:78` (Lv 25) gated by `VAR_SPIRITOMB_COUNTER`, incremented by Underground interaction (`src/underground/player.c:237`) |
| Fossils | `src/scrcmd_fossil.c` item→species table; revival `scripts_mining_museum.s:228`; fossil items come from Underground mining (`src/underground/mining.c`) |
| Legendary/mythical statics | 13 `StartLegendaryBattle` calls (out of scope) |

## 3. Source limitations / architecture-relevant findings

1. **Super Rod is post-Hall of Fame.** It is only given by the Fight Area fisherman (`scripts_fight_area.s:426-432`).
   The approved matrix lists Clamperl (M2) and Relicanth (L2) under "Super Rod". A pre-Elite Four family entry cannot rely
   on Super Rod, so the implementation uses Good Rod slots for those two families (see `AVAILABILITY_IMPLEMENTATION_REPORT.md`,
   discrepancy D1). Super Rod tables are left to P1.
2. **Slots below 5 % cannot carry required entries.** Land slots 8–11 (4/4/1/1 %) and water slots 3–4 (4/1 %) are never relied on.
3. **Slots 6/7 are unstable on Trophy Garden and Great Marsh maps** (replaced by dailies); required families there are kept in slots 0–5.
4. **Time-of-day slots.** Only slots 2/3 change with the clock. The plan keeps slot 2 time-invariant and uses slot 3 for
   time flavour, and every required family has a time-invariant ≥ 5 % slot.
5. **Dual-slot is table-structural**, not script logic, so it is neutralised in data (mirror slots 8/9 into every cartridge array).
6. **Radar/swarm/Honey/Garden/Marsh are bonus replacements of ordinary slots**, so converting them to "bonus only" needs
   no code change — only guaranteeing fixed fallbacks (done and validated).
7. **Trophy Garden dailies stay gated by the National Dex in code.** They are bonus-only; removing the gate would be a code
   change and touches the unresolved National Dex timing decision, so it is left alone.
8. **Local build prerequisites** (session notes): `gcc-arm-none-eabi`, `libc6-i386` for the 32-bit Metrowerks tools, and the
   `rapidjson`/`yyjson` meson subprojects (WrapDB is unreachable from the session proxy; they were assembled by hand from the
   cached sources). CI is unaffected.
