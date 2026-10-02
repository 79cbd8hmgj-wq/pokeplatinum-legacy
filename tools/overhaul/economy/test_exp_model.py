#!/usr/bin/env python3
"""Deterministic coverage for the conserved team-wide EXP model."""
from __future__ import annotations

import itertools
import unittest

from exp_model import Member, allocate, ev_recipients, final_exp, payout, raw_pool


def party(n, participants=(0,), holders=(), **over):
    return [Member(slot=i, participant=i in participants, exp_share=i in holders, **over) for i in range(n)]


class ExpModel(unittest.TestCase):
    def test_raw_pool_formula(self):
        self.assertEqual(raw_pool(64, 10), 91)
        self.assertEqual(raw_pool(255, 100), 3642)

    def test_conservation_across_sizes_and_groups(self):
        for n, raw in itertools.product((1, 3, 6), (0, 1, 7, 91, 100, 101, 3642)):
            for participants in ((0,), tuple(range(min(2, n))), tuple(range(n))):
                for holders in ((), (n - 1,), tuple(range(n))):
                    a = allocate(raw, party(n, participants, holders))
                    if raw * 60 // 100 >= n:  # below this only the legacy min-1 floor can add EXP
                        self.assertEqual(sum(a.values()), raw, (n, raw, participants, holders))
                    else:
                        self.assertGreaterEqual(sum(a.values()), raw)

    def test_single_active_six_party_split(self):
        a = allocate(1000, party(6))
        self.assertEqual(a[0], 600 + 67)   # 600 battle + ceil share of 400/6
        self.assertEqual([a[i] for i in range(1, 6)], [67, 67, 67, 66, 66])  # 400 % 6 = 4 -> slots 0..3
        self.assertEqual(sum(a.values()), 1000)

    def test_party_size_does_not_inflate_pool(self):
        for n in (1, 3, 6):
            self.assertEqual(sum(allocate(990, party(n)).values()), 990)

    def test_one_party_member_gets_everything(self):
        self.assertEqual(allocate(91, party(1)), {0: 91})

    def test_multiple_participants_divide_battle_pool(self):
        a = allocate(1000, party(6, participants=(0, 1)))
        self.assertEqual(a[0], 300 + 67)
        self.assertEqual(a[1], 300 + 67)
        self.assertEqual(a[2], 67)  # slots 0..3 take the team remainder

    def test_exp_share_priority_creates_no_extra_exp(self):
        base = sum(allocate(1000, party(6)).values())
        with_share = allocate(1000, party(6, holders=(5,)))
        self.assertEqual(sum(with_share.values()), base)
        self.assertEqual(with_share[0], 300 + 67)
        self.assertEqual(with_share[5], 300 + 66)  # holder is slot 5: no remainder slot

    def test_multiple_exp_shares_only_divide_battle_pool(self):
        a = allocate(1000, party(6, holders=(3, 4, 5)))
        self.assertEqual(sum(a.values()), 1000)
        self.assertEqual(a[0], 150 + 67)

    def test_participant_holding_exp_share_counted_once(self):
        once = allocate(1000, party(6, participants=(0,), holders=(0,)))
        self.assertEqual(once, allocate(1000, party(6)))

    def test_exclusions_leave_denominators_correct(self):
        p = party(6)
        p[1] = Member(1, hp=0)
        p[2] = Member(2, level=100)
        p[3] = Member(3, egg=True)
        a = allocate(1000, p)
        self.assertEqual(set(a), {0, 4, 5})
        self.assertEqual(sum(a.values()), 1000)
        self.assertEqual(a[4], 133)
        p[4] = Member(4, exp_share=True, hp=0)
        self.assertNotIn(4, allocate(1000, p))

    def test_ineligible_holders_not_in_battle_group(self):
        p = party(3)
        p[1] = Member(1, exp_share=True, level=100)
        p[2] = Member(2, exp_share=True, hp=0)
        self.assertEqual(allocate(100, p), {0: 100})

    def test_odd_pools_deterministic_remainders(self):
        a = allocate(7, party(6))
        self.assertEqual(sum(a.values()), 7)  # battle 4 -> slot0; team 3 -> slots 0..2
        self.assertEqual(a, {0: 5, 1: 1, 2: 1, 3: 0, 4: 0, 5: 0})
        self.assertEqual(allocate(7, party(6)), a)

    def test_min_one_only_for_battle_group(self):
        a = allocate(1, party(3, holders=(1,)))
        self.assertGreaterEqual(a[0], 1)
        self.assertGreaterEqual(a[1], 1)

    def test_trainer_bonus(self):
        self.assertEqual(payout(100, 70, party(1), True)[0], 1000 * 150 // 100)

    def test_lucky_egg(self):
        p = [Member(0, participant=True, lucky_egg=True)]
        self.assertEqual(payout(100, 70, p, False)[0], 1000 * 150 // 100)

    def test_traded_same_language(self):
        p = [Member(0, participant=True, traded=True)]
        self.assertEqual(payout(100, 70, p, False)[0], 1500)

    def test_traded_foreign(self):
        p = [Member(0, participant=True, traded=True, foreign=True)]
        self.assertEqual(payout(100, 70, p, False)[0], 1700)

    def test_modifier_order_and_stacking(self):
        m = Member(0, lucky_egg=True, traded=True, foreign=True)
        self.assertEqual(final_exp(333, m, True), ((333 * 150 // 100) * 150 // 100) * 170 // 100)

    def test_modifiers_apply_after_allocation_per_recipient(self):
        p = party(3)
        p[2] = Member(2, lucky_egg=True)
        a = payout(300, 7, p, True)  # raw 300
        base = allocate(300, p)
        self.assertEqual(a[2], base[2] * 150 // 100 * 150 // 100)
        self.assertEqual(a[1], base[1] * 150 // 100)

    def test_evs_participants_only(self):
        p = party(6, participants=(0, 2), holders=(4,))
        self.assertEqual(ev_recipients(p), [0, 2])
        p[2] = Member(2, participant=True, hp=0)
        self.assertEqual(ev_recipients(p), [0])

    def test_exp_share_holder_never_gets_evs_unless_participant(self):
        p = party(3, participants=(0,), holders=(1, 2))
        self.assertEqual(ev_recipients(p), [0])


class Simulation(unittest.TestCase):
    def test_deterministic_and_conserving(self):
        import simulate_progression as sp
        tables, cache = sp.load_tables(), {}
        seg, boss, aces, _ = sp.collect_segments(cache)
        wild = sp.wild_per_segment(cache)
        a = sp.simulate("normal", True, tables, seg, boss, wild, [b[2] for b in sp.BOSSES])
        b = sp.simulate("normal", True, tables, seg, boss, wild, [b[2] for b in sp.BOSSES])
        self.assertEqual(a, b)
        van = sp.simulate("normal", False, tables, seg, boss, wild, [b[2] for b in sp.BOSSES])
        # conserved pool: team-wide sharing never multiplies progression severalfold vs vanilla
        self.assertLess(a[-1]["avg"], van[-1]["avg"] * 1.5)

    def test_live_aces_near_locked_targets(self):
        # Trainer levels belong to the trainer phase; vanilla Fantina is 26 vs the locked 27 and is reported, not edited.
        import simulate_progression as sp
        _, _, aces, _ = sp.collect_segments({})
        for live, (name, _, spec) in zip(aces, sp.BOSSES):
            self.assertLessEqual(abs(live - spec), 1, name)


if __name__ == "__main__":
    unittest.main()
