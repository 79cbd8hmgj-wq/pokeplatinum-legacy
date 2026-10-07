# hgss_field_3d catalog extension and mining

Baseline: `main` 21b909dd (PR #68). Donor: pokeheartgold `9d8b7591f09b65804da2fb2dfd56f320633e0d36` (read-only). No Platinum asset or source changed; GBA/GBC pool excluded.

## Catalog

| Part | Assets | Groups | Usable | Rejected |
|---|---:|---:|---:|---:|
| Building models (bm_field 340 + bm_room 222) | 562 | 562 | 562 | 0 |
| Map textures (106 BTX0 sets) | 3,659 | 106 | 3,647 | 12 (fully transparent) |
| Follower sheets (566 species/form + 6 party-slot placeholders) | 572 | 572 | 572 | 0 |
| **Total** | **4,793** | **1,240** | 4,781 | 12 |

Curation invariant after the extension: 69,992 catalog assets = 69,992 curated, 0 missing/extra/duplicate/unreviewed, 0 overlap with the base catalog or the other extensions. Candidate groups 8,581 -> 9,821.

Texture use classes (per texture): directly reusable 760, convertible 1,056, component region 1,021, enhancement input (near Platinum variant) 53, reference only 427, identical to Platinum 342. Models: 104 are identical to a Platinum prop (same textures, tris, extents) and 104 share a mesh with an earlier model (palette/texture variants; 458 unique meshes). Followers: all 572 have 8 frames and two palettes; 566 resolve to species/form; 36 have a Platinum sheet but a different frame contract (Platinum 16/2/4 frames), so none is a drop-in.

## Mining result (new groups only)

| Part | Groups | Promoted groups | Reference/reject |
|---|---:|---:|---|
| Models | 562 | 155 (145 component, 41 novel detail) | 303 reference + 104 reject |
| Texture sets | 106 | 67 (65 component library, 9 novel detail, 4 enhancement) | 39 reference |
| Follower sheets | 572 | 530 novel detail | 42 reference (36 Platinum-equivalent, 6 placeholders) | |

794 new mined records: 580 novel_detail, 210 component_donor, 4 enhancement_candidate; 0 technique, 0 replacement, 0 needs-evidence. Whole-asset replacement: none - models convert structurally (no preferred donor), followers are contract mismatches, texture sets have no Platinum counterpart as a unit. Models yield no enhancement: of 50 models matched to a Platinum prop by texture overlap, none has richer geometry.
Pool: 2,280 -> 3,205 records, libraries 47 -> 84, queue ranked items 57 -> 94.

## Method notes

- Dedicated rules (`mine_x3d.py`): theme families from measured categories (name-token vocabulary + geometry class) so libraries are meaningful (`hgss_bm_field_building_exterior`, `hgss_texset_foliage_ground`, `hgss_follower_legendary`...).
- Follower rules count each sheet as an independent whole-asset novel detail but cap library/reuse at 3/4 and score feasibility 2 (no host event exists yet); the follower system is not proposed.
- Targeted review: montages for the five highest-value families under `mining/review/field_3d_*.png`; 88 groups carry `confirm` reviews (evidence floor 4).
