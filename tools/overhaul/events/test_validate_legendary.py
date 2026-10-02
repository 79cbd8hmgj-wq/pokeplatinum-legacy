#!/usr/bin/env python3
"""Mutation tests for tools/overhaul/validate_legendary_availability.py.

Each case copies the files the validator reads into a temp tree, applies one defect, and asserts the validator
fails with the expected check id (and that the unmutated tree passes).

Run:  python3 -m unittest discover -s tools/overhaul/events -p 'test_validate_legendary.py'
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from lib import ROOT  # noqa: E402
import validate_legendary_availability as V  # noqa: E402

COPY = [
    "res/field/scripts", "res/field/encounters", "docs/overhaul/implementation/events",
    "docs/overhaul/implementation/availability_families.json", "generated/vars_flags.txt",
    "src/overlay006/wild_encounters.c", "src/overlay006/roamer_after_battle.c", "src/scrcmd.c", "src/pokemon.c",
    "src/item_use_functions.c", "asm/macros/scrcmd.inc", "include/data/scripts/scrcmd.h",
]
S = "res/field/scripts/"


def make_tree() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="d5val_"))
    for rel in COPY:
        src = ROOT / rel
        dst = tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
    return tmp


def run(tree: Path) -> dict[str, bool]:
    v = V.Validation(tree)
    v.__post_init__()
    v.run()
    return {r.check_id: r.ok for r in v.results}


class Mut(unittest.TestCase):
    tree: Path

    def setUp(self):
        self.tree = make_tree()

    def tearDown(self):
        shutil.rmtree(self.tree, ignore_errors=True)

    def sub(self, rel: str, old: str, new: str, count: int = 1):
        p = self.tree / rel
        s = p.read_text()
        self.assertEqual(s.count(old), count, f"{rel}: {old!r}")
        p.write_text(s.replace(old, new))

    def manifest(self, name: str, fn):
        p = self.tree / V.MANIFESTS[name]
        d = json.loads(p.read_text())
        fn(d)
        p.write_text(json.dumps(d))

    def expect_fail(self, *ids: str):
        res = run(self.tree)
        for i in ids:
            self.assertFalse(res[i], f"{i} should fail; failing={[k for k, ok in res.items() if not ok]}")

    # ------------------------------------------------------------------------------------------------
    def test_baseline_passes(self):
        res = run(self.tree)
        self.assertTrue(all(res.values()), [k for k, ok in res.items() if not ok])

    # external dependencies
    def test_distribution_gate_reintroduced(self):
        self.sub(S + "scripts_newmoon_island_forest.s", "    GoToIfUnset FLAG_GAME_COMPLETED, NewmoonIslandForest_HideDarkrai\n",
                 "    CheckDistributionEvent DISTRIBUTION_EVENT_DARKRAI, VAR_MAP_LOCAL_0x00\n    GoToIfEq VAR_MAP_LOCAL_0x00, FALSE, NewmoonIslandForest_HideDarkrai\n")
        self.expect_fail("B1", "B2")

    def test_event_regigigas_gate_reintroduced(self):
        p = self.tree / (S + "scripts_route_228.s")
        p.write_text(p.read_text().replace("CheckGameCompleted VAR_MAP_LOCAL_0x01", "CheckPartyHasFatefulEncounterRegigigas VAR_MAP_LOCAL_0x01", 1))
        self.expect_fail("B1")

    def test_wfc_token_in_acquisition_script(self):
        p = self.tree / (S + "scripts_hall_of_origin.s")
        p.write_text(p.read_text().replace("HallOfOrigin_OnTransition:\n", "HallOfOrigin_OnTransition:\n    CheckHasWiFiListValidLogin VAR_MAP_LOCAL_0x00\n", 1))
        self.expect_fail("B2")

    def test_removal_record_stale(self):
        p = self.tree / (S + "scripts_rotoms_room.s")
        p.write_text(p.read_text() + "\n    CheckDistributionEvent DISTRIBUTION_EVENT_ROTOM, VAR_RESULT\n")
        self.expect_fail("B1", "B3")

    # one-time retry safety
    def test_uxie_retry_action_removed(self):
        self.sub(S + "scripts_acuity_cavern.s", "AcuityCavern_UxieDisappeared:\n    ClearFlag FLAG_HIDE_ACUITY_CAVERN_UXIE\n", "AcuityCavern_UxieDisappeared:\n")
        self.expect_fail("D2")

    def test_uxie_blackout_retry_removed(self):
        self.sub(S + "scripts_acuity_cavern.s", "AcuityCavern_LostBattle:\n    ClearFlag FLAG_HIDE_ACUITY_CAVERN_UXIE\n", "AcuityCavern_LostBattle:\n")
        self.expect_fail("D2")

    def test_caught_flag_set_before_result(self):
        self.sub(S + "scripts_valor_cavern.s", "    StartLegendaryBattle SPECIES_AZELF, 50\n", "    StartLegendaryBattle SPECIES_AZELF, 50\n    SetFlag FLAG_CAUGHT_AZELF\n")
        self.expect_fail("D1")

    def test_dialga_state_consumed_before_capture(self):
        self.sub(S + "scripts_spear_pillar_dialga.s", "    GoToIfEq VAR_RESULT, FALSE, SpearPillarDialga_BlackOut\n    CheckDidNotCapture VAR_RESULT\n",
                 "    GoToIfEq VAR_RESULT, FALSE, SpearPillarDialga_BlackOut\n    SetVar VAR_SPEAR_PILLAR_DIALGA_STATE, 1\n    CheckDidNotCapture VAR_RESULT\n")
        self.expect_fail("D1")

    def test_palkia_flag_not_set_on_capture(self):
        self.sub(S + "scripts_spear_pillar_palkia.s", "    SetFlag FLAG_CAUGHT_PALKIA\n", "")
        self.expect_fail("D1")

    def test_regi_permanent_consumed_state(self):
        self.sub(S + "scripts_iron_ruins.s", "IronRuins_DidNotCatchRegisteelStatueStoppedEmanatingPower:\n    SetVar VAR_IRON_RUINS_STATE, 0\n",
                 "IronRuins_DidNotCatchRegisteelStatueStoppedEmanatingPower:\n    SetVar VAR_IRON_RUINS_STATE, RUINS_STATE_DID_NOT_CATCH_REGI\n")
        self.expect_fail("D1")

    def test_regi_reset_removed(self):
        self.sub(S + "scripts_rock_peak_ruins.s", "GoToIfNe VAR_ROCK_PEAK_RUINS_STATE, RUINS_STATE_CAUGHT_REGI, RockPeakRuins_ResetState", "GoToIfLt VAR_ROCK_PEAK_RUINS_STATE, RUINS_STATE_DID_NOT_CATCH_REGI, RockPeakRuins_ResetState")
        self.expect_fail("D3")

    def test_heatran_uncaught_state_not_restored(self):
        self.sub(S + "scripts_stark_mountain_room_3.s", "StarkMountainRoom3_HeatranDisappeared:\n    SetVar VAR_STARK_MOUNTAIN_ROOM_3_STATE, 1\n", "StarkMountainRoom3_HeatranDisappeared:\n")
        self.expect_fail("D2")

    def test_regigigas_transition_without_caught_guard(self):
        self.sub(S + "scripts_snowpoint_temple_b5f.s", "    GoToIfSet FLAG_CAUGHT_REGIGIGAS, SnowpointTempleB5F_HideRegigigas\n", "")
        self.expect_fail("D3")

    def test_cresselia_reset_removed(self):
        self.sub(S + "scripts_fullmoon_island_forest.s", "    CallIfEq VAR_ROAMING_CRESSELIA_STATE, ROAMER_STATE_DEFEATED, FullmoonIslandForest_ResetDefeatedCresselia\n", "")
        self.expect_fail("D3")

    def test_mesprit_reset_removed(self):
        self.sub(S + "scripts_verity_cavern.s", "    SetVar VAR_ROAMING_MESPRIT_STATE, ROAMER_STATE_RESET\n    Return\n", "    Return\n")
        self.expect_fail("D3")

    def test_birds_reactivated(self):
        p = self.tree / (S + "scripts_eterna_city_south_house.s")
        p.write_text(p.read_text().replace("EternaCitySouthHouse_ActivateRoamingLegendaryBirds:\n", "EternaCitySouthHouse_ActivateRoamingLegendaryBirds:\n    ActivateRoamingPokemon ROAMING_SLOT_MOLTRES\n", 1))
        self.expect_fail("D6")

    def test_mythical_respawns_after_capture(self):
        self.sub(S + "scripts_eterna_forest.s", "    GoToIfSet FLAG_CAUGHT_MEW, EternaForest_MewEnd\n", "")
        self.expect_fail("D4")

    def test_mythical_missing_hof_gate(self):
        self.sub(S + "scripts_floaroma_meadow.s", "    GoToIfUnset FLAG_GAME_COMPLETED, FloaromaMeadow_CelebiEnd\n", "")
        self.expect_fail("E1")

    def test_mythical_capture_flag_never_set(self):
        self.sub(S + "scripts_mt_coronet_6f.s", "    SetFlag FLAG_CAUGHT_JIRACHI\n", "")
        self.expect_fail("D1")

    def test_deoxys_gate_removed(self):
        self.sub(S + "scripts_veilstone_city.s", "    GoToIfSet FLAG_CAUGHT_DEOXYS, VeilstoneCity_MeteoriteNoDeoxys\n", "")
        self.expect_fail("D4")

    # habitats
    def test_habitat_rate_changed(self):
        self.sub("src/overlay006/wild_encounters.c", "ENCOUNTER_TYPE_GRASS, 2, SPECIES_ARTICUNO", "ENCOUNTER_TYPE_GRASS, 3, SPECIES_ARTICUNO")
        self.expect_fail("C3", "C4")

    def test_habitat_level_changed(self):
        self.sub("src/overlay006/wild_encounters.c", "SPECIES_MEWTWO, 70, 70 },\n    { MAP_HEADER_ROUTE_222", "SPECIES_MEWTWO, 60, 70 },\n    { MAP_HEADER_ROUTE_222")
        self.expect_fail("C3", "C4")

    def test_habitat_hof_gate_removed(self):
        self.sub("src/overlay006/wild_encounters.c", "    if (SystemFlag_CheckGameCompleted(SaveData_GetVarsFlags(fieldSystem->saveData)) == FALSE) {\n        return FALSE;\n    }\n\n    for (int i = 0; i < NELEMS(sLegendaryHabitats)", "    for (int i = 0; i < NELEMS(sLegendaryHabitats)")
        self.expect_fail("C6")

    def test_habitat_hook_unwired(self):
        p = self.tree / "src/overlay006/wild_encounters.c"
        s = p.read_text().replace("TryRollLegendaryHabitat(fieldSystem, encounterType, &habitatSpecies, &habitatLevel)", "FALSE", 1)
        p.write_text(s)
        self.expect_fail("C7")

    def test_habitat_shares_slot(self):
        self.sub("src/overlay006/wild_encounters.c", "    { MAP_HEADER_ROUTE_225, ENCOUNTER_TYPE_GRASS, 2, SPECIES_LATIOS, 55, 60 },", "    { MAP_HEADER_ROUTE_224, ENCOUNTER_TYPE_GRASS, 2, SPECIES_LATIOS, 55, 60 },")
        self.expect_fail("C2")

    def test_habitat_flag_suppression(self):
        p = self.tree / "src/overlay006/wild_encounters.c"
        s = p.read_text().replace("        *species = habitat->species;", "        SystemFlag_SetFoo(0);\n        *species = habitat->species;", 1)
        p.write_text(s)
        self.expect_fail("C8")

    def test_legendary_in_ordinary_table(self):
        p = self.tree / "res/field/encounters/encounters_route_201.json"
        p.write_text(p.read_text().replace("SPECIES_STARLY", "SPECIES_RAIKOU", 1))
        self.expect_fail("A6")

    # ownership / coverage
    def test_species_missing(self):
        self.manifest("mythical", lambda d: d["statics"].__delitem__(0))
        self.expect_fail("A2")

    def test_conflicting_ownership(self):
        def dup(d):
            d["encounters"].append(dict(d["encounters"][0], species="SPECIES_MEW"))
        self.manifest("legacy", dup)
        self.expect_fail("A3")

    def test_runtime_verified_claim(self):
        def v(d):
            d["events"][0]["validation_status"]["runtime"] = "VERIFIED"
        self.manifest("native", v)
        self.expect_fail("A5")

    def test_wrong_class(self):
        def v(d):
            d["events"][0]["acquisition_class"] = "NATIVE_ROAMER"
        self.manifest("native", v)
        self.expect_fail("A7")

    def test_wrong_level(self):
        def v(d):
            for e in d["events"]:
                if e["species"] == "SPECIES_SHAYMIN":
                    e["level"] = "50"
        self.manifest("native", v)
        self.expect_fail("A8")

    # Arceus / chains
    def test_arceus_check_includes_arceus(self):
        self.sub("src/scrcmd.c", "species < SPECIES_ARCEUS; species++", "species <= SPECIES_ARCEUS; species++")
        self.expect_fail("F1")

    def test_arceus_check_counts_total_only(self):
        self.sub("src/scrcmd.c", "        if (Pokedex_HasCaughtSpecies(dex, species) == FALSE) {\n            *destVar = FALSE;\n            break;\n        }\n", "        if (Pokedex_CountCaught_National(dex) < 492) {\n            *destVar = FALSE;\n            break;\n        }\n")
        self.expect_fail("F1")

    def test_flute_given_before_check(self):
        self.sub(S + "scripts_veilstone_store_b1f.s", "    CheckPokedexCaughtAllButArceus VAR_RESULT\n    GoToIfEq VAR_RESULT, FALSE, VeilstoneStoreB1F_ProfRowanDexIncomplete\n", "    GoToIfEq VAR_RESULT, FALSE, VeilstoneStoreB1F_ProfRowanDexIncomplete\n    CheckPokedexCaughtAllButArceus VAR_RESULT\n")
        self.expect_fail("F3")

    def test_hall_of_origin_without_recheck(self):
        self.sub(S + "scripts_hall_of_origin.s", "    CheckPokedexCaughtAllButArceus VAR_MAP_LOCAL_0x00\n    GoToIfEq VAR_MAP_LOCAL_0x00, FALSE, HallOfOrigin_HideArceus\n", "")
        self.expect_fail("F4", "D3")

    def test_other_species_depends_on_dex(self):
        def v(d):
            d["events"][0]["depends_on_dex_completion"] = True
        self.manifest("native", v)
        self.expect_fail("F5")

    def test_member_card_without_hof(self):
        self.sub(S + "scripts_canalave_city.s", "    GoToIfUnset FLAG_GAME_COMPLETED, CanalaveCity_SailorEldritchTryGiftsEnd\n", "")
        self.expect_fail("G1", "H3", "E1")

    def test_oaks_letter_still_required_by_route_224(self):
        self.sub(S + "scripts_route_224.s", "    CallIfEq VAR_SHAYMIN_EVENT_STATE, 0, Route224_StartShayminEvent\n", "    CheckItem ITEM_OAKS_LETTER, 1, VAR_MAP_LOCAL_0x00\n    GoToIfEq VAR_MAP_LOCAL_0x00, FALSE, Route224_DontHideProfOak\n    CallIfEq VAR_SHAYMIN_EVENT_STATE, 0, Route224_StartShayminEvent\n")
        self.expect_fail("G4")

    # Manaphy / Rotom
    def test_manaphy_flag_before_egg(self):
        self.sub(S + "scripts_canalave_city.s", "    GiveEgg SPECIES_MANAPHY, SPECIAL_METLOC_NAME_DISTANT_LAND\n    SetFlag FLAG_RECEIVED_CANALAVE_CITY_MANAPHY_EGG\n", "    SetFlag FLAG_RECEIVED_CANALAVE_CITY_MANAPHY_EGG\n    GiveEgg SPECIES_MANAPHY, SPECIAL_METLOC_NAME_DISTANT_LAND\n")
        self.expect_fail("H1")

    def test_manaphy_no_party_check(self):
        self.sub(S + "scripts_canalave_city.s", "    GoToIfGe VAR_RESULT, MAX_PARTY_SIZE, CanalaveCity_SailorEldritchPartyFull\n", "")
        self.expect_fail("H1")

    def test_manaphy_full_party_consumes(self):
        self.sub(S + "scripts_canalave_city.s", "CanalaveCity_SailorEldritchPartyFull:\n    Message CanalaveCity_Text_EggWaitsForRoom\n", "CanalaveCity_SailorEldritchPartyFull:\n    SetFlag FLAG_RECEIVED_CANALAVE_CITY_MANAPHY_EGG\n    Message CanalaveCity_Text_EggWaitsForRoom\n")
        self.expect_fail("H2")

    def test_phione_special_case_removed(self):
        p = self.tree / "src/pokemon.c"
        p.write_text(p.read_text().replace("SPECIES_PHIONE", "SPECIES_XXXX"))
        self.expect_fail("H4")

    def test_secret_key_before_capture(self):
        self.sub(S + "scripts_old_chateau_back_middle_west_room.s", "    SetFlag FLAG_CAUGHT_OLD_CHATEAU_ROTOM\n", "")
        self.expect_fail("I2")

    def test_rotom_form_removed(self):
        p = self.tree / (S + "scripts_rotoms_room.s")
        p.write_text(p.read_text().replace("ROTOM_FORM_MOW", "ROTOM_FORM_XXX"))
        self.expect_fail("I1")

    # graph
    def test_regigigas_cycle(self):
        def v(d):
            for e in d["events"]:
                if e["species"] == "SPECIES_REGIROCK":
                    e["internal_prerequisites"] = ["SPECIES_REGIGIGAS"]
        self.manifest("native", v)
        self.expect_fail("J1")


if __name__ == "__main__":
    unittest.main(verbosity=1)
