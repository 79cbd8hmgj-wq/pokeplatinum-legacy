# DAU2 gap report

Base: `main` @ `76bbdbb8` (PR #112 = DAU1 **merged**; so this is a normal PR onto `main`, not stacked on an open branch). Branch `claude/pokemon-opal-dau2-kjst3j`. Nothing merged, nothing in P0/P1/P2 implemented.

## 1. B9 manifest recovered and bound (Phase A)

* Original manifest imported unchanged; SHA-256 `419c17818fbdabf20bf65b729ef40bd123c09899398c75fdb0258a8c8561be37` verified before copy and re-verified by `check`. **19 P1 + 14 P2** names match the manifest exactly (also 19 P0 / 52 total).
* All 33 resolve to an existing `res/moves/<slug>/anim.s` (script hashes recorded; `check` fails if one changes, i.e. it guards "P1/P2 not implemented"). Discrepancies recorded in `B9_P1_P2_BINDING.json`:
  * `ThunderShock` (P0) and `BubbleBeam` (P1) are directories `thunder_shock` / `bubble_beam` - explicit aliases.
  * Seven P1/P2 moves already hold a **design-only** B2-B8 archetype assignment (`aerial_ace`, `magical_leaf`, `rock_slide`, `psybeam`, `thunder_wave`, `hypnosis`, `confuse_ray`); none has an Opal cue-trace baseline entry, so none is implemented - audit before replacing.
  * Every manifest entry's `source_animation` is the placeholder `locate_in_pr110_head`; resolved here to the repository scripts above.
  * The 19 P0 names equal the P0 set already on `main`; the recovered `P1_P2_MOVE_INDEX.md` agrees with the manifest for all 33.

## 2. Cross-source candidate matrix (Phase A/B)

| | |
|---|---|
| Moves with a matrix | **33 / 33** (P1 19, P2 14) |
| Candidate references / distinct assets | **366 / 263** (named Platinum-family particle 105, named GBA/Crystal 127, heuristic 134) |
| By source family | nds_spl 122 (Platinum 105, Diamond 17), gba 123, pmd_sky 63, ranger2 54, crystal 4 |
| Moves whose candidates span >= 3 source families | 33 / 33 |
| Status | 33 `READY_FOR_OWNER_REVIEW` (>= 3 distinct *name-backed* renderings and >= 3 families), 0 `INSUFFICIENT_VERIFIED_CANDIDATES` |
| Pool searched | 1,788 canonical decoded renderings (1,978 cross-library duplicates collapsed: Emerald = FireRed = Ruby art, Platinum = Diamond = HGSS textures) |
| Native same-move Platinum particle | present for 31 moves; **Metal Claw**: the Platinum `.spa` is an empty archive (0 emitters, 0 textures); **Double Team**: no Platinum particle file at all |
| Candidates with runtime-palette caveat | 21 (PMD effect entries with unresolved palette rows) |

Components (native baseline / launch / travel / impact / aftermath / reaction) are filled independently, so different pools can supply different components of one move. "READY" only means enough distinct, source-backed candidates exist **to look at**; it says nothing about visual fit.

Model observations (advisory, from the rendered boards, 334 cells): 120 plausible on sight, 87 need a closer look, 70 wrong on sight, 40 too small/fragmentary to judge as stills (sprite strips need animation context). Weakest boards: **Double Team** (no convincing silhouette/echo art; needs procedural/custom afterimage), **Swords Dance** (one clear blade: Emerald `sword.png`), **Hypnosis** (rings from `sing.spa`, no true spiral art), **Poison Powder**, **Rock Tomb**, **String Shot**.

### Sources searched in one coordinated index (and what was unavailable)

| Pool | Searched | Pin | Notes |
|---|---|---|---|
| Platinum (this repo, `res/graphics/battle/particles`) | yes - 602 SPL archives, 568 decoded | repo `main` @ `76bbdbb8` | 485 move particles named by move; exact baseline |
| Diamond/Pearl (`pokediamond`) | yes - 614 SPL, 688 decoded units incl. `wazaeffect` cell banks | `5bc4b1a3d8` | names via texture-verified list alignment |
| HeartGold/SoulSilver (`pokeheartgold`) | yes - 645 SPL (+ cell banks decoded but not heuristic-searched) | `9d8b7591f0` | 72 base-ROM files MISSING |
| Emerald / FireRed (`pokeemerald`, `pokefirered`) | yes - 279 sprites each (identical art, collapsed) | `a81cfacbe5` / `037335f4c7` | named |
| Crystal (`pokecrystal`) | yes - 64 reconstructed objects | `3bc8daa417` | 4 matched; renders as black 2bpp arcs in stills |
| PMD Sky (`pmd-sky`) | yes - 184 effect entries (heuristic) | `be11cacd78` | 82 need run-time palettes |
| Ranger 2 (`pokeranger2`) | yes - 294 cell banks / 8 textures (effect packages only) | `55b4e0cd45` | heuristic |
| Ruby/Sapphire (`pokeruby`) | **not mounted in this workspace** | DAU1 pin `5784633ce4` | art identical to Emerald/FireRed per DAU1 |
| Pokemon Yellow | searched, nothing usable (layout tables not reconstructed in DAU1) | `e89ead154b` | |

## 3. Visual curation artefacts (Phase B)

* `sheets` renders, from real decoded frames: **33 per-move side-by-side boards** and **21 indexed pool contact sheets covering all 1,788 canonical assets** (Platinum, Diamond, HGSS, Emerald/FireRed/Ruby, Crystal, PMD Sky, Ranger 2). Every cell is index-numbered; `ASSET_INDEX.json` maps each (sheet, cell) to its immutable asset id with the SHA-256 of the cell's pixels.
* Previews are local only (`build/dau2`, ~3.6 MB, git-ignored; `package` zips them for attaching). **No image is committed by DAU2.** (DAU1's committed ~325 KB `gallery/*_excerpt.png` are untouched - see decision 1.)

## 4. SPL emitter motion (Phase C)

* Parser verified on **1,874 archives** (HGSS 645, Diamond 614, Platinum 615; 5,519 emitters): every archive tiles exactly, every cross-reference resolves, no divisor field is 0, value distributions match `lib/spl` semantics (see `EMITTER_RESEARCH.md`). DAU1 texture decoding is unchanged (its tests + catalog hashes re-verified).
* Coverage (HGSS / Diamond): `DECODED_TEXTURE_ONLY` baseline 611 / 580; `EMITTER_FIELDS_VERIFIED` **645 / 614**; `EMITTER_PREVIEW_VERIFIED` 3 / 3; `CANDIDATE_REVIEWED` 0 / 0; `BLOCKED_SOURCE` 72 / 0.
* Replays of **Headbutt (contact), Flame Wheel (element), Sleep Powder (status)** in all three games, with documented assumptions, invariants (spawn schedule re-derived from the header, ages within life, determinism, DS quad limit), static GX counts and OBJ-flatten estimates; three `emitter_recipe.json` exported. Emitter records are identical across Platinum / Diamond / HGSS for all three.
* **"Verified" here = consistent with a port of Platinum's own `lib/spl`, not compared with a runtime capture.**

## 5. Exact blockers

1. **No runtime capture.** No emulator/hardware here, so replays are unvalidated against real frames; positions depend on an unknown RNG seed.
2. **Which emitters a move creates, when and where** lives in battle scripts/particle-index tables that are not decoded; without it a recipe cannot be mapped to an Opal macro unambiguously.
3. **Emitter callbacks / battle camera / draw types** (polygon, directional, view-space), fixed-point sin tables: not modelled (listed under "Unknown" in each recipe).
4. **HGSS**: 72 base-ROM files MISSING; HGSS cell banks are anonymous with 593 unresolved palette pairings, so they are **excluded** from the heuristic search; 65 of 485 HGSS and 57 of 485 Diamond move-particle entries have unverified (position-only) name alignment and carry no name-based role.
5. **PMD Sky**: 82 effect entries need run-time palette banks (21 candidate references carry this caveat).
6. 34 SPL archives per game have blank or 4x4-compressed textures (format 5 not decoded).
7. **Ruby/Sapphire** checkout is not mounted in this workspace (DAU1 had it; its art is byte-identical to Emerald/FireRed), so a fresh `features` run here omits it; the committed DAU1 catalog still lists it.
8. **Licensing** of all donor art is unverified; the decomp licences do not grant rights over original game artwork.
9. Platinum `metal_claw.spa` is empty and Double Team has no particle file (see section 2).

## 6. Visual decisions requiring your approval

1. **Release/licensing strategy**: keep DAU2 preview-only (local) as built; and decide whether DAU1's committed `*_excerpt.png` stay or are removed.
2. **Per-move selection (33 boards)**: for each move/component accept/reject cells in `OWNER_REVIEW_QUEUE.json`. Do not treat the advisory observations as decisions.
3. **Baseline policy**: Platinum already ships a native `.spa` (with real emitter motion) for 31 of the 33 moves. Decide per move whether P1/P2 should **reuse/retint the native emitter** or build new Opal FX-sheet sequences from the donor art, and whether the SPL-derived looks (colour comes from the emitter) are acceptable next to flattened OBJ sprites.
4. **Style match**: Emerald/FireRed sprites (15 colours) vs Ranger/PMD art vs Platinum's soft 3D masks - pick the target look (e.g. prefer Platinum/Emerald parts; allow Ranger/PMD only where clearly better such as the shaded leaves `ranger2:e079` for Magical Leaf).
5. **No-good-candidate moves**: Double Team (custom/procedural afterimage?), Hypnosis (spiral), Swords Dance (orbit of one blade), Poison Powder / Rock Tomb / String Shot.
6. **Heuristic scope**: confirm HGSS anonymous cell banks stay out of the search until a human labels the effect-vs-UI containers.

## 7. How you review

```sh
python3 tools/visual_overhaul/dau2_curate.py sheets && python3 tools/visual_overhaul/dau2_curate.py emitters && python3 tools/visual_overhaul/dau2_curate.py package
```
Open `build/dau2/boards/<P1|P2>_<move>.png` (cell `#n` = the number in `OWNER_REVIEW_GALLERY.md` / `OWNER_REVIEW_QUEUE.json`), the pool sheets in `build/dau2/contact/`, and `build/dau2/emitter/*_timeline.png` / `*.gif`. Record decisions in a copy of `OWNER_REVIEW_QUEUE.json`.
