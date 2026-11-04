import unittest
from fractions import Fraction
from quotient import energy, quotient_edges, squared_autonomy_defect, externally_equitable

class DirichletQuotientTests(unittest.TestCase):
    def test_unequal_cross_edges_preserve_energy_but_break_autonomy(self):
        vertices = (0, 1, 2)
        edges = ((0, 2, Fraction(1)), (1, 2, Fraction(2)))
        grouping = {0: "A", 1: "A", 2: "B"}
        f = {"A": Fraction(0), "B": Fraction(1)}
        lifted = {u: f[grouping[u]] for u in vertices}
        self.assertEqual(energy(edges, lifted), Fraction(3))
        self.assertEqual(energy(quotient_edges(edges, grouping), f), Fraction(3))
        self.assertFalse(externally_equitable(vertices, edges, grouping))
        self.assertEqual(squared_autonomy_defect(vertices, edges, grouping, f), Fraction(1, 2))

    def test_equitable_graph_has_zero_defect(self):
        vertices = (0, 1, 2)
        edges = ((0, 2, Fraction(1)), (1, 2, Fraction(1)))
        grouping = {0: "A", 1: "A", 2: "B"}
        f = {"A": Fraction(3), "B": Fraction(-2)}
        self.assertTrue(externally_equitable(vertices, edges, grouping))
        self.assertEqual(squared_autonomy_defect(vertices, edges, grouping, f), Fraction(0))
        self.assertEqual(energy(edges, {u: f[grouping[u]] for u in vertices}),
                         energy(quotient_edges(edges, grouping), f))

    def test_internal_edges_do_not_affect_lifted_energy(self):
        grouping = {0: "A", 1: "A", 2: "B"}
        edges = ((0, 1, Fraction(100)), (0, 2, Fraction(1)), (1, 2, Fraction(2)))
        f = {"A": Fraction(0), "B": Fraction(1)}
        self.assertEqual(energy(edges, {u: f[grouping[u]] for u in grouping}),
                         energy(quotient_edges(edges, grouping), f))

if __name__ == "__main__":
    unittest.main()
