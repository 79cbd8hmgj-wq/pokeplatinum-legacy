# V02 — HGSS forest texture/material composites: comparison audit

Opportunity: V02 (`OPAL_POST_S2_DONOR_ROADMAP.md`). Result: **comparison complete; one safe first candidate selected (V02-A, stump decals). No game asset was modified.**
Static, offline analysis only. No emulator, runtime or visual testing was performed or is claimed; those stay with the project owner.
Base: `7443b929` (PR #99 merge). Donor source: `pokeheartgold` @ `9d8b7591f09b65804da2fb2dfd56f320633e0d36` (the commit the HGSS field-3D catalog was built from), NARC `files/a/0/4/4` (106 texture sets, 3,659 textures).
Reproduce: `python3 -I tools/visual_overhaul/audit_v02_eterna_materials.py --hgss <pokeheartgold checkout>` (read-only; rewrites only the review PNGs and `v02_eterna_material_audit.json`).

## 1. Baseline facts

| Item | Value |
|---|---|
| Area | `area_data_075` (used only by `MAP_HEADER_ETERNA_FOREST`) → `map_texture_set_074`, `lighting_set_010` |
| Terrain models | `map_matrix_007` → `MAP_338…MAP_346` → `res/field/maps/data/map_data_338…346.bin` (embedded BMD0, 9 models) |
| Texture set | `res/field/maps/texture_sets/map_texture_set_074.nsbtx`, 42,244 B, 57 textures, 59 palette names (56 palette blocks) |
| Lineage | Texel data is **byte-identical** to the shared `map_texture_set_053` (no indexed texel was ever changed). Palettes were graded twice: G4A (14 palettes, `G4A_ETERNA_TEXTURE_RECOLOR_REPORT.md`) and G7.6 (31 palettes, `G7_6_ATMOSPHERE_REPORT.json`). A direct `read_palettes` diff of 074 vs 053 shows **33 changed palette names**, so "14 of 57" understates the current grade: tree canopy, bark/stump, cliff and rock palettes were graded in G7.6. Any donor work must be judged against the *current graded* palettes, not the original 053 ones. |
| Texture use | Only **15 of the 57** textures are bound by the nine Eterna terrain models (below). The other 42 ride along from the 053 clone and are not drawn by Eterna terrain. Props use `prop_texture_set_050`, a different archive, and are out of scope. |

### The 15 textures Eterna terrain actually draws

Pairing is the real material texture↔palette binding read from the models (not name guessing). All are 4bpp/16-colour (`fmt 3`); `c0` = index 0 transparent.

| # | Texture (index) | Size | Palette | c0 | Shapes/tris | Role (UV window evidence) | Donor verdict |
|---|---|---|---|---|---|---|---|
| 1 | `conttree_b` (12) | 64×64 | `conttree_b`* | yes | 9 / 936 | Tiling forest tree-wall: upper band v0–36 slanted canopy (world h 19.5); **lower band v36–62 flat ground decal (h 0)**, two 32-px stump cells | **Stump cells: enhance (V02-A)**; canopy: no |
| 2 | `conttree_t` (13) | 64×64 | `conttree_t` | yes | 9 / 936 | Canopy-only, two slanted bands v4–26 / v32–62 | no |
| 3 | `tree01` (53) | 64×64 | `tree01`* | yes | 7 / 2104 | Four windows: (0,0)-(34,30), (22,28)-(64,64) slanted canopies; **(34,0)-(64,28) flat ground decal (stump)**; window (0,42)-(22,64) samples only transparent texels | **Stump cell: enhance (V02-A)**; canopy: conditional (§3.3) |
| 4 | `criffp` (15) | 32×32 | `criffp` | no | 7 / 1592 | Cliff face: lip v0–4, face v4–26, base v26–32, U tiles ±128 | conditional (§3.2) |
| 5 | `criffp2` (16) | 32×32 | `criff2` | no | 7 / 746 | Cliff face with grass lip: v0–4 / 4–26 | conditional (§3.2) |
| 6 | `criff` (14) | 16×16 | `criff` | no | 5 / 72 | Rock top, whole texture | **recolor of HGSS `gsm_dcliff01`**; no gain |
| 7 | `ngrass` (34) | 16×16 | `grass` | no | 6 / 514 | Underbrush tuft tile | no donor |
| 8 | `nectgr` (32) | 16×16 | `nectgrass` | no | 6 / 256 | Underbrush fern tile | no donor |
| 9 | `fenter` (20) | 32×32 | `fenter` | no | 2 / 8 | Radial floor patch (8 tris) | no donor |
| 10 | `tshadow` (55) | 32×32 | `tshadow` | no | 9 / 470 | Ground shadow disc | recolor family only |
| 11–12 | `nsand` (36) / `nsandp` (37) | 16² / 32² | `sandset` / `nsandp` | yes / no | 3 / 16, 4 / 138 | Sand path tiles | style-incompatible |
| 13 | `beachp` (4) | 32×32 | `beachp` | no | 1 / 12 | Pale path patch | style-incompatible |
| 14 | `rhana` (45) | 16×16 | `rhana` | no | 2 / 8 | Orange flowers on green | no donor |
| 15 | `imped` (25) | 64×64 | `imped` | yes | 2 / 52 | Fence / rock / bush strips | no donor |

\* `conttree_b` and `tree01` are two names for **one shared palette block** (file offset `0xA0F4`, 32 bytes). One palette edit covers both textures, and nothing else in the set references that block.

Images: `docs/visual_overhaul/review/v02_eterna_bound_textures.png` (all 15, current graded state).

## 2. Native vs donor pixel comparison

Method: every one of the 3,659 HGSS textures was decoded with the catalog's own palette binding and compared to the 15 bound textures by (a) byte-identical texel data, (b) bijective-index-relabel identity ("same texels, other palette" = recolor), (c) structure/luminance correlation among same-size textures, and (d) visual side-by-sides at 4–8×.

- **Byte-identical to any HGSS texture:** none of the 15.
- **Same texels, different palette (recolor, no enhancement):** `criff` ≡ `gsm_dcliff01` (HGSS member 85, also 72/75). Nothing to import.
- **Unrelated art of the same kind:** every other bound texture has no sibling in HGSS. The HGSS lookalikes by name (`tshadow`, `imped`, `ngrass`, `lgreen` in member 93, `conttree3_2`, `bf_*` in 92/93) are Battle-Frontier or Platinum-derived copies and mostly recolors; `conttree3_2` (HGSS member 93, a Battle Frontier-style set) shares the *atlas layout* of `conttree_b` but is a tropical frond/stump set whose green-olive palette and silhouette do not fit a graded dark teal forest.
- **HGSS forest analogue:** Ilex Forest's set is member 74 (`d05*`). Its tree art (`d05tree01`, `_re`, `_un`) is in the same dark teal-blue family as Eterna's current graded palette (e.g. ring colors (32,98,106)/(41,115,123) vs Eterna's graded (24,65,82)), so it is the only donor family with compatible mood.
- **Palette:** Platinum 074 is graded; HGSS Johto day art (`tree01_re`, `grass01gs`, `wall01_*`) is bright lime/orange-brown and would need regrading to sit in the scene. Only the `d05*` family needs little or none.

Images: `v02_canopy_compare.png`, `v02_cliff_rock_compare.png`, `v02_ground_underbrush_compare.png`, `v02_stump_decal_candidate.png` (all under `docs/visual_overhaul/review/`; magenta = transparent).

## 3. Strongest three composite opportunities

### 3.1 V02-A — Stump/bark ground decals (conttree_b + tree01) ← HGSS `d05tree01_un`  **(selected; best fit)**

- **Donor:** `hgss:narc:files:a:0:4:4:set_074:tex_019`, `d05tree01_un`, palette `d05tree01_un_pl`, 32×32, `fmt 3`, c0 (also `set_002:tex_032 tree01_un` = same art, brighter palette — do not use).
- **Native:** `conttree_b` rows 36–61 (two identical 32×26 cells; opaque disc 24×22 at cols 4–27/36–59) and `tree01` cell (34,0)-(64,28) (disc 24×22). Both are the same 22-row disc: a green-rimmed teal ring around a cream "sawn top" (palette idx 10–13).
- **Why it matches:** same role (`_un` = under-tree ground disc; both are flat decals, world height 0), same format (4bpp, c0), same ring-on-forest-floor structure, same hue family. The donor swaps the pale sawn stump for a brown trunk base with roots — a genuine bark/material gain, and the brown should sit with lower contrast against the dark canopy floor than the current cream (a judgement for the owner's visual QA).
- **Technical compatibility (verified):** palette slots 1 and 10–13 are used **only** inside the two stump windows (288 px in `conttree_b`, 144 px in `tree01`; 0 px elsewhere); slot 1 is otherwise unused; slots 6/7 are used by `tree01` canopy so the recipe leaves them alone; all indices fit 0–14. See `v02_eterna_material_audit.json` → `slot_ownership`.
- **Cost/risk:** low. Two 64×64 textures, one shared 32-byte palette block, two stump cell windows. Isolated to Eterna (set 074 is referenced only by `area_data_075`).
- **Caveat:** the donor disc is 28 px (vs 24×22), so the decal grows ≈ +38 % in opaque area (800 → 1,192 px across the two `conttree_b` cells) inside the *unchanged* quads. This is a visible change for the owner to judge.

### 3.2 V02-B — Cliff faces (criffp, criffp2) ← HGSS `wall01_d/g/h` strata

- **Native:** very flat — rows 8–19 of `criffp` are twelve identical rows of vertical colour bands; `criffp2` is the same with a grass lip. No vertical detail.
- **Donor:** `set_002:tex_053 wall01_d`, `tex_054 wall01_g`, `set_003:tex_058 wall01_h` (32×32, 13–16 colours, convertible) and the 16×16 cliff-edge `set_074:tex_016 d05pond_line`, `set_029:tex_014 g02pond`. Richer, bumpier face with column shadowing.
- **Blockers:** (a) layout — HGSS `wall01_*` is two stacked 16-row tiers (lip + face repeated, no base); Eterna's windows are lip 0–4 / face 4–26 / base 26–32, so it is a real re-composite, not a drop-in; (b) palette — orange-brown vs Eterna's graded mauve-grey, requiring a quantize-to-existing-palette pass; (c) `criffp2`'s palette is `criff2`, not shared with `criffp`. Requires an art decision on how to build the 22-row face. **Not a safe first PR.**

### 3.3 V02-C — Canopy interior shading (tree01 / conttree_t) ← HGSS `d05tree01(_re)` tiering

- **Native:** flat, 3-tone round blobs 24×22 and 36×32 (`tree01`), 24×23 (`conttree_t`).
- **Donor:** `set_074:tex_017 d05tree01` / `tex_018 d05tree01_re` (64×64, 11 colours): scalloped conifer tiers with a pale apex; same teal-blue mood.
- **Blockers:** the donor's opaque bbox is 42×43 (a pyramid), 1.8× the small blobs; there is no pixel-clean down-scale, and the silhouette changes from rounded cloud to conifer inside a forest where the canopy shows as a wall of repeating tiles. `tree01_re` (set 10) is bright lime; `conttree3_2` is tropical. Viable only as hand-redrawn "shading reference" work, not a mechanical transplant. Highest visual stakes, highest risk; **defer**.

### Rejected for Eterna

Ground/underbrush (`ngrass`, `nectgr`, `fenter`, `rhana`, sand/beach path): no HGSS counterpart with the same role; HGSS `grass01gs`/`grass02_r`/`road01_*`/`egrass`/`flower01` are pastel, flat, different-purpose (path edge, tall-grass overlay, flower decal on transparency) and would clash with G4A/G7.6's already-graded ground. `criff`: identical texels to a donor, recolor only.

## 4. Selected first implementation candidate — V02-A recipe

Scope: **stump decals only**, in `map_texture_set_074.nsbtx`. Changes: texels inside the two stump windows of `conttree_b` and `tree01`, plus palette indices 1, 10, 11, 12 of the shared block at `0xA0F4`. Canopy, transparency outline of every other region, indices of all other textures/palettes, model/material assignments, UV windows and every other texture set stay byte-identical.

**Before-guards (fail closed):** `map_texture_set_074.nsbtx` size 42,244 and sha256 prefix `b8dddf8425a87264`; `conttree_b` texels at file offset `0x2F74` (2,048 B, sha256 prefix `c1c467a1d8496c76`); `tree01` texels at `0x8D34` (2,048 B, `b76ad0cd1a222fe0`); shared palette at `0xA0F4` (32 B, hex `9c73e3240329c220252d87312a3ec835a31c8210113a944e195fe81865219c73`). Re-derive offsets with `nsbmd_preview.parse_tex0` rather than trusting these constants; assert equality, then edit. Also assert: palette indices {1,10–13} are used nowhere outside the two stump windows (the audit script's `slot_ownership` asserts this), and `set_053` unchanged.

**Texel edit (4bpp, low nibble = even pixel):**
1. Read donor member 74 of `files/a/0/4/4` (pin `pokeheartgold` @ `9d8b7591…`), texture `d05tree01_un` (catalog `tex_019`), 32×32 indices.
2. Map donor→Eterna palette index: `0→0, 3→14 (rim), 2→2, 1→3, 4→4, 11→13, 9→1, 10→11, 5→11, 7→12, 8→10, 6→10`. Every donor index 0–11 is covered (asserted).
3. `conttree_b`: blank rows 36–61 (all cols) to index 0; for each cell write the mapped donor rows 3–28 × cols 2–29 (26×28; drops the two 6-px ring caps so it fits the 26-row window) at cols 2–29 and cols 34–61.
4. `tree01`: blank cols 34–63 × rows 0–27 to index 0; write mapped donor rows 2–29 × cols 2–29 (28×28) at cols 35–62, rows 0–27.
5. Index 0 stays the only transparent index; indices 6 and 7 are never written. (Step 3 is mocked in the PNG below; step 4 is derived from the window geometry and not mocked.)

**Palette edit (shared block 0xA0F4, BGR555):** apply the measured G7.6 grade (mean cur/orig over stump entries 10–13 = R 0.877, G 0.872, B 0.94) to the donor browns so they sit in the graded scene: idx1 `0x14A6` (49,41,41), idx10 `0x216E` (115,90,65), idx11 `0x212A` (82,74,65), idx12 `0x214B` (90,82,65). idx13 (`0x18E8`, already ≈ donor outline (65,57,49)) and all other entries stay unchanged. Values are computed by the audit script's `build_mockup`; reuse it.

**Mock-up (illustrative, not applied):** `docs/visual_overhaul/review/v02_stump_decal_candidate.png` (`conttree_b` rebuilt in memory: current vs recipe vs donor).

**Validation for the implementation PR:** guard assertions above; assert byte diff is confined to the two texel windows and the 4 palette entries; decode before/after and confirm every pixel outside the windows is identical; rev0 + rev1 US builds; no change to `map_texture_set_053`; no other file touched. Runtime/visual acceptance is the owner's.

**Owner decision points (do not resolve in the PR):** accept the larger decal footprint (+38 % area) or request a 24-px variant; keep the green rim (`3→14`) or use the donor's lighter teal rim.

## 5. Findings the next PR must not lose

- 074 is graded twice; always diff against the *current* 074, not 053.
- Texture-index order, UV windows and the 15-texture bound list must not change. Bound-texture detection must use the model material pairing, not name heuristics (name heuristics mis-pair `nectgr→nectgrass`, `ngrass→grass`, `nsand→sandset`, `criffp2→criff2`).
- HGSS catalog `palette_name` is missing for some textures (e.g. `set_002 cliff01gs`); the audit falls back to name-matching.
- HGSS decomp provides no source references for these textures (they are packed binary NARC members); provenance is the NARC path + member + catalog asset ID above.

## 6. Status

- Game assets modified: **none**. Files added: this document, `tools/visual_overhaul/audit_v02_eterna_materials.py`, `implementation/v02_eterna_material_audit.json`, five review PNGs, and a roadmap update (V02 row + result section).
- Not performed (owner's responsibility): emulator, runtime and visual acceptance.
