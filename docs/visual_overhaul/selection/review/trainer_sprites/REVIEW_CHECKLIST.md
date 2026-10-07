# Trainer Sprite Visual QA Checklist

Status: **human review complete** (verdicts recorded in `../decisions/trainer_battle_sprites.json` and consumed by the selection rules as explicit evidence). Automated metrics only describe *difference*, not *quality*.

- Candidates reviewed: **10** (10 front, 0 back); verdicts: {'use_hgss': 6, 'keep_platinum': 4}
- Needing later-frame inspection (frame 0 identical, a later frame differs): **1**
- Automated classes: {'redrawn_artwork': 8, 'later_frames_differ': 1, 'recolor_only': 1}
- Withdrawn from the earlier 21 after a decoder fix: **11** (see below)

Contact sheets: `front_01.png`. Legend: yellow=both opaque but colour differs, green=HGSS-only pixel, magenta=Platinum-only pixel, grey=same, comparison in BGR555 space.

## Review criteria (per candidate)

1. Same character/class identity as Platinum's (a redraw changes the class's look, not just quality).
2. Art quality and consistency with neighbouring Platinum trainer art (outline, palette, shading).
3. All animation frames present, in the same order, with no popping (frame count must match or exceed Platinum's).
4. Geometry: feet/bottom anchor and centre within a few px of Platinum (battle placement is not re-tuned).
5. Palette: 16-colour limit and index 0 transparency preserved (decoded palette fits Platinum's trainer palette slot).

## Candidates

| Done | ID | Class | Automated class | Changed px / % | Frames | Verdict | Reason |
|---|---|---|---|---|---|---|---|---|
| [x] | hgss_front_002 | youngster | redrawn_artwork | 1211 / 96.7% | 1/1 | **use_hgss** | Clear art-quality improvement that preserves the trainer class identity. |
| [x] | hgss_front_003 | lass | redrawn_artwork | 1282 / 96.9% | 1/1 | **use_hgss** | Clear art-quality improvement that preserves the trainer class identity. |
| [x] | hgss_front_006 | bug_catcher | redrawn_artwork | 2401 / 99.2% | 1/1 | **use_hgss** | Clear art-quality improvement that preserves the trainer class identity. |
| [x] | hgss_front_008 | twins | redrawn_artwork | 1660 / 97.6% | 1/1 | **use_hgss** | Clear art-quality improvement that preserves the trainer class identity. |
| [x] | hgss_front_024 | ace_trainer_male | redrawn_artwork | 1720 / 98.7% | 1/1 | **keep_platinum** | Ace Trainers keep their Platinum/Sinnoh designs; HGSS is a regional redesign, not a quality upgrade. |
| [x] | hgss_front_025 | ace_trainer_female | redrawn_artwork | 1633 / 98.6% | 1/1 | **keep_platinum** | Ace Trainers keep their Platinum/Sinnoh designs; HGSS is a regional redesign, not a quality upgrade. |
| [x] | hgss_front_036 | beauty | redrawn_artwork | 1853 / 97.5% | 1/1 | **use_hgss** | Clear art-quality improvement that preserves the trainer class identity. |
| [x] | hgss_front_043 | swimmer_female | redrawn_artwork | 1315 / 90.5% | 1/1 | **use_hgss** | Clear art-quality improvement that preserves the trainer class identity. |
| [x] | hgss_front_101 | arcade_star | later_frames_differ | 2304 / 14.5% | 11/11 | **keep_platinum** | Only a limited later-frame difference (3 of 11 frames); insufficient to justify replacement. |
| [x] | hgss_front_122 | young_couple | recolor_only | 126 / 7.1% | 1/1 | **keep_platinum** | Recolor-only/negligible change; not worth introducing a donor dependency. |

## Withdrawn after decoder fix

Earlier renders ignored the NCER per-cell VRAM transfer table, so later animation frames were mis-decoded. After decoding each cell from its own VRAM-transfer chunk, these now compare as follows:

| ID | Class | Now | Relation |
|---|---|---|---|
| hgss_back_004 | trainer_cheryl | not_selected | identical |
| hgss_back_005 | trainer_riley | not_selected | identical |
| hgss_back_009 | dp_player_male | not_selected | identical |
| hgss_back_010 | dp_player_female | not_selected | identical |
| hgss_back_011 | dp_rival | not_selected | identical |
| hgss_back_012 | player_male | not_selected | identical |
| hgss_back_013 | player_female | not_selected | identical |
| hgss_back_014 | rival | not_selected | identical |
| hgss_front_097 | tower_tycoon | alternate | art_diff_minor |
| hgss_front_099 | hall_matron | not_selected | identical |
| hgss_front_100 | factory_head | not_selected | identical |
