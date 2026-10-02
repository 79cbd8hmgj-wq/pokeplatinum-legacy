"""Mutation tests: reintroducing a vanilla behaviour must make the validator fail."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import validate_breeding as V  # noqa: E402


def failures(mutate):
    src = V.load_sources()
    mutate(src)
    res = V.Results()
    V.source_checks(res, src)
    return [r[1] for r in res.failures]


class Mutations(unittest.TestCase):
    def test_clean_tree_passes(self):
        self.assertEqual(failures(lambda s: None), [])

    def test_three_ivs(self):
        f = failures(lambda s: s.update(consts=s["consts"].replace("NUM_INHERITED_IVS 4", "NUM_INHERITED_IVS 3")))
        self.assertTrue(any("NUM_INHERITED_IVS" in x for x in f))

    def test_interval_255(self):
        f = failures(lambda s: s.update(consts=s["consts"].replace("INTERVAL            128", "INTERVAL            256").replace("DAYCARE_EGG_CHECK_INTERVAL  128", "DAYCARE_EGG_CHECK_INTERVAL  256")))
        self.assertTrue(any("128" in x for x in f))

    def test_incense_back(self):
        f = failures(lambda s: s.update(daycare=s["daycare"] + "\nstatic const u16 sIncenseBabyTable[1];\n"))
        self.assertTrue(any("incense" in x for x in f))

    def test_wrong_power_mapping(self):
        f = failures(lambda s: s.update(rules=s["rules"].replace("return STAT_ATTACK;", "return STAT_DEFENSE;", 1)))
        self.assertTrue(any("Power item" in x for x in f))

    def test_ability_percent(self):
        f = failures(lambda s: s.update(rules=s["rules"].replace("INHERIT_PERCENT 80", "INHERIT_PERCENT 50")))
        self.assertTrue(any("80%" in x for x in f))

    def test_father_only_moves(self):
        f = failures(lambda s: s.update(daycare=s["daycare"].replace("builder->fatherMoves, builder->motherMoves", "builder->fatherMoves, builder->fatherMoves")))
        self.assertTrue(any("either parent" in x for x in f))

    def test_everstone_female_only(self):
        f = failures(lambda s: s.update(daycare=s["daycare"].replace("return BreedingRules_PickNatureParent(Daycare_GetEverstoneMask(daycare));", "return BoxPokemon_GetGender(Daycare_GetBoxMon(daycare, 0)) == GENDER_FEMALE ? 0 : -1;")))
        self.assertTrue(any("Everstone" in x for x in f))

    def test_flame_body_removed(self):
        f = failures(lambda s: s.update(rules=s["rules"].replace("ability == ABILITY_FLAME_BODY", "0")))
        self.assertTrue(any("Flame Body" in x for x in f))


if __name__ == "__main__":
    unittest.main()
