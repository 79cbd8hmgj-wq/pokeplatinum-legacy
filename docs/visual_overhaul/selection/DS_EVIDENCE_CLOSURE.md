# DS high-value evidence closure

Phase `ds_only`. Baseline: `main` be13c4ce (PR #67). No Platinum asset or code was modified; no donor repo was rescanned or recataloged; GBA/GBC findings untouched.
Donor pins (read-only): pokeheartgold `9d8b7591f09b65804da2fb2dfd56f320633e0d36`, pmd-sky `be11cacd78574257bb88116c36dfca8f0839feba`, pokeranger2 `55b4e0cd4598bcbc966f64ad6a10eeab98f813e1`.

## How evidence flows into the pool

1. Targeted decoders (`tools/visual_overhaul/selection/evidence_*.py`, `nsbmd_preview.py`) write measured JSON + small renders to `mining/evidence/`.
2. `resolve_evidence.py` (donor-free) turns that evidence into `mining/EVIDENCE_RESOLUTIONS.json`: family verdicts plus per-group tiers/subtypes measured from the decode.
3. `mine_pool.py` applies resolutions **to the existing records** (same `opportunity_id`s): evidence quality is raised, dimensions are adjusted from measurement, and a group the evidence shows to be weak is closed to `reference_only` (`evidence_closed_*` signal in `mining/passes`). Resolutions apply only to the frozen baseline queue (`mining/EVIDENCE_CLOSURE_SCOPE.json`, 643 records / 559 groups); siblings that were never queued are untouched.
4. HGSS 3D resources and follower sheets are catalog blind spots, so they enter as explicit findings (`opp:hgss/field_building_model_library`, `opp:hgss/map_texture_set_library`, `opp:hgss/follower_sheet_library`, `opp:hgss/land_data_terrain`); `opp:hgss/ui_dex_party_reference` was updated in place.
5. Evidence scripts need `pip install skytemple-files numpy pillow` (pulls ndspy) and the pinned donor checkouts; everything downstream is donor-free. `refresh_all.sh` reruns resolutions, pool, queue, status and validation; `validate_pool.py` checks every baseline record is promoted-with-evidence or explicitly closed.

## Result: 643 baseline needs-evidence records

Resolved 643, remaining 0 (277 promoted with measured evidence, 366 closed to reference_only). Per family:

| Family (source) | Records | Promoted | Closed | Evidence and verdict |
|---|---:|---:|---:|---|
| ranger_poke_w (Ranger) | 163 | 0 | 163 | 295 walk-cycle sets rendered; coherent but ~40px field scale and superseded by the HGSS follower sheets (reference) |
| ranger_poke_a (Ranger) | 96 | 96 | 0 | 596 attack sets rendered (3-157 cells): multi-pose body + attached effect props. Technique only (feasibility 2: no pixels, authoring cost) |
| ranger_poke_s / _t (Ranger) | 89 | 0 | 89 | pose semantics unverified, overlap w/a; no distinct technique |
| ranger_event/event (Ranger) | 129 | 117 | 12 | 76/76 bundles render (tilemap preview): 35 newspaper cards, 29 establishing scenes, 12 mission-board UI; mission_ui novel-capability records closed |
| ranger_ending/edu (Ranger) | 62 | 0 | 62 | 31/31 letterboxed ending vignettes render; redundant with event scene records, below threshold |
| ranger_title/title (Ranger) | 6 | 0 | 6 | separable sky/cloud/mountain/moon layer bands render; below threshold |
| ranger_interface/i (Ranger) | 5 | 3 | 2 | i072_* are 3D effect textures (beam/glow/streak); i024/i059 are static bitmap/tilemap, closed |
| ranger_menu/um (Ranger) | 1 | 1 | 0 | 37 tilemap menu bundles render (frames, banners, rows, mission board); 432-member library, sample-based |
| pmd_mapbg_* animated tiles (PMD Sky) | 85 | 56 | 29 | 72/72 MAP_BG decoded (SkyTemple): 48 rich (water, fire, glow, waves, palette light grade), 16 moderate (8 promoted), 21 trivial (<0.8% animated) closed |
| pmd_ground_p09p01a1 (PMD Sky) | 1 | 1 | 0 | WAN decodes: 12-frame glowing arch/portal rise |
| hgss_mmodel (HGSS) | 4 | 3 | 1 | NPC sheets with 4-direction walk frames |
| hgss_battle_forms egg/shadow (HGSS) | 2 | 0 | 2 | tiny egg/faint shadow; Platinum already has both |

23 more `ranger_event` technique records now exist on groups already in the queue (the same bundles clear the threshold under a second class) - counted as new records, not new groups.

## Priority outcomes

- **A. PMD Sky.** MAP_BG BPA/BPL decode is cheap and reusable (SkyTemple `Bma/Bpc/Bpl/Bpa`; one pip dependency; Pillow incompatibility on its palette-animation render path worked around by falling back to BPA-only frames, flagged per row). BPA tile animation and BPL palette animation are **technique donors** (re-expressed as NSBTA/NSBTP or weather-layer motion), 2D pixels are not reused. 95 further palette-animated backgrounds without BPA exist (`palette_animated_without_bpa`), unqueued. Boundary: WAN decode only for one sample; no broad WAN decoding; `manpu_*`/`effect.bin` status icons stay uncataloged and undecoded (not cheap to locate).
- **B. Ranger 2.** One 150-line tilemap path (existing NSCR/NCGR helpers + NCLR) renders event/ending/title/menu bundles; no general renderer was built. The newspaper card is the standout (editorial/story card layout), scene stills are layout/composition references. Nothing here shows transition *choreography* (static tilemaps): technique tags were corrected to `screen_composition`/`layered_backgrounds`. 158 menu `nbfs` bitmaps and cell-based menu sets remain undecoded (sample-based verdict).
- **C. HGSS field 3D.** The earlier statement that building models are "not present as discrete files" was wrong: they are NARCs inside `fielddata/build_model/` (`bm_field.narc` 340 BMD0, `bm_room.narc` 222 BMD0) and `a/0/4/4` (106 BTX0 map texture sets), `a/0/6/5` (676 land-data blobs). A 350-line BMD0/TEX0 previewer (no skinning/node transforms; shape->material via SBC) rendered all 562 models and decoded all textures: 317/340 outdoor models carry textures Platinum lacks, 129/222 interiors reuse only Platinum textures; 1,847 of 2,100 unique map textures (88%) have no exact Platinum match (62 near-matches). Verdict: **major component/texture pool**, same Gen IV format family, convertible after re-grading; terrain meshes are reference only. Justifies a targeted catalog extension (below).
- **D. HGSS follower sheets.** All 572 decode (538 at 32x32, 34 at 64x64; 8 frames = 4 directions x 2; normal + shiny palette; Platinum ships 43 overworld Pokemon sheets). Usable **without** the follower system as event/cutscene/special-encounter sprites on the existing field-sprite NSBTX path; the system itself stays deferred.
- **E. HGSS party/Pokedex/camera UI.** Party backdrop (Pokeball motif + slot tabs), Pokedex button strips/header grid/cry dial and the 256x16 viewfinder strip were composed (partial NSCR/NCGR pairing; many screens blank). Each has a Platinum equivalent already rebuilt natively in G7: reference_only confirmed, no whole-screen replacement, no promoted component.

## Limits of the evidence

- The BMD0 previewer approximates multi-node models (no node transforms) and pairs palettes by name; counts are exact, individual renders are indicative.
- Ranger tilemap screens render the first screen of each bundle; subtype is a measured colour-coverage heuristic.
- Poke `s`/`t` semantics were not decoded; they were closed on redundancy, not proven useless.
- Evidence is agent visual review, not human approved (`decided_by` says so).

## Recommended catalog extension (before any import)

HGSS targeted extension `hgss_field_3d` (read-only inventory, no import): 562 model groups (bm_field/bm_room) + 106 texture-set groups (3,659 textures, ~1.8k novel by hash) + 572 follower-sheet groups (or 2 family groups) = about 1,240 groups / 5,300 member assets, plus one `land_data` reference family (676 blobs). No other extension is needed.
