# Catalog Extensions — HGSS sprite gap passes

Targeted, script-generated additions to the donor catalog (the 65 MB base catalog is not rewritten).
`MANIFEST.json` lists extensions; each has `CATALOG.json` (catalog schema, pinned HGSS commit, exact source paths/NARC members)
and `CURATION.json` (recovered-curation schema). Coverage invariant (`DONOR_CURATION_STATUS`): base + extension catalog assets
== base + extension curation records, no overlap, no unreviewed. Everything downstream (groups, selection, validation) reads
extension ledgers automatically via `MANIFEST.json`. Refresh: `tools/visual_overhaul/selection/refresh_all.sh`.

## hgss_trainer_sprites (146 sets)
* Source: `files/a/0/5/8` (129 front classes) and `files/a/0/0/6` (17 back pics), 5 members per class
  (NCGR, NCLR, NCER, NANR, NCBR; loader `src/pokemon.c:sub_02070D3C`). Source paths are `files/a/0/5/8#class=NNN` (fragment = NARC class index).
* Format: same extended-cell NCER / 80x80 4bpp NCGR model as Platinum trfgra/trbgra; OBJ char unit = 64 B (RAHC mapping mode 1D_64K) — decoded renders in `hgss_trainer_sprites/renders/` (all 146 usable, none rejected).
* Alignment (`selection/alignment/trainer_classes.json`): HGSS class -> Platinum class by exact/suffix/alias name (75/137 front, 11/17 back); Diamond class index == Platinum class index (98/98).
* Selection (after the VRAM-transfer decoder fix below): 10 preferred, 18 alternate, 58 identical to native, 166 reference_only (68 without a Platinum counterpart + Diamond control).
* **Decoder correction:** NCER banks carry a per-cell VRAM-transfer table (source offset/size into the NCGR); the first render pass ignored it, so multi-frame sets showed the first pose repeated. After fixing, all 8 back-pic candidates and 2 front candidates (hall_matron, factory_head) matched Platinum exactly and tower_tycoon dropped to a 0.8% minor difference; all 11 were withdrawn (earlier 21 preferred -> 10). Review package: `selection/review/trainer_sprites/`.

## hgss_field_sprites (212 sheets)
* Source: `files/data/mmodel/mmodel/*.NSBTX` (832 scanned). Human NPC/player scope rule only; excluded and NOT cataloged: {'object_or_other': 48, 'pokemon_follower_2pal': 572} (Pokemon followers, objects, 64x64 sheets, NSBMD models/json).
* Format: NSBTX frame textures (32x32 4bpp, numeric-suffix order) — index data is byte-identical to Platinum's `res/graphics/field_sprites` PNGs for 96 aligned sprites.
* Alignment (`selection/alignment/field_sprites.json`) is by shared model-slot base name. **Slot name != subject**: Platinum reuses slot names for different characters, so non-trivial differences are `subject_unverified` (needs visual confirmation), not gain.
* Selection ({'alternate': 1, 'not_selected': 259, 'reference_only': 115}): 96 identical to native, 111 HGSS-only sprites (reference), 4 `needs_evidence`, 1 minor-diff alternate; 163 Ranger sprites not relevant.

## hgss_field_3d (4,793 assets / 1,240 groups)
* Source (pinned HGSS commit in `CATALOG.json`): `files/fielddata/build_model/bm_field.narc` (340 BMD0) + `bm_room.narc` (222), `files/a/0/4/4` (106 BTX0 map texture sets, 3,659 textures) and the 572 `MMODEL_FOLLOWER_MON*` sheets in `files/data/mmodel/mmodel` (the follower sheets were explicitly excluded from `hgss_field_sprites`; no overlap). `land_data` (`files/a/0/6/5`) stays reference-only and is not cataloged. The four container files (`bm_*.narc`, `bm_*_matshp.dat`) already exist in the base catalog as binary candidates; the extension decomposes them and does not touch those ids.
* Groups: one per model (562), per texture set (106, members = its textures), per follower sheet (572). Asset ids: `hgss:narc:files:fielddata:build_model:<bm_field|bm_room>:model_NNN`, `hgss:narc:files:a:0:4:4:set_SSS:tex_TTT`, `hgss:source:files:data:mmodel:mmodel:mmodel_NNNNNNNN.NSBTX`; source paths use `#member=` / `#set=&tex=` fragments.
* Measured metadata lives in `source_metadata` so mining never reopens the checkout: model geometry (tris, shapes, extents, geometry signature, duplicate-of), texture lists with exact/near hashes, Platinum counterpart by texture overlap, texture->set links; per-texture analysis and use class (`directly_reusable`, `convertible`, `component_region`, `enhancement_input`, `reference_only`, `identical_to_platinum`); follower species/form from `include/constants/mmodel.h`, 8-frame structure, mirror-pair direction test, palette names, Platinum equivalents. The previewer is approximate (no node transforms, name-paired palettes): discovery evidence, not pixel truth.
* New subsystems (`SUBSYSTEMS.json`): `field_building_models`, `field_texture_sets`, `overworld_pokemon_sheets`; evidence provider `evidence_field_3d.py` (donor-free). Mining rules: `mine_x3d.py`. Refresh: `inventory_hgss_field_3d.py --hgss-root <pinned checkout>` then `refresh_all.sh`. Tests: `test_field_3d.py`.

## Combined queue
| # | Kind | Subsystem | Source | Targets |
|---:|---|---|---|---:|
| 1 | implement | pokemon_battle_sprites | hgss | 26 |
| 2 | implement | trainer_battle_sprites | hgss | 21 |
| 3 | evidence | pokemon_battle_sprites | hgss | 2 |
| 4 | evidence | field_environment_art | hgss | 23 |
| 5 | evidence | field_npc_player_sprites | hgss | 4 |
| 6 | evidence | menu_ui_frames | hgss | 1 |
| 7 | evidence | party_summary_ui | hgss | 1 |
| 8 | evidence | pokedex_ui | hgss | 1 |
| 9 | runtime_qa | pokemon_battle_sprites | hgss | 26 |
| 10 | runtime_qa | trainer_battle_sprites | hgss | 21 |

## Decoder lock (authoritative)

HGSS trainer sprite comparisons must use `tools/visual_overhaul/hgss_trainer_sprite_lib.decode_sheet()` (`DECODER_VERSION = ncer-vram-transfer-v1`): each NCER cell is drawn from its own VRAM-transfer chunk, and a multi-cell bank without a transfer table is rejected. Catalog assets record `decoder_version`; the validator and `test_hgss_trainer_decoder.py` (CI) fail if any asset was produced otherwise or if the first-chunk-for-every-frame behaviour returns.

## Human review

Verdicts live in `selection/review/decisions/trainer_battle_sprites.json` and are consumed by the rules (R0) as explicit evidence bound to the group digest and evidence-entry digest. Result: 6 `use_hgss` (youngster, lass, bug_catcher, twins, beauty, swimmer_female) -> preferred; 4 `keep_platinum` (ace_trainer_male/female, arcade_star, young_couple).
