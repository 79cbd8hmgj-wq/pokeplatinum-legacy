# Pass C1 Recovery Supplement — Historical Evidence

> **Status: RECOVERED / RECONCILED.**
>
> This file preserves the batch-by-batch recovery evidence used to reconstruct C1. The current human-readable authority is `C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`; the machine-readable implementation authority is `../implementation/c1_move_changes_manifest.json`.

## Batch 2 — Physical Poison Offense

- Poison Sting — **30 BP / 100 Acc / 35 PP**; 30% poison preserved.
- Poison Tail — **60 BP / 100 Acc / 25 PP**; high crit + poison preserved.
- Gunk Shot — **120 BP / 80 Acc / 5 PP**; poison preserved.

KEEP: Poison Fang, Cross Poison, Poison Jab.

## Batch 3 — Rock Offense

- Rock Throw — **50 / 100 / 15**.
- Rock Tomb — **60 / 95 / 10**; Speed -1 retained.
- Rock Blast — **25 ×2–5 / 90 / 10**.
- AncientPower — **60 / 100 / 10**; omniboost retained.
- Power Gem — **80 / 100 / 20**.

KEEP: Rollout, Rock Slide, Stone Edge.

## Batch 4 — Early Grass Offense

- Absorb — **30 / 100 / 25**; drain retained.
- Vine Whip — **45 / 100 / 25**.
- Bullet Seed — **20 ×2–5 / 100 / 20**.
- Mega Drain — **50 / 100 / 15**; drain retained.
- Giga Drain — **75 / 100 / 10**; drain retained.

KEEP: Razor Leaf, Magical Leaf, Seed Bomb, Energy Ball.

## Batch 5 — Fighting Offense

- Arm Thrust — **20 ×2–5 / 100 / 20**.
- Drain Punch — **75 / 100 / 10**; drain retained.
- Vital Throw — **80 BP**; never-miss and -1 priority retained.
- Submission — **90 / 95**; recoil retained.

KEEP: Karate Chop, Double Kick, Force Palm, Wake-Up Slap, Brick Break, Revenge, Sky Uppercut, Cross Chop.

## Batch 6 — Physical Ghost & Dark Offense

- Lick — **30 BP**.
- Astonish — **40 BP**.
- Shadow Punch — **70 BP**.
- Knock Off — **40 BP**.
- Thief — **60 BP**.

KEEP: Shadow Sneak, Shadow Claw, Pursuit, Bite, Faint Attack, Payback, Assurance, Night Slash, Crunch, Sucker Punch.

## Batch 7 — Ice Offense & Access

No edits in this batch. Icicle Spear was changed later in the final catch-up to **20 BP per hit / 20 PP**.

## Batch 8A — Special Category Balance

- Mud-Slap — **30 BP**.
- Mud Bomb — **70 / 95**.
- Ominous Wind — **10 PP**.
- Mirror Shot — **70 / 95**.

Batch 8B made no move-data edits.

## Batch 9D — Status & Control Reliability

Final accuracies:

- String Shot 100
- Screech 90
- Metal Sound 90
- Kinesis 100
- Supersonic 70
- Sing 65
- GrassWhistle 65
- Hypnosis 70
- Will-O-Wisp 85
- Toxic 90
- PoisonPowder 90
- Glare 90

No effect rewrites/new mechanics.

KEEP: Sleep Powder, Stun Spore, Confuse Ray.

## Batch 9E — Recovery & Sustain

- Synthesis — **10 PP**.
- Morning Sun — **10 PP**.
- Moonlight — **10 PP**.

Recovery formulas unchanged.

## Batch 9F reconciliation

The authoritative Platinum lock is:

- Bind — **30 / 90 / 20**.
- Wrap — **30 / 90 / 20**.
- Fire Spin — **35 / 90 / 15**.
- Whirlpool — **35 / 90 / 15**.
- Sand Tomb — **35 / 90 / 15**.
- Clamp — **35 / 90 / 10**.
- Magma Storm — **KEEP 120 / 70 / 5**.

Trapping duration and residual-damage behavior remain unchanged.

The previously surfaced Sand Tomb **50/95** value came from a separate Emerald buff-first move spec and is not Platinum C1 authority.

## Recovery result

- 82/82 C1 edited moves identified.
- Final values reconciled.
- Only move-effect reassignment: Razor Wind charge-high-crit → immediate high-crit.
- Canonical machine manifest exists.
- Remaining work is implementation against current main with live-source before-value guards, not design recovery.
