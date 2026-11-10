"""BM-24: independent wreath histogram orbit, full readout and sharp-family tests.

Small instances compare orbit kernels against explicit full Boolean mask
orbits, Fourier coefficients against independent vertex-label census,
and entire completed output laws against direct XOR convolution. The
large n=250 instance uses only symbolic quantities and exact samplers.
"""
from fractions import Fraction
from itertools import product
from math import comb
from random import Random
import unittest

from repeated_theta_orbits_BM24 import (
    PathType,RepeatedTheta,type_histograms,type_histogram_size,
    type_krawtchouk_kernel,type_histogram_multiplicity,
    build_repeated_lp,check_repeated_lp_matrix,repeated_manifest,
)
from repeated_gain_erasure_BM24 import (
    gain_family,exact_common_cap,exact_state_aware_cap,
    common_mask_orbits,common_mask_character,
    verify_common_symbolic,clean_support_count_length_two,
    prove_matching_lower,common_full_mask_law,
    q4_sparse_full_dual,verify_q4_sparse_dual_symbolic,
    certify_q4_family_finite,
    common_full_mask_integer,sample_common_mask,repeated_family_manifest,
)
from generic_fourier_erasure_BM17 import census,signed_walsh
from fourier_completion_BM18 import convolve_clean,mask_marginals
from theta_shared_cycle_erasure import (
    q4_common_mask,Q8_FLAT,Q8_FRUSTRATED,
    verify_q4_primal,verify_q8_primal,verify_q8_dual,
)
from sparse_fourier_degree_BM13 import (
    dual_certificate as bm13_dual,verify_sparse_dual,
)
from sharp_erasure_optimality import critical_erasure_cap


def _joint_mask_boolean_signature(model,mask):
    return model.signature(mask)


def direct_character(full_mask,selected):
    return -1 if (full_mask&selected).bit_count()%2 else 1


class RepeatedThetaOrbitTests(unittest.TestCase):
    def test_exact_Krawtchouk_histogram_kernel_against_full_orbit_masks(self):
        model=RepeatedTheta(4,(PathType(2,0,1,2),))
        classes=model.all_signatures()
        self.assertEqual(len(classes),6)
        self.assertEqual(type_histogram_size(2,2),6)
        for sig in classes:
            S=model.canonical_subset(sig)
            for mask_sig in classes:
                atoms=[m for m in range(16)
                       if model.signature(m)==mask_sig]
                want=Fraction(sum(direct_character(m,S) for m in atoms),
                              len(atoms))
                got=model.orbit_kernel(sig,mask_sig)
                self.assertEqual(got,want)
                self.assertEqual(
                    got,type_krawtchouk_kernel(2,sig[0],mask_sig[0])
                )

    def test_repeated_type_orbit_sizes_sum_to_uncompressed_Boolean_masks(self):
        for n,L in ((2,2),(3,2),(2,3),(3,1)):
            model=gain_family(n,L)
            classes=model.all_signatures(max_orbits=200)
            self.assertEqual(len(classes),model.orbit_size)
            self.assertEqual(
                sum(model.orbit_size_of_signature(sig) for sig in classes),
                1<<model.m
            )
            for sig in classes:
                self.assertEqual(model.signature(model.canonical_subset(sig)),
                                 sig)

    def test_all_fourier_coefficients_match_fresh_vertex_labels(self):
        for q,n,L in ((2,2,1),(4,2,2),(4,3,2),(8,2,2),(4,2,3)):
            model=gain_family(n,L,q=q)
            a,b=census(model.game(0)),census(model.game(1))
            self.assertEqual(sum(a),q**model.vertices)
            self.assertEqual(sum(b),q**model.vertices)
            for S in range(1<<model.m):
                self.assertEqual(model.clean_walsh(0,S),signed_walsh(a,S))
                self.assertEqual(model.clean_walsh(1,S),signed_walsh(b,S))
            self.assertEqual(model.clean_support_count(max_orbits=200),
                             sum(signed_walsh(a,S)!=signed_walsh(b,S)
                                 for S in range(1<<model.m)))
            if q>=4 and L==2:
                self.assertEqual(model.clean_support_count(),
                                 4**n-3**n)

    def test_full_q4_and_q8_BM09_masks_project_to_repeated_type_orbits(self):
        for q in (4,8):
            model=RepeatedTheta.from_paths(q,(
                (2,0,0),(2,0,1),(2,0,2)
            ))
            self.assertEqual(len(model.types),3)
            self.assertEqual((model.m,model.orbit_size),(6,27))
            if q==4:
                self.assertTrue(verify_q4_primal())
                old=q4_common_mask()
                flat=model.full_mask_to_orbits({
                    i:w for i,w in enumerate(old) if w},12)
                other=flat
                eta=Fraction(1,6)
            else:
                self.assertTrue(verify_q8_primal() and verify_q8_dual())
                flat=model.full_mask_to_orbits({
                    i:w for i,w in enumerate(Q8_FLAT) if w},10080)
                other=model.full_mask_to_orbits({
                    i:w for i,w in enumerate(Q8_FRUSTRATED) if w},10080)
                eta=Fraction(29,630)
            self.assertEqual(model.verify_primal(flat,other,cap=eta),eta)
        # The BM-13 five-term full theta dual can be averaged to the
        # three individual-path histogram types without changing value.
        model=RepeatedTheta.from_paths(4,(
            (2,0,0),(2,0,1),(2,0,2)
        ))
        norm,old_coeff,old_z=bm13_dual("theta")
        new_coeff={}
        for subset,value in old_coeff.items():
            sig=model.signature(subset)
            new_coeff[sig]=new_coeff.get(sig,Fraction(0))+value
        new_z=tuple(
            tuple(sum((old_z[h].get(2*i+j,Fraction(0))
                       for j in range(2)),Fraction(0))
                  for i in range(3))
            for h in range(2)
        )
        self.assertEqual(verify_sparse_dual("theta"),Fraction(1,6))
        self.assertEqual(model.verify_dual(norm,new_coeff,new_z),
                         Fraction(1,6))

    def test_new_full_orbit_LP_matrix_and_independent_primal_feasibility(self):
        model=gain_family(2,2)
        self.assertEqual(model.orbit_size,18)
        lp=build_repeated_lp(model)
        self.assertEqual(lp.variables,37)
        self.assertEqual(len(lp.equalities),19)
        self.assertEqual(len(lp.inequalities),4)
        q=common_mask_orbits(2,2)
        self.assertTrue(check_repeated_lp_matrix(lp,q,q,Fraction(1,8)))
        self.assertFalse(check_repeated_lp_matrix(
            lp,q,q,Fraction(1,8)-Fraction(1,100)
        ))
        self.assertEqual(model.verify_primal(q,q,cap=Fraction(1,8)),
                         Fraction(1,8))
        self.assertEqual(sum(q.values()),1)

    def test_new_common_mask_character_matches_full_independent_mask_oracle(self):
        for n,L in ((2,2),(3,2),(2,3)):
            model=gain_family(n,L)
            law=common_full_mask_law(n,L)
            for sig in model.all_signatures(max_orbits=200):
                S=model.canonical_subset(sig)
                expected=sum((p*direct_character(mask,S)
                              for mask,p in law.items()),Fraction(0))
                actual=common_mask_character(n,L,sig)
                self.assertEqual(actual,expected)

    def test_full_mask_family_to_orbits_equals_closed_histogram_mixture(self):
        for n,L in ((1,1),(2,2),(3,2),(2,3)):
            model=gain_family(n,L)
            weights,den=common_full_mask_integer(n,L)
            orbits=model.full_mask_to_orbits(weights,den)
            self.assertEqual(orbits,common_mask_orbits(n,L))
            self.assertEqual(model.max_bit_marginal(orbits),
                             Fraction(1,4*L))
            self.assertEqual(len(orbits),n+2)

    def test_entire_masked_Boolean_laws_equal_in_small_q2_q4_q8_models(self):
        for q,n,L in (
            (2,2,1),(4,1,1),(4,2,1),
            (4,1,2),(4,2,2),(4,3,2),(4,4,2),
            (8,1,2),(8,2,2),
        ):
            model=gain_family(n,L,q=q)
            if model.m>12:
                continue
            law=common_full_mask_law(n,L)
            a,b=census(model.game(0)),census(model.game(1))
            self.assertNotEqual(a,b)
            self.assertEqual(convolve_clean(model.m,a,law),
                             convolve_clean(model.m,b,law))
            self.assertEqual(mask_marginals(model.m,law),
                             (Fraction(1,4*L),)*model.m)
            self.assertEqual(verify_common_symbolic(n,L,q=q),
                             Fraction(1,4*L))
            self.assertEqual(model.verify_primal(
                common_mask_orbits(n,L,q=q),
                common_mask_orbits(n,L,q=q),max_orbits=100
            ),Fraction(1,4*L))

    def test_sharp_state_aware_family_and_common_mask_for_all_q(self):
        for n,L in ((1,1),(2,2),(3,3),(8,4),(70,2)):
            for q in (2,4,8):
                result=prove_matching_lower(n,L,q=q)
                self.assertEqual(result["common_lower"],
                                 Fraction(1,4*L))
                self.assertEqual(result["common_upper_verified"],
                                 Fraction(1,4*L))
                if q<=4:
                    self.assertEqual(exact_state_aware_cap(q,L),
                                     Fraction(1,4*L))
                    self.assertTrue(result["state_aware_sharp"])
                else:
                    self.assertFalse(result["state_aware_sharp"])
                    self.assertLessEqual(result["state_aware_lower"],
                                         result["common_lower"])

    def test_clean_support_count_formula_exact_for_all_small_n_and_large(self):
        for n in (1,2,3,4,8):
            model=gain_family(n,2)
            if n<=3:
                self.assertEqual(model.clean_support_count(),
                                 4**n-3**n)
            self.assertEqual(clean_support_count_length_two(n),
                             4**n-3**n)
        huge=clean_support_count_length_two(250)
        self.assertEqual(huge,4**250-3**250)
        self.assertGreater(huge,1<<499)

    def test_250_repeated_paths_nontrivial_variable_core_compression(self):
        n,L=250,2
        model=gain_family(n,L)
        manifest=repeated_family_manifest(n,L)
        self.assertEqual(model.path_count,251)
        self.assertEqual(model.vertices,253)
        self.assertEqual(model.m,502)
        self.assertEqual(model.orbit_size,3*comb(252,2))
        self.assertEqual(manifest["BM24_type_histogram_orbits"],94878)
        self.assertEqual(manifest["BM14_path_orbits"],3**251)
        self.assertEqual(manifest["full_mask_states_per_world"],1<<502)
        self.assertEqual(manifest["clean_support_cardinality_L2"],
                         4**250-3**250)
        self.assertEqual(manifest["nonzero_common_mask_orbits"],252)
        self.assertEqual(manifest["sharp_state_aware_cap_q2_q4"],"1/8")
        self.assertFalse(manifest["full_LP_solved"])
        self.assertFalse(manifest["full_Fourier_table_materialized"])
        self.assertEqual(verify_common_symbolic(n,L),Fraction(1,8))
        with self.assertRaises(ValueError):
            model.all_signatures(max_orbits=2000)
        with self.assertRaises(ValueError):
            build_repeated_lp(model,max_orbits=64)
        rng=Random(20261110)
        for _ in range(60):
            mask=sample_common_mask(n,L,rng)
            self.assertLess(mask,1<<model.m)
            self.assertEqual((mask>>model.m),0)
            # Each path receives <=1 flip in the independent branches.
            for i in range(model.path_count):
                self.assertLessEqual(
                    ((mask>>(i*L))&((1<<L)-1)).bit_count(),1
                )

    def test_one_character_exact_full_erasure_dual_finite_and_symbolic(self):
        for n,L in ((1,1),(2,1),(3,1),(1,2),(2,2),
                    (3,2),(4,2),(1,3)):
            eta=Fraction(1,4*L)
            dual=q4_sparse_full_dual(n,L)
            self.assertEqual(len(dual.walsh_numerators),1)
            self.assertEqual(sum(dual.normalization_numerators),
                             dual.walsh_denominator*eta)
            self.assertEqual(-sum(dual.marginal_numerators),
                             dual.marginal_denominator)
            self.assertEqual(verify_q4_sparse_dual_symbolic(n,L),eta)
            result=certify_q4_family_finite(n,L)
            self.assertEqual(result.optimum,eta)
            self.assertTrue(result.full_output_equal)
            self.assertEqual(result.walsh_terms,1)
        self.assertEqual(verify_q4_sparse_dual_symbolic(250,2),
                         Fraction(1,8))
        self.assertEqual(verify_q4_sparse_dual_symbolic(2,120),
                         Fraction(1,480))
        with self.assertRaises(ValueError):
            certify_q4_family_finite(250,2)
        with self.assertRaises(ValueError):
            q4_sparse_full_dual(0,2)

    def test_duplicate_type_grouping_and_model_validation(self):
        model=RepeatedTheta.from_paths(4,(
            (2,0,1),(2,0,0),(2,0,1),(3,0,2)
        ))
        self.assertEqual(model.path_count,4)
        self.assertEqual(len(model.types),3)
        self.assertEqual(model.orbit_size,
                         comb(2+2,2)*3*4)
        with self.assertRaises(ValueError):
            RepeatedTheta(4,(PathType(2,0,0,2),PathType(2,0,0,1)))
        with self.assertRaises(ValueError):
            RepeatedTheta(3,(PathType(2,0,1,1),))
        with self.assertRaises(ValueError):
            gain_family(0,2)
        with self.assertRaises(ValueError):
            gain_family(2,0)
        with self.assertRaises(ValueError):
            gain_family(1,2,q=3)
        with self.assertRaises(ValueError):
            gain_family(1,2,gain=0)
        with self.assertRaises(ValueError):
            exact_state_aware_cap(8,2)
        with self.assertRaises(ValueError):
            model.clean_walsh(0,1<<model.m)
        with self.assertRaises(ValueError):
            model.verify_dual((0,0),{},((0,)*3,(0,)*3))
        with self.assertRaises(ValueError):
            type_krawtchouk_kernel(2,(2,0,0),(0,1,0))
        with self.assertRaises(ValueError):
            clean_support_count_length_two(1,q=2)


if __name__=="__main__":
    unittest.main()
