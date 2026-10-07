# DS opportunity mining summary

Phase `ds_only` (Platinum baseline; Diamond control; HGSS, PMD Sky, Ranger 2 donors). No donor repo was rescanned or recataloged; no Platinum asset or code was touched; deferred GBA/GBC findings are excluded.

## Method

1. **Features** (`mine_features.py`): every candidate group is joined to its members (catalog + recovered curation), ledger decision, evidence relation and target resolution; structural signals are parsed from curation details (frames/animation groups, cells, composed map layers, texture chips, composed backgrounds, animated-tile companions, cell counts, time-of-day variants, family size).
2. **Proposals** (`mine_rules.py`): each group is asked the eight taxonomy questions; rules emit zero or more proposals per group (novel capability/detail, technique, component, enhancement, replacement, reference, reject). A group may therefore yield several records (different contribution types) and loses nothing by failing a replacement comparison.
3. **Scoring**: ten dimensions (visual impact, novelty, feasibility, reuse, library value, evidence quality, cost, risk, format dependency, vertical-slice value; cost/risk/dependency inverted) with weights 7/6/5/4/3/3/3/2/2/2; impact is adjusted by richness percentile inside a family. Whole-asset replacement gets novelty 1 and low library value by construction, so it cannot outrank component/technique/novel work on whole-asset superiority alone.
4. **Disposition**: composite >= 3.3 -> promoted; >= 3.0 with evidence quality <= 2 (or ledger needs_evidence) -> needs_evidence; otherwise reference_only, or reject (identical/companion-only/no content). Diamond is control: reference_only only.
5. **Libraries**: promoted records cluster by (source, domain, family, class); library score rewards size.

Per-domain passes: `mining/passes/<domain>.json` (every group with disposition, signals, record ids); ranked views: `mining/ranked/<domain>.md`; unresolved: `mining/NEEDS_EVIDENCE_QUEUE.json`.

## Result

- groups processed 8581; surfaced 1839; dispositions promoted 1839, reference_only 6039, reject 703
- class counts: novel_capability 86, novel_detail 186, technique_donor 545, enhancement_candidate 111, component_donor 1285, replacement_candidate 32, reference_only 6048, reject 704

## Catalog blind spots

- **HGSS follower Pokemon sheets (572 NSBTX in files/data/mmodel)** — evidence closure decoded all 572 (8 frames each, normal+shiny); recorded as explicit findings opp:hgss/follower_sheet_library (sheets) and opp:hgss/follower_pokemon (system, deferred); still 0 catalog groups
- **HGSS 3D field models/textures/building models** — evidence closure decoded bm_field (340) / bm_room (222) models and 106 map texture sets (explicit findings opp:hgss/field_building_model_library, opp:hgss/map_texture_set_library); still no catalog groups: a targeted catalog extension is recommended (see DS_EVIDENCE_CLOSURE.md)
- **PMD Sky manpu_* / effect.bin / status-icon art** — uncataloged and still undecoded (status-icon art container not identified); PMD MAP_BG BPA/BPL animation and a WAN sample were decoded in the closure pass
- **Diamond trainer/field/model assets beyond sprites** — Diamond is control only; no field/model catalog
- **Ranger 2 poke/ battle frames semantic pose approval** — w/a/s/t sets rendered (295/596/296/272); poses are field-scale (~40px), not the 160x80 battle contract; walk/s/t sets closed as reference, attack sets kept as a technique library
- **HGSS UI (zukan_gra/plist_gra/camera) visual comparison with Platinum** — targeted renders composed (partial NSCR/NCGR pairing); reference_only confirmed (opp:hgss/ui_dex_party_reference)

## Targeted review of ambiguous high-value groups

21 group reviews (confirm) and 3 family reviews from committed or targeted renders (`mining/TARGETED_REVIEW.json`, images under `mining/review/` and `opportunities/evidence/`). Findings: HGSS-only trainer classes are clean multi-frame sets; Ranger walk frames form genuine cycles; Ranger effect/interface primitives are shaded multi-frame Nitro cells; Ranger composed maps are 2D tile art (motif/prop library, low feasibility); Ranger menu/event/ending bundles have no available renderer and stay needs-evidence.

## Evidence closure

`mining/EVIDENCE_RESOLUTIONS.json` (built by `resolve_evidence.py` from the committed decoder evidence under `mining/evidence/`) resolved the frozen baseline needs-evidence queue (`mining/EVIDENCE_CLOSURE_SCOPE.json`, 643 records): records were promoted with measured evidence or the group was closed to reference_only. See `DS_EVIDENCE_CLOSURE.md`.

## Top-level recommendation

Pick vertical slices from the ranked queue (`IMPLEMENTATION_QUEUE.md`); the HGSS 3D field resources need a targeted catalog extension before any import.
