# Donor Selection Framework

Nothing here modifies Platinum visual resources. Selection decides **which donor (if any) should supply each
Platinum visual target**; implementation is a later, separate step driven by `IMPLEMENTATION_QUEUE`.

## Data flow (all machine-readable, all reproducible)

```
LANE_{A,B,CDE}_RECOVERED_CURATION.json  (authoritative; only `usable` records are candidates)
        │  tools/visual_overhaul/selection/mapping.py  (record -> subsystem/target/unit)
        ▼
CANDIDATE_GROUPS.json      group = (subsystem, source, unit); member_digest binds the exact asset set
        │  + SUBSYSTEMS.json (source roles: donor class, format family, conversion) 
        │  + evidence/<subsystem>.json (measured native-vs-donor relation, bound to member_digest)
        │  + SELECTION_RULES.json (v1.0 scoring/gates)
        ▼
ledgers/<subsystem>.json   one decision per group, one resolution per target
        ▼
IMPLEMENTATION_QUEUE.json / SELECTION_STATUS.json
```

## Terms

* **subsystem** – a Platinum visual area (`SUBSYSTEMS.json`), traced to a row of `CROSS_GAME_DONOR_MATRIX.md`.
* **target** – the Platinum thing a donor competes for (`sp_0025`, a trainer class, `family:<subsystem>`).
* **group** – the donor-side bundle selected as one unit (e.g. HGSS icon for species 25; a Ranger package).
* **role** – `preferred` | `alternate` | `reference_only` | `not_selected`.
* **resolution** (per target) – `platinum_native` (default) or `donor:<group_id>` (only when a group is `preferred`).

## Decision record (ledger `decisions[]`)

`group_id`, `target_id`, `subsystem`, `source_id`, `asset_identity{unit, member_count, member_digest, sample_paths}`,
`curation_trace{recovered_ledger_member_counts}`, `donor_class`, `format_family`, `conversion_requirement`,
`role`, `reason_code`, `needs_evidence`, `needs_runtime_validation`,
`scores{visual_gain, compat, risk, integration_cost, independent_share}`, `visual_evidence{native_relation, detail}`.

## Scoring (SELECTION_RULES.json)

| Dimension | Source | Scale |
|---|---|---|
| compat | conversion requirement of the group (`none`=3 … `not_portable`=0) | 0–3 |
| risk | conversion baseline, +1 level for runtime-validation relations, +1 for unresolved decode_issue members | low/medium/high |
| integration_cost | subsystem cost + conversion scale | integer |
| visual_gain | measured native-vs-donor relation (`identical`=0 … `art_diff*`=2); **null = unmeasured** | 0–3 / null |
| independent_share | share of members not companion/palette-only/sibling-resource evidence | 0–1 |

Gates, in order: group with no independently evidenced member → `not_selected`; donor class `none` → `not_selected`;
class `technique`/`reference` or `not_portable` conversion → `reference_only`; class `control` (same-lineage build,
e.g. Diamond) can never be selected, only compared; `direct`/`convertible` with gain 0 → `not_selected`
(Platinum-native wins), gain unmeasured → `reference_only` + `needs_evidence`, otherwise eligible when
compat/risk/gain meet thresholds and independent evidence share ≥ 0.5 (else `weak_evidence_share`). Per target the best eligible group is `preferred`, others `alternate`;
no eligible group ⇒ the target resolves to `platinum_native`.

This encodes the donor-use policy: a donor is selected only when format is compatible **and** a measured visual
gain exists; anything uncertain is `reference_only`, never silently preferred.

## Evidence providers

One per subsystem (`evidence_<name>.py`). They are the only code that may open donor checkouts (read-only) and must
write `evidence/<subsystem>.json` with donor commits, the comparison method, and per-group
`{native_relation, member_digest, detail}`. Subsystems without a provider default to `unmeasured`, i.e. policy-class
decisions only.

## Commands

```
python3 tools/visual_overhaul/selection/build_candidate_groups.py            # regenerate groups
python3 tools/visual_overhaul/selection/evidence_icons.py --hgss-root … --diamond-root …   # pilot evidence
python3 tools/visual_overhaul/selection/select_subsystem.py --subsystem pokemon_icons
python3 tools/visual_overhaul/selection/build_queue.py && .../build_status.py
python3 tools/visual_overhaul/selection/validate_selection.py                # CI gate
python3 tools/visual_overhaul/selection/test_selection_framework.py          # negative tests
```

## Validation guarantees

Groups regenerate byte-identically from the recovered ledgers; every `usable` record is in exactly one group;
ledgers cover exactly their subsystem's groups with no duplicates; ≤1 `preferred` per target; selected groups are
`direct`/`convertible`, have measured gain, ≥50 % independent evidence, and a curation trace; evidence entries bind to
the current `member_digest`; every ledger re-derives identically from rules + evidence; queue/status are reproducible.

## Catalog extensions

Targeted catalog additions live in `docs/visual_overhaul/catalog_extensions/` (see its README/MANIFEST). Alignment tables for Platinum targets live in `selection/alignment/`; their hashes are part of `CANDIDATE_GROUPS` inputs, so edits force regeneration. Slot-name alignment must never be treated as subject identity (`subject_unverified`).

## Use outcomes (selection v2: donors contribute in more ways than whole-asset replacement)

`USE_OUTCOMES.json` is the vocabulary; `components/<subsystem>.json` holds explicit use records; `OUTCOME_STATUS.*` is the derived summary.
The ledgers (role/reason_code, `SELECTION_RULES.json`) are **unchanged and still reproducible**: they only answer "should this whole donor asset replace the Platinum one?". A donor that fails that test is **not** thereby useless.

| Outcome | Axis | Source of truth |
|---|---|---|
| `direct_replacement` | replacement | derived: ledger role `preferred` (human-gated where required) |
| `alternate` | replacement | derived: ledger role `alternate` |
| `native_keep` | replacement | derived: `not_selected` for `identical_to_native` / `human_keep_platinum` |
| `not_selected` | replacement | derived: other `not_selected`/non-technique `reference_only` |
| `needs_evidence` | replacement | derived: ledger `needs_evidence` flag |
| `component_donor` | contribution | explicit record: a specific component/property of a donor asset is useful for a Platinum target |
| `composite_input` | contribution | explicit record committed as an input of a composite plan (new Platinum-native asset from Platinum + donor components) |
| `technique_reference` | contribution | derived pool for technique-class groups; explicit record pins a target + technique, **never carries donor pixels** (`pixel_use: none`) |

A group has exactly one derived replacement outcome and zero or more explicit contribution records. Replacement outcomes are never written as records.

### Use record (`components/<target subsystem>.json: records[]`)
Required: `record_id`, `outcome`, `status` (`proposed|human_confirmed|withdrawn`), `source` {`group_id`, `source_id`, `member_digest`, `assets[]` {`asset_id`, `source_path`, `source_commit`, `render_path?`, `render_sha256?`}}, `target` {`subsystem`, `target_id`, `native_ref` {`path`, `sha256`}}, `tags[]` (⊆ component tags: pose, silhouette, palette, shading, clothing_detail, accessory, texture_region, geometry_detail, animation_frame, animation_timing, particle_shape, layout, UI_element, environmental_motif, material_treatment), `component.property`, `pixel_use` (`donor_pixels|recolored_donor|derived|none`), `constraints[]` (compatibility), `adaptation[]` (transformation needed), `evidence` {`kind`, `summary`, `refs[]`, `evidence_entry_digest`}, `confidence`, `risk`, `reason`, `proposed_by`.
`human_review` (only with `status: human_confirmed`) binds `member_digest`, `evidence_digest` **and** `record_digest` (content hash of the record minus status/human_review): editing a confirmed record, its source group or its evidence makes the confirmation stale (error).

### Composite plan (`composites[]`) and component reviews (`component_reviews[]`)
A plan names a `target_id` (must still resolve to `platinum_native`; native enhancement and donor replacement are exclusive), a hash-pinned `native_base`, `inputs[]` (active `composite_input` records for that target) and `technique_refs[]` (active `technique_reference` records). `ready` requires every input `human_confirmed`. Plans are metadata only: **pixel compositing is not automated** and no Platinum resource changes.
A `component_review` records "this group was examined for component use": `none_found` (digest-bound; conflicts with any active record on that group) or `records_proposed`.

### Validator additions (`validate_selection.py` → `outcomes.validate_use_records`, negative tests in `test_use_outcomes.py`)
every ledger decision maps to an outcome; records carry complete provenance (source assets must be members of the cited group, curated `usable`, and match the catalog path/commit/render hash); source/evidence/native-file hashes are current; technique use carries no pixels; component use on a `direct_replacement` group is rejected; composites cannot reference missing/uncurated/unconfirmed inputs, orphan `composite_input` records are rejected, `component_donor` cannot enter a plan unpromoted; `OUTCOME_STATUS.json` and the queue are reproducible.

### Work lanes (`IMPLEMENTATION_QUEUE`)
A `direct_replacement` (implement, runtime_qa) · B `native_enhancement` (component_review, composite_build) · C `technique_only` (technique_build, technique_pool) · `evidence`.
