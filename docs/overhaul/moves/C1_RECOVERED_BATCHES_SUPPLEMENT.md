# Pass C1 Recovery Supplement — Additional Locked Batches

> **Status: recovered locked evidence; supplements `C1_EXISTING_MOVE_REBALANCE_RECOVERY.md`.**
>
> This is still not the final 82-edit implementation manifest. Values below were recovered from locked August 20, 2026 Pass C1 checkpoints. Missing batches remain fail-closed.

## Batch 2 — Physical Poison Offense

### Changed

| Move | Final values | Effect |
|---|---|---|
| Poison Sting | 30 BP / 100 Acc / 35 PP | 30% poison |
| Poison Tail | 60 BP / 100 Acc / 25 PP | High crit; 10% poison |
| Gunk Shot | 120 BP / 80 Acc / 5 PP | 30% poison |

### KEEP

- Poison Fang — 50 BP / 100 Acc / 15 PP / 30% badly poison
- Cross Poison — 70 BP / 100 Acc / 20 PP / high crit / 10% poison
- Poison Jab — 80 BP / 100 Acc / 20 PP / 30% poison

---

## Batch 3 — Rock Offense

### Recovered final changes

| Move | Final values | Status |
|---|---|---|
| Rock Throw | 50 BP / 100 Acc / 15 PP | CONFIRMED |
| Rock Tomb | 60 BP / 95 Acc / 10 PP | CONFIRMED; Speed -1 retained |
| Rock Blast | 25 BP per hit ×2–5 / 90 Acc / 10 PP | CONFIRMED |
| AncientPower | 60 BP / 100 Acc | CONFIRMED; omniboost identity retained |
| Power Gem | 80 BP / 100 Acc / 20 PP | CONFIRMED by later C2/C2.5 authority |

Later locked ladder evidence confirms:

- physical: Rock Throw 50 → Rock Tomb 60 → Rock Slide 75 → Stone Edge 100
- special: AncientPower 60 → Power Gem 80

**Full Batch 3 KEEP table still needs exact source recovery before the final 82-edit manifest is closed.**

---

## Batch 4 — Early Grass Offense

### Changed

| Move | Final values | Effect |
|---|---|---|
| Absorb | 30 BP / 100 Acc / 25 PP | 50% drain |
| Vine Whip | 45 BP / 100 Acc / 25 PP | ordinary damage |
| Bullet Seed | 20 BP per hit / 100 Acc / 20 PP | 2–5 hits |
| Mega Drain | 50 BP / 100 Acc / 15 PP | 50% drain |
| Giga Drain | 75 BP / 100 Acc / 10 PP | 50% drain |

### KEEP

- Razor Leaf — 55 BP / 95 Acc / high crit
- Magical Leaf — 60 BP / never miss / 20 PP
- Seed Bomb — 80 BP / 100 Acc / 15 PP
- Energy Ball — 80 BP / 100 Acc / existing 10% Sp. Def drop

---

## Batch 5 — Fighting Offense

### Changed

| Move | Final values | Effect |
|---|---|---|
| Arm Thrust | 20 BP per hit ×2–5 / 100 Acc / 20 PP | multi-hit retained |
| Drain Punch | 75 BP / 100 Acc / 10 PP | 50% drain retained |
| Vital Throw | 80 BP / never miss | -1 priority retained |
| Submission | 90 BP / 95 Acc | 1/4 recoil retained |

### KEEP

- Karate Chop
- Double Kick
- Force Palm
- Wake-Up Slap
- Brick Break
- Revenge
- Sky Uppercut
- Cross Chop

---

## Batch 6 — Physical Ghost & Dark Offense

### Changed

| Move | Final value |
|---|---|
| Lick | 30 BP |
| Astonish | 40 BP |
| Shadow Punch | 70 BP |
| Knock Off | 40 BP |
| Thief | 60 BP |

Existing effects/accuracy identities remain unless separately documented by the final audit.

### KEEP

- Shadow Sneak
- Shadow Claw
- Pursuit
- Bite
- Faint Attack
- Payback
- Assurance
- Night Slash
- Crunch
- Sucker Punch

---

## Batch 7 — Ice Offense & Access

**No numerical move-data changes were locked in this batch.**

Explicit KEEP:

- Powder Snow — 40 BP / 100 Acc / 25 PP / 10% freeze
- Ice Shard — 40 BP / 100 Acc / +1 priority
- Icy Wind — 55 BP / 95 Acc / Speed -1
- Aurora Beam — 65 BP / 100 Acc / 10% Attack drop
- Ice Fang — 65 BP / 95 Acc
- Avalanche — 60 BP / 100 Acc / doubles after being hit
- Ice Punch — 75 BP / 100 Acc / 10% freeze
- Ice Ball — 30 BP / 90 Acc / escalating lock
- Ice Beam — 95 BP / 100 Acc / 10 PP / 10% freeze
- Blizzard — 120 BP / 70 Acc / 5 PP / 10% freeze

The later final catch-up pass separately changed **Icicle Spear → 20 BP per hit / 20 PP**; that catch-up value is already recorded in the main recovery ledger.

---

## Batch 8A — Special Category Balance

### Changed

| Move | Final values | Notes |
|---|---|---|
| Mud-Slap | 30 BP | existing accuracy-drop effect retained |
| Mud Bomb | 70 BP / 95 Acc | existing accuracy-drop behavior retained |
| Ominous Wind | 10 PP | 60 BP / omniboost identity retained |
| Mirror Shot | 70 BP / 95 Acc | existing accuracy-drop chance retained |

## Batch 8B — Physical Category Balance

**No move-data changes.**

Physical Fire, Electric, and Psychic ladders were deliberately left unchanged; remaining problems were treated as distribution/access issues for later Pass C work.

---

## Batch 9D — Status & Control Reliability

### Changed

| Move | Final accuracy |
|---|---:|
| String Shot | 100 |
| Screech | 90 |
| Metal Sound | 90 |
| Kinesis | 100 |
| Supersonic | 70 |
| Sing | 65 |
| GrassWhistle | 65 |
| Hypnosis | 70 |
| Will-O-Wisp | 85 |
| Toxic | 90 |
| PoisonPowder | 90 |
| Glare | 90 |

No effect rewrites and no new mechanics were introduced.

### KEEP

- Sleep Powder
- Stun Spore
- Confuse Ray

---

## Batch 9E — Recovery & Sustain

### Changed

| Move | Final PP |
|---|---:|
| Synthesis | 10 |
| Morning Sun | 10 |
| Moonlight | 10 |

No recovery-effect rewrite was made.

### KEEP

- Recover
- Softboiled
- Milk Drink
- Slack Off
- Heal Order
- Roost
- Wish
- Rest
- Aqua Ring
- Ingrain
- Leech Seed

---

## Remaining recovery gaps after this supplement

The full 82-edit ledger still requires:

1. the complete Batch 3 KEEP table;
2. the **final superseding Batch 9F trapping values** (Sand Tomb is independently confirmed at 50 BP / 95 Acc / 15 PP, but the rest of 9F is not yet safely recovered at its final revision);
3. any earlier type/category batches not represented by Batch 1–8A here/main recovery file;
4. any final-audit corrections not yet surfaced by downstream C2/C2.5 dependencies;
5. exact move-data fields/flags for every changed move in the eventual machine-readable manifest.

Until the final manifest contains exactly **82 edits** and passes a live-source validation, Claude must continue treating C1 implementation as blocked on canonical recovery rather than filling gaps by inference.
