"""BM-04: exact adaptive active-monitor versus fixed-schedule controls.

An independent exhaustive two-step policy enumerator checks the recursively
cached dynamic program. All probabilities are exact rationals.
"""
from fractions import Fraction
from itertools import product
import unittest

from adaptive_monitor_design import (
    adaptive_success_probability, fixed_schedule_success_probability,
    optimal_second_shift_actions,
)
from finite_sample_monitor import noisy_failure_count_law


def direct_two_step_policy_optimum(q: int, length: int, eta: Fraction = Fraction(0)):
    """Brute-force every map k_first -> x_second, with first x fixed to zero.

    This implementation does not reuse the dynamic program or its symmetry
    reduction and is deliberately limited to tiny q and cycle length.
    """
    p0 = noisy_failure_count_law(length,q,flat=True,flip_probability=eta)
    p1 = noisy_failure_count_law(length,q,flat=False,flip_probability=eta)
    results=[]
    for policy in product(range(q),repeat=length+1):
        score=Fraction(0)
        for k_first in range(length+1):
            for k_second in range(length+1):
                score += max(
                    (p0[k_first] if h==0 else p1[k_first]) *
                    (p0[k_second] if h==policy[k_first] else p1[k_second])
                    for h in range(q)
                )
        results.append((score/q, policy))
    return max(result[0] for result in results)


def direct_fixed_two_step_optimum(q: int, length: int, eta: Fraction = Fraction(0)):
    p0 = noisy_failure_count_law(length,q,flat=True,flip_probability=eta)
    p1 = noisy_failure_count_law(length,q,flat=False,flip_probability=eta)
    best=Fraction(0)
    for first,second in product(range(q),repeat=2):
        score=Fraction(0)
        for k_first,k_second in product(range(length+1),repeat=2):
            score += max(
                (p0[k_first] if h==first else p1[k_first]) *
                (p0[k_second] if h==second else p1[k_second])
                for h in range(q)
            )
        best=max(best,score/q)
    return best


class AdaptiveMonitorTests(unittest.TestCase):
    def test_q4_length3_explicit_adaptive_advantage_two_steps(self):
        self.assertEqual(adaptive_success_probability(4,3,2),Fraction(189,512))
        fixed,allocation=fixed_schedule_success_probability(4,3,2)
        self.assertEqual(fixed,Fraction(183,512))
        self.assertEqual(allocation,(1,1,0,0))
        self.assertEqual(Fraction(189,512)-fixed,Fraction(3,256))
        self.assertEqual(adaptive_success_probability(4,3,2),
                         direct_two_step_policy_optimum(4,3))
        self.assertEqual(fixed,direct_fixed_two_step_optimum(4,3))

    def test_policy_uses_failure_count_to_choose_retest_or_new_probe(self):
        self.assertEqual(optimal_second_shift_actions(4,3,0),(0,1,2,3))
        self.assertEqual(optimal_second_shift_actions(4,3,1),(1,2,3))
        self.assertEqual(optimal_second_shift_actions(4,3,2),(0,))
        self.assertEqual(optimal_second_shift_actions(4,3,3),(1,2,3))

    def test_more_episodes_and_three_step_references(self):
        self.assertEqual(adaptive_success_probability(4,3,0),Fraction(1,4))
        self.assertEqual(adaptive_success_probability(4,3,1),Fraction(5,16))
        self.assertEqual(adaptive_success_probability(4,3,3),Fraction(3467,8192))
        self.assertEqual(fixed_schedule_success_probability(4,3,3),
                         (Fraction(1617,4096),(2,1,0,0)))
        prev=Fraction(0)
        for n in range(0,5):
            adaptive=adaptive_success_probability(4,3,n)
            fixed,_=fixed_schedule_success_probability(4,3,n)
            self.assertGreaterEqual(adaptive,fixed)
            self.assertGreaterEqual(adaptive,prev)
            prev=adaptive

    def test_fully_random_readout_erases_the_ability_to_identify_h(self):
        eta=Fraction(1,2)
        for n in range(0,5):
            self.assertEqual(adaptive_success_probability(
                4,3,n,flip_probability=eta),Fraction(1,4))
            self.assertEqual(fixed_schedule_success_probability(
                4,3,n,flip_probability=eta)[0],Fraction(1,4))

    def test_binary_group_one_full_cycle_observation_identifies_gain(self):
        self.assertEqual(adaptive_success_probability(2,4,0),Fraction(1,2))
        for n in (1,2,3):
            self.assertEqual(adaptive_success_probability(2,4,n),1)
            self.assertEqual(fixed_schedule_success_probability(2,4,n)[0],1)

    def test_noisy_two_episode_dynamic_program_matches_brute_policy(self):
        eta=Fraction(1,8)
        self.assertEqual(adaptive_success_probability(
            4,3,2,flip_probability=eta),
            direct_two_step_policy_optimum(4,3,eta))
        self.assertEqual(fixed_schedule_success_probability(
            4,3,2,flip_probability=eta)[0],
            direct_fixed_two_step_optimum(4,3,eta))

    def test_bounded_seed_resource_and_input_guards(self):
        with self.assertRaises(ValueError):
            adaptive_success_probability(5,3,2)
        with self.assertRaises(ValueError):
            adaptive_success_probability(4,5,2)
        with self.assertRaises(ValueError):
            adaptive_success_probability(4,3,7)
        with self.assertRaises(ValueError):
            fixed_schedule_success_probability(4,3,-1)
        with self.assertRaises(ValueError):
            optimal_second_shift_actions(4,3,4)
        with self.assertRaises(ValueError):
            optimal_second_shift_actions(4,3,1,flip_probability=Fraction(5,4))


if __name__ == "__main__":
    unittest.main()
