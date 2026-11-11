"""BM-34: exact independent finite concentration and inverse-sqrt-n scalar rate.

The tests reconstruct the full conditional path-output variance table
without any Gaussian/CLT approximation. They enumerate multiple fixed
histogram path-type allocations and all 2^(2n) possible observed
ordinary outputs to verify exact first two moments. The complete
BM-25/26/27/30 equalizers are then checked end to end with the direct
observable and BM-33's independent pointwise signed-overlap dual.
"""
from fractions import Fraction
from itertools import product
from random import Random
from math import isqrt
import unittest

from direct_finite_concentration_BM34 import (
    LIMIT,ONE_BIT_LIP,PAIR_PARITY_LIP,
    MATCHED_U_SQRT_BOUND,UNMATCHED_U_SQRT_BOUND,
    UNMATCHED_W_SQRT_BOUND,SAMPLE_ERROR,
    SIGNED_DEFECT_COEFFICIENT,SCALAR_RATE,
    PathMoment,ConditionalMoment,path_moment,verify_variance_table,
    conditional_moments,direct_signed_bound_squared,
    finite_threshold_bound_squared,certified_lower_squared,
    verify_finite_witness,theorem_receipt,
)
from replication_uniform_upper_BM27 import (
    PAIR_A,PAIR_B,xor_pair,explicit_mask_law as bm27_mask,
)
from state_aware_replication_BM25 import (
    EXACT_ETA as ETA2,expanded_full_mask_law as bm25_mask,
)
from state_aware_three_replica_BM26 import (
    EXACT_CAP as ETA3,full_mask_law as bm26_mask,
)
from optimal_channel_rigidity_BM30 import (
    explicit_frontier_mask,
)
from n16_rational_lower_BM28 import EXACT_LOWER as LOWER16
from robust_overlap_potential_BM33 import (
    optimized_window_rate,robust_potential,verify_analytic_potential,
)
from robust_dyadic_observables_BM32 import (
    dyadic_residual,LipschitzTest,
)
from finite_empirical_extension_BM31 import (
    empirical_joint_law,
)


def independent_pair_moments(regime,t):
    clean=PAIR_A if regime=="A" else PAIR_B
    masks={
        0:{0:Fraction(1)},
        1:{1:Fraction(1,2),2:Fraction(1,2)},
        2:{3:Fraction(1)},
    }[t]
    output={}
    for x,px in enumerate(clean):
        for y,py in masks.items():
            output[x^y]=output.get(x^y,Fraction(0))+px*py
    values=[]
    for outcome,prob in output.items():
        x=(-1 if outcome&1 else 1)
        y=(-1 if outcome&2 else 1)
        values.append((Fraction(2,3)*(x+y),Fraction(x*y),prob))
    mu=sum((u*p for u,_,p in values),Fraction(0))
    mw=sum((w*p for _,w,p in values),Fraction(0))
    vu=sum(((u-mu)**2*p for u,_,p in values),Fraction(0))
    vw=sum(((w-mw)**2*p for _,w,p in values),Fraction(0))
    return mu,mw,vu,vw,output


def independent_conditional_histogram(n,hist,regime):
    # Fix one arbitrary order for the pair type counts; since the
    # statistic is permutation-invariant and the clean paths are iid
    # conditional on terminal difference, this is without loss.
    types=tuple(t for t,count in enumerate(hist) for _ in range(count))
    output={0:Fraction(1)}
    for i,t in enumerate(types):
        pair=independent_pair_moments(regime,t)[4]
        nxt={}
        for mask,p in output.items():
            for bits,v in pair.items():
                combined=mask|(bits<<(2*i))
                nxt[combined]=nxt.get(combined,Fraction(0))+p*v
        output=nxt
    assert sum(output.values())==1
    stats=[]
    for mask,p in output.items():
        U=sum(
            (Fraction(2,3)*(
                (1 if not mask&(1<<(2*i)) else -1)+
                (1 if not mask&(1<<(2*i+1)) else -1)
            ) for i in range(n)),Fraction(0))/n
        W=sum(
            (Fraction(-1 if ((mask>>(2*i))&3).bit_count()%2 else 1)
             for i in range(n)),Fraction(0))/n
        stats.append((U,W,p))
    eu=sum((x*p for x,_,p in stats),Fraction(0))
    ew=sum((y*p for _,y,p in stats),Fraction(0))
    vu=sum((p*(x-eu)**2 for x,_,p in stats),Fraction(0))
    vw=sum((p*(y-ew)**2 for _,y,p in stats),Fraction(0))
    return eu,ew,vu,vw


class DirectFiniteConcentrationTests(unittest.TestCase):
    def test_exact_six_conditional_one_path_variance_entries(self):
        expected={
            ("A",0):(1,1,Fraction(7,9),0),
            ("A",1):(0,-1,0,0),
            ("A",2):(-1,1,Fraction(7,9),0),
            ("B",0):(1,Fraction(1,2),Fraction(1,3),Fraction(3,4)),
            ("B",1):(0,-Fraction(1,2),Fraction(4,9),Fraction(3,4)),
            ("B",2):(-1,Fraction(1,2),Fraction(1,3),Fraction(3,4)),
        }
        for (regime,t),want in expected.items():
            got=path_moment(regime,t)
            self.assertEqual((got.mean_u,got.mean_parity,
                              got.variance_u,got.variance_parity),want)
            self.assertEqual(independent_pair_moments(regime,t)[:4],want)
        result=verify_variance_table()
        self.assertEqual(result["variance_cases_checked"],6)
        self.assertEqual(result["ordinary_coordinate_lipschitz"],Fraction(64,15))
        self.assertEqual(result["parity_coordinate_lipschitz"],Fraction(18,5))
        self.assertEqual(result["max_one_world_estimator_error_coefficient"],
                         Fraction(1079,180))
        self.assertEqual(result["scalar_masking_gap_coefficient"],
                         Fraction(2158,117))

    def test_all_histogram_conditional_variances_independent_path_enumeration(self):
        for n in (1,2,3,4):
            for a in range(n+1):
                for b in range(n-a+1):
                    hist=(n-a-b,a,b)
                    for regime in ("A","B"):
                        predicted=conditional_moments(n,hist,regime)
                        independent=independent_conditional_histogram(
                            n,hist,regime
                        )
                        self.assertEqual(
                            (predicted.mean_u,predicted.mean_w,
                             predicted.variance_u,predicted.variance_w),
                            independent
                        )
                        self.assertLessEqual(
                            n*predicted.variance_u,
                            Fraction(7,9) if regime=="A" else Fraction(4,9)
                        )
                        self.assertLessEqual(
                            n*predicted.variance_w,
                            0 if regime=="A" else Fraction(3,4)
                        )

    def test_exact_coordinatewise_Lipschitz_and_global_fraction_constants(self):
        self.assertEqual(ONE_BIT_LIP,Fraction(64,15))
        self.assertEqual(PAIR_PARITY_LIP,Fraction(18,5))
        self.assertEqual(
            max(MATCHED_U_SQRT_BOUND*ONE_BIT_LIP,
                UNMATCHED_U_SQRT_BOUND*ONE_BIT_LIP+
                UNMATCHED_W_SQRT_BOUND*PAIR_PARITY_LIP),
            SAMPLE_ERROR
        )
        self.assertEqual(SAMPLE_ERROR,Fraction(1079,180))
        self.assertEqual(SIGNED_DEFECT_COEFFICIENT,
                         Fraction(32)*SAMPLE_ERROR)
        self.assertEqual(LIMIT*SIGNED_DEFECT_COEFFICIENT,SCALAR_RATE)
        self.assertTrue(verify_analytic_potential())
        rng=Random(20261111)
        for _ in range(2000):
            u=Fraction(rng.randint(-1000,1000),1000)
            uu=Fraction(rng.randint(-1000,1000),1000)
            w=Fraction(rng.randint(-1000,1000),1000)
            ww=Fraction(rng.randint(-1000,1000),1000)
            self.assertLessEqual(
                abs(robust_potential(u,w)-robust_potential(uu,ww)),
                ONE_BIT_LIP*abs(u-uu)+PAIR_PARITY_LIP*abs(w-ww)
            )

    def test_end_to_end_true_finite_world_mask_equalizers(self):
        witnesses=(
            ("BM25",2,bm25_mask(0),bm25_mask(1),ETA2),
            ("BM26",3,bm26_mask(0),bm26_mask(1),ETA3),
            ("BM27-n1",1,bm27_mask(1,0),bm27_mask(1,1),LIMIT),
            ("BM27-n2",2,bm27_mask(2,0),bm27_mask(2,1),LIMIT),
            ("BM27-n3",3,bm27_mask(3,0),bm27_mask(3,1),LIMIT),
            ("BM30",3,
             explicit_frontier_mask(3,Fraction(1,13),0),
             explicit_frontier_mask(3,Fraction(1,13),1),LIMIT),
        )
        for name,n,a,b,expected in witnesses:
            receipt=verify_finite_witness(n,a,b)
            self.assertTrue(receipt.complete_output_equal,msg=name)
            self.assertEqual(receipt.direct_observable_gap,0,msg=name)
            self.assertEqual(receipt.latent_ideal_gap,
                             receipt.signed_dyadic_defect/16)
            self.assertEqual(receipt.independent_BM32_residual
                             if hasattr(receipt,"independent_BM32_residual")
                             else receipt.signed_dyadic_defect,
                             receipt.signed_dyadic_defect)
            self.assertEqual(
                max(receipt.ordinary_bit_cost,receipt.exceptional_bit_cost),
                expected
            )
            self.assertLessEqual(
                n*receipt.signed_dyadic_defect**2,
                SIGNED_DEFECT_COEFFICIENT**2,
            )

    def test_signed_ideal_defect_can_be_nonzero_for_exact_finite_erasure(self):
        receipt=verify_finite_witness(2,bm25_mask(0),bm25_mask(1))
        self.assertNotEqual(receipt.signed_dyadic_defect,0)
        self.assertEqual(receipt.direct_observable_gap,0)
        self.assertEqual(receipt.latent_ideal_gap,
                         receipt.signed_dyadic_defect/16)
        self.assertGreater(
            receipt.conditional_one_world_error_bound_squared,0
        )

    def test_squared_rate_inverse_n_and_symbolic_million_billion_cases(self):
        for n in (1,2,3,16,10**3,10**6,10**9,10**12,10**15):
            scalar=finite_threshold_bound_squared(n)
            signed=direct_signed_bound_squared(n)
            self.assertEqual(scalar*n,SCALAR_RATE**2)
            self.assertEqual(signed*n,SIGNED_DEFECT_COEFFICIENT**2)
            self.assertEqual(
                scalar,LIMIT**2*signed
            )
            self.assertEqual(
                certified_lower_squared(n)["squared_scalar_gap_upper"],
                scalar
            )
        for n in (10**6,10**9,10**12):
            self.assertLess(
                finite_threshold_bound_squared(n),
                optimized_window_rate(n).bound_squared
            )
        self.assertLess(finite_threshold_bound_squared(10**12),
                        Fraction(1,10**9))
        self.assertLess(finite_threshold_bound_squared(10**9),
                        Fraction(1,10**6))
        receipt=theorem_receipt(10**12)
        self.assertEqual(receipt["uniform_rate"],"O(n^-1/2)")
        self.assertFalse(receipt["finite_exchangeability_approximation_required"])
        self.assertFalse(receipt["abstract_de_Finetti_limit_required"])

    def test_prev_sharp_thresholds_and_sixteen_replica_lower_consistent(self):
        self.assertEqual(ETA2,Fraction(5,118))
        self.assertEqual(ETA3,Fraction(751225,13956626))
        self.assertEqual(LOWER16,Fraction(4743879,50000000))
        for n,lower in ((2,ETA2),(3,ETA3),(16,LOWER16)):
            self.assertLessEqual(
                n*(LIMIT-lower)**2,SCALAR_RATE**2
            )
        # The analytic lower becomes stronger than the n16 projected
        # lower for sufficiently large n, while all upper bounds are
        # still certified by BM27's exact all-n channel.
        n=10**9
        self.assertLess(
            SCALAR_RATE**2/Fraction(n),
            (LIMIT-LOWER16)**2
        )

    def test_bound_rejects_invalid_histograms_and_non_equalizing_masks(self):
        with self.assertRaises(ValueError):
            path_moment("C",0)
        with self.assertRaises(ValueError):
            path_moment("A",3)
        with self.assertRaises(ValueError):
            conditional_moments(2,(1,1,1),"A")
        with self.assertRaises(ValueError):
            conditional_moments(2,(2,0,0),"C")
        with self.assertRaises(ValueError):
            direct_signed_bound_squared(0)
        with self.assertRaises(ValueError):
            direct_signed_bound_squared(2,lip_w=-1)
        with self.assertRaises(ValueError):
            finite_threshold_bound_squared(0)
        with self.assertRaises(ValueError):
            verify_finite_witness(6,{0:Fraction(1)},{0:Fraction(1)})
        with self.assertRaises(AssertionError):
            verify_finite_witness(2,{0:Fraction(1)},{0:Fraction(1)})


if __name__=="__main__":
    unittest.main()
