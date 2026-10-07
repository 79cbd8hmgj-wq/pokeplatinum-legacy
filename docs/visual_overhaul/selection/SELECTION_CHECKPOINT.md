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

Trainer battle sprites (146 sets) and NPC/player field sprites (212 sheets) are now cataloged, curated and selected; details, scope rules and caveats in `../catalog_extensions/README.md`. Net new donor selections: 21 HGSS trainer sets preferred; NPC/player sprites yield no preferred donor (96 identical, 4 unverified-subject). 3D models, textures, menus/UI and battle HUD remain unstarted.
