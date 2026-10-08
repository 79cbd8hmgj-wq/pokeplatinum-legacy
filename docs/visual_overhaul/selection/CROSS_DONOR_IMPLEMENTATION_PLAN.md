# Cross-Donor Synthesis + Implementation Design

Status: **DESIGN PROPOSAL / NOT HUMAN-APPROVED / NO PLATINUM ASSET OR SOURCE MODIFIED**
Baseline: `main` @ `ad2b61bb` (post PR #69). Phase: DS-only; donor discovery is closed.
Machine-readable ranking: `IMPLEMENTATION_SLICE_RANKING.json`.
Mockup generator: `tools/visual_overhaul/selection/make_cross_donor_mockups.py` (writes only to `synthesis/`).

Three vertical slices, deliberately using three different donors in three different *use modes*:

| Slice | Track | Donor | Use mode | Host |
|---|---|---|---|---|
| **S1** | A — component enhancement | HGSS | component (shading *treatment*; 0 donor pixels) | Ace Trainer M/F battle front sprites |
| **S2** | B — technique | PMD Sky | technique (palette/tile animation; 0 donor pixels) | Battle terrain palette path |
| **S3** | C — novel capability | Ranger 2 (layout) + Platinum-native | technique (screen composition; 0 donor pixels) | Solaceon *Pokémon News Press* PC |

Diamond stays control/reference. Only HGSS contributes anything resembling "component" value, and even that is
re-expressed on the Platinum silhouette and palette. No donor pixel enters the game in any of the three slices.

---

## Selection method

Ten criteria (visual impact, Sinnoh-identity preservation, novelty, feasibility, reusable infrastructure, applicability
elsewhere, donor dependence, technical risk, authoring burden, runtime-validation burden), scored 1-5 (5 = best/lowest
burden) by hand after reading the evidence. The automated pool score was used only to build the shortlist; library-size
bonuses were ignored. Where the automated score and the decision disagree it is called out below.

### Track A candidates

| Candidate | Imp | Id | Nov | Feas | Reuse | Appl | Dep | Risk | Auth | RT | Total | Verdict |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| **Ace Trainer M/F HGSS shading components** | 3 | 5 | 3 | 5 | 4 | 4 | 4 | 4 | 4 | 5 | **41** | **selected** |
| HGSS building-exterior details (rank 3) | 4 | 3 | 3 | 1 | 4 | 3 | 3 | 1 | 1 | 2 | 25 | no authoring pipeline for NSBMD props (G7.6 records this); highest risk |
| HGSS texture-set regions (ranks 11/12/21) | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 33 | already palette-graded in G4/G7.6; region transplant is a second, riskier pass over the same assets |
| Whole-sprite HGSS trainer swaps (use_hgss verdicts) | 4 | 3 | 1 | 5 | 2 | 3 | 2 | 4 | 5 | 4 | 33 | not a component use; separate, already-reviewed track |

Note: the automated finding scores for the Ace Trainer pair are low (visual_impact 2, reuse 2). That is accepted. The
slice is chosen because (a) the human verdict already ruled the *whole* HGSS Ace Trainers `keep_platinum`, which makes them the
cleanest possible test that the component route preserves Sinnoh identity; (b) the 80x80 front-sprite contract has a working
pipeline today; and (c) the output is a reusable *component-transfer + review gate* for the 73-record
`hgss_front` component library and 15 composite-input candidates.

### Track B candidates

| Candidate | Imp | Id | Nov | Feas | Reuse | Appl | Dep | Risk | Auth | RT | Total | Verdict |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| **PMD palette/tile-cycling → battle terrain palettes** | 3 | 5 | 5 | 4 | 5 | 5 | 5 | 3 | 3 | 3 | **41** | **selected** |
| Ranger multi-phase effect sequencing | 3 | 5 | 2 | 4 | 4 | 3 | 5 | 4 | 4 | 3 | 37 | G5 already applied this approach (selective impact staging); low novelty |
| Ranger interface pulse/entrance states | 4 | 3 | 3 | 4 | 4 | 3 | 5 | 3 | 3 | 3 | 35 | UI is owned/finished by G7; would reopen it |
| PMD GROUND overlay sprites (ranks 20/25/26) | 3 | 4 | 4 | 1 | 4 | 4 | 4 | 2 | 2 | 2 | 30 | no WAN decoder or render evidence yet; evidence-poor |
| Ranger field background movement (rank 28) | 3 | 4 | 3 | 2 | 3 | 3 | 4 | 2 | 2 | 2 | 28 | needs NSBTA/3D material authoring; no pipeline |

### Track C candidates

| Candidate | Imp | Id | Nov | Feas | Reuse | Appl | Dep | Risk | Auth | RT | Total | Verdict |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| **Still-scene newspaper card (Ranger layout; Solaceon News Press)** | 4 | 5 | 5 | 3 | 5 | 4 | 5 | 3 | 4 | 3 | **41** | **selected** |
| Area/location preview card (rank 8) | 5 | 5 | 5 | 2 | 5 | 5 | 3 | 2 | 1 | 2 | 35 | needs a new UI state *and* ≥2-3 new illustrations; collides with map-name popup; second HGSS-derived track. Kept as the natural S4 once S3's card host exists |
| HGSS follower sheets (ranks 2/4/14) | 5 | 3 | 5 | 2 | 4 | 4 | 1 | 2 | 3 | 2 | 31 | whole-asset donor dependence, species-identity risk, overworld OBJ palette pipeline unproven |
| PMD title/BACK still cards (rank 30) | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 30 | style mismatch with Sinnoh; PMD art is reference only |

---

# S1 — Track A: Ace Trainer shading components (HGSS)

| Field | Value |
|---|---|
| Target | `res/trainers/classes/ace_trainer_male/front.png`, `res/trainers/classes/ace_trainer_female/front.png` (80x80, 16 colours, single cell) |
| Opportunity IDs | `opp:trainer/tc_ace_trainer_male/enhancement`, `opp:trainer/tc_ace_trainer_female/enhancement`; records `uc:trainer_battle_sprites/tc_ace_trainer_{male,female}/{01,02}`; libraries `lib:hgss/trainer_sprites/hgss_front/component_donor/component` (#1), `…/enhancement_candidate/composite_input` (#15) |
| Donor | HGSS trainer front sprites `front_024` (male), `front_025` (female), `hgss_trainer_sprites` catalog extension |
| Opportunity class | enhancement_candidate (+ component_donor) |
| Use mode | **component** — treatment only, `pixel_use: derived` |
| Visual concept | Platinum Ace Trainers keep their Sinnoh brown bodysuit, green hair and silhouette; they gain HGSS-grade *depth*: clustered hair highlight bands, jacket/zip/hem definition, fingerless gloves (male) |

**Donor components used (nothing copied)**

| Record | Component | Applied how |
|---|---|---|
| male/01 | 3-tone fold shading, centre-zip highlight, hem seam on torso/sleeves | re-expressed in Platinum brown ramp (idx 7/8/3), on the Platinum silhouette |
| male/02 | fingerless gloves | redrawn on Platinum hand regions with existing dark indices |
| female/01 | clustered hair highlight bands | re-derived with Platinum's own 3 greens (idx 4/5/6), Platinum hair outline kept |
| female/02 | collar / zip seam / hem highlights | translated into the Platinum brown/orange ramp; no HGSS jacket/skirt/boot shape |

**Pixel provenance (the four classes the review needs)**

| Class | Amount |
|---|---|
| Direct donor pixels | **0** |
| Modified donor pixels | **0** |
| Platinum-native pixels retained | the large majority (mockup simulation: 92.5-97.4 % of opaque pixels untouched) |
| Newly authored/derived pixels | small, localised edits (mockup simulation: 2.6 % male, 7.5 % female) |

**What remains Platinum-native:** silhouette, pose, outline, colourway, palette *entries*, hair shape, class identity, cell/animation JSON.
**Newly authored/composited:** shading clusters, seam/zip/hem highlights, gloves.

| Field | Value |
|---|---|
| Technical host format | Platinum trainer-class front PNG → NCGR/NCLR via existing meson rules; 4bpp, index 0 transparent; `front_cell.json`/`front_anim.json` untouched |
| Conversion requirements | none for donor (visual reference only); author on the Platinum indexed PNG with the existing 16-colour row; reuse `tools/visual_overhaul/hgss_trainer_sprite_lib.py` for side-by-side render and `apply_platinum_sprite_pixel_patch.py` for guarded application |
| Implementation path | (1) hand-author edits per record on a copy; (2) generate comparison sheet with direct/modified/native/new pixel classes via the guard script; (3) human review; (4) apply through the guarded patch tool with before-hash guards on the two PNGs; (5) build Rev 0/Rev 1; (6) in-battle visual check |
| Expected visual improvement | clearer fabric/hair form on every Ace Trainer battle intro; closes the "flat two-tone" gap noted for both sprites |
| Reusable infrastructure gained | **component-transfer + review gate**: per-component records that are independently rejectable, a four-class provenance sheet, a guarded pixel-patch workflow; directly reusable for the other 71 `hgss_front` component records and 15 composite inputs |
| Cost | **S** (2 PNGs; ~4 independent component edits) |
| Risk | **low** (no format, palette-budget or animation change) |
| Dependencies | none; existing front-sprite contract |
| Human review | **required**: hand-authored final pixels (1x/4x, in-battle context, M and F), each component accept/reject individually |
| Rollback boundary | restore the two `front.png` files (and nothing else). No source, JSON, script or palette-slot change |

**Evidence:** `synthesis/track_a_ace_trainer_comparison.png` (baseline | HGSS reference | composite | provenance map).

> **Caveat on the mockup.** The composite column is a deterministic procedural simulation on the real Platinum index data, not
> authored art. It demonstrates *footprint and placement* only; the male edit in particular is too small to judge. Quality is
> decided by the hand-authored pass and its human review, not by this image.

---

# S2 — Track B: palette/tile cycling on battle terrain (PMD Sky)

| Field | Value |
|---|---|
| Target | battle terrain palettes/platforms: first `res/graphics/battle/terrain/water/*` (day/evening/night), then `distortion_world`, `cave`, `ice` |
| Opportunity IDs | libraries `lib:pmd_sky/environmental_effects/pmd_mapbg_d/technique_donor/technique` (#18), `…/pmd_mapbg_v/…` (#19); exemplar `opp:mined/field_environment_art/pmd_sky/pmd_mapbg_d01p11a5/technique_donor/technique`; evidence `mining/evidence/pmd_mapbg_bpa.json`, `pmd_mapbg_bpa_d17p33a.png` |
| Donor | PMD Sky `MAP_BG` BPA animated-tile + palette-animation backgrounds |
| Opportunity class | technique_donor |
| Use mode | **technique** — no donor pixels reused |
| Visual concept | static platforms/arenas gain constant, subtle motion: travelling water crests, pulsing Distortion World cracks, cave-crystal glints; the *index ramp* animates, the sprite does not move |

**Donor technique:** a static background carries ramps of palette indices; a per-frame table rotates colours through that ramp (PMD `d17p33a`: static crystal/water art with animated glow and shimmer from BPA tiles + palette animation).
**Exact Platinum host:** `src/battle/terrain.c` — `Terrain_LoadResources()` already loads the terrain palette twice, into `PLTTBUF_MAIN_OBJ` (sprite) and `PLTTBUF_MAIN_BG` slot 7 (`PLTT_DEST(7)`). A new `Terrain_TickPaletteCycle()` runs from the existing terrain object lifecycle (`Terrain_Init`/`Terrain_Destroy`) and writes the cycled ramp into the unfaded palette buffers, the same buffer family the existing `PaletteAnimator` (`src/unk_0201567C.c`, used by battle bag/party fades) already manipulates.
**Intended behaviour:** per-terrain table `{first_index, count, period_frames, mode}`; crest ramp advances every `period` frames; pauses/continues correctly across battle fades and menu overlays (cooperates with `PaletteAnimator` fades); off in reduced-motion/safe mode.

| Field | Value |
|---|---|
| Donor pixels reused | **none** (PMD art is reference only; style differs) |
| New Platinum-native art | one-time re-authoring so crest/crack pixels are *phase-coded* across a small index ramp (existing 16-colour budget; free indices 1-2 on water, more on others). Static frame 0 must equal a valid still of today's platform |
| Scripts/animation systems | `src/battle/terrain.c`; `PaletteData` unfaded buffers; existing `PaletteAnimator` for fade interaction; generator in `tools/visual_overhaul/` (same family as `generate_battle_terrain.py`) emitting the cycled `.pal` + reauthored PNG + a C table |
| Complexity | **medium** (one small task + data table + art re-index; one spike to confirm OBJ/BG slot-7 write path) |
| Reusable infrastructure gained | a **data-driven palette-cycle service** (table + tick) usable on any 4bpp BG/OBJ palette |
| Reuse later | Distortion World / Giratina arenas, cave & ice, league arenas; title/Hall of Fame/Spear Pillar 2D layers; water-side Pokétch/menu BG shimmer; combines with S3 (card state glows) |
| Cost | **M** |
| Risk | **medium-low**: palette-write path not yet proven for the OBJ copy; fade interaction; flicker/photosensitivity (limit per-step contrast, period ≥ 8 frames) |
| Dependencies | none on S1/S3; one runtime spike first |
| Human review | **required**: animated capture at real speed, in-battle, day/evening/night; confirm "subtle, not busy"; photosensitivity check |
| Rollback boundary | remove the one tick call + table; revert the reauthored terrain PNG/PAL (static fallback still renders a valid platform). Other terrains independent |

**Evidence:** `synthesis/track_b_water_platform_palette_cycle.png` and `.gif` (PMD reference strip above eight simulated frames of the Platinum water platform). The simulation recolours crest indices per frame; it is indicative of motion, not final art.

> **Honest scale note:** the platform ellipse is small. Slice impact is *subtle but present in every battle*; the value of S2 is the reusable service, not the single platform.

---

# S3 — Track C: Sinnoh newspaper still-scene card (Ranger 2 layout, Platinum-native art)

| Field | Value |
|---|---|
| Feature | a full-screen, still-scene "card" presentation type — first use: a Pokémon News Press front page |
| Opportunity IDs | `lib:ranger2/transitions_presentation/ranger_event/event/novel_capability/technique` (#13) and `…/technique_donor/technique` (#10); evidence `mining/evidence/ranger_tiled_event.png`, `ranger_tiled_bundles.json` |
| Donor | Ranger 2 `event` bundles (Almia Times newspaper cards, layered event scenes) — composition/state-variant reference only |
| Opportunity class | novel_capability (+ technique_donor) |
| Use mode | **technique** (screen composition, state variants) — no donor pixels |
| Where it appears | Solaceon Town → Pokémon News Press → PC (`SolaceonTownPokemonNewsPress_PC`, `res/field/scripts/scripts_solaceon_town_pokemon_news_press.s`) |
| First test event | interacting with the PC: **today** it shows a top-story message and a text menu (Dusk / Heal / Quick / Dive Ball, Exit) leading to message-only articles; **after** it shows a front-page card with masthead, headline, illustration well and article tabs, then the same four articles over the card |
| Visual concept | Sinnoh press front page in the G7 navy/teal system; Ranger contributes the *structure* (masthead, headline rule, illustration well, column grid, state-selectable tabs) only |

**Platinum host systems:** field script system (`LockAll`/`Message`/`InitGlobalTextMenu` flow stays); `bg_window.c` BG/window + message printing; `graphics.h` NARC loaders; G7 palettes/frame art; item icons (`res/items/icons/{dusk,heal,quick,dive}_ball.png`) as native illustration; optional S2 palette-cycle service for a masthead glint.
**New assets required:** one 256x192 card (NCGR/NSCR/NCLR) built from a generator (masthead + well + column grid + tab states); 4 tab-selection states; optional per-article headline art (reuse item icons first). **Authored art is Platinum-native; Ranger pixels: none.**
**Implementation scope (minimal):** two new script commands `ShowStillCard <id>` / `CloseStillCard` (the second may be implicit), a small card task (fade in → show → input → fade out) using existing BG/window code, one data table of cards, and a two-line edit to the Solaceon PC script. Pastoria-style or other newspaper NPCs are *not* touched. No game-wide rollout.
**Implementation decision to settle at the spike (not a design question):** which BG layer/VRAM bank the card uses while the field is locked; fallback is the sub screen.
**Future expansion:** same card host for story/flashback cards, Team Galactic news, Legendary lore, Hall-style recaps, and the **area-preview card (S4)**; per-article illustration wells; palette-cycle glints via S2.

| Field | Value |
|---|---|
| Cost | **M-L** (new UI state + one new art set) |
| Risk | **medium** (new screen type; VRAM/layer availability in field overlay; text fit) |
| Dependencies | none hard; benefits from S1/S2 review process being established |
| Human review | **required**: art direction (masthead, palette, typography) *before* implementation; then in-engine screenshots on both screens, text fit for all four articles |
| Rollback boundary | revert the 2-line script edit → feature is inert (new commands/resources unused). New files can stay or be removed without touching anything else |

**Evidence:** `synthesis/track_c_news_press_card_mockup.png`.

> **Mockup limits.** Placeholder bitmap font; the illustration well uses real Platinum item icons; real text goes through the
> Platinum text pipeline.

---

## Implementation order

1. **S1 — Ace Trainer shading components.** Lowest risk, working pipeline, gets the component-transfer workflow and review gate proven, and its human review can start immediately. Authoring is the only real cost.
2. **S2 — Terrain palette cycling.** One small spike, then a reusable service. Starts after S1's pixel work is in review.
3. **S3 — News Press card.** Highest novelty and the most unknowns (new screen type); begin *art-direction* review during S1/S2 so engineering starts with an approved look.

Parallelisable: S3 art-direction approval and S1 pixel authoring.

## Human review needed before implementation

| Slice | Review | Gate |
|---|---|---|
| S1 | final hand-authored Ace Trainer M/F sprites (1x/4x, in-battle), per-component accept/reject | before applying the PNG patch |
| S2 | animated capture of the water platform at game speed, day/evening/night; subtle-vs-busy; flicker check | before the generator output is committed |
| S3 | card art direction + layout + typography; then in-engine screenshots and text fit | art direction before engineering; screenshots before merge |

Agent visual review is not approval for any of the above.

## Blockers / donor-discovery reopen

**None.** Every dependency is Platinum-side (palette write path for the OBJ copy, card BG-layer choice). No missing donor evidence blocks any slice. The only evidence gaps (PMD `palette_animation_rendered: false` on some records; PMD WAN decoder absent) belong to alternatives *not* selected.

## Scope guard

No file under `res/` or `src/` was modified. Added: this plan, `IMPLEMENTATION_SLICE_RANKING.json`, `synthesis/*` (mockups + `mockup_stats.json`), and the mockup generator under `tools/visual_overhaul/selection/`.
