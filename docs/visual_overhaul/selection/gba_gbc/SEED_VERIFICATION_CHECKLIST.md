# Seed verification checklist

This is the bounded first-pass contract for GBA/GBC mining.

The next agent should **not** start by scanning all six donor repositories. It should resolve the existing seed queue using `DONOR_PATH_TARGETS.json` and this checklist.

## Decision rule

Each seed ends the first pass as one of:

- **promote** — exact source evidence supports a useful canonical opportunity;
- **reference_only / reject** — verified but not useful enough to enter implementation ranking;
- **needs_evidence** — a narrowly scoped render/decoder is still required.

No seed stays vague merely because the donor repository is large.

## First tranche

Resolve, in order:

1. Emerald field-action choreography
2. Emerald environmental primitives
3. FireRed timed palette sequences
4. FireRed map/location previews
5. FireRed interactive-object states
6. PMD Red battler status overlays

Then stop and checkpoint.

Only after that checkpoint should Crystal, Ruby delta-only, and Yellow specialized review proceed.

## Evidence discipline

For each seed record:
- pinned donor revision;
- exact source paths/functions/tables;
- exact referenced graphic family when applicable;
- what the donor contributes;
- what Platinum already does;
- classification;
- pixel-use policy;
- confidence;
- reason for promote/reject/needs-evidence.

Do not broaden into adjacent subsystems unless a verified source relationship directly exposes a high-value family.
