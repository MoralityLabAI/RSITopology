"""BM-23: independent fixed-core Fourier/orbit LP and K4 exact-mask checks."""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from core_subdivision_orbit_BM23 import (
    CoreSubdivision,build_core_orbit_lp,check_core_orbit_lp_matrix,
    core_subdivision_manifest,
)
from k4_subdivision_erasure_BM23 import (
    K4_EDGES,K4_FLAT,K4_OTHER,L2_ORBIT_NUMERATORS,
    k4_single_subdivision,exact_cap,l2_orbit_mask,l2_mask_law,
    mask_for_small,product_mask_law,
    exact_mask_rate,prove_diamond_projection_lower,
    verify_L2_exact,verify_L_ge3_symbolic,sample_common_mask,
    theorem_receipt,
)
from generic_fourier_erasure_BM17 import (
    census,signed_walsh
)
from fourier_completion_BM18 import convolve_clean
from theta_orbit_lp_BM14 import (
    mask_mass_orbits,expand_orbit_masses,walsh_kernel
)
from theta_fourier_transfer_BM12 import theta_walsh_transfer
from k4_high_degree_BM17 import DEGREE_PRIMALS,DEGREE_DUALS
from diamond_weighted_fourier_BM10 import (
    EDGES as DIAMOND_EDGES, PRIMAL_MASK_COUNTS as BM10_MASK
)
from separator_factor_transfer_BM16 import exact_walsh
from finite_seed import Game


def rational_orbit_law(model,flat):
    return mask_mass_orbits(model.lengths,flat.weights if hasattr(flat,"weights")
                            else flat,flat.denominator)


def full_output_equal(model,law):
    a,b=census(model.subdivided_game(0)),census(model.subdivided_game(1))
    return convolve_clean(model.m,a,law)==convolve_clean(model.m,b,law)


class CoreSubdivisionOrbitTests(unittest.TestCase):
    def test_K4_all_six_original_edges_match_BM17_full_Fourier_table(self):
        model=k4_single_subdivision(1)
        p0,p1=census(model.subdivided_game(0)),census(model.subdivided_game(1))
        self.assertEqual(model.m,6)
        self.assertEqual(model.orbit_size,64)
        for S in range(64):
            self.assertEqual(model.clean_walsh(S,0),signed_walsh(p0,S))
            self.assertEqual(model.clean_walsh(S,1),signed_walsh(p1,S))
            self.assertEqual(model.clean_delta(S),
                             signed_walsh(p0,S)-signed_walsh(p1,S))
            self.assertEqual(model.clean_walsh(S,1),exact_walsh(
                model.subdivided_game(1),S
            ))
        self.assertEqual(model.clean_support_count(),
                         sum(signed_walsh(p0,S)!=signed_walsh(p1,S)
                             for S in range(64)))

    def test_subdivided_K4_every_Fourier_subset_matches_independent_census(self):
        for lengths,q in (
            ((2,1,1,1,1,1),4),
            ((2,2,1,1,1,1),4),
            ((1,2,1,1,2,1),4),
            ((1,1,1,1,1,1),8),
        ):
            model=CoreSubdivision(q,4,K4_EDGES,lengths,K4_FLAT,K4_OTHER)
            p0,p1=census(model.subdivided_game(0)),census(model.subdivided_game(1))
            for S in range(1<<model.m):
                self.assertEqual(model.clean_walsh(S,0),signed_walsh(p0,S))
                self.assertEqual(model.clean_walsh(S,1),signed_walsh(p1,S))
            self.assertEqual(model.clean_support_count(),sum(
                signed_walsh(p0,S)!=signed_walsh(p1,S)
                for S in range(1<<model.m)))

    def test_nonseries_parallel_five_edge_Wheatstone_core_and_subdivision(self):
        core=((0,2),(2,1),(0,3),(3,1),(2,3))
        shifts=(0,1,2,0,3)
        for lengths in ((1,1,1,1,1),(2,1,1,2,1),(1,2,2,1,1)):
            model=CoreSubdivision(4,4,core,lengths,(0,)*5,shifts)
            p0,p1=census(model.subdivided_game(0)),census(model.subdivided_game(1))
            for S in range(1<<model.m):
                self.assertEqual(model.clean_walsh(S,0),signed_walsh(p0,S))
                self.assertEqual(model.clean_walsh(S,1),signed_walsh(p1,S))
            self.assertEqual(model.clean_support_count(),sum(
                signed_walsh(p0,S)!=signed_walsh(p1,S)
                for S in range(1<<model.m)))

    def test_parallel_edge_core_recovers_BM12_theta_path_transfer(self):
        base=((0,1),(0,1),(0,1))
        for q,lengths,gains in (
            (4,(1,2,2),(0,1,2)),
            (4,(2,2,2),(0,1,2)),
            (8,(2,2,2),(0,1,2)),
            (2,(2,3,3),(0,1,0)),
        ):
            model=CoreSubdivision(q,2,base,lengths,(0,)*3,gains)
            for S in range(1<<model.m):
                self.assertEqual(model.clean_walsh(S,1),
                                 theta_walsh_transfer(q,lengths,gains,S))

    def test_original_K4_exact_primal_dual_from_BM17_in_new_orbit_basis(self):
        model=k4_single_subdivision(1)
        primal=DEGREE_PRIMALS[6]
        q=mask_mass_orbits(model.lengths,primal.q0,primal.denominator)
        self.assertEqual(model.verify_orbit_primal(
            q,q,cap=Fraction(3,14)),Fraction(3,14))
        dual=DEGREE_DUALS[6]
        signatures={model.signature(S):Fraction(c,dual.walsh_denominator)
                    for S,c in dual.walsh_numerators.items()}
        norms=tuple(Fraction(v,dual.walsh_denominator)
                    for v in dual.normalization_numerators)
        marg=tuple(tuple(Fraction(dual.marginal_numerators[h*6+i],
                                   dual.marginal_denominator)
                         for i in range(6)) for h in (0,1))
        self.assertEqual(model.verify_orbit_dual(
            norms,signatures,marg),Fraction(3,14))
        lp=build_core_orbit_lp(model)
        self.assertEqual((lp.variables,len(lp.equality_rows),
                          len(lp.marginal_rows)),(129,65,12))
        self.assertTrue(check_core_orbit_lp_matrix(
            lp,q,q,Fraction(3,14)))
        self.assertFalse(check_core_orbit_lp_matrix(
            lp,q,q,Fraction(1,5)))

    def test_exact_orbit_LP_nontrivial_K4_subdivision_upper_witness(self):
        model=k4_single_subdivision(2)
        mask=l2_orbit_mask()
        lp=build_core_orbit_lp(model)
        self.assertEqual(model.orbit_size,96)
        self.assertEqual((lp.variables,len(lp.equality_rows),
                          len(lp.marginal_rows)),(193,97,12))
        self.assertTrue(check_core_orbit_lp_matrix(
            lp,mask,mask,Fraction(1,5)))
        self.assertFalse(check_core_orbit_lp_matrix(
            lp,mask,mask,Fraction(19,100)))
        self.assertEqual(model.verify_orbit_primal(mask,mask),
                         Fraction(1,5))
        self.assertEqual(sum(mask.values()),1)

    def test_large_nonseries_parallel_core_no_label_or_Fourier_table(self):
        model=CoreSubdivision(
            4096,4,K4_EDGES,(120,1,1,1,1,1),K4_FLAT,K4_OTHER
        )
        manifest=core_subdivision_manifest(model)
        self.assertEqual(manifest["subdivided_edges"],125)
        self.assertEqual(manifest["subdivided_vertices"],123)
        self.assertEqual(manifest["path_orbit_classes_per_world"],121*32)
        self.assertEqual(manifest["raw_readout_masks_per_world"],1<<125)
        self.assertGreater(manifest["clean_residual_support_count"],1<<120)
        self.assertFalse(manifest["full_output_or_Fourier_table_materialized"])
        full=(1<<model.m)-1
        for S in (0,1,full,full^1,full^(1<<120),full^(1<<124)):
            self.assertTrue(-1<=model.clean_walsh(S,0)<=1)
            self.assertTrue(-1<=model.clean_walsh(S,1)<=1)
        with self.assertRaises(ValueError):
            build_core_orbit_lp(model,max_classes=128)

    def test_reject_malformed_core_and_mask_constraints(self):
        with self.assertRaises(ValueError):
            CoreSubdivision(3,4,K4_EDGES,(1,)*6,K4_FLAT,K4_OTHER)
        with self.assertRaises(ValueError):
            CoreSubdivision(4,4,K4_EDGES,(0,)*6,K4_FLAT,K4_OTHER)
        with self.assertRaises(ValueError):
            CoreSubdivision(4,4,((0,0),), (1,), (0,), (0,))
        model=k4_single_subdivision(2)
        with self.assertRaises(ValueError):
            model.full_path_average(0,64)
        with self.assertRaises(ValueError):
            model.clean_walsh(1<<7,0)
        with self.assertRaises(ValueError):
            model.orbit_clean_walsh((2,2,1,1,1,1),0)
        with self.assertRaises(ValueError):
            model.verify_orbit_dual((0,0),{},((0,)*6,(0,)*6))
        with self.assertRaises(ValueError):
            build_core_orbit_lp(model,max_classes=50)


class K4SubdivisionSharpErasureTests(unittest.TestCase):
    def test_length_one_recovers_BM17_sharp_three_fourteenths(self):
        model=k4_single_subdivision(1)
        self.assertEqual(exact_cap(1),Fraction(3,14))
        self.assertEqual(theorem_receipt(1)["sharp_hypothesis_aware_cap"],"3/14")
        self.assertEqual(model.m,6)

    def test_sharp_length_two_common_rational_witness_full_output(self):
        model=k4_single_subdivision(2)
        self.assertEqual(len(L2_ORBIT_NUMERATORS),21)
        self.assertEqual(sum(L2_ORBIT_NUMERATORS.values()),40)
        self.assertEqual(verify_L2_exact(),Fraction(1,5))
        law=l2_mask_law()
        self.assertEqual(sum(law.values()),1)
        self.assertEqual(exact_mask_rate(model.m,law),Fraction(1,5))
        self.assertTrue(full_output_equal(model,law))
        self.assertEqual(model.verify_orbit_primal(
            l2_orbit_mask(),l2_orbit_mask()),Fraction(1,5))
        self.assertEqual(prove_diamond_projection_lower(2),Fraction(1,5))

    def test_all_length_three_four_five_common_product_masks_are_exact(self):
        for L in (3,4,5):
            model=k4_single_subdivision(L)
            self.assertEqual(verify_L_ge3_symbolic(L),Fraction(1,5))
            law=product_mask_law(L)
            self.assertTrue(full_output_equal(model,law))
            self.assertEqual(exact_mask_rate(model.m,law),Fraction(1,5))
            self.assertEqual(sum(law.values()),1)
            self.assertEqual(exact_cap(L),Fraction(1,5))
            self.assertLessEqual(Fraction(1,2*L),Fraction(1,5))

    def test_length_120_K4_path_subdivision_has_closed_exact_cap(self):
        L=120
        model=k4_single_subdivision(L)
        result=theorem_receipt(L)
        self.assertEqual(result["sharp_hypothesis_aware_cap"],"1/5")
        self.assertEqual(result["total_reported_edges"],125)
        self.assertEqual(result["total_vertices"],123)
        self.assertGreater(result["clean_residual_support_count"],
                           (1<<120)-1)
        self.assertFalse(result["full_mask_table_created"])
        self.assertEqual(verify_L_ge3_symbolic(L),Fraction(1,5))
        rng=Random(20261110)
        for _ in range(100):
            mask=sample_common_mask(L,rng)
            self.assertLessEqual(mask.bit_count(),4)
            self.assertLessEqual((mask&((1<<L)-1)).bit_count(),1)
        with self.assertRaises(ValueError):
            product_mask_law(L,max_states=100)

    def test_diamond_lower_bound_is_unaffected_by_extra_series_length(self):
        for L in (2,3,5,120):
            self.assertEqual(prove_diamond_projection_lower(L),Fraction(1,5))
            c=k4_single_subdivision(L)
            self.assertEqual(
                len({c.gains1[5],
                     c.gains1[1]^c.gains1[2],
                     c.gains1[3]^c.gains1[4]}),3
            )
            self.assertEqual(exact_cap(L),Fraction(1,5))

    def test_input_validation_and_specific_L2_orbit_symmetry(self):
        for L in (-1,0):
            with self.assertRaises(ValueError):
                k4_single_subdivision(L)
            with self.assertRaises(ValueError):
                exact_cap(L)
        with self.assertRaises(ValueError):
            k4_single_subdivision(3,q=8)
        with self.assertRaises(ValueError):
            verify_L_ge3_symbolic(2)
        with self.assertRaises(ValueError):
            product_mask_law(2)
        with self.assertRaises(ValueError):
            sample_common_mask(2,Random(1))
        with self.assertRaises(ValueError):
            mask_for_small(1)
        self.assertEqual(sum(l2_mask_law().values()),1)
        self.assertLess(len(l2_mask_law()),1<<7)


if __name__=="__main__":
    unittest.main()
