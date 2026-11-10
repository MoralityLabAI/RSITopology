"""BM-17: K4 exact Fourier-degree erasure certificate regression suite.

Every certified value has independently reconstructed exact integer clean
pattern counts, rational primal mask distributions, and dual inequalities.
The source graph has treewidth three and has no BM-14 parallel-path
permutation-symmetry reduction.
"""
from fractions import Fraction
from itertools import combinations
import unittest

from k4_high_degree_BM17 import (
    EDGES, FLAT_GAINS, OTHER_GAINS,
    DEGREE_PRIMALS, DEGREE_DUALS,
    DEGREE_ZERO_PRIMAL, DEGREE_ZERO_DUAL,
    k4_pair, degree_receipt, degree_certificate,
)
from generic_fourier_erasure_BM17 import (
    Pair, Primal, Dual, census, signed_walsh, queried_subsets,
    mask_walsh, mask_marginals, output_counts,
    check_primal, check_dual, certify,
)
from separator_factor_transfer_BM16 import exact_walsh
from sharp_erasure_optimality import critical_erasure_cap
from diamond_weighted_fourier_BM10 import verify_full_primal as diamond_primal


class K4HighDegreeTests(unittest.TestCase):
    def test_all_seven_levels_match_exact_primal_and_dual(self):
        model=k4_pair()
        expected=(Fraction(0),Fraction(0),Fraction(0),Fraction(1,6),
                  Fraction(1,5),Fraction(4,19),Fraction(3,14))
        records=[]
        for d,want in enumerate(expected):
            primal,dual=degree_certificate(d)
            cert=certify(model,d,primal,dual)
            records.append(cert.optimum)
            self.assertEqual(cert.degree,d)
            self.assertEqual(cert.optimum,want)
            self.assertEqual(cert.checked_mask_inequalities,128)
            self.assertTrue(cert.primal_valid and cert.dual_valid)
            self.assertEqual(cert.full_output_equal,d==6)
        self.assertEqual(tuple(records),expected)

    def test_K4_all_Fourier_coefficients_agree_with_independent_BM16_eliminator(self):
        p=k4_pair()
        for g in (p.flat,p.other):
            counts=census(g)
            for S in range(64):
                self.assertEqual(signed_walsh(counts,S),exact_walsh(g,S))
        self.assertEqual(sum(census(p.flat)),4**4)
        self.assertEqual(sum(census(p.other)),4**4)
        self.assertNotEqual(census(p.flat),census(p.other))

    def test_all_four_triangles_frustrated_two_cycles_over_F2_squared(self):
        shifts=OTHER_GAINS
        triangles=tuple(combinations(range(4),3))
        for triangle in triangles:
            sub_edges=tuple(
                i for i,(u,v) in enumerate(EDGES) if u in triangle and v in triangle
            )
            self.assertEqual(len(sub_edges),3)
            self.assertNotEqual(
                shifts[sub_edges[0]]^shifts[sub_edges[1]]^shifts[sub_edges[2]],0
            )
        self.assertEqual(k4_pair().m,6)

    def test_degree_five_is_a_strict_but_valid_relaxation(self):
        p=k4_pair()
        primal=DEGREE_PRIMALS[5]
        clean=(census(p.flat),census(p.other))
        self.assertTrue(check_primal(p,5,primal,counts=clean))
        self.assertEqual(check_dual(p,5,DEGREE_DUALS[5],counts=clean),
                         Fraction(4,19))
        obs0=output_counts(clean[0],primal.q0)
        obs1=output_counts(clean[1],primal.q1)
        self.assertNotEqual(obs0,obs1)
        self.assertNotEqual(signed_walsh(obs0,63),signed_walsh(obs1,63))
        for s in range(1,64):
            if s.bit_count()<=5:
                self.assertEqual(signed_walsh(obs0,s),signed_walsh(obs1,s))

    def test_full_degree_six_is_sharp_and_common_channel_witness(self):
        p=k4_pair()
        cp=DEGREE_PRIMALS[6]
        self.assertEqual(cp.q0,cp.q1)
        self.assertEqual(cp.denominator,56)
        self.assertEqual(sum(cp.q0.values()),56)
        self.assertEqual(mask_marginals(cp.q0,56,6),
                         (Fraction(3,14),)*6)
        c0,c1=census(p.flat),census(p.other)
        self.assertEqual(output_counts(c0,cp.q0),output_counts(c1,cp.q1))
        self.assertEqual(check_dual(p,6,DEGREE_DUALS[6]),Fraction(3,14))

    def test_all_dual_supports_respect_degree_and_verified_marginal_signs(self):
        for degree in (3,4,5,6):
            dual=DEGREE_DUALS[degree]
            self.assertTrue(all(s.bit_count()<=degree and s>0
                                for s in dual.walsh_numerators))
            self.assertTrue(all(v<=0 for v in dual.marginal_numerators))
            self.assertEqual(
                -sum(dual.marginal_numerators),dual.marginal_denominator
            )
            self.assertEqual(Fraction(sum(dual.normalization_numerators),
                                      dual.walsh_denominator),
                             DEGREE_PRIMALS[degree].eta)

    def test_max_cycle_projection_gap_and_preexisting_diamond_control(self):
        self.assertTrue(diamond_primal())
        isolated=critical_erasure_cap(4,3)
        self.assertEqual(isolated,Fraction(1,6))
        self.assertEqual(DEGREE_PRIMALS[6].eta/isolated,Fraction(9,7))
        self.assertGreater(DEGREE_PRIMALS[6].eta,Fraction(1,5))
        self.assertGreater(DEGREE_PRIMALS[6].eta,DEGREE_PRIMALS[5].eta)
        self.assertEqual(DEGREE_PRIMALS[6].eta-DEGREE_PRIMALS[5].eta,
                         Fraction(1,266))

    def test_exact_certification_rejects_mutated_primal_and_dual(self):
        p=k4_pair()
        witness=DEGREE_PRIMALS[6]
        q0=dict(witness.q0)
        q0[0]-=1
        q0[1]+=1
        with self.assertRaises(AssertionError):
            check_primal(p,6,Primal(56,q0,witness.q1,witness.eta))
        dual=DEGREE_DUALS[6]
        forged=Dual(
            dual.walsh_denominator,dual.walsh_numerators,
            (dual.normalization_numerators[0]+1,
             dual.normalization_numerators[1]),
            dual.marginal_denominator,dual.marginal_numerators,
        )
        with self.assertRaises(AssertionError):
            certify(p,6,witness,forged)
        with self.assertRaises(ValueError):
            check_dual(p,5,dual)

    def test_generic_lp_and_fixture_input_guards(self):
        p=k4_pair()
        with self.assertRaises(ValueError):
            Pair(p.flat, type(p.other)(5,2,p.other.edges))
        with self.assertRaises(ValueError):
            degree_certificate(7)
        with self.assertRaises(ValueError):
            queried_subsets(6,7)
        with self.assertRaises(ValueError):
            signed_walsh((2,3,4),1)
        with self.assertRaises(ValueError):
            check_primal(p,6,Primal(1,{0:2},{0:1},Fraction(0)))
        with self.assertRaises(ValueError):
            check_dual(p,6,Dual(1,{},(0,0),1,(0,)*12))
        self.assertEqual(len(queried_subsets(6,5)),62)

    def test_receipt_matches_exact_level_results(self):
        record=degree_receipt()
        self.assertEqual(tuple(record.keys()),tuple(range(7)))
        self.assertEqual(record[3]["optimum"],"1/6")
        self.assertEqual(record[4]["optimum"],"1/5")
        self.assertEqual(record[5]["optimum"],"4/19")
        self.assertEqual(record[6]["optimum"],"3/14")
        self.assertTrue(record[6]["full_output_equal"])
        self.assertFalse(record[5]["full_output_equal"])


if __name__ == "__main__":
    unittest.main()
