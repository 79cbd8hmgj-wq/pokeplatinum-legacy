# B1 — Existing donor database integration for cinematic battle work

**Source-backed integration register, 2026-10-10.** This is a development input, **not proof that donor sprites or particle textures have been installed**.

## Existing database is the primary visual ingredient library

- `docs/visual_overhaul/DONOR_ASSET_CATALOG.md`: 64,841 indexed assets from Diamond, HGSS, PMD Sky, Ranger 2. Its initial review-status report is a historical snapshot, **not** the latest verdict.
- `docs/visual_overhaul/DONOR_CURATION_HANDOFF.md`: later resolved curation records across all 64,841 assets: **55,157 usable, 9,578 rejected, 106 decode issues**. "Usable" indicates recovered/reviewed provenance, **not** drop-in compatibility with Platinum's battle engine.
- `docs/visual_overhaul/selection/OPPORTUNITY_POOL_SUMMARY.md`: **636 battle-effects opportunity records**, of which 346 are promoted and 290 deferred in that snapshot; 845 UI/menu/HUD records, and 96 environmental-effects records. Opportunity records are not necessarily unique underlying images or implemented features.
- `docs/visual_overhaul/selection/ledgers/battle_effects_particles.json` and `selection/mining/passes/battle_effects.json`: primary source of per-effect donor ranking, provenance and classifications.
- `docs/visual_overhaul/selection/opportunities/evidence/ranger2_effect_ui_sample.png` and `selection/DS_OPPORTUNITY_REASSESSMENT.md`: recovered Ranger 2 fire/tornado/lightning/glow primitives and phase structure. The specific Platinum move-target assignments are **not yet selected** in the source audit.
- `docs/visual_overhaul/POKEMON_OPAL_ASSET_DIRECTION.md`: decisions: preserve, replace, enhance, composite, animate, create, discard. Composite multiple sources where useful; do not default to wholesale copying or a mandatory import of an entire donor library.
- `docs/visual_overhaul/OPAL_POST_S2_DONOR_ROADMAP.md`: post-S2 opportunity status and compatibility guardrails.

## Battle visual integration matrix (provisional; must verify file and render per choice)

| Opal host | Donor source / research | Targeted approach | Gate |
|---|---|---|---|
| Thunderbolt, Spark, Thunder Shock | Ranger 2 lightning and multi-stage impact timing; Platinum existing .spa | Improve discharge branching, preimpact anticipation and secondary impact; initially compose existing .spa emitters | Confirm donor image visually, author compatible new .spa only with proven emitter editor |
| Flamethrower, Ember, Fire Spin | Ranger 2 fire and glow primitives; AV1 composites | Use flame fragments, bloom timing and residual motes rather than generic repeat emitters | Native texture conversion+VRAM budget |
| Shadow Ball, Dark Pulse, Psybeam | Ranger 2 glow, PMD visual timing, native particle resources | Opalescent/violet ghost & psychic framing while preserving unique move-type coloration | Verify BG fades and palette restoration |
| Water Pulse, Surf, Hydro Pump | PMD Sky effects/environment transitions, Ranger 2 compositing, existing Platinum water assets | Layer crest, spray and dissipation; keep multi-target anchoring safe | Resource ownership, doubles/friendly-fire logic |
| Ice Beam / environment | Existing Platinum Ice particles + PMD environmental palette treatment | Crystal scatter/afterglow balanced against S2-D terrain cycling | Battle terrain BG/OBJ palette collision QA |
| Battle HUD/status/move selection | G7 native ownership, HGSS/Ranger 2 UI detailing and PMD status-icon model | Selectively introduce Opal pearl/violet/gold framing, status movement and clearer focus, never import an entire foreign BG map | DS SUB bank, tilemap indices, OAM and touch ownership |
| Climactic move/encounter sequences | Ranger 2 `e010`/`e100` phase sequencing evidence | Build native reusable anticipation → impact → decay sequences | Confirm no gameplay timing/mechanics change |

## Required implementation protocol

1. **Start with the real Opal host** (`res/moves/*/anim.s`, existing `.spa`, healthbox or SUB UI resource), not an attractive donor image.
2. Read donor ledger entry, rank, curation record and original source path; record exact donor record ID and license/provenance in a per-move manifest.
3. Review the *rendered* image/timing. Filter out `reject`/`decode_issue`, weak companion-only and reference-only records for direct import.
4. Decide whether donor is used as `technique`, `component`, `composite` or `direct replacement`; keep visual references separate from assets actually shipped.
5. Convert to legitimate target representation (SPL .spa or native sprite sheets/palettes), with actual tooling, resource usage and build evidence. The existing AV1 work explicitly did **not** develop an SPL authoring tool; don't claim donor textures are installed until solved.
6. Preserve existing G5/G7/S2-D/AV1 visual work and update tests. The owner will perform runtime/emulator visual acceptance later.

## B1 scope checkpoint

Five implemented native-script cinematic effect pilots (**Thunderbolt, Shadow Ball, Ice Beam, Flamethrower, Energy Ball**) currently reuse *existing Platinum emitter IDs*. They are **not donor texture imports**, and they are merely the first source-level changes. The next material visual improvement should select and convert candidates from this database, not continue endlessly duplicating vanilla particles.
