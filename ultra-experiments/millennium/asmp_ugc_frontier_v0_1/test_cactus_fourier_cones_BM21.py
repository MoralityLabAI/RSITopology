"""BM-21: exact implicit Fourier support and cactus channel regression tests."""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from finite_seed import Game
from generic_fourier_erasure_BM17 import census,signed_walsh
from fourier_completion_BM18 import mask_marginals,convolve_clean
from cactus_fourier_cones_BM21 import (
    CycleBlock,CactusCircuit,compile_cactus,
    one_hot_cycle_sampler,explicit_common_eraser,
    common_eraser_dual_lower,verify_common_eraser_small,
    make_triangle_with_bridges,
)
from gain_balanced_inclusion_BM21 import (
    edge_subset_rank_balance,all_constraints_probability,
    graph_walsh_inclusion,clean_difference_inclusion,
    contains_unbalanced_cycle,pure_cycle_minimal_difference,
)
from separator_factor_transfer_BM16 import exact_walsh
from k4_high_degree_BM17 import k4_pair
from diamond_weighted_fourier_BM10 import EDGES as DIAMOND_EDGES
from theta_shared_cycle_erasure import THETA_EDGES


def two_triangles(q=4,gains=(1,2),bridge=0):
    # Two odd cyclic blocks with articulation 0 and optional pendant bridge.
    edges=[
        (0,1,0),(1,2,0),(2,0,gains[0]),
        (0,3,0),(3,4,0),(4,0,gains[1]),
    ]
    if bridge:
        edges.append((4,5,0))
    return Game(5+bool(bridge),q.bit_length()-1,tuple(edges))


def triangle_square(q=4,gains=(1,2),bridges=0):
    edges=[
        (0,1,0),(1,2,0),(2,0,gains[0]),
        (0,3,0),(3,4,0),(4,5,0),(5,0,gains[1])
    ]
    for j in range(bridges):
        edges.append((5+j,6+j,0))
    return Game(6+bridges,q.bit_length()-1,tuple(edges))


def compare_against_direct_labels(game):
    c=compile_cactus(game)
    flat=Game(game.vertices,game.bits,tuple(
        (u,v,0) for u,v,g in game.edges
    ))
    p0,p1=census(flat),census(game)
    for S in range(1<<len(game.edges)):
        a,b=signed_walsh(p0,S),signed_walsh(p1,S)
        assert a==c.fourier(S),(S,a,c.fourier(S))
        assert b==c.fourier(S,frustrated=True),(
            S,b,c.fourier(S,frustrated=True)
        )
        assert a-b==c.delta(S)
    return c


class BM21CactusFourierTests(unittest.TestCase):
    def test_one_frustrated_cycle_and_bridges_all_patterns_q4_q8_q2(self):
        for q,max_t in ((2,4),(4,4),(8,3)):
            for t in range(max_t):
                g=make_triangle_with_bridges(t,q=q,shift=1)
                c=compare_against_direct_labels(g)
                self.assertEqual(c.cycle_rank,1)
                self.assertEqual(c.bridge_mask.bit_count(),t)
                self.assertEqual(c.common_erasure_cap,Fraction(1,6))
                expected=(1 if q==2 else 1<<t)
                self.assertEqual(c.unicyclic_support_count(),expected)
                self.assertEqual(c.q4_support_count(),expected) if q==4 else None
                self.assertEqual(common_eraser_dual_lower(c),Fraction(1,6))
                self.assertTrue(verify_common_eraser_small(c))
                for S in range(1<<len(g.edges)):
                    self.assertEqual(c.unicyclic_cone_member(S),
                                     c.residual_support_member(S))
                    if q==4:
                        self.assertEqual(c.q4_support_member(S),
                                         c.residual_support_member(S))

    def test_two_frustrated_triangles_q4_cancel_on_both_full_cycles(self):
        game=two_triangles(q=4,gains=(1,2))
        c=compare_against_direct_labels(game)
        self.assertEqual(c.cycle_rank,2)
        self.assertEqual(tuple(v.length for v in c.cycles),(3,3))
        self.assertEqual(c.delta((1<<6)-1),0)
        self.assertTrue(contains_unbalanced_cycle(game,63))
        self.assertFalse(c.q4_support_member(63))
        self.assertEqual(c.q4_support_count(),14)
        self.assertEqual(sum(bool(c.delta(S)) for S in range(64)),14)
        self.assertEqual(c.common_erasure_cap,Fraction(1,6))
        self.assertTrue(verify_common_eraser_small(c))
        self.assertEqual(len(explicit_common_eraser(c)),16)
        for S in range(64):
            self.assertEqual(c.q4_support_member(S),bool(c.delta(S)))

    def test_two_frustrated_triangles_q8_do_not_have_q4_parity_cancellation(self):
        game=two_triangles(q=8,gains=(1,2))
        c=compile_cactus(game)
        self.assertNotEqual(c.delta(63),0)
        self.assertNotEqual(c.delta(7),0)
        self.assertEqual(c.common_erasure_cap,Fraction(1,6))
        self.assertTrue(verify_common_eraser_small(c))
        for S in (0,7,15,31,56,63):
            self.assertEqual(c.fourier(S),exact_walsh(
                Game(game.vertices,game.bits,tuple(
                    (u,v,0) for u,v,g in game.edges
                )),S))
            self.assertEqual(c.fourier(S,frustrated=True),
                             exact_walsh(game,S))
        with self.assertRaises(ValueError):
            c.q4_support_count()

    def test_triangle_square_even_frustrated_cycle_exact_cactus_formula(self):
        game=triangle_square(q=4,gains=(1,2),bridges=1)
        c=compare_against_direct_labels(game)
        self.assertEqual(c.cycle_rank,2)
        self.assertEqual(tuple(v.length for v in c.cycles),(3,4))
        # The shortest unbalanced block controls the uniform cap.
        self.assertEqual(c.common_erasure_cap,Fraction(1,6))
        self.assertTrue(verify_common_eraser_small(c))
        self.assertEqual(c.q4_support_count(),
                         sum(bool(c.delta(S)) for S in range(1<<c.edge_count)))
        for S in range(1<<c.edge_count):
            self.assertEqual(c.q4_support_member(S),bool(c.delta(S)))

    def test_balanced_cycle_and_a_forest_have_no_residual(self):
        for q in (2,4,8):
            for t in (0,1,3):
                g=make_triangle_with_bridges(t,q=q,shift=0)
                c=compile_cactus(g)
                self.assertFalse(c.unbalanced)
                self.assertEqual(c.unicyclic_support_count(),0)
                self.assertEqual(c.common_erasure_cap,0)
                self.assertEqual(c.q4_support_count(),0) if q==4 else None
                self.assertTrue(verify_common_eraser_small(c))
                for S in range(1<<c.edge_count):
                    self.assertEqual(c.delta(S),0)

    def test_q4_two_odd_cyclic_blocks_with_bridges_symbolic_count(self):
        for t in (0,1,2):
            g=two_triangles(4,(1,2),bridge=t>0)
            c=compare_against_direct_labels(g)
            want=14*(2 if t else 1)
            self.assertEqual(c.q4_support_count(),want)
            self.assertEqual(sum(bool(c.delta(S))
                                 for S in range(1<<c.edge_count)),want)

    def test_hypothesis_aware_correlated_mask_membership_exact_without_clean_census(self):
        game=make_triangle_with_bridges(2,q=4)
        c=compile_cactus(game)
        flat=Game(game.vertices,game.bits,tuple(
            (u,v,0) for u,v,g in game.edges
        ))
        p0,p1=census(flat),census(game)
        q0={0:3,1:1}
        q1={0:2,4:1,8:1}
        for S in range(1<<c.edge_count):
            actual=c.residual_from_mask_pair(S,q0,q1,4)
            h0=Fraction(3+( -1 if S&1 else 1),4)
            h1=Fraction(2+
                (-1 if S&4 else 1)+(-1 if S&8 else 1),4)
            reference=signed_walsh(p0,S)*h0-signed_walsh(p1,S)*h1
            self.assertEqual(actual,reference)
        with self.assertRaises(ValueError):
            c.residual_from_mask_pair(7,{0:3},{0:4},4)

    def test_large_triangle_250_bridges_exponential_support_compact(self):
        t=250
        g=make_triangle_with_bridges(t,q=4,shift=1)
        c=compile_cactus(g)
        self.assertEqual((c.vertices,c.edge_count),(253,253))
        self.assertEqual(c.bridge_mask.bit_count(),250)
        self.assertEqual(c.unicyclic_support_count(),1<<250)
        self.assertEqual(c.q4_support_count(),1<<250)
        self.assertEqual(c.symbolic_receipt()["q4_exact_support_count"],1<<250)
        self.assertEqual(c.common_erasure_cap,Fraction(1,6))
        full=(1<<c.edge_count)-1
        self.assertTrue(c.unicyclic_cone_member(full))
        self.assertTrue(c.q4_support_member(full))
        self.assertFalse(c.q4_support_member(full^1))
        self.assertEqual(
            c.delta(full),Fraction(-1,2**(t+1))
        )
        self.assertEqual(c.delta(7),Fraction(-1,2))
        self.assertFalse(c.symbolic_receipt()["explicit_Fourier_table_constructed"])
        with self.assertRaises(ValueError):
            explicit_common_eraser(c)
        rng=Random(20261110)
        for _ in range(100):
            noise=one_hot_cycle_sampler(c,rng)
            self.assertEqual(noise&c.bridge_mask,0)
            self.assertLessEqual(noise.bit_count(),1)
        # Even though graph treewidth=2, D contains the full edge set,
        # so the clique expansion of the residual support is K_253,
        # of treewidth 252. Its explicit support contains 2^250 entries.

    def test_q8_large_unicyclic_support_and_q2_bridge_character_extinction(self):
        t=120
        a=compile_cactus(make_triangle_with_bridges(t,q=8))
        b=compile_cactus(make_triangle_with_bridges(t,q=2))
        self.assertEqual(a.unicyclic_support_count(),1<<t)
        self.assertEqual(b.unicyclic_support_count(),1)
        self.assertEqual(a.common_erasure_cap,Fraction(1,6))
        self.assertEqual(b.common_erasure_cap,Fraction(1,6))
        self.assertEqual(b.delta((1<<b.edge_count)-1),0)

    def test_edge_reordering_and_nongauge_spanning_forest_invariance(self):
        original=make_triangle_with_bridges(3,q=4,shift=2)
        ordering=(3,0,5,2,1,4)
        permuted=Game(original.vertices,original.bits,tuple(
            original.edges[i] for i in ordering
        ))
        c=compare_against_direct_labels(permuted)
        self.assertEqual(len(c.cycles),1)
        self.assertEqual(c.cycles[0].gain,2)
        self.assertEqual(c.q4_support_count(),8)
        self.assertEqual(c.common_erasure_cap,Fraction(1,6))

    def test_cactus_eraser_full_convolution_matches_direct_Boolean_laws(self):
        for g in (two_triangles(4,(1,2)),
                  triangle_square(4,(1,2),bridges=0),
                  make_triangle_with_bridges(2,q=8)):
            c=compile_cactus(g)
            flat=Game(g.vertices,g.bits,tuple(
                (u,v,0) for u,v,s in g.edges
            ))
            w=explicit_common_eraser(c)
            c0,c1=census(flat),census(g)
            self.assertEqual(convolve_clean(c.edge_count,c0,w),
                             convolve_clean(c.edge_count,c1,w))
            marg=mask_marginals(c.edge_count,w)
            self.assertEqual(max(marg),common_eraser_dual_lower(c))
            self.assertTrue(all(p==0 for i,p in enumerate(marg)
                                if c.bridge_mask&(1<<i)))

    def test_reject_overlap_non_cactus_and_disconnected_and_parallel(self):
        k4=k4_pair().other
        with self.assertRaises(ValueError):
            compile_cactus(k4)
        theta=Game(5,2,tuple(
            (u,v,1 if i==3 else 0) for i,(u,v) in enumerate(THETA_EDGES)
        ))
        with self.assertRaises(ValueError):
            compile_cactus(theta)
        with self.assertRaises(ValueError):
            compile_cactus(Game(4,2,((0,1,0),(1,2,0))))
        with self.assertRaises(ValueError):
            compile_cactus(Game(3,2,((0,1,0),(1,0,1),(1,2,0))))
        with self.assertRaises(ValueError):
            compile_cactus(Game(2,2,((0,0,0),(0,1,0))))
        with self.assertRaises(ValueError):
            make_triangle_with_bridges(-1)
        with self.assertRaises(ValueError):
            make_triangle_with_bridges(1,q=3)
        with self.assertRaises(ValueError):
            compile_cactus(make_triangle_with_bridges(0)).q4_support_member(8)
        with self.assertRaises(ValueError):
            compile_cactus(make_triangle_with_bridges(0)).unicyclic_cone_member(-1)


class BM21BalancedSubgraphTests(unittest.TestCase):
    def test_general_balanced_subgraph_Fourier_formula_matches_independent_K4(self):
        pair=k4_pair()
        for g in (pair.flat,pair.other):
            p=census(g)
            for S in range(64):
                self.assertEqual(graph_walsh_inclusion(g,S),
                                 signed_walsh(p,S))
                self.assertEqual(graph_walsh_inclusion(g,S),exact_walsh(g,S))
        for S in range(64):
            diff=clean_difference_inclusion(pair.other,S)
            direct=signed_walsh(census(pair.flat),S)-signed_walsh(
                census(pair.other),S
            )
            self.assertEqual(diff,direct)
            if not contains_unbalanced_cycle(pair.other,S):
                self.assertEqual(diff,0)

    def test_all_balanced_subgraph_constraints_retain_probability(self):
        g=make_triangle_with_bridges(2,q=4,shift=1)
        for S in range(1<<len(g.edges)):
            r,balanced=edge_subset_rank_balance(g,S)
            value=all_constraints_probability(g,S)
            self.assertEqual(value,Fraction(1,4**r) if balanced else 0)
            self.assertEqual(clean_difference_inclusion(g,S),
                             compile_cactus(g).delta(S))
        self.assertEqual(pure_cycle_minimal_difference(g,(0,1,2)),
                         Fraction(-1,2))
        with self.assertRaises(ValueError):
            pure_cycle_minimal_difference(g,(0,1,3))
        with self.assertRaises(ValueError):
            pure_cycle_minimal_difference(g,(0,1))
        with self.assertRaises(ValueError):
            pure_cycle_minimal_difference(make_triangle_with_bridges(
                0,shift=0),(0,1,2))

    def test_tree_branching_and_odd_cycle_cancellation(self):
        g=two_triangles(4,(1,2))
        c=compile_cactus(g)
        self.assertEqual(clean_difference_inclusion(g,63),0)
        self.assertTrue(contains_unbalanced_cycle(g,63))
        self.assertEqual(c.delta(63),0)
        for S in range(64):
            self.assertEqual(clean_difference_inclusion(g,S),c.delta(S))
        for S in (7,56):
            self.assertNotEqual(clean_difference_inclusion(g,S),0)

    def test_malformed_inclusion_queries(self):
        g=make_triangle_with_bridges(1)
        with self.assertRaises(ValueError):
            graph_walsh_inclusion(g,-1)
        with self.assertRaises(ValueError):
            clean_difference_inclusion(g,16)
        with self.assertRaises(ValueError):
            all_constraints_probability(g,100)
        with self.assertRaises(ValueError):
            edge_subset_rank_balance(None,0)


if __name__=="__main__":
    unittest.main()
