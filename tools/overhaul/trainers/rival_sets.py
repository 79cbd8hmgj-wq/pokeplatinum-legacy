"""Rival (all starter branches) move sets and evolution-timing fixes per fight group.

Species lines per branch are preserved from current main (starter-counter structure); only
  * evolution timing (species whose level-evolution threshold is reached) and
  * moves / held items
change.  Branch files: rival_<fight>_<player starter>; the rival owns the next starter in the cycle.
"""
M = lambda *a: list(a)  # noqa: E731

FIGHT_GROUP = {
    "rival_route_209": "r209", "rival_pastoria_city": "pastoria", "rival_canalave_city": "canalave",
    "rival_pokemon_league": "league", "rival_fight_area": "league",
    "rival_survival_area_1": "league", "rival_survival_area_2": "league", "rival_survival_area_unused": "league",
}
BRANCHES = ("turtwig", "chimchar", "piplup")
FIGHTS = tuple(FIGHT_GROUP)
# Pastoria (Lv32-36): species whose natural level-evolution has been reached evolve ("evolution timing").
EVOLVE = {"pastoria": {"STARAVIA": "STARAPTOR", "BUIZEL": "FLOATZEL", "PRINPLUP": "EMPOLEON",
                       "MONFERNO": "INFERNAPE", "GROTLE": "TORTERRA"}}
STARTER_FINAL = {"INFERNAPE", "EMPOLEON", "TORTERRA"}
STARTER_LINES = {"MONFERNO", "PRINPLUP", "GROTLE", "INFERNAPE", "EMPOLEON", "TORTERRA"}

SETS = {
    "r209": {
        "STARAVIA": M("WING_ATTACK", "QUICK_ATTACK", "ENDEAVOR", "DOUBLE_TEAM"),
        "BUIZEL": M("AQUA_JET", "QUICK_ATTACK", "PURSUIT", "WATER_GUN"),
        "ROSELIA": M("MEGA_DRAIN", "MAGICAL_LEAF", "LEECH_SEED", "STUN_SPORE"),
        "MONFERNO": M("FLAME_WHEEL", "MACH_PUNCH", "FURY_SWIPES", "LEER"),
        "PONYTA": M("EMBER", "STOMP", "FLAME_WHEEL", "GROWL"),
        "PRINPLUP": M("BUBBLE_BEAM", "METAL_CLAW", "WATER_PULSE", "GROWL"),
        "GROTLE": M("RAZOR_LEAF", "BITE", "MEGA_DRAIN", "WITHDRAW"),
    },
    "pastoria": {
        "STARAPTOR": M("AERIAL_ACE", "QUICK_ATTACK", "TAKE_DOWN", "DOUBLE_TEAM"),
        "FLOATZEL": M("AQUA_JET", "WATER_PULSE", "QUICK_ATTACK", "PURSUIT"),
        "ROSELIA": M("MEGA_DRAIN", "MAGICAL_LEAF", "LEECH_SEED", "TOXIC_SPIKES"),
        "INFERNAPE": M("FLAME_WHEEL", "MACH_PUNCH", "BRICK_BREAK", "AERIAL_ACE"),
        "PONYTA": M("FLAME_WHEEL", "STOMP", "TAKE_DOWN", "TAIL_WHIP"),
        "EMPOLEON": M("WATER_PULSE", "METAL_CLAW", "AERIAL_ACE", "GROWL"),
        "TORTERRA": M("RAZOR_LEAF", "BITE", "MEGA_DRAIN", "LEECH_SEED"),
    },
    "canalave": {
        "STARAPTOR": M("AERIAL_ACE", "QUICK_ATTACK", "CLOSE_COMBAT", "DOUBLE_TEAM"),
        "FLOATZEL": M("AQUA_JET", "WATER_PULSE", "CRUNCH", "QUICK_ATTACK"),
        "HERACROSS": M("BRICK_BREAK", "AERIAL_ACE", "NIGHT_SLASH", "HORN_ATTACK"),
        "ROSERADE": M("GIGA_DRAIN", "TOXIC_SPIKES", "LEECH_SEED", "SHADOW_BALL"),
        "INFERNAPE": M("FLAMETHROWER", "MACH_PUNCH", "BRICK_BREAK", "AERIAL_ACE"),
        "RAPIDASH": M("FIRE_SPIN", "TAKE_DOWN", "STOMP", "WILL_O_WISP"),
        "EMPOLEON": M("SURF", "METAL_CLAW", "AERIAL_ACE", "ICE_BEAM"),
        "TORTERRA": M("RAZOR_LEAF", "BITE", "EARTHQUAKE", "LEECH_SEED"),
    },
    "league": {
        "STARAPTOR": M("CLOSE_COMBAT", "BRAVE_BIRD", "QUICK_ATTACK", "U_TURN"),
        "FLOATZEL": M("AQUA_JET", "CRUNCH", "ICE_FANG", "BRICK_BREAK"),
        "HERACROSS": M("CLOSE_COMBAT", "ROCK_SLIDE", "NIGHT_SLASH", "AERIAL_ACE"),
        "ROSERADE": M("GIGA_DRAIN", "SLUDGE_BOMB", "SHADOW_BALL", "TOXIC"),
        "RAPIDASH": M("FLARE_BLITZ", "WILL_O_WISP", "BOUNCE", "SUNNY_DAY"),
        "SNORLAX": M("BODY_SLAM", "CRUNCH", "EARTHQUAKE", "REST"),
        "INFERNAPE": M("FLAMETHROWER", "CLOSE_COMBAT", "SHADOW_CLAW", "AERIAL_ACE"),
        "EMPOLEON": M("SURF", "FLASH_CANNON", "ICE_BEAM", "AERIAL_ACE"),
        "TORTERRA": M("WOOD_HAMMER", "EARTHQUAKE", "CRUNCH", "STONE_EDGE"),
    },
}
