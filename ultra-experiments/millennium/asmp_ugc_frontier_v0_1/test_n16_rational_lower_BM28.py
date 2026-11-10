"""BM-28: independent exact q8 n16 rational-dual regression checks.

The 459 dual coefficients are preserved losslessly under a SHA256-checked
frozen archive. The verifier rebuilds the complete Walsh-orbit matrix from
integer polynomials and checks 918 exact integer dual inequalities, with
no scipy/numpy/float dependencies.
"""
from fractions import Fraction
import unittest

from n16_rational_lower_BM28 import (
    N,M,SCALE,EXACT_LOWER,UPPER,W_SCALE,
    EXPECTED_SHA256,NORM_NUMERATORS,MARGINAL_NUMERATORS,
    ordinary_histograms,frozen_dual_numerators,
    ordinary_kernel_numerators,exact_clean_walsh,
    scaled_clean_walsh,verify_integer_dual,exact_limit_bracket,
)
from repeated_gain_erasure_BM24 import gain_family
from repeated_theta_orbits_BM24 import type_krawtchouk_kernel
from replication_uniform_upper_BM27 import theorem_upper
from state_aware_three_replica_BM26 import EXACT_CAP as N3_LOWER
from state_aware_replication_BM25 import EXACT_ETA as N2_LOWER


class N16RationalDualTests(unittest.TestCase):
    def test_losslessly_frozen_coefficient_table_and_exact_lower(self):
        y=frozen_dual_numerators()
        self.assertEqual(len(y),459)
        self.assertEqual(sum(bool(v) for v in y),441)
        self.assertEqual(y[0],0)
        self.assertEqual(
            EXPECTED_SHA256,
            "47bd694403aa4ce43d1e8e8b501b7ca05d2b2f1dbe97dd1e0152cbdc1835ec16"
        )
        self.assertEqual(sum(MARGINAL_NUMERATORS),-SCALE)
        self.assertTrue(all(v<=0 for v in MARGINAL_NUMERATORS))
        self.assertEqual(
            Fraction(sum(NORM_NUMERATORS),SCALE),
            Fraction(4743879,50000000)
        )

    def test_independent_multivariate_integer_kernel_matches_BM24(self):
        for n in (2,3,4,6):
            hists,coeffs,den=ordinary_kernel_numerators(n)
            self.assertEqual(len(hists),(n+1)*(n+2)//2)
            for i,s in enumerate(hists):
                for j,t in enumerate(hists):
                    self.assertEqual(
                        Fraction(coeffs[i][j],den[j]),
                        type_krawtchouk_kernel(2,s,t)
                    )
            self.assertEqual(coeffs[0],den)

    def test_q8_clean_fourier_moments_match_separate_BM24_oracle(self):
        for n in (2,3,4,8):
            model=gain_family(n,2,q=8)
            for ordinary in ordinary_histograms(n):
                for special_degree in (0,1,2):
                    exc=tuple(int(k==special_degree) for k in range(3))
                    sig=(ordinary,exc)
                    for h in (0,1):
                        a=exact_clean_walsh(n,ordinary,special_degree,h)
                        self.assertEqual(
                            a,model.clean_walsh_signature(h,sig)
                        )
                        self.assertEqual(
                            scaled_clean_walsh(n,ordinary,special_degree,h),
                            a*(1<<(3*n+6))
                        )

    def test_all_918_full_equivalent_mask_orbit_inequalities_exact(self):
        r=verify_integer_dual()
        self.assertEqual(r["certified_lower"],EXACT_LOWER)
        self.assertEqual(r["certified_upper"],UPPER)
        self.assertEqual(r["dual_inequalities_checked"],918)
        self.assertEqual(r["orbit_classes_per_hypothesis"],459)
        self.assertEqual(r["active_Fourier_orbit_multipliers"],441)
        self.assertEqual(r["max_dual_slack"],0)
        self.assertFalse(r["external_optimizer_needed"])
        self.assertEqual(r["proved_limit_gap"],
                         Fraction(829573,650000000))

    def test_limit_bracket_is_sharper_than_prior_BM26_and_BM27(self):
        lo,hi=exact_limit_bracket()
        self.assertEqual(lo,Fraction(4743879,50000000))
        self.assertEqual(hi,Fraction(5,52))
        self.assertGreater(lo,N3_LOWER)
        self.assertGreater(lo,N2_LOWER)
        self.assertEqual(theorem_upper(250),hi)
        self.assertEqual(theorem_upper(16),hi)
        self.assertLess(hi-lo,Fraction(13,10000))
        self.assertEqual((N,M),(16,459))

    def test_bad_indices_rejected(self):
        with self.assertRaises(ValueError):
            ordinary_histograms(0)
        with self.assertRaises(ValueError):
            exact_clean_walsh(16,(16,0,0),3,0)
        with self.assertRaises(ValueError):
            exact_clean_walsh(16,(16,0,0),2,2)
        with self.assertRaises(ValueError):
            exact_clean_walsh(16,(15,0,0),1,0)


if __name__=="__main__":
    unittest.main()
