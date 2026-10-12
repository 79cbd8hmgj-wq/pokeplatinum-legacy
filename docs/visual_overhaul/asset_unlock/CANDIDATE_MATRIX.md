# DAU1 - refreshed cross-library candidate matrix

Generated from the decoded `ASSET_CATALOG.json` by `tools/visual_overhaul/dau1_unlock.py matrix`. Nothing here is a visual approval; every shortlist entry still needs owner/visual QA, and licence status is unverified (`PROVENANCE.md`).

**P1/P2 move binding: BLOCKED_INPUT** - the B9 everyday-moves manifest (pokemon_opal_everyday_moves_b9_manifest_v2) that names the 19 P1 and 14 P2 moves is not in the repository or in the DAU1 package; candidates are therefore keyed by effect role, not by move.

Budgets: <= 192 OBJ tiles per sheet, <= 15 colours (index 0 transparent).

Decoded, Opal-convertible rows evaluated: **3198**. Decisions: candidate 135, duplicate_alias 1410, needs_visual_review 944, rejected 667, shortlisted 42.

## Rows per library

| Library | Rows |
|---|---:|
| crystal | 64 |
| diamond | 688 |
| emerald | 279 |
| firered | 279 |
| hgss | 1124 |
| pmd_sky | 184 |
| ranger2 | 302 |
| ruby | 278 |

## Shortlist by effect role (named donors only)

| Role | Shortlisted | Library | Tiles~ | Colours | Frames | Rationale |
|---|---|---|---:|---:|---:|---|
| electric | `sparkle_1.png` | emerald | 128 | 4 | 1 | electric: best decoded emerald candidate by size/frames (128 est. OBJ tiles <= 192, 4 colours, 1 frame(s)); needs visual QA before use |
| electric | `BATTLE_ANIM_OBJ_MASTER_BALL_SPARKLE` | crystal | 2 | 3 | 2 | electric: best decoded crystal candidate by size/frames (2 est. OBJ tiles <= 192, 3 colours, 2 frame(s)); needs visual QA before use |
| electric | `shock.png` | emerald | 96 | 8 | 1 | electric: best decoded emerald candidate by size/frames (96 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |
| fire | `fire.png` | emerald | 128 | 10 | 1 | fire: best decoded emerald candidate by size/frames (128 est. OBJ tiles <= 192, 10 colours, 1 frame(s)); needs visual QA before use |
| fire | `BATTLE_ANIM_OBJ_BURNED` | crystal | 26 | 3 | 8 | fire: best decoded crystal candidate by size/frames (26 est. OBJ tiles <= 192, 3 colours, 8 frame(s)); needs visual QA before use |
| fire | `fire_plume.png` | emerald | 72 | 8 | 1 | fire: best decoded emerald candidate by size/frames (72 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |
| ghost_dark | `gray_smoke.png` | emerald | 80 | 9 | 1 | ghost_dark: best decoded emerald candidate by size/frames (80 est. OBJ tiles <= 192, 9 colours, 1 frame(s)); needs visual QA before use |
| ghost_dark | `BATTLE_ANIM_OBJ_HAZE` | crystal | 8 | 2 | 2 | ghost_dark: best decoded crystal candidate by size/frames (8 est. OBJ tiles <= 192, 2 colours, 2 frame(s)); needs visual QA before use |
| ghost_dark | `round_shadow.png` | emerald | 48 | 7 | 1 | ghost_dark: best decoded emerald candidate by size/frames (48 est. OBJ tiles <= 192, 7 colours, 1 frame(s)); needs visual QA before use |
| grass_nature | `vine_2.png` | emerald | 80 | 3 | 1 | grass_nature: best decoded emerald candidate by size/frames (80 est. OBJ tiles <= 192, 3 colours, 1 frame(s)); needs visual QA before use |
| grass_nature | `BATTLE_ANIM_OBJ_FLOWER` | crystal | 8 | 3 | 2 | grass_nature: best decoded crystal candidate by size/frames (8 est. OBJ tiles <= 192, 3 colours, 2 frame(s)); needs visual QA before use |
| grass_nature | `vine.png` | emerald | 80 | 5 | 1 | grass_nature: best decoded emerald candidate by size/frames (80 est. OBJ tiles <= 192, 5 colours, 1 frame(s)); needs visual QA before use |
| ice | `ice_cube_0.png` | emerald | 64 | 3 | 1 | ice: best decoded emerald candidate by size/frames (64 est. OBJ tiles <= 192, 3 colours, 1 frame(s)); needs visual QA before use |
| ice | `BATTLE_ANIM_OBJ_ICE_BUILDUP` | crystal | 77 | 3 | 4 | ice: best decoded crystal candidate by size/frames (77 est. OBJ tiles <= 192, 3 colours, 4 frame(s)); needs visual QA before use |
| ice | `ice_chunk.png` | emerald | 64 | 10 | 1 | ice: best decoded emerald candidate by size/frames (64 est. OBJ tiles <= 192, 10 colours, 1 frame(s)); needs visual QA before use |
| impact_strike | `explosion_2.png` | emerald | 96 | 6 | 1 | impact_strike: best decoded emerald candidate by size/frames (96 est. OBJ tiles <= 192, 6 colours, 1 frame(s)); needs visual QA before use |
| impact_strike | `BATTLE_ANIM_OBJ_EXPLOSION1` | crystal | 32 | 2 | 3 | impact_strike: best decoded crystal candidate by size/frames (32 est. OBJ tiles <= 192, 2 colours, 3 frame(s)); needs visual QA before use |
| impact_strike | `blue_star.png` | emerald | 96 | 7 | 1 | impact_strike: best decoded emerald candidate by size/frames (96 est. OBJ tiles <= 192, 7 colours, 1 frame(s)); needs visual QA before use |
| poison_acid | `poison_powder.png` | emerald | 16 | 8 | 1 | poison_acid: best decoded emerald candidate by size/frames (16 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |
| poison_acid | `BATTLE_ANIM_OBJ_ACID` | crystal | 4 | 3 | 1 | poison_acid: best decoded crystal candidate by size/frames (4 est. OBJ tiles <= 192, 3 colours, 1 frame(s)); needs visual QA before use |
| poison_acid | `BATTLE_ANIM_OBJ_SLUDGE` | crystal | 3 | 3 | 3 | poison_acid: best decoded crystal candidate by size/frames (3 est. OBJ tiles <= 192, 3 colours, 3 frame(s)); needs visual QA before use |
| psychic_sense | `leer.png` | emerald | 72 | 11 | 1 | psychic_sense: best decoded emerald candidate by size/frames (72 est. OBJ tiles <= 192, 11 colours, 1 frame(s)); needs visual QA before use |
| psychic_sense | `BATTLE_ANIM_OBJ_CONFUSE_RAY` | crystal | 8 | 3 | 2 | psychic_sense: best decoded crystal candidate by size/frames (8 est. OBJ tiles <= 192, 3 colours, 2 frame(s)); needs visual QA before use |
| psychic_sense | `thin_ring.png` | emerald | 64 | 3 | 1 | psychic_sense: best decoded emerald candidate by size/frames (64 est. OBJ tiles <= 192, 3 colours, 1 frame(s)); needs visual QA before use |
| rock_ground | `warm_rock.png` | emerald | 84 | 11 | 1 | rock_ground: best decoded emerald candidate by size/frames (84 est. OBJ tiles <= 192, 11 colours, 1 frame(s)); needs visual QA before use |
| rock_ground | `BATTLE_ANIM_OBJ_SMALL_ROCK` | crystal | 1 | 1 | 1 | rock_ground: best decoded crystal candidate by size/frames (1 est. OBJ tiles <= 192, 1 colours, 1 frame(s)); needs visual QA before use |
| rock_ground | `rocks.png` | emerald | 54 | 10 | 1 | rock_ground: best decoded emerald candidate by size/frames (54 est. OBJ tiles <= 192, 10 colours, 1 frame(s)); needs visual QA before use |
| slash_bite | `fang_attack.png` | emerald | 64 | 6 | 1 | slash_bite: best decoded emerald candidate by size/frames (64 est. OBJ tiles <= 192, 6 colours, 1 frame(s)); needs visual QA before use |
| slash_bite | `BATTLE_ANIM_OBJ_BITE` | crystal | 8 | 1 | 1 | slash_bite: best decoded crystal candidate by size/frames (8 est. OBJ tiles <= 192, 1 colours, 1 frame(s)); needs visual QA before use |
| slash_bite | `claw_slash.png` | emerald | 60 | 8 | 1 | slash_bite: best decoded emerald candidate by size/frames (60 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |
| sound_noise | `noise_line.png` | emerald | 64 | 5 | 1 | sound_noise: best decoded emerald candidate by size/frames (64 est. OBJ tiles <= 192, 5 colours, 1 frame(s)); needs visual QA before use |
| sound_noise | `BATTLE_ANIM_OBJ_BELLY_DRUM_NOTE` | crystal | 4 | 2 | 1 | sound_noise: best decoded crystal candidate by size/frames (4 est. OBJ tiles <= 192, 2 colours, 1 frame(s)); needs visual QA before use |
| sound_noise | `music_notes_2.png` | emerald | 64 | 10 | 1 | sound_noise: best decoded emerald candidate by size/frames (64 est. OBJ tiles <= 192, 10 colours, 1 frame(s)); needs visual QA before use |
| status_buff | `circle_of_light.png` | emerald | 64 | 4 | 1 | status_buff: best decoded emerald candidate by size/frames (64 est. OBJ tiles <= 192, 4 colours, 1 frame(s)); needs visual QA before use |
| status_buff | `BATTLE_ANIM_OBJ_MOONLIGHT` | crystal | 8 | 2 | 2 | status_buff: best decoded crystal candidate by size/frames (8 est. OBJ tiles <= 192, 2 colours, 2 frame(s)); needs visual QA before use |
| status_buff | `green_light_wall.png` | emerald | 48 | 8 | 1 | status_buff: best decoded emerald candidate by size/frames (48 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |
| water | `water_droplet_2.png` | emerald | 80 | 8 | 1 | water: best decoded emerald candidate by size/frames (80 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |
| water | `BATTLE_ANIM_OBJ_BUBBLE` | crystal | 1 | 1 | 1 | water: best decoded crystal candidate by size/frames (1 est. OBJ tiles <= 192, 1 colours, 1 frame(s)); needs visual QA before use |
| water | `bubble_burst_2.png` | emerald | 80 | 11 | 1 | water: best decoded emerald candidate by size/frames (80 est. OBJ tiles <= 192, 11 colours, 1 frame(s)); needs visual QA before use |
| wind_air | `whirlwind.png` | emerald | 38 | 8 | 1 | wind_air: best decoded emerald candidate by size/frames (38 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |
| wind_air | `BATTLE_ANIM_OBJ_SPEED_LINE` | crystal | 8 | 3 | 1 | wind_air: best decoded crystal candidate by size/frames (8 est. OBJ tiles <= 192, 3 colours, 1 frame(s)); needs visual QA before use |
| wind_air | `gust.png` | emerald | 32 | 8 | 1 | wind_air: best decoded emerald candidate by size/frames (32 est. OBJ tiles <= 192, 8 colours, 1 frame(s)); needs visual QA before use |

## Provisional shortlist from anonymous donors (role inferred from dominant hue ONLY)

PMD / HGSS / Ranger / Diamond assets have no names, so these are *hints for a human visual pass*, not classifications. Up to two per library per role, >= 3 frames, 8..192 est. OBJ tiles, <= 15 colours.

| Hinted role | Library | Unit | Frames | Tiles~ | Colours | Hue |
|---|---|---|---:|---:|---:|---|
| electric | pmd_sky | `files/EFFECT/effect.bin#57` | 56 | 180 | 5 | yellow |
| electric | pmd_sky | `files/EFFECT/effect.bin#226` | 12 | 136 | 12 | yellow |
| electric | hgss | `files/a/1/6/7#27` | 25 | 168 | 9 | yellow |
| electric | hgss | `files/a/1/1/3#42` | 11 | 47 | 5 | yellow |
| electric | ranger2 | `res/prebuilt/data/effect/e053_LZ.bin#12` | 6 | 96 | 5 | yellow |
| electric | ranger2 | `res/prebuilt/data/effect/e022_LZ.bin#4` | 6 | 64 | 5 | yellow |
| electric | diamond | `files/data/weather_sys/narc_0001.NCER` | 10 | 31 | 3 | yellow |
| electric | diamond | `files/data/wifip2pmatch/narc_0001.NCER` | 8 | 32 | 3 | yellow |
| fire | pmd_sky | `files/EFFECT/effect.bin#185` | 80 | 150 | 8 | orange |
| fire | pmd_sky | `files/EFFECT/effect.bin#13` | 50 | 184 | 5 | orange |
| fire | hgss | `files/a/0/2/8#5` | 55 | 31 | 9 | red |
| fire | hgss | `files/a/2/2/4#12` | 29 | 146 | 15 | orange |
| fire | ranger2 | `res/prebuilt/data/field/effect/ew008_LZ.bin#4` | 16 | 50 | 6 | orange |
| fire | ranger2 | `res/prebuilt/data/effect/e017_LZ.bin#4` | 8 | 88 | 3 | orange |
| fire | diamond | `files/data/slot/narc_0037.NCER` | 10 | 44 | 2 | orange |
| fire | diamond | `les/wazaeffect/effectclact/wecell/narc_0024.NCER` | 8 | 152 | 5 | red |
| ghost_dark | pmd_sky | `files/EFFECT/effect.bin#81` | 208 | 190 | 1 | black |
| ghost_dark | pmd_sky | `files/EFFECT/effect.bin#37` | 105 | 80 | 1 | black |
| ghost_dark | hgss | `files/a/2/6/3#147` | 12 | 144 | 7 | purple |
| ghost_dark | hgss | `files/a/0/1/4#2` | 10 | 80 | 2 | black |
| ghost_dark | ranger2 | `res/prebuilt/data/effect/e033_LZ.bin#4` | 8 | 82 | 10 | purple |
| ghost_dark | ranger2 | `res/prebuilt/data/effect/e050_LZ.bin#12` | 6 | 96 | 5 | purple |
| ghost_dark | diamond | `files/graphic/nutmixer/narc_0016.NCER` | 16 | 40 | 4 | black |
| ghost_dark | diamond | `files/graphic/pst_gra/narc_0123.NCER` | 10 | 40 | 1 | black |
| grass_nature | pmd_sky | `files/EFFECT/effect.bin#129` | 94 | 46 | 9 | green |
| grass_nature | pmd_sky | `files/EFFECT/effect.bin#1` | 81 | 47 | 7 | green |
| grass_nature | hgss | `files/a/1/9/1#71` | 11 | 88 | 12 | green |
| grass_nature | hgss | `files/data/slot.narc#61` | 10 | 80 | 5 | green |
| grass_nature | ranger2 | `res/prebuilt/data/effect/e014_LZ.bin#4` | 10 | 191 | 14 | green |
| grass_nature | ranger2 | `res/prebuilt/data/effect/e051_LZ.bin#12` | 6 | 96 | 5 | green |
| grass_nature | diamond | `files/data/underg_radar/narc_0005.NCER` | 55 | 46 | 12 | green |
| grass_nature | diamond | `files/data/slot/narc_0029.NCER` | 10 | 44 | 4 | green |
| ice | pmd_sky | `files/EFFECT/effect.bin#173` | 38 | 168 | 5 | cyan |
| ice | pmd_sky | `files/EFFECT/effect.bin#251` | 4 | 64 | 3 | cyan |
| ice | hgss | `files/a/0/4/8#16` | 7 | 70 | 9 | cyan |
| ice | hgss | `files/a/2/3/5#17` | 3 | 36 | 7 | cyan |
| ice | ranger2 | `res/prebuilt/data/effect/e062_LZ.bin#4` | 12 | 120 | 8 | cyan |
| ice | ranger2 | `res/prebuilt/data/effect/e124_LZ.bin#12` | 9 | 157 | 7 | cyan |
| ice | diamond | `files/graphic/bag_gra/narc_0005.NCER` | 4 | 16 | 11 | cyan |
| ice | diamond | `azaeffect/effectdata/waza_particle/narc_0407.bin` | 3 | 36 | 11 | cyan |
| psychic_sense | pmd_sky | `files/EFFECT/effect.bin#69` | 4 | 160 | 10 | pink |
| psychic_sense | hgss | `files/a/1/7/8#12` | 18 | 140 | 14 | pink |
| psychic_sense | hgss | `files/a/1/8/6#21` | 12 | 192 | 14 | pink |
| psychic_sense | ranger2 | `res/prebuilt/data/effect/e116_LZ.bin#4` | 5 | 160 | 14 | pink |
| psychic_sense | ranger2 | `res/prebuilt/data/effect/e104_LZ.bin#8` | 4 | 192 | 10 | pink |
| psychic_sense | diamond | `les/wazaeffect/effectclact/wecell/narc_0005.NCER` | 4 | 66 | 7 | pink |
| rock_ground | pmd_sky | `files/EFFECT/effect.bin#53` | 69 | 110 | 4 | grey |
| rock_ground | pmd_sky | `files/EFFECT/effect.bin#175` | 52 | 160 | 7 | grey |
| rock_ground | hgss | `files/a/0/6/3#23` | 24 | 16 | 3 | grey |
| rock_ground | hgss | `files/a/2/3/5#25` | 20 | 62 | 15 | grey |
| rock_ground | ranger2 | `s/prebuilt/data/field/character/heroine_LZ.bin#4` | 16 | 128 | 15 | grey |
| rock_ground | ranger2 | `res/prebuilt/data/effect/e107_LZ.bin#8` | 5 | 89 | 11 | grey |
| rock_ground | diamond | `les/wazaeffect/effectclact/wecell/narc_0022.NCER` | 10 | 160 | 5 | grey |
| rock_ground | diamond | `les/wazaeffect/effectclact/wecell/narc_0023.NCER` | 10 | 144 | 5 | grey |
| water | pmd_sky | `files/EFFECT/effect.bin#183` | 15 | 30 | 6 | blue |
| water | pmd_sky | `files/EFFECT/effect.bin#98` | 4 | 28 | 3 | blue |
| water | hgss | `files/a/1/9/1#41` | 23 | 186 | 7 | blue |
| water | hgss | `files/a/1/9/7#5` | 16 | 186 | 12 | blue |
| water | ranger2 | `res/prebuilt/data/effect/e054_LZ.bin#4` | 8 | 120 | 5 | blue |
| water | ranger2 | `res/prebuilt/data/effect/e054_LZ.bin#8` | 8 | 112 | 5 | blue |
| water | diamond | `azaeffect/effectdata/waza_particle/narc_0205.bin` | 5 | 54 | 6 | blue |
| water | diamond | `les/wazaeffect/effectclact/wecell/narc_0016.NCER` | 3 | 16 | 8 | blue |

## Anonymous decoded donors awaiting visual role assignment

Counts of in-budget decoded assets whose role cannot be known from a name (hue is a hint, not a classification).

| Library / dominant hue | Count |
|---|---:|
| crystal/black | 3 |
| crystal/blue | 3 |
| crystal/green | 2 |
| crystal/grey | 7 |
| crystal/orange | 1 |
| crystal/red | 4 |
| crystal/yellow | 2 |
| diamond/black | 13 |
| diamond/blue | 11 |
| diamond/cyan | 12 |
| diamond/green | 18 |
| diamond/grey | 36 |
| diamond/orange | 13 |
| diamond/pink | 6 |
| diamond/purple | 5 |
| diamond/red | 19 |
| diamond/white | 101 |
| diamond/yellow | 14 |
| emerald/black | 2 |
| emerald/blue | 13 |
| emerald/cyan | 5 |
| emerald/green | 18 |
| emerald/grey | 3 |
| emerald/orange | 27 |
| emerald/pink | 12 |
| emerald/purple | 6 |
| emerald/red | 17 |
| emerald/white | 10 |
| emerald/yellow | 9 |
| hgss/black | 15 |
| hgss/blue | 22 |
| hgss/cyan | 8 |
| hgss/green | 16 |
| hgss/grey | 99 |
| hgss/orange | 63 |
| hgss/pink | 16 |
| hgss/purple | 9 |
| hgss/red | 55 |
| hgss/white | 19 |
| hgss/yellow | 18 |
| pmd_sky/black | 22 |
| pmd_sky/blue | 6 |
| pmd_sky/cyan | 4 |
| pmd_sky/green | 5 |
| pmd_sky/grey | 6 |
| pmd_sky/orange | 11 |
| pmd_sky/pink | 3 |
| pmd_sky/purple | 3 |
| pmd_sky/red | 3 |
| pmd_sky/white | 2 |
| pmd_sky/yellow | 4 |
| ranger2/black | 4 |
| ranger2/blue | 27 |
| ranger2/cyan | 12 |
| ranger2/green | 11 |
| ranger2/grey | 10 |
| ranger2/orange | 24 |
| ranger2/pink | 8 |
| ranger2/purple | 17 |
| ranger2/red | 10 |
| ranger2/white | 10 |
| ranger2/yellow | 10 |

## Rejection reasons (all libraries)

| Reason | Rows |
|---|---:|
| N estimated OBJ tiles > N budget | 349 |
| N translucent pixels would be dropped (OBJ art is binary alpha) | 302 |
| N colours must be folded to N (lossy) | 78 |

Per-row data (ids, hashes, estimates, rationale) is in `candidate_matrix.json`.
