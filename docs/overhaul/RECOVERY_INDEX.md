# Chat-to-Repo Recovery Index

## Purpose

Track which historical Platinum-overhaul decisions have been migrated into repository authority and which still require recovery. This file exists specifically so implementation never again depends on remembering an old chat.

## Status legend

- `CANONICALIZED` — authoritative repo document/artifact exists.
- `RECOVERED SOURCE` — exact historical implementation source is preserved in-repo and reproducibly extractable.
- `PARTIAL` — governing rules are captured, but detailed record authority is still being migrated.
- `NEEDS RECOVERY` — completed historical work exists but is not yet safely canonicalized.
- `PLANNED` — work was not fully designed yet; no recovery is expected.

## Top-level project

| Area | Status | Repo authority |
|---|---|---|
| Project identity | CANONICALIZED | `MASTER_PLAN.md`, `MASTER_SPEC.md` |
| Phase order / roadmap | CANONICALIZED | `MASTER_PLAN.md` |
| Current checkpoint | CANONICALIZED | `STATUS.md` |
| Implementation workflow | CANONICALIZED | `IMPLEMENTATION_PLAN.md`, `/CLAUDE.md` |
| Emerald reuse strategy | CANONICALIZED | `EMERALD_PORT_PLAN.md` |

## C1 — existing move rebalance

Status: `NEEDS RECOVERY` **for the full implementation ledger only. Design itself is complete and locked.**

Historical final-audit evidence confirms:

- C1 was completed and locked;
- the final source-of-truth Markdown contained all approved batches, KEEP rulings, rationales, C1 consistency rules, C2/C3 deferrals, and a complete **82-move edit ledger**;
- old proposal spreadsheets marked `Needs approval` are not implementation authority.

Already canonicalized elsewhere or independently reconfirmed include representative/high-impact final values such as:

- Fury Cutter — 20 BP / 100 Acc / 20 PP;
- Leech Life — 40 BP / 100 Acc / 20 PP, normal drain effect;
- Pin Missile — 20 BP per hit / 95 Acc / 20 PP;
- Twineedle — 30 BP ×2 / 100 Acc / 20 PP, existing poison behavior;
- Silver Wind — 60 BP / 100 Acc / 10 PP, existing omniboost behavior;
- Power Gem — 80 BP / 100 Acc / 20 PP;
- Toxic — 90 Acc;
- Bullet Seed — 20 BP per hit / 20 PP;
- Giga Drain — 75 BP;
- Iron Tail — 85 Acc;
- Rock Tomb — 60 BP / 95 Acc;
- Thief — 60 BP;
- Steel Wing — 75 BP / 95 Acc;
- Drain Punch — 75 BP / 10 PP;
- Will-O-Wisp — 85 Acc;
- Mirror Shot — 70 BP / 95 Acc;
- Twister — 50 BP;
- Dragon Rush — 100 BP / 85 Acc;
- Icicle Spear — 20 BP per hit;
- Ominous Wind — 10 PP.

Still required before C1 implementation is considered repo-self-contained:

1. recover the complete final 82-move ledger;
2. write `moves/C1_EXISTING_MOVE_REBALANCE.md`;
3. write a machine-readable `implementation/c1_move_changes_manifest.json`;
4. preserve explicit final KEEP rulings where later balance decisions depend on them;
5. validate the manifest against the live Platinum source before applying edits.

**Do not fill unrecovered entries by inference.**

## C2 — TM/HM

Status: `CANONICALIZED` for design.

Authority:

- `tm_hm/TM_HM_SPEC.md`
- `implementation/tm_compat_manifest.json`

Still useful to archive after live-source validation:

- final guarded compatibility apply script;
- validation/build evidence tied to the implementation commit.

## C2.5 — created moves

Status: `CANONICALIZED` for design.

Authority:

- `moves/CREATED_MOVES.md`
- `implementation/created_moves_manifest.json`

Still required on the implementation side:

- reconcile the final plumbing/source-patch artifacts against the active implementation branch;
- run the created-move build/resource gate;
- archive only the validated final artifact versions as current authority.

Do not promote obsolete v1/v2 artifacts without marking them superseded.

## Pass A/B — species types/stats/abilities/roles

Status: `RECOVERED SOURCE` for implemented guarded changes; `PARTIAL` for a polished human-readable #001–#493 catalog.

The exact C3H species implementation payload contains the guarded stat/type/ability changes needed by the implementation batches. A future generated species catalog should expose these in human-readable form rather than creating a second manually maintained authority.

Still desirable:

- generated #001–#493 table with types, stats, abilities, role, evolution method, implementation status, and rationale/reference.

## C3 — level-up learnsets and species implementation

Status: `RECOVERED SOURCE`.

### Exact historical source

The original application workflow is archived byte-for-byte at:

- `implementation/archive/c3h-apply-species-original.yml`

Historical provenance:

- commit: `dceb548782be5c3ed30afba39a8b5727fdd6716d`
- workflow blob SHA: `c45362c9913899aae07e6a84fa5bc62e9ee7edb0`
- exact ledger counts: **67 / 27 / 40 / 53 / 38 = 225 operations**

Deterministic verifier/extractor:

- `/tools/overhaul/recover_c3h_ledgers.py`

Provenance manifest:

- `implementation/ledgers/C3H_LEDGER_PROVENANCE.json`

One ledger is already materialized byte-for-byte as an additional cross-check:

- `implementation/ledgers/platinum_c3h_l4_gen3_guarded_ledger_v1.json`

The extractor is the canonical way to materialize/reconcile all five exact ledgers from the archived historical payload.

### Critical supersession rule

Do **not** use the historical `platinum_c3h_l3_gen2_guarded_ledger_v1_rebuilt.json` inferred reconstruction found in old branch history. It was explicitly removed as superseded. Use the five embedded historical blobs above.

### Final-audit correction

Banette authority remains:

- Shadow Ball Lv31 remains;
- Cursed Stitch Lv38;
- Shadow Claw Lv42.

Any older proposal replacing Shadow Ball Lv31 with Cursed Stitch is superseded.

## C3 — TM/HM compatibility

Status: `CANONICALIZED` for design.

Authority:

- `tm_hm/TM_HM_SPEC.md`
- `implementation/tm_compat_manifest.json`

Implementation still requires final guarded script + validation evidence against the live branch.

## C3 — tutors

Status: `CANONICALIZED` at policy level.

- tutors specialize; they do not repair baseline functionality;
- no created move becomes a general tutor in Core 1.0.

## C3 — egg moves

Status: `CANONICALIZED` at policy level.

- vanilla Platinum egg pools remain the baseline;
- ordinary STAB cannot depend on breeding;
- no blanket created-move egg expansion.

Detailed exceptions should be added only if final implementation evidence establishes them.

## Evolution overhaul

Status: `PARTIAL / next major design-to-implementation target`.

Captured:

- no required trade evolutions;
- Emerald-successor philosophy;
- several proposed replacements and item-access principles.

Still required:

- authoritative complete evolution manifest for every affected species;
- exact levels/items/locations/friendship thresholds;
- source implementation mapping;
- item-availability dependencies;
- validation that every evolution can be completed in one save.

## World / #001–#493 availability

Status: `PLANNED`.

Still required:

- complete encounter matrix;
- gifts/fossils/static encounters;
- swarm/Radar/Honey/Marsh/Trophy Garden handling;
- pre-E4 nonlegendary-family audit;
- National Dex timing;
- one-save 493 completion audit.

## Trainers

Status: `PLANNED`.

Still required:

- ordinary trainer curve;
- Gym/Rival/Galactic teams;
- Elite Four/Cynthia;
- rematches;
- held-item/AI rules.

## Economy / EXP

Status: `PLANNED PORT` from Emerald.

Still required:

- compare the final Emerald implementation against Platinum equivalents;
- classify each change DIRECT / ADAPT / PLATINUM-SPECIFIC;
- validate final Platinum multipliers/prices through playtesting.

## Poké Balls

Status: `PLANNED PORT` from Emerald.

Still required:

- audit native Platinum ball behavior;
- translate Emerald balance goals to Platinum's larger ball ecosystem;
- lock exact multipliers and availability;
- test capture behavior.

## Breeding

Status: `PLANNED PORT` from Emerald.

Still required:

- Gen IV inheritance audit;
- exact Core 1.0 scope;
- egg-group/egg-move decisions;
- hatch-cycle targets;
- Day Care/economy integration.

## Legendary/Mythical events

Status: `PLANNED`.

Still required:

- native Platinum event-state/source audit;
- Darkrai/Shaymin/Arceus and other event unlock paths;
- event-item requirements;
- permanent one-save acquisition flow;
- softlock/repeatability tests.

## Battle Frontier / postgame

Status: `PARTIAL`.

Captured:

- TM BP price reduction;
- anti-grind philosophy.

Still required:

- general BP earnings/reward audit;
- held-item prices;
- rematches/postgame availability;
- completion rewards.

## QA / release

Status: `PLANNED`.

Future required artifacts include:

- structural validators;
- 493 availability checker;
- evolution-completion checker;
- trainer legality/progression checker;
- move/learnset validator;
- event-state checklist;
- Rev 0/Rev 1 build matrix;
- runtime regression suite for custom mechanics;
- release changelog/patch packaging.

## Immediate recovery/implementation priorities

1. **Finish C1 canonical recovery**: complete locked 82-move ledger + machine-readable manifest.
2. Materialize/verify all five exact C3 ledgers using `/tools/overhaul/recover_c3h_ledgers.py` when working in a local Claude checkout.
3. Reconcile/check in the final guarded TM/HM compatibility apply script after live-source validation.
4. Reconcile/check in the final created-move plumbing/source-patch/apply artifacts after the build gate.
5. Generate a human-readable #001–#493 species authority from machine-readable source rather than manually duplicating it.
6. Build the authoritative evolution manifest.

Once C1 recovery and the live-source implementation artifacts are complete, old chat history should no longer be required to implement the completed Pokémon/move phases correctly.
