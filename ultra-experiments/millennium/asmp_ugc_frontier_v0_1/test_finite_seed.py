"""Exact finite seed tests for the provisional ASMP-13..16 research draft."""
from fractions import Fraction
from itertools import combinations, product
from math import log
import unittest

from finite_seed import (
    Game, cycle_signature, quotient_counts, gauge_witness, optimum,
    satisfaction_law, regular_flat_cover, descent_error,
    descent_upper_bound, maxcut,
)

C4 = ((0, 2), (0, 3), (1, 2), (1, 3))
K23 = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))


def game(n, bits, pairs, shifts):
    return Game(n, bits, tuple(
        (u, v, c) for (u, v), c in zip(pairs, shifts)))


class FiniteASMPSeeds(unittest.TestCase):
    def test_C4_complete_F2_squared_gauge_class_census(self):
        flat = game(4, 2, C4, (0, 0, 0, 0))
        self.assertEqual(quotient_counts(flat), (4, 64))
        histogram = {}
        for shifts in product(range(4), repeat=4):
            g = game(4, 2, C4, shifts)
            signature = tuple(h for _, h in cycle_signature(g))
            histogram[signature] = histogram.get(signature, 0) + 1
            p, tree, _ = __import__("finite_seed").forest(g)
            normal = game(4, 2, C4, tuple(p[u] ^ s ^ p[v] for u, v, s in g.edges))
            self.assertIsNotNone(gauge_witness(g, normal))
        self.assertEqual(len(histogram), 4)
        self.assertEqual(sorted(histogram.values()), [64]*4)

    def test_K23_binary_two_independent_cycle_access(self):
        flat = game(5, 1, K23, (0,)*6)
        self.assertEqual(quotient_counts(flat), (4, 16))
        chords = tuple(i for i, _ in cycle_signature(flat))
        self.assertEqual(len(chords), 2)
        for ignored in chords:
            bad = game(5, 1, K23, tuple(
                1 if i == ignored else 0 for i in range(6)))
            for observed in ((), (next(i for i in chords if i != ignored),)):
                self.assertEqual(
                    tuple(dict(cycle_signature(flat))[i] for i in observed),
                    tuple(dict(cycle_signature(bad))[i] for i in observed))
            self.assertIsNone(gauge_witness(flat, bad))
            self.assertLess(optimum(bad), 1)

    def test_every_proper_C4_edge_observation_is_indistinguishable(self):
        for bits in (1, 2):
            flat = game(4, bits, C4, (0,0,0,0))
            bad = game(4, bits, C4, (0,0,0,1))
            for r in range(4):
                for queried in combinations(range(4), r):
                    self.assertEqual(
                        satisfaction_law(flat, queried),
                        satisfaction_law(bad, queried))
            self.assertNotEqual(satisfaction_law(flat, tuple(range(4))),
                                satisfaction_law(bad, tuple(range(4))))
            self.assertEqual(optimum(flat) - optimum(bad), Fraction(1,4))

    def test_full_binary_cycle_disjoint_parity_support(self):
        flat = game(4, 1, C4, (0,0,0,0))
        bad = game(4, 1, C4, (0,0,0,1))
        self.assertTrue(set(satisfaction_law(flat,(0,1,2,3))).isdisjoint(
                        set(satisfaction_law(bad,(0,1,2,3)))))

    def test_binary_all_one_game_is_MAXCUT_on_K4_subgraphs(self):
        pairs = tuple(combinations(range(4),2))
        for flags in product((False, True), repeat=len(pairs)):
            retained = tuple(pair for flag,pair in zip(flags,pairs) if flag)
            g = game(4,1,retained,(1,)*len(retained))
            expect = Fraction(maxcut(4,retained),len(retained)) if retained else Fraction(1)
            self.assertEqual(optimum(g),expect)

    def test_kernel_cover_perfect_but_base_frustrated(self):
        base = game(4,1,C4,(0,0,0,1))
        self.assertEqual(optimum(base),Fraction(3,4))
        lifted, labels, r = regular_flat_cover(base)
        self.assertEqual(r,2)
        self.assertEqual(optimum(lifted),1)
        self.assertTrue(all(labels[u]^labels[v] == s for u,v,s in lifted.edges))
        self.assertEqual(descent_error(labels,4,r),Fraction(1,2))
        self.assertLessEqual(1-optimum(base),descent_upper_bound(base,lifted,labels,r))

    def test_cover_rank_two_and_perturbed_lift_certificate(self):
        base = game(5,2,K23,(0,0,0,1,0,2))
        lifted, labels, r = regular_flat_cover(base)
        self.assertEqual(r,4)
        self.assertTrue(all(labels[u]^labels[v]==s for u,v,s in lifted.edges))
        for flips in ((), (0,), (0,3,8,13)):
            altered = tuple(v ^ int(i in flips) for i,v in enumerate(labels))
            self.assertLessEqual(1-optimum(base),
                                 descent_upper_bound(base,lifted,altered,r))

    def test_positive_random_signing_existence_bound_at_degree_twelve(self):
        # Union-bound control: 2^n exp(-d*n/16) < 1 for all n>0 if d>=12.
        for n in (20, 100, 1000):
            self.assertLess(n*log(2)-12*n/16,0)

    def test_reject_invalid_query_or_graph(self):
        g=game(4,1,C4,(0,0,0,1))
        with self.assertRaises(ValueError):
            satisfaction_law(g,(1,1))
        with self.assertRaises(ValueError):
            satisfaction_law(g,(9,))
        with self.assertRaises(ValueError):
            gauge_witness(g,game(4,1,tuple(reversed(C4)),(0,0,0,1)))


if __name__ == "__main__":
    unittest.main()
