"""BM-15 exact SP transfer algebra, nonexchangeable nested block controls."""
from fractions import Fraction
from functools import reduce
from itertools import product
import unittest

from series_parallel_transfer_BM15 import (
    SPNode, SpikeMessage, edge, series, parallel, transfer, walsh,
    parallel_transfer, series_transfer, compile_game,
    direct_conditional, direct_walsh, selected_spike_profile,
)
from theta_fourier_transfer_BM12 import theta_walsh_transfer,theta_path_game
from finite_seed import satisfaction_law


def chain(gains):
    if not gains:
        raise ValueError("path must have >=1 edge")
    return reduce(series,(edge(g) for g in gains))


def theta_tree(lengths,gains):
    return reduce(parallel, (
        chain((g,)+(0,)*(n-1)) for n,g in zip(lengths,gains)
    ))


def nested_graph():
    # First branch: edge u-w, then parallel edges w-v with gains 0,1.
    # Second branch: two-edge path u-x-v. The middle pair on first
    # branch has a frustrated length-two subcycle.
    return parallel(series(edge(0),parallel(edge(0),edge(1))),
                    series(edge(0),edge(0)))


class SPTransferTests(unittest.TestCase):
    def test_leaf_selected_and_unselected_conditional_messages(self):
        for q in (2,4,8):
            for gain in range(q):
                node=edge(gain)
                self.assertEqual(walsh(q,node,0),1)
                self.assertEqual(walsh(q,node,1),1-Fraction(2,q))
                a=transfer(q,node,1)
                for d in range(q):
                    self.assertEqual(a.evaluate(d),-1 if d==gain else 1)
                    self.assertEqual(a.evaluate(d),
                                     direct_conditional(q,node,1,d))

    def test_composed_spike_operators_equal_pointwise_and_convolution(self):
        q=4
        a=SpikeMessage(Fraction(3,5),{0:Fraction(-1,4),2:Fraction(2,3)})
        b=SpikeMessage(Fraction(4,7),{1:Fraction(-2,5),2:Fraction(1,3)})
        para=parallel_transfer(a,b)
        serial=series_transfer(a,b,q)
        for d in range(q):
            self.assertEqual(para.evaluate(d),a.evaluate(d)*b.evaluate(d))
            target=sum((a.evaluate(x)*b.evaluate(x^d) for x in range(q)),
                       Fraction(0))/q
            self.assertEqual(serial.evaluate(d),target)

    def test_BM12_parallel_paths_all_walsh_indices_agree_with_new_algebra(self):
        for q,lengths,gains in (
            (4,(1,2,2),(0,1,2)),
            (4,(2,2,2),(0,1,0)),
            (4,(1,3,2),(1,3,2)),
            (8,(2,2,2),(0,1,2)),
            (8,(1,2,2),(2,2,1)),
        ):
            node=theta_tree(lengths,gains)
            m=sum(lengths)
            self.assertEqual(compile_game(q,node).edges,
                             theta_path_game(q,lengths,gains).edges)
            for subset in range(1<<m):
                self.assertEqual(walsh(q,node,subset),
                                 theta_walsh_transfer(q,lengths,gains,subset))
            if q==4:
                for subset in (0,1,3,(1<<m)-1):
                    self.assertEqual(walsh(q,node,subset),
                                     direct_walsh(q,node,subset))

    def test_nested_SP_graph_all_Fourier_subsets_match_independent_labels(self):
        node=nested_graph()
        game=compile_game(4,node)
        self.assertEqual(game.vertices,4)
        self.assertEqual(len(game.edges),5)
        for subset in range(32):
            model=transfer(4,node,subset)
            for d in range(4):
                self.assertEqual(model.evaluate(d),
                                 direct_conditional(4,node,subset,d))
            self.assertEqual(model.average(4),direct_walsh(4,node,subset))

    def test_nested_internal_branch_invalidates_naive_path_exchangeability(self):
        node=nested_graph()
        # Both tested degree-two subsets lie in the same outer u-v path.
        # The pair (e1,e2) is a frustrated parallel two-cycle. The pair
        # (e0,e1) is a forest. They must be distinguished.
        inner_pair=walsh(4,node,(1<<1)|(1<<2))
        chain_pair=walsh(4,node,(1<<0)|(1<<1))
        self.assertEqual(inner_pair,Fraction(0))
        self.assertEqual(chain_pair,Fraction(1,4))
        self.assertNotEqual(inner_pair,chain_pair)

    def test_walsh_matches_existing_complete_Boolean_satisfaction_law(self):
        node=nested_graph()
        game=compile_game(4,node)
        law=satisfaction_law(game,tuple(range(len(game.edges))))
        for S in range(1<<len(game.edges)):
            observed=sum((
                prob * (-1 if sum(mask[i] for i in range(len(mask))
                                    if S&(1<<i))%2 else 1)
                for mask,prob in law.items()
            ),Fraction(0))
            self.assertEqual(walsh(4,node,S),observed)

    def test_series_parallel_coherence_in_small_identity_cases(self):
        # Associativity at fixed terminals and edge order, for both
        # series convolution and pointwise parallel composition.
        for q in (2,4,8):
            a,b,c=edge(0),edge(1),edge(0)
            for op in (series,parallel):
                first=op(op(a,b),c)
                second=op(a,op(b,c))
                for subset in range(8):
                    self.assertEqual(walsh(q,first,subset),
                                     walsh(q,second,subset))
            # An exact interchange law is not generally asserted.

    def test_large_alphabet_40_edge_nested_sp_recurrence(self):
        q=1<<12
        node=parallel(chain((1,)+(0,)*19),chain((2,)+(0,)*19))
        game=compile_game(q,node)
        self.assertEqual((game.vertices,len(game.edges)),(40,40))
        for subset in (0,1,(1<<40)-1,0xAAAAAAAAAA,0x123456789A):
            message=transfer(q,node,subset)
            self.assertLessEqual(message.support_size,2)
            self.assertTrue(-1<=message.average(q)<=1)
        receipt=selected_spike_profile(q,node,(1<<40)-1)
        self.assertEqual(receipt["enumerated_vertex_labelings"],0)
        self.assertEqual(receipt["full_label_space"],"4096^40")

    def test_bad_input_rejected(self):
        with self.assertRaises(ValueError):
            edge(-1)
        with self.assertRaises(ValueError):
            series(edge(0),3)
        with self.assertRaises(ValueError):
            walsh(3,edge(0),1)
        with self.assertRaises(ValueError):
            walsh(4,edge(0),2)
        with self.assertRaises(ValueError):
            compile_game(4,edge(7))
        with self.assertRaises(ValueError):
            walsh(4,SPNode("unknown",left=edge(0),right=edge(0)),1)
        with self.assertRaises(ValueError):
            direct_conditional(4,edge(0),1,4)


if __name__=="__main__":
    unittest.main()
