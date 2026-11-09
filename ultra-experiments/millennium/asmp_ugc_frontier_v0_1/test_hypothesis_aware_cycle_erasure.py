"""BM-07/T2: independent exact validations of all-length cycle erasure masks."""
from fractions import Fraction
from itertools import product
import unittest

from hypothesis_aware_cycle_erasure import (
    active_erased_cycle_response, common_erasure_per_bit_cap,
    equalized_output_laws, erasure_mask_atom, erasure_parity_class_masks,
    erasure_per_bit_cap,
)
from hypothesis_aware_two_edge import erasure_threshold, extremal_output_laws
from frontier_bounds import full_cycle_law, tv_distance
from correlated_minimax import apply_correlated_mask, mask_marginals
from finite_seed import Game, satisfaction_law


class HypothesisAwareCycleErasureTests(unittest.TestCase):
    def test_exact_output_equality_for_simple_cycles_through_length_six(self):
        for q in (4,8,16,32):
            for length in (2,3,4,5,6):
                m0,m1=erasure_parity_class_masks(length,q)
                self.assertEqual(sum(m0.values()),1)
                self.assertEqual(sum(m1.values()),1)
                per_bit=erasure_per_bit_cap(length,q)
                self.assertTrue(all(v==per_bit for v in mask_marginals(m0)))
                self.assertTrue(all(v==per_bit for v in mask_marginals(m1)))
                a,b=equalized_output_laws(length,q)
                self.assertEqual(a,b)
                self.assertEqual(tv_distance(a,b),0)

    def test_eight_label_closed_exact_thresholds_decay_with_cycle_length(self):
        expected={
            2:Fraction(1,8),
            3:Fraction(1,14),
            4:Fraction(1,44),
            5:Fraction(1,122),
        }
        for length,cap in expected.items():
            self.assertEqual(erasure_per_bit_cap(length,8),cap)
            self.assertLess(cap,common_erasure_per_bit_cap(length))
        self.assertEqual(erasure_per_bit_cap(3,16),Fraction(1,86))
        self.assertEqual(erasure_per_bit_cap(4,16),Fraction(1,604))

    def test_simple_triangle_q8_independent_direct_label_enumeration(self):
        q,length=8,3
        pairs=((0,1),(1,2),(2,0))
        base=Game(3,3,tuple((u,v,0) for u,v in pairs))
        bad=Game(3,3,tuple((u,v,1 if i==2 else 0)
                          for i,(u,v) in enumerate(pairs)))
        independent0=satisfaction_law(base,(0,1,2))
        independent1=satisfaction_law(bad,(0,1,2))
        self.assertEqual(independent0,full_cycle_law(length,q,flat=True))
        self.assertEqual(independent1,full_cycle_law(length,q,flat=False))
        mask0,mask1=erasure_parity_class_masks(length,q)
        masked0=apply_correlated_mask(independent0,mask0)
        masked1=apply_correlated_mask(independent1,mask1)
        self.assertEqual(masked0,masked1)
        self.assertEqual(sum(masked0.values()),1)

    def test_parity_class_formula_and_nonnegative_zero_probability(self):
        for q in (4,8,16):
            for length in range(2,7):
                a=erasure_mask_atom(length,q)
                d=(q-2)**length + ((q-1) if length%2==0 else 1)*2**length
                self.assertEqual(a,Fraction(q,d))
                m0,m1=erasure_parity_class_masks(length,q)
                self.assertTrue(all(v>=0 for v in m0.values()))
                self.assertTrue(all(v>=0 for v in m1.values()))
                for mask,p in m0.items():
                    if any(mask):
                        self.assertEqual(sum(mask)%2,1-length%2)
                        self.assertEqual(p,a)
                for mask,p in m1.items():
                    if any(mask):
                        self.assertEqual(sum(mask)%2,length%2)
                        self.assertEqual(p,a)

    def test_parity_masks_have_matching_Walsh_transforms_after_channel(self):
        for q in (8,16):
            for length in (3,4,5):
                m0,m1=erasure_parity_class_masks(length,q)
                clean0=full_cycle_law(length,q,flat=True)
                clean1=full_cycle_law(length,q,flat=False)
                # Independent Fourier-domain equality for every subset S.
                for subset in range(1<<length):
                    def hat(law):
                        return sum(
                            (p if (sum(v for i,v in enumerate(bits)
                                       if subset & (1<<i))%2)==0 else -p
                             for bits,p in law.items()),Fraction(0))
                    self.assertEqual(hat(clean0)*hat(m0),
                                     hat(clean1)*hat(m1))

    def test_active_multi_round_simple_cycle_remains_uninformative(self):
        length,q=3,8
        first_shift=2
        responses=[]
        alphabet=list(product((False,True),repeat=length))
        for h in range(q):
            first=active_erased_cycle_response(length,q,h,first_shift)
            joint={}
            for y0 in alphabet:
                next_shift=(first_shift+1+
                            sum((1<<j) for j,v in enumerate(y0) if v))%q
                next_law=active_erased_cycle_response(length,q,h,next_shift)
                for y1 in alphabet:
                    joint[(y0,next_shift,y1)]=first.get(y0,0)*next_law.get(y1,0)
            self.assertEqual(sum(joint.values()),1)
            responses.append(joint)
        self.assertTrue(all(law==responses[0] for law in responses))

    def test_two_edge_formula_recovers_exact_minimax_erasure(self):
        for q in (4,8,16,32):
            self.assertEqual(erasure_per_bit_cap(2,q),erasure_threshold(q))
            constructed0,constructed1=equalized_output_laws(2,q)
            earlier0,earlier1=extremal_output_laws(q,erasure_threshold(q))
            self.assertEqual(constructed0,constructed1)
            self.assertEqual(constructed0,earlier0)
            self.assertEqual(constructed1,earlier1)

    def test_correct_non_power_of_two_and_small_length_guards(self):
        with self.assertRaises(ValueError):
            erasure_per_bit_cap(1,8)
        with self.assertRaises(ValueError):
            erasure_mask_atom(3,3)
        with self.assertRaises(ValueError):
            erasure_mask_atom(3,2)
        with self.assertRaises(ValueError):
            active_erased_cycle_response(3,8,8,0)
        with self.assertRaises(ValueError):
            active_erased_cycle_response(3,8,0,8)
        with self.assertRaises(ValueError):
            common_erasure_per_bit_cap(0)


if __name__=="__main__":
    unittest.main()
