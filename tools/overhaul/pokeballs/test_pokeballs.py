import unittest
from pokeball_model import ball_mod as m, catch_rate


class BallTests(unittest.TestCase):
    def test_quick(self):
        self.assertEqual(m("quick", turns=0), 50)
        self.assertEqual([m("quick", turns=t) for t in (1, 2, 30)], [10, 10, 10])

    def test_timer(self):
        self.assertEqual([m("timer", turns=t) for t in (0, 1, 2, 5, 9, 10, 11, 20, 30, 255)],
                         [10, 13, 16, 25, 37, 40, 40, 40, 40, 40])

    def test_repeat(self):
        self.assertEqual((m("repeat", caught=True), m("repeat", caught=False)), (35, 10))

    def test_nest(self):  # level-ratio model (Level Ball role)
        self.assertEqual([m("nest", user_level=u, target_level=10) for u in (5, 9, 10, 19, 20, 39, 40, 100)],
                         [10, 10, 20, 20, 35, 35, 50, 50])

    def test_dive_lure_role(self):
        self.assertEqual((m("dive", terrain="water"), m("dive", terrain="land")), (40, 10))

    def test_net_dusk(self):
        self.assertEqual([m("net", target_types=t) for t in (("water",), ("bug", "flying"), ("fire",))], [35, 35, 10])
        self.assertEqual([m("dusk", time="day"), m("dusk", time="night"), m("dusk", time="late_night"),
                          m("dusk", terrain="cave")], [10, 30, 30, 30])

    def test_heal(self):
        self.assertEqual(m("heal"), 15)

    def test_standard_unchanged(self):
        self.assertEqual((m("poke"), m("great"), m("ultra"), m("safari")), (10, 15, 20, 15))
        self.assertEqual((m("luxury"), m("premier")), (10, 10))

    def test_status_hp_species_unchanged(self):
        self.assertEqual(catch_rate(45, 10, 100, 100), 15)
        self.assertEqual(catch_rate(45, 10, 100, 1), 44)
        self.assertEqual(catch_rate(45, 10, 100, 100, "sleep"), 30)
        self.assertEqual(catch_rate(45, 10, 100, 100, "burn"), 22)
        self.assertEqual(catch_rate(45, 50, 100, 100), 75)


if __name__ == "__main__":
    unittest.main()


class ValidatorMutationTests(unittest.TestCase):
    def test_mutations_caught(self):
        import validate_pokeballs as v
        bs, marts, prices, man, shop = v.load()
        self.assertEqual(v.validate(bs, marts, prices, man, shop), [])
        muts = [
            ("bs", "ballMod = 50;\n            }\n            break;\n\n        case ITEM_HEAL", "ballMod = 40;\n            }\n            break;\n\n        case ITEM_HEAL"),
            ("bs", "10 + 3 * battleCtx->totalTurns", "10 + battleCtx->totalTurns"),
            ("bs", "catchRate *= 2;", "catchRate *= 3;"),
            ("bs", "ballMod = 15;\n            break;\n    ", "ballMod = 10;\n            break;\n    "),
            ("marts", "{ ITEM_GREAT_BALL, 0x2 }", "{ ITEM_GREAT_BALL, 0x3 }"),
            ("marts", "    ITEM_QUICK_BALL,\n    ITEM_DIVE_BALL,", "    ITEM_QUICK_BALL,"),
        ]
        for tgt, a, b in muts:
            args = {"bs": bs, "marts": marts}
            self.assertIn(a, args[tgt], a)
            args[tgt] = args[tgt].replace(a, b, 1)
            self.assertTrue(v.validate(args["bs"], args["marts"], prices, man, shop), a)
        self.assertTrue(v.validate(bs, marts, {**prices, "ultra_ball": 1000}, man, shop))
