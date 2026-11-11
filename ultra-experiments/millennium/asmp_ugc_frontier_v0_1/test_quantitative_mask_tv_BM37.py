"""BM-37 adversarial TV, unconditional Walsh and adaptive transcript checks."""
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from quantitative_mask_tv_BM37 import (
    LIMIT, K_TRI, CERTIFIED_SUP, EXPECTED_BERNSTEIN_SUP,
    NODES, U_BREAKS, Y_BREAKS, _bernstein, _collocation_inverse,
    _sup_cell, certify_supremum, matched_marginal_tv_lower,
    unrestricted_low_noise_tv_lower, unrestricted_tv_lower,
    adaptive_bayes_error_upper, verify_small_mask_pair,
    theorem_receipt,
)
from smooth_polynomial_overlap_BM35 import polynomial
from replication_uniform_upper_BM27 import (
    explicit_mask_law, exact_clean_law, xor_convolve,
)
from state_aware_replication_BM25 import (
    expanded_full_mask_law as sharp_mask,
)


def blend(a, b, alpha):
    out = {}
    for law, weight in ((a, Fraction(1)-alpha), (b, alpha)):
        for mask, prob in law.items():
            out[mask] = out.get(mask, Fraction(0))+weight*prob
    return {mask: value for mask, value in out.items() if value}


def parity_char(mask, bits):
    return 1 if (mask & bits).bit_count() % 2 == 0 else -1


class BM37TVTests(unittest.TestCase):
    def test_exact_1152_supremum_bernstein_certificate(self):
        r = certify_supremum()
        self.assertEqual((r.cells, r.coefficients), (32, 1152))
        self.assertEqual(r.exact_bernstein_envelope, EXPECTED_BERNSTEIN_SUP)
        self.assertLess(r.exact_bernstein_envelope, Fraction(127, 50))
        self.assertEqual(r.simple_rational_envelope, CERTIFIED_SUP)

    def test_independent_collocation_reconstructs_interior_samples(self):
        inv = _collocation_inverse()
        for i, j in product(range(6), repeat=2):
            self.assertEqual(
                sum((inv[i][k]*_bernstein(j, NODES[k])
                     for k in range(6)), Fraction(0)),
                int(i == j),
            )
        rng = Random(37)
        for _ in range(60):
            i = rng.randrange(8)
            j = rng.randrange(4)
            ua, ub = U_BREAKS[i:i+2]
            ya, yb = Y_BREAKS[j:j+2]
            coefficients = _sup_cell(ua, ub, ya, yb)
            x = Fraction(rng.randrange(1, 37), 37)
            y = Fraction(rng.randrange(1, 37), 37)
            u = ua+(ub-ua)*x
            low = Fraction(3, 2)*abs(u)-1
            w = low+(1-low)*(ya+(yb-ya)*y)
            reconstructed = sum(
                coefficients[6*a+b]*_bernstein(a, x)*_bernstein(b, y)
                for a, b in product(range(6), repeat=2)
            )
            self.assertEqual(reconstructed, polynomial(u, w))

    def test_exact_two_path_parity_walsh_witness(self):
        # Projection to one ordinary path plus exceptional pair.
        for n in (1, 2, 3):
            result = []
            for h in (0, 1):
                law = exact_clean_law(n, h)
                character = 3 | (3<<(2*n))
                val = sum((p*parity_char(mask, character)
                           for mask, p in law.items()), Fraction(0))
                result.append(val)
            self.assertEqual(result, [Fraction(11, 32), Fraction(5, 16)])
        self.assertEqual(unrestricted_low_noise_tv_lower(Fraction(0)),
                         Fraction(1, 64))
        self.assertEqual(unrestricted_low_noise_tv_lower(Fraction(1, 88)), 0)

    def test_BM27_exact_eraser_zero_TV_and_matching_margins(self):
        for n in (1, 2, 3):
            q0, q1 = explicit_mask_law(n, 0), explicit_mask_law(n, 1)
            receipt = verify_small_mask_pair(n, q0, q1)
            self.assertEqual(receipt.corruption_cap, LIMIT)
            self.assertEqual(receipt.observed_tv, 0)
            self.assertTrue(receipt.matched_margins)
            self.assertEqual(receipt.conditional_tv_lower, 0)

    def test_zero_masks_positive_TV_all_noise_classes(self):
        for n in (1, 2, 3):
            r = verify_small_mask_pair(n, {0: Fraction(1)},
                                       {0: Fraction(1)})
            self.assertTrue(r.matched_margins)
            self.assertEqual(r.corruption_cap, 0)
            self.assertGreaterEqual(r.observed_tv, Fraction(1, 64))
            self.assertLessEqual(r.universal_all_mask_lower, r.observed_tv)

    def test_blended_exact_eraser_has_known_linear_TV(self):
        for n in (1, 2, 3):
            p0 = exact_clean_law(n, 0)
            p1 = exact_clean_law(n, 1)
            clean_tv = sum(
                (abs(p0.get(k, 0)-p1.get(k, 0))
                 for k in p0.keys()|p1.keys()), Fraction(0))/2
            for lam in (Fraction(1, 3), Fraction(2, 3)):
                q0 = blend(explicit_mask_law(n, 0), {0: Fraction(1)}, lam)
                q1 = blend(explicit_mask_law(n, 1), {0: Fraction(1)}, lam)
                r = verify_small_mask_pair(n, q0, q1)
                self.assertTrue(r.matched_margins)
                self.assertEqual(r.corruption_cap, (1-lam)*LIMIT)
                self.assertEqual(r.observed_tv, lam*clean_tv)

    def test_asymmetric_mask_margins_reject_conditional_claim(self):
        n = 2
        q0 = blend(explicit_mask_law(n, 0), {0: Fraction(1)},
                   Fraction(1, 2))
        q1 = explicit_mask_law(n, 1)
        r = verify_small_mask_pair(n, q0, q1)
        self.assertFalse(r.matched_margins)
        self.assertIsNone(r.conditional_tv_lower)
        self.assertGreaterEqual(r.observed_tv, r.universal_all_mask_lower)

    def test_small_random_legal_masks_respect_unrestricted_TV(self):
        rng = Random(20261111)
        for n in (1, 2):
            for _ in range(12):
                def random_law():
                    keys = [rng.randrange(1<<(2*n+2)) for _ in range(4)]
                    counts = {key: Fraction(rng.randrange(1, 10))
                              for key in keys}
                    total = sum(counts.values())
                    return {key: val/total for key, val in counts.items()}
                r = verify_small_mask_pair(n, random_law(), random_law())
                self.assertGreaterEqual(r.observed_tv,
                                        r.universal_all_mask_lower)

    def test_nontrivial_large_n_matched_certificate_and_inputs(self):
        n, eta = 10000, Fraction(1, 20)
        t = matched_marginal_tv_lower(n, eta)
        self.assertGreater(t, 0)
        self.assertLess(t, 1)
        self.assertEqual(t,
                         Fraction(65, 508)*(LIMIT-eta-K_TRI/n))
        self.assertEqual(unrestricted_tv_lower(1, Fraction(1, 100)),
                         unrestricted_low_noise_tv_lower(Fraction(1, 100)))
        for n, eta in ((0, 0), (-1, 0), (1, -1), (1, 2)):
            with self.assertRaises(ValueError):
                matched_marginal_tv_lower(n, eta)

    def test_adaptive_transcript_risk_bound_exact_controls(self):
        self.assertEqual(adaptive_bayes_error_upper(0, Fraction(1, 3)),
                         Fraction(1, 2))
        self.assertEqual(adaptive_bayes_error_upper(1, 1),
                         Fraction(1, 4))
        # Construct a history-dependent binary channel with uniformly
        # separated conditional hypotheses, and calculate exact Bayes risk.
        t = Fraction(1, 3)
        states = ({(): Fraction(1)}, {(): Fraction(1)})
        for step in range(3):
            next_states = []
            for h in (0, 1):
                nxt = {}
                for history, mass in states[h].items():
                    # Reverse the output naming at odd parity histories.
                    flip = sum(history)%2
                    p = (Fraction(1)+t)/2 if h == 0 else (Fraction(1)-t)/2
                    p1 = (1-p) if flip else p
                    nxt[history+(0,)] = mass*(1-p1)
                    nxt[history+(1,)] = mass*p1
                next_states.append(nxt)
            states = tuple(next_states)
            bayes = sum((min(states[0][k], states[1][k])
                         for k in states[0]), Fraction(0))/2
            self.assertLessEqual(bayes,
                                 adaptive_bayes_error_upper(step+1, t))
        for m, t in ((-1, 0), (1, -1), (1, 2)):
            with self.assertRaises(ValueError):
                adaptive_bayes_error_upper(m, t)

    def test_receipt_reconciles_source_certificates(self):
        r = theorem_receipt(10000, Fraction(1, 20))
        self.assertEqual(r["bernstein_cells"], 32)
        self.assertEqual(r["supremum_bernstein_coefficients"], 1152)
        self.assertTrue(r["near_threshold_unrestricted_bound_exponentially_weak"])
        self.assertFalse(r["external_optimizer_required"])


if __name__ == "__main__":
    unittest.main()
