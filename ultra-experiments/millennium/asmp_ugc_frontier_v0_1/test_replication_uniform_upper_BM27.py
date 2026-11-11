"""BM-27: independent full-output tests of the all-n q8 5/52 construction."""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from replication_uniform_upper_BM27 import (
    PAIR_I,PAIR_A,PAIR_B,PAIR_E,PAIRS,UPPER_CAP,
    COMPONENTS,CLEAN_COMPONENTS,xor_pair,pair_bit_marginals,
    ordinary_category,formal_output_components,
    verify_convolution_identity,exact_mask_rate,theorem_upper,
    explicit_mask_law,exact_clean_law,xor_convolve,
    verify_complete_small,exact_orbit_masks,
    sample_mask,theorem_receipt,
)
from repeated_gain_erasure_BM24 import (
    gain_family,exact_common_cap,verify_common_symbolic,
)
from state_aware_three_replica_BM26 import EXACT_CAP as N3_SHARP
from state_aware_replication_BM25 import EXACT_ETA as N2_SHARP
from sharp_erasure_optimality import critical_erasure_cap
from generic_fourier_erasure_BM17 import census


class ReplicationUniformUpperTests(unittest.TestCase):
    def test_signed_pair_identity_and_total_algebraic_convolution(self):
        self.assertEqual(PAIR_E,tuple(2*b-i for b,i in zip(PAIR_B,PAIR_I)))
        self.assertEqual(xor_pair(PAIR_A,PAIR_E),
                         xor_pair(PAIR_B,PAIR_E))
        self.assertNotEqual(PAIR_A,PAIR_B)
        self.assertTrue(verify_convolution_identity())
        x,y=formal_output_components(0),formal_output_components(1)
        self.assertEqual(x,y)
        self.assertEqual(set(x),{"A","B","AA","AB","BB"})
        self.assertEqual(sum((sum(v,Fraction(0)) for v in x.values()),
                             Fraction(0)),1)
        self.assertEqual(
            xor_pair(PAIR_A,PAIR_E),
            (Fraction(7,16),Fraction(1,4),
             Fraction(1,4),Fraction(1,16))
        )

    def test_every_world_and_bit_type_has_identical_exact_5_over_52_cost(self):
        self.assertEqual(UPPER_CAP,Fraction(5,52))
        self.assertEqual(pair_bit_marginals(PAIR_A),
                         (Fraction(1,8),)*2)
        self.assertEqual(pair_bit_marginals(PAIR_B),
                         (Fraction(1,8),)*2)
        self.assertEqual(pair_bit_marginals(PAIR_E),
                         (Fraction(1,4),)*2)
        for h in (0,1):
            self.assertEqual(exact_mask_rate(h),(UPPER_CAP,UPPER_CAP))
            self.assertEqual(sum(x[2] for x in COMPONENTS[h]),13)
            self.assertEqual(sum(x[2] for x in CLEAN_COMPONENTS[h]),8)
        self.assertEqual(Fraction(1,8)-UPPER_CAP,Fraction(3,104))
        self.assertEqual(1-UPPER_CAP/Fraction(1,8),Fraction(3,13))

    def test_independent_uniform_vertex_census_matches_clean_mixture(self):
        for n in (1,2,3):
            net=gain_family(n,2,q=8)
            for h in (0,1):
                clean=exact_clean_law(n,h)
                census_counts=census(net.game(h))
                self.assertEqual(sum(census_counts),net.q**net.vertices)
                for S in range(1<<net.m):
                    self.assertEqual(
                        clean.get(S,Fraction(0)),
                        Fraction(census_counts[S],net.q**net.vertices)
                    )

    def test_all_output_probabilities_equal_and_per_edge_budget_exact(self):
        for n in (1,2,3,4):
            if n<=3:
                self.assertTrue(verify_complete_small(n))
            else:
                self.assertTrue(verify_complete_small(n,max_bits=12))
            q0,q1=explicit_mask_law(n,0),explicit_mask_law(n,1)
            self.assertNotEqual(q0,q1)
            self.assertEqual(sum(q0.values()),1)
            self.assertEqual(sum(q1.values()),1)
            clean0,clean1=exact_clean_law(n,0),exact_clean_law(n,1)
            self.assertNotEqual(clean0,clean1)
            result0=xor_convolve(clean0,q0)
            result1=xor_convolve(clean1,q1)
            self.assertEqual(result0,result1)
            self.assertEqual(sum(result0.values()),1)
            for law in (q0,q1):
                for i in range(2*n+2):
                    self.assertEqual(
                        sum((v for x,v in law.items() if x&(1<<i)),
                            Fraction(0)),UPPER_CAP
                    )

    def test_orbit_lp_verifies_complete_output_equalization(self):
        for n in (1,2,3,4):
            net=gain_family(n,2,q=8)
            p0,p1=exact_orbit_masks(n)
            self.assertEqual(sum(p0.values()),1)
            self.assertEqual(sum(p1.values()),1)
            self.assertEqual(
                net.verify_primal(p0,p1,cap=UPPER_CAP,max_orbits=128),
                UPPER_CAP
            )
            self.assertEqual(net.max_bit_marginal(p0,p1),UPPER_CAP)

    def test_small_exact_sharp_optima_respect_uniform_upper(self):
        for val in (critical_erasure_cap(8,4),N2_SHARP,N3_SHARP):
            self.assertLess(val,UPPER_CAP)
        self.assertGreater(UPPER_CAP,N3_SHARP)
        self.assertLess(UPPER_CAP,exact_common_cap(2))
        self.assertEqual(
            (critical_erasure_cap(8,4),N2_SHARP),
            (Fraction(1,44),Fraction(5,118))
        )

    def test_upper_algebraically_uniform_for_any_replica_count(self):
        for n in (1,2,3,8,16,250,1000):
            self.assertEqual(theorem_upper(n),UPPER_CAP)
            self.assertEqual(theorem_upper(n,gain=7),UPPER_CAP)
        r=theorem_receipt(250)
        self.assertEqual(r["reported_bits"],502)
        self.assertEqual(r["exact_upper_cap"],"5/52")
        self.assertEqual(r["n_ge3_exact_lower"],str(N3_SHARP))
        self.assertEqual(r["flat_branches"],5)
        self.assertEqual(r["frustrated_branches"],4)
        self.assertEqual(r["formal_tensor_power_components"],5)
        self.assertFalse(r["asymptotic_limit_claimed"])
        self.assertTrue(r["no_full_mask_table_materialized"])
        self.assertEqual(r["improvement_relative"],"3/13")

    def test_sampler_respects_pair_support_and_large_ordinary_count(self):
        rng=Random(20261110)
        n=250
        for h in (0,1):
            for _ in range(200):
                mask=sample_mask(n,h,rng)
                self.assertTrue(0<=mask<1<<(2*n+2))
                for j in range(n):
                    self.assertTrue(0<=((mask>>(2*j))&3)<=3)
                self.assertTrue(0<=((mask>>(2*n))&3)<=3)
        with self.assertRaises(ValueError):
            sample_mask(0,0,rng)
        with self.assertRaises(ValueError):
            sample_mask(1,2,rng)

    def test_invalid_inputs_and_full_mask_size_guard(self):
        with self.assertRaises(ValueError):
            theorem_upper(0)
        with self.assertRaises(ValueError):
            theorem_upper(2,gain=0)
        with self.assertRaises(ValueError):
            theorem_upper(2,gain=8)
        with self.assertRaises(ValueError):
            explicit_mask_law(6,0)
        with self.assertRaises(ValueError):
            exact_clean_law(6,1)
        with self.assertRaises(ValueError):
            exact_orbit_masks(6)
        with self.assertRaises(ValueError):
            xor_pair((1,0),(1,0,0,0))
        with self.assertRaises(ValueError):
            pair_bit_marginals((Fraction(2),)*4)
        with self.assertRaises(ValueError):
            ordinary_category("E","A")
        with self.assertRaises(ValueError):
            formal_output_components(-1)


if __name__=="__main__":
    unittest.main()
