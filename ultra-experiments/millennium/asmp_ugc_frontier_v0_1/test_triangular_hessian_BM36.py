"""BM-36 exact rational geometric Hessian and all-n rate regressions."""
from fractions import Fraction
from itertools import product
from random import Random
from math import comb
import unittest

from smooth_polynomial_overlap_BM35 import (
    COEFFICIENT_NUMERATORS, DENOMINATOR, smooth_hessian_rate,
)
from direct_finite_concentration_BM34 import conditional_moments
from triangular_hessian_BM36 import (
    NODES, U_BREAKS, Y_BREAKS, DERIVATIVES, INVERSE_BERNSTEIN,
    SIMPLE_RATE_CONSTANT, in_observation_triangle, bernstein_basis,
    verify_basis_inverse, hessian_value, cell_bernstein_coefficients,
    verify_triangular_hessian, finite_gap_bound, theorem_receipt,
)


class BM36TriangularHessianTests(unittest.TestCase):
    def test_exact_1536_coefficient_certificate_and_constants(self):
        r = verify_triangular_hessian()
        self.assertTrue(verify_basis_inverse())
        self.assertEqual((r.cells, r.derivative_fields, r.coefficients_checked),
                         (32, 3, 1536))
        self.assertEqual(r.hessian_uu, Fraction(
            436135497777991794997121344, 31855192562479434723338625))
        self.assertEqual(r.hessian_uw, Fraction(
            640780500121816588916939272, 31855192562479434723338625))
        self.assertEqual(r.hessian_ww, Fraction(
            17346026126993139909417264008, 286696733062314912510047625))
        self.assertEqual(r.exact_rate_coefficient, Fraction(
            433489819753448825447087550392,
            3727057529810093862630619125))
        self.assertLess(r.exact_rate_coefficient, 117)
        self.assertGreater(r.exact_rate_coefficient, 116)
        self.assertEqual(r.integer_rate_coefficient, SIMPLE_RATE_CONSTANT)
        self.assertLess(r.exact_rate_coefficient,
                        smooth_hessian_rate().sharp_computable_rate_coefficient)

    def test_collocation_matrix_is_exact_identity(self):
        for i in range(4):
            for j in range(4):
                value = sum(
                    INVERSE_BERNSTEIN[i][r]*bernstein_basis(j, NODES[r])
                    for r in range(4)
                )
                self.assertEqual(value, int(i == j))
        self.assertEqual(sum(bernstein_basis(i, Fraction(2, 7))
                             for i in range(4)), 1)

    def test_every_observed_path_average_stays_in_triangle(self):
        points = ((Fraction(-4, 3), Fraction(1)),
                  (Fraction(0), Fraction(-1)),
                  (Fraction(4, 3), Fraction(1)))
        for n in range(1, 7):
            for paths in product(points, repeat=n):
                u = sum(p[0] for p in paths)/n
                w = sum(p[1] for p in paths)/n
                self.assertTrue(in_observation_triangle(u, w))
        self.assertFalse(in_observation_triangle(Fraction(4, 3), -1))
        self.assertFalse(in_observation_triangle(Fraction(0), Fraction(3, 2)))

    def test_conditional_latent_centers_stay_in_triangle(self):
        for n in range(1, 9):
            for c0 in range(n+1):
                for c1 in range(n+1-c0):
                    c2 = n-c0-c1
                    for regime in ("A", "B"):
                        r = conditional_moments(n, (c0, c1, c2), regime)
                        self.assertTrue(in_observation_triangle(
                            r.mean_u, r.mean_w
                        ))
                        if regime == "A":
                            self.assertEqual(r.variance_w, 0)

    def test_interpolant_reconstructs_true_derivative_on_cell_interiors(self):
        rng = Random(20261111)
        for _ in range(90):
            derivative = DERIVATIVES[rng.randrange(3)]
            i = rng.randrange(len(U_BREAKS)-1)
            j = rng.randrange(len(Y_BREAKS)-1)
            ua, ub = U_BREAKS[i:i+2]
            ya, yb = Y_BREAKS[j:j+2]
            beta = cell_bernstein_coefficients(
                derivative, ua, ub, ya, yb
            )
            x = Fraction(rng.randrange(1, 49), 49)
            y = Fraction(rng.randrange(1, 49), 49)
            u = ua+(ub-ua)*x
            low = Fraction(3, 2)*abs(u)-1
            w = low+(1-low)*(ya+(yb-ya)*y)
            reconstructed = sum(
                beta[k][l]*bernstein_basis(k, x)*bernstein_basis(l, y)
                for k in range(4) for l in range(4)
            )
            self.assertEqual(reconstructed,
                             hessian_value(derivative, u, w))

    def test_hessian_direct_differentiation_matches_manual_monomial(self):
        c = {(4, 0): DENOMINATOR*3, (1, 2): DENOMINATOR*5}
        u, w = Fraction(2, 3), Fraction(3, 4)
        self.assertEqual(hessian_value((2, 0), u, w, coefficients=c),
                         36*u*u)
        self.assertEqual(hessian_value((1, 1), u, w, coefficients=c),
                         10*w)
        self.assertEqual(hessian_value((0, 2), u, w, coefficients=c),
                         10*u)
        with self.assertRaises(ValueError):
            hessian_value((0, 0), u, w)
        with self.assertRaises(ValueError):
            cell_bernstein_coefficients((2, 0), -1, 1, 0, 1)

    def test_large_mutation_refused_by_rate_certificate(self):
        altered = dict(COEFFICIENT_NUMERATORS)
        altered[(2, 0)] = 100*DENOMINATOR
        with self.assertRaises(AssertionError):
            verify_triangular_hessian(coefficients=altered)
        with self.assertRaises(ValueError):
            verify_triangular_hessian(coefficients={(9, 0): 1})

    def test_all_integer_n_and_receipt(self):
        for n in (1, 2, 3, 16, 100, 10**4, 10**6, 10**12):
            self.assertEqual(finite_gap_bound(n), Fraction(117, n))
            self.assertLess(finite_gap_bound(n), Fraction(348, n))
        for n in (0, -1, Fraction(1, 2), "9"):
            with self.assertRaises(ValueError):
                finite_gap_bound(n)
        r = theorem_receipt(10**6)
        self.assertEqual(r["cells"], 32)
        self.assertEqual(r["exact_bernstein_coefficients"], 1536)
        self.assertEqual(r["gap_bound"], "117/1000000")
        self.assertTrue(r["uses_same_BM35_polynomial"])
        self.assertFalse(r["trusts_external_optimizer"])


if __name__ == "__main__":
    unittest.main()
