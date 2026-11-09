"""BM-05 exact noise-class and restoration confounding adversarial controls."""
from fractions import Fraction
from itertools import product
from math import comb
import unittest

from correlated_minimax import (
    apply_correlated_mask, binary_majority_error_from_signal,
    conditional_false_restoration_union_bound, conditional_minimax_error,
    least_favorable_masks, marginal_only_persistent_burst_floor,
    mask_marginals, minimum_guaranteed_parity_signal, parity_flip_budget,
    restoration_observation_class,
)
from frontier_bounds import full_cycle_law, tv_distance
from finite_sample_monitor import binary_parity_signal


def independent_full_sequence_error(
    flat_law, frustrated_law, episodes
):
    """Independent full-pattern Bayes error oracle, no parity DP imports."""
    words = tuple(set(flat_law) | set(frustrated_law))
    overlap = Fraction(0)
    for seq in product(words, repeat=episodes):
        p = Fraction(1)
        q = Fraction(1)
        for event in seq:
            p *= flat_law.get(event, Fraction(0))
            q *= frustrated_law.get(event, Fraction(0))
        overlap += min(p, q)
    return overlap / 2


class CorrelatedMinimaxTests(unittest.TestCase):
    def test_zero_and_single_flip_mixture_is_exact_least_favorable(self):
        for ell in range(1, 7):
            for eta in (Fraction(0), Fraction(1, 20), Fraction(1, 8),
                        Fraction(1, 4), Fraction(1, 2)):
                masks = least_favorable_masks(ell, eta)
                self.assertEqual(sum(masks.values()), 1)
                self.assertTrue(all(m <= eta for m in mask_marginals(masks)))
                self.assertEqual(sum((p for m,p in masks.items()
                                      if sum(m) % 2), Fraction(0)),
                                 parity_flip_budget(ell, eta))
                self.assertEqual(minimum_guaranteed_parity_signal(ell, eta),
                                 1 - 2*parity_flip_budget(ell, eta))

    def test_full_pattern_channel_matches_predicted_sharp_tv(self):
        for length in range(1, 6):
            for eta in (Fraction(0), Fraction(1, 16), Fraction(1, 8),
                        Fraction(1, 4)):
                masks = least_favorable_masks(length, eta)
                p0 = apply_correlated_mask(full_cycle_law(length, 2, flat=True), masks)
                p1 = apply_correlated_mask(full_cycle_law(length, 2, flat=False), masks)
                self.assertEqual(tv_distance(p0, p1),
                                 minimum_guaranteed_parity_signal(length, eta))

    def test_enumerated_short_noise_class_cannot_erase_more_parity(self):
        # Independent grid of all joint mask laws with denominator 8,
        # satisfying each coordinate marginal bound 1/8. The extremal
        # adversarial noise is one uniform single-bit flip with prob 1/4.
        length = 2
        eta = Fraction(1, 8)
        clean0 = full_cycle_law(length, 2, flat=True)
        clean1 = full_cycle_law(length, 2, flat=False)
        masks = tuple(product((False, True), repeat=length))
        smallest = Fraction(1)
        feasible = 0
        for n0 in range(9):
            for n1 in range(9-n0):
                for n2 in range(9-n0-n1):
                    n3 = 8-n0-n1-n2
                    law = {m: Fraction(n,8) for m,n in zip(masks,(n0,n1,n2,n3))
                           if n}
                    if any(v > eta for v in mask_marginals(law)):
                        continue
                    feasible += 1
                    got = tv_distance(apply_correlated_mask(clean0,law),
                                      apply_correlated_mask(clean1,law))
                    smallest = min(smallest, got)
        self.assertGreater(feasible, 1)
        self.assertEqual(smallest, Fraction(1, 2))

    def test_iid_bit_flip_signal_is_stronger_than_worst_correlation(self):
        ell, eta = 4, Fraction(1, 8)
        iid = binary_parity_signal(ell, eta)
        minimax = minimum_guaranteed_parity_signal(ell, eta)
        self.assertEqual(iid, Fraction(81,256))
        self.assertEqual(minimax, 0)
        self.assertEqual(conditional_minimax_error(ell,eta,1),Fraction(1,2))

    def test_conditional_minimax_exact_full_law_for_multiple_episodes(self):
        for ell, eta, episodes in (
            (2,Fraction(1,8),2), (3,Fraction(1,16),2),
            (4,Fraction(1,16),2), (3,Fraction(1,8),3)
        ):
            masks = least_favorable_masks(ell, eta)
            p0 = apply_correlated_mask(full_cycle_law(ell,2,flat=True),masks)
            p1 = apply_correlated_mask(full_cycle_law(ell,2,flat=False),masks)
            expected = independent_full_sequence_error(p0,p1,episodes)
            self.assertEqual(conditional_minimax_error(ell,eta,episodes), expected)
            self.assertEqual(binary_majority_error_from_signal(
                minimum_guaranteed_parity_signal(ell,eta), episodes), expected)

    def test_sharp_three_shot_conditional_and_persistent_burst_separation(self):
        ell, eta = 4, Fraction(1,16)
        self.assertEqual(parity_flip_budget(ell,eta),Fraction(1,4))
        self.assertEqual(conditional_minimax_error(ell,eta,3),Fraction(5,32))
        # Reusing one hidden mask across all episodes leaves an irreducible
        # 25% ambiguity even as the number of episodes increases.
        self.assertEqual(marginal_only_persistent_burst_floor(ell,eta),
                         Fraction(1,4))
        self.assertLess(conditional_minimax_error(ell,eta,3),
                        marginal_only_persistent_burst_floor(ell,eta))

    def test_restoration_drift_is_indistinguishable_from_true_holonomy(self):
        for x in range(4):
            self.assertEqual(restoration_observation_class(1,2,x,4),
                             restoration_observation_class(3,0,x,4))
        with self.assertRaises(ValueError):
            restoration_observation_class(0,0,0,3)
        with self.assertRaises(ValueError):
            restoration_observation_class(4,0,0,4)

    def test_restoration_audit_conditional_union_bound(self):
        self.assertEqual(conditional_false_restoration_union_bound(
            (Fraction(1,100),Fraction(1,200),Fraction(1,200))),
            Fraction(1,50))
        self.assertEqual(conditional_false_restoration_union_bound(()),0)
        self.assertEqual(conditional_false_restoration_union_bound((1,1)),1)
        with self.assertRaises(ValueError):
            conditional_false_restoration_union_bound((Fraction(-1, 10),))
        with self.assertRaises(ValueError):
            conditional_false_restoration_union_bound((Fraction(11, 10),))

    def test_shared_burst_multi_episode_error_floor_independent_oracle(self):
        # Draw ONE hidden mask, then fresh parity-coset labelings every
        # episode. Under either hypothesis the mask parity is a persistent
        # hidden bit. Exact exhaustive observation histories retain its
        # one-shot Bayes error, unlike conditionally budgeted masks.
        ell, eta = 3, Fraction(1,12)
        masks = least_favorable_masks(ell,eta)
        pstar = parity_flip_budget(ell,eta)
        flat = full_cycle_law(ell,2,flat=True)
        nonflat = full_cycle_law(ell,2,flat=False)
        outcomes=tuple(product((False,True),repeat=ell))
        for episodes in (1,2):
            overlap=Fraction(0)
            for history in product(outcomes, repeat=episodes):
                masses=[]
                for clean in (flat,nonflat):
                    total=Fraction(0)
                    for mask,maskprob in masks.items():
                        likelihood=Fraction(1)
                        for observed in history:
                            unmasked=tuple(x != bit for x,bit in zip(observed,mask))
                            likelihood*=clean.get(unmasked,Fraction(0))
                        total+=maskprob*likelihood
                    masses.append(total)
                overlap+=min(masses)
            self.assertEqual(overlap/2,pstar)
        self.assertGreater(pstar,conditional_minimax_error(ell,eta,3))

    def test_restoration_alias_extends_to_full_cycle_laws_for_all_actions(self):
        for action in range(4):
            effective_a=restoration_observation_class(1,2,action,4)
            effective_b=restoration_observation_class(3,0,action,4)
            self.assertEqual(effective_a,effective_b)
            a=full_cycle_law(3,4,flat=(effective_a==0))
            b=full_cycle_law(3,4,flat=(effective_b==0))
            self.assertEqual(a,b)

    def test_probability_validations(self):
        with self.assertRaises(ValueError):
            least_favorable_masks(0,Fraction(1,4))
        with self.assertRaises(ValueError):
            least_favorable_masks(4,Fraction(5,4))
        with self.assertRaises(ValueError):
            binary_majority_error_from_signal(Fraction(5,4),1)
        with self.assertRaises(ValueError):
            conditional_minimax_error(4,Fraction(1,8),0)
        with self.assertRaises(ValueError):
            apply_correlated_mask({(False,):Fraction(1)}, {(False,False):Fraction(1)})


if __name__ == "__main__":
    unittest.main()
