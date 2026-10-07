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
