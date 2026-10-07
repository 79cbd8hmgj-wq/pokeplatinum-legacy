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
* Selection ({'alternate': 17, 'not_selected': 48, 'preferred': 21, 'reference_only': 166}): 21 preferred, 17 alternate, 48 identical to native, 166 reference_only (60 HGSS-only classes without a Platinum counterpart + Diamond control).
* Caveat: 8 preferred back pics have an identical first frame; their gain is in later animation frames (runtime QA).

## hgss_field_sprites (212 sheets)
* Source: `files/data/mmodel/mmodel/*.NSBTX` (832 scanned). Human NPC/player scope rule only; excluded and NOT cataloged: {'object_or_other': 48, 'pokemon_follower_2pal': 572} (Pokemon followers, objects, 64x64 sheets, NSBMD models/json).
* Format: NSBTX frame textures (32x32 4bpp, numeric-suffix order) — index data is byte-identical to Platinum's `res/graphics/field_sprites` PNGs for 96 aligned sprites.
* Alignment (`selection/alignment/field_sprites.json`) is by shared model-slot base name. **Slot name != subject**: Platinum reuses slot names for different characters, so non-trivial differences are `subject_unverified` (needs visual confirmation), not gain.
* Selection ({'alternate': 1, 'not_selected': 259, 'reference_only': 115}): 96 identical to native, 111 HGSS-only sprites (reference), 4 `needs_evidence`, 1 minor-diff alternate; 163 Ranger sprites not relevant.

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
