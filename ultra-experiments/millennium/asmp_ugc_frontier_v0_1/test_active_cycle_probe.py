"""ASMP-14 active interventions recover the information lost by Boolean masks."""
from fractions import Fraction
from itertools import product
import unittest

from biased_graph_observability import cactus_pair, full_boolean_law, holonomy_image_size
from finite_seed import Game, satisfaction_law
from frontier_bounds import cycle_tv_formula, tv_distance
from active_cycle_probe import (
    all_success_episodes_for_one_sided_power, exact_cycle_equality_probe,
    intervene_edge, joint_success_probability, recover_cycle_holonomy,
)

C4=((0,2),(0,3),(1,2),(1,3))


class ActiveCycleProbeTests(unittest.TestCase):
    def test_every_q4_four_cycle_holonomy_recovered_from_intervention(self):
        for shifts in product(range(4), repeat=4):
            g=Game(4,2,tuple((u,v,s) for (u,v),s in zip(C4,shifts)))
            for controlled in (0,3):
                recovered, calls=recover_cycle_holonomy(g,tuple(range(4)),controlled)
                self.assertEqual(recovered,shifts[0]^shifts[1]^shifts[2]^shifts[3])
                self.assertLessEqual(calls,3)
                self.assertEqual(
                    exact_cycle_equality_probe(g,tuple(range(4)),controlled,recovered),
                    True
                )

    def test_invisible_cactus_pair_becomes_observable_after_known_shift(self):
        a,b=cactus_pair(2,2)
        self.assertEqual(full_boolean_law(a),full_boolean_law(b))
        self.assertEqual(holonomy_image_size(a),2)
        self.assertEqual(holonomy_image_size(b),4)
        # Index 5 is the closing edge of the second triangle.
        a_shift=intervene_edge(a,5,1)
        b_shift=intervene_edge(b,5,1)
        self.assertTrue(exact_cycle_equality_probe(a,(3,4,5),5,1))
        self.assertFalse(exact_cycle_equality_probe(b,(3,4,5),5,1))
        self.assertEqual(joint_success_probability(a_shift,(3,4,5)),Fraction(1,16))
        self.assertEqual(joint_success_probability(b_shift,(3,4,5)),0)
        self.assertEqual(tv_distance(full_boolean_law(a_shift),
                                     full_boolean_law(b_shift)),
                         cycle_tv_formula(3,4))
        self.assertEqual(cycle_tv_formula(3,4),Fraction(1,4))

    def test_recovery_on_loop_and_two_parallel_edges(self):
        cases=(
            (Game(1,2,((0,0,3),)),(0,),0,3),
            (Game(2,2,((0,1,1),(0,1,2))),(0,1),1,3),
            (Game(3,2,((0,1,0),(1,2,1),(2,0,2))),(0,1,2),2,3),
        )
        for g,cycle,control,expected in cases:
            self.assertEqual(recover_cycle_holonomy(g,cycle,control)[0],expected)

    def test_minimal_one_sided_sample_counts(self):
        for length,q in ((1,4),(2,4),(3,4),(4,8)):
            for target in (Fraction(1,5),Fraction(1,20)):
                n=all_success_episodes_for_one_sided_power(length,q,target)
                p=Fraction(1,q**(length-1))
                self.assertLessEqual((1-p)**n,target)
                if n>0:
                    self.assertGreater((1-p)**(n-1),target)

    def test_joint_success_oracle_independent_against_direct_labelings(self):
        g=Game(4,2,tuple((u,v,s) for (u,v),s in zip(C4,(0,1,2,3))))
        for indices in ((),(0,), (0,1), (0,1,2),(0,1,2,3)):
            truth = satisfaction_law(g,indices)
            p=sum(prob for mask,prob in truth.items() if all(mask))
            self.assertEqual(joint_success_probability(g,indices),p)

    def test_invalid_interventions_and_cycle_queries(self):
        g=Game(4,2,tuple((u,v,s) for (u,v),s in zip(C4,(0,1,2,3))))
        with self.assertRaises(ValueError):
            intervene_edge(g,4,1)
        with self.assertRaises(ValueError):
            intervene_edge(g,0,4)
        with self.assertRaises(ValueError):
            exact_cycle_equality_probe(g,(0,1),0,1)
        with self.assertRaises(ValueError):
            exact_cycle_equality_probe(g,(0,1,2,3),5,1)
        with self.assertRaises(ValueError):
            joint_success_probability(g,(0,0))


if __name__=="__main__":
    unittest.main()
