"""BM-32: robust dyadic signed-measure equation from finite observations.

Independently checks conditional q8 pair character means, the latent
signed pushforward coefficients, empirical-observable TV bounds, the
finite-n KL/Pinsker-to-dyadic composite and symbolic million-path
horizons. Finite tests rely on actual registered BM-25/26/27/30 masks.
"""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from robust_dyadic_observables_BM32 import (
    LipschitzTest,TESTS,
    dyadic_residual,empirical_observable,observable_expectation,
    robust_sampling_term_squared,assert_robust_dyadic_inequality,
    finite_n_squared_bound,empirical_extended_outputs,
    certify_finite_dyadic_window,growing_horizon_rate,
)
from finite_empirical_extension_BM31 import (
    empirical_joint_law,finite_alphabet_tv_squared_bound,
    collision_bound,total_variation,with_replacement_window,
)
from replication_uniform_upper_BM27 import (
    PAIR_A,PAIR_B,PAIR_I,PAIR_E,
    xor_pair,explicit_mask_law,exact_clean_law,xor_convolve,
)
from state_aware_replication_BM25 import (
    expanded_full_mask_law as bm25_mask,
)
from state_aware_three_replica_BM26 import (
    full_mask_law as bm26_mask,
)
from optimal_channel_rigidity_BM30 import (
    explicit_frontier_mask,
)
from infinite_replication_rigidity_BM29 import (
    pair_walsh,verify_bm27_equality_case,
)


def registered_cases():
    yield "BM25",2,bm25_mask(0),bm25_mask(1)
    yield "BM26",3,bm26_mask(0),bm26_mask(1)
    for n in (1,2,3,4):
        yield "BM27",n,explicit_mask_law(n,0),explicit_mask_law(n,1)
    for c in (Fraction(0),Fraction(1,20),Fraction(1,13),
              Fraction(1,10)):
        for n in (2,3):
            yield "BM30",n,(
                explicit_frontier_mask(n,c,0)
            ),explicit_frontier_mask(n,c,1)


def direct_signed_test(n,j0,j1,test):
    """Recompute signed flow from the two output-component regimes."""
    total=Fraction(0)
    for h,joint in enumerate((j0,j1)):
        for (hist,special),p in joint.items():
            u=Fraction(hist[0]-hist[2],n)
            w=Fraction(hist[0]-hist[1]+hist[2],n)
            parity=-1 if special in (1,2) else 1
            if h==0:
                total+=p*parity*(
                    16*Fraction(1,8)*test.evaluate(u,w)+
                    16*Fraction(7,16)*test.evaluate(u,w/2)
                )
            else:
                total-=p*parity*(
                    16*Fraction(1,16)*test.evaluate(u,w)+
                    16*Fraction(1,2)*test.evaluate(u,w/2)
                )
    return total


def pair_character_average(law,S):
    return sum((p*(-1 if (x&S).bit_count()%2 else 1)
                for x,p in enumerate(law)),Fraction(0))


class BM32RobustDyadicTests(unittest.TestCase):
    def test_conditional_pair_output_estimators_are_unbiased(self):
        for mask in (PAIR_I,PAIR_A,PAIR_B,PAIR_E):
            mu=pair_walsh(mask)
            u=mu[1]
            w=mu[3]
            for clean,scale in ((PAIR_A,1),(PAIR_B,Fraction(1,2))):
                output=xor_pair(clean,mask)
                one0=pair_character_average(output,1)
                one1=pair_character_average(output,2)
                both=pair_character_average(output,3)
                self.assertEqual(Fraction(2,3)*(one0+one1),u)
                self.assertEqual(both,w*scale)
                self.assertLessEqual(
                    sum((p*((Fraction(2,3)*((
                        1 if not x&1 else -1
                    )+(
                        1 if not x&2 else -1
                    )))**2) for x,p in enumerate(output)),Fraction(0)),
                    Fraction(16,9)
                )

    def test_latent_signed_pushforward_matches_direct_coefficients(self):
        for name,n,a,b in registered_cases():
            j0=empirical_joint_law(n,a)
            j1=empirical_joint_law(n,b)
            for test in TESTS:
                self.assertEqual(
                    dyadic_residual(n,j0,j1,test),
                    direct_signed_test(n,j0,j1,test),
                    msg=(name,n,test.name)
                )
                # The empirical-iid REPLACEMENT of a finite sample
                # generally differs from its original infinite directing
                # mixture, even for the BM27/30 all-n mask families.
                # Signed defects are bounded quantitatively below.

    def test_finite_window_signed_dyadic_bound_on_all_exact_witnesses(self):
        for name,n,a,b in registered_cases():
            for k in range(1,min(n,3)+1):
                for test in TESTS:
                    receipt=certify_finite_dyadic_window(n,k,a,b,test)
                    self.assertEqual((receipt.n,receipt.k),(n,k))
                    self.assertEqual(receipt.test_name,test.name)
                    self.assertTrue(receipt.finite_n_bound_verified)
                    self.assertLessEqual(abs(receipt.observed_statistic_difference),
                                         2*test.bound*receipt.output_total_variation)
                    self.assertLessEqual(receipt.signed_dyadic_defect**2,
                                         receipt.finite_n_bound_squared)
                    self.assertLessEqual(
                        receipt.output_total_variation**2,
                        4*finite_alphabet_tv_squared_bound(n,k)
                    )

    def test_observable_is_bounded_and_restricts_to_latent_test_domain(self):
        for k in (1,2,3):
            for mask in range(1<<(2*k+2)):
                for test in TESTS:
                    self.assertLessEqual(abs(empirical_observable(mask,k,test)),
                                         test.bound)
            with self.assertRaises(ValueError):
                empirical_observable(1<<(2*k+2),k,TESTS[0])
        with self.assertRaises(ValueError):
            TESTS[0].evaluate(Fraction(4,3),0)

    def test_exact_signed_bound_rejects_violated_claims(self):
        self.assertTrue(assert_robust_dyadic_inequality(
            Fraction(1),Fraction(0),100,
            bound=Fraction(1),lipschitz=Fraction(1)
        ))
        with self.assertRaises(AssertionError):
            assert_robust_dyadic_inequality(
                Fraction(100),Fraction(0),100,
                bound=Fraction(1),lipschitz=Fraction(1)
            )
        self.assertTrue(assert_robust_dyadic_inequality(
            Fraction(1),Fraction(1,10),100,
            bound=Fraction(1),lipschitz=Fraction(0)
        ))
        with self.assertRaises(ValueError):
            assert_robust_dyadic_inequality(
                0,Fraction(-1),1
            )
        with self.assertRaises(ValueError):
            robust_sampling_term_squared(0,1)

    def test_symbolic_finite_n_bl_dual_rate_is_explicit_and_vanishing(self):
        last=None
        for n in (1,8,64,1000,10**6,10**9,10**12):
            report=growing_horizon_rate(n)
            k=report["window_ordinary_paths"]
            self.assertTrue(k**3<=n**2<(k+1)**3)
            expected=finite_n_squared_bound(n,k)
            self.assertEqual(
                report["bounded_lipschitz_defect_squared_upper"],expected
            )
            self.assertFalse(report["explicit_threshold_rate_claimed"])
            self.assertFalse(report["external_numeric_solver_used"])
            if n>=10**6:
                if last is not None:
                    self.assertLess(expected,last)
                last=expected
        self.assertLess(
            growing_horizon_rate(10**12)[
                "bounded_lipschitz_defect_squared_upper"],
            Fraction(1,2500) # BL defect below 2% at n=10^12
        )

    def test_finite_window_estimator_matches_independent_output_convolution(self):
        n=3
        j0=empirical_joint_law(n,bm26_mask(0))
        j1=empirical_joint_law(n,bm26_mask(1))
        for k in (1,2,3):
            out0,out1=empirical_extended_outputs(n,k,j0,j1)
            for h,j in enumerate((j0,j1)):
                q=with_replacement_window(n,k,j)
                clean=exact_clean_law(k,h)
                self.assertEqual((out0,out1)[h],xor_convolve(clean,q))
            for test in TESTS:
                reference=sum(
                    (p*empirical_observable(x,k,test) for x,p in out0.items()),
                    Fraction(0)
                )-sum(
                    (p*empirical_observable(x,k,test) for x,p in out1.items()),
                    Fraction(0)
                )
                self.assertEqual(reference,
                    observable_expectation(k,out0,test)-
                    observable_expectation(k,out1,test)
                )

    def test_nontrivial_finite_mask_certificate_can_have_signed_defect(self):
        # Finite-n world-aware optimum may fail the infinite signed
        # flow constraint, even though the FINITE output laws agree.
        n=2
        j0=empirical_joint_law(n,bm25_mask(0))
        j1=empirical_joint_law(n,bm25_mask(1))
        vals=tuple(dyadic_residual(n,j0,j1,test) for test in TESTS)
        self.assertTrue(any(v!=0 for v in vals))
        self.assertLessEqual(
            max(abs(v) for v in vals)**2,
            max(finite_n_squared_bound(n,n,bound=t.bound,
                  lipschitz=t.lipschitz) for t in TESTS)
        )

    def test_exact_bound_preserves_role_of_observation_tv(self):
        for n,k in ((2,2),(3,2),(5,3),(100,10),(10**6,10**4)):
            B,L=Fraction(1,2),Fraction(2,3)
            b=finite_n_squared_bound(n,k,bound=B,lipschitz=L)
            e2=finite_alphabet_tv_squared_bound(n,k)
            self.assertEqual(
                b,2*(4096*B*B*e2+
                     Fraction(224,3)**2*L*L/k)
            )
            self.assertGreaterEqual(b,0)
        with self.assertRaises(ValueError):
            finite_n_squared_bound(2,1,bound=-1)
        with self.assertRaises(ValueError):
            finite_n_squared_bound(2,1,lipschitz=-1)


if __name__=="__main__":
    unittest.main()
