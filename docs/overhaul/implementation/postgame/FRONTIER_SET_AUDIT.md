# Battle Frontier Set Audit (D6 F3 / F4)

Start SHA: `98f9cbdf43f9a8ef4c04c3f80e7ee0b6d9482638` - vanilla baseline for type/stat/ability/learnset comparison: `1c1fb925`.

Authority: `docs/overhaul/postgame/BATTLE_FRONTIER_POSTGAME_SPEC.md` s5/s6/s14. The Frontier pool was audited, **not rebuilt**.
Tool: `tools/overhaul/postgame/frontier_audit.py`; fixes: `apply_frontier_set_changes.py`; manifest: `frontier_set_changes.json`.

## Scope

- Sets audited: **951** across **401** species (950 real sets + 1 `none_1` padding set used by Brain pools).
- Checks: constants valid, duplicate/empty move slots, retype representation, lost STAB, stat-redistribution mismatch, moves no longer learnable, identical sets, moves whose type/class changed.

## Result after fixes (live tree)

| Finding | Count |
|---|---:|
| INVALID | 0 |
| RETYPE | 0 |
| LOST_STAB | 0 |
| STAT | 0 |
| REMOVED | 0 |
| DUPLICATE | 0 |
| MOVECHG | 0 |

`MOVECHG` = 0: no move used by a Frontier set changed type or damage class under C1/C2, so no set silently changed STAB or physical/special split.

## Retyped Frontier species (all covered)

| Species | Overhaul types | Vanilla types | Sets | Sets carrying the new type |
|---|---|---|---:|---|
| SPECIES_BLASTOISE | WATER/GROUND | WATER | 4 | GROUND: 1/4 |
| SPECIES_ELECTABUZZ | ELECTRIC/FIGHTING | ELECTRIC | 2 | FIGHTING: 1/2 |
| SPECIES_ELECTIVIRE | ELECTRIC/FIGHTING | ELECTRIC | 4 | FIGHTING: 3/4 |
| SPECIES_FARFETCHD | FIGHTING/FLYING | NORMAL/FLYING | 1 | FIGHTING: 1/1 |
| SPECIES_FERALIGATR | WATER/GROUND | WATER | 4 | GROUND: 1/4 |
| SPECIES_GLALIE | ICE/STEEL | ICE | 4 | STEEL: 3/4 |
| SPECIES_GOLDUCK | WATER/PSYCHIC | WATER | 4 | PSYCHIC: 3/4 |
| SPECIES_LUXIO | ELECTRIC/DARK | ELECTRIC | 2 | DARK: 1/2 |
| SPECIES_LUXRAY | ELECTRIC/DARK | ELECTRIC | 4 | DARK: 2/4 |
| SPECIES_MILOTIC | WATER/DRAGON | WATER | 4 | DRAGON: 1/4 |
| SPECIES_PINSIR | BUG/FIGHTING | BUG | 4 | FIGHTING: 3/4 |
| SPECIES_PSYDUCK | WATER/PSYCHIC | WATER | 1 | PSYCHIC: 1/1 |
| SPECIES_RAICHU | ELECTRIC/STEEL | ELECTRIC | 4 | STEEL: 2/4 |
| SPECIES_SCEPTILE | GRASS/DRAGON | GRASS | 4 | DRAGON: 1/4 |
| SPECIES_SHINX | ELECTRIC/DARK | ELECTRIC | 1 | DARK: 1/1 |
| SPECIES_SLAKING | NORMAL/FIGHTING | NORMAL | 4 | FIGHTING: 1/4 |
| SPECIES_VIGOROTH | NORMAL/FIGHTING | NORMAL | 2 | FIGHTING: 2/2 |

Per spec s5 not every set carries both STAB types (Milotic keeps its special/tank sets; only `milotic_4` uses Dragon).

## Fixes applied (15 sets)

| Set | Reason | Moves before | Moves after |
|---|---|---|---|
| farfetchd_1 | RETYPE: Fighting/Flying Farfetch'd had no Fighting move | SLASH, AIR_CUTTER, KNOCK_OFF, SWORDS_DANCE | SLASH, CLOSE_COMBAT, KNOCK_OFF, SWORDS_DANCE |
| raichu_1 | STAT: all-physical set on Atk 70 / SpA 100 Raichu; keeps Steel STAB via Flash Cannon | THUNDER_PUNCH, IRON_TAIL, SLAM, QUICK_ATTACK | THUNDERBOLT, FLASH_CANNON, GRASS_KNOT, QUICK_ATTACK |
| raichu_2 | STAT: all-physical set on Atk 70 / SpA 100 Raichu | THUNDER_PUNCH, FOCUS_PUNCH, SWEET_KISS, THUNDER_WAVE | THUNDER, FOCUS_BLAST, SWEET_KISS, THUNDER_WAVE |
| raichu_4 | STAT: all-physical set on Atk 70 / SpA 100 Raichu; adds Steel STAB | VOLT_TACKLE, RETURN, BRICK_BREAK, THUNDER_WAVE | VOLT_TACKLE, FLASH_CANNON, BRICK_BREAK, THUNDER_WAVE |
| glalie_3 | STAT: all-special set on Atk 90 / SpA 70 Glalie; adds Steel STAB | ICE_BEAM, SHADOW_BALL, SIGNAL_BEAM, WATER_PULSE | FROST_RUSH, SHADOW_BALL, IRON_HEAD, ICE_BEAM |
| glalie_4 | STAT: all-special set on Atk 90 / SpA 70 Glalie; adds Steel STAB | BLIZZARD, DARK_PULSE, SHEER_COLD, HAIL | BLIZZARD, IRON_HEAD, SHEER_COLD, HAIL |
| ledian_1 | STAT: all-special set on Atk 85 / SpA 45 Ledian (new Iron Fist ability) | SILVER_WIND, AIR_CUTTER, AGILITY, BATON_PASS | DRAIN_PUNCH, AERIAL_ACE, AGILITY, BATON_PASS |
| beedrill_1 | REMOVED: Assurance no longer learnable | TWINEEDLE, TOXIC, ASSURANCE, AGILITY | TWINEEDLE, TOXIC, POISON_JAB, AGILITY |
| cacturne_1 | REMOVED: Faint Attack no longer learnable | BULLET_SEED, FAINT_ATTACK, SPIKES, INGRAIN | BULLET_SEED, SUCKER_PUNCH, SPIKES, INGRAIN |
| carnivine_2 | REMOVED: Wring Out no longer learnable | SEED_BOMB, WRING_OUT, CRUNCH, INGRAIN | SEED_BOMB, POWER_WHIP, CRUNCH, INGRAIN |
| kabutops_1 | REMOVED: Metal Sound no longer learnable | AQUA_JET, ROCK_TOMB, HARDEN, METAL_SOUND | AQUA_JET, ROCK_TOMB, HARDEN, STEALTH_ROCK |
| lumineon_1 | REMOVED: Captivate no longer learnable | WATER_GUN, U_TURN, CAPTIVATE, ATTRACT | WATER_GUN, U_TURN, AQUA_RING, ATTRACT |
| masquerain_1 | REMOVED: Scary Face no longer learnable | SILVER_WIND, AIR_CUTTER, SWEET_SCENT, SCARY_FACE | SILVER_WIND, AIR_CUTTER, SWEET_SCENT, STUN_SPORE |
| relicanth_1 | REMOVED: Mud Sport no longer learnable | WATER_PULSE, ROCK_TOMB, MUD_SPORT, HARDEN | WATER_PULSE, ROCK_TOMB, YAWN, HARDEN |
| solrock_1 | REMOVED: Psywave no longer learnable | PSYWAVE, ROCK_TOMB, COSMIC_POWER, LIGHT_SCREEN | PSYCHIC, ROCK_TOMB, COSMIC_POWER, LIGHT_SCREEN |

Nature changes accompany stat-driven fixes (see manifest `nature`).

## Battle Hall static type pool

`sBattleHallPotentialOpponentTypes` is a static vanilla type table, so retyped species drifted out of their Hall type groups. 17 entries were corrected to the overhaul types (Wormadam entries are form-specific and intentionally skipped). Records: `frontier_set_changes.json` -> `hall_pool_type_changes`.

## Frontier Brains (F4)

- Palmer (Tower), Dahlia (Arcade) and Darach (Castle) Silver/Gold sets were audited separately: no INVALID/RETYPE/LOST_STAB/STAT/REMOVED finding touches a Brain set. **No Brain edits.**
- Palmer Silver's Milotic is Surf/Ice Beam special - consistent with its locked Water/Dragon special-tank identity.
- Thorton (Factory rentals) and Argenta (Hall type-matched pool) have no fixed sets; the Hall pool fix above covers Argenta's retype drift.
- Milestone/streak numbers, facility gimmicks and difficulty relationships are unchanged.

## Ability / stat changes reviewed

Ability changes on Frontier species (Farfetch'd, Furret, Ledian, Lopunny, Wigglytuff) and stat redistributions on 19 species were screened by the STAT heuristic (all-physical or all-special sets whose attacking stat flipped). Only Raichu, Glalie and Ledian tripped it; those sets were fixed above. Sets left as-is are treated as valid under spec s5 ("do not force every set").

## Legality note

Frontier legality is checked against overhaul move/species data (constants exist, no vanilla-learnable move lost to C3). Vanilla Frontier sets that were already outside a species' learnset (event/egg moves) are inherited and not flagged.
