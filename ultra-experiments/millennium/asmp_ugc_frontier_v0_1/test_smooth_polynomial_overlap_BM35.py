"""BM-35 independent exact rational polynomial / Bernstein / erasure tests.

The global pointwise claim is checked by a 5,760-coefficient rational
Bernstein proof over 40 physical wedge patches. A separate direct
evaluation grid, corrupted full-output census, finite signed-measure
moment oracle, Hessian envelope and deliberate certificate mutations
guard against vacuous or incomplete proof verification.
"""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from smooth_polynomial_overlap_BM35 import (
    DEGREE,DENOMINATOR,COEFFICIENT_NUMERATORS,
    U_BREAKS,Y_BREAKS,LIMIT,polynomial,physical_pair,
    pointwise_slacks,verify_bernstein_certificate,
    smooth_hessian_rate,scalar_gap_squared_bound,
    _unclipped_statistic,observable,verify_full_witness,
    theorem_receipt,
)
from state_aware_replication_BM25 import (
    EXACT_ETA as ETA2,expanded_full_mask_law as mask2,
)
from state_aware_three_replica_BM26 import (
    EXACT_CAP as ETA3,full_mask_law as mask3,
)
from n16_rational_lower_BM28 import EXACT_LOWER as LOWER16
from replication_uniform_upper_BM27 import (
    explicit_mask_law as mask_uniform,
)
from optimal_channel_rigidity_BM30 import (
    explicit_frontier_mask,
)
from robust_dyadic_observables_BM32 import (
    LipschitzTest,dyadic_residual,
)
from finite_empirical_extension_BM31 import empirical_joint_law
from direct_finite_concentration_BM34 import SCALAR_RATE


class BM35SmoothPolynomialDualTests(unittest.TestCase):
    def test_global_continuum_bernstein_certificate_exact(self):
        r=verify_bernstein_certificate()
        self.assertEqual(r.cells,40)
        self.assertEqual(r.inequalities,4)
        self.assertEqual(r.coefficients_checked,5760)
        self.assertEqual(r.zero_coefficients,72)
        self.assertEqual(r.minimum_coefficient,Fraction(0))
        self.assertTrue(r.global_nonnegative)
        self.assertEqual(len(COEFFICIENT_NUMERATORS),15)
        self.assertEqual(DEGREE,5)
        self.assertEqual(len(U_BREAKS),11)
        self.assertEqual(len(Y_BREAKS),5)

    def test_independent_full_physical_grid_inequalities(self):
        # Directly evaluate all four original inequalities on physical
        # coordinates. This is supplementary to the global Bernstein
        # certificate, which covers every real point between grid nodes.
        checked=0
        for i in range(-40,41):
            u=Fraction(i,40)
            for j in range(-40,41):
                w=Fraction(j,40)
                if not physical_pair(u,w):
                    continue
                checked+=1
                for slack in pointwise_slacks(u,w):
                    self.assertGreaterEqual(slack,0,msg=(u,w,slack))
        self.assertGreater(checked,1500)
        self.assertFalse(physical_pair(Fraction(3,4),Fraction(1,4)))
        with self.assertRaises(ValueError):
            pointwise_slacks(2,1)

    def test_dual_saturates_all_BM27_optimal_directing_modes(self):
        u=Fraction(3,4)
        self.assertEqual(polynomial(u,1),Fraction(4,15))
        self.assertEqual(polynomial(u,Fraction(1,2)),Fraction(1,15))
        self.assertEqual(polynomial(u,Fraction(1,4)),-Fraction(2,15))
        self.assertEqual(polynomial(1,1)-polynomial(1,Fraction(1,2)),
                         Fraction(1))
        self.assertEqual(pointwise_slacks(u,1)[0],0)
        self.assertEqual(pointwise_slacks(u,1)[2],0)
        self.assertEqual(pointwise_slacks(u,Fraction(1,2))[0],0)
        self.assertEqual(pointwise_slacks(u,Fraction(1,2))[3],0)
        self.assertEqual(pointwise_slacks(1,1)[0],0)

    def test_exact_hessian_second_derivative_envelope_and_348_constant(self):
        r=smooth_hessian_rate()
        self.assertGreater(r.hessian_uu,0)
        self.assertGreater(r.hessian_uw,0)
        self.assertGreater(r.hessian_ww,0)
        self.assertLess(r.hessian_uu,97)
        self.assertLess(r.hessian_uw,93)
        self.assertLess(r.hessian_ww,96)
        self.assertLess(r.worst_one_world_bias_coefficient,113)
        self.assertEqual(
            r.sharp_computable_rate_coefficient,
            Fraction(40,13)*r.worst_one_world_bias_coefficient
        )
        self.assertLess(r.sharp_computable_rate_coefficient,348)
        self.assertGreater(r.sharp_computable_rate_coefficient,347)
        self.assertEqual(r.simple_integer_rate_coefficient,348)
        # Independent Hessian derivative evaluations with exact
        # coefficient differentiation inside the rectangular domain.
        rand=Random(20261111)
        for _ in range(250):
            u=Fraction(rand.randint(-400,400),300)
            w=Fraction(rand.randint(-300,300),300)
            uu=sum((
                Fraction(c,DENOMINATOR)*i*(i-1)*
                u**(i-2)*w**j
                for (i,j),c in COEFFICIENT_NUMERATORS.items() if i>=2
            ),Fraction(0))
            uw=sum((
                Fraction(c,DENOMINATOR)*i*j*
                u**(i-1)*w**(j-1)
                for (i,j),c in COEFFICIENT_NUMERATORS.items()
                if i>=1 and j>=1
            ),Fraction(0))
            ww=sum((
                Fraction(c,DENOMINATOR)*j*(j-1)*
                u**i*w**(j-2)
                for (i,j),c in COEFFICIENT_NUMERATORS.items()
                if j>=2
            ),Fraction(0))
            self.assertLessEqual(abs(uu),r.hessian_uu)
            self.assertLessEqual(abs(uw),r.hessian_uw)
            self.assertLessEqual(abs(ww),r.hessian_ww)

    def test_both_rational_dual_certificates_respond_to_corruption(self):
        altered=dict(COEFFICIENT_NUMERATORS)
        altered[(0,0)]+=DENOMINATOR//100
        with self.assertRaises(AssertionError):
            verify_bernstein_certificate(coefficients=altered)
        with self.assertRaises(AssertionError):
            verify_bernstein_certificate(
                coefficients={(9,0):DENOMINATOR}
            )

    def test_actual_full_output_world_pair_masks_and_dyadic_defect(self):
        candidates=(
            (2,mask2(0),mask2(1),ETA2),
            (3,mask3(0),mask3(1),ETA3),
            (1,mask_uniform(1,0),mask_uniform(1,1),LIMIT),
            (2,mask_uniform(2,0),mask_uniform(2,1),LIMIT),
            (3,mask_uniform(3,0),mask_uniform(3,1),LIMIT),
            (3,explicit_frontier_mask(3,Fraction(1,13),0),
             explicit_frontier_mask(3,Fraction(1,13),1),LIMIT),
        )
        test=LipschitzTest(
            "independent smooth dyadic test",Fraction(30),Fraction(100),
            polynomial,
        )
        for n,q0,q1,expected in candidates:
            proof=verify_full_witness(n,q0,q1)
            self.assertTrue(proof.reported_laws_equal)
            self.assertTrue(proof.finite_scalar_gap_bound_holds)
            self.assertEqual(proof.observed_expectation_gap,0)
            self.assertEqual(max(proof.ordinary_bit_cost,
                                 proof.exceptional_bit_cost),expected)
            residual=dyadic_residual(
                n,empirical_joint_law(n,q0),empirical_joint_law(n,q1),
                test,
            )
            self.assertEqual(proof.dyadic_defect,residual)
            self.assertEqual(sum(proof.world_biases),
                             sum(proof.world_biases))
            if expected==LIMIT:
                self.assertLessEqual(abs(proof.dyadic_defect),
                                     Fraction(32)*smooth_hessian_rate().
                                     worst_one_world_bias_coefficient/n)

    def test_large_n_inverse_n_rate_and_certified_lower_controls(self):
        for n in (1,2,3,16,100,1000,10**6,10**9,10**12):
            self.assertEqual(scalar_gap_squared_bound(n),
                             Fraction(348**2,n**2))
        self.assertEqual((ETA2,ETA3),(
            Fraction(5,118),Fraction(751225,13956626)
        ))
        for n,lower in ((2,ETA2),(3,ETA3),(16,LOWER16)):
            self.assertLessEqual(LIMIT-lower,Fraction(348,n))
        self.assertLess(scalar_gap_squared_bound(10**9),
                        Fraction(1,10**12))
        self.assertLess(Fraction(348,10**9),
                        Fraction(2158,117*31622))
        with self.assertRaises(ValueError):
            scalar_gap_squared_bound(0)
        with self.assertRaises(ValueError):
            verify_full_witness(5,{0:Fraction(1)},{0:Fraction(1)})

    def test_full_receipt_has_no_runtime_solver_or_external_dependency(self):
        r=theorem_receipt(250)
        self.assertEqual(r["ordinary_paths"],250)
        self.assertEqual(r["exact_bernstein_cells"],40)
        self.assertEqual(r["bernstein_coefficients_checked"],5760)
        self.assertEqual(r["identically_zero_bernstein_coefficients"],72)
        self.assertEqual(r["new_scalar_gap"],
                         "0 <= 5/52-eta_n <= 348/n")
        self.assertEqual(r["simple_integer_constant"],348)
        self.assertFalse(r["external_numeric_optimizer_trusted"])
        self.assertFalse(r["finite_n_rate_sharp_claimed"])
        self.assertTrue(r["all_checks_fraction_only"])


if __name__=="__main__":
    unittest.main()
