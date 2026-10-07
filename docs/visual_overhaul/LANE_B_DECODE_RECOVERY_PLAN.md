# Lane B Decode Recovery Plan

Original Lane B `decode_issue` population (7,183) grouped by family with current disposition.
No Platinum resources are modified.

- Original decode_issue: **7183**
- Now usable: **5081**  ·  reject: **1173**  ·  still decode_issue: **929**

## By source

| Source | Original | usable | reject | decode_issue |
|---|---:|---:|---:|---:|
| diamond | 723 | 715 | 8 | 0 |
| hgss | 86 | 76 | 8 | 2 |
| pmd_sky | 557 | 538 | 0 | 19 |
| ranger2 | 5817 | 3752 | 1157 | 908 |

## By route and method

| Route | Original | usable | reject | decode_issue | Method |
|---|---:|---:|---:|---:|---|
| container_unpack_then_decode | 1350 | 903 | 3 | 444 | same package pipelines as ranger_embedded_decode, applied at package level |
| format_context_unknown | 9 | 0 | 9 | 0 | evidence-based non-art classification (classify_lane_b_support_files.py) |
| nitro_2d_decode | 719 | 715 | 4 | 0 | Diamond icon NCGR sentinel geometry (recover_lane_b_diamond_icons.py); otherpoke NCGR/NCLR pairing from decomp pokemon.c with back-to-front LCG decrypt (recover_lane_b_nitro2d_pairs.py) |
| pmd_format_decode | 557 | 538 | 0 | 19 | SkyTemple reference decoder (recover_lane_b_pmd_sky.py) |
| ranger_embedded_decode | 4472 | 2849 | 1157 | 466 | Ranger LZ10->NARC->NCLR/NCBR/NCGR/NCER render incl. 1D OBJ mapping + sentinel NCGR (recover_lane_b_ranger_embedded.py); map chips (recover_lane_b_ranger_maps.py) |
| source_png_equivalent | 76 | 76 | 0 | 0 | same-stem native PNG already curated usable (resolve_lane_b_source_png_equivalents.py) |

## Families still needing work

| Source | Type | Group | Kind | Path family | Remaining |
|---|---|---|---|---|---:|
| ranger2 | embedded_visual_resource | field | member_N | `field/map` | 447 |
| ranger2 | compressed_visual_package | field | lz | `field/map` | 442 |
| ranger2 | embedded_visual_resource | field | member_N | `field/effect` | 4 |
| hgss | visual_container | field | narc | `files/fielddata/build_model` | 2 |
| ranger2 | embedded_visual_resource | field | NCGR | `field/effect` | 2 |
| ranger2 | embedded_visual_resource | npc | NCBR | `npc/n000_00_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | NCBR | `npc/npc072_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | NCER | `npc/npc072_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | cac | `npc/npc072_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | NCBR | `npc/npc107_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | NCER | `npc/npc107_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | cac | `npc/npc107_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | NCBR | `npc/npc108_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | NCER | `npc/npc108_LZ.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | cac | `npc/npc108_LZ.bin` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | effects | wba | `files/EFFECT/ame.wba` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | effects | wba | `files/EFFECT/test.wba` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | ground_sprites_effects | wat | `files/GROUND/g01p03a2.wat` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | ground_sprites_effects | wat | `files/GROUND/p09p01a1.wat` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/s01p01a1.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/s01p01a2.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/s13p03a1.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/s13p03a2.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/s20p01a1.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/s20p01a2.wan` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | ground_sprites_effects | wat | `files/GROUND/s20p02a1.wat` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/v01p05b1.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/v01p05b2.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/v01p05b3.wan` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | ground_sprites_effects | wat | `files/GROUND/v10p01c1.wat` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | ground_sprites_effects | wat | `files/GROUND/v10p01c2.wat` | 1 |
| pmd_sky | pmd_effect_or_texture_resource | ground_sprites_effects | wat | `files/GROUND/v10p01c3.wat` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/v19p06a1.wan` | 1 |
| pmd_sky | pmd_sprite_animation_container | ground_sprites_effects | wan | `files/GROUND/v37p02a1.wan` | 1 |
| ranger2 | embedded_visual_resource | field | narc | `field/effect` | 1 |
| ranger2 | visual_candidate_file | field | bin | `field/fielddata.bin` | 1 |
| ranger2 | embedded_visual_resource | npc | narc | `npc/n000_00_LZ.bin` | 1 |
