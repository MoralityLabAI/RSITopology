"""BM-16 exact general graph separator factor elimination controls.

Independent full vertex-label averages, K4 and the two-terminal Wheatstone
network are included, so the checks are not confined to SP graphs.
"""
from fractions import Fraction
from itertools import product
import unittest

from finite_seed import Game,satisfaction_law
from separator_factor_transfer_BM16 import (
    Factor,BoundaryResult,_initial_factors,min_fill_order,
    eliminate_factor,boundary_expectation,anchored_boundary,
    exact_walsh,direct_boundary_oracle,elimination_manifest,
)
from series_parallel_transfer_BM15 import (
    edge,series,parallel,compile_game,walsh as sp_walsh,
)


def k4(q):
    return Game(4,q.bit_length()-1,(
        (0,1,0),(0,2,1),(0,3,2),
        (1,2,0),(1,3,3),(2,3,1),
    ))


def wheatstone(q):
    return Game(4,q.bit_length()-1,(
        (0,2,0),(2,1,1),(0,3,2),
        (3,1,0),(2,3,3),
    ))


def theta():
    return Game(5,2,(
        (0,2,0),(1,2,0),(0,3,0),(1,3,1),
        (0,4,0),(1,4,2),
    ))


class SeparatorFactorTransferTests(unittest.TestCase):
    def test_all_K4_walsh_subsets_match_independent_label_enumeration(self):
        for q in (4,8):
            game=k4(q)
            for S in range(1<<len(game.edges)):
                expected=direct_boundary_oracle(game,S,())[()]
                self.assertEqual(exact_walsh(game,S),expected)
            self.assertEqual(exact_walsh(game,0),1)

    def test_wheatstone_boundary_three_terminals_and_full_walsh(self):
        for q in (4,8):
            game=wheatstone(q)
            for S in (0,1,3,7,15,31):
                r=boundary_expectation(game,S,(0,1,2))
                expected=direct_boundary_oracle(game,S,(0,1,2))
                self.assertEqual(r.values,expected)
                self.assertEqual(r.elimination_order,(3,))
                self.assertEqual(len(r.values),q**3)
                anchor=anchored_boundary(r,q)
                self.assertEqual(len(anchor),q**2)
                self.assertEqual(r.max_join_scope,4 if (S & (1<<4))
                                 and (S & (1<<2)) else r.max_join_scope)
                self.assertEqual(sum(r.values.values(),Fraction(0))/q**3,
                                 exact_walsh(game,S))

    def test_genuine_K4_three_terminal_gauge_quotient(self):
        game=k4(4)
        r=boundary_expectation(game,63,(0,1,2))
        expected=direct_boundary_oracle(game,63,(0,1,2))
        self.assertEqual(r.values,expected)
        self.assertEqual(r.max_join_scope,4)
        quotient=anchored_boundary(r,4)
        self.assertEqual(len(quotient),16)
        for x,y,z in product(range(4),repeat=3):
            self.assertEqual(r.at(x,y,z),quotient[(y^x,z^x)])

    def test_two_terminal_theta_good_and_bad_orders_report_width(self):
        game=theta()
        S=(1<<6)-1
        greedy=min_fill_order(game,S)
        efficient=boundary_expectation(game,S,order=greedy)
        poor=boundary_expectation(game,S,order=(0,2,3,4,1))
        self.assertEqual(efficient.at(),poor.at())
        self.assertEqual(efficient.at(),direct_boundary_oracle(game,S,())[()])
        self.assertEqual(efficient.max_join_scope,3)
        self.assertEqual(poor.max_join_scope,4)
        self.assertEqual(min_fill_order(game,S,preserve=(0,1)),(2,3,4))

    def test_selected_two_terminal_boundary_messages_match_direct(self):
        game=theta()
        for S in (0,3,15,31,51,60,63):
            result=boundary_expectation(game,S,(0,1))
            self.assertEqual(result.values,
                             direct_boundary_oracle(game,S,(0,1)))
            self.assertEqual(len(anchored_boundary(result,4)),4)

    def test_all_SP_nested_walsh_subsets_match_general_factor_method(self):
        node=parallel(series(edge(0),parallel(edge(0),edge(1))),
                      series(edge(0),edge(0)))
        game=compile_game(4,node)
        for S in range(1<<5):
            self.assertEqual(exact_walsh(game,S),sp_walsh(4,node,S))

    def test_32_label_long_chain_without_exponential_vertex_enumeration(self):
        from functools import reduce
        node=reduce(series,(edge(1) if i==0 else edge(0)
                            for i in range(15)))
        game=compile_game(32,node)
        S=(1<<15)-1
        report=elimination_manifest(game,S)
        self.assertEqual(report["max_table_states"],32**2)
        self.assertEqual(report["induced_max_join_scope"],2)
        self.assertEqual(exact_walsh(game,S),sp_walsh(32,node,S))
        self.assertEqual(report["boundary_entries"],1)
        self.assertLess(report["explicit_table_entries"],32**15)

    def test_edge_loops_and_unselected_edges_normalize_exactly(self):
        game=Game(3,2,((0,0,1),(0,1,0),(1,2,0),(2,2,0)))
        for S in range(16):
            self.assertEqual(exact_walsh(game,S),
                             direct_boundary_oracle(game,S,())[()])
        self.assertEqual(exact_walsh(game,1),1)
        self.assertEqual(exact_walsh(game,8),-1)

    def test_graph_factorization_sensitivities_and_validation(self):
        game=k4(4)
        with self.assertRaises(ValueError):
            boundary_expectation(game,64)
        with self.assertRaises(ValueError):
            boundary_expectation(game,63,(0,0))
        with self.assertRaises(ValueError):
            boundary_expectation(game,63,(4,))
        with self.assertRaises(ValueError):
            boundary_expectation(game,63,order=(0,1,2))
        with self.assertRaises(ValueError):
            min_fill_order(game,63,preserve=(0,0))
        with self.assertRaises(ValueError):
            direct_boundary_oracle(game,63,(0,4))
        with self.assertRaises(ValueError):
            anchored_boundary(boundary_expectation(game,63),4)
        with self.assertRaises(ValueError):
            boundary_expectation(game,63,(0,1)).at(0)


if __name__=="__main__":
    unittest.main()
