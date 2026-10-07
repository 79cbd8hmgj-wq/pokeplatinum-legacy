# Donor Selection Checkpoint — framework + all subsystems first pass

Source commit: `main` @ `186dee00` (PR #65). Nothing here modifies Platinum visual resources.
Framework spec: `SELECTION_SCHEMA.md`. Machine-readable state: `SELECTION_STATUS.json`, `ledgers/*.json`, `IMPLEMENTATION_QUEUE.json`.

## Result

* 55,157 usable records → **8,223 candidate groups** → 1,730 targets across **14 subsystems**; all 14 have a ledger (rules v1.2).
* The 106 `decode_issue` records stay backlog; none blocks a selected group (selected groups with unresolved members are risk-flagged, preferred is forbidden).
* **Only one subsystem produced donor selections: `pokemon_battle_sprites` (HGSS, direct).** Everything else resolves to `platinum_native`.

| Subsystem | Outcome |
|---|---|
| pokemon_icons (pilot) | 544 targets all native. HGSS and Diamond icons are pixel-identical to Platinum for all 494 base species; 90 form icons match Platinum form folders by content. 4 HGSS-only form icons (members 547–550) have no Platinum target → `reference_only/no_native_target`; Diamond Snover/Rotom differ (Platinum is the later revision) → `reference_only`. |
| pokemon_battle_sprites | **26 preferred** HGSS species (art-diff, geometry-close, palette-safe), 537 alternates (palette-only, or art-diff needing geometry/palette review), Diamond = control (never selectable; 489 differ, 5 identical), 2 needs_evidence (`egg`, `shadow`). |
| trainer_battle_sprites | Diamond only (control) → `reference_only/control_unmeasured`; no HGSS donor in catalog (see gaps). |
| pokemon_animation_reference, battle_effects_particles, field_effects_overlays | Ranger 2 / PMD Sky = technique/reference by matrix → `reference_only` (policy). |
| field_environment_art | 1,372 reference (PMD/Ranger), 90 weak-evidence not_selected, **23 HGSS area previews `needs_evidence`**. |
| menu_ui_frames, pokedex_ui, party_summary_ui | HGSS convertible families `needs_evidence` (3 groups); Ranger UI not_selected (not named for the matrix row). |
| field_npc_player_sprites, battle_backgrounds_hud, title_and_presentation (Ranger), no_platinum_target | `not_selected/source_not_relevant_to_subsystem`. |

### 26 preferred battle-sprite donors (HGSS)

Venusaur, Metapod, Sandslash, Nidorino, Clefairy, Clefable, Jigglypuff, Gloom, Diglett, Dugtrio, Psyduck, Growlithe, Abra, Weepinbell, Tentacool, Voltorb, Electrode, Horsea, Magmar, Lapras, Ditto, Omanyte, Omastar, Larvitar, Pupitar, Tyranitar.

Each preferred group lists per-view relations in `ledgers/pokemon_battle_sprites.json` (`visual_evidence.detail.views`): only the art-diff views should be ported; identical/palette-only views stay native. All 26 require runtime validation (`runtime_qa` queue item) before any import, per `HGSS_BATTLE_SPRITE_RUNTIME_PILOT.md` rules.

## Implementation queue (`IMPLEMENTATION_QUEUE.md`)

1. implement — 26 HGSS battle-sprite species (score 86.7), gated by runtime QA.
2. evidence — `egg`/`shadow` battle forms, 23 HGSS area previews, 3 HGSS UI families.

## Coverage gaps (not blockers for the above)

The HGSS catalog (5,784 files) only roots `poketool/pokegra`, `poketool/icongra`, `fielddata/graphic/preview_graphic` and a few `graphic/` dirs. The matrix names HGSS as primary for trainer battle sprites, NPC/player field sprites, 3D field models/textures, menus/UI and battle HUD; **none of those HGSS assets are cataloged**, so those subsystems cannot yet receive an HGSS preferred donor. Extending the catalog is a targeted per-subsystem inventory (trainer sprites first), not a broad scan.

## Known limitations of this pass

* Gain is derived from render comparison (identical / palette-only / art-diff + static geometry triage) — it proves *difference*, not *better*. A preferred donor still needs the runtime/visual QA gate before import.
* Targets for Diamond/HGSS `otherpoke` forms are matched by explicit alias table in `evidence_battle_sprites.py`.
* Diamond `otherpoke` raw NCGR (213) is not compared (control, never selectable).

## Reproduce / validate

```
python3 tools/visual_overhaul/selection/build_candidate_groups.py
python3 tools/visual_overhaul/selection/evidence_icons.py --hgss-root <pokeheartgold> --diamond-root <pokediamond>
python3 tools/visual_overhaul/selection/evidence_battle_sprites.py --hgss-root <pokeheartgold> --diamond-root <pokediamond>
for s in <subsystem>; do python3 tools/visual_overhaul/selection/select_subsystem.py --subsystem $s; done
python3 tools/visual_overhaul/selection/build_queue.py && python3 tools/visual_overhaul/selection/build_status.py
python3 tools/visual_overhaul/selection/validate_selection.py   # CI: .github/workflows/donor-selection-validate.yml
```


## Update: HGSS sprite catalog gap passes

Trainer battle sprites (146 sets) and NPC/player field sprites (212 sheets) are now cataloged, curated and selected; details, scope rules and caveats in `../catalog_extensions/README.md`. Net new donor selections: 10 HGSS trainer sets preferred (corrected from 21, see catalog_extensions README: NCER VRAM-transfer decoder fix); NPC/player sprites yield no preferred donor (96 identical, 4 unverified-subject). 3D models, textures, menus/UI and battle HUD remain unstarted.


## Update: use-outcome model (donor contribution beyond replacement)

Selection now has a second axis (`USE_OUTCOMES.json`, `components/*.json`, `OUTCOME_STATUS.md`; spec in `SELECTION_SCHEMA.md` "Use outcomes"). Ledgers, groups, evidence and human review decisions are untouched (byte-identical, still reproducible); the six trainer `direct_replacement` verdicts and the pilot are unchanged.

First migration (`tools/visual_overhaul/selection/migrate_trainer_components.py`, trainers):
* Ace Trainer M/F stay `keep_platinum` as whole assets (`native_keep`) but now carry 4 **proposed** `component_donor` records (jacket fold/zip shading, fingerless gloves; hair highlight banding, collar/seam detail), each `derived` pixel use, awaiting human confirmation. Evidence image: `components/evidence/ace_trainer_*_platinum_vs_hgss.png`.
* Arcade Star and Young Couple: digest-bound `none_found` component reviews (Arcade Star frames 4-6 differ only by a ~1px row offset; Young Couple is a recolor) -> remain `native_keep`.
* Queue now has lanes A/B/C (B: Ace component review; C: technique pools for Ranger/PMD).

## Update: next subsystem — field_environment_art (HGSS map previews) under the use-outcome model

* The 23 `needs_evidence` HGSS preview groups were not renderable from the cataloged PNGs (those are NCGR tile sheets, scrambled). `hgss_preview_compose.py` (NSCR tilemap over the sheet) composes all 76 time-of-day variants; contact sheet in `review/environment_previews/`.
* Evidence (`evidence/field_environment_art.json`): Platinum has no area-preview screen (no map/area preview code in `src`/`include`; `res/graphics/map_popups` are 136x48 name signs; the only 256x192 PNGs are unrelated Battle Frontier backgrounds) -> `missing_in_native`: **no whole-asset replacement target exists** (`reference_only/no_native_target`, ledger regenerated; no other ledger changed). 23 `needs_evidence` -> 0.
* Under the new model these are component/technique sources (environmental_motif, material_treatment, palette, texture_region, layout), surfaced in queue lane B as `component_pool` (alongside other `no_native_target` donor pools). No use records were written: they need Platinum-side targets (see STOP below).

**STOP (design decision, not guessed):** `field_environment_art` has a single family target (`family:field_environment_art`) and no per-environment Platinum targets/native files, so a component/composite record cannot name an intended Platinum target + hash-pinned native base. Which Platinum environments should receive enhancement (e.g. Eterna Forest, Mt. Coronet caves, Snowpoint/Ice areas, lakes) and at what granularity is a design choice for the owner; once supplied, add a target alignment table (`alignment/`) and records via the existing schema.

## Update: opportunity classes (selection v3)

Canonical 8-class classification added (`OPPORTUNITY_CLASSES.json`, `opportunities/findings.json`, `OPPORTUNITY_REGISTER.*`; spec in `SELECTION_SCHEMA.md`). Replacement is now one class among eight; the queue is organised by opportunity type. Ledgers, rules, groups, evidence and components are unchanged.

Migrated (`migrate_opportunities.py`): 11 explicit findings + 4 existing component records + 32 ledger replacement verdicts + 2 none_found reviews. **Blocker:** the evidence for FireRed (palette sequences, interactive-object states), Emerald (field action, effect primitives), PMD Red, Crystal and Yellow Pikachu specifics was never committed to this repo and none of those games is a cataloged source (the cataloged PMD Sky has no assets matching 'status'). They are recorded as `prior_session_unrecorded` leads (low confidence, verify-first), not fabricated evidence. The location-preview finding is the only novel finding with committed evidence (23 HGSS preview groups, `missing_in_native`).

## Update: DS-only phase (supersedes the previous opportunity update's non-DS entries)

GBA/GBC findings moved to `opportunities/deferred/non_ds_findings.json` (preserved, unused). Active set rebuilt from DS evidence with targeted HGSS/PMD Sky/Ranger 2 verification; queue re-ranked across all eight classes by the weighted opportunity score. Details: `DS_OPPORTUNITY_REASSESSMENT.md`.

## Update: DS catalog mining pass

All 8,581 candidate groups were processed by deterministic mining passes (see `DS_OPPORTUNITY_MINING_SUMMARY.md`, `OPPORTUNITY_POOL_SUMMARY.md`); the implementation queue is rebuilt from the pool. Ledgers/groups/evidence unchanged. No implementation started.
