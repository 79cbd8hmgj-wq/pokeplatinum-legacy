# G7.6 — Overworld Atmosphere Escalation

Status: **SOURCE-COMPLETE / OWNER RUNTIME REVIEW PENDING**

Baseline: `main` @ `896570704f26` (pinned as `BASE_REV` in the generator).
Builds on the G4/G6 environment work; nothing was restarted from retail assets.

Authority: `tools/visual_overhaul/generate_g76_atmosphere.py` (+ `recolor_g76_atmosphere.c`).
Every texture/lighting/area-data output below is derived from blobs pinned at `BASE_REV`, so a
rerun is byte-identical (verified) and grades never compound.
Machine-readable per-palette result: `G7_6_ATMOSPHERE_REPORT.json`.
Validator: `tools/visual_overhaul/validate_g76_atmosphere.py`.

## Concrete defect found in G4 (fixed, separate commit)

`AreaDataManager_IsOutdoorsLighting()` (`src/overlay005/area_data.c`) decides whether map terrain
uses the global time-of-day light (`AreaLight_UseGlobalModelAttributes`) and which edge-marking
table is used. G4 gave Eterna, the snow region, Spear Pillar and the lakes *new* area-light IDs
(10-13) derived from outdoor sets (004/005/008/000) but never added them to that switch, so those
areas silently fell back to baked model lighting — their dedicated lighting sets did not reach the
terrain. IDs 10-13 and the new outdoor coast IDs are now classified outdoors; cave/interior IDs
(Turnback, Galactic, new cave/Coronet-upper sets) stay indoors. Validator-enforced.

## Technical approach

* Palette-only texture grades (no texel/dimension/name changes) through a data-driven grader
  (`names=`/colour-mask/sat/contrast/luma/shadow+highlight tint rules) applied to **dedicated**
  texture sets only. Magenta key colours are never touched. Turnback's saturated greens (G4F
  suspected key colours) are excluded via a hue-exclusion mask.
* Lighting sets: keyframe times, enable flags and directions are preserved (validator-enforced);
  only colours change. New dedicated sets 015-019 were added where a shared retail set
  (000/001) would otherwise leak; area records are re-pointed (only `lightingSet` changes).
* Fog: constants-only tuning of existing special-fog/weather paths; slopes, offsets and density
  tables unchanged (except Distortion alpha 10→12).
* No geometry, collision, matrices, scripts, events, encounters, camera, weather behaviour or
  renderer changes (`git diff` guard in the validator).

## Per-group record

### 1. Eterna Forest / deep forest
* Areas: `area_data_075` (ETERNA_FOREST only) · `map_texture_set_074` · `lighting_set_010`.
* Visual: canopy palettes darker/cooler with more contrast (greens `lum .80`, blue-shadow lift),
  non-green trunk tones cooled, ground greens −8% luma with cool shadows, rock cooler. Lighting:
  key/diffuse/ambient shifted cool, ambient blue lift by day. `DEEP_FOREST_FOG_COLOR`
  (20,24,22)→(15,21,21): deeper blue-green canopy haze, alpha/offset/scroll unchanged.
  Paths (sand/dirt palettes) deliberately untouched for navigation readability.
* Shared safety: dedicated area/texture slot since G4A; Fullmoon/Newmoon forest (`area_data_054`,
  set 053/lighting 004) untouched.
* Generator: `generate_g76_atmosphere.py` (job `map_texture_set_074`, lighting 010).
* Deferred: tree/prop models are NSBMD (no authoring pipeline); no new emitters.

### 2. Route 217 / Snowpoint / heavy snow
* Areas: `area_data_014` — Snowpoint, Routes 216/217, Lake Acuity + lakefront, Mt. Coronet
  exterior N/S, unknown_243 (one coherent snow family) · `map_texture_set_014` · `lighting_set_011`.
* Visual: three luma bands graded darkest→brightest: dark structure/trees get contrast
  (+12%, cool lift); mid snow shading goes pale-blue; bright whites ×0.93 with a cold tint
  (reduces flat white); vegetation cooled. Water/puddle/smoke palettes skipped. Lighting colder
  (key/diffuse/ambient blue, lower specular). Fog colours colder:
  light (21,26,31)→(19,24,30), heavy (19,24,31)→(16,22,30), blizzard (18,23,31)→(15,20,29).
  Weather behaviour/slopes/offsets untouched.
* Shared safety: the area record is used only by the snow family (audited); no other map uses
  set 014 / lighting 011.
* Deferred: snow particle density changes (weather lifecycle not re-derived).

### 3. Galactic interiors
* Areas: `area_data_058` (Eterna building, HQ, Rotom room; set 057, lighting 006),
  `area_data_068` (lab/control room; set 067), `area_data_077` (Veilstone warehouse; set 076).
  068 and 077 moved from shared `lighting_set_001` to the Galactic set 006.
* Visual: dark structural neutrals −18% luma with contrast and cold shadows; mid/bright neutrals
  cooler; cyan/blue accents (hue 170-230) boosted as the controlled highlight; warm browns
  desaturated/darkened for material hierarchy; glass/key palettes skipped. Lighting 006:
  deeper ambient, cyan-leaning specular. Warehouse (generic interior bank clone) gets a uniform
  cold industrial grade.
* Shared safety: all three texture sets are dedicated; validator asserts consumers.
* Deferred: none.

### 4. Mt. Coronet / Spear Pillar
* Coronet 1F-3F/B1F: `area_data_069` · set 068 · lighting 007 (existing Coronet fog path).
  Coronet 4F-6F: `area_data_070` · set 069 · new `lighting_set_016` (derived from 007; was
  shared retail set 001). Coronet exterior is part of the snow family (group 2).
* Visual: walls darker/cooler with contrast, floors/steps slightly lifted for floor/wall and
  elevation separation, hole/stair depth palettes deeper; upper floors' warm brown cooled hard.
  Coronet fog colour (8,10,14)→(7,9,15).
* Spear Pillar (+ distorted, Hall of Origin, Dialga/Palkia rooms): `area_data_060` · set 059 ·
  lighting 012. Columns/chips/cliff stone: contrast +18%, luma −10%, cool shadows; harder cool
  daylight key with deeper ambient. Fog (16,18,22)/α5 → (13,16,23)/α6. Event staging untouched.
* Deferred: summit sky is a background resource, not a map texture.

### 5. Distortion World
* Areas: `area_data_074` (12 maps incl. Giratina room) · set 073 · lighting 009 · special fog path.
* Visual (strongest treatment): navigable surface palettes get deeper darks (contrast +15%,
  violet/indigo shadows) while their highlights are lifted, so walkable ground separates from
  void/wall palettes (`criff`, `criffP2`, `tree_sbt01` darkened to ×0.78). Lighting pushed
  indigo/violet (key, fill, ambient, specular, emission). Fog (14,8,22)/α10 → (10,5,22)/α12,
  same offset/density table so the near field stays clear.
* Shared safety: dedicated set/area/lighting; lake/water palettes skipped.
* Deferred: prop-model texture bank (`prop_model_set_070` NSBMD-embedded textures) — no safe
  authoring pipeline; floating-platform/gravity effects are script-owned and untouched.

### 6. Lakes and coastal routes
* Lakes: `area_data_062` (Verity, Valor, Sendoff Spring) · set 061 · lighting 013:
  deeper cool freshwater (`sea` ×0.84 red, luma −12%), cool daylight.
* Sunyshore/Routes 223-224/League/Flower Paradise: `area_data_013` · set 013 · new
  `lighting_set_017` (`AREA_LIGHT_SET_COAST_RESORT`): saturated turquoise water, warm sand/sun.
* Canalave/Route 218/islands: `area_data_015` · set 015 · new `lighting_set_018`
  (`..._COAST_HARBOR`): cold steel-blue sea, cooler rock.
* Valor Lakefront/Spring Path/Routes 213, 214, 222: `area_data_018` · set 018 · new
  `lighting_set_019` (`..._LAKESHORE`): restrained teal-green lakeside.
* Each family has its own water grade; ordinary routes (set 000, shared by Jubilife etc.) are
  unchanged. Previously these areas shared retail lighting 000, so new IDs were required and added
  to the outdoors classification.
* Deferred: Verity/Valor/Sendoff share one area record (cannot differ without a new area
  record + header edits, which would touch map headers); Lake Acuity stays with the snow family.

### 7. Caves / Turnback Cave
* Natural caves: Ravaged Path/Wayward/Oreburgh Gate (`053`, set 052), Oreburgh Mine (`055`, set 054),
  Solaceon/Celestic (`056`, set 055), Stark Mountain/Rock Peak (`057`, set 056), Victory Road
  (`071`, set 070) → new `lighting_set_015` (`AREA_LIGHT_SET_CAVE_NATURAL`, from 001, cooler and
  darker). Textures: walls darker/cooler with contrast, floors/steps slightly lifted and
  desaturated (floor/wall boundary), hole/step depth deepened. Entrance, ladder, ledge, water,
  light and impediment palettes left alone for navigation.
* Turnback: `area_data_076` (21 maps) · set 075 · `lighting_set_014`. Lighting darker/colder with
  a violet-tinted fill; walls/floors/depth graded toward cold violet-grey with a hue-exclusion
  mask that leaves the saturated greens untouched. More oppressive than the natural cave grade.
* Shared safety: every cave texture set is dedicated to one area record; the pre-existing shared
  retail lighting 001 is still used by interiors/gyms and is untouched.
* Deferred: Iron Island (lighting 002), Snowpoint Temple, Lost Tower — not in the G7.6 set.

## G7.7 amendment
`lighting_set_012` (Spear Pillar) and `lighting_set_015` (natural caves) were retuned in G7.7 to restore the
visual-intensity hierarchy (caves had out-graded the legendary summit). The values above for those two sets
describe the G7.6 merge state; current authority is `generate_g76_atmosphere.py` / `G7_7_FINAL_COHESION_REPORT.md`.

## Not changed (explicit)
Map geometry, collision, scripts, events, matrices, encounters, camera types, weather behaviour,
renderers and gameplay were not intentionally changed. The validator fails on any change under
`res/field/{maps/data,matrices,scripts,events,encounters,props}` or `include/data/map_headers.h`.

## Validation record
| Check | Result |
|---|---|
| `generate_g76_atmosphere.py` rerun | no diff (second run byte-identical) |
| `validate_g76_atmosphere.py` | PASS — 19 texture sets / 398 palettes palette-only, 13 lighting sets structure-preserving, 11 area records re-pointed |
| `validate_area_light_contract.py` | PASS — 20 members, `AREA_LIGHT_SET_COUNT=20` |
| `validate_g6_showcase_integration.py` | PASS (fog/Galactic contracts updated to the G7.6 values) |
| `validate_g4*` recolor validators | N/A — they diff transient CI dump directories that no longer exist (fail identically on the baseline); superseded by the two validators above |
| `validate_overhaul.py --no-write` | PASS (33/33 children) |
| US Rev 0 build | PASS (`make rom ROM_REVISION=0`) |
| US Rev 1 build | PASS (`make rom ROM_REVISION=1`) |

## Owner runtime checklist (portrait stacked **and** landscape side-by-side)
* **Eterna Forest** — normal navigation; NPC/trainer visibility against canopy; exits and path
  boundaries; day vs night; haze not hiding signs/ledges.
* **Route 217 / Snowpoint** — active snow and blizzard; buildings vs snow; player/NPC vs snow;
  route visibility; Coronet exterior and Lake Acuity use the same grade (check no flat white).
* **Galactic** — HQ halls, doors, consoles, stairs/warps (Eterna building, HQ, lab, Veilstone
  warehouse); battles inside (shared presentation).
* **Coronet / Spear Pillar** — Coronet 1F-3F and 4F-6F traversal (floor vs wall, stairs, ladders);
  summit exterior; Dialga/Palkia/Hall of Origin event visibility.
* **Distortion World** — normal traversal; moving platforms; puzzle surfaces; NPC/event scenes;
  Giratina room; walkable surface vs void contrast.
* **Lakes / coast** — shoreline separation; surfable water; nearby NPCs/objects; compare Verity,
  Valor, Acuity, Sunyshore, Canalave, Valor Lakefront and an ordinary route for distinct identity.
* **Caves / Turnback** — wall/floor separation; entrances/exits; ladders; NPC/object visibility;
  Turnback pillar rooms feel more oppressive than Solaceon/Stark.
* Verify: no accidental palette inheritance between maps; no invisible exits/ledges; no crushed
  shadows; no unreadable snow/water; no fog/weather conflicts; no navigation loss; no
  visual-state leaks between maps; terrain now follows the area light in Eterna/snow/Spear/lakes
  (defect fix) — judge overall brightness there first.
