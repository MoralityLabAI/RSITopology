"""BM-39 exact full-output, finite formula, limiting calibration controls."""
import unittest
from fractions import Fraction

from exact_graded_visibility_BM39 import (
    PAIR_A, PAIR_B, UPPER_CAP, clean_total_variation,
    graded_total_variation, graded_mask_cap,
    attacker_family_tv_at_budget, asymptotic_total_variation,
    ideal_equal_prior_bayes_risk,population_tpr_upper,
    verify_full_output,theorem_receipt,
)


class BM39ExactGradedVisibilityTests(unittest.TestCase):
    def test_clean_all_n_formula_at_previous_exact_n2(self):
        self.assertEqual(clean_total_variation(1),Fraction(1,64))
        self.assertEqual(clean_total_variation(2),Fraction(7,256))
        self.assertEqual(clean_total_variation(3),Fraction(37,1024))
        self.assertEqual(graded_total_variation(2,Fraction(1,2)),
                         Fraction(7,512))
        self.assertEqual(graded_total_variation(2,1),Fraction(7,256))

    def test_all_full_output_patterns_independent_census(self):
        for n in (1,2,3):
            for lam in (Fraction(0),Fraction(1,4),Fraction(1,2),
                        Fraction(3,4),Fraction(1)):
                r=verify_full_output(n,lam)
                self.assertEqual(r.full_output_tv,r.predicted_full_output_tv)
                self.assertEqual(r.per_bit_mask_cap,(1-lam)*UPPER_CAP)
                self.assertEqual(r.complete_probabilities_checked,1<<(2*n+2))

    def test_budget_curve_is_attacker_achievable_not_minimax_claim(self):
        for eta in (Fraction(0),Fraction(5,104),UPPER_CAP):
            lam=1-eta/UPPER_CAP
            self.assertEqual(attacker_family_tv_at_budget(15,eta),
                             graded_total_variation(15,lam))
        with self.assertRaises(ValueError):
            attacker_family_tv_at_budget(100,UPPER_CAP+Fraction(1,1000))

    def test_99pct_saturation_by_n17_and_limits(self):
        self.assertLess(clean_total_variation(16),Fraction(99,100)*Fraction(1,16))
        self.assertGreater(clean_total_variation(17),Fraction(99,100)*Fraction(1,16))
        for n in (1,2,17,25,4096):
            self.assertLess(clean_total_variation(n),Fraction(1,16))
        self.assertEqual(asymptotic_total_variation(Fraction(1,2)),
                         Fraction(1,32))

    def test_exact_bayes_risk_and_fixed_fpr_population_upper(self):
        n,lam=4096,Fraction(1,2)
        t=graded_total_variation(n,lam)
        self.assertEqual(ideal_equal_prior_bayes_risk(n,lam),(1-t)/2)
        self.assertEqual(population_tpr_upper(n,lam,Fraction(1,20)),
                         Fraction(1,20)+t)
        self.assertLess(population_tpr_upper(n,lam,Fraction(1,20)),
                        Fraction(13,160))
        self.assertGreater(population_tpr_upper(n,lam,Fraction(1,20)),
                           Fraction(8,100))

    def test_errors_and_theorem_receipt(self):
        for n,lam in ((0,1),(1,-1),(1,2)):
            with self.assertRaises(ValueError):
                graded_total_variation(n,lam)
        with self.assertRaises(ValueError):
            population_tpr_upper(1,1,Fraction(11,10))
        with self.assertRaises(ValueError):
            verify_full_output(4,Fraction(1,2))
        r=theorem_receipt(4096,Fraction(1,2))
        self.assertEqual(r["asymptotic_TV"],"1/32")
        self.assertEqual(r["exact_formula"],"lambda*(1-(3/4)^n)/16")
        self.assertTrue(r["family_specific"])
        self.assertFalse(r["unrestricted_minimax_claim"])


if __name__=="__main__":
    unittest.main()
