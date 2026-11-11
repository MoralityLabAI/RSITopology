"""BM-09 exact independent rational theta erasure and Fourier controls."""
from fractions import Fraction
from itertools import product
import unittest

from theta_shared_cycle_erasure import (
    N_EDGES, MASKS, THETA_EDGES, THETA_SHIFTS, Q8_FLAT,
    Q8_FRUSTRATED, Q8_DUAL_EQUALITY, Q8_DUAL_MARGINAL,
    q4_common_mask, q4_one_balanced_mask, signed_walsh_count, theta_counts, theta_laws,
    uniform_cap_counts, xor_convolve_counts,
    verify_q4_primal, verify_q4_lower_lemma, verify_q4_one_balanced_case,
    verify_q8_primal, verify_q8_dual, exact_theta_certificate,
)
from sharp_erasure_optimality import critical_erasure_cap
from finite_seed import Game, satisfaction_law


def direct_satisfaction_law_counts(q, shifts):
    """Independent existing graph oracle built around an Edge-game model."""
    g=Game(5,q.bit_length()-1,tuple(
        (u,v,s) for (u,v),s in zip(THETA_EDGES,shifts)))
    law=satisfaction_law(g,tuple(range(6)))
    return tuple(
        int(law.get(tuple(bool(mask & (1<<i)) for i in range(6)),
                    Fraction(0))*q**5)
        for mask in range(MASKS)
    )


class ThetaInteractingCycleTests(unittest.TestCase):
    def test_exact_clean_theta_laws_match_independent_graph_oracle(self):
        for q in (2,4,8):
            for shifts in ((0,)*6,THETA_SHIFTS,
                           (0,0,0,1,0,0)):
                if any(s>=q for s in shifts):
                    continue
                self.assertEqual(theta_counts(q,shifts),
                                 direct_satisfaction_law_counts(q,shifts))

    def test_q4_short_combinatorial_lower_and_common_witness(self):
        self.assertTrue(verify_q4_lower_lemma())
        self.assertTrue(verify_q4_primal())
        masks=q4_common_mask()
        self.assertEqual(masks[0],3)
        self.assertEqual(sum(int(x>0) for x in masks),10)
        self.assertEqual(sum(masks),12)
        self.assertEqual(uniform_cap_counts(masks),2)
        self.assertEqual(Fraction(uniform_cap_counts(masks),sum(masks)),
                         Fraction(1,6))
        p0,p1=theta_laws(4)
        for subset in (15,51,60,63):
            self.assertGreater(signed_walsh_count(p0,subset),0)
            self.assertEqual(signed_walsh_count(p1,subset),0)

    def test_same_theta_graph_different_balance_pattern_changes_erasure(self):
        self.assertTrue(verify_q4_one_balanced_case())
        witness=q4_one_balanced_mask()
        self.assertEqual(sum(witness),16)
        self.assertEqual(uniform_cap_counts(witness),2)
        self.assertEqual(Fraction(2,16),Fraction(1,8))
        self.assertEqual(exact_theta_certificate()[
            "q4_one_balanced_exact_erasure"],"1/8")
        # A single balanced four-cycle with two unbalanced ones needs
        # exactly 1/8; with all three unbalanced cycles it needs 1/6.
        self.assertLess(Fraction(1,8),Fraction(1,6))

    def test_q8_primal_and_dual_exact_complementary_certificate(self):
        self.assertTrue(verify_q8_primal())
        self.assertTrue(verify_q8_dual())
        self.assertEqual(sum(Q8_FLAT),10080)
        self.assertEqual(sum(Q8_FRUSTRATED),10080)
        self.assertEqual(Q8_DUAL_EQUALITY[64]+Q8_DUAL_EQUALITY[65],1740)
        self.assertEqual(sum(Q8_DUAL_MARGINAL),-300)
        self.assertEqual(Fraction(464,10080),Fraction(29,630))

    def test_synchronized_cycle_erasure_more_expensive_than_either_cycle(self):
        for q,eta in ((4,Fraction(1,6)),(8,Fraction(29,630))):
            isolated=critical_erasure_cap(q,4)
            self.assertGreater(eta,isolated)
            self.assertEqual(isolated, Fraction(1,8) if q==4
                             else Fraction(1,44))
            self.assertGreater(eta/isolated,1)

    def test_perturbing_primal_masks_invalidates_exact_equalization(self):
        p0,p1=theta_laws(8)
        altered=list(Q8_FLAT)
        altered[0]-=1
        altered[1]+=1
        self.assertEqual(sum(altered),sum(Q8_FLAT))
        self.assertNotEqual(xor_convolve_counts(p0,tuple(altered)),
                            xor_convolve_counts(p1,Q8_FRUSTRATED))

    def test_q4_fourier_lower_bound_pointwise_inequality_all_64_masks(self):
        # k=sum errors, T=sum of parities after omitting each coordinate.
        # For k even, T=k; for k odd, T=6-k <= k+4.
        for mask in range(MASKS):
            k=mask.bit_count()
            t=sum(((mask^(mask & (1<<i))).bit_count()%2)
                  for i in range(N_EDGES))
            self.assertEqual(t,k if k%2==0 else N_EDGES-k)
            self.assertLessEqual(t,k+4*(k%2))

    def test_certificate_receipt_and_malformed_cases(self):
        certificate=exact_theta_certificate()
        self.assertTrue(certificate["q4_lower_verified"])
        self.assertTrue(certificate["q8_primal_dual_verified"])
        self.assertFalse(certificate["external_solver_required"])
        self.assertEqual(certificate["q8_exact_erasure"],"29/630")
        with self.assertRaises(ValueError):
            theta_counts(3,THETA_SHIFTS)
        with self.assertRaises(ValueError):
            theta_counts(4,(0,)*5)
        with self.assertRaises(ValueError):
            xor_convolve_counts((1,),(1,)*MASKS)
        with self.assertRaises(ValueError):
            uniform_cap_counts((1,)*5)


if __name__=="__main__":
    unittest.main()
