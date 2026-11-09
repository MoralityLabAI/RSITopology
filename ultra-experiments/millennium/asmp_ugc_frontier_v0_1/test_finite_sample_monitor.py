"""BM-03: independent exact controls for finite-sample monitoring.

Cross-check count sufficiency with the original full-pattern enumerator,
independently noisy bit-pattern convolution, and exhaustive likelihood
products. No random simulation or unsealed data is used.
"""
from fractions import Fraction
from itertools import product
import unittest

from frontier_bounds import apply_bsc, full_cycle_law, tv_distance
from finite_sample_monitor import (
    binary_hellinger_necessary_samples, binary_optimal_iid_bayes_error,
    binary_parity_signal, cycle_failure_count_law, cycle_iid_bayes_error,
    exact_iid_bayes_error, noisy_failure_count_law,
)


def aggregate_failures(law):
    length = len(next(iter(law)))
    return tuple(
        sum((p for x,p in law.items() if x.count(False)==k), Fraction(0))
        for k in range(length+1)
    )


def direct_bayes_error(law0,law1,n):
    """Independent exhaustive full-pattern product hypothesis test."""
    patterns = tuple(set(law0) | set(law1))
    overlap = Fraction(0)
    for sequence in product(patterns,repeat=n):
        p0=Fraction(1)
        p1=Fraction(1)
        for pattern in sequence:
            p0*=law0.get(pattern,Fraction(0))
            p1*=law1.get(pattern,Fraction(0))
        overlap+=min(p0,p1)
    return overlap/2


class FiniteSampleMonitorTests(unittest.TestCase):
    def test_clean_failure_count_matches_full_pattern_aggregation(self):
        for q in (2,3,4,8):
            for length in range(1,6):
                for flat in (False,True):
                    predicted=cycle_failure_count_law(length,q,flat=flat)
                    independent=aggregate_failures(full_cycle_law(length,q,flat=flat))
                    self.assertEqual(predicted,independent)

    def test_noisy_failure_counts_match_independent_full_pattern_channel(self):
        for q in (2,4):
            for length in range(1,5):
                for flat in (False,True):
                    clean=full_cycle_law(length,q,flat=flat)
                    for eta in (Fraction(0),Fraction(1,8),Fraction(1,2),Fraction(3,4)):
                        expected=aggregate_failures(apply_bsc(clean,eta))
                        observed=noisy_failure_count_law(length,q,flat=flat,
                                                         flip_probability=eta)
                        self.assertEqual(observed,expected)

    def test_one_sample_error_is_tv_identity(self):
        for length in range(1,6):
            for q in (2,4,8):
                expected=(1-Fraction(2,q)**(length-1))/2
                self.assertEqual(cycle_iid_bayes_error(length,q,1),expected)

    def test_full_pattern_two_sample_likelihood_matches_count_histogram(self):
        for q,length in ((2,3),(4,3),(4,4)):
            a=full_cycle_law(length,q,flat=True)
            b=full_cycle_law(length,q,flat=False)
            self.assertEqual(cycle_iid_bayes_error(length,q,2),
                             direct_bayes_error(a,b,2))

    def test_exact_multi_episode_example_q4_length_four(self):
        self.assertEqual(cycle_iid_bayes_error(4,4,1),Fraction(7,16))
        self.assertEqual(cycle_iid_bayes_error(4,4,2),Fraction(205,512))
        self.assertEqual(cycle_iid_bayes_error(4,4,3),Fraction(24409,65536))
        self.assertEqual(cycle_iid_bayes_error(4,4,8),
                         Fraction(581854902983,2199023255552))
        # Comparing only all-satisfied events under an equal prior incurs
        # much more error: on a flat cycle chance of this event is 1/64.
        all_satisfied_one_sided=Fraction(1,2)*Fraction(63,64)**8
        self.assertGreater(all_satisfied_one_sided,cycle_iid_bayes_error(4,4,8))

    def test_binary_closed_majority_test_matches_full_noisy_pattern_likelihood(self):
        for length in (1,2,3,4):
            for eta in (Fraction(0),Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1)):
                for n in (1,2,3,4,5):
                    self.assertEqual(binary_optimal_iid_bayes_error(length,eta,n),
                                     cycle_iid_bayes_error(length,2,n,flip_probability=eta))

    def test_hellinger_lower_bound_is_necessary_but_not_sufficient(self):
        target=Fraction(1,3)
        for length,bound,actual in ((1,1,1),(2,2,3),(3,8,13),(4,31,47)):
            eta=Fraction(1,4)
            self.assertEqual(binary_hellinger_necessary_samples(length,eta,target),
                             bound)
            t=binary_parity_signal(length,eta)
            self.assertLessEqual((1-t*t)**bound,4*target*(1-target))
            if bound>1:
                self.assertGreater((1-t*t)**(bound-1),4*target*(1-target))
            self.assertGreater(binary_optimal_iid_bayes_error(length,eta,actual-1),
                               target) if actual>1 else None
            self.assertLessEqual(binary_optimal_iid_bayes_error(length,eta,actual),
                                 target)
            self.assertGreaterEqual(actual,bound)

    def test_exact_independence_assumption_matters(self):
        # Correlated noise flips ALL bits together. For a binary even
        # cycle, that leaves parity untouched at any eta, whereas iid
        # BSC(1/2) removes all parity information.
        a=full_cycle_law(4,2,flat=True)
        b=full_cycle_law(4,2,flat=False)
        eta=Fraction(1,2)
        def global_flip(law):
            return {p:(1-eta)*law.get(p,Fraction(0)) +
                    eta*law.get(tuple(not v for v in p),Fraction(0))
                    for p in product((False,True),repeat=4)}
        self.assertEqual(tv_distance(global_flip(a),global_flip(b)),1)
        self.assertEqual(tv_distance(apply_bsc(a,eta),apply_bsc(b,eta)),0)

    def test_invalid_contracts_and_budget(self):
        with self.assertRaises(ValueError):
            cycle_failure_count_law(0,4,flat=True)
        with self.assertRaises(ValueError):
            noisy_failure_count_law(4,2,flat=True,flip_probability=Fraction(3,2))
        with self.assertRaises(ValueError):
            cycle_iid_bayes_error(4,4,0)
        with self.assertRaises(ValueError):
            exact_iid_bayes_error((Fraction(1),),(Fraction(1),),1,max_histograms=0)
        with self.assertRaises(ValueError):
            cycle_iid_bayes_error(4,4,10,max_histograms=1)
        with self.assertRaises(ValueError):
            binary_optimal_iid_bayes_error(3,Fraction(1,2),0)
        self.assertIsNone(binary_hellinger_necessary_samples(
            4,Fraction(1,2),Fraction(1,3)))
        with self.assertRaises(ValueError):
            binary_hellinger_necessary_samples(4,Fraction(1,4),
                                              Fraction(1,3),max_samples=1)


if __name__ == "__main__":
    unittest.main()
