"""BM-31: independent empirical-mixture, collision and mask-rigidity tests.

Two exact constructions are compared:
  (i) direct projection of a fully symmetrized finite original mask,
  (ii) sampling its empirical pair-type histogram without replacement.
An infinite exchangeable extension instead samples WITH replacement.
The error is bounded by the exact collision probability. Checks include
BM-25/26 optimal q8 world-specific masks and BM-27/30 full equalizers.
"""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from finite_empirical_extension_BM31 import (
    collision_bound,window_bounds,mask_histogram,
    empirical_joint_law,histogram_multinomial,
    expand_empirical_joint_law,directing_law,
    empirical_pair_law,without_replacement_window,
    with_replacement_window,total_variation,
    independent_project_full,exceptional_singlebit_marginal,
    certify_finite_window,growing_window_bound,
)
from state_aware_replication_BM25 import (
    expanded_full_mask_law as bm25_mask,
)
from state_aware_three_replica_BM26 import (
    full_mask_law as bm26_mask,
)
from replication_uniform_upper_BM27 import (
    explicit_mask_law as bm27_mask,
    exact_clean_law,xor_convolve,
)
from optimal_channel_rigidity_BM30 import (
    explicit_frontier_mask,
)
from repeated_gain_erasure_BM24 import gain_family
from generic_fourier_erasure_BM17 import census


def original_masks():
    yield "BM25 n2",2,bm25_mask(0),bm25_mask(1)
    yield "BM26 n3",3,bm26_mask(0),bm26_mask(1)
    for n in (1,2,3,4):
        yield f"BM27 n{n}",n,bm27_mask(n,0),bm27_mask(n,1)
    for c in (Fraction(0),Fraction(1,20),Fraction(1,13),
              Fraction(1,10)):
        for n in (2,3):
            yield f"BM30 c{c} n{n}",n,(
                explicit_frontier_mask(n,c,0)),(
                explicit_frontier_mask(n,c,1))


class BM31EmpiricalExchangeabilityTests(unittest.TestCase):
    def test_collision_probability_exact_falling_factorial_and_union_bound(self):
        for n in (1,2,3,4,5,10,20,50,100):
            for k in range(1,min(n,10)+1):
                exact=Fraction(1)
                for i in range(k):
                    exact*=Fraction(n-i,n)
                e=collision_bound(n,k)
                self.assertEqual(e,1-exact)
                self.assertLessEqual(e,Fraction(k*(k-1),2*n))
                self.assertEqual(window_bounds(n,k)[
                    "mask_tv_each_world"],e)
                self.assertEqual(window_bounds(n,k)[
                    "output_tv_between_worlds"],min(1,2*e))
                self.assertEqual(window_bounds(n,k)[
                    "max_abs_fourier_discrepancy"],min(2,4*e))
            self.assertEqual(collision_bound(n,1),0)

    def test_independent_orbit_reconstruction_of_ordinary_and_exceptional_masks(self):
        for name,n,q0,q1 in original_masks():
            for q in (q0,q1):
                joint=empirical_joint_law(n,q)
                sym=expand_empirical_joint_law(n,joint)
                self.assertEqual(sum(sym.values()),1,msg=name)
                self.assertEqual(sum(joint.values()),1,msg=name)
                self.assertEqual(directing_law(n,joint),{
                    hist:sum((v for (j,s),v in joint.items() if j==hist),
                             Fraction(0))
                    for hist in {key[0] for key in joint}
                },msg=name)
                for hist in directing_law(n,joint):
                    self.assertEqual(sum(empirical_pair_law(n,hist)),1)
                    self.assertEqual(histogram_multinomial(n,hist),
                                     __import__("math").factorial(n)//
                                     __import__("math").prod(
                                         __import__("math").factorial(v)
                                         for v in hist
                                     ))
                # The within-pair and across-pair symmetrized law agrees
                # on all histogram + full exceptional pair atoms.
                self.assertEqual(empirical_joint_law(n,sym),joint,msg=name)

    def test_finite_marginal_rigidity_holds_for_world_specific_equalizers(self):
        for name,n,q0,q1 in original_masks():
            j0=empirical_joint_law(n,q0)
            j1=empirical_joint_law(n,q1)
            self.assertEqual(directing_law(n,j0),directing_law(n,j1),
                             msg=name)
            for bit in (0,1):
                self.assertEqual(exceptional_singlebit_marginal(n,j0,bit),
                                 exceptional_singlebit_marginal(n,j1,bit),
                                 msg=(name,bit))
            if name.startswith(("BM25","BM26")):
                self.assertNotEqual(j0,j1)

    def test_exact_hypergeometric_and_iid_k_windows_differ_by_collision_bound(self):
        for name,n,q0,q1 in original_masks():
            for q in (q0,q1):
                joint=empirical_joint_law(n,q)
                full=expand_empirical_joint_law(n,joint)
                for k in range(1,min(n,3)+1):
                    true=without_replacement_window(n,k,joint)
                    fake=with_replacement_window(n,k,joint)
                    self.assertEqual(true,independent_project_full(n,k,full))
                    self.assertLessEqual(total_variation(true,fake),
                                         collision_bound(n,k),msg=(name,k))
                    self.assertEqual(total_variation(true,fake),0) if k==1 else None
                    self.assertEqual(sum(fake.values()),1)
                    self.assertEqual(sum(true.values()),1)

    def test_q8_complete_equalizers_yield_near_equal_infinite_output_windows(self):
        examples=(
            ("BM25",2,bm25_mask(0),bm25_mask(1)),
            ("BM26",3,bm26_mask(0),bm26_mask(1)),
            ("BM27",4,bm27_mask(4,0),bm27_mask(4,1)),
            ("BM30",3,explicit_frontier_mask(3,Fraction(1,20),0),
                        explicit_frontier_mask(3,Fraction(1,20),1)),
        )
        for name,n,q0,q1 in examples:
            for k in range(1,min(3,n)+1):
                receipt=certify_finite_window(n,k,q0,q1)
                self.assertEqual(receipt.n,n)
                self.assertEqual(receipt.k,k)
                self.assertTrue(receipt.true_output_laws_equal)
                self.assertTrue(receipt.shared_directing_mu)
                self.assertTrue(receipt.shared_exceptional_singlebits)
                self.assertLessEqual(receipt.approximate_output_tv,
                                     2*collision_bound(n,k),msg=(name,k))
                self.assertLessEqual(receipt.maximum_walsh_gap,
                                     4*collision_bound(n,k))
                if k==1:
                    self.assertEqual(receipt.actual_mask_tv_world0,0)
                    self.assertEqual(receipt.actual_mask_tv_world1,0)
                    self.assertEqual(receipt.approximate_output_tv,0)

    def test_sharp_hostile_fixed_histogram_sampling_collision(self):
        # n=2: one ordinary pair 00, one ordinary pair 11.
        # Uniformly randomize their order; the exceptional pair is 00.
        # Original law is supported on masks 00|11 and 11|00.
        # IID empirical extension additionally allows 00|00 and 11|11.
        n=2
        ordinary={3:Fraction(1,2),12:Fraction(1,2)}
        joint=empirical_joint_law(n,ordinary)
        self.assertEqual(joint,{((1,0,1),0):Fraction(1)})
        true=without_replacement_window(n,2,joint)
        fake=with_replacement_window(n,2,joint)
        self.assertEqual(true,ordinary)
        self.assertEqual(fake,{
            0:Fraction(1,4),3:Fraction(1,4),
            12:Fraction(1,4),15:Fraction(1,4),
        })
        self.assertEqual(total_variation(true,fake),Fraction(1,2))
        self.assertEqual(collision_bound(2,2),Fraction(1,2))
        self.assertEqual(without_replacement_window(n,1,joint),
                         with_replacement_window(n,1,joint))

    def test_empirical_iid_extension_retains_every_one_pair_and_special_marginal(self):
        for name,n,q0,q1 in original_masks():
            for q in (q0,q1):
                joint=empirical_joint_law(n,q)
                original=without_replacement_window(n,1,joint)
                infinite=with_replacement_window(n,1,joint)
                self.assertEqual(original,infinite,msg=name)
                # Bit-flip marginals on a single ordinary pair, on the
                # exceptional pair, and ordinary+one exceptional bit
                # are consequently identical without any approximation.
                self.assertEqual(sum(original.values()),1)

    def test_symbolic_growing_k_window_bound_vanishes_as_n_grows(self):
        for n in (1,8,64,1000,10**6,10**9):
            receipt=growing_window_bound(n)
            k=receipt["k"]
            self.assertTrue(k**3<=n)
            self.assertTrue((k+1)**3>n)
            self.assertEqual(receipt["exact_collision_bound"],
                             collision_bound(n,k))
            self.assertLessEqual(receipt["exact_collision_bound"],
                                 receipt["elementary_upper"])
            self.assertFalse(receipt["explicit_threshold_convergence_rate_claimed"])
        self.assertLess(
            growing_window_bound(10**9)["elementary_upper"],
            Fraction(1,2000)
        )
        self.assertGreater(growing_window_bound(10**9)["k"],900)

    def test_consistent_finite_iid_extensions_project_to_the_same_k_law(self):
        # An infinite extension generated from one empirical directing
        # mixture must be projective, irrespective of world and finite n.
        n=3
        for h in (0,1):
            joint=empirical_joint_law(n,bm26_mask(h))
            longer=with_replacement_window(n,3,joint)
            keep=with_replacement_window(n,2,joint)
            projected={}
            for mask,p in longer.items():
                target=(mask&15)|(((mask>>6)&3)<<4)
                projected[target]=projected.get(target,Fraction(0))+p
            self.assertEqual(projected,keep)

    def test_malformed_or_nonexchangeable_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            collision_bound(2,3)
        with self.assertRaises(ValueError):
            collision_bound(0,1)
        with self.assertRaises(ValueError):
            mask_histogram(2,-1)
        with self.assertRaises(ValueError):
            histogram_multinomial(2,(2,1,0))
        with self.assertRaises(ValueError):
            empirical_pair_law(2,(1,1,1))
        with self.assertRaises(ValueError):
            empirical_joint_law(1,{0:Fraction(2)})
        with self.assertRaises(ValueError):
            expand_empirical_joint_law(6,{((6,0,0),0):Fraction(1)})
        with self.assertRaises(ValueError):
            exceptional_singlebit_marginal(2,{},2)
        with self.assertRaises(ValueError):
            certify_finite_window(6,2,{0:Fraction(1)},{0:Fraction(1)})
        with self.assertRaises(ValueError):
            total_variation({0:Fraction(1)},{0:Fraction(2)})
        with self.assertRaises(ValueError):
            growing_window_bound(1,power=1)


if __name__=="__main__":
    unittest.main()
