"""BM-08: sharp erasure-cap theorem witnesses and exact algebraic lower checks."""
from fractions import Fraction
from itertools import product
import unittest

from correlated_minimax import apply_correlated_mask, mask_marginals
from frontier_bounds import full_cycle_law, tv_distance
from hypothesis_aware_cycle_erasure import (
    erasure_parity_class_masks, erasure_per_bit_cap
)
from sharp_erasure_optimality import (
    algebraic_optimality_certificate, clean_full_walsh,
    common_channel_cap, common_one_hot_masks, critical_erasure_cap,
    masked_distributions, overlap_lower_bound_for_erasing_pair,
    parity_class_candidate_cap, proof_regime, sharp_erasure_masks,
    verify_sharp_witness,
)


def mixed_mask_laws(a,b,mix: Fraction):
    """An independent exact convex-combination oracle for mask laws."""
    mix=Fraction(mix)
    if not 0<=mix<=1:
        raise ValueError("convex weight outside [0,1]")
    return {x:mix*a.get(x,0)+(1-mix)*b.get(x,0)
            for x in a.keys()|b.keys() if mix*a.get(x,0)+(1-mix)*b.get(x,0)>0}


class SharpErasureOptimalityTests(unittest.TestCase):
    def test_optimal_constructive_zero_tv_all_seed_alphabets(self):
        for q in (2,4,8,16,32):
            for length in range(2,8):
                self.assertTrue(verify_sharp_witness(q,length))
                a,b=masked_distributions(q,length)
                self.assertEqual(a,b)
                self.assertEqual(tv_distance(a,b),0)
                m0,m1=sharp_erasure_masks(q,length)
                t=critical_erasure_cap(q,length)
                for law in (m0,m1):
                    self.assertEqual(sum(law.values()),1)
                    self.assertEqual(mask_marginals(law),(t,)*length)
                self.assertEqual(algebraic_optimality_certificate(q,length)[
                    "critical"],t)

    def test_four_label_existing_construction_was_suboptimal(self):
        for length in range(3,8):
            common=common_channel_cap(length)
            previous=erasure_per_bit_cap(length,4)
            self.assertEqual(critical_erasure_cap(4,length),common)
            self.assertGreater(previous,common)
            common_masks=common_one_hot_masks(length)
            self.assertEqual(sharp_erasure_masks(4,length),
                             (common_masks,common_masks))
            self.assertEqual(proof_regime(4,length),
                             "q4-opposite-or-zero-full-Walsh")
        self.assertEqual(critical_erasure_cap(4,2),Fraction(1,4))

    def test_eight_and_more_labels_previous_BM07_attains_the_optimum(self):
        for q in (8,16,32):
            for length in range(2,8):
                self.assertEqual(critical_erasure_cap(q,length),
                                 erasure_per_bit_cap(length,q))
                self.assertEqual(sharp_erasure_masks(q,length),
                                 erasure_parity_class_masks(length,q))
                self.assertLess(critical_erasure_cap(q,length),
                                common_channel_cap(length))

    def test_binary_clean_parity_union_threshold(self):
        for length in range(2,8):
            self.assertEqual(proof_regime(2,length),"binary-parity-union")
            self.assertEqual(critical_erasure_cap(2,length),
                             Fraction(1,2*length))
            self.assertTrue(verify_sharp_witness(2,length))

    def test_first_Walsh_coefficient_sign_regimes_for_q4_and_q8(self):
        for length in range(2,8):
            a,b=clean_full_walsh(4,length)
            if length%2:
                self.assertEqual(a,-b)
                self.assertLess(a,0)
                self.assertGreater(b,0)
            else:
                self.assertGreater(a,0)
                self.assertEqual(b,0)
            a,b=clean_full_walsh(8,length)
            self.assertGreater(a,0)
            self.assertGreater(b,0)

    def test_exact_forced_mass_overlap_certificate_at_achieving_masks(self):
        for q in (4,8,16):
            for length in range(2,7):
                m0,m1=sharp_erasure_masks(q,length)
                c=overlap_lower_bound_for_erasing_pair(q,length,m0,m1)
                self.assertTrue(c["matches_theorem"])
                self.assertEqual(c["observed_cap"],critical_erasure_cap(q,length))
                self.assertEqual(c["necessary_cap"],critical_erasure_cap(q,length))
                if q>=8:
                    self.assertEqual(c["shared_odd_mass"],0)
                    self.assertEqual(c["forced_mass"],
                                     Fraction(q, (q-2)**length+
                                              ((q-1) if length%2==0 else 1)*2**length))
                else:
                    self.assertEqual(c["forced_mass"],0)
                    self.assertEqual(c["shared_odd_mass"],Fraction(1,2))

    def test_nontrivial_convex_mixtures_satisfy_lower_certificate(self):
        for q,length in ((8,3),(8,4),(16,3),(16,4)):
            a,b=erasure_parity_class_masks(length,q)
            common=common_one_hot_masks(length)
            for w in (Fraction(0),Fraction(1,3),Fraction(1,2),Fraction(1)):
                m0=mixed_mask_laws(common,a,w)
                m1=mixed_mask_laws(common,b,w)
                cert=overlap_lower_bound_for_erasing_pair(q,length,m0,m1)
                t=w*common_channel_cap(length)+(1-w)*erasure_per_bit_cap(length,q)
                self.assertEqual(cert["observed_cap"],t)
                self.assertEqual(cert["necessary_cap"],t)
                self.assertEqual(cert["shared_odd_mass"],w/2)
                self.assertTrue(cert["matches_theorem"])

    def test_bad_perturbation_pair_rejected(self):
        q,length=8,3
        a,b=sharp_erasure_masks(q,length)
        with self.assertRaises(ValueError):
            overlap_lower_bound_for_erasing_pair(q,length,a,a)
        with self.assertRaises(ValueError):
            overlap_lower_bound_for_erasing_pair(q,length,{(False,)*length:2},b)

    def test_closed_form_sample_caps_and_earlier_corrected_cases(self):
        expected={
            (2,2):Fraction(1,4),(2,3):Fraction(1,6),
            (4,2):Fraction(1,4),(4,3):Fraction(1,6),
            (4,4):Fraction(1,8),(4,5):Fraction(1,10),
            (8,2):Fraction(1,8),(8,3):Fraction(1,14),
            (8,4):Fraction(1,44),(8,5):Fraction(1,122),
            (16,2):Fraction(1,16),(16,3):Fraction(1,86),
            (16,4):Fraction(1,604),
        }
        for key,want in expected.items():
            self.assertEqual(critical_erasure_cap(*key),want)

    def test_input_validation(self):
        for q,L in ((1,3),(3,3),(8,1),(0,2),(8,0)):
            with self.assertRaises(ValueError):
                critical_erasure_cap(q,L)
        with self.assertRaises(ValueError):
            parity_class_candidate_cap(2,3)
        with self.assertRaises(ValueError):
            common_channel_cap(1)


if __name__=="__main__":
    unittest.main()
