# Lane A Semantic Review Plan

Compact semantic grouping for final Lane A curation. This file does not
change donor review statuses or modify Platinum resources.

## Coverage

- Unified catalog assets: **64841**
- Review queue assets: **64841**
- Lane A unique candidates: **21496**
- P1 Ranger candidates: **18331**
- P3 native HGSS/Diamond PNG candidates: **3165**
- P3 semantic groups: **7**

### P1 technical status

| Status | Candidates |
|---|---:|
| decode_issue | 19 |
| valid_render | 18312 |

## P3 semantic groups

| # | Source | Group | Tags | Path family | Candidates | Queue status |
|---:|---|---|---|---|---:|---|
| 1 | diamond | pokemon_battle | battle_back, battle_front, pokemon | `files/poketool/pokegra` | 1079 | unreviewed=1079 |
| 2 | diamond | trainer_graphics | portrait, trainer | `files/poketool/trgra` | 104 | unreviewed=104 |
| 3 | hgss | field | field, overworld | `files/fielddata/graphic` | 76 | unreviewed=76 |
| 4 | hgss | graphics | graphics, ui | `files/graphic/camera_viewfinder` | 1 | unreviewed=1 |
| 5 | hgss | graphics | graphics, ui | `files/graphic/zukan_gra` | 46 | unreviewed=46 |
| 6 | hgss | pokemon_battle | battle_back, battle_front, pokemon | `files/poketool/pokegra` | 1316 | unreviewed=1316 |
| 7 | hgss | pokemon_icons | party_icon, pokemon, summary_icon | `files/poketool/icongra` | 543 | unreviewed=543 |

## Curation boundary

- P1 valid_render is reconstruction evidence, not automatically usable.
- P3 native PNG status still requires visual/semantic review.
- Grouping is for efficient review; decisions must remain traceable to asset_id.
- Exact duplicates stay represented by their Lane A visual representative.
- No preferred donor or Platinum replacement is selected here.
