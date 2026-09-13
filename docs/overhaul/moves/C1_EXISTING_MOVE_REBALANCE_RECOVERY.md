# Pass C1 — Existing Move Rebalance Recovery Ledger

> **Status: RECOVERY IN PROGRESS — NOT YET COMPLETE IMPLEMENTATION AUTHORITY**

Pass C1 design was completed and locked. The final audit produced a source-of-truth Markdown with a complete **82-move edit ledger** plus KEEP rulings and rationale. That final file has not yet been fully migrated into this repository.

This document records only values that have been recovered from locked/final checkpoints or from later design documents that explicitly depend on those final C1 values. It exists to prevent repeated reconstruction and, equally importantly, to prevent Claude or another implementation agent from filling gaps by inference.

## Authority rule

A row marked `CONFIRMED FINAL` may be used as recovered design evidence, but **do not implement the complete C1 pass until the canonical 82-move machine-readable manifest is complete and validated against live Platinum source**.

A row/batch marked `NEEDS FINAL-AUDIT CHECK` is historical evidence only.

If an earlier locked batch conflicts with a later final-audit value, the later final-audit value wins and the earlier value must be marked superseded.

---

## Confirmed final — Batch 1 Bug offense

| Move | Final C1 values | Effect / notes | Status |
|---|---|---|---|
| Fury Cutter | 20 BP / 100 Acc / 20 PP | Consecutive-use doubling preserved | CONFIRMED FINAL |
| Leech Life | 40 / 100 / 20 | Restores 50% of damage dealt | CONFIRMED FINAL |
| Pin Missile | 20 BP per hit / 95 Acc / 20 PP | 2–5 hits | CONFIRMED FINAL |
| Twineedle | 30 BP per hit ×2 / 100 Acc / 20 PP | Existing poison behavior preserved | CONFIRMED FINAL |
| Silver Wind | 60 / 100 / 10 | Existing 10% omniboost preserved | CONFIRMED FINAL |

### Explicit KEEP rulings

- Bug Bite — 60 / 100 / 20; Berry interaction unchanged.
- U-turn — 70 / 100 / 20; switch-after-damage behavior unchanged.
- Signal Beam — 75 / 100 / 15; confusion chance unchanged.
- X-Scissor — 80 / 100 / 15.
- Bug Buzz — 90 / 100 / 10; Sp. Def-drop chance unchanged.
- Megahorn — 120 / 85 / 10.

---

## Confirmed final — Batch 9A Normal offense cleanup

| Move | Final C1 values | Status |
|---|---|---|
| Tackle | 40 BP / 100 Acc | CONFIRMED FINAL |
| DoubleSlap | 20 BP per hit / 90 Acc | CONFIRMED FINAL |
| Barrage | 20 BP per hit / 90 Acc | CONFIRMED FINAL |
| Fury Swipes | 20 BP per hit / 90 Acc | CONFIRMED FINAL |
| Comet Punch | 20 BP per hit / 90 Acc | CONFIRMED FINAL |
| Slam | 85 BP / 95 Acc | CONFIRMED FINAL |
| Take Down | 100 BP / 95 Acc | CONFIRMED FINAL |

Explicit KEEP: Pound, Scratch, Quick Attack, Headbutt, Double-Edge.

---

## Confirmed final — Batch 9B low/mid-power offense cleanup

| Move | Final C1 values | Effect / notes | Status |
|---|---|---|---|
| Fury Attack | 20 BP per hit / 90 Acc | 2–5 hits | CONFIRMED FINAL |
| Bubble | 30 BP / 100 Acc | Existing 10% Speed-drop chance preserved | CONFIRMED FINAL |
| Smog | 30 BP / 90 Acc | Existing 40% poison chance preserved | CONFIRMED FINAL |
| Air Cutter | 60 BP / 100 Acc | High-critical-ratio effect preserved | CONFIRMED FINAL |
| Twister | 50 BP / 100 Acc | Existing 20% flinch chance preserved | CONFIRMED FINAL |
| Bone Club | 70 BP / 95 Acc | Existing 10% flinch chance preserved | CONFIRMED FINAL |
| Steel Wing | 75 BP / 95 Acc | Existing 10% Defense-raise chance preserved | CONFIRMED FINAL |

Explicit KEEP: Metal Claw, Bonemerang, Spike Cannon.

---

## Confirmed final — Batch 9C two-turn / charge attacks

| Move | Final C1 values | Effect / notes | Status |
|---|---|---|---|
| Razor Wind | 80 BP / 100 Acc / 10 PP | Charge turn removed; remains high crit | CONFIRMED FINAL |
| Skull Bash | 120 BP / 100 Acc / 15 PP | Two-turn structure and first-turn Defense raise retained | CONFIRMED FINAL |
| Bounce | 85 BP / 95 Acc / 10 PP | Two-turn; existing 30% paralysis retained | CONFIRMED FINAL |

Explicit KEEP recovered: Sky Attack 140 / 90 / 5 with two-turn/high-crit/flinch identity; Dig 80 / 100 / 10; Dive 80 / 100 / 10.

---

## Confirmed final — Batch 9G setup moves

**No C1 property/effect edits.**

Explicit KEEP:

- Meditate
- Howl
- Sharpen
- Growth
- Swords Dance
- Nasty Plot
- Tail Glow
- Bulk Up
- Calm Mind
- Dragon Dance
- Agility
- Rock Polish
- Harden
- Defense Curl
- Iron Defense
- Amnesia
- Focus Energy
- Charge
- Stockpile

---

## Confirmed final — Batch 9H screens, weather & field control

| Move | Final C1 values | Effect / notes | Status |
|---|---|---|---|
| Rapid Spin | 40 BP | Existing hazard/binding removal behavior retained | CONFIRMED FINAL |

Other reviewed screen/weather/field-control moves were kept unchanged. Defog behavior was deliberately deferred to C2 and is governed by `../tm_hm/TM_HM_SPEC.md`.

---

## Confirmed final — final catch-up audit entries

The final catch-up pass locked the following values:

| Move | Final C1 values | Status |
|---|---|---|
| Constrict | 30 BP | CONFIRMED FINAL |
| Icicle Spear | 20 BP per hit / 20 PP | CONFIRMED FINAL |
| Bone Rush | 90 Acc | CONFIRMED FINAL |
| Triple Kick | 15 base BP | CONFIRMED FINAL |
| Rolling Kick | 95 Acc | CONFIRMED FINAL |
| Mega Punch | 90 BP / 100 Acc | CONFIRMED FINAL |
| Egg Bomb | 90 Acc | CONFIRMED FINAL |
| Iron Tail | 85 Acc | CONFIRMED FINAL |
| Dragon Rush | 100 BP / 85 Acc | CONFIRMED FINAL |
| Psywave | 100 Acc | CONFIRMED FINAL |
| Poison Gas | 90 Acc | CONFIRMED FINAL |
| Future Sight | 100 BP / 100 Acc | CONFIRMED FINAL |

Explicit KEEP from the same catch-up record:

- Mega Kick
- Present
- ViceGrip
- Acid
- Sweet Kiss
- Rage
- SonicBoom
- Dragon Rage
- Bide
- Doom Desire

---

## Confirmed final — later cross-checks from C2/C2.5/C3

The following C1 values are explicitly relied upon by later locked design and therefore are final C1 dependencies:

| Move | Final C1 value(s) | Later dependency evidence |
|---|---|---|
| Power Gem | 80 BP / 100 Acc / 20 PP | C2 TM78 design / special Rock ladder |
| Toxic | 90 Acc | C2 TM roster |
| Bullet Seed | 20 BP per hit / 20 PP | C2 TM roster |
| Giga Drain | 75 BP | C2 TM roster |
| Rock Tomb | 60 BP / 95 Acc | C2 TM roster / Rock ladder |
| Thief | 60 BP | C2 TM roster |
| Drain Punch | 75 BP / 10 PP | C2 Gym-TM preservation |
| Will-O-Wisp | 85 Acc | C2 TM roster |
| Mirror Shot | 70 BP / 95 Acc | C2.5 special-Steel gap audit |
| Ominous Wind | 10 PP | C2.5 special-Ghost gap audit |
| Mud-Slap | 30 BP | C2.5 final Ground ladder |
| Mud Shot | 55 BP | C2.5 final Ground ladder |
| Mud Bomb | 70 BP | C2.5 final Ground ladder |
| Earth Power | 90 BP | C2.5 final Ground ladder |

Additional final ladders used downstream:

- Rock physical: Rock Throw 50 → Rock Tomb 60 → Rock Slide 75 → Stone Edge 100.
- Rock special: AncientPower 60 → Power Gem 80.

---

## Historical Batch 9F conflict — DO NOT IMPLEMENT YET

An earlier locked snapshot of the trapping/residual batch records:

- Bind — 30 BP / 90 Acc / 20 PP
- Wrap — 30 / 90 / 20
- Fire Spin — 35 / 90 / 15
- Whirlpool — 35 / 90 / 15
- Sand Tomb — 35 / 90 / 15
- Clamp — 35 / 90 / 10
- Magma Storm — KEEP 120 / 70 / 5
- trapping duration/effects unchanged

However, later recovered project evidence reports **Sand Tomb final = 50 BP / 95 Acc / 15 PP** with its trapping/damage effect retained.

Therefore Batch 9F is marked:

> **NEEDS FINAL-AUDIT CHECK — probable later supersession exists.**

Do not put any Batch 9F value into the machine-readable implementation manifest until the final source-of-truth or an unambiguous later audit is recovered.

---

## Still unrecovered / incomplete

The final 82-edit ledger is **not yet fully represented here**. In particular, the following batch ranges still require exact final-audit recovery before C1 can become implementation authority:

- Batch 9D
- Batch 9E
- Batch 9F final superseding values
- earlier C1 type/category batches not already represented above
- any final audit corrections not captured by later C2/C2.5 dependencies

## Completion gate

C1 recovery is complete only when all of the following are true:

1. exactly **82 edited existing moves** are represented in a machine-readable manifest;
2. every row has final power/accuracy/PP/effect/flag changes, not just shorthand;
3. all known supersessions are resolved;
4. important KEEP rulings are archived in the human-readable source-of-truth;
5. the manifest is validated against the current Platinum source before application;
6. `CLAUDE.md` no longer needs to block C1 implementation on recovery.

Until then, this document is a recovery ledger, not a license to infer the missing entries.
