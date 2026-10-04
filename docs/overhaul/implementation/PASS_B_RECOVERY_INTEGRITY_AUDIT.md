# Post-Pass-B Recovery Integrity Audit

Date: 2026-10-04

## Scope

This audit checks the two Pass B recovery merges against the already-implemented C1, C2, C2.5, and C3 layers.

Recovery merges:
- PR #41 — Light Enrichment recovery
- PR #42 — Role Repair recovery

This is a source-integrity audit, not emulator/runtime verification.

## Result

**PASS — no cross-pass implementation conflict found.**

The recovered Pass B edits are compatible with the locked C1/C2/C2.5/C3 implementation currently on `main`.

## PR #41 — Light Enrichment

The recovery touched the 17 locked Light Enrichment species.

Semantic intent is limited to:
- base-stat edits;
- ability edits;
- schema-safe restoration of float-valued Pokédex weights where JSON rewriting had collapsed values such as `65.0` to `65`.

No type, evolution, TM/HM compatibility, created-move, or intentional learnset change is introduced by the recovery.

Vespiquen's large textual diff is JSON reformatting only outside the intended ability edit; its type, egg groups, evolution array, and level-up entries retain the same semantic values.

PR #41 passed both:
- US Rev 0 build
- US Rev 1 build

before merge.

## PR #42 — Role Repair

The recovery touched 45 species data files across Generations I-IV.

A patch-field audit found no semantic edits outside:
- `base_stats`;
- `abilities`;
- required `weight_pounds` float normalization.

No C1 move data, C2 TM/HM mechanics, C2.5 created-move records, C3 level-up entries, or TM compatibility masks were changed by PR #42.

PR #42 passed both:
- US Rev 0 build
- US Rev 1 build

before merge.

## C3H guarded-ledger overlap

The archived C3H guarded ledgers were checked specifically for species also touched by the Pass B recovery.

The overlapping C3H stat/ability postconditions are consistent with the recovered Pass B state:

- Wigglytuff — Sp. Atk 85; Cute Charm / Soundproof
- Furret — Frisk / Keen Eye
- Purugly — 80/95/70/55/65/115
- Carnivine — recovered HP/Atk/Def/SpD/Speed values match the C3H postconditions

Other recovered species appearing in the C3H ledgers are represented there through learnset operations rather than conflicting stat/ability assignments. Those learnset operations were not changed by the Pass B recovery.

Important Gen IV reconstruction cases:
- Mothim — 70/60/60/110/80/80
- Cherrim — 70/75/70/90/80/85
- Lumineon — 75/60/80/90/90/90

The archived C3H ledgers do not impose conflicting base-stat postconditions on those three. Lumineon's C3H operation is its Luminous Current level-up placement, which remains untouched.

Chatot's C3H operation is its Air Cutter level-up placement; its recovered stats remain independent of that operation.

## Earlier pass isolation

### C1
PRs #41/#42 do not touch `res/moves/*`, Razor Wind resources, or the C1 manifest/validator surface.

**No direct C1 regression path found.**

### C2
PRs #41/#42 do not touch HM move data, Defog scripts, TM item assignments, reusable-TM code, TM acquisition scripts, or C2 shop/economy code.

**No direct C2 regression path found.**

### C2.5
PRs #41/#42 do not touch created move IDs 468–489, created-move data/scripts/animations, move registries, or `MAX_MOVES`.

**No direct C2.5 regression path found.**

### C3
PRs #41/#42 do not intentionally alter level-up learnsets or TM compatibility. Archived guarded-ledger stat/ability overlaps checked above are consistent.

**No C3 authority conflict found.**

## Verification boundary

The repository's last recorded D7 master validation before this recovery was:

- 19 validators PASS
- 14 mutation/regression suites PASS
- 0 failed children

That historical result remains useful baseline evidence, but it is not being relabeled as a post-recovery validator run.

The Pass B recovery itself has dual-revision build evidence from PRs #41/#42. A fresh `python3 tools/overhaul/validate_overhaul.py --no-write` run should be performed in the next heavy-tool/Claude Code session to produce explicit post-recovery static validation evidence.

## Current integrity state

- Pass A identity/evolution: retained
- Pass B Identity Rework: 17/17 audited on current main
- Pass B Role Repair: recovered
- Pass B Light Enrichment: recovered
- C1: no recovery conflict found
- C2: no recovery conflict found
- C2.5: no recovery conflict found
- C3/C3H: guarded-ledger overlap reconciled
- Dual-revision build gate for recovery PRs: PASS
- Fresh post-recovery master static validator: PENDING
- Runtime QA: still PENDING

## Next action

Hand the current `main` tree to the heavy-tool workflow and run:

```bash
python3 tools/overhaul/validate_overhaul.py --no-write
```

If green, record that as the post-recovery D7 static baseline and move directly to the remaining runtime QA / D8 runtime blocker work rather than reopening Pokémon design.
