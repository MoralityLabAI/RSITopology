"""ASMP-13/14 sharp finite visibility and structural-decoding tests."""
from fractions import Fraction
from itertools import combinations, product
from math import comb
import unittest

from finite_seed import Game, optimum, satisfaction_law, cycle_signature
from frontier_bounds import (
    apply_bsc, cycle_tv_formula, exact_forest_chord_decoder,
    full_cycle_law, full_cycle_pattern_counts, minimum_iid_replicates_by_coupling,
    noisy_binary_cycle_tv, tv_distance,
)


def game(n, bits, pairs, shifts):
    return Game(n, bits, tuple((u, v, s)
                               for (u, v), s in zip(pairs, shifts)))


def cycle(n, bits, frustrated):
    return game(n, bits, tuple((i, (i+1)%n) for i in range(n)),
                (1 if frustrated else 0,) + (0,)*(n-1))


class ExactFrontierBoundsTests(unittest.TestCase):
    def test_closed_cycle_pattern_distribution_matches_independent_label_enumeration(self):
        for bits in (1, 2, 3):
            for length in (1, 2, 3, 4):
                for frustrated in (False, True):
                    g = cycle(length, bits, frustrated)
                    predicted = full_cycle_law(length, 1 << bits, flat=not frustrated)
                    empirical = satisfaction_law(g, tuple(range(length)))
                    self.assertEqual(predicted, empirical)

    def test_exact_tv_all_binary_and_four_label_cycles(self):
        for q in (2, 4, 8):
            for length in range(1, 7):
                flat = full_cycle_law(length, q, flat=True)
                other = full_cycle_law(length, q, flat=False)
                self.assertEqual(tv_distance(flat, other), cycle_tv_formula(length, q))
                self.assertEqual(sum(flat.values()), 1)
                self.assertEqual(sum(other.values()), 1)
                self.assertEqual(
                    cycle_tv_formula(length, q), Fraction(2, q)**(length-1))

    def test_noisy_binary_full_cycle_tv_exact_and_data_processing(self):
        for length in range(1, 6):
            a = full_cycle_law(length, 2, flat=True)
            b = full_cycle_law(length, 2, flat=False)
            for eta in (Fraction(0), Fraction(1, 10), Fraction(1, 4),
                        Fraction(1, 2), Fraction(3, 4), Fraction(1)):
                aa, bb = apply_bsc(a, eta), apply_bsc(b, eta)
                observed = tv_distance(aa, bb)
                self.assertEqual(observed, noisy_binary_cycle_tv(length, eta))
                self.assertLessEqual(observed, tv_distance(a, b))
                self.assertEqual(sum(aa.values()), 1)
                self.assertEqual(sum(bb.values()), 1)

    def test_sharp_one_sample_Bayes_and_coupling_N_sample_lower_bound(self):
        self.assertEqual(cycle_tv_formula(4, 4), Fraction(1, 8))
        self.assertEqual(minimum_iid_replicates_by_coupling(
            4, 4, Fraction(1, 6)), 3)
        self.assertEqual(minimum_iid_replicates_by_coupling(
            4, 8, Fraction(1, 6)), 22)
        with self.assertRaises(ValueError):
            minimum_iid_replicates_by_coupling(4, 4, Fraction(1, 2))

    def test_cycle_rank_FPT_decoder_all_C4_F2_squared_connections(self):
        pairs = ((0, 2), (0, 3), (1, 2), (1, 3))
        for shifts in product(range(4), repeat=4):
            g = game(4, 2, pairs, shifts)
            bad, labels = exact_forest_chord_decoder(g)
            self.assertEqual(Fraction(len(g.edges)-bad,len(g.edges)), optimum(g))
            self.assertEqual(bad, sum(
                labels[u] ^ labels[v] != shift for u,v,shift in g.edges))

    def test_cycle_rank_FPT_decoder_K23_F2_squared_classes(self):
        pairs = ((0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4))
        for h0, h1 in product(range(4), repeat=2):
            g = game(5, 2, pairs, (0, 0, 0, h0, 0, h1))
            bad, labels = exact_forest_chord_decoder(g)
            self.assertEqual(Fraction(6-bad,6),optimum(g))
            self.assertEqual(bad,sum(
                labels[u]^labels[v]!=shift for u,v,shift in g.edges))

    def test_cycle_rank_FPT_decoder_all_64_K4_simple_graphs(self):
        pairs = tuple(combinations(range(4), 2))
        for flags in product((False, True), repeat=6):
            chosen = tuple(edge for flag,edge in zip(flags,pairs) if flag)
            for shift in (0,1):
                g = game(4,1,chosen,(shift,)*len(chosen))
                bad,labels = exact_forest_chord_decoder(g)
                self.assertEqual(Fraction(len(chosen)-bad,len(chosen)) if chosen else 1,
                                 optimum(g))

    def test_cycle_rank_decoder_loops_parallel_and_disconnected(self):
        for g in (
            game(2, 2, ((0,0),(0,1),(0,1)), (1,2,3)),
            game(4, 1, ((0,1),(0,1),(2,3)), (0,1,1)),
            game(3, 2, (), ()),
        ):
            bad,labels=exact_forest_chord_decoder(g)
            predicted=1-Fraction(bad,len(g.edges)) if g.edges else Fraction(1)
            self.assertEqual(predicted,optimum(g))
            self.assertEqual(len(labels),g.vertices)

    def test_rank_one_holonomy_image_alone_cannot_bound_exact_decoding(self):
        # Over F2 every image has size 1 or 2; all-ones games still
        # contain MAX-CUT. This tests the structural negative-control fact.
        pairs = tuple(combinations(range(4),2))
        for flags in product((False,True),repeat=6):
            edges = tuple(edge for flag,edge in zip(flags,pairs) if flag)
            g = game(4,1,edges,(1,)*len(edges))
            self.assertTrue(all(h in (0,1) for _,h in cycle_signature(g)))
            bad,_=exact_forest_chord_decoder(g)
            self.assertEqual(Fraction(len(edges)-bad,len(edges)) if edges else 1,
                             optimum(g))


if __name__ == "__main__":
    unittest.main()
