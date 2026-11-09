"""ASMP-15 composable descent inequality and malformed-cover controls."""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from finite_seed import Game, descent_error, descent_upper_bound, regular_flat_cover
from tower_descent import fiberwise_mode, pullback_hamming, two_step_descent


class DescentTowerTests(unittest.TestCase):
    def test_all_four_bit_two_by_two_towers(self):
        for labels in product((0,1), repeat=4):
            r = two_step_descent(labels, n_base=1, sheets_first=2, sheets_second=2)
            self.assertLessEqual(r["eta_composite"], r["bound"])
            self.assertEqual(r["eta_composite"], descent_error(labels,1,4))
            self.assertEqual(r["eta_second"], pullback_hamming(
                labels, r["middle_labels"], 2))
            self.assertEqual(r["eta_first"], pullback_hamming(
                r["middle_labels"], r["base_labels"], 2))

    def test_all_four_label_two_by_two_towers(self):
        for labels in product(range(4), repeat=4):
            r = two_step_descent(labels,1,2,2)
            self.assertLessEqual(r["eta_composite"], r["bound"])
            self.assertEqual(r["eta_second"], descent_error(labels,2,2))
            self.assertEqual(r["eta_first"], descent_error(r["middle_labels"],1,2))

    def test_random_two_base_vertex_towers_and_tie_breaking(self):
        rng = Random(1709)
        for _ in range(128):
            labels = tuple(rng.randrange(4) for _ in range(2*3*2))
            r=two_step_descent(labels,2,3,2)
            self.assertLessEqual(r["eta_composite"], r["bound"])
        self.assertEqual(fiberwise_mode((3,1,2,2),2,2),(1,2))

    def test_descent_safety_bound_for_regular_flat_cover(self):
        # Frustration can vanish upstairs while the descent defect remains.
        original = Game(4,1,((0,2,0),(0,3,0),(1,2,0),(1,3,1)))
        lifted, labels, degree=regular_flat_cover(original)
        self.assertEqual(degree,2)
        self.assertEqual(descent_error(labels,4,degree), Fraction(1,2))
        self.assertGreaterEqual(descent_upper_bound(original,lifted,labels,degree),
                                Fraction(1,4))

    def test_malformed_target_fiber_rejected(self):
        original = Game(4,1,((0,2,0),(0,3,0),(1,2,0),(1,3,1)))
        lifted, labels, degree=regular_flat_cover(original)
        bad_edges=list(lifted.edges)
        # Two lifts of one base edge now share the same target sheet.
        u0, v0, c0 = bad_edges[0]
        u1, v1, c1 = bad_edges[1]
        bad_edges[1]=(u1,v0,c1)
        malformed=Game(lifted.vertices,lifted.bits,tuple(bad_edges))
        with self.assertRaisesRegex(ValueError, "target fibers"):
            descent_upper_bound(original,malformed,labels,degree)

    def test_invalid_tower_inputs(self):
        with self.assertRaises(ValueError):
            two_step_descent((0,1,0),1,2,2)
        with self.assertRaises(ValueError):
            pullback_hamming((0,1,0),(0,),2)
        with self.assertRaises(ValueError):
            fiberwise_mode((0,),1,0)


if __name__ == "__main__":
    unittest.main()
