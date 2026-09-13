# Chat-to-Repo Recovery Index

## Purpose

Track which historical Platinum-overhaul decisions have been migrated into repository authority so implementation never depends on remembering an old chat.

## Status legend

- `CANONICALIZED` — authoritative repo document/artifact exists.
- `IMPLEMENTED` — current main contains the source implementation.
- `RECOVERED SOURCE` — exact historical implementation source is preserved for provenance/audit.
- `PARTIAL` — governing rules captured; later design/implementation still required.
- `PLANNED` — work was not fully designed yet; no recovery is expected.

## Top-level project

| Area | Status | Repo authority |
|---|---|---|
| Project identity | CANONICALIZED | `MASTER_PLAN.md`, `MASTER_SPEC.md` |
| Phase order / roadmap | CANONICALIZED | `MASTER_PLAN.md` |
| Current checkpoint | CANONICALIZED | `STATUS.md` |
| Claude/implementation workflow | CANONICALIZED | `IMPLEMENTATION_PLAN.md`, `/CLAUDE.md` |
| Emerald reuse strategy | CANONICALIZED | `EMERALD_PORT_PLAN.md` |

## C1 — existing move rebalance

**Status: CANONICALIZED / implementation-ready.**

Authority:

- human-readable: `moves/C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`
- machine-readable: `implementation/c1_move_changes_manifest.json`
- edit-membership/provenance: `implementation/c1_move_edit_membership_recovery.json`
- batch recovery evidence: `moves/C1_RECOVERED_BATCHES_SUPPLEMENT.md`

Recovered result:

- exactly **82 edited existing moves**;
- final values resolved for all 82;
- no C1-created moves;
- no new C1 mechanics;
- one effect reassignment: Razor Wind charge-high-crit → immediate high-crit;
- Batch 9F trapping mechanics/duration remain unchanged.

Final Batch 9F values:

- Bind 30/90/20
- Wrap 30/90/20
- Fire Spin 35/90/15
- Whirlpool 35/90/15
- Sand Tomb 35/90/15
- Clamp 35/90/10
- Magma Storm KEEP 120/70/5

The previously surfaced Sand Tomb 50/95 value is from a separate Emerald move-rework spec and is not Platinum C1 authority.

Remaining work is implementation, not recovery: validate current source, generate before-value guards, apply exactly 82 edits, build Rev 0/Rev 1, and archive evidence.

## C2 — TM/HM

**Status: CANONICALIZED for design / PARTIAL implementation.**

Authority:

- `tm_hm/TM_HM_SPEC.md`
- `implementation/tm_compat_manifest.json`

Implemented subset:

- TM21 Air Slash compatibility rebuild;
- TM78 Power Gem compatibility rebuild;
- explicit compatibility additions.

These landed as part of main commit `8a74452654e1552b78bfb329afcb351a2caec5cf` and passed the Rev 0/Rev 1 build matrix.

Still to implement/audit separately:

- reusable TM behavior;
- HM battle rework / Defog behavior;
- TM source/economy changes;
- any vendor UX changes retained for Core 1.0.

## C2.5 — created moves

**Status: CANONICALIZED + IMPLEMENTED + L2 build verified.**

Authority:

- `moves/CREATED_MOVES.md`
- `implementation/created_moves_manifest.json`

Implementation:

- main commit `071b8c7976801e64af5296f30b7437d7da2d8632`
- GitHub Actions run `33981291318`: success
- 22 moves, IDs 468–489, `MAX_MOVES = 490`

Focused L4 runtime QA is still required for special interactions such as Resonant Slash sound logic, Star Jab punching logic, and Magnet Volley exact-three-hit behavior.

## Pass A/B + C3 species work

**Status: IMPLEMENTED + RECOVERED SOURCE + L2 build verified.**

Current main implementation:

- commit `8a74452654e1552b78bfb329afcb351a2caec5cf`
- GitHub Actions run `33995072848`: success
- 225 guarded species operations plus final Torkoal/Seviper corrections

Historical provenance:

- `implementation/archive/c3h-apply-species-original.yml`
- historical commit `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- ledger counts `67 / 27 / 40 / 53 / 38 = 225`
- verifier/extractor `/tools/overhaul/recover_c3h_ledgers.py`

Historical ledgers are for audit/provenance only; do not reapply them over current main.

Critical final corrections:

- Banette: Shadow Ball 31; Cursed Stitch 38; Shadow Claw 42.
- Torkoal: Yawn 52; Heat Wave 55.
- Seviper: Sludge Bomb 55.

Known superseded historical artifact:

- inferred/rebuilt L3 ledger from the old branch; do not use it.

## C3 — tutors and egg moves

**Status: CANONICALIZED at policy level.**

- tutors specialize; they do not repair baseline functionality;
- no created move becomes a general tutor in Core 1.0;
- vanilla Platinum egg pools remain the baseline unless an explicit locked change exists;
- ordinary STAB/campaign functionality must not depend on breeding.

## Evolution overhaul

**Status: PARTIAL / next major design-to-implementation target after foundation stabilization.**

Still required:

- authoritative complete evolution manifest;
- exact replacement methods for all trade/trade-item evolutions;
- friendship/location threshold/access review;
- item-availability dependencies;
- one-save completion validation.

## World / #001–#493 availability

**Status: PLANNED.**

Still required:

- complete encounter matrix;
- gifts/fossils/static encounters;
- swarm/Radar/Honey/Marsh/Trophy Garden handling;
- pre-E4 nonlegendary-family audit;
- National Dex timing;
- one-save #001–#493 completion audit.

## Trainers

**Status: PLANNED.**

Still required:

- ordinary trainer curve;
- Gym/Rival/Galactic teams;
- Elite Four/Cynthia;
- rematches;
- held-item/AI rules.

## Economy / EXP

**Status: PLANNED PORT from Emerald.**

Still required:

- compare final Emerald implementation against Platinum equivalents;
- classify DIRECT / ADAPT / PLATINUM-SPECIFIC;
- implement and playtest Platinum values.

## Poké Balls

**Status: PLANNED PORT from Emerald.**

Still required:

- audit native Platinum ball behavior;
- translate Emerald balance goals to Platinum's larger specialist-ball ecosystem;
- lock multipliers/availability;
- test capture behavior.

## Breeding

**Status: PLANNED PORT from Emerald.**

Still required:

- Gen IV inheritance audit;
- exact Core 1.0 scope;
- egg-group/egg-move decisions;
- hatch-cycle targets;
- Day Care/economy integration.

## Legendary/Mythical events

**Status: PLANNED.**

Still required:

- native Platinum event-state/source audit;
- Darkrai/Shaymin/Arceus and other event unlock paths;
- event-item requirements;
- one-save acquisition flow;
- softlock/repeatability tests.

## Battle Frontier / postgame

**Status: PARTIAL.**

Captured:

- TM BP price reduction;
- anti-grind philosophy.

Still required:

- general BP earnings/rewards;
- held-item prices;
- rematches/postgame availability;
- completion rewards.

## QA / release

**Status: PLANNED.**

Future required artifacts include:

- structural validators;
- 493 availability checker;
- evolution-completion checker;
- trainer legality/progression checker;
- move/learnset validator;
- event-state checklist;
- runtime regression suite;
- release changelog/patch packaging.

## Immediate priorities

1. Implement C1 from `implementation/c1_move_changes_manifest.json` with live-source before-value guards.
2. Build Rev 0 / Rev 1 and record evidence.
3. Audit/implement remaining C2 reusable-TM/HM/economy behavior.
4. Perform focused L4 runtime QA on created moves and high-risk C3 mechanics.
5. Build the authoritative evolution manifest and run the Emerald-to-Platinum port audit.
6. Generate a human-readable #001–#493 species authority from machine-readable/current source rather than manually duplicating it.
7. Proceed into availability, trainers, economy, events, postgame, and release QA.

At this point, old chat history is no longer required to implement the completed C1/C2.5/C3 Pokémon/move phases correctly. Remaining chats are historical evidence, not operational authority.
