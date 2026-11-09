"""BM-09 cactus versus shared-edge theta exact risk comparison."""
from fractions import Fraction
import unittest

from cactus_erasure_control import (
    C4_CACTUS_EDGES, C4_CACTUS_SHIFT, cactus_counts,
    cactus_convolve, independent_cycle_masks, verify_cactus_q4,
)
from theta_shared_cycle_erasure import (
    verify_q4_primal, verify_q4_lower_lemma, verify_q8_primal, verify_q8_dual,
)


class CactusThetaComparisonTests(unittest.TestCase):
    def test_two_edge_disjoint_fourcycles_erase_at_the_single_cycle_cap(self):
        report=verify_cactus_q4()
        self.assertEqual(report["erasure_cap"],Fraction(1,8))
        self.assertEqual(report["cycle_rank"],2)
        self.assertTrue(report["full_pattern_equality"])
        self.assertEqual((report["vertices"],report["edges"]),(8,9))

    def test_every_mask_marginal_exact_and_no_bridge_error(self):
        mask=independent_cycle_masks()
        self.assertEqual(sum(mask.values()),64)
        self.assertEqual(len(mask),25)
        for i in range(9):
            marginal=sum(w for m,w in mask.items() if m&(1<<i))
            self.assertEqual(marginal,8 if i<8 else 0)

    def test_independent_label_oracle_still_sees_distinct_worlds_without_mask(self):
        flat=cactus_counts((0,)*9)
        frustrated=cactus_counts(C4_CACTUS_SHIFT)
        self.assertNotEqual(flat,frustrated)
        self.assertEqual(sum(flat),4**8)
        self.assertEqual(sum(frustrated),4**8)
        masks=independent_cycle_masks()
        self.assertEqual(cactus_convolve(flat,masks),
                         cactus_convolve(frustrated,masks))

    def test_theta_same_cycle_rank_requires_larger_mask_budget(self):
        self.assertTrue(verify_q4_primal() and verify_q4_lower_lemma())
        self.assertGreater(Fraction(1,6),Fraction(1,8))
        self.assertTrue(verify_q8_primal() and verify_q8_dual())
        self.assertGreater(Fraction(29,630),Fraction(1,44))

    def test_bad_cactus_input_rejected(self):
        with self.assertRaises(ValueError):
            cactus_counts((0,)*8)
        with self.assertRaises(ValueError):
            cactus_counts((0,)*8+(4,))
        with self.assertRaises(ValueError):
            cactus_convolve((0,)*32,independent_cycle_masks())


if __name__=="__main__":
    unittest.main()
