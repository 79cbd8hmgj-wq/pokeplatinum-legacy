#!/usr/bin/env python3
"""Generate the D5 Legendary/Mythical event manifests.

The manifests under docs/overhaul/implementation/events/ are the canonical machine-readable record of
how every Legendary/Mythical species (#001-#493) is acquired in a single save. This script holds the
data; `validate_legendary_availability.py` re-derives every claim from live source.

Run:  python3 tools/overhaul/events/build_manifests.py
"""
from __future__ import annotations

import json

from lib import EVENTS_DIR

BASE_COMMIT = "08092189cd4ea322a5b1b788a559a1ea2fbcbfd9"
AUTH = [
    "docs/overhaul/events/LEGENDARY_MYTHICAL_SPEC.md",
    "docs/overhaul/events/LEGENDARY_MYTHICAL_IMPLEMENTATION_PLAN.md",
    "docs/overhaul/AVAILABILITY_ARCHITECTURE.md",
]
S = "res/field/scripts/"

# Every Legendary/Mythical species #001-#493 (matches the 35 RESERVED_LATER_PHASE families).
SPECIES_IDS = {
    "ARTICUNO": 144, "ZAPDOS": 145, "MOLTRES": 146, "MEWTWO": 150, "MEW": 151,
    "RAIKOU": 243, "ENTEI": 244, "SUICUNE": 245, "LUGIA": 249, "HO_OH": 250, "CELEBI": 251,
    "REGIROCK": 377, "REGICE": 378, "REGISTEEL": 379, "LATIAS": 380, "LATIOS": 381,
    "KYOGRE": 382, "GROUDON": 383, "RAYQUAZA": 384, "JIRACHI": 385, "DEOXYS": 386,
    "UXIE": 480, "MESPRIT": 481, "AZELF": 482, "DIALGA": 483, "PALKIA": 484, "HEATRAN": 485,
    "REGIGIGAS": 486, "GIRATINA": 487, "CRESSELIA": 488, "PHIONE": 489, "MANAPHY": 490,
    "DARKRAI": 491, "SHAYMIN": 492, "ARCEUS": 493,
}

STATUS = {
    "source": "IMPLEMENTED",
    "structural_validator": "validate_legendary_availability.py",
    "runtime": "PENDING (not VERIFIED)",
}


def entry(species, cls, system, level, rate, vanilla, target, cadence, capture_flag, retry, removed, source, **extra):
    d = {
        "species": f"SPECIES_{species}",
        "dex": SPECIES_IDS[species],
        "acquisition_class": cls,
        "map_system": system,
        "level": level,
        "rate": rate,
        "vanilla_gates": vanilla,
        "target_gates": target,
        "one_time_vs_renewable": cadence,
        "capture_flag": capture_flag,
        "retry_behavior": retry,
        "external_dependency_removed": removed,
        "source_path": source,
        "validation_status": dict(STATUS),
    }
    d.update(extra)
    return d


HOF = "FLAG_GAME_COMPLETED"

# --------------------------------------------------------------------------------------------------
# native_legendary_events.json
# --------------------------------------------------------------------------------------------------
native = []

native.append(entry(
    "UXIE", "NATIVE_STATIC", "Acuity Cavern (object)", "50", "static",
    ["Sandgem Lab story event clears FLAG_HIDE_ACUITY_CAVERN_UXIE"],
    ["unchanged (Sandgem Lab event / Hall of Fame re-show)"],
    "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_UXIE",
    "uncaught (defeat/flee) and blackout branches clear FLAG_HIDE_ACUITY_CAVERN_UXIE so the object returns on map re-entry; FLAG_CAUGHT_UXIE only set on capture",
    "none (vanilla bug: OnLoad hid the object after any battle until the next Hall of Fame)",
    S + "scripts_acuity_cavern.s",
    script={"file": S + "scripts_acuity_cavern.s", "entry": "AcuityCavern_Uxie", "battle": "StartLegendaryBattle SPECIES_UXIE, 50"},
    retry_actions=["ClearFlag FLAG_HIDE_ACUITY_CAVERN_UXIE"],
))
native.append(entry(
    "AZELF", "NATIVE_STATIC", "Valor Cavern (object)", "50", "static",
    ["Sandgem Lab story event clears FLAG_HIDE_VALOR_CAVERN_AZELF"],
    ["unchanged"], "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_AZELF",
    "uncaught and blackout branches clear FLAG_HIDE_VALOR_CAVERN_AZELF; FLAG_CAUGHT_AZELF only set on capture",
    "none (vanilla bug: permanent hide after any battle until next Hall of Fame)",
    S + "scripts_valor_cavern.s",
    script={"file": S + "scripts_valor_cavern.s", "entry": "ValorCavern_Azelf", "battle": "StartLegendaryBattle SPECIES_AZELF, 50"},
    retry_actions=["ClearFlag FLAG_HIDE_VALOR_CAVERN_AZELF"],
))
native.append(entry(
    "MESPRIT", "NATIVE_ROAMER", "Verity Cavern activation + Sinnoh roaming", "50", "roamer",
    ["Verity Cavern interaction activates ROAMING_SLOT_MESPRIT"],
    ["unchanged"], "ONE_TIME_UNTIL_CAPTURED", "VAR_ROAMING_MESPRIT_STATE == ROAMER_STATE_CAPTURED",
    "ROAMER_STATE_DEFEATED is reset on next Verity Cavern entry (VerityCavern_ResetDefeatedMesprit: show object, state RESET) and the cavern interaction re-activates the roamer; flee keeps the roamer alive; Hall-of-Fame reset retained",
    "none (vanilla reset only at the next Hall of Fame)",
    S + "scripts_verity_cavern.s",
    reset_script=[{"file": S + "scripts_verity_cavern.s", "label": "VerityCavern_OnTransition",
                   "requires": ["CallIfEq VAR_ROAMING_MESPRIT_STATE, ROAMER_STATE_DEFEATED, VerityCavern_ResetDefeatedMesprit"]},
                  {"file": S + "scripts_verity_cavern.s", "label": "VerityCavern_ResetDefeatedMesprit",
                   "requires": ["ClearFlag FLAG_HIDE_VERITY_CAVERN_MESPRIT", "SetVar VAR_ROAMING_MESPRIT_STATE, ROAMER_STATE_RESET"]}],
))
native.append(entry(
    "CRESSELIA", "NATIVE_ROAMER", "Fullmoon Island Forest activation (Lunar Wing) + Sinnoh roaming", "50", "roamer",
    ["Fullmoon Island Forest interaction activates ROAMING_SLOT_CRESSELIA"],
    ["unchanged"], "ONE_TIME_UNTIL_CAPTURED", "VAR_ROAMING_CRESSELIA_STATE == ROAMER_STATE_CAPTURED",
    "ROAMER_STATE_DEFEATED is reset on next Fullmoon Island Forest entry (new init OnTransition) and the interaction re-activates the roamer; Lunar Wing is only offered on first activation",
    "none (vanilla reset only at the next Hall of Fame)",
    S + "scripts_fullmoon_island_forest.s",
    reset_script=[{"file": S + "scripts_fullmoon_island_forest.s", "label": "FullmoonIslandForest_Dummy1",
                   "requires": ["CallIfEq VAR_ROAMING_CRESSELIA_STATE, ROAMER_STATE_DEFEATED, FullmoonIslandForest_ResetDefeatedCresselia"]},
                  {"file": S + "scripts_fullmoon_island_forest.s", "label": "FullmoonIslandForest_ResetDefeatedCresselia",
                   "requires": ["ClearFlag FLAG_HIDE_FULLMOON_ISLAND_FOREST_CRESSELIA", "SetVar VAR_ROAMING_CRESSELIA_STATE, ROAMER_STATE_RESET"]}],
))
native.append(entry(
    "GIRATINA", "NATIVE_STATIC", "Distortion World story battle + Turnback Cave Giratina room", "47", "static",
    ["story battle in Distortion World; Turnback Cave room object re-shown at Hall of Fame"],
    ["unchanged story; Turnback Cave fallback retry-safe"],
    "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_GIRATINA",
    "Turnback Cave uncaught and blackout branches clear FLAG_HIDE_TURNBACK_CAVE_GIRATINA_ROOM_GIRATINA; capture sets FLAG_CAUGHT_GIRATINA",
    "none (vanilla bug: permanent hide after an uncaught Turnback Cave battle)",
    S + "scripts_turnback_cave_giratina_room.s",
    script={"file": S + "scripts_turnback_cave_giratina_room.s", "entry": "TurnbackCaveGiratinaRoom_Giratina", "battle": "StartLegendaryBattle SPECIES_GIRATINA, 47"},
    retry_actions=["ClearFlag FLAG_HIDE_TURNBACK_CAVE_GIRATINA_ROOM_GIRATINA"],
))
for sp, lbl, N in (("DIALGA", "Dialga", "Dialga"), ("PALKIA", "Palkia", "Palkia")):
    native.append(entry(
        sp, "NATIVE_STATIC", f"Spear Pillar {lbl} rift (postgame)", "70", "static",
        ["VAR_SPEAR_PILLAR_%s_STATE set to 1 after any non-loss battle" % sp, f"{'Adamant' if sp == 'DIALGA' else 'Lustrous'} Orb warp"],
        ["VAR_SPEAR_PILLAR_%s_STATE set only on capture" % sp], "ONE_TIME_UNTIL_CAPTURED", f"FLAG_CAUGHT_{sp}",
        f"state var and FLAG_CAUGHT_{sp} are set together only in the captured branch; defeat/flee/blackout leaves the rift challengeable",
        "none (vanilla bug: state set to 1 before the capture check consumed the rift until next Hall of Fame)",
        S + f"scripts_spear_pillar_{lbl.lower()}.s",
        script={"file": S + f"scripts_spear_pillar_{lbl.lower()}.s", "entry": f"SpearPillar{lbl}_Rift", "battle": f"StartLegendaryBattle SPECIES_{sp}, 70"},
        consumed_markers=[f"VAR_SPEAR_PILLAR_{sp}_STATE"],
    ))
native.append(entry(
    "HEATRAN", "NATIVE_STATIC", "Stark Mountain room 3 (object, postgame)", "50", "static",
    [HOF, "National Dex", "FLAG_TALKED_TO_BATTLEGROUND_BUCK", "VAR_STARK_MOUNTAIN_ROOM_3_STATE == 1"],
    ["unchanged"], "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_HEATRAN",
    "uncaught branch resets VAR_STARK_MOUNTAIN_ROOM_3_STATE to 1 (the show condition); blackout already sets it; capture sets FLAG_CAUGHT_HEATRAN",
    "none (vanilla bug: state stayed 2 after an uncaught battle)",
    S + "scripts_stark_mountain_room_3.s",
    script={"file": S + "scripts_stark_mountain_room_3.s", "entry": "StarkMountainRoom3_Heatran", "battle": "StartLegendaryBattle SPECIES_HEATRAN, 50"},
    retry_actions=["SetVar VAR_STARK_MOUNTAIN_ROOM_3_STATE, 1"],
    reset_script={"file": S + "scripts_stark_mountain_room_3.s", "label": "StarkMountainRoom3_TryHideHeatran",
                  "requires": ["GoToIfSet FLAG_CAUGHT_HEATRAN", "ClearFlag FLAG_HIDE_STARK_MOUNTAIN_ROOM_3_HEATRAN"]},
))
native.append(entry(
    "REGIGIGAS", "NATIVE_STATIC", "Snowpoint Temple B5F (object)", "1", "static",
    [HOF + " (object re-shown by Hall of Fame script only when National Dex was already on)", "all three Regis in party (native Titan-party check)"],
    [HOF, "all three Regis in party (native Titan-party check, unchanged)"], "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_REGIGIGAS",
    "new init OnTransition shows the object after the Hall of Fame until FLAG_CAUGHT_REGIGIGAS; uncaught and blackout branches clear FLAG_HIDE_SNOWPOINT_TEMPLE_B5F_REGIGIGAS",
    "event Regigigas is not needed here (it was needed by the Regi statues, removed below)",
    S + "scripts_snowpoint_temple_b5f.s",
    script={"file": S + "scripts_snowpoint_temple_b5f.s", "entry": "SnowpointTempleB5F_Regigigas", "battle": "StartLegendaryBattle SPECIES_REGIGIGAS, 1"},
    retry_actions=["ClearFlag FLAG_HIDE_SNOWPOINT_TEMPLE_B5F_REGIGIGAS"],
    internal_prerequisites=["SPECIES_REGIROCK", "SPECIES_REGICE", "SPECIES_REGISTEEL"],
    hall_of_fame_required=True,
    reset_script={"file": S + "scripts_snowpoint_temple_b5f.s", "label": "SnowpointTempleB5F_OnTransition",
                  "requires": ["GoToIfSet FLAG_CAUGHT_REGIGIGAS", "GoToIfUnset FLAG_GAME_COMPLETED", "ClearFlag FLAG_HIDE_SNOWPOINT_TEMPLE_B5F_REGIGIGAS"]},
))
for sp, ruin, var, var_ns in (("REGIROCK", "Rock Peak Ruins", "VAR_ROCK_PEAK_RUINS_STATE", "rock_peak"),
                                ("REGICE", "Iceberg Ruins", "VAR_ICEBERG_RUINS_STATE", "iceberg"),
                                ("REGISTEEL", "Iron Ruins", "VAR_IRON_RUINS_STATE", "iron")):
    label = {"REGIROCK": "RockPeakRuins", "REGICE": "IcebergRuins", "REGISTEEL": "IronRuins"}[sp]
    native.append(entry(
        sp, "NATIVE_RUIN", f"{ruin} (statue puzzle)", "30", "static",
        [HOF, "event Regigigas in party (CheckPartyHasFatefulEncounterRegigigas)", "braille dot puzzle"],
        [HOF, "braille dot puzzle (normal map accessibility)"], "ONE_TIME_UNTIL_CAPTURED", f"{var} == RUINS_STATE_CAUGHT_REGI",
        f"uncaught branch resets {var} to 0 and the OnTransition resets every non-captured state, so leaving and re-entering restores the puzzle; only capture sets RUINS_STATE_CAUGHT_REGI",
        "event-distributed Regigigas requirement removed from the statue",
        S + f"scripts_{var_ns}_ruins.s",
        script={"file": S + f"scripts_{var_ns}_ruins.s", "entry": f"{label}_EncounterRegi" + sp[4:].lower(), "battle": f"StartLegendaryBattle SPECIES_{sp}, 30"},
        consumed_markers=[f"{var}, RUINS_STATE_DID_NOT_CATCH_REGI"],
        hall_of_fame_required=True,
        reset_script=[{"file": S + f"scripts_{var_ns}_ruins.s", "label": f"{label}_OnTransition",
                       "requires": [f"GoToIfNe {var}, RUINS_STATE_CAUGHT_REGI"]},
                      {"file": S + f"scripts_{var_ns}_ruins.s", "label": f"{label}_ResetState",
                       "requires": [f"SetVar {var}, 0"]}],
    ))
native.append(entry(
    "DARKRAI", "RESTORED_EVENT", "Canalave Harbor Inn -> Newmoon Island Forest", "50", "static",
    [HOF, "National Dex", "ITEM_MEMBER_CARD (distribution-only)", "DISTRIBUTION_EVENT_DARKRAI", "FLAG_WOKE_UP_CANALAVE_CITY_SAILOR_ELDRITCH_HOUSE_LITTLE_BOY"],
    [HOF, "National Dex", "ITEM_MEMBER_CARD (given by Sailor Eldritch in Canalave City after the Lunar Wing child sequence)", "FLAG_WOKE_UP_CANALAVE_CITY_SAILOR_ELDRITCH_HOUSE_LITTLE_BOY"],
    "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_DARKRAI",
    "FLAG_CAUGHT_DARKRAI only after capture; OnTransition re-shows Darkrai on every Newmoon entry until caught; Harbor Inn state resets to 0 via Canalave OnTransition",
    "DISTRIBUTION_EVENT_DARKRAI check removed from Canalave City, Harbor Inn and Newmoon Island Forest scripts",
    S + "scripts_newmoon_island_forest.s",
    script={"file": S + "scripts_newmoon_island_forest.s", "entry": "NewmoonIslandForest_Darkrai", "battle": "StartLegendaryBattle SPECIES_DARKRAI, 50"},
    hall_of_fame_required=True,
    unlock_source={"file": S + "scripts_canalave_city.s", "label": "CanalaveCity_SailorEldritchGiveMemberCard", "item": "ITEM_MEMBER_CARD"},
    reset_script={"file": S + "scripts_newmoon_island_forest.s", "label": "NewmoonIslandForest_OnTransition",
                  "requires": ["GoToIfSet FLAG_CAUGHT_DARKRAI", "ClearFlag FLAG_HIDE_NEWMOON_ISLAND_FOREST_DARKRAI", "GoToIfUnset FLAG_GAME_COMPLETED"]},
))
native.append(entry(
    "SHAYMIN", "RESTORED_EVENT", "Route 224 (Oak, tablet) -> Seabreak Path -> Flower Paradise", "30", "static",
    [HOF, "National Dex", "ITEM_OAKS_LETTER (distribution-only)", "DISTRIBUTION_EVENT_SHAYMIN", "VAR_SHAYMIN_EVENT_STATE set by distribution"],
    [HOF, "National Dex", "Oak (Route 224) gives ITEM_OAKS_LETTER in-game and starts VAR_SHAYMIN_EVENT_STATE"],
    "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_SHAYMIN",
    "FLAG_CAUGHT_SHAYMIN only after capture; Flower Paradise OnTransition re-shows Shaymin on every entry until caught; uncaught/blackout branches also clear FLAG_HIDE_FLOWER_PARADISE_SHAYMIN",
    "DISTRIBUTION_EVENT_SHAYMIN check removed from Route 224 and Flower Paradise scripts",
    S + "scripts_flower_paradise.s",
    script={"file": S + "scripts_flower_paradise.s", "entry": "FlowerParadise_Shaymin", "battle": "StartFatefulEncounter SPECIES_SHAYMIN, 30"},
    hall_of_fame_required=True,
    unlock_source={"file": S + "scripts_route_224.s", "label": "Route224_GiveOaksLetter", "item": "ITEM_OAKS_LETTER"},
    retry_actions=["ClearFlag FLAG_HIDE_FLOWER_PARADISE_SHAYMIN"],
    reset_script={"file": S + "scripts_flower_paradise.s", "label": "FlowerParadise_OnTransition",
                  "requires": ["GoToIfSet FLAG_CAUGHT_SHAYMIN", "ClearFlag FLAG_HIDE_FLOWER_PARADISE_SHAYMIN", "GoToIfUnset FLAG_GAME_COMPLETED"]},
))
native.append(entry(
    "ARCEUS", "RESTORED_EVENT", "Veilstone Store B1F (Prof. Rowan, Azure Flute) -> Spear Pillar -> Hall of Origin", "80", "static",
    [HOF, "National Dex", "ITEM_AZURE_FLUTE (distribution-only)", "DISTRIBUTION_EVENT_ARCEUS"],
    [HOF, "caught-Pokédex check for every species #001-#492 (forms not counted; Arceus excluded)", "Rowan gives ITEM_AZURE_FLUTE only after the check"],
    "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_ARCEUS",
    "FLAG_CAUGHT_ARCEUS only after capture; Hall of Origin OnTransition re-shows Arceus until caught; DefeatedArceus clears FLAG_HIDE_HALL_OF_ORIGIN_ARCEUS",
    "DISTRIBUTION_EVENT_ARCEUS removed from Hall of Origin, Spear Pillar (normal/Dialga/Palkia), the common Azure Flute script and CanUseAzureFlute()",
    S + "scripts_hall_of_origin.s",
    script={"file": S + "scripts_hall_of_origin.s", "entry": "HallOfOrigin_CoordEvent_Arceus", "battle": "StartLegendaryBattle SPECIES_ARCEUS, 80"},
    hall_of_fame_required=True,
    depends_on_dex_completion=True,
    unlock_source={"file": S + "scripts_veilstone_store_b1f.s", "label": "VeilstoneStoreB1F_ProfRowanTryAzureFlute", "item": "ITEM_AZURE_FLUTE",
                   "command": "CheckPokedexCaughtAllButArceus"},
    retry_actions=["ClearFlag FLAG_HIDE_HALL_OF_ORIGIN_ARCEUS"],
    reset_script={"file": S + "scripts_hall_of_origin.s", "label": "HallOfOrigin_OnTransition",
                  "requires": ["GoToIfSet FLAG_CAUGHT_ARCEUS", "ClearFlag FLAG_HIDE_HALL_OF_ORIGIN_ARCEUS", "GoToIfUnset FLAG_GAME_COMPLETED", "CheckPokedexCaughtAllButArceus"]},
))
native.append(entry(
    "MANAPHY", "RESTORED_EVENT", "Canalave City - Sailor Eldritch (Egg gift)", "Egg (Lv1)", "gift",
    ["Pokémon Ranger / Mystery Gift Manaphy Egg only"],
    [HOF, "FLAG_WOKE_UP_CANALAVE_CITY_SAILOR_ELDRITCH_HOUSE_LITTLE_BOY (Cresselia/Lunar Wing child sequence)", "party has a free slot"],
    "ONE_TIME_GIFT", "FLAG_RECEIVED_CANALAVE_CITY_MANAPHY_EGG",
    "gift withheld (no flag set, no consumption) while the party is full; flag set only after GiveEgg",
    "Ranger link / Mystery Gift Manaphy Egg no longer required",
    S + "scripts_canalave_city.s",
    script={"file": S + "scripts_canalave_city.s", "entry": "CanalaveCity_SailorEldritchTryGiveManaphyEgg", "gift": "GiveEgg SPECIES_MANAPHY"},
    hall_of_fame_required=True,
))
native.append(entry(
    "PHIONE", "BREEDING_ONLY", "Daycare breeding (Manaphy + Ditto)", "Egg", "breeding",
    ["Manaphy breeding"], ["Manaphy breeding (Breeding 2.0 special case preserved)"], "RENEWABLE", None,
    "n/a", "none", "src/pokemon.c / docs/overhaul/implementation/breeding/BREEDING_VALIDATION_REPORT.md",
    internal_prerequisites=["SPECIES_MANAPHY"],
))

# --------------------------------------------------------------------------------------------------
# legacy_legendary_encounters.json
# --------------------------------------------------------------------------------------------------
HABITAT_SRC = "src/overlay006/wild_encounters.c"
# (species, [(map_header, encounter_type)], percent, min, max, conceptual habitat, mapping note, method)
habitats = [
    ("ARTICUNO", [("MAP_HEADER_SNOWPOINT_TEMPLE_B4F", "GRASS")], 2, 55, 60, "Snowpoint Temple deep floors / Acuity cavern ecology", "cave", "B4F is the deepest Snowpoint floor with a cave table that is not the Regigigas chamber"),
    ("ZAPDOS", [("MAP_HEADER_VALLEY_WINDWORKS_OUTSIDE", "GRASS")], 2, 55, 60, "Fuego Ironworks / Valley Windworks high-energy zone", "land", "Valley Windworks exterior (land table)"),
    ("MOLTRES", [("MAP_HEADER_STARK_MOUNTAIN_ROOM_1", "GRASS")], 2, 55, 60, "Stark Mountain volcanic zone", "cave", "interior room 1 (cave table); Entei owns the exterior and Groudon the deepest room"),
    ("MEWTWO", [(f"MAP_HEADER_TURNBACK_CAVE_PILLAR_3_ROOM_{i}", "GRASS") for i in range(1, 7)], 1, 70, 70, "deepest Turnback Cave rooms", "cave", "all six pillar-3 rooms (the last pillar before the Giratina room)"),
    ("RAIKOU", [("MAP_HEADER_ROUTE_222", "GRASS")], 2, 55, 60, "Route 222 / Sunyshore electric coast", "land", "Route 222 land table"),
    ("ENTEI", [("MAP_HEADER_STARK_MOUNTAIN_OUTSIDE", "GRASS")], 2, 55, 60, "Stark Mountain exterior volcanic zone", "land", "Stark Mountain exterior"),
    ("SUICUNE", [("MAP_HEADER_LAKE_ACUITY", "SURF")], 2, 55, 60, "Lake Acuity / northern clear-water zone", "surf", "Lake Acuity Surf table"),
    ("LUGIA", [("MAP_HEADER_ROUTE_226", "SURF")], 1, 65, 70, "deep postgame sea near Routes 226-230", "surf", "Route 226 Surf table (Kyogre uses Route 230 to keep the hunts separate)"),
    ("HO_OH", [("MAP_HEADER_MT_CORONET_5F", "GRASS")], 1, 65, 70, "upper Mt. Coronet / Spear Pillar-adjacent habitat", "cave", "Mt. Coronet 5F cave table"),
    ("LATIAS", [("MAP_HEADER_ROUTE_224", "GRASS")], 2, 55, 60, "Routes 224-230 postgame coast", "land", "Route 224 land table (no dedicated Latias/Latios slot sharing with Latios)"),
    ("LATIOS", [("MAP_HEADER_ROUTE_225", "GRASS")], 2, 55, 60, "Routes 224-230 postgame coast", "land", "Route 225 land table"),
    ("GROUDON", [("MAP_HEADER_STARK_MOUNTAIN_ROOM_2", "GRASS")], 1, 70, 70, "Stark Mountain deepest terrestrial zone", "cave", "Stark Mountain room 2 (room 3 is the Heatran chamber)"),
    ("KYOGRE", [("MAP_HEADER_ROUTE_230", "SURF")], 1, 70, 70, "deep postgame ocean, Routes 226-230", "surf", "Route 230 Surf table"),
    ("RAYQUAZA", [("MAP_HEADER_MT_CORONET_6F", "GRASS")], 1, 70, 70, "upper Mt. Coronet / Spear Pillar postgame zone", "cave", "Mt. Coronet 6F cave table (the Spear Pillar approach)"),
]
legacy = []
for sp, maps, pct, lo, hi, concept, method, note in habitats:
    legacy.append(entry(
        sp, "RARE_POSTGAME_HABITAT", concept, f"{lo}" if lo == hi else f"{lo}-{hi}", f"{pct}%",
        ["vanilla Platinum: roaming (birds) / no Platinum source (other species)"],
        [HOF, "renewable roll on the listed map(s); no flag suppression; no swarm/Radar/dual-slot dependency"],
        "RENEWABLE", None,
        "none: every wild encounter on the map/method rolls the percentage independently; ordinary table is untouched on a miss",
        "dual-slot / roaming dependency not used",
        HABITAT_SRC,
        hall_of_fame_required=True,
        percent=pct, min_level=lo, max_level=hi,
        encounter_method=method,
        rows=[{"map_header": m, "encounter_type": t} for m, t in maps],
        mapping_note=note,
    ))

# --------------------------------------------------------------------------------------------------
# mythical_statics.json
# --------------------------------------------------------------------------------------------------
myth = []
mythic = [
    ("MEW", "Eterna Forest (north-east dead end, tile of the Ether item ball)", 50, "scripts_eterna_forest.s", "EternaForest_Mew", "events_eterna_forest.json", 13, 81, 12, "FLAG_CAUGHT_MEW", "EternaForest"),
    ("CELEBI", "Floaroma Meadow (north-west, tile of the Miracle Seed item ball)", 50, "scripts_floaroma_meadow.s", "FloaromaMeadow_Celebi", "events_floaroma_meadow.json", 8, 14, 15, "FLAG_CAUGHT_CELEBI", "FloaromaMeadow"),
    ("JIRACHI", "Mt. Coronet 6F (Spear Pillar approach, tile south of the summit warp)", 50, "scripts_mt_coronet_6f.s", "MtCoronet6F_Jirachi", "events_mt_coronet_6f.json", 3, 7, 6, "FLAG_CAUGHT_JIRACHI", "MtCoronet6F"),
]
for sp, where, lvl, sf, ent, ef, sid, x, z, flag, pre in mythic:
    myth.append(entry(
        sp, "HIDDEN_MYTHICAL_STATIC", where, str(lvl), "static",
        ["vanilla Platinum: no in-game source (distribution only)"],
        [HOF, "interact with the BG-event tile (no time-of-day restriction)"],
        "ONE_TIME_UNTIL_CAPTURED", flag,
        f"{flag} set only in the captured branch; defeat/flee/blackout leave the BG event active; captured species never re-triggers",
        "none",
        S + sf,
        script={"file": S + sf, "entry": ent, "battle": f"StartLegendaryBattle SPECIES_{sp}, {lvl}"},
        bg_event={"events_file": f"res/field/events/{ef}", "script_id": sid, "x": x, "z": z},
        hall_of_fame_required=True,
        night_presentation=("not implemented (time of day deliberately not used)" if sp == "JIRACHI" else None),
    ))
myth.append(entry(
    "DEOXYS", "HIDDEN_MYTHICAL_STATIC", "Veilstone City meteorites (four existing BG events)", "60", "static",
    ["vanilla Platinum: meteorites only change the form of a party Deoxys"],
    [HOF, "touch any meteorite while no Deoxys is owned/caught (existing form-change scripts retained)"],
    "ONE_TIME_UNTIL_CAPTURED", "FLAG_CAUGHT_DEOXYS",
    "FLAG_CAUGHT_DEOXYS set only in the captured branch; defeat/flee/blackout leave the meteorites active",
    "none",
    S + "scripts_veilstone_city.s",
    script={"file": S + "scripts_veilstone_city.s", "entry": "VeilstoneCity_MeteoriteFromTheStars", "battle": "StartLegendaryBattle SPECIES_DEOXYS, 60"},
    hall_of_fame_required=True,
    form_changes_preserved=["VeilstoneCity_DeoxysMeteoriteSpeed", "VeilstoneCity_DeoxysMeteoriteDefense", "VeilstoneCity_DeoxysMeteoriteAttack", "VeilstoneCity_DeoxysMeteoriteNormal"],
))

RESPAWN_GUARD = {
    # how a captured encounter is prevented from respawning
    "UXIE": "hof_reshow_guard", "AZELF": "hof_reshow_guard", "GIRATINA": "hof_reshow_guard",
    "HEATRAN": "reset_script+hof_reshow_guard", "REGIGIGAS": "reset_script+hof_reshow_guard",
    "DIALGA": "entry_guard+hof_reshow_guard", "PALKIA": "entry_guard+hof_reshow_guard",
    "REGIROCK": "reset_script", "REGICE": "reset_script", "REGISTEEL": "reset_script",
    "DARKRAI": "reset_script", "SHAYMIN": "reset_script", "ARCEUS": "reset_script",
    "MEW": "entry_guard", "CELEBI": "entry_guard", "JIRACHI": "entry_guard", "DEOXYS": "entry_guard",
}
for _e in native + myth:
    _k = _e["species"].replace("SPECIES_", "")
    if _k in RESPAWN_GUARD:
        _e["respawn_guard"] = RESPAWN_GUARD[_k]


# --------------------------------------------------------------------------------------------------
# event_gate_removals.json
# --------------------------------------------------------------------------------------------------
removals = [
    {"gate": "DISTRIBUTION_EVENT_DARKRAI", "species": ["DARKRAI"], "files": [S + "scripts_canalave_city.s", S + "scripts_canalave_city_harbor_inn.s", S + "scripts_newmoon_island_forest.s"], "replacement": "Member Card from Sailor Eldritch (Canalave City) after Hall of Fame + Lunar Wing child sequence; Newmoon Island also checks the Hall of Fame"},
    {"gate": "DISTRIBUTION_EVENT_SHAYMIN", "species": ["SHAYMIN"], "files": [S + "scripts_route_224.s", S + "scripts_flower_paradise.s"], "replacement": "Oak (Route 224) gives Oak's Letter and starts VAR_SHAYMIN_EVENT_STATE after Hall of Fame + National Dex"},
    {"gate": "DISTRIBUTION_EVENT_ARCEUS", "species": ["ARCEUS"], "files": [S + "scripts_hall_of_origin.s", S + "scripts_spear_pillar.s", S + "scripts_spear_pillar_dialga.s", S + "scripts_spear_pillar_palkia.s", S + "scripts_common.s", "src/item_use_functions.c"], "replacement": "Rowan (Veilstone Store B1F) gives the Azure Flute after CheckPokedexCaughtAllButArceus; Hall of Origin re-checks it"},
    {"gate": "DISTRIBUTION_EVENT_ROTOM", "species": ["ROTOM"], "files": [S + "scripts_rotoms_room.s", S + "scripts_team_galactic_eterna_building_1f.s", S + "scripts_old_chateau_back_middle_west_room.s"], "replacement": "ITEM_SECRET_KEY (already given on the first Old Chateau Rotom capture) is the only gate; the room stays usable"},
    {"gate": "CheckPartyHasFatefulEncounterRegigigas", "species": ["REGIROCK", "REGICE", "REGISTEEL"], "files": [S + "scripts_rock_peak_ruins.s", S + "scripts_iceberg_ruins.s", S + "scripts_iron_ruins.s", S + "scripts_route_228.s", S + "scripts_mt_coronet_1f_north_room_2.s", S + "scripts_iron_island_b3f.s"], "replacement": "statues: Hall of Fame + braille puzzle only; ruin entrance warps (Route 228, Mt. Coronet 1F north room 2, Iron Island B3F) select the Regi ruins map with CheckGameCompleted instead of an event-Regigigas party check"},
    {"gate": "Roaming legendary birds (Eterna City South House Oak activation)", "species": ["ARTICUNO", "ZAPDOS", "MOLTRES"], "files": [S + "scripts_eterna_city_south_house.s"], "replacement": "renewable postgame habitats; Oak's Pokédex rating service no longer waits on the roaming birds"},
    {"gate": "Mystery Gift Manaphy Egg / Pokémon Ranger link", "species": ["MANAPHY"], "files": [S + "scripts_canalave_city.s"], "replacement": "Sailor Eldritch Manaphy Egg gift"},
    {"gate": "Dual-slot / Slot-2 legendary dependence", "species": [], "files": ["src/overlay006/dual_slot_encounters.c"], "replacement": "none required: no legendary uses dual-slot encounters (neutralised in the ordinary availability phase)"},
]
for r in removals:
    r["validation_status"] = dict(STATUS)

# --------------------------------------------------------------------------------------------------
# event_retry_rules.json
# --------------------------------------------------------------------------------------------------
retry = {
    "rules": [
        "A captured/completion marker (FLAG_CAUGHT_*, *_RUINS_STATE == RUINS_STATE_CAUGHT_REGI, roamer state CAPTURED, a consumed state variable) may only be written on the confirmed-capture path.",
        "Defeat-without-capture, flee and blackout branches must restore whatever the object hide flag / state variable hid at battle start.",
        "Defeated roamers (Mesprit, Cresselia) reset on the next visit to their activation map.",
        "Renewable habitat encounters carry no flag at all.",
    ],
    "checks": [],
}
for e in native + myth:
    sp = e["species"]
    chk = {
        "species": sp,
        "acquisition_class": e["acquisition_class"],
        "capture_flag": e["capture_flag"],
        "retry_behavior": e["retry_behavior"],
        "source_path": e["source_path"],
        "structural_checks": [
            "1 encounter available", "2 defeat/flee does not consume it", "3 leave/re-enter allows retry",
            "4 capture sets completion", "5 captured encounter does not respawn",
        ] if e["one_time_vs_renewable"] == "ONE_TIME_UNTIL_CAPTURED" else [],
        "validation_status": dict(STATUS),
    }
    for k in ("script", "retry_actions", "consumed_markers", "reset_script", "respawn_guard"):
        if k in e:
            chk[k] = e[k]
    retry["checks"].append(chk)
retry["checks"].append({
    "species": "ROTOM", "acquisition_class": "NON_LEGENDARY_EVENT_INFRASTRUCTURE", "capture_flag": "FLAG_CAUGHT_OLD_CHATEAU_ROTOM",
    "retry_behavior": "RotomDisappearedIntoTV leaves the TV re-usable; Secret Key is given with the first capture; appliance room needs only the key",
    "source_path": S + "scripts_old_chateau_back_middle_west_room.s", "structural_checks": [], "validation_status": dict(STATUS),
})


def doc(name, entries_key, entries, extra=None):
    d = {
        "schema": "pokeplatinum-overhaul/d5-%s/v1" % name,
        "base_commit": BASE_COMMIT,
        "authority": AUTH,
        "note": "Generated by tools/overhaul/events/build_manifests.py; validated against live source by tools/overhaul/validate_legendary_availability.py.",
    }
    if extra:
        d.update(extra)
    d[entries_key] = entries
    return d


def main():
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    out = {
        "native_legendary_events.json": doc("native-legendary-events", "events", native,
                                            {"rotom": {"acquisition_class": "NON_LEGENDARY_EVENT_INFRASTRUCTURE", "source_path": S + "scripts_rotoms_room.s",
                                                       "forms_preserved": ["ROTOM_FORM_HEAT", "ROTOM_FORM_FROST", "ROTOM_FORM_WASH", "ROTOM_FORM_FAN", "ROTOM_FORM_MOW"],
                                                       "secret_key": "given with the first Old Chateau Rotom capture (Common_GiveItemQuantity ITEM_SECRET_KEY)",
                                                       "validation_status": dict(STATUS)}}),
        "legacy_legendary_encounters.json": doc("legacy-legendary-encounters", "encounters", legacy,
                                                {"mechanism": "LegendaryHabitat table in src/overlay006/wild_encounters.c (post-Hall-of-Fame percentage roll before the ordinary slot pick). Exact 1%/2% on Surf is impossible with the code-fixed Surf slot weights 60/30/5/4/1, hence the roll; ordinary encounter JSON is untouched."}),
        "mythical_statics.json": doc("mythical-statics", "statics", myth),
        "event_gate_removals.json": doc("event-gate-removals", "removals", removals),
        "event_retry_rules.json": doc("event-retry-rules", "rules_doc", retry),
    }
    for name, d in out.items():
        (EVENTS_DIR / name).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        print("wrote", name)


if __name__ == "__main__":
    main()
