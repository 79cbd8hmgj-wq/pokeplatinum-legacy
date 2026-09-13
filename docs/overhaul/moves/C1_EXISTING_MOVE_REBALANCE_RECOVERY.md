# Pass C1 — Existing Move Rebalance

> **Status: RECOVERED / LOCKED DESIGN AUTHORITY**

Pass C1 design was completed and locked on August 20, 2026. The final audit contains **82 edited existing moves**, no new C1 moves, no new C1 mechanics, and one existing-effect reassignment: Razor Wind.

The canonical machine-readable authority is now:

`../implementation/c1_move_changes_manifest.json`

That manifest contains exactly **82 entries** and encodes only the fields C1 changes. All unlisted move fields/effects/flags remain Platinum behavior unless the manifest explicitly says otherwise.

## Implementation rule

Before applying C1, Claude must validate every manifest entry against current `main` and generate before-value/source guards. C1 is recovered, but it is **not yet implemented** on current main.

Do not use older proposal spreadsheets or Emerald move-rework files as Platinum C1 authority.

## Core batch rulings

### Batch 1 — Bug Offense

- Fury Cutter — **20 BP / 100 Acc / 20 PP**; consecutive doubling preserved.
- Leech Life — **40 / 100 / 20**; 50% drain preserved.
- Pin Missile — **20 BP per hit / 95 Acc / 20 PP**; 2–5 hits.
- Twineedle — **30 BP per hit ×2 / 100 / 20**; poison behavior preserved.
- Silver Wind — **60 / 100 / 10**; omniboost behavior preserved.

KEEP: Bug Bite, U-turn, Signal Beam, X-Scissor, Bug Buzz, Megahorn.

### Batch 2 — Physical Poison Offense

- Poison Sting — **30 / 100 / 35**.
- Poison Tail — **60 / 100 / 25**; high crit + poison preserved.
- Gunk Shot — **120 / 80 / 5**; poison behavior preserved.

KEEP: Poison Fang, Cross Poison, Poison Jab.

### Batch 3 — Rock Offense

- Rock Throw — **50 / 100 / 15**.
- Rock Tomb — **60 / 95 / 10**; guaranteed Speed -1 preserved.
- Rock Blast — **25 ×2–5 / 90 / 10**.
- AncientPower — **60 / 100 / 10**; omniboost preserved.
- Power Gem — **80 / 100 / 20**.

KEEP: Rollout, Rock Slide, Stone Edge.

### Batch 4 — Early Grass Offense

- Absorb — **30 / 100 / 25**; drain preserved.
- Vine Whip — **45 / 100 / 25**.
- Bullet Seed — **20 ×2–5 / 100 / 20**.
- Mega Drain — **50 / 100 / 15**; drain preserved.
- Giga Drain — **75 / 100 / 10**; drain preserved.

KEEP: Razor Leaf, Magical Leaf, Seed Bomb, Energy Ball.

### Batch 5 — Fighting Offense

- Arm Thrust — **20 ×2–5 / 100 / 20**.
- Drain Punch — **75 / 100 / 10**; drain preserved.
- Vital Throw — **80 BP**, never-miss and -1 priority preserved.
- Submission — **90 / 95**, recoil preserved.

KEEP: Karate Chop, Double Kick, Force Palm, Wake-Up Slap, Brick Break, Revenge, Sky Uppercut, Cross Chop.

### Batch 6 — Physical Ghost & Dark Offense

- Lick — **30 BP**.
- Astonish — **40 BP**.
- Shadow Punch — **70 BP**.
- Knock Off — **40 BP**.
- Thief — **60 BP**.

KEEP: Shadow Sneak, Shadow Claw, Pursuit, Bite, Faint Attack, Payback, Assurance, Night Slash, Crunch, Sucker Punch.

### Batch 7 — Ice Offense & Access

No edits in this batch. The later final catch-up changes Icicle Spear.

### Batch 8A — Special Category Balance

- Mud-Slap — **30 BP**.
- Mud Bomb — **70 / 95**.
- Ominous Wind — **10 PP**.
- Mirror Shot — **70 / 95**.

Batch 8B made no move-data edits.

### Batch 9A — Normal Offense Cleanup

- Tackle — **40 / 100**.
- DoubleSlap — **20 per hit / 90**.
- Barrage — **20 per hit / 90**.
- Fury Swipes — **20 per hit / 90**.
- Comet Punch — **20 per hit / 90**.
- Slam — **85 / 95**.
- Take Down — **100 / 95**.

KEEP: Pound, Scratch, Quick Attack, Headbutt, Double-Edge.

### Batch 9B — Low/Mid-Power Offense Cleanup

- Fury Attack — **20 per hit / 90**.
- Bubble — **30 BP**.
- Smog — **30 / 90**.
- Air Cutter — **60 / 100**; high crit preserved.
- Twister — **50 BP**.
- Bone Club — **70 / 95**.
- Steel Wing — **75 / 95**.

KEEP: Metal Claw, Bonemerang, Spike Cannon.

### Batch 9C — Two-Turn / Charge Attacks

- Razor Wind — **80 / 100 / 10**, charge turn removed; high crit retained by changing effect to `BATTLE_EFFECT_HIGH_CRITICAL`. Its description must also be updated.
- Skull Bash — **120 / 100 / 15**; two-turn structure and first-turn Defense raise retained.
- Bounce — **85 / 95 / 10**; two-turn/paralysis behavior retained.

KEEP: Sky Attack, Dig, Dive.

### Batch 9D — Status & Control Reliability

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

No effect rewrites or new mechanics.

KEEP: Sleep Powder, Stun Spore, Confuse Ray.

### Batch 9E — Recovery & Sustain

- Synthesis — **10 PP**.
- Morning Sun — **10 PP**.
- Moonlight — **10 PP**.

Recovery formulas remain unchanged.

### Batch 9F — Trapping & Residual Damage

Final approved Platinum values:

- Bind — **30 / 90 / 20**.
- Wrap — **30 / 90 / 20**.
- Fire Spin — **35 / 90 / 15**.
- Whirlpool — **35 / 90 / 15**.
- Sand Tomb — **35 / 90 / 15**.
- Clamp — **35 / 90 / 10**.
- Magma Storm — **KEEP 120 / 70 / 5**.

**Trapping duration and residual-damage mechanics remain unchanged.** No effect rewrite or new mechanic.

Important supersession note: the previously surfaced **Sand Tomb 50/95** value came from an unrelated Emerald buff-first spec and is **not** Platinum C1 authority.

### Batch 9G — Setup Moves

No edits.

### Batch 9H — Screens, Weather & Field Control

- Rapid Spin — **40 BP**; existing removal behavior retained.

Defog behavior was deliberately deferred to C2.

### Final catch-up audit

- Constrict — **30 BP**.
- Icicle Spear — **20 BP per hit / 20 PP**.
- Bone Rush — **90 Acc**.
- Triple Kick — **15 base BP**.
- Rolling Kick — **95 Acc**.
- Mega Punch — **90 BP / 100 Acc**.
- Egg Bomb — **90 Acc**.
- Iron Tail — **85 Acc**.
- Dragon Rush — **100 BP / 85 Acc**.
- Psywave — **100 Acc**.
- Poison Gas — **90 Acc**.
- Future Sight — **100 BP / 100 Acc**.

KEEP: Mega Kick, Present, ViceGrip, Acid, Sweet Kiss, Rage, SonicBoom, Dragon Rage, Bide, Doom Desire.

## Recovery completeness

- Edited move membership: **82/82 recovered**.
- Final batch values: **recovered**.
- Known effect reassignment: **Razor Wind only**.
- New mechanics: **0**.
- Canonical machine manifest: **present**.
- Live-source before-value guards: **still to be generated/validated by Claude before application**.

C1 is no longer blocked on design recovery. The next step is guarded implementation against current main.
