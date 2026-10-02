"""Locked D1 team definitions transcribed from docs/overhaul/trainers/TRAINER_OVERHAUL_SPEC.md.

Each member: (species, level, held item or None, [moves]).  Names omit the SPECIES_/ITEM_/MOVE_ prefixes.
Only data the locked spec names explicitly lives here; moves marked as "fill" by the spec are curated in
`curated_sets.py` from current legal learnsets.
"""
GYMS = {
    "leader_roark": [
        ("GEODUDE", 12, None, ["STEALTH_ROCK", "ROCK_THROW", "TACKLE"]),
        ("ONIX", 13, None, ["STEALTH_ROCK", "ROCK_THROW", "SCREECH", "BIND"]),
        ("CRANIDOS", 14, None, ["HEADBUTT", "PURSUIT", "FOCUS_ENERGY", "LEER"]),
    ],
    "leader_gardenia": [
        ("TURTWIG", 20, None, ["GRASS_KNOT", "RAZOR_LEAF", "REFLECT", "SUNNY_DAY"]),
        ("CHERRIM", 20, None, ["MAGICAL_LEAF", "LEECH_SEED", "SUNNY_DAY", "GROWTH"]),
        ("ROSERADE", 22, "SITRUS_BERRY", ["GRASS_KNOT", "MAGICAL_LEAF", "POISON_STING", "STUN_SPORE"]),
    ],
    "leader_fantina": [
        ("DUSKULL", 24, None, ["WILL_O_WISP", "SHADOW_SNEAK", "PURSUIT", "FUTURE_SIGHT"]),
        ("HAUNTER", 25, None, ["OMINOUS_WIND", "HYPNOSIS", "SUCKER_PUNCH", "CONFUSE_RAY"]),
        ("MISMAGIUS", 27, "SITRUS_BERRY", ["SHADOW_BALL", "PSYBEAM", "MAGICAL_LEAF", "CONFUSE_RAY"]),
    ],
    "leader_maylene": [
        ("MEDITITE", 28, None, ["DRAIN_PUNCH", "CONFUSION", "ROCK_TOMB", "FAKE_OUT"]),
        ("MACHOKE", 29, None, ["BRICK_BREAK", "ROCK_TOMB", "STRENGTH", "FOCUS_ENERGY"]),
        ("HITMONCHAN", 30, None, ["MACH_PUNCH", "BULLET_PUNCH", "DRAIN_PUNCH", "ICE_PUNCH"]),
        ("LUCARIO", 32, "SITRUS_BERRY", ["DRAIN_PUNCH", "FORCE_PALM", "METAL_CLAW", "BONE_RUSH"]),
    ],
    "leader_wake": [
        ("GYARADOS", 33, None, ["WATERFALL", "BITE", "TWISTER", "LEER"]),
        ("QUAGSIRE", 34, None, ["MUD_SHOT", "ROCK_TOMB", "WATER_PULSE", "YAWN"]),
        ("KINGLER", 35, None, ["CRABHAMMER", "STOMP", "METAL_CLAW", "PROTECT"]),
        ("FLOATZEL", 37, "SITRUS_BERRY", ["AQUA_JET", "CRUNCH", "ICE_FANG", "BRINE"]),
    ],
    "leader_byron": [
        ("MAGNETON", 37, None, ["FLASH_CANNON", "THUNDERBOLT", "TRI_ATTACK", "METAL_SOUND"]),
        ("STEELIX", 38, None, ["EARTHQUAKE", "ROCK_SLIDE", "ICE_FANG", "SANDSTORM"]),
        ("SCIZOR", 39, None, ["X_SCISSOR", "IRON_HEAD", "NIGHT_SLASH", "QUICK_ATTACK"]),
        ("BASTIODON", 41, "SITRUS_BERRY", ["METAL_BURST", "ROCK_TOMB", "IRON_DEFENSE", "ROAR"]),
    ],
    "leader_candice": [
        ("WEAVILE", 40, None, ["ICE_PUNCH", "NIGHT_SLASH", "FAKE_OUT", "AERIAL_ACE"]),
        ("PILOSWINE", 40, None, ["AVALANCHE", "EARTHQUAKE", "STONE_EDGE", "HAIL"]),
        ("ABOMASNOW", 42, None, ["AVALANCHE", "WOOD_HAMMER", "WATER_PULSE", "FOCUS_BLAST"]),
        ("FROSLASS", 44, "SITRUS_BERRY", ["BLIZZARD", "SHADOW_BALL", "DOUBLE_TEAM", "PSYCHIC"]),
    ],
    "leader_volkner": [
        ("LANTURN", 46, None, ["SURF", "DISCHARGE", "THUNDER_WAVE", "SIGNAL_BEAM"]),
        ("JOLTEON", 46, None, ["THUNDERBOLT", "SHADOW_BALL", "QUICK_ATTACK", "THUNDER_WAVE"]),
        ("RAICHU", 47, None, ["THUNDERBOLT", "METAL_RAY", "FOCUS_BLAST", "SIGNAL_BEAM"]),
        ("LUXRAY", 48, None, ["THUNDER_FANG", "CRUNCH", "ICE_FANG", "FIRE_FANG"]),
        ("ELECTIVIRE", 50, "SITRUS_BERRY", ["STATIC_STRIKE", "CROSS_CHOP", "ICE_PUNCH", "FIRE_PUNCH"]),
    ],
}

# moves=None -> filled from the deterministic proposal in moveset_lib (reviewed/overridden in curated_sets.py).
SITRUS = "SITRUS_BERRY"

GALACTIC = {
    "commander_mars_valley_windworks": [("ZUBAT", 15, None, None), ("PURUGLY", 17, "ORAN_BERRY", None)],
    "commander_jupiter_team_galactic_eterna_building": [("ZUBAT", 21, None, None), ("SKUNTANK", 23, SITRUS, None)],
    "commander_saturn_valor_cavern": [("GOLBAT", 38, None, None), ("BRONZOR", 38, None, None), ("TOXICROAK", 40, SITRUS, None)],
    "commander_mars_lake_verity": [("GOLBAT", 38, None, None), ("BRONZONG", 38, None, None), ("PURUGLY", 40, SITRUS, None)],
    "commander_saturn_galactic_hq": [("CROBAT", 42, None, None), ("BRONZONG", 42, None, None), ("TOXICROAK", 44, SITRUS, None)],
    "galactic_boss_cyrus_galactic_hq": [("WEAVILE", 44, None, None), ("CROBAT", 44, None, None), ("HOUNDOOM", 45, None, None),
                                         ("HONCHKROW", 46, SITRUS, None)],
    "galactic_boss_cyrus_distortion_world": [("HOUNDOOM", 45, None, None), ("CROBAT", 46, None, None), ("GYARADOS", 46, None, None),
                                              ("HONCHKROW", 47, None, None), ("WEAVILE", 48, SITRUS, None)],
    "commander_mars_spear_pillar": [("BRONZONG", 44, None, None), ("CROBAT", 44, None, None), ("PURUGLY", 46, SITRUS, None)],
    "commander_jupiter_spear_pillar": [("BRONZONG", 44, None, None), ("CROBAT", 44, None, None), ("SKUNTANK", 46, SITRUS, None)],
    "commander_mars_stark_mountain": [("BRONZONG", 58, None, None), ("CROBAT", 58, None, None), ("PURUGLY", 60, SITRUS, None)],
    "commander_jupiter_stark_mountain": [("BRONZONG", 58, None, None), ("CROBAT", 58, None, None), ("SKUNTANK", 60, SITRUS, None)],
}

ELITE = {
    "elite_four_aaron": [("YANMEGA", 49, None, None), ("SCIZOR", 49, None, None), ("VESPIQUEN", 50, None, None),
                         ("HERACROSS", 51, None, None), ("DRAPION", 53, SITRUS, None)],
    "elite_four_bertha": [("WHISCASH", 50, None, None), ("HIPPOWDON", 52, None, None), ("GOLEM", 52, None, None),
                          ("GLISCOR", 53, None, None), ("RHYPERIOR", 55, SITRUS, None)],
    "elite_four_flint": [("HOUNDOOM", 52, None, None), ("RAPIDASH", 53, None, None), ("FLAREON", 55, None, None),
                         ("INFERNAPE", 55, None, None), ("MAGMORTAR", 57, SITRUS, None)],
    "elite_four_lucian": [("MR_MIME", 53, None, None), ("BRONZONG", 54, None, None), ("ESPEON", 55, None, None),
                          ("ALAKAZAM", 56, None, None), ("GALLADE", 59, SITRUS, None)],
    "champion_cynthia": [("SPIRITOMB", 58, None, None), ("ROSERADE", 58, None, None), ("TOGEKISS", 60, None, None),
                         ("LUCARIO", 60, None, None), ("MILOTIC", 58, None, None), ("GARCHOMP", 62, SITRUS, None)],
}

# Rematch teams: species per spec; levels reuse the current slot levels (spec: tuned later against postgame EXP/economy).
REMATCH_SPECIES = {
    "leader_roark_rematch": ["AERODACTYL", "KABUTOPS", "OMASTAR", "RHYPERIOR", "RAMPARDOS"],
    "leader_gardenia_rematch": ["JUMPLUFF", "LUDICOLO", "BRELOOM", "CHERRIM", "ROSERADE"],
    "leader_maylene_rematch": ["HITMONTOP", "MEDICHAM", "HERACROSS", "TOXICROAK", "LUCARIO"],
    "leader_wake_rematch": ["KINGDRA", "GYARADOS", "QUAGSIRE", "FERALIGATR", "FLOATZEL"],
    "leader_fantina_rematch": ["GENGAR", "BANETTE", "SPIRITOMB", "DUSKNOIR", "MISMAGIUS"],
    "leader_byron_rematch": ["MAGNEZONE", "STEELIX", "SCIZOR", "PROBOPASS", "BASTIODON"],
    "leader_candice_rematch": ["WEAVILE", "MAMOSWINE", "GLALIE", "ABOMASNOW", "FROSLASS"],
    "leader_volkner_rematch": ["LANTURN", "JOLTEON", "RAICHU", "LUXRAY", "ELECTIVIRE"],
    "elite_four_aaron_rematch": ["YANMEGA", "SCIZOR", "HERACROSS", "PINSIR", "VESPIQUEN"],
    "elite_four_bertha_rematch": ["WHISCASH", "HIPPOWDON", "GOLEM", "GLISCOR", "RHYPERIOR"],
    "elite_four_flint_rematch": ["HOUNDOOM", "ARCANINE", "RAPIDASH", "INFERNAPE", "MAGMORTAR"],
    "elite_four_lucian_rematch": ["SLOWKING", "BRONZONG", "ESPEON", "ALAKAZAM", "GALLADE"],
    "champion_cynthia_rematch": ["SPIRITOMB", "ROSERADE", "TOGEKISS", "LUCARIO", "MILOTIC", "GARCHOMP"],
}
