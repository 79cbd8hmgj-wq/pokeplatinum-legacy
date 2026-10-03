# Mystery Egg Starter — Source Audit (D8 / S0)

Starting SHA: `6fc1eedfec637041733b5e5d9626a49c7524daa9` (`main`, PR #23 merged). Scope: starter selection, starter persistence, Rival-branch consumers, egg/hatch
presentation, Route 201 integration. Genuine blockers: **none**. The audit below is the pre-change state; the post-change state is in
`MYSTERY_EGG_STARTER_IMPLEMENTATION_REPORT.md`.

## 1. Pre-change flow

`Route201_Briefcase` (`res/field/scripts/scripts_route_201.s`):
`StartChooseStarterScene` → `SaveChosenStarter` → `ReturnToField` → fade in → `GetPlayerStarterSpecies VAR_0x8000` → `GivePokemon VAR_0x8000, 5, ITEM_NONE`
→ Rowan/Barry text (`BufferRivalStarterSpeciesName 2`) → Rowan + counterpart leave → `Route201_StartRivalBattle` (branch on starter) → `StartFirstBattle`.
The player therefore must own a usable Lv5 Pokémon before `Route201_StartRivalBattle`.

## 2. Traced symbols

| Symbol | Where | Pre-change behavior |
|---|---|---|
| `ScrCmd_StartChooseStarterScene` | `src/scrcmd.c` | allocs `ChooseStarterData {int species; Options*}`, launches `FieldSystem_LaunchChooseStarterApp`. |
| Chooser app | `src/choose_starter/choose_starter_app.c` | 3D Poké Ball shell; `STARTER_OPTION_0/1/2` = Turtwig/Chimchar/Piplup; one `PokemonSprite` per option (hidden until confirm, then zoomed into a preview plate); `Sound_PlayPokemonCry(species)` on confirm; confirm text `pl_msg_00000360_00001..3` names the species; `ChooseStarter_Exit` wrote `data->species = GetSelectedSpecies(cursorPosition)`. |
| `ScrCmd_SaveChosenStarter` | `src/scrcmd.c` | `SystemVars_SetPlayerStarter(chooseStarterData->species)` → `VAR_PLAYER_STARTER` (u16 var, **existing**), frees data. |
| `ScrCmd_GetPlayerStarterSpecies` | `src/scrcmd.c` | returns `VAR_PLAYER_STARTER`. |
| `SystemVars_GetRivalStarter` / `…GetPlayerCounterpartStarter` | `src/system_vars.c` | keyed on `playerStarter == TURTWIG/CHIMCHAR`, else-branch Piplup. Back `BufferRivalStarterSpeciesName` and `BufferPlayerCounterpartStarterSpeciesName[WithArticle]`, and `field_battle_data_transfer.c` (counterpart Lv5 partner mon). |
| `BufferPlayerStarterSpeciesName` | `src/scrcmd_strings.c` | actual species name; only used in an `_Unused` Route 201 label. |
| `start_menu.c:371` | | `GetPlayerStarter == SPECIES_NONE` (menu gating) — actual-species use, unchanged. |
| `ScrCmd_GivePokemon` → `Pokemon_GiveMonFromScript` | `src/scrcmd_party.c`, `src/unk_02054884.c` | `Pokemon_InitWith(level, INIT_IVS_RANDOM, personality 0 → random, OTID_NOT_SET)`, `Pokemon_SetCatchData`, `Party_AddPokemon`, `SaveData_UpdateCatchRecords`. |

## 3. Egg / hatch internals

- **Egg construction:** `Egg_CreateEgg(egg, species, param2, trainerInfo, param4, metLocation)` (`src/overlay005/daycare.c`): `Pokemon_InitWith(species, level 1, INIT_IVS_RANDOM, shiny FALSE, personality 0 = random, OTID_NOT_SET)`; `MON_DATA_FRIENDSHIP` = species hatch cycles; `MON_DATA_IS_EGG` = TRUE; nickname "Egg"; egg location/date via `UpdateMonStatusAndTrainerInfo`. Species is stored directly (Pikachu stays Pikachu; Pichu only arises from Day Care species resolution upstream of this function).
- **Hatch entry:** `FieldSystem_HatchEgg` (`src/unk_0203D1B8.c`) → `EggHatch_HatchEgg` → `FieldTask_HatchEgg` (`src/egg_hatch.c`) → `Egg_CreateHatchedMon` → overlay `egg_hatch_cutscene`. It also records the Happy Happy Egg Club TV segment.
- **Hatch level:** `Egg_CreateHatchedMonInternal` rebuilds the mon with `Pokemon_InitWith(..., level 1, ..., egg personality)` and copies the egg's moves/IVs/OT/dates; `friendship = 120`, `metLevel = 0`. So a stock hatch is always **Lv1**.
- **Personality / nature / gender / IV / ability:** all derive from the egg's stored personality + IVs (random for non-Day-Care eggs); ability slot is personality bit 0. Day Care inheritance happens only in the Breeding 2.0 egg *generation* path, not in `Egg_CreateEgg`.
- **Existing assets:** `SPECIES_EGG` is a first-class sprite species (`BuildPokemonSpriteTemplate`), used by the party/summary screens. No new art is needed.

## 4. Consumers of the starter choice

### 4a. Uses needing the ACTUAL player starter species
| Use | Location | Decision |
|---|---|---|
| Egg binding | new `ScrCmd_GiveMysteryStarterEgg` | reads `VAR_PLAYER_STARTER` |
| Persistence | `VAR_PLAYER_STARTER` (no save-format change) | stores the 13-way species |
| Menu gating | `start_menu.c` (`!= SPECIES_NONE`) | unchanged |
| Sandgem lab starter-gift skip | `scripts_sandgem_town_pokemon_research_lab.s` (`GetPlayerStarterSpecies VAR_0x8000`, `GoToIfEq … SKIP_<species>`) | unchanged: skips an offered Sinnoh gift when it equals the hatched species; Kanto/Johto/Hoenn offers are untouched (D8 does not change one-save completion policy) |
| `BufferPlayerStarterSpeciesName` | `_Unused` Route 201 label | unchanged (actual species) |

### 4b. Uses needing the three-way RIVAL BRANCH (converted to `GetPlayerStarterBranch` / branch-derived)
Route 201 first battle; Route 203; Route 209 gate; Pastoria rival battle + Pastoria accessory mask; Canalave; Pokémon League North Pokécenter rival; Fight Area partner team; Survival Area rival team; Spear Pillar partner team; Jubilife (Dawn/Lucas partner); Veilstone (Dawn/Lucas partner) + Veilstone store socialite mask; Jubilife TV 2F mask; Trainers' School (Harrison, Christine); Eterna Underground doll. C side: `SystemVars_GetRivalStarter` (→ `BufferRivalStarterSpeciesName`), `SystemVars_GetPlayerCounterpartStarter` (→ counterpart name buffers + `field_battle_data_transfer.c`).
Total script call sites converted: 19 (`GetPlayerStarterSpecies` → `GetPlayerStarterBranch`). Every converted site compares only against Turtwig/Chimchar/Piplup, so branch labels/trainer IDs/teams are untouched.

## 5. Design consequences
- Real result lives in `VAR_PLAYER_STARTER`; the Rival branch is a **pure function** of it (`MysteryStarter_GetRivalBranch`), so no extra var/save field.
- The stock hatch is Lv1 and logs a TV segment, so a dedicated starter path sets `hatchLevel = 5` (ordinary callers pass 0) and skips the TV segment; breeding code paths keep Lv1.
- Native hatch needs a real party egg → `GiveMysteryStarterEgg` inserts the Lv5-seeded egg, the hatch scene converts it in place (no duplicate insertion).
- The 3D Poké Ball models cannot display an egg; the chooser keeps its camera/navigation/cursor and renders three identical 2D egg sprites in the ball positions with the ball models hidden.
