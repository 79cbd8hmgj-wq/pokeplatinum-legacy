# DAU2 gap report (revision 2: recipes, HGSS labels, local-only previews)

Base: `main` @ `76bbdbb8` (PR #112 = DAU1, merged). Branch `claude/pokemon-opal-dau2-kjst3j`, PR #113 (draft, not merged). Nothing in P0/P1/P2 is implemented; no gameplay, move data, script or `res/` file is touched.

## Owner decisions applied

1. Galleries stay **local-only** (`build/dau2`, git-ignored). 2. DAU1's donor-image excerpts (`gallery/*_excerpt.png`) are **removed from version control**; local copies kept (`build/dau1_excerpts_local` and in place), `.gitignore` + both `check` gates now refuse tracked images; Git history still contains the old blobs (a history rewrite is a separate, owner-only decision). 3. Native Platinum emitters and new Opal sprite sequences are **combined**. 4. **No donor style is privileged.** 5. Double Team / Hypnosis / Swords Dance are **custom composites**. 6. HGSS cell banks keep being labelled; **unidentified banks are excluded from automatic selection**.

## 1. The 33-move design shortlist (all PROVISIONAL until runtime verified)

`DESIGN_SHORTLIST.md` (one page) and `RECIPES_P1_P2.{md,json}` (full): per move one primary + two alternatives = **99 recipes**, each with launch / travel / impact (/ aftermath / reaction) parts, symbolic timing (`L` = script start, `H` = native hit beat; 60 fps), donor provenance (asset id, archive path, sha256, revision), compatibility (macros, installed sheets, palette variants, decode confidence, runtime-palette dependency, conversion route, contest branch, licence) and static cost estimates.

* **Strategy of the primaries:** 30 `native+opal` (keep the native script's own emitters and add Opal sprite sequences / borrowed Platinum emitters / cues) and 3 `custom_composite` (Double Team, Hypnosis, Swords Dance). Alternatives are a zero-new-tile variant (`opal_existing`) and a bolder or differently-sourced variant.
* **Budgets enforced by the generator (it fails on a violation):** <= 2 concurrent sprite managers, <= 400 concurrent OBJ tiles, <= 40 concurrent OAM, <= 192 tiles per new sheet, FX lifetime <= 180 frames, judged-wrong/illegible donors may not be selected, installed sheets/sequences/palette variants must exist, kept native emitters must be ones the native script really creates. All 99 recipes pass. Cadence (total frames vs the native lower bound, +12 allowed) holds for every primary; 8 alternatives carry an explicit CADENCE / "unverifiable" note.
* **Primary cost envelope (static estimates):** 29 of 33 primaries add a new donor sheet, **1,453 new OBJ tiles in total (~46 KiB of character data)**, max 161 tiles for one move (Leech Seed), max concurrent 312 tiles (Supersonic) and 30 OAM (Double Team), 2 managers at most, <= 283 GX particle quads (Rock Slide), <= 10.5 KB particle texture VRAM (Mud Bomb). 4 primaries add nothing (Flame Wheel, Rock Tomb, Supersonic and Defense Curl's art is borrowed/installed only). Two primaries need a **new palette variant** of an installed sheet (Metal Claw: steel strike; Poison Powder: purple wind) and two new sheets would need a **palette fold** to 15 colours (Mud Bomb, Sleep Powder).
* **Source mix:** native Platinum layer in all 33; new donor cells Emerald 35, Ranger 2 10, PMD Sky 3, Diamond 1; borrowed Platinum emitters in Defense Curl (primary) and in 22 alternatives; 54 installed-sheet parts. Emerald dominates the *small named sprites* because its sprites were the most legible in the review stills; larger shaded or spiral art comes from Ranger 2 / PMD / Diamond where nothing else fit. Rebalancing is a swap of sources, not of choreography.
* **Custom composites (investigation results):**
  * *Double Team*: the native script already spawns real battler-sprite copies (+ `Func_DoubleTeam` sway), so the silhouettes are the battler itself and no donor art can improve them. Recipe: staggered tinted afterimages (`Func_FadeBattlerSprite` on the copies - **unproven**, see blockers), feet dust, ground ellipses, light pulses.
  * *Hypnosis*: PMD `effect.bin#128` is the only true spiral drawing in any pool (needs recolour); combined with converging psychic rings, Emerald `z` glyphs and the native emitters.
  * *Swords Dance*: Emerald `sword.png` is the only blade art; the DS sheet pipeline cannot rotate sprites, so a **baked 12-step orbit animation** is specified from two pixel-exact blade frames (upright/horizontal) plus hflip/vflip.

## 2. Corrections found while reading the native scripts

`native_scripts.py` now reads each `res/moves/<slug>/anim.s`. This **resolved a DAU2 blocker** (which emitters a Platinum move creates): the script says so, with callbacks and lower-bound frames (stored in `B9_P1_P2_BINDING.json`). It also corrected earlier matrix assumptions: Spark loads `discharge.spa` (not `spark.spa`), Leech Seed loads `bullet_seed.spa`, Metal Claw and String Shot are sprite-based (Metal Claw loads no particle archive at all), Double Team loads none, Flame Wheel already carries an installed Ranger 2 donor sprite, and `CreateEmitterEx` takes the emitter index as its third argument (Aqua Jet, Supersonic). The matrix (366 refs / 264 assets) was regenerated; model observations stayed valid by asset id.

## 3. HGSS cell-bank labelling

`HGSS_CELL_BANK_LABELS.json`: 130 containers, 942 banks (513 decoded). **32 containers identified** (244 decoded banks: named containers or source-referenced by named decomp files), **98 unidentified** (269 decoded banks) - these are **excluded from automatic selection**. Auto-eligible categories are only `battle_move_effect` and `field_weather_effect`; today that is exactly 9 banks (`weather_sys.narc`). A source reference proves where a container is used, not what a bank looks like. Labelled: Pokemon graphics 146, PBR interface 24, menu UI 26, minigame 16, underground 13, battle UI 5, demo 3, cut-in 2.
For the rest, `labels` writes a local worksheet per unidentified container (97 sheets in `build/dau2/hgss_labeling`) and an owner override file (`hgss_cell_bank_label_overrides.json`). A model also looked at the first bank of every unidentified container and recorded **advisory** categories (`hgss_cell_bank_model_labels.json`: 69 UI elements, 7 trainer/character sprites, 4 minigame, 4 Pokemon sprites, 3 unclear). **None looks like a move effect**; 3 unclear containers are flagged for an owner look. These advisory labels never grant eligibility.

## 4. Still true from revision 1

Candidate matrix 33/33 READY_FOR_OWNER_REVIEW (366 refs); emitter parser verified on 1,874 archives, three replays/recipes; all decisions `AWAITING_OWNER_REVIEW`; previews local; licensing unverified. See `README.md`, `MOVE_CANDIDATE_MATRIX.md`, `EMITTER_RESEARCH.md`.

## 5. Remaining technical blockers

1. **No runtime verification of anything** (no emulator/hardware here): replays, cadence, OAM/tile peaks and every recipe are static estimates; native task durations (`WaitForAnimTasks`, battler moves, fades) are unknown lower bounds.
2. **Double Team's afterimage tint** assumes `Func_FadeBattlerSprite` accepts `BATTLE_ANIM_MON_SPRITE_n` copies; not provable from source reading.
3. **Swords Dance orbit** needs a new baked-orbit authoring step (animation resource with per-step cell offsets); unproven that the cue system tolerates 4 sprites each with a baked orbit and an anchor on the attacker.
4. **Sheet/resource budget**: 29 new sheets (1,453 tiles) + palette variants grow `anim_n*.narc`; the NARC/sheet-count ceiling and OBJ palette slot pressure with the battle UI were not measured. The tile/OAM caps used are the project's policy caps, not hardware limits.
5. **Palette work not done**: 2 new palette variants, 2 palette folds, PMD#128 recolour; the PMD spiral/other PMD entries must keep `runtime_palette_dependency = none` (21 PMD-based candidate references elsewhere in the matrix are PARTIAL).
6. **Borrowed Platinum emitters** (second particle resource) were assumed to fit a free particle slot and VRAM; 22 alternatives borrow emitters with long lifetimes (flagged) and Signal Beam must be limited to one emitter (all nine would peak at ~1,400 quads).
7. **HGSS**: 72 base-ROM files missing; 98 containers unidentified; 593 cell banks with unresolved palette pairing remain excluded.
8. **Emitter timing/position inside the real battle scene** (camera, callbacks) is still not captured; replays use fixed seeds and a fixed camera.
9. **Licensing** of all donor art is unverified; new sheets must not be committed or released until the owner clears them. Ruby/Sapphire is not mounted in this workspace (identical art to Emerald/FireRed per DAU1).

## 6. Decisions still needed from the owner

1. Approve/reject each primary (and alternatives) in `DESIGN_SHORTLIST.md`; nothing is a visual approval yet.
2. Whether to rebalance the Emerald-heavy small-sprite sourcing toward Ranger 2 / PMD / Diamond at the cost of larger tile budgets.
3. Whether to accept ~1,450 new OBJ tiles / 29 new sheets for the P1/P2 set, or cap per move (the zero-tile `opal_existing` alternative exists for every move).
4. Confirm the three custom composites, in particular the baked-orbit approach for Swords Dance and the afterimage tint for Double Team.
5. Look at the 3 HGSS containers flagged "unclear" and, if wanted, label more containers via `hgss_cell_bank_label_overrides.json`.
6. Licensing/release strategy and whether to rewrite Git history to purge DAU1's old excerpt blobs.

## 7. How you review

```sh
python3 tools/visual_overhaul/dau2_curate.py sheets && python3 tools/visual_overhaul/dau2_curate.py emitters && python3 tools/visual_overhaul/dau2_curate.py package
```
Read `DESIGN_SHORTLIST.md`, then each move's recipe in `RECIPES_P1_P2.md` next to its board in `build/dau2/boards/`. Record decisions in a copy of `OWNER_REVIEW_QUEUE.json`.
