# C1 Implementation Audit

- Canonical manifest: `c1_move_changes_manifest.json` (82 edits, unchanged authority).
- Guard file (before-values from pinned base, KEEP invariants): `c1_move_guards.json`.
- Base: `main` @ `9034963728913416f2968b56f7dab8ac61b19c07` (includes PR #10, #11, #12).
- Tooling: `tools/overhaul/moves/` — `apply_c1.py` (guarded, idempotent, including Razor Wind script/animation), `validate_c1.py`, `test_validate_c1.py` (24 rejecting mutations + 4 forward-compatibility cases), `scope_audit_c1.py`.

## Accounting

| Category | Count |
|---|---|
| Total locked edits | 82 |
| Newly applied (live == expected before) | 82 |
| Already implemented | 0 |
| Reconciled with a later locked pass | 0 |
| Unresolved | 0 |

No C1-edited move is overridden by a locked C2 value. Whirlpool is not a Platinum HM; its C1 value 35/90/15 applies independently. The locked C2 HM battle changes (Cut, Fly, Defog, Rock Smash, Rock Climb, …) are separate later-pass authority and must be allowed by the permanent C1 validator.

## Razor Wind (only effect reassignment)

- `BATTLE_EFFECT_CHARGE_TURN_HIGH_CRIT` → `BATTLE_EFFECT_HIGH_CRITICAL`, description rewritten (no two-turn claim).
- Required plumbing, same locked behavior: `script.s` no longer prints the charge message ("whipped up a whirlwind"), and `anim.s` plays only the strike animation (the old charge/strike branch relied on the charge-turn state).

## Validation (source level)

- `validate_c1.py`: OK, 0 problems. The permanent validator checks the 82 C1-owned records, KEEP invariants, Razor Wind resources, and created-move regressions without freezing unrelated moves against the old base; the one-time scope audit remains responsible for proving this PR did not touch unrelated move state.
- `test_validate_c1.py`: 24/24 C1 regressions rejected plus 4/4 forward-compatible cases accepted. Coverage includes power, accuracy, PP, effect chance/type, high-crit, multi-hit, trapping, KEEP invariants, Razor Wind description/script/animation, Magnet Volley, Resonant Slash/Star Jab registries, move IDs/MAX_MOVES, custom-record loss, manifest/guard disagreement, and proof that later C2 HM or unrelated move changes do not invalidate C1.
- `scope_audit_c1.py`: only `res/moves/*/data.json`, Razor Wind script/anim, `docs/overhaul/`, `tools/overhaul/moves/` differ from base.
- Availability validators (PR #10/#11): `validate_availability.py --state live` 0 failures; `test_validators.py` 12/12 + 25/25.
- Builds: Rev 0 / Rev 1 are verified by the `build` GitHub Actions workflow on the PR (no toolchain in the authoring container).
- Battle runtime QA: **pending** (source/build/validator complete; focused battle runtime QA pending).
