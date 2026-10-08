# Cross-generation implementation plan (final synthesis)

Status: **SYNTHESIS PROPOSAL / NOT HUMAN-APPROVED / NO PLATINUM SOURCE OR ASSET MODIFIED**
Baseline: `main` @ `81168942` (post PR #76). Machine-readable: `CROSS_GEN_OPPORTUNITY_RANKING.json`. Generator: `tools/visual_overhaul/selection/build_cross_gen_synthesis.py`.

Inputs are read, never rewritten: the DS evidence base (`OPPORTUNITY_POOL.json`, `IMPLEMENTATION_QUEUE.json`, `opportunities/findings.json`, `CROSS_DONOR_IMPLEMENTATION_PLAN.md`) and the frozen GBA/GBC pool (`gba_gbc/`). Donor identity stays attached to every member of every opportunity.

## 1. Answers

* **What should actually be implemented?** 16 ranked opportunities: 6 immediate candidates and 10 later/high-cost. 7 further clusters (19 DS queue items) are gated out of the ranking. The GBA/GBC donor layer adds **no new ranked opportunity**; it strengthens 4 existing ones.
* **Strongest ideas (canonical score):** Area/location preview card on map entry (4.143); HGSS overworld Pokemon sheet library (non-follower use, pilot subset first) (4.0); Battle terrain palette/tile-cycle service (water platform first) (3.786); Following-Pokemon overworld mechanic (3.714).
* **Best first slice:** `IO-PAL-CYCLE` - the battle-terrain palette-cycle service on the water platform (section 10).
* **Donor findings that informed design but must not be implemented:** all 14 GBA/GBC `reference_only` records and 2 `reject` records (Emerald, FireRed, Crystal, Yellow, plus the PMD Red engine/pixels record) and the DS `reference_only`/`reject` findings (section 9).
* **Duplicates/subsumed:** 9 decisions (section 8). Headline cases: FireRed map preview -> HGSS area preview; PMD Red status overlay -> PMD Sky status indicators; FireRed palette sequences -> PMD Sky palette cycling; Yellow reaction table -> follower mechanic.
* **Deferred, non-blocking:** Crystal angels motif, Ruby (both by project decision), plus the DS evidence gaps in section 6.

## 2. Frozen GBA/GBC donor status

| Donor | Pinned commit | Status | Records | Needs evidence |
|---|---|---|---|---:|
| emerald | `a81cfacb` | complete | 3 reference_only | 0 |
| firered | `037335f4` | complete | 4 reference_only | 0 |
| pmd_red | `aefe6a46` | complete | 1 novel_detail, 1 technique_donor (conditional), 1 reference_only | 0 |
| crystal | `3bc8daa4` | reviewed; **angels motif deferred** (non-blocking) | 3 reference_only, 1 reject, 1 needs_evidence | 1 |
| yellow | `e89ead15` | complete | 3 reference_only, 1 reject | 0 |
| ruby | `-` | **skipped by project decision** | none (not mined) | 0 |

Skipped and not blocking: B4.5 (Crystal angels evidence closure) and B5 (Ruby semantic delta). `ne:crystal/angels_motif_vs_platinum` is kept as an explicit deferred item (provisional `reference_only`, excluded from ranking) and is **not resolved** here.

### Pool validation (`validate_gba_gbc_pool.py`, passes)

| Check | Result |
|---|---|
| Duplicate finding ids / collisions with DS ids | none |
| Provenance | every record carries the pinned donor commit, verification facts, and evidence refs that exist in the repo |
| Taxonomy | all classes canonical; 2 records corrected (below); pixel policy and target policy hold for all 19 |
| `replacement_candidate` overuse | 0 of 19 GBA/GBC records. In the DS pool 32 of ~3,170 promoted records (about 1%); in this ranking 2 of 16 opportunities, both last and runtime-QA gated |
| `reference_only`/`reject` isolation | 16 GBA/GBC + 10 DS findings are listed in a separate register and cannot enter `ranked` |
| Needs evidence | 1 (Crystal angels), deferred; Ruby recorded as a non-blocking skip |

Corrections applied by `freeze_gba_gbc_pool.py` (no donor fact changed): `opp:pmd_red/battler_status_overlays` used target kind `battle_presentation_layer` and had null cost/feasibility, and `opp:pmd_red/battler_status_overlays/multi_status_cycling` used target kind `ui_behaviour`; both are now canonical (`none` + host system for the novel_detail, `system` for the technique donor, cost/risk as low/medium/high with the prose kept in `risk_note`, feasibility 2 to match the DS record they merge into). The two records also gained a `merge` pointer.

## 3. Method

* **Unit.** One implementation opportunity (IO) = one concept on one Platinum host. All 94 DS queue items and all 19 GBA/GBC records are accounted for exactly once: ranked member, corroboration, gated, or reference_only/reject/deferred.
* **Score.** Canonical 7-weight mean from `OPPORTUNITY_CLASSES.json`: visual impact 7, novelty 6, feasibility 5, reuse 4, cost 3 (inverted), risk 2 (inverted), slice 1; scale 1-5.
* **Anchor.** If a reviewed explicit DS finding exists for the concept, its scores are the IO's scores; otherwise the strongest mined library (mean of its top-5 records per dimension, no library-size bonus). Mined scores are auto-assigned and flagged as such (`score_basis`, `confidence`).
* **Corroboration never moves a score.** GBA/GBC evidence raises confidence and evidence breadth only; it cannot inflate a ranking.
* **Ranking vs. execution.** Rank is the pure canonical score. Execution order adds dependencies, spikes and risk (section 7), so the two differ on purpose.
* **DS queue scores differ.** `IMPLEMENTATION_QUEUE.json` uses a 10-dimension composite with a library-size bonus; DS queue ranks are kept as `ds_queue_rank` for traceability.
* **Gating.** A mined library whose pool is covered by an explicit `reference_only` finding is excluded unless a later reviewed decision (cross-donor slice plan S2/S3) chose a narrower technique use; those nuances are on the IO.

## 4. Final ranked implementation opportunities

| # | IO | Class | Score | Donors | Bucket | Wave | Exec. order | Cost / risk |
|---:|---|---|---:|---|---|---:|---:|---|
| 1 | `IO-PREVIEW` Area/location preview card on map entry | novel_capability | 4.143 | hgss, firered (corroborates) | immediate | 3 | 4 | high / medium |
| 2 | `IO-FOL-SHEETS` HGSS overworld Pokemon sheet library (non-follower use, pilot subset first) | novel_detail | 4.0 | hgss | immediate | 3 | 5 | medium / medium |
| 3 | `IO-PAL-CYCLE` Battle terrain palette/tile-cycle service (water platform first) | technique_donor | 3.786 | pmd_sky, firered (corroborates) | immediate | 1 | 1 | medium / medium-low |
| 4 | `IO-FOL-MECH` Following-Pokemon overworld mechanic | novel_capability | 3.714 | hgss, yellow (corroborates) | later | 5 | 10 | high / high |
| 5 | `IO-CARD` Still-scene card presentation (Solaceon News Press front page first) | novel_capability | 3.643 | ranger2, pmd_sky (supporting) | immediate | 2 | 2 | medium-high / medium |
| 6 | `IO-FX-PRIM` Ranger 2 effect primitives as per-move particle shapes | component_donor | 3.571 | ranger2 | later | 4 | 7 | medium / medium |
| 7 | `IO-TEX-HGSS` HGSS map texture-set regions | component_donor | 3.571 | hgss | later | 4 | 8 | medium / medium |
| 8 | `IO-STATUS` Persistent battler status-glyph overlay (volatile and stat conditions) | novel_detail | 3.393 | pmd_sky, pmd_red (corroborates) | immediate | 2 | 3 | medium / medium |
| 9 | `IO-TEX-RANGER` Ranger 2 field texture/material sets | technique_donor | 3.357 | ranger2 | later | 5 | 11 | high / medium |
| 10 | `IO-FX-SEQ` Ranger 2 multi-phase effect sequencing (launch/impact/embers) | technique_donor | 3.321 | ranger2 | later | 4 | 9 | low / low |
| 11 | `IO-NPC-COMP` HGSS NPC/player model components and enhancements | component_donor | 3.274 | hgss | later | 5 | 12 | low / low |
| 12 | `IO-MODELS` HGSS building/prop model library | component_donor | 3.25 | hgss | later | 5 | 13 | high / high |
| 13 | `IO-PKM-COMP` HGSS Pokemon battle-sprite components and composites | component_donor | 3.179 | hgss | later | 5 | 14 | high / medium |
| 14 | `IO-PKM-REPL` HGSS Pokemon battle-sprite whole replacements (26) | replacement_candidate | 2.814 | hgss | later | 6 | 15 | medium / medium |
| 15 | `IO-TRN-COMP` HGSS trainer-sprite component enhancement (Ace Trainer M/F pilot, then component library) | enhancement_candidate | 2.714 | hgss | immediate | 3 | 6 | low / low |
| 16 | `IO-TRN-REPL` HGSS trainer front-sprite whole replacements (6) | replacement_candidate | 2.679 | hgss | later | 6 | 16 | low / medium |

### Top 10

1. **`IO-PREVIEW`** - Area/location preview card on map entry - *novel_capability*, score 4.143, immediate, wave 3. A preview card (new Sinnoh artwork + name, time-of-day variants) shown beside the existing map-name popup. HGSS supplies the module structure and layout; FireRed corroborates and adds visit-gated hold, skip, per-area style and a second UI consumer.
2. **`IO-FOL-SHEETS`** - HGSS overworld Pokemon sheet library (non-follower use, pilot subset first) - *novel_detail*, score 4.0, immediate, wave 3. 572 species/form overworld sheets usable for event/cutscene/roaming Pokemon presence without a follower mechanic.
3. **`IO-PAL-CYCLE`** - Battle terrain palette/tile-cycle service (water platform first) - *technique_donor*, score 3.786, immediate, wave 1. Data-driven per-terrain palette ramp rotation (table + tick) so static battle platforms gain subtle constant motion; the art is re-indexed Platinum-native, no donor pixels.
4. **`IO-FOL-MECH`** - Following-Pokemon overworld mechanic - *novel_capability*, score 3.714, later, wave 5. Overworld follower object using the map-object system plus follower sheets. Highest visual impact, lowest feasibility.
5. **`IO-CARD`** - Still-scene card presentation (Solaceon News Press front page first) - *novel_capability*, score 3.643, immediate, wave 2. A reusable full-screen still card state (masthead, headline, illustration well, tabs) shown over the field script flow; Ranger 2 event bundles supply composition/state-variant structure only.
6. **`IO-FX-PRIM`** - Ranger 2 effect primitives as per-move particle shapes - *component_donor*, score 3.571, later, wave 4. Redraw selected Ranger primitives (fire/tornado/lightning/glow) into Platinum particle resources for specific moves.
7. **`IO-TEX-HGSS`** - HGSS map texture-set regions - *component_donor*, score 3.571, later, wave 4. Region-level reuse of HGSS NSBTX materials on Platinum map texture sets.
8. **`IO-STATUS`** - Persistent battler status-glyph overlay (volatile and stat conditions) - *novel_detail*, score 3.393, immediate, wave 2. A small animated glyph anchored to each battler while a condition is active, covering conditions Platinum never shows after the animation ends (confusion, infatuation, taunt-type, stat drops, screens). Redrawn Platinum-native.
9. **`IO-TEX-RANGER`** - Ranger 2 field texture/material sets - *technique_donor*, score 3.357, later, wave 5. Ranger 2 field texture and material-animation technique/components (905 ntfp groups remain unscoped).
10. **`IO-FX-SEQ`** - Ranger 2 multi-phase effect sequencing (launch/impact/embers) - *technique_donor*, score 3.321, later, wave 4. Re-express launch/impact/ember phase structure in anim.s sequencing for selected moves.

## 5. Implementation-ready shortlist (immediate candidates)

Nature = canonical class (novel capability / novel detail / technique donor / component donor / enhancement candidate / replacement candidate).

### 1. `IO-PAL-CYCLE` - Battle terrain palette/tile-cycle service (water platform first)

* **Nature:** technique_donor | **Score:** 3.786 (rank 3, mined library (top-5 record mean)) | **Wave:** 1 | **Slice:** S2
* **What:** Data-driven per-terrain palette ramp rotation (table + tick) so static battle platforms gain subtle constant motion; the art is re-indexed Platinum-native, no donor pixels.
* **Donors (scored):** pmd_sky [DS, primary]: `lib:pmd_sky/environmental_effects/pmd_mapbg_d/technique_donor/technique`, `lib:pmd_sky/environmental_effects/pmd_mapbg_v/technique_donor/technique`, `lib:pmd_sky/environmental_effects/pmd_mapbg_h/technique_donor/technique` +3 more
* **Corroboration (does not move the score):** firered `opp:firered/animated_palette_sequences` (reference_only, corroborates_timing_shape_only)
* **Likely files/subsystems:** `src/battle/terrain.c`, `src/unk_0201567C.c`, `res/graphics/battle/terrain`, `tools/visual_overhaul/generate_battle_terrain.py`
* **Depends on:** none; spikes/gates: spike: confirm OBJ/BG palette slot-7 write path and fade interaction in src/battle/terrain.c
* **Cost/risk:** medium / medium-low | **Pixel use:** none
* **Human review:** animated capture at game speed (day/evening/night), subtle-vs-busy, photosensitivity check
* **Rollback:** remove the tick call + table; revert the re-authored terrain PNG/PAL
* **Note:** Pool field_environment_art/pmd_sky is also covered by reference_only opp:pmd_sky/environment_and_title_backgrounds; that finding rejects the 2D tilemap art/motifs. Palette/tile animation as a technique was selected separately by the cross-donor slice plan (S2, mining/evidence/pmd_mapbg_bpa.json). Art stays excluded.

### 2. `IO-CARD` - Still-scene card presentation (Solaceon News Press front page first)

* **Nature:** novel_capability | **Score:** 3.643 (rank 5, mined library (top-5 record mean)) | **Wave:** 2 | **Slice:** S3
* **What:** A reusable full-screen still card state (masthead, headline, illustration well, tabs) shown over the field script flow; Ranger 2 event bundles supply composition/state-variant structure only.
* **Donors (scored):** ranger2 [DS, primary]: `lib:ranger2/transitions_presentation/ranger_event/event/technique_donor/technique`, `lib:ranger2/transitions_presentation/ranger_event/event/novel_capability/technique`; pmd_sky [DS, supporting]: `lib:pmd_sky/transitions_presentation/pmd_back_s/novel_capability/technique`, `lib:pmd_sky/transitions_presentation/pmd_back_s/technique_donor/technique`
* **Likely files/subsystems:** `res/field/scripts/scripts_solaceon_town_pokemon_news_press.s`, `src/bg_window.c`, `src/field_task.c`
* **Depends on:** none; spikes/gates: spike: choose BG layer/VRAM bank for a card while the field is locked (fallback: sub screen)
* **Cost/risk:** medium-high / medium | **Pixel use:** none
* **Human review:** art direction before engineering; then in-engine screenshots on both screens and text fit for all four articles
* **Rollback:** revert the 2-line script edit; new commands/resources become inert
* **Note:** Pool title_and_presentation/ranger2 is covered by the broad reference_only opp:ranger2/ui_and_story_backgrounds (no concrete element proposed). The later cross-donor slice plan S3 selected the event-card composition technique specifically; art stays excluded. PMD Sky BACK still cards are absorbed as technique corroboration only (S3 rejected them as an art source).

### 3. `IO-STATUS` - Persistent battler status-glyph overlay (volatile and stat conditions)

* **Nature:** novel_detail | **Score:** 3.393 (rank 8, reviewed explicit DS finding) | **Wave:** 2
* **What:** A small animated glyph anchored to each battler while a condition is active, covering conditions Platinum never shows after the animation ends (confusion, infatuation, taunt-type, stat drops, screens). Redrawn Platinum-native.
* **Donors (scored):** pmd_sky [DS, primary]: `opp:pmd_sky/battler_status_indicators`
* **Corroboration (does not move the score):** pmd_red `opp:pmd_red/battler_status_overlays` (novel_detail, corroborates_and_strengthens); pmd_red `opp:pmd_red/battler_status_overlays/multi_status_cycling` (technique_donor, conditional_sub_technique)
* **Likely files/subsystems:** `src/battle/healthbox.c`, `src/battle/battle_lib.c`, `src/battle/battle_display.c`, `src/battle_anim/script_funcs_status.c`
* **Depends on:** none; spikes/gates: spike: measure battle OAM/palette headroom (GBA_GBC_NEEDS_EVIDENCE defer:platinum/battle_overlay_oam_palette_headroom)
* **Cost/risk:** medium / medium | **Pixel use:** none (redraw)
* **Human review:** required: glyph set selection (which conditions), double-battle clutter, in-battle capture
* **Rollback:** remove the overlay task and glyph sheet; healthbox icon path is untouched
* **Note:** Merged record: the DS PMD Sky status-icon model and the GBA PMD Red trace are the same concept. PMD Red supplies traced mask/slot/timing behaviour and the Platinum comparison; the multi-status cycling rule is a conditional sub-technique (a static side-by-side row may beat it on DS screens). OAM headroom is unmeasured (cost/risk only).

### 4. `IO-PREVIEW` - Area/location preview card on map entry

* **Nature:** novel_capability | **Score:** 4.143 (rank 1, reviewed explicit DS finding) | **Wave:** 3 | **Slice:** S4
* **What:** A preview card (new Sinnoh artwork + name, time-of-day variants) shown beside the existing map-name popup. HGSS supplies the module structure and layout; FireRed corroborates and adds visit-gated hold, skip, per-area style and a second UI consumer.
* **Donors (scored):** hgss [DS, primary]: `opp:hgss/map_location_preview`, `lib:hgss/location_area/hgss_preview/technique_donor/technique`
* **Corroboration (does not move the score):** firered `opp:firered/map_location_preview` (reference_only, corroborates)
* **Likely files/subsystems:** `src/overlay005/map_name_popup.c`, `res/graphics/map_popups`, `src/map_header.c`
* **Depends on:** IO-CARD (soft: shares the still-card host)
* **Cost/risk:** high / medium | **Pixel use:** none
* **Human review:** required: art direction for 2-3 pilot locations before volume art; popup collision check
* **Rollback:** disable the entry trigger; popup path is unchanged
* **Note:** One record with multi-donor evidence: HGSS (primary) + FireRed map_location_preview (reference_only, subsumed).

### 5. `IO-FOL-SHEETS` - HGSS overworld Pokemon sheet library (non-follower use, pilot subset first)

* **Nature:** novel_detail | **Score:** 4.0 (rank 2, reviewed explicit DS finding) | **Wave:** 3
* **What:** 572 species/form overworld sheets usable for event/cutscene/roaming Pokemon presence without a follower mechanic.
* **Donors (scored):** hgss [DS, primary]: `lib:hgss/overworld_pokemon/hgss_follower_legendary/novel_detail/whole_asset`, `lib:hgss/overworld_pokemon/hgss_follower_species/novel_detail/whole_asset`, `lib:hgss/overworld_pokemon/hgss_follower_form/novel_detail/whole_asset` +2 more
* **Likely files/subsystems:** `res/graphics/field_sprites`, `src/map_object.c`
* **Depends on:** none; spikes/gates: spike: prove an overworld OBJ palette pipeline for a donor-style Pokemon sheet (unproven per cross-donor plan)
* **Cost/risk:** medium / medium | **Pixel use:** donor_pixels (whole assets)
* **Human review:** required: species identity and palette fit per sheet
* **Rollback:** remove added object sheets
* **Note:** Absorbs the four mined follower libraries (species, form, large, legendary).

### 6. `IO-TRN-COMP` - HGSS trainer-sprite component enhancement (Ace Trainer M/F pilot, then component library)

* **Nature:** enhancement_candidate | **Score:** 2.714 (rank 15, reviewed explicit DS finding) | **Wave:** 3 | **Slice:** S1
* **What:** Hand-authored shading/detail on the Platinum Ace Trainer front sprites derived from HGSS components (0 donor pixels), proving a component-transfer + review gate reusable for the 73-record hgss_front library.
* **Donors (scored):** hgss [DS, primary]: `lib:hgss/trainer_sprites/hgss_front/component_donor/component`, `lib:hgss/trainer_sprites/hgss_front/enhancement_candidate/composite_input`, `lib:hgss/trainer_sprites/hgss_back/component_donor/component` +2 more
* **Likely files/subsystems:** `res/trainers/classes/ace_trainer_male/front.png`, `res/trainers/classes/ace_trainer_female/front.png`, `tools/visual_overhaul/hgss_trainer_sprite_lib.py`, `tools/visual_overhaul/apply_platinum_sprite_pixel_patch.py`
* **Depends on:** none
* **Cost/risk:** low / low | **Pixel use:** derived
* **Human review:** required: final hand-authored sprites (1x/4x, in-battle, M and F); per-component accept/reject
* **Rollback:** restore the two front.png files
* **Note:** Explicit reviewed findings (the Ace Trainer pair) anchor the score; the 73-record component library and 15 composite inputs are scope expansion after the gate is proven. Canonical score is low (visual impact 2); it is sequenced first-wave for infrastructure and zero risk, not for impact.

### Later / high-cost candidates

| IO | Nature | Score | Why later | Depends on / gate | Likely files |
|---|---|---:|---|---|---|
| `IO-FX-PRIM` Ranger 2 effect primitives as per-move particle shapes | component_donor | 3.571 | Redraw selected Ranger primitives (fire/tornado/lightning/glow) into Platinum particle resources for specific moves. | design step: choose per-move Platinum targets (none chosen yet) | res/moves, src/particle_system.c, res/graphics/battle |
| `IO-TEX-HGSS` HGSS map texture-set regions | component_donor | 3.571 | Already palette-graded in G4/G7.6; a region transplant is a second, riskier pass over the same assets (cross-donor plan). | none | res/field/area_data, res/field/props |
| `IO-FX-SEQ` Ranger 2 multi-phase effect sequencing (launch/impact/embers) | technique_donor | 3.321 | G5 already applied selective impact staging; low novelty (cross-donor plan). | none | res/moves |
| `IO-FOL-MECH` Following-Pokemon overworld mechanic | novel_capability | 3.714 | Yellow partner reaction table (reference_only) informs friendship-keyed reaction design; Platinum already has friendship reactions in the [...] | IO-FOL-SHEETS; spike: prove an overworld OBJ palette pipeline for a donor-style Pokemon sheet (unproven [...] | src/map_object.c, src/map_object_move.c, src/player_avatar.c |
| `IO-TEX-RANGER` Ranger 2 field texture/material sets | technique_donor | 3.357 | Needs NSBTA/3D material authoring; no pipeline (cross-donor plan). | scoping: 905 ntfp groups unscoped | res/field/area_data |
| `IO-NPC-COMP` HGSS NPC/player model components and enhancements | component_donor | 3.274 | Small component/enhancement set on existing Platinum NPC sprites. | none | res/graphics/field_sprites |
| `IO-MODELS` HGSS building/prop model library | component_donor | 3.25 | Absorbs 20 mined model libraries for exterior/interior/prop families. | spike: NSBMD prop authoring pipeline does not exist (G7.6 records this) | res/field/props, res/field/area_data |
| `IO-PKM-COMP` HGSS Pokemon battle-sprite components and composites | component_donor | 3.179 | Component and composite use of HGSS battle sprites on existing Platinum Pokemon sprites. | IO-TRN-COMP (review gate proven first) | res/pokemon, src/pokemon_sprite.c |
| `IO-PKM-REPL` HGSS Pokemon battle-sprite whole replacements (26) | replacement_candidate | 2.814 | Replacement is one outcome among eight, not the primary one. | gate: runtime QA before any replacement import | res/pokemon, src/pokemon_sprite.c |
| `IO-TRN-REPL` HGSS trainer front-sprite whole replacements (6) | replacement_candidate | 2.679 | Whole-asset trainer replacements ledgered as preferred; gated by runtime QA. | gate: runtime QA before any replacement import | res/trainers/classes |

## 6. Deferred, gated, reference-only and evidence gaps

### Gated out of the ranking (DS mined libraries)

| Cluster | DS queue items | Records | Reason |
|---|---:|---:|---|
| `GX-ICONS-EXTRA` HGSS 'icon_extra' icons (4 auto-mined records) | 1 | 4 | no Platinum target or host system is named for these auto-mined records (the taxonomy requires a host_system for novel_detail); identify what the icons are before ranking |
| `GX-TRN-NOVEL` HGSS-only trainer classes with no Platinum counterpart | 2 | 31 | opp:hgss/npc_trainer_variety_pool (reference_only: no Platinum target) |
| `GX-NPC-NOVEL` HGSS-only NPC models with no Platinum counterpart | 1 | 76 | opp:hgss/npc_trainer_variety_pool (reference_only: no Platinum target) |
| `GX-RANGER-UI` Ranger 2 interface pulses/glows, menu parts and capture backgrounds | 4 | 129 | opp:ranger2/ui_and_story_backgrounds (reference_only) and G7 owns Platinum UI; reopening G7 needs an owner decision |
| `GX-RANGER-POKE` Ranger 2 Pokemon animation/frames | 2 | 97 | opp:ranger2/pokemon_sprite_frames (reference_only: scale mismatch, Platinum Pokemon presentation) |
| `GX-PMD-BG-ART` PMD Sky 2D map-background art | 4 | 65 | opp:pmd_sky/environment_and_title_backgrounds (reference_only: 2D tilemap art does not map to Platinum 3D; colour/motif reference only) |
| `GX-PMD-GROUND` PMD Sky GROUND overlay/object animation | 5 | 106 | opp:pmd_sky/ground_overlay_sprites (reference_only until WAN decoded; no renderer, no visual evidence) |

### Unresolved but non-blocking evidence gaps

| Id | Donor | Status | Affects | Note |
|---|---|---|---|---|
| `ne:crystal/angels_motif_vs_platinum` | crystal | deferred_non_blocking | none ranked | Closure (B4.5) skipped by project decision. Provisional reference_only; excluded from ranking. If reopened: one five-move key-frame sheet; novel_detail if Platinum lacks a recurring figure. |
| `defer:ruby/semantic_delta` | ruby | skipped_by_project_decision | none ranked | B5 not run. Emerald closed with 0 promoted records, so no ranked item depends on Ruby. |
| `defer:platinum/battle_overlay_oam_palette_headroom` | pmd_red | deferred_non_blocking | IO-STATUS cost/risk | Becomes the first step of the IO-STATUS spike. |
| `gap:ds/pmd_wan_decoder` | pmd_sky | open_non_blocking | GX-PMD-GROUND | No GROUND .wan renderer; the pool stays gated. |
| `gap:ds/pmd_manpu_effect_bin` | pmd_sky | open_non_blocking | IO-STATUS (donor art only) | manpu_*/effect.bin uncataloged; moot because the glyphs are redrawn Platinum-native (PMD Red already shows the art shape). |
| `gap:ds/hgss_field_models` | hgss | open_non_blocking | IO-MODELS, IO-TEX-HGSS | Largest unexamined DS area: map building models not present as discrete files in the decomp checkout. |
| `gap:ds/ranger_ntfp_scope` | ranger2 | open_non_blocking | IO-TEX-RANGER | 905 field ntfp groups unscoped. |
| `gap:ds/ranger_per_move_targets` | ranger2 | open_non_blocking | IO-FX-PRIM | Per-move Platinum targets not chosen. |

None of these blocks an immediate candidate. `defer:platinum/battle_overlay_oam_palette_headroom` becomes the first step of the `IO-STATUS` spike.

## 7. Waves, dependencies and execution order

### Wave 1 - prove the first runtime service

One engineering slice plus the spikes and art-direction reviews every later wave needs.

1. `IO-PAL-CYCLE` (technique_donor, 3.786)

### Wave 2 - new presentation layers

Two new Platinum-native layers whose hosts are decided by Wave 1 spikes.

2. `IO-CARD` (novel_capability, 3.643)
3. `IO-STATUS` (novel_detail, 3.393)

### Wave 3 - build on the Wave 2 hosts / authoring tracks

One item that reuses a Wave 2 host (area preview), plus authoring-bound tracks with no engineering dependency (overworld sheet pilot, Ace Trainer shading).

4. `IO-PREVIEW` (novel_capability, 4.143); depends on IO-CARD (soft: shares the still-card host)
5. `IO-FOL-SHEETS` (novel_detail, 4.0)
6. `IO-TRN-COMP` (enhancement_candidate, 2.714)

### Wave 4 - per-asset and per-move work (later)

Valid but needs a design step or is a second pass over already-graded assets.

7. `IO-FX-PRIM` (component_donor, 3.571)
8. `IO-TEX-HGSS` (component_donor, 3.571)
9. `IO-FX-SEQ` (technique_donor, 3.321)

### Wave 5 - high-cost or unscoped (later)

Needs a missing pipeline, unscoped evidence, or low-value library work.

10. `IO-FOL-MECH` (novel_capability, 3.714); depends on IO-FOL-SHEETS
11. `IO-TEX-RANGER` (technique_donor, 3.357)
12. `IO-NPC-COMP` (component_donor, 3.274)
13. `IO-MODELS` (component_donor, 3.25)
14. `IO-PKM-COMP` (component_donor, 3.179); depends on IO-TRN-COMP (review gate proven first)

### Wave 6 - replacement candidates (runtime-QA gated)

Whole-asset replacement is one outcome among eight; nothing here starts before runtime QA.

15. `IO-PKM-REPL` (replacement_candidate, 2.814)
16. `IO-TRN-REPL` (replacement_candidate, 2.679)

**Parallel tracks that need no engineering (start in Wave 1):** (a) card art-direction review for `IO-CARD`; (b) 2-3 pilot location previews art-direction for `IO-PREVIEW`; (c) four Platinum-side spikes: palette write path (`IO-PAL-CYCLE`), card BG layer (`IO-CARD`), battle OAM/palette headroom (`IO-STATUS`) and the overworld OBJ palette pipeline (`IO-FOL-SHEETS`).

### Dependency graph

```
IO-PAL-CYCLE   (none; spike: palette write path)
IO-CARD        (none; spike: BG layer)  ----soft----> IO-PREVIEW
IO-STATUS      (none; spike: OAM headroom)
IO-FOL-SHEETS  (spike: OBJ palette pipeline) ----> IO-FOL-MECH
IO-TRN-COMP    (none; review gate) ----> IO-PKM-COMP
```

## 8. Duplicates and subsumption

| Id | Kept | Absorbed | Decision |
|---|---|---|---|
| D1 | IO-PREVIEW | opp:firered/map_location_preview; lib hgss_preview (23 areas) -> explicit opp:hgss/map_location_preview | One area-preview opportunity. FireRed was already subsumed by the HGSS concept (B2); it stays reference_only and is attached as corroboration (visit-gated hold 120 vs 40 frames, B skips, per-area style, second UI consumer). The mined HGSS preview library is the same 23 areas as the explicit finding. |
| D2 | IO-STATUS | opp:pmd_red/battler_status_overlays; opp:pmd_red/battler_status_overlays/multi_status_cycling | PMD Red and PMD Sky are the same concept (battler-local, mask-driven status indicator). One record: the DS finding stays the anchor, PMD Red strengthens it with traced behaviour and the Platinum comparison; the cycling rule is a conditional sub-technique. No duplicate inserted. |
| D3 | IO-PAL-CYCLE | opp:firered/animated_palette_sequences; 6 PMD Sky mapbg technique libraries | FireRed palette sequences are reference_only (Platinum has native hosts); they only corroborate timing shape for the PMD Sky technique. Six mined libraries become one palette-cycle service. |
| D4 | IO-FOL-SHEETS | 4 mined overworld_pokemon libraries (species, form, large, legendary) | The explicit 572-sheet library finding subsumes the four mined follower-sheet libraries. The follower mechanic stays a separate, dependent opportunity (IO-FOL-MECH). |
| D5 | IO-FOL-MECH | opp:yellow/pikachu_presentation/partner_reaction_table | Yellow's happiness x mood reaction table informs reaction design only (reference_only); Platinum already has friendship reactions in the Poketch Friendship Checker. |
| D6 | IO-CARD | 2 PMD Sky pmd_back_s still-card libraries | Same host (field/title transition and event presentation) and same technique; PMD art is excluded (style mismatch, S3), so they corroborate the Ranger-derived composition rather than compete. |
| D7 | IO-TRN-COMP | opp:trainer/tc_ace_trainer_{male,female}/enhancement; uc:trainer_battle_sprites/tc_ace_trainer_*/{01,02}; 3 hgss_front/hgss_back component and composite libraries | One enhancement path: the reviewed Ace Trainer pair is the pilot; library members are scope expansion. |
| D8 | IO-MODELS / IO-TEX-HGSS | 21 model items; 14 texture-set items | Per-family mined libraries collapse into the two explicit library findings; they are not independent implementation units. |
| D9 | (excluded) | Emerald field_action_choreography; Emerald/FireRed environment & interactive-object effects; Crystal move sequencing and battle transitions; Yellow starter entrance/exit and transitions | Platinum already supersedes these (HM cut-in with Fly path, fldeff.narc families, 31 encounter effects, per-move anim.s). Kept reference_only, excluded from ranking. |

## 9. Informed design but not to be implemented (reference_only / reject)

Kept for design understanding with donor identity; never ranked.

| Id | Gen | Donor | Class | Subject | Merge |
|---|---|---|---|---|---|
| `opp:diamond/control_reference` | DS | diamond | reference_only | Diamond as Platinum control/reference |  |
| `opp:hgss/camera_viewfinder` | DS | hgss | reference_only | HGSS photo-camera viewfinder frame |  |
| `opp:hgss/land_data_terrain` | DS | hgss | reference_only | HGSS land-data terrain models (676 maps, per-map NSBMD) |  |
| `opp:hgss/npc_trainer_variety_pool` | DS | hgss | reference_only | HGSS-only NPC/trainer sprites (111 field sheets, 68 trainer classes) |  |
| `opp:hgss/ui_dex_party_reference` | DS | hgss | reference_only | HGSS Pokedex/party-list UI graphics |  |
| `opp:hgss_diamond/icons_identical` | DS | hgss | reject | HGSS/Diamond Pokemon icons are pixel-identical to Platinum |  |
| `opp:pmd_sky/environment_and_title_backgrounds` | DS | pmd_sky | reference_only | PMD Sky dungeon/ground backgrounds and title BACK art |  |
| `opp:pmd_sky/ground_overlay_sprites` | DS | pmd_sky | reference_only | PMD Sky GROUND animated sprites (523 groups) |  |
| `opp:ranger2/pokemon_sprite_frames` | DS | ranger2 | reference_only | Ranger 2 Pokemon field sprite frames (35k frames, 282 species) |  |
| `opp:ranger2/ui_and_story_backgrounds` | DS | ranger2 | reference_only | Ranger 2 interface, menu, event and ending art |  |
| `opp:crystal/battle_anim_artwork` | GBA/GBC | crystal | reference_only | Crystal battle-animation primitive banks aeroblast, globe, noise, reflect, rope, shapes, shine, web, [...] |  |
| `opp:crystal/battle_anim_artwork/wave_bank_orphan` | GBA/GBC | crystal | reject | Crystal wave bank (BATTLE_ANIM_GFX_WAVE, 18 tiles) and the misleadingly named BATTLE_ANIM_OBJ_WAVE |  |
| `opp:crystal/battle_anim_choreography/battle_transition` | GBA/GBC | crystal | reference_only | Crystal battle transition: four starting points (cave or not x lead level+3 vs enemy) feeding four outros |  |
| `opp:crystal/battle_anim_choreography/move_sequencing` | GBA/GBC | crystal | reference_only | Crystal move scripts for the bound primitive moves, per-turn residual animations and the BG/palette [...] |  |
| `opp:emerald/environment_effect_primitives` | GBA/GBC | emerald | reference_only | Emerald generic field primitives (shadow, grass, footprints/tracks, splash/ripple, dust, sparkle): [...] |  |
| `opp:emerald/environment_effect_primitives/location_specific` | GBA/GBC | emerald | reference_only | Emerald field primitives tied to Hoenn-specific locations or mechanics (carved out of [...] |  |
| `opp:emerald/field_action_choreography` | GBA/GBC | emerald | reference_only | Emerald field-move 'show mon' banner and per-move avatar choreography (Surf/Fly/Waterfall/Dive/Teleport) |  |
| `opp:firered/animated_palette_sequences` | GBA/GBC | firered | reference_only | FireRed Pokemon League timed BG-palette lighting sequences (Elite Four 12 palettes, Champion room 9 palettes) | cross-gen IO palette-cycle service (DS libraries pmd_mapbg_*) |
| `opp:firered/interactive_object_states` | GBA/GBC | firered | reference_only | FireRed Deoxys triangle: variable-driven staged palette feedback on an interactable object (generic half [...] |  |
| `opp:firered/interactive_object_states/location_specific` | GBA/GBC | firered | reference_only | FireRed Birth Island Deoxys triangle puzzle + rock movement/destruction choreography (event-specific [...] |  |
| `opp:firered/map_location_preview` | GBA/GBC | firered | reference_only | FireRed dungeon/forest location-preview screens (tiles+tilemap+palette per map section), shown on entry [...] | opp:hgss/map_location_preview |
| `opp:pmd_red/battler_status_overlays/gba_engine_and_pixels` | GBA/GBC | pmd_red | reference_only | PMD Red GBA-specific implementation (OAM shape/size switch, fixed VRAM tile index 0x32B, 4-phase VRAM [...] |  |
| `opp:yellow/pikachu_presentation/battle_transitions_special_effects` | GBA/GBC | yellow | reference_only | Yellow battle transitions (8 bit-selected entries, 7 distinct routines) and the 24-entry special-effect [...] |  |
| `opp:yellow/pikachu_presentation/partner_reaction_table` | GBA/GBC | yellow | reference_only | Pikachu mood x happiness portrait reaction selection (7 happiness bands x 5 mood columns -> 18 of 30 [...] |  |
| `opp:yellow/pikachu_presentation/starter_entrance_exit` | GBA/GBC | yellow | reference_only | Starter Pikachu battle entrance (column wipe instead of poof and ball send-out), slide-off retreat, and [...] |  |
| `opp:yellow/pikachu_presentation/surfing_pikachu` | GBA/GBC | yellow | reject | Surfing Pikachu minigame graphics (gfx/surfing_pikachu/*) and tilemaps |  |

## 10. Recommended execution order and first slice

| Order | IO | Why here |
|---:|---|---|
| 1 | `IO-PAL-CYCLE` | best first slice: no dependency, one small runtime spike, visible in every battle, produces a reusable service |
| 2 | `IO-CARD` | highest-novelty new screen type; art direction runs in Wave 1 so engineering starts with an approved look |
| 3 | `IO-STATUS` | new gameplay-facing feedback; starts with the OAM headroom spike |
| 4 | `IO-PREVIEW` | top canonical score but needs new art and a clean coexistence with the map-name popup; follows the card host |
| 5 | `IO-FOL-SHEETS` | ranks 2nd, but the OBJ palette pipeline is unproven; do a pilot subset after the spike |
| 6 | `IO-TRN-COMP` | cheap, risk-free authoring task that proves the component review gate; low impact, so it is filler, not a driver |
| 7 | `IO-FX-PRIM` | valid, but per-move targets have not been chosen |
| 8 | `IO-TEX-HGSS` | second pass over already graded assets |
| 9 | `IO-FX-SEQ` | G5 already applied the idea |
| 10 | `IO-FOL-MECH` | highest impact, lowest feasibility; needs sheets first |
| 11 | `IO-TEX-RANGER` | 905 groups unscoped |
| 12 | `IO-NPC-COMP` | small, auto-scored |
| 13 | `IO-MODELS` | no NSBMD authoring pipeline |
| 14 | `IO-PKM-COMP` | hundreds of hand-reviewed sprites; needs the review gate first |
| 15 | `IO-PKM-REPL` | runtime QA gate |
| 16 | `IO-TRN-REPL` | runtime QA gate |

### Best first implementation slice: `IO-PAL-CYCLE`

* Canonical score 3.786 (rank 3), the top-scoring item with no dependency, no new art direction and no donor pixels. Evidence: PMD Sky BPA palette animation (`mining/evidence/pmd_mapbg_bpa.json`), with FireRed's Elite Four/Champion palette sequences corroborating the timing shape.
* Scope: `src/battle/terrain.c` tick + data table, re-indexed water platform (day/evening/night), `generate_battle_terrain.py` extension. Rollback: remove one tick call and revert one PNG/PAL.
* Gate before merge: animated capture at game speed, subtle-vs-busy and photosensitivity review.
* **Differs from the earlier proposal.** `CROSS_DONOR_IMPLEMENTATION_PLAN.md` ordered S1 (Ace Trainer shading) first. Under the canonical weights S1 scores 2.714 (visual impact 2, novelty 2, rank 15 of 16), and the review gate it proves mainly benefits lower-value component work. S1 moves to Wave 3 as a parallel authoring task; S2 leads. S3 (card) and S4 (area preview) keep the earlier relative order.

## 11. Scope guard

No file under `res/` or `src/` was modified. `PHASE_SCOPE.json` still governs the DS-only register/queue and is unchanged; this layer is separate and read-only over them. DS evidence files (`OPPORTUNITY_POOL.json`, `IMPLEMENTATION_QUEUE.json`, `findings.json`, ledgers) and Ruby are untouched; the Crystal angels item is not resolved. Added/updated: this plan, `CROSS_GEN_OPPORTUNITY_RANKING.json`, the four GBA/GBC artifacts, and the generator/validator scripts under `tools/visual_overhaul/selection/`.
