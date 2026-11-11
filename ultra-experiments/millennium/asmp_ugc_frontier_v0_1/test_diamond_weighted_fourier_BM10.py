"""BM-10: independent exact-primal, exact-dual and zero-only-gap tests."""
from fractions import Fraction
from itertools import product
import unittest

from diamond_weighted_fourier_BM10 import (
    ALPHABET, N_EDGES, MASK_COUNT, LABEL_COUNT, EDGES, SHIFT,
    PRIMAL_MASK_COUNTS, PRIMAL_DENOMINATOR,
    DUAL_NORMALIZATION, DUAL_MARGINAL, DUAL_WALSH,
    ZERO_ONLY_MASK_COUNTS, ZERO_DENOMINATOR,
    clean_counts, counts_for, full_dual_slacks, output_counts,
    per_bit_counts, receipt, verify_full_primal, verify_full_dual,
    verify_zero_only_surrogate, walsh, zero_only_constraints,
)
from finite_seed import Game, satisfaction_law
from sharp_erasure_optimality import critical_erasure_cap
from theta_shared_cycle_erasure import verify_q4_primal, verify_q4_lower_lemma


class DiamondWeightedFourierTests(unittest.TestCase):
    def test_clean_laws_against_independent_finite_seed_oracle(self):
        for shifts in ((0,)*5,SHIFT,(1,2,3,0,1)):
            game=Game(4,2,tuple(
                (u,v,shift) for (u,v),shift in zip(EDGES,shifts)))
            law=satisfaction_law(game,tuple(range(N_EDGES)))
            expected=tuple(
                int(law.get(tuple(bool(m&(1<<j))
                                  for j in range(N_EDGES)),Fraction(0))
                    *LABEL_COUNT)
                for m in range(MASK_COUNT)
            )
            self.assertEqual(counts_for(shifts),expected)

    def test_common_primal_exact_full_law_equalization(self):
        self.assertTrue(verify_full_primal())
        self.assertEqual(sum(PRIMAL_MASK_COUNTS.values()),PRIMAL_DENOMINATOR)
        self.assertEqual(per_bit_counts(PRIMAL_MASK_COUNTS),(4,)*5)
        p0,p1=clean_counts()
        self.assertNotEqual(p0,p1)
        self.assertEqual(output_counts(p0,PRIMAL_MASK_COUNTS),
                         output_counts(p1,PRIMAL_MASK_COUNTS))
        self.assertEqual(Fraction(4,PRIMAL_DENOMINATOR),Fraction(1,5))

    def test_sparse_dual_bound_checks_both_worlds_and_all_mask_atoms(self):
        self.assertTrue(verify_full_dual())
        self.assertEqual(sum(DUAL_NORMALIZATION),Fraction(1,5))
        self.assertEqual(len(DUAL_WALSH),17)
        self.assertEqual(-sum(
            (x for row in DUAL_MARGINAL for x in row.values()),Fraction(0)
        ),1)
        slacks=full_dual_slacks()
        self.assertEqual(tuple(len(row) for row in slacks),(32,32))
        self.assertTrue(all(v<=0 for row in slacks for v in row))
        self.assertTrue(any(v<0 for row in slacks for v in row))
        self.assertTrue(any(v==0 for row in slacks for v in row))

    def test_zero_only_Fourier_surrogate_provably_underestimates_cost(self):
        self.assertTrue(verify_zero_only_surrogate())
        self.assertEqual(zero_only_constraints(),(30,31))
        p0,p1=clean_counts()
        self.assertTrue(walsh(p0,30)!=0 and walsh(p1,30)==0)
        self.assertTrue(walsh(p0,31)!=0 and walsh(p1,31)==0)
        self.assertEqual(sum(ZERO_ONLY_MASK_COUNTS.values()),ZERO_DENOMINATOR)
        self.assertEqual(per_bit_counts(ZERO_ONLY_MASK_COUNTS),(2,)*5)
        self.assertNotEqual(output_counts(p0,ZERO_ONLY_MASK_COUNTS),
                            output_counts(p1,ZERO_ONLY_MASK_COUNTS))
        self.assertEqual(Fraction(1,5)/Fraction(1,8),Fraction(8,5))

    def test_interaction_vs_isolated_triangle_and_K23(self):
        isolated=critical_erasure_cap(4,3)
        self.assertEqual(isolated,Fraction(1,6))
        self.assertEqual(Fraction(1,5)/isolated,Fraction(6,5))
        self.assertTrue(verify_q4_lower_lemma() and verify_q4_primal())
        self.assertEqual(Fraction(1,6)/critical_erasure_cap(4,4),
                         Fraction(4,3))
        self.assertGreater(Fraction(4,3),Fraction(6,5))

    def test_changing_mask_weights_detected_by_output_comparison(self):
        p0,p1=clean_counts()
        changed=dict(PRIMAL_MASK_COUNTS)
        changed[0]-=1
        changed[1]+=1
        self.assertEqual(sum(changed.values()),PRIMAL_DENOMINATOR)
        self.assertNotEqual(output_counts(p0,changed),
                            output_counts(p1,changed))

    def test_receipt_and_invalid_inputs(self):
        record=receipt()
        self.assertEqual(record["full_erasure_optimum"],"1/5")
        self.assertTrue(record["full_primal"] and record["full_dual"])
        self.assertTrue(record["zero_only_certificate"])
        self.assertEqual(record["dual_mask_constraints_checked"],64)
        self.assertFalse(record["numeric_optimizer_required"])
        with self.assertRaises(ValueError):
            counts_for((0,)*4)
        with self.assertRaises(ValueError):
            counts_for((0,0,0,0,4))
        with self.assertRaises(ValueError):
            output_counts((0,)*3,PRIMAL_MASK_COUNTS)
        with self.assertRaises(ValueError):
            walsh((0,)*3,1)


if __name__=="__main__":
    unittest.main()
