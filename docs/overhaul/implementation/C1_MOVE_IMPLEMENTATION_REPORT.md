# C1 Existing-Move Rebalance — Implementation Report

Status: source-applied; CI/build verification pending.

- Manifest entries applied: **82**
- Move data files changed: **82**
- New moves: **0**
- New battle mechanics: **0**
- Razor Wind is the only effect reassignment; its description is updated.
- Trapping duration/residual mechanics remain unchanged.

## Applied edits

| Move | Batch | Before -> target |
|---|---|---|
| Fury Cutter | 1 | power: 10 -> 20; accuracy: 95 -> 100 |
| Leech Life | 1 | power: 20 -> 40; pp: 15 -> 20 |
| Pin Missile | 1 | power: 14 -> 20; accuracy: 85 -> 95 |
| Twineedle | 1 | power: 25 -> 30 |
| Silver Wind | 1 | pp: 5 -> 10 |
| Poison Sting | 2 | power: 15 -> 30 |
| Poison Tail | 2 | power: 50 -> 60 |
| Gunk Shot | 2 | accuracy: 70 -> 80 |
| Rock Throw | 3 | accuracy: 90 -> 100 |
| Rock Tomb | 3 | power: 50 -> 60; accuracy: 80 -> 95 |
| Rock Blast | 3 | accuracy: 80 -> 90 |
| AncientPower | 3 | pp: 5 -> 10 |
| Power Gem | 3 | power: 70 -> 80 |
| Absorb | 4 | power: 20 -> 30 |
| Vine Whip | 4 | power: 35 -> 45; pp: 15 -> 25 |
| Bullet Seed | 4 | power: 10 -> 20; pp: 30 -> 20 |
| Mega Drain | 4 | power: 40 -> 50 |
| Giga Drain | 4 | power: 60 -> 75 |
| Arm Thrust | 5 | power: 15 -> 20 |
| Drain Punch | 5 | power: 60 -> 75; pp: 5 -> 10 |
| Vital Throw | 5 | power: 70 -> 80 |
| Submission | 5 | power: 80 -> 90; accuracy: 80 -> 95 |
| Lick | 6 | power: 20 -> 30 |
| Astonish | 6 | power: 30 -> 40 |
| Shadow Punch | 6 | power: 60 -> 70 |
| Knock Off | 6 | power: 20 -> 40 |
| Thief | 6 | power: 40 -> 60 |
| Mud-Slap | 8A | power: 20 -> 30 |
| Mud Bomb | 8A | power: 65 -> 70; accuracy: 85 -> 95 |
| Ominous Wind | 8A | pp: 5 -> 10 |
| Mirror Shot | 8A | power: 65 -> 70; accuracy: 85 -> 95 |
| Tackle | 9A | power: 35 -> 40; accuracy: 95 -> 100 |
| DoubleSlap | 9A | power: 15 -> 20; accuracy: 85 -> 90 |
| Barrage | 9A | power: 15 -> 20; accuracy: 85 -> 90 |
| Fury Swipes | 9A | power: 18 -> 20; accuracy: 80 -> 90 |
| Comet Punch | 9A | power: 18 -> 20; accuracy: 85 -> 90 |
| Slam | 9A | power: 80 -> 85; accuracy: 75 -> 95 |
| Take Down | 9A | power: 90 -> 100; accuracy: 85 -> 95 |
| Fury Attack | 9B | power: 15 -> 20; accuracy: 85 -> 90 |
| Bubble | 9B | power: 20 -> 30 |
| Smog | 9B | power: 20 -> 30; accuracy: 70 -> 90 |
| Air Cutter | 9B | power: 55 -> 60; accuracy: 95 -> 100 |
| Twister | 9B | power: 40 -> 50 |
| Bone Club | 9B | power: 65 -> 70; accuracy: 85 -> 95 |
| Steel Wing | 9B | power: 70 -> 75; accuracy: 90 -> 95 |
| Razor Wind | 9C | effect_type: BATTLE_EFFECT_CHARGE_TURN_HIGH_CRIT -> BATTLE_EFFECT_HIGH_CRITICAL; description updated |
| Skull Bash | 9C | power: 100 -> 120 |
| Bounce | 9C | accuracy: 85 -> 95; pp: 5 -> 10 |
| String Shot | 9D | accuracy: 95 -> 100 |
| Screech | 9D | accuracy: 85 -> 90 |
| Metal Sound | 9D | accuracy: 85 -> 90 |
| Kinesis | 9D | accuracy: 80 -> 100 |
| Supersonic | 9D | accuracy: 55 -> 70 |
| Sing | 9D | accuracy: 55 -> 65 |
| GrassWhistle | 9D | accuracy: 55 -> 65 |
| Hypnosis | 9D | accuracy: 60 -> 70 |
| Will-O-Wisp | 9D | accuracy: 75 -> 85 |
| Toxic | 9D | accuracy: 85 -> 90 |
| PoisonPowder | 9D | accuracy: 75 -> 90 |
| Glare | 9D | accuracy: 75 -> 90 |
| Synthesis | 9E | pp: 5 -> 10 |
| Morning Sun | 9E | pp: 5 -> 10 |
| Moonlight | 9E | pp: 5 -> 10 |
| Bind | 9F | power: 15 -> 30; accuracy: 75 -> 90; pp: 20 -> 20 |
| Wrap | 9F | power: 15 -> 30; accuracy: 85 -> 90; pp: 20 -> 20 |
| Fire Spin | 9F | power: 15 -> 35; accuracy: 70 -> 90; pp: 15 -> 15 |
| Whirlpool | 9F | power: 15 -> 35; accuracy: 70 -> 90; pp: 15 -> 15 |
| Sand Tomb | 9F | power: 15 -> 35; accuracy: 70 -> 90; pp: 15 -> 15 |
| Clamp | 9F | power: 35 -> 35; accuracy: 75 -> 90; pp: 10 -> 10 |
| Rapid Spin | 9H | power: 20 -> 40 |
| Constrict | final_catch_up | power: 10 -> 30 |
| Icicle Spear | final_catch_up | power: 10 -> 20; pp: 30 -> 20 |
| Bone Rush | final_catch_up | accuracy: 80 -> 90 |
| Triple Kick | final_catch_up | power: 10 -> 15 |
| Rolling Kick | final_catch_up | accuracy: 85 -> 95 |
| Mega Punch | final_catch_up | power: 80 -> 90; accuracy: 85 -> 100 |
| Egg Bomb | final_catch_up | accuracy: 75 -> 90 |
| Iron Tail | final_catch_up | accuracy: 75 -> 85 |
| Dragon Rush | final_catch_up | accuracy: 75 -> 85 |
| Psywave | final_catch_up | accuracy: 80 -> 100 |
| Poison Gas | final_catch_up | accuracy: 55 -> 90 |
| Future Sight | final_catch_up | power: 80 -> 100; accuracy: 90 -> 100 |
