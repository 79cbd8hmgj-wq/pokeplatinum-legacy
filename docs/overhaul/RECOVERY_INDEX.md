# Chat-to-Repo Recovery Index

## Purpose

Track which historical design/implementation decisions have been migrated into repository authority and which still require recovery.

This file exists specifically to prevent another situation where critical project state lives only in old chats.

## Recovery status legend

- `CANONICALIZED` — authoritative repo document now exists.
- `PARTIAL` — major rules captured, detailed per-record authority still needs migration.
- `ARTIFACT EXISTS` — implementation artifact was previously generated/recovered but still needs permanent repo placement or verification.
- `NEEDS RECOVERY` — historical work exists in checkpoints but is not yet canonicalized.
- `PLANNED` — work was not fully designed yet; no recovery expected.

## Top-level project

| Area | Status | Repo authority |
|---|---|---|
| Project identity | CANONICALIZED | `MASTER_PLAN.md`, `MASTER_SPEC.md` |
| Phase order / roadmap | CANONICALIZED | `MASTER_PLAN.md` |
| Current checkpoint | CANONICALIZED | `STATUS.md` |
| Implementation workflow | CANONICALIZED | `IMPLEMENTATION_PLAN.md` |
| Emerald reuse strategy | CANONICALIZED | `EMERALD_PORT_PLAN.md` |

## C1 — existing move rebalance

Status: `PARTIAL`

Captured:

- governing philosophy
- representative/high-impact final values
- relationship to C2/C3

Still required:

- canonical full move-by-move C1 ledger
- every final power/accuracy/PP/effect change
- explicit unchanged rulings where they mattered to later design
- source path/implementation status per move

Historical sources include the C1 move-rebalance batch files/checkpoints, including the Bug offense workbook and later move-rework checkpoints.

## C2 — TM/HM

Status: `CANONICALIZED` for design.

Repo authority:

- `tm_hm/TM_HM_SPEC.md`

Still useful to archive permanently:

- generated compatibility manifest JSON
- guarded compatibility apply script
- validation output/checkpoint metadata

## C2.5 — created moves

Status: `CANONICALIZED` for design; implementation artifacts still need permanent source placement/verification.

Repo authority:

- `moves/CREATED_MOVES.md`

Historical/recovered implementation artifacts:

- `platinum_created_moves_plumbing_manifest_v3.json`
- created-move source patch specification
- guarded created-move apply script

Required next step:

- put the final artifact versions in a stable repo path after validating them against the live implementation branch
- do not archive obsolete v1/v2 artifacts as current authority without marking them superseded

## Pass A/B — species types/stats/abilities/roles

Status: `PARTIAL`

Captured:

- major retype authority in `MASTER_SPEC.md`
- design principles
- numerous species details exist in guarded-ledger/checkpoint history

Still required:

- canonical #001–#493 species design table containing:
  - types
  - base stats
  - abilities
  - role
  - evolution method
  - implementation status
  - justification/reference

This should ultimately replace any need to search old Pass A/B chats.

## C3 — level-up learnsets

Status: `PARTIAL`

Captured:

- design hierarchy
- final audit rules
- Banette correction
- created-move distribution
- compatibility/tutor/egg policies
- several high-risk examples

Still required:

- canonical species-by-species C3 learnset ledger/table
- every insert/replace/remove operation from the final guarded implementation plan
- clear `SUPERSEDED` handling for provisional pre-C2.5 learnset proposals

Historical checkpoint indicates at least 225 guarded Pokémon operations across C3H-L1 through L5.

Preferred canonical form:

- machine-readable final ledger in repo
- generated human-readable species summary derived from that ledger

Do not manually maintain two divergent authorities if the human-readable table can be generated from the machine-readable ledger.

## C3 — TM/HM compatibility

Status: `CANONICALIZED` for design.

Still required:

- final manifest/script checked into repo beside the implementation
- validation evidence attached to the implementation commit/PR

## C3 — tutors

Status: `CANONICALIZED` at policy level.

Final rule:

- tutors specialize; they do not repair baseline functionality
- no created move becomes a general tutor in Core 1.0

No large custom tutor rewrite needs recovery unless a later implementation branch proves otherwise.

## C3 — egg moves

Status: `CANONICALIZED` at policy level.

Final rule:

- vanilla Platinum egg pools remain baseline
- no breeding dependency for ordinary STAB
- no blanket created-move egg expansion

Detailed exceptions should be recovered only if final guarded implementation contains them.

## Evolution overhaul

Status: `PARTIAL / next planning target`

Captured:

- no required trade evolutions
- proposed item/level replacements in `EMERALD_PORT_PLAN.md`

Still required:

- authoritative complete evolution manifest for all affected species
- exact levels/items/locations/friendship thresholds
- source implementation mapping
- item availability dependencies

## World / #001–#493 availability

Status: `PLANNED`

Captured:

- philosophy and phase targets

Still required:

- complete encounter matrix
- all gifts/fossils/static encounters
- swarm/Radar/Honey/Marsh/Trophy Garden policy per species
- pre-E4 completion audit
- National Dex timing

## Trainers

Status: `PLANNED`

Captured:

- difficulty philosophy only

Still required:

- ordinary trainer curve
- Gym teams
- Rival teams
- Galactic teams
- Elite Four/Cynthia
- rematches
- held items/AI level rules

## Economy / EXP

Status: `PLANNED PORT`

Captured:

- Emerald numerical baseline and port methodology

Still required:

- Platinum audit
- playtest-based final multipliers/prices
- source implementation spec

## Poké Balls

Status: `PLANNED PORT`

Captured:

- Emerald role/value references and Platinum adaptation rule

Still required:

- audit native Platinum ball behavior
- choose exact final Platinum multipliers
- exact shop/field availability
- implementation tests

## Breeding

Status: `PLANNED PORT`

Captured:

- Emerald inheritance candidates
- Platinum C3 egg-move policy

Still required:

- Gen IV inheritance audit
- exact Core 1.0 breeding scope
- hatch-cycle targets
- Day Care/economy integration

## Legendary/Mythical events

Status: `PLANNED`

Captured:

- intended native Platinum event paths

Still required:

- event-state/source audit
- trigger/item requirements
- permanent in-game unlock path
- softlock/repeatability tests

## Battle Frontier / postgame

Status: `PARTIAL`

Captured:

- TM BP price reduction
- anti-grind philosophy

Still required:

- general BP earning/reward audit
- held-item prices
- rematches/postgame availability
- completion rewards

## QA / release

Status: `PLANNED`

Required future artifacts:

- automated structural validation
- 493 availability checker
- evolution completion checker
- trainer legality checker
- move/learnset validator
- event-state checklist
- Rev 0/Rev 1 build matrix
- runtime regression suite for custom mechanics
- release changelog

## Immediate recovery priorities

1. Recover/check in the final machine-readable **species guarded ledgers**.
2. Recover/check in final **TM/HM compatibility manifest + guarded script**.
3. Recover/check in the final **created-move plumbing manifest/spec/apply script** after live-repo validation.
4. Build the complete **C1 move-change ledger**.
5. Generate a human-readable #001–#493 species authority from the guarded species ledgers.

Once those five are complete, the old chats should no longer be required to implement Phase 1 correctly.
