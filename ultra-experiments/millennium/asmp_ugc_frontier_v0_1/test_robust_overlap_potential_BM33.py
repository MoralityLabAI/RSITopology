"""BM-33: independent rational verification of a global Lipschitz dual.

Analytic verification uses a finite set of piecewise-affine breakpoints
and convex interpolation. A separate dense rational grid probes the
FULL physical symmetric pair-mask domain, including negative u/w and
u close to 3/4. Exact finite atom tests include the BM-27 and BM-30
equality cases and signed measures with nonzero dyadic residuals.

This test suite also checks the explicit finite-n scalar convergence
bound against registered exact n=2/3 optima and the n=16 lower
certificate. The bound is conservative for moderate n but vanishes at
a provable O(n^-1/3) rate without a numerical LP solver.
"""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from robust_overlap_potential_BM33 import (
    HALF,LOW_U,HIGH_U,SUP_NORM,LIP_L1,
    RATE_COLLISION,RATE_SAMPLING,C,LIMIT,
    base_potential,robust_potential,physical_pair,
    pointwise_receipt,verify_analytic_potential,
    overlap_dual_gap,finite_rate,optimized_window_rate,
    certify_known_eta,symbolic_rate_manifest,
)
from infinite_replication_rigidity_BM29 import (
    bm27_directing_atoms,verify_bm27_equality_case,
)
from optimal_channel_rigidity_BM30 import (
    canonical_equality_atoms,
)
from state_aware_replication_BM25 import EXACT_ETA as ETA2
from state_aware_three_replica_BM26 import EXACT_CAP as ETA3
from n16_rational_lower_BM28 import EXACT_LOWER as LOWER16
from finite_empirical_extension_BM31 import (
    finite_alphabet_tv_squared_bound,
)


def independent_four_corner_criterion(u,w):
    """Directly maximize the pointwise signed-measure inequality over corners."""
    f=robust_potential(u,w)
    g=robust_potential(u,w/2)
    A=2*f+7*g
    B=-f-8*g
    vals=tuple(
        min(a,b)-A*a-B*b
        for a,b in product((-1,1),repeat=2)
    )
    return max(vals),C*(1-u)


def directing(atom_table):
    mu,nu0,nu1,v={}, {}, {}, {}
    for a in atom_table:
        if a.mu:
            key=(a.u,a.w)
            mu[key]=a.mu
            nu0[key]=a.nu0
            nu1[key]=a.nu1
            v[key]=a.v
    return mu,nu0,nu1,v


class BM33RobustDualTests(unittest.TestCase):
    def test_global_piecewise_potential_breakpoint_proof_exact(self):
        receipt=verify_analytic_potential()
        self.assertEqual(receipt["base_affine_segments"],3)
        self.assertEqual(receipt["physical_u_regimes"],3)
        self.assertEqual(receipt["sup_bound"],Fraction(5,6))
        self.assertEqual(receipt["l1_lipschitz_bound"],Fraction(64,15))
        self.assertEqual((RATE_COLLISION,RATE_SAMPLING),
                         (Fraction(200,39),Fraction(3584,117)))
        for w in (Fraction(3,8),Fraction(1,2),
                  Fraction(3,4),Fraction(1)):
            self.assertEqual(base_potential(w)-base_potential(w/2),
                             Fraction(1,5))
            self.assertLessEqual(
                abs(3*base_potential(w)+15*base_potential(w/2)),
                Fraction(9,5)
            )

    def test_dense_rational_grid_of_full_physical_mask_region(self):
        # All 10,201 rational (u,w) grid coordinates with denominator 100,
        # filtered to the physical symmetric two-bit probability region.
        points=0
        for a in range(-100,101):
            u=Fraction(a,100)
            for b in range(-100,101):
                w=Fraction(b,100)
                if not physical_pair(u,w):
                    continue
                points+=1
                result=pointwise_receipt(u,w)
                want,cap=independent_four_corner_criterion(u,w)
                self.assertLessEqual(want,cap)
                self.assertGreaterEqual(result.overlap_slack,0)
                self.assertGreaterEqual(result.budget_slack,0)
                self.assertLessEqual(abs(result.potential),SUP_NORM)
                self.assertLessEqual(abs(result.shifted_potential),SUP_NORM)
        self.assertGreater(points,20000)

    def test_piecewise_potential_exact_continuity_and_lipschitz(self):
        rng=Random(20261110)
        pairs=[]
        for _ in range(300):
            u=Fraction(rng.randint(-10000,10000),10000)
            w=Fraction(rng.randint(-10000,10000),10000)
            pairs.append((u,w))
        for u,w in pairs:
            self.assertLessEqual(abs(robust_potential(u,w)),SUP_NORM)
        for _ in range(1200):
            u,w=pairs[rng.randrange(len(pairs))]
            uu,ww=pairs[rng.randrange(len(pairs))]
            self.assertLessEqual(
                abs(robust_potential(u,w)-robust_potential(uu,ww)),
                LIP_L1*(abs(u-uu)+abs(w-ww))
            )
        for w in (Fraction(-1),0,Fraction(1,4),
                  Fraction(1,2),Fraction(1)):
            self.assertEqual(
                robust_potential(LOW_U,w),0
            )
            self.assertEqual(
                robust_potential(HIGH_U,w),base_potential(w)
            )
        for bad in ((2,0),(0,2),(-2,1)):
            with self.assertRaises(ValueError):
                robust_potential(*bad)

    def test_pointwise_dual_saturated_by_BM27_modes(self):
        at_high=pointwise_receipt(Fraction(3,4),1)
        at_low=pointwise_receipt(Fraction(3,4),Fraction(1,2))
        at_I=pointwise_receipt(1,1)
        for r in (at_high,at_low,at_I):
            self.assertEqual(r.overlap_slack,0)
        self.assertEqual(at_high.budget_slack,0)
        self.assertEqual(at_low.budget_slack,0)
        self.assertEqual(at_I.potential,Fraction(5,6))
        self.assertEqual(at_I.shifted_potential,-Fraction(1,6))
        self.assertEqual(at_high.potential,Fraction(4,15))
        self.assertEqual(at_high.shifted_potential,Fraction(1,15))
        self.assertEqual(at_low.potential,Fraction(1,15))
        self.assertEqual(at_low.shifted_potential,-Fraction(2,15))
        with self.assertRaises(ValueError):
            pointwise_receipt(Fraction(3,4),0)

    def test_signed_measure_overlap_bound_saturates_BM27_BM30(self):
        old=bm27_directing_atoms()
        table=[
            (old[name]["u"],old[name]["w"],old[name]["mu"],
             old[name]["nu0"],old[name]["nu1"],old[name]["v"])
            for name in ("I","A","B")
        ]
        self.assertEqual(sum((x[2] for x in table),Fraction(0)),1)
        values=overlap_dual_gap(*directing(
            canonical_equality_atoms(Fraction(1,13))
        ))
        self.assertEqual(values["dyadic_defect"],0)
        self.assertEqual(values["weighted_cost"],Fraction(5,4))
        self.assertEqual(values["weighted_lower"],Fraction(5,4))
        self.assertEqual(values["overlap_slack"],0)
        self.assertEqual(values["weighted_slack"],0)
        self.assertEqual(values["ordinary_bit_cost"],LIMIT)
        self.assertEqual(values["exceptional_bit_cost"],LIMIT)
        for c in (Fraction(0),Fraction(1,100),
                  Fraction(1,20),Fraction(1,13),Fraction(1,10)):
            result=overlap_dual_gap(*directing(canonical_equality_atoms(c)))
            self.assertEqual(result["dyadic_defect"],0)
            self.assertEqual(result["overlap_slack"],0)
            self.assertEqual(result["weighted_slack"],0)

    def test_approximate_signed_measures_without_dyadic_flow_still_pass(self):
        rng=Random(20261110)
        states=((Fraction(1),Fraction(1)),
                (Fraction(3,4),Fraction(1)),
                (Fraction(3,4),Fraction(1,2)),
                (Fraction(1,2),0),
                (Fraction(-1,2),0))
        for _ in range(200):
            raw=[rng.randint(1,50) for _ in states]
            total=sum(raw)
            mu={state:Fraction(x,total) for state,x in zip(states,raw)}
            nu0={}
            nu1={}
            special={}
            for state,m in mu.items():
                a=m*Fraction(rng.randint(-10,10),10)
                b=m*Fraction(rng.randint(-10,10),10)
                nu0[state]=a
                nu1[state]=b
                special[state]=(m+min(a,b))/2
            result=overlap_dual_gap(mu,nu0,nu1,special)
            self.assertGreaterEqual(result["overlap_slack"],0)
            self.assertGreaterEqual(result["weighted_slack"],0)
            self.assertGreaterEqual(
                result["weighted_cost"],
                result["weighted_lower"]
            )
        with self.assertRaises(ValueError):
            overlap_dual_gap({(1,1):1},{(1,1):2},{},{})
        with self.assertRaises(ValueError):
            overlap_dual_gap({(1,1):1},{},{},{(0,0):0})

    def test_exact_rational_squared_rate_and_independent_thresholds(self):
        for n in (2,3,4,16,100,1000,10**6,10**9):
            for k in (1,2,min(n,3),min(n,10),n):
                if k>n:
                    continue
                rate=finite_rate(n,k)
                v=finite_alphabet_tv_squared_bound(n,k)
                self.assertEqual(rate.collision_variance,v)
                self.assertEqual(rate.bound_squared,2*(
                    RATE_COLLISION**2*v+RATE_SAMPLING**2/k
                ))
                self.assertTrue(rate.threshold_rate_proved)
            opt=optimized_window_rate(n)
            self.assertTrue(1<=opt.k<=n)
        self.assertTrue(certify_known_eta(2,ETA2))
        self.assertTrue(certify_known_eta(3,ETA3))
        self.assertTrue(certify_known_eta(16,LOWER16))
        with self.assertRaises(ValueError):
            finite_rate(1,1)
        with self.assertRaises(ValueError):
            finite_rate(10,11)
        with self.assertRaises(ValueError):
            certify_known_eta(3,LIMIT+Fraction(1,10))

    def test_large_n_bound_is_nontrivial_and_has_correct_symbolic_rate(self):
        a=optimized_window_rate(10**9)
        b=optimized_window_rate(10**12)
        c=optimized_window_rate(10**15)
        self.assertEqual(a.k,10**6)
        self.assertEqual(b.k,10**8)
        self.assertEqual(c.k,10**10)
        self.assertLess(c.bound_squared,b.bound_squared)
        self.assertLess(b.bound_squared,a.bound_squared)
        self.assertLess(a.bound_squared,LIMIT**2)
        self.assertLess(
            b.bound_squared,Fraction(1,10000)
        )
        info=symbolic_rate_manifest(10**12)
        self.assertTrue(info["finite_scalar_threshold_rate_proved"])
        self.assertEqual(info["limit"],"5/52")
        self.assertEqual(info["rate"],"eta_inf-eta_n=O(n^(-1/3))")
        self.assertFalse(info["measure_theory_formalized_in_Lean"])


if __name__=="__main__":
    unittest.main()
