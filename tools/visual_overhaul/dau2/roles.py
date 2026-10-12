"""Per-move ingredient queries for the 33 B9 P1/P2 moves (planning data - provisional until the owner reviews visuals).

Each move lists *components* (launch / travel / impact / aftermath / reaction ...).  A component query has three evidence kinds, which
the matrix keeps strictly apart:

  names  - regex over donor art that carries a real name (GBA sprite file names, Crystal object names)      -> basis "named_source"
  plat   - Platinum move-particle slugs (``res/graphics/battle/particles/<slug>.spa``) whose DP/HGSS counterparts are found via
           the index/texture-set alignment verified by the matrix                                         -> basis "named_move_particle"
  feat   - a hue/shape target for ANONYMOUS art (PMD, Ranger 2, HGSS/Diamond cell banks)                  -> basis "feature_heuristic"

The mapping from a move to these queries is the model's design judgement from the move's B9 template and visual intent. It is a *search aid*;
it is not a visual approval and nothing here selects an asset for implementation.
"""
from __future__ import annotations

HUE_GROUPS = {
    "warm": ["red", "orange", "yellow"], "fire": ["red", "orange"], "yellow": ["yellow", "orange"],
    "green": ["lime", "green", "teal"], "water": ["azure", "blue", "cyan", "teal"], "ice": ["cyan", "azure", "blue"],
    "psychic": ["pink", "magenta", "purple"], "ghost": ["purple", "magenta"], "earth": ["orange", "yellow", "red"],
}


def C(names, plat, hues, shape, **kw):
    return {"names": names, "plat": plat, "feat": {"hues": HUE_GROUPS.get(hues, hues) if isinstance(hues, str) else hues, "shape": shape, **kw}}


IMPACT = r"^(hit|hit_duplicate|impact|impact_2|impact_3|punch_impact|circle_impact|cross_impact|slam_hit|slam_hit_2|horn_hit|horn_hit_2|red_fist|pink_glove)$"
STARS = r"^(gold_stars|yellow_star|blue_star|green_star|sparkle_1|sparkle_3|sparkle_4|sparkle_6|eye_sparkle|green_sparkle|twinkle|star)"
DUST = r"^(speed_dust|flying_dirt|dirt_mound|mud_sand_0|mud_sand_1|mud_unk|smoke|smoke_2|gray_smoke|black_smoke)$"
SLASH = r"^(slash|slash_2\.pal|claw_slash|claw_slash_2|scratch|scratch_2|scratch_3|cut|swipe|purple_scratch|purple_swipe|air_slash|sword|sword_2|torn_metal)$"
SHOCK = r"^(electricity|electric_orbs|lightning|lightning_2|shock|shock_2|shock_3|shock_4|spark_0|spark_1|spark_2|spark_h|spark\.pal)$"
FIRE = r"^(fire|fire_plume|small_ember|spinning_fire|wisp_fire|blue_flames|blue_flames_2|purple_flame|red_particles)$"
WATER = r"^(water_column|water_droplet|water_droplet_2|water_impact|water_orb|splash|rain_drops|bubble|bubble_burst|bubble_burst_2|small_bubbles|blue_burst)$"
ROCK = r"^(rocks|flat_rock|warm_rock|brown_triangle|meteor|metal_ball)$"
ICE = r"^(ice_chunk|ice_spikes|icicle_spear|blue_shards|ice_crystals_[0-4]|ice_crystals\.pal|ice_cube_[0-3]|ice_cube\.pal|hail|snowball)$"
LEAF = r"^(leaf|petal|pink_petal|green_spike|green_star|green_sparkle|sprout|vine|vine_2)$"
RING = r"^(thin_ring|ring|blue_ring\.pal|blue_ring_2\.pal|purple_ring\.pal|rainbow_rings|circle_of_light|white_circle_of_light\.pal|round_white_halo|guard_ring|movement_waves|metal_sound_waves|gold_ring)$"
POWDER = r"^(poison_powder|sleep_powder\.pal|stun_spore\.pal|spore|particles|purple_gas_cloud\.pal|pink_cloud|poison_bubble|toxic_bubble|sparkle_2\.pal)$"

MOVE_QUERIES: dict[str, dict] = {
    "Headbutt": {"launch": C(DUST, ["headbutt", "zen_headbutt", "skull_bash"], "earth", "specks"),
                 "impact": C(IMPACT, ["hit_1", "hit_2", "headbutt", "zen_headbutt", "pound"], "warm", "burst"),
                 "aftermath": C(STARS, ["dizzy_punch", "headbutt"], "yellow", "specks")},
    "Slam": {"impact": C(IMPACT, ["slam", "body_slam", "stomp", "mega_kick", "hit_2"], "warm", "burst"),
             "aftermath": C(DUST, ["earthquake", "dig", "stomp"], "earth", "specks")},
    "Wing Attack": {"travel": C(r"^(air_slash|air_wave|air_wave_2|white_feather|whirlwind|whirlwind_2|whirlwind_lines|bird|slash)$",
                                ["wing_attack", "steel_wing", "air_cutter", "air_slash", "gust"], ["white", "cyan", "azure"], "streak"),
                    "impact": C(IMPACT + "|" + SLASH, ["hit_1", "wing_attack", "slash"], ["white", "yellow"], "burst")},
    "Aerial Ace": {"travel": C(r"^(speed_dust|noise_line|air_wave|air_wave_2|whirlwind_lines|blue_lines|void_lines)$",
                               ["aerial_ace", "air_cutter", "quick_attack", "extreme_speed"], ["white", "cyan", "azure"], "streak"),
                   "impact": C(SLASH, ["aerial_ace", "slash", "night_slash", "cut", "air_slash"], ["white", "azure"], "streak")},
    "Spark": {"launch": C(SHOCK, ["spark", "charge", "thunder_shock"], "yellow", "specks"),
              "impact": C(SHOCK + "|" + IMPACT, ["spark", "thunder_punch", "thunderbolt", "discharge"], "yellow", "burst")},
    "Flame Wheel": {"travel": C(FIRE, ["flame_wheel", "fire_spin", "flare_blitz", "blaze_kick"], "fire", "orb"),
                    "aftermath": C(FIRE + "|small_ember", ["ember", "flame_wheel", "heat_wave"], "fire", "specks")},
    "Aqua Jet": {"travel": C(WATER, ["aqua_jet", "water_gun", "aqua_tail", "waterfall"], "water", "streak"),
                 "impact": C(WATER, ["surf", "water_pulse", "aqua_jet", "splash"], "water", "burst")},
    "BubbleBeam": {"travel": C(WATER, ["bubble_beam", "bubble", "octazooka", "water_pulse"], "water", "orb"),
                   "impact": C(WATER, ["bubble_beam", "bubble", "splash"], "water", "burst")},
    "Magical Leaf": {"travel": C(LEAF, ["magical_leaf", "razor_leaf", "leaf_blade", "leaf_storm", "petal_dance"], "green", "shard"),
                     "aftermath": C(LEAF + "|" + STARS, ["magical_leaf", "aromatherapy", "petal_dance"], "green", "specks")},
    "Metal Claw": {"travel": C(SLASH, ["metal_claw", "slash", "crush_claw", "fury_swipes", "iron_tail", "steel_wing"], ["white", "azure", "cyan"], "streak"),
                   "impact": C(STARS + "|" + IMPACT, ["metal_claw", "metal_sound", "mirror_shot"], ["white", "azure"], "burst")},
    "Rock Tomb": {"travel": C(ROCK, ["rock_tomb", "rock_throw", "rock_blast", "stone_edge", "rock_smash"], "earth", "shard"),
                  "aftermath": C(DUST, ["rock_slide", "rock_tomb", "magnitude"], "earth", "specks")},
    "Rock Slide": {"travel": C(ROCK, ["rock_slide", "rock_throw", "rock_blast", "stone_edge", "avalanche"], "earth", "shard"),
                   "aftermath": C(DUST, ["rock_slide", "earthquake", "rock_wrecker"], "earth", "specks")},
    "Crunch": {"launch": C(r"^(teeth|sharp_teeth|fangs|fang_attack)$", ["crunch", "bite", "super_fang", "hyper_fang"], ["white", "purple"], "shard"),
               "impact": C(IMPACT + "|^(teeth|sharp_teeth|fangs|fang_attack)$", ["crunch", "bite", "poison_fang", "thunder_fang", "fire_fang", "ice_fang"], ["white", "purple"], "burst")},
    "Ice Shard": {"travel": C(ICE, ["ice_shard", "icicle_spear", "ice_ball", "avalanche", "ice_fang"], "ice", "shard"),
                  "impact": C(ICE + "|" + STARS, ["ice_shard", "ice_beam", "blizzard"], "ice", "burst")},
    "Icy Wind": {"travel": C(r"^(hail|ice_crystals_[0-4]|ice_crystals\.pal|mist_cloud|whirlwind_lines|whirlwind|whirlwind_2|snowball)$",
                             ["icy_wind", "powder_snow", "blizzard", "mist", "hail"], "ice", "streak"),
                 "aftermath": C(ICE + "|" + STARS, ["icy_wind", "powder_snow", "ice_beam"], "ice", "specks")},
    "Mud Shot": {"travel": C(r"^(mud_sand_0|mud_sand_1|mud_unk|mud_sand\.pal|brown_orb\.pal|flying_dirt|dirt_mound)$",
                             ["mud_shot", "mud_slap", "muddy_water", "sand_attack"], "earth", "orb"),
                 "impact": C(DUST, ["mud_shot", "mud_slap", "mud_bomb"], "earth", "burst")},
    "Mud Bomb": {"travel": C(r"^(brown_orb\.pal|mud_sand_0|mud_sand_1|mud_unk|dirt_mound|metal_ball)$",
                             ["mud_bomb", "mud_shot", "mud_slap", "sludge_bomb", "muddy_water"], "earth", "orb"),
                 "impact": C(DUST + "|" + IMPACT, ["mud_bomb", "mud_slap", "earth_power", "explosion"], "earth", "burst")},
    "Psybeam": {"travel": C(RING, ["psybeam", "confusion", "psychic", "signal_beam", "psywave", "extrasensory"], "psychic", "ring"),
                "impact": C(RING + "|pink_orb|" + STARS, ["psybeam", "signal_beam", "psycho_cut"], "psychic", "burst")},
    "Swift": {"travel": C(STARS, ["swift", "luster_purge", "mist_ball", "tail_glow", "cosmic_power"], ["yellow", "white"], "burst"),
              "impact": C(STARS + "|" + IMPACT, ["swift", "mirror_shot", "magnet_bomb"], ["yellow", "white"], "burst")},
    "Thunder Wave": {"travel": C(SHOCK, ["thunder_wave", "thunder_shock", "charge", "discharge"], "yellow", "streak"),
                     "reaction": C(SHOCK, ["thunder_wave", "spark", "shock_wave"], "yellow", "specks")},
    "Hypnosis": {"travel": C(RING + "|^(spiral|pink_cloud)$", ["hypnosis", "sing", "lovely_kiss", "yawn"], "psychic", "ring"),
                 "reaction": C(r"^(letter_z|snore_z|z|thought_bubble|pink_cloud)$", ["hypnosis", "sleep_powder", "snore", "yawn"], ["white", "pink", "azure"], "specks")},
    "Confuse Ray": {"travel": C(r"^(ghostly_spirit|purple_flame|round_shadow|wisp_orb|hollow_orb|eclipsing_orb|wisp_fire|bluegreen_orb|gray_orb)$",
                                ["confuse_ray", "shadow_ball", "will_o_wisp", "astonish", "spite"], "ghost", "orb"),
                    "reaction": C(RING, ["confuse_ray", "psybeam", "confusion", "dizzy_punch"], ["purple", "yellow", "white"], "ring")},
    "Poison Powder": {"travel": C(POWDER, ["poison_powder", "poison_gas", "smog", "toxic"], ["purple", "magenta"], "specks"),
                      "reaction": C(r"^(poison_bubble|toxic_bubble|purple_gas_cloud\.pal|purple_droplet|purple_green_unk)$", ["poison_gas", "toxic", "acid"], ["purple", "magenta"], "specks")},
    "Sleep Powder": {"travel": C(POWDER, ["sleep_powder", "spore", "cotton_spore", "sweet_scent"], ["pink", "azure", "white"], "specks"),
                     "reaction": C(r"^(letter_z|snore_z|z|pink_cloud)$", ["sleep_powder", "spore", "snore"], ["white", "pink", "azure"], "specks")},
    "Stun Spore": {"travel": C(POWDER, ["stun_spore", "spore", "cotton_spore"], "yellow", "specks"),
                   "reaction": C(SHOCK, ["stun_spore", "thunder_wave", "spark"], "yellow", "specks")},
    "Swords Dance": {"launch": C(r"^(sword|sword_2|nail|needle)$", ["swords_dance", "sharpen", "dragon_dance", "bulk_up"], ["white", "azure"], "streak"),
                     "aftermath": C(STARS + "|" + RING, ["swords_dance", "nasty_plot", "calm_mind"], ["white", "azure"], "specks")},
    "Defense Curl": {"launch": C(r"^(guard_ring|round_white_halo|circle_of_light|white_circle_of_light\.pal|metal_ball|protect|substitute)$", ["defense_curl", "harden", "withdraw", "iron_defense", "barrier"], ["white", "yellow"], "ring"),
                     "aftermath": C(STARS, ["defense_curl", "harden", "iron_defense"], ["white", "yellow"], "specks")},
    "Focus Energy": {"launch": C(r"^(focus_energy|red_orb|red_orb_2\.pal|red_ring|spotlight|particles|glowy_red_orb|yellow_ball)$", ["focus_energy", "mind_reader", "charge", "cosmic_power", "bulk_up"], ["red", "orange", "yellow"], "ring"),
                     "aftermath": C(STARS, ["focus_energy", "power_trick", "calm_mind"], ["white", "yellow"], "specks")},
    "Sand Attack": {"travel": C(r"^(mud_sand_0|mud_sand_1|mud_sand\.pal|flying_dirt|dirt_mound|speed_dust|smokescreen_impact|brown_orb\.pal)$", ["sand_attack", "smoke_screen", "mud_slap", "sandstorm"], "earth", "specks"),
                    "reaction": C(DUST, ["sand_attack", "smoke_screen", "dig"], "earth", "specks")},
    "String Shot": {"travel": C(r"^(string|string_2|web|web_thread|spider_web|tendrils)$", ["string_shot", "spider_web", "bind", "wrap", "constrict"], ["white", "pink"], "streak"),
                    "reaction": C(r"^(web|web_thread|spider_web|string|string_2)$", ["string_shot", "spider_web", "bind"], ["white"], "ring")},
    "Leech Seed": {"travel": C(r"^(seed|seed_2|sprout|sap_drip|sap_drip_2\.pal|green_orb)$", ["leech_seed", "bullet_seed", "seed_bomb", "absorb"], "green", "orb"),
                   "reaction": C(r"^(vine|vine_2|roots|tendrils|sprout|sap_drip|sap_drip_2\.pal)$", ["leech_seed", "ingrain", "vine_whip", "mega_drain", "giga_drain"], "green", "streak")},
    "Supersonic": {"travel": C(RING + "|^(jagged_music_note|music_notes|music_notes_2|noise_line)$", ["supersonic", "sonic_boom", "screech", "metal_sound", "hyper_voice", "uproar"], ["azure", "cyan", "white", "blue"], "ring"),
                   "reaction": C(r"^(noise_line|jagged_music_note|music_notes|alert|teal_alert|dizzy)$", ["supersonic", "screech", "sing"], ["azure", "white", "yellow"], "specks")},
    "Double Team": {"launch": C(r"^(white_shadow|round_shadow|humanoid_hand|humanoid_foot|substitute|substitute_back)$", ["agility", "teleport", "extreme_speed", "quick_attack", "substitute"], ["white"], "orb"),
                    "aftermath": C(DUST, ["agility", "teleport", "quick_attack"], ["white"], "specks")},
}

ASSUMED_MISSING = ["Double Team has no dedicated Platinum move-particle file (its vanilla animation is script-only), so its 'plat' list is analogous effects."]
