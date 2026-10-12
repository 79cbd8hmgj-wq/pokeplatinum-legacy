# DAU2 - owner review gallery (index of local previews)

**Nothing in this file is an approval.** Every decision below is `AWAITING_OWNER_REVIEW`. The images are decoded Nintendo artwork and are therefore **not committed**: they are generated into `build/dau2/` (git-ignored) by `python3 tools/visual_overhaul/dau2_curate.py sheets` and can be zipped for review with `python3 tools/visual_overhaul/dau2_curate.py package` (also local). This file maps every preview cell to an immutable asset id; `ASSET_INDEX.json` additionally carries the SHA-256 of each rendered cell's pixels so a regenerated sheet can be verified.

## How to review

1. Generate the previews locally (donor checkouts next to the repository): `sheets`, then `package`.
2. Open `boards/<tier>_<move>.png`. Each row is one *component* of the move (native baseline, launch / travel / impact / aftermath / reaction); candidates run left to right, numbered `#n` (the cell number used below and in `OWNER_REVIEW_QUEUE.json`). Colour of the caption: green = Platinum/DP/HGSS particle with a verified name, blue = named GBA/Crystal sprite, orange = anonymous art ranked by a hue/shape heuristic (a search aid only).
3. SPL particle textures (Platinum / Diamond / HGSS) are **untinted intensity masks**: the in-game colour comes from the emitter's colour/colour-animation (see `emitter/recipes/*.emitter_recipe.json`), so grey/white previews of those are expected.
4. Record accept / reject per cell in a copy of `OWNER_REVIEW_QUEUE.json` (vocabulary `ACCEPT`, `REJECT`, `NEEDS_ANOTHER_LOOK`). Model observations are advisory and made from the rendered boards; they are not decisions.

## Pool contact sheets (indexed; every library, every canonical decoded asset)

| Sheet (local) | Library | Cells | First asset | Last asset |
|---|---|---:|---|---|
| `contact/crystal_p01.png` | crystal | 43 | `tal:data/battle_anims/objects.asm#BATTLE_ANIM_OBJ_ABSORB` | `stal:data/battle_anims/objects.asm#BATTLE_ANIM_OBJ_SWIFT` |
| `contact/diamond_p01.png` | diamond | 100 | `diamond:files/data/field_cutin/narc_0006.NCER` | `amond:files/wazaeffect/effectclact/wecell/narc_0020.NCER` |
| `contact/diamond_p02.png` | diamond | 35 | `amond:files/wazaeffect/effectclact/wecell/narc_0021.NCER` | `d:files/wazaeffect/pt_debug/debug_particle/narc_0001.bin` |
| `contact/emerald_p01.png` | emerald | 100 | `emerald:graphics/battle_anims/sprites/air_slash.png` | `emerald:graphics/battle_anims/sprites/ice_crystals_2.png` |
| `contact/emerald_p02.png` | emerald | 100 | `emerald:graphics/battle_anims/sprites/ice_crystals_3.png` | `emerald:graphics/battle_anims/sprites/slam_hit_2.png` |
| `contact/emerald_p03.png` | emerald | 78 | `emerald:graphics/battle_anims/sprites/slash.png` | `emerald:graphics/battle_anims/sprites/z.png` |
| `contact/hgss_p01.png` | hgss | 100 | `hgss:files/a/0/0/6#12` | `hgss:files/a/0/5/8#252` |
| `contact/hgss_p02.png` | hgss | 100 | `hgss:files/a/0/5/8#257` | `hgss:files/a/0/6/3#19` |
| `contact/hgss_p03.png` | hgss | 100 | `hgss:files/a/0/6/3#23` | `hgss:files/a/1/6/0#8` |
| `contact/hgss_p04.png` | hgss | 100 | `hgss:files/a/1/6/1#2` | `hgss:files/a/2/1/7#12` |
| `contact/hgss_p05.png` | hgss | 63 | `hgss:files/a/2/1/7#16` | `hgss:files/pbr/poketch.narc#5` |
| `contact/platinum_p01.png` | platinum | 100 | `platinum:res/graphics/battle/particles/absorb.spa` | `platinum:res/graphics/battle/particles/encore.spa` |
| `contact/platinum_p02.png` | platinum | 100 | `m:res/graphics/battle/particles/encounter_building_b.spa` | `platinum:res/graphics/battle/particles/lucky_chant.spa` |
| `contact/platinum_p03.png` | platinum | 100 | `platinum:res/graphics/battle/particles/lunar_dance.spa` | `tinum:res/graphics/battle/particles/pokeballs/t_seal.spa` |
| `contact/platinum_p04.png` | platinum | 100 | `res/graphics/battle/particles/pokeballs/twinkle_seal.spa` | `platinum:res/graphics/battle/particles/toxic.spa` |
| `contact/platinum_p05.png` | platinum | 28 | `platinum:res/graphics/battle/particles/toxic_spikes.spa` | `platinum:res/graphics/battle/particles/zen_headbutt.spa` |
| `contact/pmd_sky_p01.png` | pmd_sky | 100 | `pmd_sky:files/EFFECT/effect.bin#1` | `pmd_sky:files/EFFECT/effect.bin#23` |
| `contact/pmd_sky_p02.png` | pmd_sky | 83 | `pmd_sky:files/EFFECT/effect.bin#230` | `pmd_sky:files/EFFECT/effect.bin#99` |
| `contact/ranger2_p01.png` | ranger2 | 100 | `ranger2:res/prebuilt/data/effect/e001_LZ.bin#4` | `ranger2:res/prebuilt/data/effect/e080_LZ.bin#4` |
| `contact/ranger2_p02.png` | ranger2 | 100 | `ranger2:res/prebuilt/data/effect/e081_LZ.bin#4` | `ranger2:res/prebuilt/data/effect/e165_LZ.bin#4` |
| `contact/ranger2_p03.png` | ranger2 | 58 | `ranger2:res/prebuilt/data/effect/e166_LZ.bin#4` | `ranger2:res/prebuilt/data/interface/i072_02.ntft` |

Cell numbers on a pool sheet index into `ASSET_INDEX.json` -> `contact_sheets[<sheet>].cells[n]`.

## Per-move boards

### Headbutt (P1) - `heavy_contact`: shoulder/head impact

Board: `build/dau2/boards/P1_headbutt.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/headbutt.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/eye_sparkle.png` | ILLEGIBLE_OR_TOO_SMALL: thin vertical sparkle strip; frames stacked, hard to judge as a still | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/gold_stars.png` | PLAUSIBLE_ON_SIGHT: gold star cluster reads as dizzy/impact stars | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/dizzy_punch.spa` | NEEDS_CLOSER_LOOK: SPL textures of dizzy_punch: duck + bars are wrong for Headbutt, the white star frame is usable | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#125` | WRONG_ON_SIGHT: black crosses/sparks read as soot, not impact stars | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ew008_LZ.bin#4` | WRONG_ON_SIGHT: tiny red embers, wrong element | AWAITING_OWNER_REVIEW |
| 6 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/horn_hit.png` | PLAUSIBLE_ON_SIGHT: red/yellow directional burst reads as a hard strike | AWAITING_OWNER_REVIEW |
| 7 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/impact.png` | PLAUSIBLE_ON_SIGHT: classic yellow hit star - clearest contact flash on the board | AWAITING_OWNER_REVIEW |
| 8 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/zen_headbutt.spa` | PLAUSIBLE_ON_SIGHT: radial gradient + soft star masks from zen_headbutt: fits a pressure burst (untinted masks) | AWAITING_OWNER_REVIEW |
| 9 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#253` | PLAUSIBLE_ON_SIGHT: cream starburst/explosion frames read as a contact burst | AWAITING_OWNER_REVIEW |
| 10 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ef014_LZ.bin#2` | PLAUSIBLE_ON_SIGHT: ring + fireball burst; ring suits a compressed-impact look, fireball may be too fiery | AWAITING_OWNER_REVIEW |
| 11 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/gray_smoke.png` | ILLEGIBLE_OR_TOO_SMALL: grey puff strip too small to judge | AWAITING_OWNER_REVIEW |
| 12 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/mud_unk.png` | ILLEGIBLE_OR_TOO_SMALL: brown fragments strip, unclear role | AWAITING_OWNER_REVIEW |
| 13 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/zen_headbutt.spa` | PLAUSIBLE_ON_SIGHT: radial gradient + soft star masks from zen_headbutt: fits a pressure burst (untinted masks) | AWAITING_OWNER_REVIEW |
| 14 | launch | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#57` | WRONG_ON_SIGHT: white glow + cone is a beam, not a charge-up | AWAITING_OWNER_REVIEW |
| 15 | launch | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e011_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: yellow sparkles suit aftermath twinkles | AWAITING_OWNER_REVIEW |

### Slam (P1) - `heavy_contact`: heavier contact

Board: `build/dau2/boards/P1_slam.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/slam.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/gray_smoke.png` | ILLEGIBLE_OR_TOO_SMALL: grey puff strip too small | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/mud_unk.png` | ILLEGIBLE_OR_TOO_SMALL: brown fragments strip unclear | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/earthquake.spa` | NEEDS_CLOSER_LOOK: grey boulder from earthquake.spa: debris idea fits slam shake, shape is a rock | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#216` | WRONG_ON_SIGHT: yellow flecks, no weight | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e103_LZ.bin#4` | WRONG_ON_SIGHT: vertical lightning strand | AWAITING_OWNER_REVIEW |
| 6 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/horn_hit.png` | PLAUSIBLE_ON_SIGHT: red/yellow strike burst fits heavy hit | AWAITING_OWNER_REVIEW |
| 7 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/impact.png` | PLAUSIBLE_ON_SIGHT: yellow hit star, fits | AWAITING_OWNER_REVIEW |
| 8 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/body_slam.spa` | PLAUSIBLE_ON_SIGHT: body_slam masks: radial burst + soft puff fit compressed impact | AWAITING_OWNER_REVIEW |
| 9 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#185` | NEEDS_CLOSER_LOOK: thin ring/disc: could be shockwave | AWAITING_OWNER_REVIEW |
| 10 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e053_LZ.bin#12` | WRONG_ON_SIGHT: yellow crescent flames, wrong role | AWAITING_OWNER_REVIEW |

### Wing Attack (P1) - `wing_strike`: wing arcs and pressure

Board: `build/dau2/boards/P1_wing_attack.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/wing_attack.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/impact.png` | PLAUSIBLE_ON_SIGHT: yellow starburst as impact flash | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/horn_hit_2.png` | NEEDS_CLOSER_LOOK: orange dart shape reads as speed marker, not wing pressure | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/slash.spa` | PLAUSIBLE_ON_SIGHT: slash.spa masks: radial + diagonal streak + spire read as cut flashes | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#185` | WRONG_ON_SIGHT: red ring + disc, no relation | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e112_LZ.bin#4` | WRONG_ON_SIGHT: rainbow W glyph | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/air_slash.png` | PLAUSIBLE_ON_SIGHT: white air_slash curls read as wing wind | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/white_feather.png` | PLAUSIBLE_ON_SIGHT: white feathers fit wing strike | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/air_cutter.spa` | PLAUSIBLE_ON_SIGHT: air_cutter crescent masks: clean wing-arc silhouette | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ef010_LZ.bin#2` | NEEDS_CLOSER_LOOK: cyan streak: usable as speed streak | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0020.NCER` | WRONG_ON_SIGHT: small white grub-like shapes | AWAITING_OWNER_REVIEW |

### Aerial Ace (P1) - `speed_contact`: fast double-cut

Board: `build/dau2/boards/P1_aerial_ace.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/aerial_ace.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/claw_slash.png` | PLAUSIBLE_ON_SIGHT: claw_slash small slashes: double-cut reading | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/air_slash.png` | PLAUSIBLE_ON_SIGHT: air_slash curls | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/slash.spa` | PLAUSIBLE_ON_SIGHT: slash masks | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e097_LZ.bin#8` | NEEDS_CLOSER_LOOK: white puff/dust, maybe for dash dust | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#244` | PLAUSIBLE_ON_SIGHT: white horizontal streaks: clean speed-cut lines | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/blue_lines.png` | PLAUSIBLE_ON_SIGHT: blue_lines: sharp cyan slashes | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/speed_dust.png` | NEEDS_CLOSER_LOOK: speed_dust puffs: aftermath dust only | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/air_cutter.spa` | PLAUSIBLE_ON_SIGHT: air_cutter crescents | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#262` | NEEDS_CLOSER_LOOK: cyan arcs tiny | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ef010_LZ.bin#2` | PLAUSIBLE_ON_SIGHT: cyan blade streak, strong 'fast cut' silhouette | AWAITING_OWNER_REVIEW |

### Spark (P1) - `electric_contact`: charging aura into impact

Board: `build/dau2/boards/P1_spark.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/spark.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/impact.png` | PLAUSIBLE_ON_SIGHT: yellow starburst impact | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/horn_hit_2.png` | NEEDS_CLOSER_LOOK: orange dart, speed marker | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/discharge.spa` | PLAUSIBLE_ON_SIGHT: thunder_punch masks: jagged bolt silhouettes | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#253` | PLAUSIBLE_ON_SIGHT: starburst frames | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ef014_LZ.bin#2` | PLAUSIBLE_ON_SIGHT: ring + explosion burst | AWAITING_OWNER_REVIEW |
| 6 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/electricity.png` | ILLEGIBLE_OR_TOO_SMALL: tiny sparks strip, judge in animation | AWAITING_OWNER_REVIEW |
| 7 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/spark_1.png` | PLAUSIBLE_ON_SIGHT: orange zig-zag spark_1 reads as arc | AWAITING_OWNER_REVIEW |
| 8 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/charge.spa` | PLAUSIBLE_ON_SIGHT: charge.spa masks incl. bolts | AWAITING_OWNER_REVIEW |
| 9 | launch | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#57` | NEEDS_CLOSER_LOOK: yellow glow + cone | AWAITING_OWNER_REVIEW |
| 10 | launch | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e011_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: yellow sparkles: crackle accents | AWAITING_OWNER_REVIEW |

### Flame Wheel (P1) - `fire_contact`: flaming roll

Board: `build/dau2/boards/P1_flame_wheel.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/flame_wheel.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/small_ember.png` | PLAUSIBLE_ON_SIGHT: small_ember strip: ember trail | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/fire_plume.png` | PLAUSIBLE_ON_SIGHT: fire_plume strip: ember trail | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/ember.spa` | NEEDS_CLOSER_LOOK: ember.spa masks (flame crescent): untinted | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#53` | WRONG_ON_SIGHT: tiny debris | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e129_LZ.bin#8` | NEEDS_CLOSER_LOOK: orange cinder puffs; may read as explosion | AWAITING_OWNER_REVIEW |
| 6 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/flare_blitz.spa` | PLAUSIBLE_ON_SIGHT: flare_blitz masks: flame crescent + puff, strong roll silhouette | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/red_particles.png` | PLAUSIBLE_ON_SIGHT: red_particles ember dots | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/fire.png` | PLAUSIBLE_ON_SIGHT: fire.png vertical flame column | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0024.NCER` | WRONG_ON_SIGHT: pot-shaped diamond cell objects, unrelated | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#128` | NEEDS_CLOSER_LOOK: red spiral on disc: could suggest rotation but not fire | AWAITING_OWNER_REVIEW |

### Aqua Jet (P1) - `water_contact`: water-wrapped dash

Board: `build/dau2/boards/P1_aqua_jet.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/aqua_jet.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/water_impact.png` | PLAUSIBLE_ON_SIGHT: blue starburst reads as a splash burst | AWAITING_OWNER_REVIEW |
| 2 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/water_pulse.spa` | PLAUSIBLE_ON_SIGHT: water_pulse masks: bubble sphere, droplets, arc - good water set (untinted) | AWAITING_OWNER_REVIEW |
| 3 | impact | named source | crystal | `crystal:data/battle_anims/objects.asm#BATTLE_ANIM_OBJ_BUBBLE` | ILLEGIBLE_OR_TOO_SMALL: Crystal 2bpp object renders as a single black arc (GB palette colour not applied in this still); unusable as shown | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e052_LZ.bin#12` | PLAUSIBLE_ON_SIGHT: blue-white spray fan reads as splash | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#251` | NEEDS_CLOSER_LOOK: flat blue blob; role unclear | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/blue_burst.png` | ILLEGIBLE_OR_TOO_SMALL: tiny blue dots strip | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/mud_sport.spa` | NEEDS_CLOSER_LOOK: mud_sport masks: soft puff, mist-like only | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | crystal | `crystal:data/battle_anims/objects.asm#BATTLE_ANIM_OBJ_BUBBLE` | ILLEGIBLE_OR_TOO_SMALL: Crystal 2bpp object renders as a single black arc (GB palette colour not applied in this still); unusable as shown | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#230` | WRONG_ON_SIGHT: purple dash + red dots, not water | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ef012_LZ.bin#2` | WRONG_ON_SIGHT: white/blue zig-zag looks electric | AWAITING_OWNER_REVIEW |

### BubbleBeam (P1) - `water_bubble`: dense bubbles and burst

Board: `build/dau2/boards/P1_bubble_beam.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/bubble_beam.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/water_impact.png` | PLAUSIBLE_ON_SIGHT: glossy bubble sphere | AWAITING_OWNER_REVIEW |
| 2 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/bubble.spa` | NEEDS_CLOSER_LOOK: starburst as travel element is odd; pop only | AWAITING_OWNER_REVIEW |
| 3 | impact | named source | crystal | `crystal:data/battle_anims/objects.asm#BATTLE_ANIM_OBJ_BUBBLE` | ILLEGIBLE_OR_TOO_SMALL: Crystal 2bpp object renders as a single black arc (GB palette colour not applied in this still); unusable as shown | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e015_LZ.bin#4` | WRONG_ON_SIGHT: dark sphere with red eyes | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#175` | PLAUSIBLE_ON_SIGHT: glow + ring frames read as pop ripple | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/water_impact.png` | PLAUSIBLE_ON_SIGHT: glossy bubble sphere | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/bubble.spa` | NEEDS_CLOSER_LOOK: starburst as travel element is odd; pop only | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | crystal | `crystal:data/battle_anims/objects.asm#BATTLE_ANIM_OBJ_BUBBLE` | ILLEGIBLE_OR_TOO_SMALL: Crystal 2bpp object renders as a single black arc (GB palette colour not applied in this still); unusable as shown | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#183` | PLAUSIBLE_ON_SIGHT: blue ring with dots reads as bubble/ripple | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0016.NCER` | WRONG_ON_SIGHT: reads as Pokeball cells, not bubbles | AWAITING_OWNER_REVIEW |

### Magical Leaf (P1) - `leaf_homing`: curved leafy projectiles

Board: `build/dau2/boards/P1_magical_leaf.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/magical_leaf.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_1.png` | ILLEGIBLE_OR_TOO_SMALL: tiny sparkle strip | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/vine.png` | ILLEGIBLE_OR_TOO_SMALL: tiny vine strip | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/aromatherapy.spa` | NEEDS_CLOSER_LOOK: aromatherapy masks: petal and star usable, rings not | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e026_LZ.bin#4` | NEEDS_CLOSER_LOOK: green slash fans, more blade than leaf | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#150` | NEEDS_CLOSER_LOOK: green gem/blob, not a leaf | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/green_spike.png` | NEEDS_CLOSER_LOOK: green dart; speed marker | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/leaf_blade.spa` | PLAUSIBLE_ON_SIGHT: leaf_blade masks: clear leaf silhouette (untinted) | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/razor_leaf.spa` | PLAUSIBLE_ON_SIGHT: razor_leaf masks: leaf + crescent | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e079_LZ.bin#12` | PLAUSIBLE_ON_SIGHT: shaded leaf art, best leaf silhouette among anonymous sources | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#129` | NEEDS_CLOSER_LOOK: one leaf frame plus unrelated disc | AWAITING_OWNER_REVIEW |

### Metal Claw (P1) - `steel_slash`: metal glint/trailing slash

Board: `build/dau2/boards/P1_metal_claw.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `EMPTY_OR_UNDECODABLE`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_6.png` | PLAUSIBLE_ON_SIGHT: four-point glint reads as a metal sparkle | AWAITING_OWNER_REVIEW |
| 1 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/mirror_shot.spa` | NEEDS_CLOSER_LOOK: mirror_shot ring/arc masks: shine arc only | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/blue_star.png` | ILLEGIBLE_OR_TOO_SMALL: tiny strip | AWAITING_OWNER_REVIEW |
| 3 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e054_LZ.bin#8` | NEEDS_CLOSER_LOOK: blue fan, element-neutral slash | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#164` | WRONG_ON_SIGHT: blue orb | AWAITING_OWNER_REVIEW |
| 5 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/claw_slash.png` | PLAUSIBLE_ON_SIGHT: small claw slashes | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/air_slash.png` | NEEDS_CLOSER_LOOK: air curls, wind rather than metal | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/slash.spa` | PLAUSIBLE_ON_SIGHT: slash masks: streak/spire read as cut + glint | AWAITING_OWNER_REVIEW |
| 8 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#159` | WRONG_ON_SIGHT: green specks and grey streak | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0007.NCER` | WRONG_ON_SIGHT: bone, wrong move | AWAITING_OWNER_REVIEW |

### Rock Tomb (P1) - `rock_fall`: rocks converge

Board: `build/dau2/boards/P1_rock_tomb.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/rock_tomb.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/gray_smoke.png` | ILLEGIBLE_OR_TOO_SMALL: grey puff strip | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/mud_unk.png` | ILLEGIBLE_OR_TOO_SMALL: brown fragments strip | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/rock_slide.spa` | PLAUSIBLE_ON_SIGHT: rock_slide masks: dust puff and boulder | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#213` | WRONG_ON_SIGHT: star + orange flecks | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e103_LZ.bin#12` | WRONG_ON_SIGHT: yellow sparks | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/meteor.png` | WRONG_ON_SIGHT: fiery meteor, wrong material | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/stone_edge.spa` | PLAUSIBLE_ON_SIGHT: stone_edge masks: spikes + boulder; boulder frame fits | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/brown_triangle.png` | NEEDS_CLOSER_LOOK: tiny brown cones, could be pebbles | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0026.NCER` | WRONG_ON_SIGHT: red debris | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#11` | WRONG_ON_SIGHT: bone | AWAITING_OWNER_REVIEW |

### Rock Slide (P1) - `rock_fall`: spread rocks

Board: `build/dau2/boards/P1_rock_slide.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/rock_slide.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/gray_smoke.png` | ILLEGIBLE_OR_TOO_SMALL: grey puff strip | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/mud_unk.png` | ILLEGIBLE_OR_TOO_SMALL: brown fragments strip | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/rock_wrecker.spa` | PLAUSIBLE_ON_SIGHT: rock_wrecker masks: dust puff and boulder | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#125` | WRONG_ON_SIGHT: black crosses/sparks | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e129_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: small brown pebble cluster: debris/aftermath | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/meteor.png` | WRONG_ON_SIGHT: fiery meteor, wrong material | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/stone_edge.spa` | PLAUSIBLE_ON_SIGHT: stone_edge masks: boulder frame | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/brown_triangle.png` | NEEDS_CLOSER_LOOK: tiny brown cones, maybe pebbles | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#135` | NEEDS_CLOSER_LOOK: dark rock with red core and yellow flecks; explosive look | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e044_LZ.bin#4` | WRONG_ON_SIGHT: white crescents, wrong role | AWAITING_OWNER_REVIEW |

### Crunch (P1) - `bite`: powerful closing impact

Board: `build/dau2/boards/P1_crunch.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/crunch.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/bite.spa` | PLAUSIBLE_ON_SIGHT: bite masks (jaw rows) for the closing snap | AWAITING_OWNER_REVIEW |
| 2 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/thunder_fang.spa` | PLAUSIBLE_ON_SIGHT: thunder_fang masks: jaw row | AWAITING_OWNER_REVIEW |
| 3 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/teeth.png` | ILLEGIBLE_OR_TOO_SMALL: tiny white tooth strip | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#51` | NEEDS_CLOSER_LOOK: dark purple pulse and magenta ring; impact accent only | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e023_LZ.bin#4` | WRONG_ON_SIGHT: music notes | AWAITING_OWNER_REVIEW |
| 6 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/bite.spa` | PLAUSIBLE_ON_SIGHT: bite masks (jaw rows) for the closing snap | AWAITING_OWNER_REVIEW |
| 7 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/hyper_fang.spa` | NEEDS_CLOSER_LOOK: hyper_fang masks: white flame/fang shape, partly usable | AWAITING_OWNER_REVIEW |
| 8 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/teeth.png` | ILLEGIBLE_OR_TOO_SMALL: tiny white tooth strip | AWAITING_OWNER_REVIEW |
| 9 | launch | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e020_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: purple fang-like cones, dark-type tint | AWAITING_OWNER_REVIEW |
| 10 | launch | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0014.NCER` | NEEDS_CLOSER_LOOK: single white tusk; static, single-frame | AWAITING_OWNER_REVIEW |

### Ice Shard (P1) - `ice_projectile`: sharp ice pieces

Board: `build/dau2/boards/P1_ice_shard.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/ice_shard.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/hail.png` | PLAUSIBLE_ON_SIGHT: faceted ice gem | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/ice_cube_3.png` | NEEDS_CLOSER_LOOK: pale purple triangle fragment | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/ice_beam.spa` | NEEDS_CLOSER_LOOK: ice_beam masks: spiky flash; impact only | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e054_LZ.bin#12` | NEEDS_CLOSER_LOOK: blue spray fan | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#251` | WRONG_ON_SIGHT: flat blue blob | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/icicle_spear.png` | PLAUSIBLE_ON_SIGHT: blue icicle - clearest 'sharp ice piece' on the board | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/ice_crystals_2.png` | PLAUSIBLE_ON_SIGHT: ice crystal pair | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/icicle_spear.spa` | PLAUSIBLE_ON_SIGHT: icicle_spear masks: spiky burst + ice chunk | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e124_LZ.bin#12` | NEEDS_CLOSER_LOOK: frosty sphere; snowball rather than shard | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#1` | WRONG_ON_SIGHT: blue wrench shape and flame | AWAITING_OWNER_REVIEW |

### Icy Wind (P1) - `ice_wind`: chilling current

Board: `build/dau2/boards/P1_icy_wind.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/icy_wind.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_4.png` | ILLEGIBLE_OR_TOO_SMALL: tiny sparkle strip | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/blue_star.png` | ILLEGIBLE_OR_TOO_SMALL: tiny blue star strip | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/powder_snow.spa` | NEEDS_CLOSER_LOOK: powder_snow masks as travel element: sparkles only | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e091_LZ.bin#4` | NEEDS_CLOSER_LOOK: cyan bubbles with dots | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#256` | PLAUSIBLE_ON_SIGHT: white star sparkle suits frost twinkle | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/ice_crystals_4.png` | PLAUSIBLE_ON_SIGHT: violet-blue crystal column | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/ice_crystals_2.png` | PLAUSIBLE_ON_SIGHT: ice crystals | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/powder_snow.spa` | NEEDS_CLOSER_LOOK: powder_snow masks as travel element: sparkles only | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#230` | WRONG_ON_SIGHT: purple dash with red dots | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ef010_LZ.bin#2` | NEEDS_CLOSER_LOOK: cyan streak could be a wind line; hard blade shape | AWAITING_OWNER_REVIEW |

### Mud Shot (P1) - `mud_projectile`: earth splash

Board: `build/dau2/boards/P1_mud_shot.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/mud_shot.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/flying_dirt.png` | NEEDS_CLOSER_LOOK: debris texture strip (flying dirt); texture-heavy | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/mud_sand_0.png` | PLAUSIBLE_ON_SIGHT: brown droplets | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/mud_slap.spa` | PLAUSIBLE_ON_SIGHT: mud_slap masks: splat | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#50` | WRONG_ON_SIGHT: white horns on brown | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e022_LZ.bin#4` | WRONG_ON_SIGHT: music notes | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/dirt_mound.png` | PLAUSIBLE_ON_SIGHT: brown clods - clear earthen lumps | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/mud_slap.spa` | PLAUSIBLE_ON_SIGHT: mud_slap masks: splat | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/mud_sand_0.png` | PLAUSIBLE_ON_SIGHT: brown droplets | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#197` | NEEDS_CLOSER_LOOK: orange expanding discs; weak mud reading | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e036_LZ.bin#8` | WRONG_ON_SIGHT: flame | AWAITING_OWNER_REVIEW |

### Mud Bomb (P1) - `mud_projectile`: heavy earthen orb

Board: `build/dau2/boards/P1_mud_bomb.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/mud_bomb.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/flying_dirt.png` | NEEDS_CLOSER_LOOK: debris texture strip | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/horn_hit.png` | WRONG_ON_SIGHT: red/yellow fire burst, wrong element | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/mud_slap.spa` | PLAUSIBLE_ON_SIGHT: mud_slap masks: splat | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#169` | NEEDS_CLOSER_LOOK: gold clumps; sandy rather than muddy | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e115_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: brown boulder/clod art - good heavy earthen orb | AWAITING_OWNER_REVIEW |
| 6 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/mud_shot.spa` | PLAUSIBLE_ON_SIGHT: mud_shot masks | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/dirt_mound.png` | PLAUSIBLE_ON_SIGHT: brown clods | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/sludge_bomb.spa` | PLAUSIBLE_ON_SIGHT: sludge_bomb masks: soft blob | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#233` | WRONG_ON_SIGHT: orange knot shapes | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0033.NCER` | WRONG_ON_SIGHT: red lava blob | AWAITING_OWNER_REVIEW |

### Psybeam (P1) - `psychic_beam`: colored psychic pulse

Board: `build/dau2/boards/P1_psybeam.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/psybeam.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/pink_orb.png` | PLAUSIBLE_ON_SIGHT: magenta orb, clear psychic colour | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/movement_waves.png` | ILLEGIBLE_OR_TOO_SMALL: tiny strip | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/psycho_cut.spa` | NEEDS_CLOSER_LOOK: psycho_cut masks: radial + crescent + arc; blade-like, partly usable | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e033_LZ.bin#4` | NEEDS_CLOSER_LOOK: magenta flame; psychic-ish but flame-shaped | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#241` | WRONG_ON_SIGHT: grey hands, wrong subject | AWAITING_OWNER_REVIEW |
| 6 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/signal_beam.spa` | NEEDS_CLOSER_LOOK: signal_beam masks: frame + glow square; beam body, untinted | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/rainbow_rings.png` | ILLEGIBLE_OR_TOO_SMALL: tiny rainbow rings strip | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/movement_waves.png` | ILLEGIBLE_OR_TOO_SMALL: tiny strip | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#69` | PLAUSIBLE_ON_SIGHT: pink/yellow starburst rings: readable pulse impact | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e041_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: purple elliptical rings: clean psychic pulse | AWAITING_OWNER_REVIEW |

### Swift (P1) - `star_volley`: star trails

Board: `build/dau2/boards/P1_swift.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/swift.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_6.png` | PLAUSIBLE_ON_SIGHT: four-point star glint | AWAITING_OWNER_REVIEW |
| 2 | impact | named source | emerald | `emerald:graphics/battle_anims/sprites/yellow_star.png` | PLAUSIBLE_ON_SIGHT: yellow star projectile | AWAITING_OWNER_REVIEW |
| 3 | impact | named move particle | platinum | `platinum:res/graphics/battle/particles/mirror_shot.spa` | NEEDS_CLOSER_LOOK: mirror_shot ring/arc masks | AWAITING_OWNER_REVIEW |
| 4 | impact | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e051_LZ.bin#12` | WRONG_ON_SIGHT: green/white fans | AWAITING_OWNER_REVIEW |
| 5 | impact | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#169` | WRONG_ON_SIGHT: gold clumps | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_6.png` | PLAUSIBLE_ON_SIGHT: four-point star glint | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/yellow_star.png` | PLAUSIBLE_ON_SIGHT: yellow star projectile | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/cosmic_power.spa` | PLAUSIBLE_ON_SIGHT: cosmic_power masks: rings, sparkle, star - usable star trail parts | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e053_LZ.bin#12` | NEEDS_CLOSER_LOOK: yellow comet fans; streak only | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#185` | WRONG_ON_SIGHT: red ring and disc | AWAITING_OWNER_REVIEW |

### Thunder Wave (P2) - `status_electric`: electric bind/brief paralysis

Board: `build/dau2/boards/P2_thunder_wave.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/thunder_wave.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/electricity.png` | ILLEGIBLE_OR_TOO_SMALL: tiny electricity strip | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/spark_1.png` | PLAUSIBLE_ON_SIGHT: yellow zig-zag arc | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/spark.spa` | PLAUSIBLE_ON_SIGHT: spark masks incl. jagged bolt | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#148` | WRONG_ON_SIGHT: log with arrow shards | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e028_LZ.bin#4` | NEEDS_CLOSER_LOOK: white streak and orange dome; unclear | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/electricity.png` | ILLEGIBLE_OR_TOO_SMALL: tiny electricity strip | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/spark_2.png` | PLAUSIBLE_ON_SIGHT: yellow zig-zag arc | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/thunder_shock.spa` | PLAUSIBLE_ON_SIGHT: thunder_shock masks: two jagged bolts | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0035.NCER` | PLAUSIBLE_ON_SIGHT: yellow jagged arcs: reads as lightning | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e017_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: orange zig-zag bolts | AWAITING_OWNER_REVIEW |

### Hypnosis (P2) - `status_sleep`: spiral and drowse

Board: `build/dau2/boards/P2_hypnosis.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/hypnosis.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/z.png` | PLAUSIBLE_ON_SIGHT: blue 'z' glyph for drowsiness | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/thought_bubble.png` | NEEDS_CLOSER_LOOK: thought-bubble dot trail | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/confuse_ray.spa` | NEEDS_CLOSER_LOOK: confuse_ray soft masks only | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e116_LZ.bin#4` | NEEDS_CLOSER_LOOK: pink dotted sphere; unclear | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#256` | NEEDS_CLOSER_LOOK: white sparkle; generic | AWAITING_OWNER_REVIEW |
| 6 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/sing.spa` | PLAUSIBLE_ON_SIGHT: sing masks: concentric rings + note + arc - rings suit a spiral pulse | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/rainbow_rings.png` | ILLEGIBLE_OR_TOO_SMALL: tiny strip | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/movement_waves.png` | ILLEGIBLE_OR_TOO_SMALL: tiny strip | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#166` | WRONG_ON_SIGHT: tiny blade lines | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0008.NCER` | WRONG_ON_SIGHT: purple ghost faces: confusion/curse, not sleep | AWAITING_OWNER_REVIEW |

### Confuse Ray (P2) - `status_confusion`: looping ghost orbs

Board: `build/dau2/boards/P2_confuse_ray.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/confuse_ray.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/metal_sound_waves.png` | NEEDS_CLOSER_LOOK: yellow spiky ring | AWAITING_OWNER_REVIEW |
| 2 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/psybeam.spa` | PLAUSIBLE_ON_SIGHT: psybeam masks: concentric rings + magenta octagon ring: pulse feedback | AWAITING_OWNER_REVIEW |
| 3 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/gold_ring.png` | NEEDS_CLOSER_LOOK: gold ring; loop-able but plain | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#166` | WRONG_ON_SIGHT: tiny blade lines | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0020.NCER` | WRONG_ON_SIGHT: white slugs | AWAITING_OWNER_REVIEW |
| 6 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/shadow_ball.spa` | PLAUSIBLE_ON_SIGHT: shadow_ball masks: soft puff + magenta ring: ghost orb parts | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/will_o_wisp.spa` | NEEDS_CLOSER_LOOK: will_o_wisp soft masks | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/bluegreen_orb.png` | PLAUSIBLE_ON_SIGHT: glowing green/blue orb | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e118_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: dark purple orbs with rim: clean ghost orbs | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#255` | PLAUSIBLE_ON_SIGHT: magenta swirl orbs: looping orb feel | AWAITING_OWNER_REVIEW |

### Poison Powder (P2) - `status_powder`: poison pollen

Board: `build/dau2/boards/P2_poison_powder.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/poison_powder.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/purple_droplet.png` | ILLEGIBLE_OR_TOO_SMALL: tiny droplet strip | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/purple_green_unk.png` | ILLEGIBLE_OR_TOO_SMALL: tiny strip | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/toxic.spa` | NEEDS_CLOSER_LOOK: toxic masks: puff + cyan bubble (untinted masks, bubble hue is the texture's own) | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#266` | PLAUSIBLE_ON_SIGHT: purple/white speck cloud reads as powder | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e084_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: pink dotted cloud reads as powder | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/poison_powder.png` | ILLEGIBLE_OR_TOO_SMALL: tiny magenta dots strip | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/toxic_bubble.png` | ILLEGIBLE_OR_TOO_SMALL: tiny strip | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/bide.spa` | NEEDS_CLOSER_LOOK: bide soft puff | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e012_LZ.bin#4` | NEEDS_CLOSER_LOOK: purple plus-sparkles | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#93` | NEEDS_CLOSER_LOOK: purple/green speck clusters | AWAITING_OWNER_REVIEW |

### Sleep Powder (P2) - `status_powder`: sleep pollen

Board: `build/dau2/boards/P2_sleep_powder.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/sleep_powder.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/z.png` | PLAUSIBLE_ON_SIGHT: blue 'z' for drowsiness | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/snore_z.png` | PLAUSIBLE_ON_SIGHT: lavender snore-Z, clear sleep read | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/snore.spa` | NEEDS_CLOSER_LOOK: snore masks: zig-zag line usable, bubble frame is not | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e054_LZ.bin#16` | NEEDS_CLOSER_LOOK: blue sparkle burst; generic | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#217` | WRONG_ON_SIGHT: pink feather/gem shapes | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/pink_cloud.png` | PLAUSIBLE_ON_SIGHT: soft pink cloud: strongest pollen-cloud read | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/particles.png` | ILLEGIBLE_OR_TOO_SMALL: tiny multi-colour strip | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/sweet_scent.spa` | NEEDS_CLOSER_LOOK: sweet_scent masks: petal/heart, ring and haze; petal could be pollen | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e116_LZ.bin#8` | WRONG_ON_SIGHT: dark sphere with eyes | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#193` | NEEDS_CLOSER_LOOK: pink dot rows and ring; sparkle accents | AWAITING_OWNER_REVIEW |

### Stun Spore (P2) - `status_powder`: stun pollen

Board: `build/dau2/boards/P2_stun_spore.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/stun_spore.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/electricity.png` | ILLEGIBLE_OR_TOO_SMALL: tiny electricity strip | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/spark_1.png` | PLAUSIBLE_ON_SIGHT: yellow zig-zag arc for paralysis feedback | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/thunder_wave.spa` | PLAUSIBLE_ON_SIGHT: thunder_wave masks: ring + bolt | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#189` | WRONG_ON_SIGHT: flame | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e103_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: yellow lightning strands | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/particles.png` | ILLEGIBLE_OR_TOO_SMALL: tiny multi-colour strip | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/spore.png` | PLAUSIBLE_ON_SIGHT: white/tan spore balls read as spore puffs | AWAITING_OWNER_REVIEW |
| 8 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/poison_powder.png` | ILLEGIBLE_OR_TOO_SMALL: tiny magenta dot strip | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#216` | NEEDS_CLOSER_LOOK: yellow flecks | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/field/effect/ew008_LZ.bin#4` | WRONG_ON_SIGHT: red embers | AWAITING_OWNER_REVIEW |

### Swords Dance (P2) - `status_buff`: orbiting blades

Board: `build/dau2/boards/P2_swords_dance.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/swords_dance.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/blue_star.png` | ILLEGIBLE_OR_TOO_SMALL: tiny blue star strip | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_4.png` | ILLEGIBLE_OR_TOO_SMALL: tiny sparkle strip | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/nasty_plot.spa` | WRONG_ON_SIGHT: nasty_plot masks: square, puff, question mark | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e040_LZ.bin#4` | WRONG_ON_SIGHT: cobweb | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#124` | WRONG_ON_SIGHT: fire burst and blue gems | AWAITING_OWNER_REVIEW |
| 6 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/nail.png` | NEEDS_CLOSER_LOOK: row of pink nails; blade-like but not a sword | AWAITING_OWNER_REVIEW |
| 7 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/sword.png` | PLAUSIBLE_ON_SIGHT: blue sword: strongest orbiting-blade read | AWAITING_OWNER_REVIEW |
| 8 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/sharpen.spa` | NEEDS_CLOSER_LOOK: sharpen masks: sphere/cube, plain | AWAITING_OWNER_REVIEW |
| 9 | launch | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#173` | WRONG_ON_SIGHT: blue drops | AWAITING_OWNER_REVIEW |
| 10 | launch | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e097_LZ.bin#8` | WRONG_ON_SIGHT: white puffs | AWAITING_OWNER_REVIEW |

### Defense Curl (P2) - `status_buff`: defensive curl glint

Board: `build/dau2/boards/P2_defense_curl.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/defense_curl.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/eye_sparkle.png` | PLAUSIBLE_ON_SIGHT: gold twinkles for the glint | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_3.png` | PLAUSIBLE_ON_SIGHT: white/cyan glint | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/disable.spa` | PLAUSIBLE_ON_SIGHT: disable masks: clean four-point glint | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#213` | PLAUSIBLE_ON_SIGHT: yellow star sparkle | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e094_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: ring with sparkle | AWAITING_OWNER_REVIEW |
| 6 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/circle_of_light.png` | NEEDS_CLOSER_LOOK: flat white disc; could be a flash | AWAITING_OWNER_REVIEW |
| 7 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/guard_ring.png` | NEEDS_CLOSER_LOOK: thin green ring | AWAITING_OWNER_REVIEW |
| 8 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/withdraw.spa` | PLAUSIBLE_ON_SIGHT: withdraw masks: glossy sphere/ring/shell - fits curl | AWAITING_OWNER_REVIEW |
| 9 | launch | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#108` | WRONG_ON_SIGHT: flame/leaf shapes | AWAITING_OWNER_REVIEW |
| 10 | launch | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0004.NCER` | WRONG_ON_SIGHT: green vine | AWAITING_OWNER_REVIEW |

### Focus Energy (P2) - `status_buff`: focus tightening

Board: `build/dau2/boards/P2_focus_energy.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/focus_energy.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/eye_sparkle.png` | PLAUSIBLE_ON_SIGHT: gold twinkles | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/sparkle_3.png` | PLAUSIBLE_ON_SIGHT: white/cyan glint | AWAITING_OWNER_REVIEW |
| 3 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/power_trick.spa` | NEEDS_CLOSER_LOOK: power_trick masks: zig-zag line, not a tightening | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#242` | NEEDS_CLOSER_LOOK: white comet streaks; could converge | AWAITING_OWNER_REVIEW |
| 5 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e040_LZ.bin#4` | WRONG_ON_SIGHT: cobweb | AWAITING_OWNER_REVIEW |
| 6 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/particles.png` | ILLEGIBLE_OR_TOO_SMALL: tiny multi-colour strip | AWAITING_OWNER_REVIEW |
| 7 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/spotlight.png` | NEEDS_CLOSER_LOOK: red cone; funnel idea, flat | AWAITING_OWNER_REVIEW |
| 8 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/mind_reader.spa` | NEEDS_CLOSER_LOOK: mind_reader masks: bubble/arc | AWAITING_OWNER_REVIEW |
| 9 | launch | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0006.NCER` | PLAUSIBLE_ON_SIGHT: red glaring eyes: intense focus read | AWAITING_OWNER_REVIEW |
| 10 | launch | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#64` | WRONG_ON_SIGHT: orange jagged mouth shapes | AWAITING_OWNER_REVIEW |

### Sand Attack (P2) - `status_debuff`: directed grains

Board: `build/dau2/boards/P2_sand_attack.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/sand_attack.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/gray_smoke.png` | ILLEGIBLE_OR_TOO_SMALL: grey puff strip | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/mud_unk.png` | ILLEGIBLE_OR_TOO_SMALL: brown fragments strip | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/smoke_screen.spa` | PLAUSIBLE_ON_SIGHT: smoke_screen masks: dust puff + ring | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#84` | WRONG_ON_SIGHT: white star with black bits | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e011_LZ.bin#4` | WRONG_ON_SIGHT: yellow sparkles | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/smokescreen_impact.png` | PLAUSIBLE_ON_SIGHT: tan sand grains: clear directed-grain read | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/flying_dirt.png` | NEEDS_CLOSER_LOOK: texture-heavy debris strip | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/sandstorm.spa` | PLAUSIBLE_ON_SIGHT: sandstorm masks: dust puff, dots, haze | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#57` | WRONG_ON_SIGHT: white cone | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0011.NCER` | WRONG_ON_SIGHT: red anger mark | AWAITING_OWNER_REVIEW |

### String Shot (P2) - `status_bind`: thread arc

Board: `build/dau2/boards/P2_string_shot.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/string_shot.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/string.png` | PLAUSIBLE_ON_SIGHT: wavy thread line | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/string_2.png` | PLAUSIBLE_ON_SIGHT: beaded thread strand | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/aurora_beam.spa` | NEEDS_CLOSER_LOOK: bright arc mask | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0020.NCER` | WRONG_ON_SIGHT: white blobs with dots | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e090_LZ.bin#4` | NEEDS_CLOSER_LOOK: white elliptical rings; could be thread loops | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/string_2.png` | PLAUSIBLE_ON_SIGHT: beaded thread strand | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/string.png` | PLAUSIBLE_ON_SIGHT: wavy thread line | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/aurora_beam.spa` | NEEDS_CLOSER_LOOK: bright arc mask | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0005.NCER` | WRONG_ON_SIGHT: pink hooks/spoon shapes | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#244` | NEEDS_CLOSER_LOOK: white streaks; could be thread trails | AWAITING_OWNER_REVIEW |

### Leech Seed (P2) - `seed_bind`: seed impact + vine strands

Board: `build/dau2/boards/P2_leech_seed.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/leech_seed.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/vine.png` | PLAUSIBLE_ON_SIGHT: green vine strip: strand reaction | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/vine_2.png` | PLAUSIBLE_ON_SIGHT: green vine strip | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/vine_whip.spa` | NEEDS_CLOSER_LOOK: vine_whip masks: burst + crescents | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e191_LZ.bin#8` | WRONG_ON_SIGHT: small green bird-like shape | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#161` | NEEDS_CLOSER_LOOK: green ring and dots | AWAITING_OWNER_REVIEW |
| 6 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/seed_2.png` | PLAUSIBLE_ON_SIGHT: green seed - clear Leech Seed projectile | AWAITING_OWNER_REVIEW |
| 7 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/seed_bomb.spa` | NEEDS_CLOSER_LOOK: seed_bomb masks: puffs and metal ball | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/bullet_seed.spa` | NEEDS_CLOSER_LOOK: bullet_seed masks: burst + metallic ball | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0010.NCER` | WRONG_ON_SIGHT: green target icons | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#145` | PLAUSIBLE_ON_SIGHT: green orbs/spheres read as seeds | AWAITING_OWNER_REVIEW |

### Supersonic (P2) - `status_sound`: resonant sound waves

Board: `build/dau2/boards/P2_supersonic.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `DECODED`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | native_baseline | named move particle | platinum | `platinum:res/graphics/battle/particles/supersonic.spa` | - | AWAITING_OWNER_REVIEW |
| 1 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/teal_alert.png` | NEEDS_CLOSER_LOOK: teal comet streak | AWAITING_OWNER_REVIEW |
| 2 | reaction | named source | emerald | `emerald:graphics/battle_anims/sprites/music_notes.png` | ILLEGIBLE_OR_TOO_SMALL: tiny music-note strip | AWAITING_OWNER_REVIEW |
| 3 | reaction | named move particle | platinum | `platinum:res/graphics/battle/particles/sing.spa` | PLAUSIBLE_ON_SIGHT: sing masks: concentric rings + note + arc: strong sound-wave read | AWAITING_OWNER_REVIEW |
| 4 | reaction | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e054_LZ.bin#16` | NEEDS_CLOSER_LOOK: blue sparkle burst | AWAITING_OWNER_REVIEW |
| 5 | reaction | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#99` | WRONG_ON_SIGHT: yellow starburst | AWAITING_OWNER_REVIEW |
| 6 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/metal_sound.spa` | PLAUSIBLE_ON_SIGHT: metal_sound masks: ring + wave arcs | AWAITING_OWNER_REVIEW |
| 7 | travel | named source | emerald | `emerald:graphics/battle_anims/sprites/rainbow_rings.png` | ILLEGIBLE_OR_TOO_SMALL: tiny rainbow-ring strip | AWAITING_OWNER_REVIEW |
| 8 | travel | named move particle | platinum | `platinum:res/graphics/battle/particles/hyper_voice.spa` | PLAUSIBLE_ON_SIGHT: hyper_voice masks: rings + arc | AWAITING_OWNER_REVIEW |
| 9 | travel | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e037_LZ.bin#4` | PLAUSIBLE_ON_SIGHT: cyan bubble rings read as sound rings | AWAITING_OWNER_REVIEW |
| 10 | travel | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#152` | NEEDS_CLOSER_LOOK: blue-green oval ring | AWAITING_OWNER_REVIEW |

### Double Team (P2) - `evasion`: echo silhouettes

Board: `build/dau2/boards/P2_double_team.png` - status `READY_FOR_OWNER_REVIEW`; native Platinum particle: `NO_PLATINUM_PARTICLE_FILE`.

| # | Component | Basis | Library | Asset (immutable id) | Model observation (advisory) | Owner decision |
|---:|---|---|---|---|---|---|
| 0 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/smoke_2.png` | NEEDS_CLOSER_LOOK: grey smoke streaks; not a silhouette | AWAITING_OWNER_REVIEW |
| 1 | aftermath | named source | emerald | `emerald:graphics/battle_anims/sprites/smoke.png` | ILLEGIBLE_OR_TOO_SMALL: tiny smoke chunk | AWAITING_OWNER_REVIEW |
| 2 | aftermath | named move particle | platinum | `platinum:res/graphics/battle/particles/agility.spa` | NEEDS_CLOSER_LOOK: agility soft square; a flat silhouette stand-in at best | AWAITING_OWNER_REVIEW |
| 3 | aftermath | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#266` | WRONG_ON_SIGHT: purple specks | AWAITING_OWNER_REVIEW |
| 4 | aftermath | feature heuristic | ranger2 | `ranger2:res/prebuilt/data/effect/e027_LZ.bin#4` | WRONG_ON_SIGHT: white claw/fan shapes | AWAITING_OWNER_REVIEW |
| 5 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/agility.spa` | NEEDS_CLOSER_LOOK: agility soft square; a flat silhouette stand-in at best | AWAITING_OWNER_REVIEW |
| 6 | launch | named move particle | platinum | `platinum:res/graphics/battle/particles/extreme_speed.spa` | NEEDS_CLOSER_LOOK: extreme_speed soft puff | AWAITING_OWNER_REVIEW |
| 7 | launch | named source | emerald | `emerald:graphics/battle_anims/sprites/white_shadow.png` | NEEDS_CLOSER_LOOK: white ellipse; plain, not an echo silhouette | AWAITING_OWNER_REVIEW |
| 8 | launch | feature heuristic | diamond | `diamond:files/wazaeffect/effectclact/wecell/narc_0019.NCER` | WRONG_ON_SIGHT: purple dots/ghost | AWAITING_OWNER_REVIEW |
| 9 | launch | feature heuristic | pmd_sky | `pmd_sky:files/EFFECT/effect.bin#237` | NEEDS_CLOSER_LOOK: pale ring discs | AWAITING_OWNER_REVIEW |

