# Availability Implementation Report (ordinary wild availability)

Branch: `claude/platinum-availability-impl-c651fe` · base commit `cb420c0d` (main) · status: **IMPLEMENTED + L2 BUILD VERIFIED (Rev 0 / Rev 1); no runtime (L4) verification**

Authority used: `docs/overhaul/AVAILABILITY_ARCHITECTURE.md` as the approved implementation basis (see D4). Section 5
(`USER APPROVAL REQUIRED`) was **not** decided; those 28 families are reserved as `USER_DECISION_REQUIRED`.
All exact map/slot/level/percentage values are `PROVISIONAL PLACEMENT` and need design review (architecture doc s.8).

## 1. What changed

| Area | Result |
|---|---|
| Manifests | `availability_families.json`, `encounter_zones.json`, `wild_encounters.json`, `special_systems.json` (+ `AVAILABILITY_SOURCE_AUDIT.md`) |
| Encounter data | 148 files in `res/field/encounters/` (85 land/cave maps retabled, 30 maps with Surf/Old/Good Rod changes, dual-slot neutralised on 134 land maps, Great Marsh Dex arrays unified). Nothing outside `res/field/encounters/`, `docs/overhaul/`, `tools/overhaul/` changed (checked by `semantic_diff.py`). |
| Families | 247 evolution families derived from live `res/pokemon/*/data.json`: 212 nonlegendary + 35 Legendary/Mythical (`RESERVED_LATER_PHASE`). 184 nonlegendary families have a verified deterministic PRE_E4 wild path; 28 are `USER_DECISION_REQUIRED`. |
| Species coverage (of 493) | 384 wild-reachable PRE_E4, 74 in `USER_DECISION_REQUIRED` families, 35 reserved (Legendary/Mythical). Babies with no wild entry (Cleffa, Igglybuff) are obtained by breeding a placed family member. |
| Bands implemented | E0, E1, M1, M2, L1, L2, P0 land/cave; water methods for E1–L2 maps; P1 = postgame maps left as evolved ecology (only the global dual-slot neutralisation touches them). |
| Special systems | Dual-slot → neutralised; Radar, swarm, Honey, Trophy Garden, Great Marsh → bonus-only with a validated fixed fallback for every species; Great Marsh before/after Dex arrays unified. |

## 2. USER_DECISION_REQUIRED (reserved, not designed)

| Key | Families |
|---|---|
| STARTER_DISTRIBUTION | bulbasaur, charmander, squirtle, chikorita, cyndaquil, totodile, treecko, torchic, mudkip, turtwig, chimchar, piplup |
| FOSSIL_ACQUISITION | omanyte, kabuto, aerodactyl, lileep, anorith, cranidos, shieldon |
| SPIRITOMB_QUEST | spiritomb (current source still has the multiplayer-counter dependency) |
| ROTOM_UNLOCK_PRESENTATION | rotom |
| TYROGUE_GIFT_VS_HABITAT | tyrogue / Hitmons |
| HAPPINY_CHANSEY_GIFT_VS_HABITAT | happiny / chansey (existing 4 %/1 % Route 209/210 entries and Trophy Garden dailies left exactly as they were) |
| EEVEE_GIFT_VS_WILD_BALANCE | eevee |
| PORYGON_ACQUISITION_PRESENTATION | porygon |
| RIOLU_REPEATABILITY | riolu |
| CASTFORM_GIFT_VS_HABITAT | castform |
| FEEBAS_IMPLEMENTATION | feebas (current source still has the random-tile dependency) |

Also left undecided (no secondary habitat added): pseudo-legendary catch-up habitats (Dratini, Larvitar, Bagon, Gible, Beldum
get only their primary matrix habitat) and the National Dex UI timing (no UI/script change).
The validator proves that no occurrence of a `USER_DECISION_REQUIRED` species was added, moved or removed in any table.

## 3. Discrepancies and implementation choices (please review)

| # | Item |
|---|---|
| D1 | **Super Rod is post-Hall of Fame** (Fight Area fisherman). The matrix puts Clamperl (M2) and Relicanth (L2) on Super Rod; a PRE_E4 entry cannot. Clamperl is on Good Rod at Canalave (15 %) and Route 223; Relicanth on Good Rod at Sunyshore (15 %). Super Rod tables are untouched. |
| D2 | **Dual-slot is neutralised**, not kept as a bonus: every cartridge array mirrors land slots 8/9. The architecture permits "bonus only"; neutralising is the zero-risk reading. A bonus can be restored by editing `special_systems.json → dual_slot` (arrays of species that also have a fixed path). |
| D3 | **Trophy Garden dailies remain National-Dex-gated in code** (`WildEncounters_ReplaceTrophyGardenEncounters`). They are bonus-only and every Garden species has a fixed fallback, so completion is unaffected; removing the gate is a code change entangled with the undecided Dex-timing item. |
| D4 | `AVAILABILITY_ARCHITECTURE.md` still carries the header "DRAFT PLAN — requires user approval" and s.8 says exact map/slot/level/percent manifests need separate review before gameplay implementation. I implemented on the explicit instruction in the task; the lifecycle header was not edited. |
| D5 | Four families first appear later than the matrix "Earliest" band (later is allowed): igglybuff/togepi (the HEARTH maps are M1), aron (Iron Island is M2; Fuego's six ≥10 % slots are full), dratini (Coronet 4F water is L1: Rock Climb gate). No family appears *earlier* than its matrix band (validator rule). |
| D6 | **Great Marsh is Safari-format**, so a family may not rely on it alone ("Safari capture is not sole path"). The validator requires a non-Safari fixed path; the marsh-only families (exeggcute, kangaskhan, tropius, carnivine, tangela, yanma, grimer, volbeat, illumise) got one on Route 212 N/S, Route 213 and Valor Lakefront (M1). |
| D7 | Mt. Coronet B1F is banded **P0** (its water route is Waterfall-gated; HM07 is given in Sunyshore). No requirement relies on it. Gating by HMs was read from scripts, not runtime-verified. |
| D8 | No machine-readable Pass A evolution manifest exists yet. Family components are the connected components of the **live** evolution edges, which do not depend on evolution *methods*, so Pass A method changes cannot alter membership. Nothing in this work touches evolution data. |
| D9 | Radar arrays on retabled maps still hold some evolved species (bonus-only). Not changed (would be a design choice). |
| D10 | Level policy: every land slot keeps the base-commit level of the same slot (route level curve preserved), water slots keep base level ranges. |
| D11 | Trophy Garden / Great Marsh / HM-gated map access was read from scripts only; Plusle/Minun/Ditto-core paths rely on the Garden being reachable pre-E4 (runtime check pending). |

## 4. Validation commands and results

All commands run from the repo root; `A=tools/overhaul/availability`.

| Check | Command | Result |
|---|---|---|
| Manifest regeneration | `python3 $A/build_families.py; python3 $A/build_wild_manifest.py; python3 $A/build_special_manifest.py; python3 $A/build_zones.py` | 247 families, 94 maps / 1532 entries, 185 zone rows |
| Validators, pre-apply proof | `python3 $A/validate_availability.py --state manifest` | 0 failures, 0 warnings; 184 verified families |
| Validators, post-apply proof | `python3 $A/validate_availability.py --state live` | 0 failures, 0 warnings; 184 verified families |
| Validators have teeth | `python3 $A/test_validators.py` | 12/12 mutation cases rejected (no path, <5 %, night-only, dual-slot, Dex arrays, decision family placed, legendary placed, density, too-early, Super-Rod-only, stale fallback, Safari-only) |
| Apply is idempotent / guarded | `python3 $A/apply_wild_encounters.py --bands all` (run twice per group) | second run changes 0 files; guard mismatch aborts untouched |
| Semantic diff | `python3 $A/semantic_diff.py --bands all` | 0 discrepancies; no file changed outside allowed scope |
| Built data = manifest | `python3 $A/verify_built_encounters.py --build <BUILD>` | 189 compiled tables, 0 mismatches (Rev 1) |
| Rev 1 build | `make rom ROM_REVISION=1 BUILD=/var/tmp/pp_r1` | success after every commit group and on the final state |
| Rev 0 build | `make configure ROM_REVISION=0 BUILD=/var/tmp/pp_r0 && make rom ROM_REVISION=0 BUILD=/var/tmp/pp_r0` | success (final state, full build); `verify_built_encounters.py --build /var/tmp/pp_r0`: 189 tables, 0 mismatches |

Density: every authored land table is within 6–8 families (connectors ≤ 5, signature ≤ 9) and every water method ≤ 4
families; adjacent non-continuous habitats share ≤ 50 % of their families (validator V8).

## 5. Not done / not claimed

* **No runtime verification.** Build success and "compiled tables equal the manifest" are L2/L3 evidence only. Suggested L4
  checks: Route 201/204/205 grass, one Surf and one Good Rod map per band, day/night at slot 3 (Lake Verity hoothoot at night, Acuity Lakefront snorunt at night), a former dual-slot species (e.g. Vulpix/Growlithe on Route 207), Great Marsh fixed cores, Radar patch species.
* Legendary/Mythical content, trainer/economy/breeding work and C1/C2 items are untouched.
