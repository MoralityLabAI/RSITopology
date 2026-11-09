"""BM-07: exact rational adversarial-channel and active tomography controls."""
from fractions import Fraction
from itertools import product
import unittest

from hypothesis_aware_two_edge import (
    adaptive_erasure_output_law, best_deterministic_mixed_threshold,
    binomial_at_least, erasure_threshold, exact_extremal_tv,
    extremal_hypothesis_aware_masks, extremal_output_laws,
    hypothesis_aware_minimax_tv, hypothesis_blind_minimax_tv,
    mixed_count_composite_bounds, mixed_event_probabilities,
)
from frontier_bounds import full_cycle_law, tv_distance
from correlated_minimax import apply_correlated_mask, mask_marginals


MASKS=tuple(product((False,True),repeat=2))


def all_noise_grid(denominator,cap):
    """Independent exhaustive mask-law enumeration on a rational grid."""
    out=[]
    for a in range(denominator+1):
        for b in range(denominator+1-a):
            for c in range(denominator+1-a-b):
                d=denominator-a-b-c
                law={m:Fraction(k,denominator)
                     for m,k in zip(MASKS,(a,b,c,d)) if k}
                if all(m <= cap for m in mask_marginals(law)):
                    out.append(law)
    return out


class HypothesisAwareTwoEdgeTests(unittest.TestCase):
    def test_exact_closed_minimax_pair_on_multiple_alphabets(self):
        for q in (2,4,8,16):
            for eta in (Fraction(0),Fraction(1,32),Fraction(1,16),
                        Fraction(1,8),Fraction(1,4),Fraction(1,2)):
                flat_mask,frust_mask=extremal_hypothesis_aware_masks(q,eta)
                self.assertTrue(all(v<=eta for v in mask_marginals(flat_mask)))
                self.assertTrue(all(v<=eta for v in mask_marginals(frust_mask)))
                self.assertEqual(exact_extremal_tv(q,eta),
                                 hypothesis_aware_minimax_tv(q,eta))
                self.assertLessEqual(hypothesis_aware_minimax_tv(q,eta),
                                     hypothesis_blind_minimax_tv(q,eta))

    def test_exhaust_mask_laws_independently_on_rational_grid(self):
        for q,cap,denominator in (
            (2,Fraction(1,8),8),
            (4,Fraction(1,8),8),
            (8,Fraction(1,8),8),
            (8,Fraction(1,16),16),
            (16,Fraction(1,16),16),
        ):
            noise=all_noise_grid(denominator,cap)
            self.assertGreater(len(noise),1)
            clean0=full_cycle_law(2,q,flat=True)
            clean1=full_cycle_law(2,q,flat=False)
            noisy0=[apply_correlated_mask(clean0,w) for w in noise]
            noisy1=[apply_correlated_mask(clean1,w) for w in noise]
            brute=min(tv_distance(x,y) for x in noisy0 for y in noisy1)
            self.assertEqual(brute,hypothesis_aware_minimax_tv(q,cap))

    def test_q8_per_bit_one_eighth_erasure_and_common_channel_separation(self):
        q,eta=8,Fraction(1,8)
        flat,frustrated=extremal_output_laws(q,eta)
        self.assertEqual(flat,frustrated)
        self.assertEqual(flat,{
            (False,False):Fraction(21,32),
            (False,True):Fraction(1,8),
            (True,False):Fraction(1,8),
            (True,True):Fraction(3,32),
        })
        self.assertEqual(hypothesis_aware_minimax_tv(q,eta),0)
        self.assertEqual(hypothesis_blind_minimax_tv(q,eta),Fraction(1,8))
        self.assertEqual(erasure_threshold(q),Fraction(1,8))

    def test_adaptive_shift_tomography_fully_blinded_under_hypothesis_aware_mask(self):
        q,eta=8,Fraction(1,8)
        first_shift=3
        patterns=list(product((False,True),repeat=2))
        transcripts=[]
        for hidden_h in range(q):
            first_law=adaptive_erasure_output_law(q,eta,hidden_h,first_shift)
            joint={}
            for first in patterns:
                second_shift=(first_shift+1+int(first[0])+2*int(first[1]))%q
                second_law=adaptive_erasure_output_law(q,eta,hidden_h,second_shift)
                for second in patterns:
                    joint[(first,second_shift,second)]=(
                        first_law.get(first,0)*second_law.get(second,0)
                    )
            self.assertEqual(sum(joint.values()),1)
            transcripts.append(joint)
        self.assertTrue(all(x==transcripts[0] for x in transcripts))

    def test_mixed_event_bounds_hold_for_every_legal_grid_mask_law(self):
        q,eta=8,Fraction(1,16)
        a,b=mixed_event_probabilities(q,eta)
        self.assertEqual((a,b),(Fraction(1,8),Fraction(1,4)))
        noise=all_noise_grid(16,eta)
        for law in noise:
            for flat,expected in ((True,a),(False,b)):
                out=apply_correlated_mask(full_cycle_law(2,q,flat=flat),law)
                mixed=sum((p for mask,p in out.items()
                           if mask[0] != mask[1]),Fraction(0))
                if flat:
                    self.assertLessEqual(mixed,expected)
                else:
                    self.assertGreaterEqual(mixed,expected)
        ext0,ext1=extremal_output_laws(q,eta)
        self.assertEqual(sum((p for x,p in ext0.items() if x[0]!=x[1]),
                             Fraction(0)),a)
        self.assertEqual(sum((p for x,p in ext1.items() if x[0]!=x[1]),
                             Fraction(0)),b)

    def test_exact_multishot_threshold_bounds_and_sharp_stationary_masks(self):
        for q,eta,samples in (
            (2,Fraction(1,8),4),
            (4,Fraction(1,8),4),
            (8,Fraction(1,16),4),
            (16,Fraction(1,32),5),
        ):
            threshold,fp,fn=best_deterministic_mixed_threshold(q,eta,samples)
            x,y=mixed_event_probabilities(q,eta)
            self.assertEqual(fp,binomial_at_least(samples,threshold,x))
            self.assertEqual(fn,1-binomial_at_least(samples,threshold,y))
            self.assertTrue(0<=fp<=1 and 0<=fn<=1)
            out0,out1=extremal_output_laws(q,eta)
            event0=sum((v for k,v in out0.items() if k[0]!=k[1]),Fraction(0))
            event1=sum((v for k,v in out1.items() if k[0]!=k[1]),Fraction(0))
            self.assertEqual((event0,event1),(x,y))

    def test_two_edge_binary_case_sharp_erasure_at_quarter(self):
        self.assertEqual(erasure_threshold(2),Fraction(1,4))
        self.assertEqual(hypothesis_aware_minimax_tv(2,Fraction(1,8)),
                         Fraction(1,2))
        a,b=extremal_output_laws(2,Fraction(1,4))
        self.assertEqual(a,b)
        self.assertEqual(hypothesis_aware_minimax_tv(2,Fraction(1,4)),0)

    def test_positive_two_sided_monitoring_gap_and_critical_budget(self):
        for q in (4,8,16):
            cap=erasure_threshold(q)
            with self.assertRaises(ValueError):
                mixed_event_probabilities(q,cap)
            a,b=mixed_event_probabilities(q,cap/2)
            self.assertGreater(b-a,0)
            for n in (3,5,9):
                threshold,fp,fn=best_deterministic_mixed_threshold(q,cap/2,n)
                self.assertGreaterEqual(threshold,0)
                self.assertLessEqual(max(fp,fn),Fraction(1))

    def test_invalid_inputs_and_overspent_thresholds(self):
        with self.assertRaises(ValueError):
            hypothesis_aware_minimax_tv(3,Fraction(0))
        with self.assertRaises(ValueError):
            hypothesis_aware_minimax_tv(8,Fraction(-1,10))
        with self.assertRaises(ValueError):
            hypothesis_aware_minimax_tv(8,Fraction(11,10))
        with self.assertRaises(ValueError):
            adaptive_erasure_output_law(8,Fraction(0),8,0)
        with self.assertRaises(ValueError):
            adaptive_erasure_output_law(8,Fraction(0),0,8)
        with self.assertRaises(ValueError):
            mixed_count_composite_bounds(8,Fraction(1,16),0,0)
        with self.assertRaises(ValueError):
            mixed_count_composite_bounds(8,Fraction(1,16),2,4)
        with self.assertRaises(ValueError):
            binomial_at_least(-1,1,Fraction(1,2))


if __name__=="__main__":
    unittest.main()
