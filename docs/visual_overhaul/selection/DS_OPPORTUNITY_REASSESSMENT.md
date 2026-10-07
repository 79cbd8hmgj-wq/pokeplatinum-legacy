# DS-only opportunity reassessment (phase `ds_only`)

Scope: Platinum (baseline), Diamond (control), HGSS, PMD Sky, Ranger 2 (`PHASE_SCOPE.json`). The nine GBA/GBC findings (FireRed, Emerald, PMD Red, Crystal, Yellow) are preserved verbatim in `opportunities/deferred/non_ds_findings.json` and are excluded from the register, queue and rankings. Eight-class taxonomy unchanged. No Platinum asset or code was modified; the only new evidence artifact is a small donor render sample (`opportunities/evidence/`).

Targeted donor-checkout verification (read-only, pinned): pokeheartgold `9d8b7591`, pmd-sky `be11cac`, pokeranger2 `55b4e0cd`. No bulk scan was run.

## Classification of the known DS opportunity space

| Area | Class | Basis |
|---|---|---|
| HGSS area previews (23 areas, time of day) + `src/map_preview_graphic.c` | **novel_capability** | Committed ledger evidence (`missing_in_native`); module verified in HGSS; layout/technique only, new Sinnoh art |
| HGSS follower Pokemon (572 sheets, `follow_mon.c`) | **novel_capability** | Sheet count in committed README; system verified in HGSS; Platinum has no follower code |
| PMD Sky status-icon model | **novel_detail** | `UpdateStatusIconFlags` verified; icon art container not yet identified (manpu/effect.bin uncataloged) |
| Ranger 2 effect primitives (fire/tornado/lightning/glow) | **component_donor** | Targeted render sample committed |
| Ranger 2 multi-phase effect sequencing | **technique_donor** | e010/e100 phase structure in the sample |
| HGSS Ace Trainer M/F shading/detail | **enhancement_candidate** x2 | Existing proposed component records (4) linked |
| HGSS 26 Pokemon battle sprites, 6 trainer sets | **replacement_candidate** (32 derived) | Existing ledgers; runtime QA still gating |
| HGSS Pokedex/party UI, camera viewfinder, HGSS-only NPC/trainer pool; Diamond control; PMD backgrounds and GROUND wan; Ranger UI/story art and Pokemon frames | **reference_only** x8 | each states why (no demonstrated gain, no counterpart, no decoder, scale mismatch, control class) |
| HGSS/Diamond icons; Arcade Star and Young Couple (none_found reviews) | **reject** x3 | identical/recolour only |

## Coverage gaps (honest limits of current DS evidence)

* HGSS late-Gen-IV field models/textures: the decomp checkout exposes only 49 NSBMD (legend/title/starter/mmodel) and 832 NSBTX (all `mmodel` sprite sheets); map building models are not present as discrete files, and the catalog has none. This is the largest unexamined DS area (matrix: HGSS is first donor for map props/textures). Needs a targeted extraction before any rating.
* PMD Sky: `SYSTEM/manpu_*` and `EFFECT/effect.bin` are not cataloged; GROUND `.wan` sprites have no renderer.
* Ranger 2: 905 field `ntfp` texture/effect groups and `menu_ui_frames/pmd_sky` fonts remain unscoped pools.
* Per-move Platinum targets for the Ranger effect primitives are not chosen yet.

## Ranking

Weights (visual impact 7, novelty 6, feasibility 5, reuse 4, cost 3, risk 2, vertical-slice 1; cost/risk inverted, scores 1-5) live in `OPPORTUNITY_CLASSES.json` -> `ranking`. Result: `IMPLEMENTATION_QUEUE.md` (and `OPPORTUNITY_REGISTER.md`).
