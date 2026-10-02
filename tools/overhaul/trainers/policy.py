"""Machine-readable validation rules + ordinary-trainer archetypes (written by build_manifest.py)."""
from __future__ import annotations

import ordinary as O
import locked_teams as L
from build_manifest_consts import ACE_LEVEL

ARCHETYPE_CLASSES = {
    "beginner": ["YOUNGSTER", "LASS", "SCHOOL_KID_MALE", "SCHOOL_KID_FEMALE", "POKE_KID", "TWINS"],
    "habitat_specialist": ["HIKER", "FISHERMAN", "BIRD_KEEPER", "BUG_CATCHER", "SAILOR", "SWIMMER_MALE", "SWIMMER_FEMALE", "CAMPER",
                           "PICNICKER", "RUIN_MANIAC", "TUBER_MALE", "TUBER_FEMALE", "SKIER_MALE", "SKIER_FEMALE", "RANGER_MALE",
                           "RANGER_FEMALE", "NINJA_BOY", "PARASOL_LADY", "AROMA_LADY", "COWGIRL", "RANCHER", "WORKER", "POLICEMAN",
                           "JOGGER", "CYCLIST_MALE", "CYCLIST_FEMALE", "BLACK_BELT", "BATTLE_GIRL"],
    "skilled_route_trainer": ["ACE_TRAINER_MALE", "ACE_TRAINER_FEMALE", "ACE_TRAINER_SNOW_MALE", "ACE_TRAINER_SNOW_FEMALE", "VETERAN",
                              "DRAGON_TAMER", "PSYCHIC_MALE", "PSYCHIC_FEMALE", "PI", "ROUGHNECK"],
    "breeder": ["BREEDER_MALE", "BREEDER_FEMALE", "POKEFAN_MALE", "POKEFAN_FEMALE", "COLLECTOR"],
    "galactic_grunt": ["GALACTIC_GRUNT_MALE", "GALACTIC_GRUNT_FEMALE"],
    "flavor": ["BEAUTY", "ARTIST", "CLOWN", "IDOL", "GENTLEMAN", "MAID", "LADY", "SOCIALITE", "RICH_BOY", "GUITARIST", "INTERVIEWERS",
               "CAMERAMAN", "REPORTER", "SCIENTIST", "WAITRESS"],
    "double_battle": ["DOUBLE_TEAM", "YOUNG_COUPLE", "SIS_AND_BRO", "BELLE_AND_PA"],
}


def archetypes() -> dict:
    return {
        "schema": "trainer_archetypes/1",
        "authority": "TRAINER_OVERHAUL_SPEC.md section 10-11",
        "classes": ARCHETYPE_CLASSES,
        "party_size_guidance": {
            "beginner": [1, 3], "habitat_specialist": [1, 4], "skilled_route_trainer": [1, 5], "breeder": [1, 5],
            "galactic_grunt": [1, 4], "flavor": [1, 4], "double_battle": [2, 4],
            "note": "advisory (validator warns; party sizes are not changed by the ordinary pass)",
        },
        "held_items": {"beginner": "none", "habitat_specialist": "rare", "skilled_route_trainer": "occasional berry", "default": "unchanged"},
        "ai": {"skilled_route_trainer": "expert where already supported; unchanged by this pass", "default": "unchanged"},
        "transformation_rules": {
            "R1_evolution_sync": "evolve to the unique plain level-evolution target when level >= threshold; devolve to the pre-evolution "
                                 "when level < the pre-evolution's threshold (thresholds read from live res/pokemon evolutions)",
            "R2_availability": "species whose family earliest band is later than the trainer's band is replaced",
            "R3_duplicate": "within-team repeated species are replaced (double battles exempt)",
            "R4_usage_cap": {"species_cap": O.CAP_SPECIES, "family_cap": O.CAP_FAMILY, "max_swaps_per_trainer": O.MAX_SWAPS_PER_TRAINER,
                             "scope": "active map-placed ordinary trainers"},
            "R5_moves": "explicit-move teams only: illegal or obviously weak (<=40 power, non-STAB, level>=28) moves are replaced "
                        "by natural STAB attacks, <=2 slots per Pokémon",
            "replacement_selection": {"types": "share a type with the replaced species (Galactic grunts: Poison/Dark/Flying/Normal)",
                                      "bst_window": [O.BST_LOW, O.BST_HIGH], "stage": "no evolution-stage contradiction at that level",
                                      "excluded": "legendary/reserved families, SPECIAL_ACQUISITION families, Unown/Ditto/Smeargle/Shedinja/Wobbuffet/Wynaut",
                                      "ranking": "type affinity, then least-used (species + family), then BST proximity, then stable hash"},
        },
        "band_overrides": O.BAND_OVERRIDE,
        "level_fallback_bands": [[lim, b] for lim, b in O.LEVEL_BAND],
        "excluded_from_ordinary_pass": {
            "prefixes": list(O.SPECIAL_PREFIXES) + list(O.BOSS_PREFIXES), "substrings": ["_unused", "dummy"],
            "reason": "partner/story specials, boss records and unused/dummy records are not ordinary trainers",
        },
        "class_identity": "preserved by the type-sharing rule; no competitive sets, no perfect coverage, held items and iv_scale unchanged",
    }


def rules(created_recipients: dict) -> dict:
    seq = ["leader_roark", "leader_gardenia", "leader_fantina", "leader_maylene", "leader_wake", "leader_byron", "leader_candice",
           "leader_volkner", "rival_pokemon_league_turtwig", "elite_four_aaron", "elite_four_bertha", "elite_four_flint",
           "elite_four_lucian", "champion_cynthia"]
    return {
        "schema": "trainer_validation_rules/1",
        "party_size": {
            "gym_leader": {"leader_roark": 3, "leader_gardenia": 3, "leader_fantina": 3, "leader_maylene": 4, "leader_wake": 4,
                           "leader_byron": 4, "leader_candice": 4, "leader_volkner": 5},
            "elite_four": 5, "champion": 6, "gym_rematch": 5, "elite_four_rematch": 5, "champion_rematch": 6,
            "galactic_commander": {"commander_mars_valley_windworks": 2, "commander_jupiter_team_galactic_eterna_building": 2,
                                   "default": 3},
            "galactic_boss": {"galactic_boss_cyrus_galactic_hq": 4, "galactic_boss_cyrus_distortion_world": 5},
            "rival": {"rival_route_203": 2, "rival_route_209": 4, "rival_pastoria_city": 4, "rival_canalave_city": 5,
                      "rival_pokemon_league": 6, "rival_fight_area": 6, "rival_survival_area_1": 6, "rival_survival_area_2": 6,
                      "rival_survival_area_unused": 6},
            "ordinary_max": 6,
        },
        "level_bands": {
            "rival_route_203": [7, 9], "rival_route_209": [23, 27], "rival_pastoria_city": [32, 36], "rival_canalave_city": [35, 38],
            "rival_pokemon_league": [47, 51], "gym_rematch_and_elite_rematch": [60, 78], "champion_rematch": [70, 80],
            "note": "main-story gym/E4/Cynthia levels are the exact locked values (checked against locked_teams); rematch bands are "
                    "provisional until the postgame EXP/economy phase (spec s.12: roughly 62-70)",
        },
        "ace_levels": ACE_LEVEL | {"rival_pokemon_league": 51, "elite_four_aaron": 53, "elite_four_bertha": 55, "elite_four_flint": 57,
                                   "elite_four_lucian": 59, "champion_cynthia": 62},
        "boss_curve_sequence": seq,
        "gym_theme_type": {"leader_roark": "TYPE_ROCK", "leader_gardenia": "TYPE_GRASS", "leader_fantina": "TYPE_GHOST",
                           "leader_maylene": "TYPE_FIGHTING", "leader_wake": "TYPE_WATER", "leader_byron": "TYPE_STEEL",
                           "leader_candice": "TYPE_ICE", "leader_volkner": "TYPE_ELECTRIC", "elite_four_aaron": "TYPE_BUG",
                           "elite_four_bertha": "TYPE_GROUND", "elite_four_flint": "TYPE_FIRE", "elite_four_lucian": "TYPE_PSYCHIC"},
        "max_off_type_members": 1,
        "ai": {
            "required_flags": ["AI_FLAG_BASIC", "AI_FLAG_EVAL_ATTACK", "AI_FLAG_EXPERT"],
            "required_categories": ["gym_leader", "gym_rematch", "elite_four", "elite_four_rematch", "champion", "champion_rematch",
                                    "galactic_commander", "galactic_boss", "rival"],
            "exempt_ids": ["rival_route_201_*", "rival_route_203_*"],
            "exempt_reason": "tutorial-tier intro rival fights keep their existing AI (spec: existing flags are the baseline)",
        },
        "duplicates": {"important_categories": ["gym_leader", "gym_rematch", "elite_four", "elite_four_rematch", "champion",
                                                "champion_rematch", "galactic_commander", "galactic_boss", "rival"],
                       "allowed": []},
        "held_items": {
            "gym1_none": "leader_roark",
            "main_story_forbidden": ["ITEM_CHOICE_BAND", "ITEM_CHOICE_SPECS", "ITEM_CHOICE_SCARF", "ITEM_LIFE_ORB", "ITEM_FOCUS_SASH",
                                     "ITEM_LEFTOVERS"],
            "main_story_categories": ["gym_leader", "elite_four", "champion", "galactic_commander", "galactic_boss", "rival"],
            "ace_may_hold": "berry; at most one extra modest item from Gym 6 on (none used)",
            "max_items_per_main_story_team": 3,
            "rival_item_gate": "starter Sitrus from Canalave onward; Snorlax Chesto at the League and postgame",
        },
        "bag_items": {"gym_max_heals": 2, "elite_four_exact": ["ITEM_FULL_RESTORE", "ITEM_FULL_RESTORE"],
                      "champion_exact": ["ITEM_FULL_RESTORE"] * 4},
        "moves": {"superseded": [], "unresolved": ["MOVE_DRAGON_SWIPE"],
                  "unresolved_reason": "final recipient unresolved in CREATED_MOVES.md; no trainer may use it",
                  "created_move_recipients": created_recipients,
                  "explicit_spec_moves_may_be_outside_learnset": True,
                  "note": "locked-spec explicit moves and manifest created-move recipients may exceed current learnsets "
                          "(reported as notes); every other manifest move must be legal"},
        "evolution": {"ordinary": "ERROR on under-evolved (level >= level-evolution threshold) or over-evolved (level < pre-evolution threshold)",
                      "bosses": "WARNING (locked/boss teams may showcase evolved forms early; explicit spec teams are authoritative)"},
        "availability": {"band_order": ["E0", "E1", "M1", "M2", "L1", "L2", "P0", "P1"],
                         "ordinary": "ERROR when a species' family earliest band is later than the trainer's band",
                         "important": "bosses may showcase at most one band early; reported, not blocking"},
        "iv_scale": {"max_meaningful": 255, "warn_values_above": 255, "normalization": "not performed"},
        "power_curve": {"bst_jump_flag_ratio": 1.18, "strength_jump_flag_ratio": 1.45,
                        "explained": {"leader_gardenia": "locked spec s.6: redesigned Cherrim + 515-BST Roserade make Gym 2 substantially stronger by design"},
                        "note": "heuristic audit only; flags are for human review"},
        "frontier": {"directory": "res/trainers/frontier", "must_be_unmodified": True},
    }
