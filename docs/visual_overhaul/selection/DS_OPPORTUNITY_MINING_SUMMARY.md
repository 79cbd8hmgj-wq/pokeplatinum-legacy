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

- groups processed 8581; surfaced 2162; dispositions needs_evidence 559, promoted 1603, reference_only 5716, reject 703
- class counts: novel_capability 129, novel_detail 352, technique_donor 677, enhancement_candidate 111, component_donor 1284, replacement_candidate 32, reference_only 5724, reject 704

## Catalog blind spots

- **HGSS follower Pokemon sheets (572 NSBTX in files/data/mmodel)** — scanned but excluded from the NPC/player catalog scope; 0 groups (see opp:hgss/follower_pokemon, explicit finding)
- **HGSS 3D field models/textures/building models** — not present as discrete files in the decomp checkout and never cataloged: the `models` and most `textures` domains have no HGSS groups
- **PMD Sky manpu_* / effect.bin / status-icon art** — uncataloged; PMD `.wan` groups are 'valid render' by ledger but have no committed previews
- **Diamond trainer/field/model assets beyond sprites** — Diamond is control only; no field/model catalog
- **Ranger 2 poke/ battle frames semantic pose approval** — catalog quality note: pose suitability not approved; frames are field-scale, not 160x80 battle contract
- **HGSS UI (zukan_gra/plist_gra/camera) visual comparison with Platinum** — ledgers are needs_evidence; no render comparison exists

## Targeted review of ambiguous high-value groups

21 group reviews (confirm) and 3 family reviews from committed or targeted renders (`mining/TARGETED_REVIEW.json`, images under `mining/review/` and `opportunities/evidence/`). Findings: HGSS-only trainer classes are clean multi-frame sets; Ranger walk frames form genuine cycles; Ranger effect/interface primitives are shaded multi-frame Nitro cells; Ranger composed maps are 2D tile art (motif/prop library, low feasibility); Ranger menu/event/ending bundles have no available renderer and stay needs-evidence.

## Top-level recommendation

Targeted evidence for the needs-evidence clusters first (tilemap preview for Ranger menu/event/ending; WAN/BPA samples for PMD Sky; follower/3D HGSS extraction), then pick vertical slices from the ranked queue.
