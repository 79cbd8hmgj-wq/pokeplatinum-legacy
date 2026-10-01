# Pokémon Platinum Overhaul — EXP, Money, Shops, and Item Economy

Status: **LOCKED SPEC**

## 1. Scaling authority

Platinum is the numeric baseline.

Emerald provides philosophy and implementation precedent only. Do not import Emerald trainer levels, wild/trainer EXP multipliers, shop multipliers, or money values directly.

All progression tuning must be evaluated against:
- Platinum's native species EXP yields and growth tables;
- Platinum's native 1.5x trainer-battle EXP bonus;
- the overhaul's team-wide EXP distribution;
- the locked trainer boss curve;
- a player who uses a rotating team and explores normally without deliberate grinding.

## 2. Team-wide EXP model

### 2.1 Preserve Platinum's EXP pool

For each defeated opposing Pokémon, calculate the same raw pool Platinum currently uses:

`raw_pool = floor(base_exp_reward * defeated_level / 7)`

Then preserve Platinum's existing battle-type modifiers:
- wild battle: 1.0x;
- trainer battle: 1.5x per recipient after allocation, matching current behavior;
- Lucky Egg: 1.5x individual recipient;
- same-language traded Pokémon: 1.5x individual recipient;
- foreign-language traded Pokémon: 1.7x individual recipient.

Do **not** add Emerald's wild/trainer EXP multipliers.

### 2.2 Conserved party distribution

The overhaul uses two shares of the raw pool:

- **Battle share: 60%**
- **Team share: 40%**

Eligible Pokémon:
- valid party species;
- not fainted;
- below Lv100;
- Eggs are excluded.

#### Battle group

The battle group is the unique set of:
- Pokémon that actually participated against the defeated opponent; plus
- eligible Pokémon holding Exp. Share.

Split the 60% battle share equally among this group.

A participating Pokémon holding Exp. Share is counted once, not twice.

#### Team group

Split the 40% team share equally among **all eligible party Pokémon**, including battle-group members.

Therefore, with one active Pokémon and a six-member healthy party:
- active receives about 66.7% of the raw pool before individual modifiers;
- each benched party member receives about 6.7%;
- total raw EXP distributed remains approximately 100%, subject only to integer rounding.

With a six-Pokémon party and no individual bonuses, team-wide EXP does **not** become the modern 350%-of-base style system.

### 2.3 Exp. Share identity

Exp. Share remains a held item.

Its new purpose is **priority training**, not creation of extra EXP:
- a healthy benched holder joins the 60% battle group;
- the total EXP budget remains conserved.

This preserves the item's identity and makes it useful for catching up a newly obtained Pokémon.

Multiple Exp. Shares are allowed but merely divide the battle-share pool among more priority recipients.

### 2.4 EV behavior

Team-share-only recipients do **not** receive EVs.

EVs remain tied to:
- actual battle participation; or
- an explicit future EV-training mechanic if separately approved.

Holding Exp. Share does not passively spread EVs under this overhaul.

This avoids homogenizing the entire party's EVs simply because EXP is team-wide.

### 2.5 Fainted / Lv100 behavior

- fainted Pokémon receive no EXP;
- Lv100 Pokémon receive no EXP and are excluded from the team-share denominator;
- empty slots/Eggs are excluded;
- EXP that would otherwise be wasted on an ineligible slot is redistributed among eligible recipients.

## 3. Progression calibration

Because total base EXP is conserved, the overhaul begins with Platinum's existing trainer/wild EXP output rather than multiplying it.

Final boss levels are calibrated through simulation after encounter and trainer manifests exist.

Required simulation profiles:

### Direct player
- mandatory battles;
- minimal optional trainers;
- little incidental wild battling.

Target: typically no more than 4 levels below the current boss ace.

### Normal explorer — primary target
- mandatory battles;
- a substantial but not exhaustive share of optional trainers;
- normal catching/exploration;
- rotating 5–6 member party;
- no deliberate grinding.

Target:
- party average usually 1–3 levels below boss ace;
- strongest party member may approach ace level;
- no grinding should be required.

### Completionist
- most/all route trainers;
- substantial catching/exploration;
- no dedicated level grinding.

Target:
- party average should normally not exceed boss ace by more than ~2 levels;
- repeated overleveling beyond this triggers trainer-level or EXP-flow review.

Trainer team composition and relative boss order are locked. Exact levels may move modestly if the simulation proves the team-wide system materially shifts expected levels.

## 4. Trainer prize money

Preserve Platinum's native prize formula:

`last_party_level * 4 * trainer_class_multiplier`

including existing doubles/tag behavior and Amulet Coin/Luck Incense multiplier behavior.

Do not apply a global money multiplier.

### Targeted low-payout cleanup

Raise only extreme low-paying ordinary classes:

- Tuber: 1 → 3
- Poké Kid: 2 → 4
- Ninja Boy: 2 → 4

Keep ordinary 4+ multipliers unchanged unless later simulation reveals a specific problem.

Keep:
- Rival 25;
- Gym Leaders 30;
- Elite Four 30;
- Cynthia 50;
- Galactic Grunts 10;
- Commanders 20;
- Cyrus 45.

Reason: lower shop friction already increases purchasing power. Increasing all payouts as well would inflate the economy.

## 5. Healing-item pricing

Reduce routine healing friction while preserving meaningful high-end costs.

Locked prices:

| Item | Vanilla | Overhaul |
|---|---:|---:|
| Potion | 300 | 200 |
| Super Potion | 700 | 500 |
| Hyper Potion | 1200 | 900 |
| Max Potion | 2500 | 2000 |
| Full Restore | 3000 | 2500 |
| Revive | 1500 | 1200 |

Status medicine should use roughly 75–80% of vanilla price, rounded to clean 50/100-Pokédollar increments.

Full Heal remains a meaningful convenience purchase rather than replacing every individual status cure.

Do not change battle effectiveness of healing items in this phase.

## 6. Vitamins

Veilstone remains the main vitamin shop.

All six standard vitamins:
- HP Up
- Protein
- Iron
- Calcium
- Zinc
- Carbos

change from 9800 to **4900**.

This makes controlled stat development practical without making six-Pokémon vitamin optimization trivial.

Vitamin EV mechanics remain Gen IV mechanics unless separately redesigned.

## 7. Move Reminder

The Move Reminder remains in Pastoria but becomes **free**.

Remove the Heart Scale payment requirement.

Rationale:
- the overhaul deliberately changes many level-up progressions;
- experimentation should not require mining/farming;
- Move Reminder access is already progression-gated by reaching Pastoria.

Heart Scale may remain as a collectible/sellable item but is no longer required for move relearning.

## 8. Move Tutor shard economy

Keep Platinum's tutor locations, move lists, and shard-color identity.

Halve every nonzero shard component:
- new_cost = ceil(vanilla_cost / 2);
- zero remains zero.

Examples:
- 8 Red → 4 Red;
- 2 Red + 6 Blue → 1 Red + 3 Blue;
- 2 of each color → 1 of each.

Do not make tutors free.

This keeps Underground/exploration shards relevant while cutting repetitive collection approximately in half.

## 9. Evolution stones

Evolution stones are the only items that directly cause evolution under the locked evolution spec.

Therefore they require reliable access.

Policy:
- preserve field pickups and existing special sources;
- add a repeatable stone shop source by midgame, no later than Veilstone/roughly the fourth-badge window;
- all standard evolution stones required by #001–#493 must be purchasable before the Elite Four;
- use each stone's existing reasonable base price when possible rather than artificially making them expensive;
- no version, daily RNG, Pickup, Underground RNG, or wild-held-item farming may be the sole repeatable source.

Former non-stone evolution items are not required for evolution. Items with independent battle utility may remain for that utility.

## 10. Rare Candies

Pre-Elite Four:
- preserve curated field/gift rewards;
- do not add an unlimited early Rare Candy shop.

Postgame:
- add an unlimited purchase source in the Battle Zone or equivalent postgame hub;
- target purchase price: **5000** Pokédollars (the current item data is 4800; implementation may use 5000 if changing the base price is clean, otherwise retain 4800).

Rare Candies are a postgame convenience/catch-up tool, not the primary campaign leveling system.

## 11. General mart progression

Preserve Platinum's badge-gated common-mart structure as the baseline.

Do not flood early marts with endgame items.

Quality-of-life rules:
- basic healing remains available on schedule;
- Great/Ultra Ball timing belongs to the separate Poké Ball phase;
- evolution stones gain reliable midgame repeatability;
- vitamins remain Veilstone-centered;
- specialty marts keep regional identity;
- postgame hubs may consolidate convenience stock;
- TMs remain governed by the locked reusable-TM/source policy, not this economy pass.

## 12. Money sinks and anti-inflation

Because:
- reusable TMs reduce duplicate-TM spending;
- healing is cheaper;
- Move Reminder becomes free;

the overhaul must retain meaningful optional sinks:

- vitamins at 4900;
- specialty Poké Balls (D3);
- evolution stones;
- held battle items where already sold;
- postgame Rare Candies;
- Game Corner / Frontier systems where appropriate.

Do not simultaneously:
- globally boost payouts;
- globally cut all prices;
- and increase EXP.

## 13. Battle Point economy boundary

Detailed BP/Frontier rewards belong to D6.

D2 only locks:
- BP grind should be lower than vanilla;
- already-locked TM BP prices remain authority;
- do not redesign Frontier rewards here.

## 14. Acceptance targets

The D2 system is successful when:
- a normal explorer can maintain a rotating six-Pokémon party without deliberate grinding;
- team-wide sharing does not multiply base EXP severalfold;
- a completionist does not routinely overlevel bosses by large margins;
- direct players can recover through optional trainers/Exp. Share priority rather than grass grinding;
- routine healing and move experimentation are materially less tedious;
- money remains useful;
- evolution stones and tutors are reliably accessible;
- no Emerald numeric multiplier is substituted for Platinum calibration.
