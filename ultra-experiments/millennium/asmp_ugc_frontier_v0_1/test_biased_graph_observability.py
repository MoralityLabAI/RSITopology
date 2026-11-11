"""ASMP-14 finite Boolean-monitor information quotient and cover-cost blindness.

All census equalities use exact rational distributions. Exhaustive label
enumeration is independent of subset/forest Möbius inversion in the oracle.
"""
from fractions import Fraction
from itertools import product
import unittest

from biased_graph_observability import (
    balanced_subset_signature, cactus_pair, exact_boolean_moments,
    full_boolean_law, holonomy_image_size, maximum_balanced_subset,
)
from finite_seed import Game, gauge_witness, optimum, satisfaction_law
from frontier_bounds import tv_distance


C4 = ((0,2),(0,3),(1,2),(1,3))


def cycle_game(bits, shifts):
    return Game(4, bits, tuple((u,v,s) for (u,v),s in zip(C4,shifts)))


class BiasedGraphObservabilityTests(unittest.TestCase):
    def test_all_256_q4_cycles_mobius_vs_direct_oracle(self):
        classes = {}
        for shifts in product(range(4), repeat=4):
            g = cycle_game(2,shifts)
            direct = satisfaction_law(g, tuple(range(4)))
            inverted = full_boolean_law(g)
            self.assertEqual(inverted,direct)
            moment = exact_boolean_moments(g)
            self.assertEqual(moment[0],1)
            self.assertEqual(moment[-1], Fraction(1, 4**3) if
                             shifts[0]^shifts[1]^shifts[2]^shifts[3] == 0 else 0)
            signature=balanced_subset_signature(g)
            key=tuple(moments > 0 for moments in moment)
            self.assertEqual(signature,key)
            if key not in classes:
                classes[key]=inverted
            self.assertEqual(inverted,classes[key])
        # Only the flat and nonflat biased-cycle profiles are identifiable.
        self.assertEqual(len(classes),2)

    def test_two_triangle_cactus_equal_full_law_different_flat_cover_degree(self):
        a,b=cactus_pair(2,2)
        self.assertEqual(a.vertices,6)
        self.assertEqual(len(a.edges),7)
        self.assertEqual(a.edges[:3],b.edges[:3])
        self.assertIsNone(gauge_witness(a,b))
        self.assertEqual(holonomy_image_size(a),2)
        self.assertEqual(holonomy_image_size(b),4)
        self.assertEqual(balanced_subset_signature(a),
                         balanced_subset_signature(b))
        law_a=full_boolean_law(a)
        law_b=full_boolean_law(b)
        self.assertEqual(law_a,law_b)
        self.assertEqual(tv_distance(law_a,law_b),0)
        self.assertEqual(law_a,satisfaction_law(a,tuple(range(7))))
        self.assertEqual(law_b,satisfaction_law(b,tuple(range(7))))
        self.assertEqual(maximum_balanced_subset(a),5)
        self.assertEqual(maximum_balanced_subset(b),5)
        self.assertEqual(optimum(a),Fraction(5,7))
        self.assertEqual(optimum(b),Fraction(5,7))

    def test_holonomy_cover_gap_exponential_across_cactus_family(self):
        for t in range(1,5):
            a,b=cactus_pair(t,t)
            self.assertEqual(a.vertices,3*t)
            self.assertEqual(len(a.edges),4*t-1)
            self.assertEqual(holonomy_image_size(a),2)
            self.assertEqual(holonomy_image_size(b),1<<t)
            # The entire Boolean-law profile is identical although an
            # optimal connected holonomy cover requires 2 versus 2**t sheets.
            self.assertEqual(balanced_subset_signature(a),
                             balanced_subset_signature(b))
            if t<=3:
                self.assertEqual(full_boolean_law(a),full_boolean_law(b))
            self.assertEqual(maximum_balanced_subset(a),len(a.edges)-t)
            self.assertEqual(maximum_balanced_subset(b),len(b.edges)-t)

    def test_binary_full_edge_bits_exactly_identify_gauge_coset(self):
        all_games=[cycle_game(1,shifts) for shifts in product((0,1),repeat=4)]
        for a in all_games:
            law_a=full_boolean_law(a)
            for b in all_games:
                gauge_equivalent=gauge_witness(a,b) is not None
                law_b=full_boolean_law(b)
                self.assertEqual(law_a == law_b,gauge_equivalent)
                if not gauge_equivalent:
                    self.assertEqual(tv_distance(law_a,law_b),1)

    def test_q4_different_nonzero_cycle_holonomy_same_full_law(self):
        examples = [cycle_game(2,(0,0,0,i)) for i in (1,2,3)]
        laws = [full_boolean_law(g) for g in examples]
        self.assertTrue(all(law == laws[0] for law in laws))
        self.assertTrue(all(gauge_witness(examples[0],g) is None
                            for g in examples[1:]))
        self.assertTrue(all(maximum_balanced_subset(g)==3 for g in examples))

    def test_empty_graph_loops_and_parallel_edges(self):
        games = (
            Game(3,2,()),
            Game(2,1,((0,0,1),)),
            Game(2,2,((0,1,1),(0,1,2))),
            Game(3,2,((0,1,0),(1,2,0),(2,0,1))),
        )
        for g in games:
            self.assertEqual(full_boolean_law(g),
                             satisfaction_law(g,tuple(range(len(g.edges)))))
            self.assertEqual(Fraction(maximum_balanced_subset(g),len(g.edges))
                             if g.edges else 1,optimum(g))

    def test_invalid_cactus_parameters(self):
        with self.assertRaises(ValueError):
            cactus_pair(0,2)
        with self.assertRaises(ValueError):
            cactus_pair(3,2)


if __name__=="__main__":
    unittest.main()
