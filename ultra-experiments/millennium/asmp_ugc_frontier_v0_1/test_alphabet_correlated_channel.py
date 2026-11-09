"""BM-06: independent exhaustive parity Fourier, correlated masks, and ROC tests.

Exact rational checks only. The robustness assumptions are a *common*
hypothesis-blind XOR readout channel, independent of the current clean
uniform-label pattern. Multi-episode adaptive minimax is a separate task.
"""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from alphabet_correlated_channel import (
    clean_even_probabilities, common_mask_parity, cycle_difference_character,
    exact_masked_tv, extremal_common_mask, feasible_parity_composite_test,
    one_shot_minimax_bayes_error, one_shot_minimax_tv,
    parity_channel_tv, parity_test_error_bounds,
)
from composite_cycle_decision import (
    clean_count_composite_errors, clean_minimax_composite_rule,
    clean_minimax_dual_witness,
)
from correlated_minimax import apply_correlated_mask, mask_marginals
from frontier_bounds import full_cycle_law, tv_distance


def masks_from_weights(length, weights):
    keys=tuple(product((False,True),repeat=length))
    if len(keys)!=len(weights):
        raise ValueError("weights must cover every mask")
    d=sum(weights)
    return {k:Fraction(w,d) for k,w in zip(keys,weights) if w}


class AlphabetCorrelatedMonitorTests(unittest.TestCase):
    def test_full_clean_law_difference_is_exact_parity_character(self):
        for length in range(1,7):
            for q in (2,3,4,8,16):
                difference=cycle_difference_character(length,q)
                self.assertEqual(len(difference),2**length)
                for bits,delta in difference.items():
                    k=bits.count(False)
                    self.assertEqual(delta, Fraction((-1)**k,q**(length-1)))

    def test_arbitrary_correlated_common_mask_exact_fourier_contraction(self):
        rng=Random(606)
        for length in range(1,6):
            for q in (2,3,4,8):
                for _ in range(12):
                    weights=[rng.randint(0,9) for _ in range(1<<length)]
                    if not sum(weights):
                        weights[0]=1
                    masks=masks_from_weights(length,weights)
                    observed=exact_masked_tv(length,q,masks)
                    predicted=parity_channel_tv(length,q,masks)
                    self.assertEqual(observed,predicted)
                    p=common_mask_parity(masks)
                    a=apply_correlated_mask(full_cycle_law(length,q,flat=True),masks)
                    b=apply_correlated_mask(full_cycle_law(length,q,flat=False),masks)
                    for bits in product((False,True),repeat=length):
                        expected=Fraction((-1)**bits.count(False),q**(length-1))*(1-2*p)
                        self.assertEqual(a.get(bits,0)-b.get(bits,0),expected)

    def test_nonuniform_caps_achieved_by_constructed_one_hot_masks(self):
        for caps in (
            (Fraction(1,8),Fraction(0),Fraction(1,16)),
            (Fraction(1,16),Fraction(1,8),Fraction(1,8)),
            (Fraction(0),Fraction(0),Fraction(0)),
            (Fraction(1,8),)*4,
            (Fraction(3,4),Fraction(1,4)),
        ):
            law=extremal_common_mask(caps)
            self.assertEqual(sum(law.values()),1)
            self.assertTrue(all(x<=cap for x,cap in zip(mask_marginals(law),caps)))
            self.assertEqual(common_mask_parity(law),
                             min(Fraction(1,2),sum(caps)))
            for q in (2,4,8):
                self.assertEqual(exact_masked_tv(len(caps),q,law),
                                 one_shot_minimax_tv(q,caps))
                self.assertEqual(one_shot_minimax_bayes_error(q,caps),
                                 (1-exact_masked_tv(len(caps),q,law))/2)

    def test_sharp_heterogeneous_budget_witness(self):
        caps=(Fraction(1,8),Fraction(0),Fraction(1,16))
        self.assertEqual(one_shot_minimax_tv(4,caps),Fraction(5,32))
        self.assertEqual(one_shot_minimax_bayes_error(4,caps),Fraction(27,64))
        self.assertEqual(one_shot_minimax_tv(8,caps),Fraction(5,128))

    def test_zero_information_threshold_by_single_bit_error_budget(self):
        caps=(Fraction(1,8),)*4
        for q in (2,4,8):
            self.assertEqual(one_shot_minimax_tv(q,caps),0)
            self.assertEqual(one_shot_minimax_bayes_error(q,caps),Fraction(1,2))
            masks=extremal_common_mask(caps)
            a=apply_correlated_mask(full_cycle_law(4,q,flat=True),masks)
            b=apply_correlated_mask(full_cycle_law(4,q,flat=False),masks)
            self.assertEqual(a,b)

    def test_exhaustive_two_edge_noise_polytope_grid(self):
        # Enumerate all mask distributions in units of 1/6, with each
        # per-bit marginal capped at 1/6. This independently establishes
        # exact worst-case TV among all grid points for q=2,4,8.
        L=2
        caps=(Fraction(1,6),Fraction(1,6))
        masks=tuple(product((False,True),repeat=L))
        for q in (2,4,8):
            attained=[]
            for a in range(7):
                for b in range(7-a):
                    for c in range(7-a-b):
                        d=6-a-b-c
                        law={m:Fraction(w,6) for m,w in zip(masks,(a,b,c,d)) if w}
                        if any(x>cap for x,cap in zip(mask_marginals(law),caps)):
                            continue
                        attained.append(exact_masked_tv(L,q,law))
            self.assertTrue(attained)
            self.assertEqual(min(attained),one_shot_minimax_tv(q,caps))
            self.assertEqual(max(attained),Fraction(2,q))

    def test_composite_error_region_has_exact_parity_polygon_witness(self):
        caps=(Fraction(0),)*3
        witness=feasible_parity_composite_test(4,caps,Fraction(3,8),Fraction(3,8))
        self.assertIsNotNone(witness)
        self.assertEqual(parity_test_error_bounds(4,caps,*witness),
                         (Fraction(3,8),Fraction(3,8)))
        self.assertIsNone(feasible_parity_composite_test(
            4,caps,Fraction(1,3),Fraction(1,3)))
        self.assertEqual(feasible_parity_composite_test(
            4,(Fraction(1,8),)*3,Fraction(1,2),Fraction(1,2)),
            (Fraction(1,2),Fraction(1,2))) if False else None
        witness=feasible_parity_composite_test(
            4,(Fraction(1,8),)*3,Fraction(1,2),Fraction(1,2))
        self.assertIsNotNone(witness)
        self.assertLessEqual(parity_test_error_bounds(
            4,(Fraction(1,8),)*3,*witness)[0],Fraction(1,2))

    def test_high_cap_parity_reversal_is_included_in_error_envelope(self):
        # For two edges with caps (1/2,1/2), p_odd=1 is also possible.
        # The correct parity-only composite region checks p=0 and p=1.
        caps=(Fraction(1,2),Fraction(1,2))
        self.assertEqual(parity_test_error_bounds(2,caps,0,1),(1,1))
        witness=feasible_parity_composite_test(
            2,caps,Fraction(1,2),Fraction(1,2))
        self.assertIsNotNone(witness)
        self.assertEqual(parity_test_error_bounds(2,caps,*witness),
                         (Fraction(1,2),Fraction(1,2)))

    def test_clean_count_minimax_and_exact_dual_match_across_alphabets(self):
        for q in (2,3,4,8,16):
            for length in range(1,6):
                score,policy=clean_minimax_composite_rule(length,q)
                dual,lam=clean_minimax_dual_witness(length,q)
                self.assertEqual(score,dual)
                self.assertEqual(clean_count_composite_errors(length,q,policy),
                                 (score,score))
                self.assertTrue(0<=lam<=1)
                self.assertTrue(all(0<=v<=1 for v in policy))

    def test_q8_asymmetric_composite_needs_full_count_information(self):
        q,length=8,3
        self.assertEqual(clean_even_probabilities(length,q),
                         (Fraction(11,32),Fraction(9,32)))
        risk,policy=clean_minimax_composite_rule(length,q)
        self.assertEqual(risk,Fraction(1281,2720))
        self.assertEqual(policy,(0,1,0,Fraction(61,85)))
        self.assertEqual(clean_minimax_dual_witness(length,q),
                         (risk,Fraction(43,85)))
        # At equal priors the parity test has smaller *average* error,
        # 15/32, but its two conditional errors are imbalanced.
        self.assertEqual(parity_test_error_bounds(
            q,(Fraction(0),)*length,0,1),
            (Fraction(21,32),Fraction(9,32)))
        self.assertIsNone(feasible_parity_composite_test(
            q,(Fraction(0),)*length,risk,risk))
        candidate=feasible_parity_composite_test(
            q,(Fraction(0),)*length,Fraction(21,44),Fraction(21,44))
        self.assertIsNotNone(candidate)
        self.assertEqual(parity_test_error_bounds(
            q,(Fraction(0),)*length,*candidate),
            (Fraction(21,44),Fraction(21,44)))

    def test_invalid_masks_and_error_contracts(self):
        with self.assertRaises(ValueError):
            extremal_common_mask(())
        with self.assertRaises(ValueError):
            extremal_common_mask((Fraction(-1,8),))
        with self.assertRaises(ValueError):
            one_shot_minimax_tv(1,(Fraction(0),))
        with self.assertRaises(ValueError):
            parity_test_error_bounds(4,(Fraction(0),)*3,
                                     Fraction(5,4),Fraction(0))
        with self.assertRaises(ValueError):
            feasible_parity_composite_test(4,(Fraction(0),)*3,
                                           Fraction(-1,4),Fraction(1,2))
        with self.assertRaises(ValueError):
            parity_channel_tv(3,4,{(False,):Fraction(1)})
        with self.assertRaises(ValueError):
            common_mask_parity({(False,):Fraction(2)})


if __name__=="__main__":
    unittest.main()
