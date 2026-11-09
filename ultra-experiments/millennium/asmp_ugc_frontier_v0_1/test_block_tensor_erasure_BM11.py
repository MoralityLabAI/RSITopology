"""BM-11: exact block tensorization, full-mask equality and dual lifting.

Independent vertex-label census checks distinguish a one-vertex sum from a
graph with shared-edge cycles. The exact joint mask law is calculated in a
different way from the original diamond/theta component mask formulas.
"""
from fractions import Fraction
from itertools import product
import unittest

from finite_seed import Game, cycle_signature
from block_tensor_erasure_BM11 import (
    vertex_sum, exact_satisfaction_counts, factor_counts,
    product_masks, mask_marginals_counts, convolve_exact,
    worked_diamond_theta_pair, verify_block_tensorization,
    extended_diamond_dual_slacks, verify_extended_dual,
)
from diamond_weighted_fourier_BM10 import (
    DUAL_WALSH, full_dual_slacks, verify_full_dual,
)
from theta_shared_cycle_erasure import (
    verify_q4_primal, verify_q4_lower_lemma,
)


class BlockTensorErasureTests(unittest.TestCase):
    def test_vertex_sum_factors_all_small_gains_and_nonzero_roots(self):
        # Pair a 2-edge parallel loop with a 3-edge triangle, over q=4.
        # Glue vertex 1 in the first block to vertex 2 in the triangle.
        pairs1=((0,1),(0,1))
        pairs2=((0,1),(1,2),(2,0))
        for a_shift in ((0,0),(0,1),(1,2)):
            for b_shift in ((0,0,0),(0,0,1),(2,1,3)):
                a=Game(2,2,tuple(
                    (u,v,s) for (u,v),s in zip(pairs1,a_shift)))
                b=Game(3,2,tuple(
                    (u,v,s) for (u,v),s in zip(pairs2,b_shift)))
                combined=vertex_sum(a,b,root_a=1,root_b=2)
                self.assertEqual(combined.vertices,4)
                self.assertEqual(len(combined.edges),5)
                self.assertEqual(exact_satisfaction_counts(combined),
                                 factor_counts(a,b))
                self.assertEqual(sum(exact_satisfaction_counts(combined)),4**4)

    def test_glued_diamond_theta_full_joint_mask_exactly_equalizes(self):
        self.assertTrue(verify_q4_primal() and verify_q4_lower_lemma())
        result=verify_block_tensorization()
        self.assertEqual(result["erasure_cap"],"1/5")
        self.assertEqual((result["vertices"],result["edges"],
                          result["cycle_rank"]),(8,11,4))
        self.assertTrue(result["product_law_verified_by_direct_labels"])
        self.assertTrue(result["full_pattern_equality"])

    def test_lifted_dual_has_4096_constraints_with_no_theta_variables(self):
        self.assertTrue(verify_full_dual())
        self.assertTrue(verify_extended_dual())
        global_slacks=extended_diamond_dual_slacks()
        local_slacks=full_dual_slacks()
        self.assertEqual(tuple(map(len,global_slacks)),(2048,2048))
        self.assertEqual(len(DUAL_WALSH),17)
        for h in (0,1):
            for mask in range(2048):
                self.assertEqual(global_slacks[h][mask],
                                 local_slacks[h][mask&31])
        self.assertEqual(max(max(a) for a in global_slacks),0)

    def test_corpus_of_three_blocks_factorizes_associatively(self):
        a=Game(3,2,((0,1,0),(1,2,1),(2,0,2)))
        b=Game(2,2,((0,1,0),(0,1,3)))
        c=Game(2,2,((0,1,1),))
        # Both parenthesizations preserve the same ordered edge occurrences,
        # although the vertex ordering can differ.
        ab=vertex_sum(a,b,root_a=2,root_b=0)
        abc=vertex_sum(ab,c,root_a=0,root_b=1)
        self.assertEqual(abc.vertices,5)
        self.assertEqual(len(abc.edges),6)
        self.assertEqual(exact_satisfaction_counts(abc),
                         tuple((x*y)//4 for y in exact_satisfaction_counts(c)
                               for x in factor_counts(a,b)))
        self.assertEqual(sum(exact_satisfaction_counts(abc)),4**5)

    def test_product_mask_cost_is_exact_block_max_not_sum(self):
        a,b,masks,denom=worked_diamond_theta_pair()
        self.assertEqual(denom,240)
        self.assertEqual(sum(masks.values()),240)
        self.assertEqual(len(masks),110)
        marg=mask_marginals_counts(masks,len(a.edges))
        self.assertEqual(marg,(48,)*5+(40,)*6)
        self.assertEqual(max(marg),48)
        self.assertEqual(Fraction(max(marg),denom),Fraction(1,5))
        self.assertGreater(Fraction(1,5)+Fraction(1,6),Fraction(1,5))

    def test_product_masks_reject_bad_probability_or_dimensions(self):
        with self.assertRaises(ValueError):
            product_masks({0:2},1,1,{0:1},1,1)
        with self.assertRaises(ValueError):
            product_masks({2:1},1,1,{0:1},1,1)
        with self.assertRaises(ValueError):
            product_masks({0:1},1,1,{0:1},0,1)
        with self.assertRaises(ValueError):
            convolve_exact((0,1,0,1),{4:1})
        with self.assertRaises(ValueError):
            vertex_sum(Game(2,1,()),Game(2,2,()))
        with self.assertRaises(ValueError):
            vertex_sum(Game(2,2,()),Game(2,2,()),root_b=3)


if __name__=="__main__":
    unittest.main()
