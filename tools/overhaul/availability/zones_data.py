"""Zone/band metadata for every encounter file (authored maps come from the plan; the rest are listed here)."""

BAND_GATES = {
    "E0": "start of game through the Oreburgh Gym (badge 1)",
    "E1": "after Oreburgh Gym through the Eterna Gym (badge 2)",
    "M1": "after Eterna Gym through the Pastoria Gym (badge 5); Surf = HM03 (Celestic Town Cave), Good Rod = Route 209",
    "M2": "after Pastoria Gym through the Canalave Gym (badge 6)",
    "L1": "after Canalave Gym through the Snowpoint Gym (badge 7)",
    "L2": "after Snowpoint Gym through the Sunyshore Gym (badge 8)",
    "P0": "after badge 8 through the Pokemon League (Victory Road)",
    "P1": "after the Hall of Fame (Super Rod = Fight Area fisherman)",
}

# Maps this work does NOT retable (their land/water tables are untouched except for the global dual-slot neutralisation).
# name: (zone, band, rationale)
UNMODIFIED = {
    "twinleaf_town": ("START", "E0", "Old Rod magikarp-only early water; unchanged"),
    "resort_area": ("POST", "P1", "postgame island resort"),
    "pokemon_league": ("POST", "P0", "League-front water; evolved ecology retained"),
    "sendoff_spring": ("POST", "P1", "postgame"),
    "route_224": ("POST", "P1", "postgame evolved ecology"), "route_225": ("POST", "P1", "postgame evolved ecology"),
    "route_226": ("POST", "P1", "postgame evolved ecology"), "route_227": ("POST", "P1", "postgame evolved ecology"),
    "route_228": ("POST", "P1", "postgame evolved ecology"), "route_229": ("POST", "P1", "postgame evolved ecology"),
    "route_230": ("POST", "P1", "postgame evolved ecology"),
    "stark_mountain_outside": ("POST", "P1", "postgame"), "stark_mountain_room_1": ("POST", "P1", "postgame"),
    "stark_mountain_room_2": ("POST", "P1", "postgame"),
    "snowpoint_temple_1f": ("POST", "P1", "postgame temple"), "snowpoint_temple_b1f": ("POST", "P1", "postgame temple"),
    "snowpoint_temple_b2f": ("POST", "P1", "postgame temple"), "snowpoint_temple_b3f": ("POST", "P1", "postgame temple"),
    "snowpoint_temple_b4f": ("POST", "P1", "postgame temple"), "snowpoint_temple_b5f": ("POST", "P1", "postgame temple"),
    "route_209_lost_tower_1f": ("HEARTH", "M1", "ghost tower; Gastly/Zubat/Duskull families already placed elsewhere"),
    "route_209_lost_tower_2f": ("HEARTH", "M1", "ghost tower"), "route_209_lost_tower_3f": ("HEARTH", "M1", "ghost tower"),
    "route_209_lost_tower_4f": ("HEARTH", "M1", "ghost tower"), "route_209_lost_tower_5f": ("HEARTH", "M1", "ghost tower"),
    "great_marsh_lookout": ("MARSH", "M1", "binocular / daily arrays (special_systems.json)"),
    "honey_tree": ("FOREST", "E1", "Honey Tree tables (special_systems.json)"),
}
for _n in ("solaceon_ruins_maniac_tunnel_room", "solaceon_ruins_room_1_northwest_dead_end",
           "solaceon_ruins_room_1_southeast_dead_end", "solaceon_ruins_room_2",
           "solaceon_ruins_room_2_northeast_dead_end", "solaceon_ruins_room_2_southeast_dead_end",
           "solaceon_ruins_room_3", "solaceon_ruins_room_3_northwest_dead_end",
           "solaceon_ruins_room_3_southwest_dead_end", "solaceon_ruins_room_4",
           "solaceon_ruins_room_4_southeast_dead_end", "solaceon_ruins_room_5",
           "solaceon_ruins_room_5_southeast_deadend", "solaceon_ruins_room_5_southwest_dead_end",
           "solaceon_ruins_room_6", "solaceon_ruins_room_6_northwest_dead_end",
           "solaceon_ruins_room_6_southeast_dead_end", "solaceon_ruins_room_7"):
    UNMODIFIED[_n] = ("HEARTH", "M1", "Unknown-only ruin rooms; Unown family already satisfied")
for _i in range(533, 558):
    UNMODIFIED[f"unknown_{_i}"] = ("POST", "P1", "Turnback Cave pillar room (postgame)")
for _n in ("turnback_cave_entrance", "turnback_cave_giratina_room", "turnback_cave_pillar_room"):
    UNMODIFIED[_n] = ("POST", "P1", "Turnback Cave (postgame)")
for _p in (1, 2, 3):
    for _r in range(1, 7):
        UNMODIFIED[f"turnback_cave_pillar_{_p}_room_{_r}"] = ("POST", "P1", "Turnback Cave (postgame)")

# Habitat adjacency used for the 'share no more than half their families' density rule: (a, b, continuous)
ADJACENT = [
    ("route_201", "route_202", False), ("route_202", "route_203", False), ("route_203", "oreburgh_gate_1f", False),
    ("oreburgh_gate_1f", "oreburgh_gate_b1f", True), ("oreburgh_mine_b1f", "oreburgh_mine_b2f", True),
    ("route_204_south", "ravaged_path", False), ("route_204_south", "route_204_north", True),
    ("route_204_north", "route_205_south", False), ("route_205_south", "route_205_north", True),
    ("route_205_south", "valley_windworks_outside", False), ("route_205_south", "eterna_forest", False),
    ("route_205_north", "eterna_forest", False), ("route_206", "route_207", False),
    ("route_206", "wayward_cave_1f", False), ("wayward_cave_1f", "wayward_cave_b1f", True),
    ("route_208", "route_209", False), ("route_209", "route_210_south", False),
    ("route_210_south", "route_210_north", True), ("route_210_south", "route_215", False),
    ("route_211_west", "route_211_east", True), ("route_212_north", "route_212_south", True),
    ("route_212_south", "route_213", False), ("route_213", "valor_lakefront", False),
    ("route_218", "route_221", False), ("route_216", "route_217", True), ("route_217", "acuity_lakefront", True),
    ("acuity_lakefront", "lake_acuity", True), ("route_222", "lake_valor", False),
    ("great_marsh_1", "great_marsh_3", True), ("great_marsh_3", "great_marsh_5", True),
    ("mt_coronet_2f", "mt_coronet_3f", True), ("mt_coronet_3f", "mt_coronet_4f_rooms_1_and_2", True),
    ("mt_coronet_5f", "mt_coronet_6f", True), ("iron_island_1f", "iron_island_b1f_left_room", True),
    ("iron_island_b1f_left_room", "iron_island_b2f_left_room", True), ("iron_island_b2f_left_room", "iron_island_b3f", True),
    ("victory_road_1f", "victory_road_1f_room_1", True), ("victory_road_1f", "victory_road_2f", True),
    ("old_chateau", "old_chateau_back_west_room", True),
]

# Land tables that intentionally exceed the 6-8 family target (reason recorded in the zones manifest).
DENSITY_NOTES = {}
