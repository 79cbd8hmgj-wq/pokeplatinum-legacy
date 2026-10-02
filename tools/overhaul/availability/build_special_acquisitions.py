#!/usr/bin/env python3
"""Generate docs/overhaul/implementation/special_acquisitions.json (the 28 families resolved by the special-acquisition pass)."""
from __future__ import annotations

import sys

from common import IMPL_DIR
from manifest_io import dumps_compact

LAB = "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"
CEL = "res/field/scripts/scripts_celestic_town_southwest_house.s"


def starter(fid, region, species, badges, vanilla):
    S = species.title()
    return fid, {
        "decision_key": "STARTER_DISTRIBUTION", "kind": "GIFT", "region": region, "band": {2: "M1", 3: "M1", 4: "M1", 5: "M2"}[badges],
        "vanilla_method": vanilla,
        "overhaul_method": f"Sandgem Lab research assistant gifts {species} once {badges} badges are held (one gift per visit, party-full retry)",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "gift": {"file": LAB, "entry_label": "SandgemTownLab_ScientistF", "species": f"SPECIES_{species}",
                 "flag": f"FLAG_RECEIVED_STARTER_{region}_{species}", "min_badges": badges,
                 "give": {"mode": "table", "offer_label": f"SandgemTownLab_StarterGift_Offer_{S}",
                          "give_label": "SandgemTownLab_StarterGift_Offer", "var": "VAR_0x8001"}},
    }


def main() -> int:
    acq = {}
    for fid, region, sp, badges, vanilla in [
        ("turtwig", "SINNOH", "TURTWIG", 2, "Route 201 starter choice (one of three, the other two never obtainable)"),
        ("chimchar", "SINNOH", "CHIMCHAR", 2, "Route 201 starter choice"), ("piplup", "SINNOH", "PIPLUP", 2, "Route 201 starter choice"),
        ("bulbasaur", "KANTO", "BULBASAUR", 3, "not obtainable (Slot-2/trade only)"),
        ("charmander", "KANTO", "CHARMANDER", 3, "not obtainable (Slot-2/trade only)"),
        ("squirtle", "KANTO", "SQUIRTLE", 3, "not obtainable (Slot-2/trade only)"),
        ("chikorita", "JOHTO", "CHIKORITA", 4, "not obtainable (Slot-2/trade only)"),
        ("cyndaquil", "JOHTO", "CYNDAQUIL", 4, "not obtainable (Slot-2/trade only)"),
        ("totodile", "JOHTO", "TOTODILE", 4, "not obtainable (Slot-2/trade only)"),
        ("treecko", "HOENN", "TREECKO", 5, "not obtainable (Slot-2/trade only)"),
        ("torchic", "HOENN", "TORCHIC", 5, "not obtainable (Slot-2/trade only)"),
        ("mudkip", "HOENN", "MUDKIP", 5, "not obtainable (Slot-2/trade only)")]:
        k, v = starter(fid, region, sp, badges, vanilla)
        acq[k] = v
    for fid, item, ritem, sp, vanilla in [
        ("omanyte", "HELIX_FOSSIL", "ITEM_HELIX_FOSSIL", "SPECIES_OMANYTE", "Underground mining; weight 0 before the National Dex"),
        ("kabuto", "DOME_FOSSIL", "ITEM_DOME_FOSSIL", "SPECIES_KABUTO", "Underground mining; weight 0 before the National Dex"),
        ("lileep", "ROOT_FOSSIL", "ITEM_ROOT_FOSSIL", "SPECIES_LILEEP", "Underground mining; weight 0 before the National Dex"),
        ("anorith", "CLAW_FOSSIL", "ITEM_CLAW_FOSSIL", "SPECIES_ANORITH", "Underground mining; weight 0 before the National Dex"),
        ("aerodactyl", "OLD_AMBER", "ITEM_OLD_AMBER", "SPECIES_AERODACTYL", "Underground mining; weight 0 before the National Dex"),
        ("shieldon", "ARMOR_FOSSIL", "ITEM_ARMOR_FOSSIL", "SPECIES_SHIELDON", "Underground mining; weight 0 for odd Trainer IDs"),
        ("cranidos", "SKULL_FOSSIL", "ITEM_SKULL_FOSSIL", "SPECIES_CRANIDOS", "Underground mining; weight 0 for even Trainer IDs")]:
        acq[fid] = {"decision_key": "FOSSIL_ACQUISITION", "kind": "FOSSIL", "band": "M1", "vanilla_method": vanilla,
                    "overhaul_method": "Underground mining (Explorer Kit from Eterna) with one TID/Dex-independent weight per fossil; revived at the Oreburgh Mining Museum",
                    "retry_safe": True, "external_dependencies": [], "engine_change": True,
                    "fossil": {"mining_item": item, "revival_item": ritem, "species": sp}}
    acq["spiritomb"] = {
        "decision_key": "SPIRITOMB_QUEST", "kind": "SPIRITOMB_RITUAL", "band": "M1",
        "vanilla_method": "Odd Keystone + Hallowed Tower after talking to 32 other players in the Underground; an uncaught Spiritomb ends the ritual",
        "overhaul_method": "Odd Keystone (Twinleaf hidden item) + Hallowed Tower; the counter rises by one per object unearthed in Underground mining; an uncaught Spiritomb leaves the ritual intact",
        "retry_safe": True, "external_dependencies": [], "engine_change": True,
        "ritual": {"file": "res/field/scripts/scripts_route_209.s"}}
    acq["rotom"] = {
        "decision_key": "ROTOM_UNLOCK_PRESENTATION", "kind": "STATIC_ENCOUNTER", "band": "E1",
        "vanilla_method": "Old Chateau TV static (night, once per day); form room needs a Mystery Gift Secret Key",
        "overhaul_method": "Old Chateau TV static at night with no daily cap; catching it grants the Secret Key and unlocks the existing appliance room",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "static": {"file": "res/field/scripts/scripts_old_chateau_back_middle_west_room.s",
                   "entry_label": "OldChateauBackMiddleWestRoom_TV", "species": "SPECIES_ROTOM",
                   "caught_flag": "FLAG_CAUGHT_OLD_CHATEAU_ROTOM", "forbidden_gate_tokens": ["FLAG_DAILY_BATTLED_OLD_CHATEAU_ROTOM"],
                   "secret_key": {"item": "ITEM_SECRET_KEY", "distribution_gate_removed": True,
                                  "form_room_files": ["res/field/scripts/scripts_rotoms_room.s", "res/field/scripts/scripts_team_galactic_eterna_building_1f.s"],
                                  "superseded_by": "D5 Legendary/Mythical events (docs/overhaul/implementation/events/event_gate_removals.json): the DISTRIBUTION_EVENT_ROTOM magic number no longer gates the appliance room; the Secret Key alone does"}}}
    acq["tyrogue"] = {
        "decision_key": "TYROGUE_GIFT_VS_HABITAT", "kind": "GIFT", "band": "M1",
        "vanilla_method": "breeding Hitmonlee/Hitmonchan/Hitmontop only (Radar slot on Route 211 West)",
        "overhaul_method": "Celestic Town Black Belt gifts Tyrogue after the Poketch watch gift",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "gift": {"file": CEL, "entry_label": "CelesticTownPokecenter1F_BlackBelt", "species": "SPECIES_TYROGUE",
                 "flag": "FLAG_RECEIVED_CELESTIC_TOWN_SOUTHWEST_HOUSE_TYROGUE", "min_badges": 0,
                 "give": {"mode": "direct", "label": "CelesticTownSoutheastHouse_OfferTyrogue"}}}
    acq["happiny"] = {
        "decision_key": "HAPPINY_CHANSEY_GIFT_VS_HABITAT", "kind": "GIFT", "band": "M1",
        "vanilla_method": "Chansey 1%/4% on Routes 209/210 (kept as bonus), Trophy Garden daily; Happiny by breeding",
        "overhaul_method": "Celestic Town Black Belt gifts Happiny after the Tyrogue gift (the Happiny in his room)",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "gift": {"file": CEL, "entry_label": "CelesticTownPokecenter1F_BlackBelt", "species": "SPECIES_HAPPINY",
                 "flag": "FLAG_RECEIVED_CELESTIC_TOWN_SOUTHWEST_HOUSE_HAPPINY", "min_badges": 0,
                 "give": {"mode": "direct", "label": "CelesticTownSoutheastHouse_OfferHappiny"}}}
    acq["castform"] = {
        "decision_key": "CASTFORM_GIFT_VS_HABITAT", "kind": "GIFT", "band": "M1",
        "vanilla_method": "Trophy Garden daily rotation only",
        "overhaul_method": "Veilstone City parasol woman (weather-report watcher) gifts Castform",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "gift": {"file": "res/field/scripts/scripts_veilstone_city.s", "entry_label": "VeilstoneCity_BattleGirl2",
                 "species": "SPECIES_CASTFORM", "flag": "FLAG_RECEIVED_VEILSTONE_CITY_CASTFORM", "min_badges": 0,
                 "give": {"mode": "direct", "label": "VeilstoneCity_BattleGirl2"}}}
    acq["eevee"] = {
        "decision_key": "EEVEE_GIFT_VS_WILD_BALANCE", "kind": "GIFT", "band": "M1",
        "vanilla_method": "Hearthome City northwest house gift (Lv20, party-full retry) + Trophy Garden daily",
        "overhaul_method": "unchanged: existing Hearthome gift verified retry-safe and pre-E4 (Hearthome is the 3rd gym town)",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "gift": {"file": "res/field/scripts/scripts_hearthome_city_northwest_house.s", "entry_label": "HearthomeCityNorthwestHouse_Bebe",
                 "species": "SPECIES_EEVEE", "flag": "FLAG_RECEIVED_HEARTHOME_CITY_NORTHWEST_HOUSE_EEVEE", "min_badges": 0,
                 "give": {"mode": "direct", "label": "HearthomeCityNorthwestHouse_AcceptEevee"}}}
    acq["porygon"] = {
        "decision_key": "PORYGON_ACQUISITION_PRESENTATION", "kind": "GIFT", "band": "M1",
        "vanilla_method": "Veilstone City northeast house gift (Lv25, party-full retry)",
        "overhaul_method": "unchanged: existing Veilstone gift verified retry-safe and pre-E4",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "gift": {"file": "res/field/scripts/scripts_veilstone_city_northeast_house.s", "entry_label": "VeilstoneCityNortheastHouse_PokefanM",
                 "species": "SPECIES_PORYGON", "flag": "FLAG_RECEIVED_VEILSTONE_CITY_NORTHEAST_HOUSE_PORYGON", "min_badges": 0,
                 "give": {"mode": "direct", "label": "VeilstoneCityNortheastHouse_AcceptPorygon"}}}
    acq["riolu"] = {
        "decision_key": "RIOLU_REPEATABILITY", "kind": "GIFT", "band": "M2",
        "vanilla_method": "Riley's Riolu egg on Iron Island B2F; a full party sets FLAG_COULD_NOT_RECEIVE_RIOLU_EGG and Riley re-offers",
        "overhaul_method": "unchanged: existing recovery flag verified (set on failure, checked at entry, cleared on success)",
        "retry_safe": True, "external_dependencies": [], "engine_change": False,
        "gift": {"file": "res/field/scripts/scripts_iron_island_b2f_left_room.s", "entry_label": "IronIslandB2FLeftRoom_Riley",
                 "species": "SPECIES_RIOLU", "give_command": "GiveEgg", "flag": "FLAG_RECEIVED_RIOLU_EGG_FROM_RILEY",
                 "flag_label": "IronIslandB2FLeftRoom_SetFlagReceivedEgg", "recovery_flag": "FLAG_COULD_NOT_RECEIVE_RIOLU_EGG",
                 "min_badges": 0, "give": {"mode": "direct", "label": "IronIslandB2FLeftRoom_AcceptedEgg"}}}
    acq["feebas"] = {
        "decision_key": "FEEBAS_IMPLEMENTATION", "kind": "FISHING_FIXED_TILES", "band": "P0",
        "vanilla_method": "Mt. Coronet B1F: four Feebas tiles re-rolled from the mixed-record RNG, 50% hit chance on them",
        "overhaul_method": "four fixed tiles (one per quarter of the lake), same 50% chance; any rod",
        "retry_safe": True, "external_dependencies": [], "engine_change": True,
        "fishing": {"fixed_tiles_xz": [[23, 21], [12, 29], [21, 39], [12, 48]], "map": "mt_coronet_b1f"}}
    out = {
        "schema": "availability_special_acquisitions/1",
        "resolves": "the 28 USER_DECISION_REQUIRED families deferred by the ordinary availability implementation (PR #10)",
        "base_commit": "f89dfc79",
        "shared": {"fossil_revival": {"file": "res/field/scripts/scripts_mining_museum.s", "revival_label": "MiningMuseum_PokemonRevival",
                                      "explorer_kit_file": "res/field/scripts/scripts_eterna_city_underground_man_house.s"}},
        "acquisitions": acq,
    }
    assert len(acq) == 28
    (IMPL_DIR / "special_acquisitions.json").write_text(dumps_compact(out, line_arrays=()))
    print(len(acq), "special acquisitions ->", IMPL_DIR / "special_acquisitions.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
