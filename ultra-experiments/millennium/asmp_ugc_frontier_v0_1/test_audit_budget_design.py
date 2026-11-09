"""BM-05 independent exact policy enumeration with restoration-resource charges."""
from fractions import Fraction
from itertools import product
import unittest

from audit_budget_design import AuditResourceModel, optimal_costed_monitor
from finite_sample_monitor import noisy_failure_count_law


def brute_two_episode_costed(
    q: int, length: int, hard_budget: int, model: AuditResourceModel
) -> Fraction:
    """Enumerate every first action and every map first-count -> second action.

    The test computes posterior weights directly, with terminal MAP on both
    the stop and two-measurement branches. No policy recursion is imported.
    """
    p0 = noisy_failure_count_law(length,q,flat=True,flip_probability=0)
    p1 = noisy_failure_count_law(length,q,flat=False,flip_probability=0)
    price = Fraction(model.utility_price_per_unit)
    best = max(Fraction(1,q),Fraction(0))
    for first in range(q):
        cost1 = model.action_cost(first)
        if cost1 > hard_budget:
            continue
        choices = (-1,) + tuple(
            x for x in range(q)
            if model.action_cost(x) + cost1 <= hard_budget
        )
        for second_policy in product(choices, repeat=length+1):
            benefit = -q * price * cost1
            for first_count in range(length+1):
                w = tuple(
                    p0[first_count] if h == first else p1[first_count]
                    for h in range(q)
                )
                second = second_policy[first_count]
                if second < 0:
                    benefit += max(w)
                    continue
                benefit -= price * model.action_cost(second) * sum(w)
                for second_count in range(length+1):
                    benefit += max(
                        weight * (p0[second_count] if h == second else p1[second_count])
                        for h, weight in enumerate(w)
                    )
            best = max(best, benefit/q)
    return best


class AuditBudgetDesignTests(unittest.TestCase):
    def test_q4_hard_budget_finite_witness(self):
        model = AuditResourceModel(
            observation_units=1, shift_bit_units=1,
            restoration_audit_units=1, utility_price_per_unit=Fraction(1,100)
        )
        expected = {
            0: (Fraction(1,4), None, Fraction(1,4), Fraction(0)),
            1: (Fraction(121,400), 0, Fraction(5,16), Fraction(1)),
            2: (Fraction(0.32921875), 0, Fraction(89,256), Fraction(59,32)),
            4: (Fraction(0.338046875), 0, Fraction(189,512), Fraction(199,64))
        }
        for budget, (val,shift,correct,cost) in expected.items():
            out=optimal_costed_monitor(4,3,2,budget,model=model)
            self.assertEqual(out.net_utility,val)
            self.assertEqual(out.first_shift,shift)
            self.assertEqual(out.correct_identification,correct)
            self.assertEqual(out.expected_units,cost)

    def test_exact_brute_two_episode_policies_with_hard_resource_limit(self):
        model=AuditResourceModel(1,1,1,Fraction(1,100))
        for budget in (0,1,2,3,4,5):
            dp=optimal_costed_monitor(4,3,2,budget,model=model)
            brute=brute_two_episode_costed(4,3,budget,model)
            self.assertEqual(dp.net_utility,brute)

    def test_restoration_audit_charge_can_change_selected_policy(self):
        cheap=AuditResourceModel(1,1,1,Fraction(1,100))
        expensive=AuditResourceModel(1,1,4,Fraction(1,100))
        # Under resource cap four, expensive nonzero interventions cannot
        # fit into a two-episode execution with an initial passive probe.
        cheap_out=optimal_costed_monitor(4,3,2,4,model=cheap)
        expensive_out=optimal_costed_monitor(4,3,2,4,model=expensive)
        self.assertGreater(cheap_out.net_utility,expensive_out.net_utility)
        self.assertGreater(cheap_out.correct_identification,
                           expensive_out.correct_identification)

    def test_high_cost_causes_early_stop(self):
        model=AuditResourceModel(1,1,1,Fraction(1))
        for episodes in (1,2,3):
            out=optimal_costed_monitor(4,3,episodes,20,model=model)
            self.assertIsNone(out.first_shift)
            self.assertEqual(out.net_utility,Fraction(1,4))
            self.assertEqual(out.expected_units,0)

    def test_zero_resource_price_recovers_previous_uncosted_optimum(self):
        from adaptive_monitor_design import adaptive_success_probability
        model=AuditResourceModel(1,1,1,Fraction(0))
        for episodes in (0,1,2,3):
            out=optimal_costed_monitor(4,3,episodes,20,model=model)
            self.assertEqual(out.net_utility,
                             adaptive_success_probability(4,3,episodes))
            self.assertEqual(out.correct_identification,out.net_utility)

    def test_invalid_units_and_model_budgets(self):
        with self.assertRaises(ValueError):
            AuditResourceModel(observation_units=0)
        with self.assertRaises(ValueError):
            AuditResourceModel(restoration_audit_units=0)
        with self.assertRaises(ValueError):
            AuditResourceModel(utility_price_per_unit=Fraction(-1,100))
        with self.assertRaises(ValueError):
            optimal_costed_monitor(3,3,2,4)
        with self.assertRaises(ValueError):
            optimal_costed_monitor(4,3,5,20)
        with self.assertRaises(ValueError):
            optimal_costed_monitor(4,3,2,21)
        with self.assertRaises(ValueError):
            optimal_costed_monitor(4,3,2,4,readout_flip=Fraction(3,2))


if __name__=="__main__":
    unittest.main()
