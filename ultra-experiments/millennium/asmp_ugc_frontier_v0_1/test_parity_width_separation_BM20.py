"""BM-20 exact treewidth separation, hostility and rational sparsification controls."""
from fractions import Fraction
from itertools import product
from math import lcm
from random import Random
import unittest

from parity_width_separation_BM20 import (
    ParityFactor,SeparationReceipt,parity_factors,min_fill_order,
    exact_separate,direct_slack,brute_separate,verify_dual_fast,
    moment_fingerprint,sparsify_mask_law,
    bipartite_pair_support_certificate,
)
from support_aware_completion_BM19 import (
    PostprocessorPrimal,PostprocessorDual,
    verify_postprocessor_dual,verify_postprocessor_primal,
)
from support_aware_fixtures_BM19 import FIXTURES,frozen_partial


def independent_fingerprint(m,support,law):
    return (
        (sum(law.values(),Fraction(0)),)+
        tuple(sum((p*(-1 if (mask&S).bit_count()%2 else 1)
                   for mask,p in law.items()),Fraction(0)) for S in support)+
        tuple(sum((p for mask,p in law.items() if mask&(1<<i)),Fraction(0))
              for i in range(m))
    )


def integer_witness(law):
    D=lcm(*(p.denominator for p in law.values()))
    return PostprocessorPrimal(D,{
        mask:int(p*D) for mask,p in law.items() if p
    })


class ParityWidthSeparationTests(unittest.TestCase):
    def test_all_existing_BM19_duals_match_exhaustive_mask_enumeration(self):
        for key,(D,optimum,upper,proof) in FIXTURES.items():
            m=frozen_partial(*key)[0].m
            dp=exact_separate(m,D,proof)
            naive,mask=brute_separate(m,D,proof)
            self.assertEqual(dp.maximum,naive)
            self.assertEqual(naive,0)
            self.assertEqual(dp.maximum,direct_slack(
                m,D,proof,dp.maximizing_mask))
            self.assertTrue(dp.feasible)
            self.assertEqual(verify_dual_fast(m,D,proof),optimum)
            self.assertEqual(verify_postprocessor_dual(m,D,proof),optimum)
            self.assertLessEqual(dp.max_join_scope,m)
            self.assertGreater(dp.candidate_assignments,0)

    def test_mutated_K4_dual_returns_actual_violating_error_mask(self):
        D,optimum,upper,proof=FIXTURES[("k4",4)]
        counterfeit=PostprocessorDual(
            proof.normalization+Fraction(1,1000),
            dict(proof.characters),proof.marginal_multipliers
        )
        result=exact_separate(6,D,counterfeit)
        self.assertEqual(result.maximum,Fraction(1,1000))
        self.assertFalse(result.feasible)
        self.assertEqual(direct_slack(
            6,D,counterfeit,result.maximizing_mask),result.maximum)
        with self.assertRaises(AssertionError):
            verify_dual_fast(6,D,counterfeit)

    def test_random_signed_parity_CSPs_equal_independent_full_search(self):
        rng=Random(20261110)
        for m in range(2,9):
            for trial in range(7):
                indices=list(range(1,1<<m))
                rng.shuffle(indices)
                D=tuple(sorted(indices[:rng.randint(1,min(8,len(indices)))]))
                active={S:Fraction(rng.choice((-3,-2,-1,1,2,3)),12)
                        for S in D}
                z=[Fraction(0)]*m
                touched=rng.sample(range(m),rng.randint(1,m))
                weights=[rng.randint(1,5) for _ in touched]
                total=sum(weights)
                for i,weight in zip(touched,weights):
                    z[i]=-Fraction(weight,total)
                proof=PostprocessorDual(
                    Fraction(rng.randint(-5,5),12),active,tuple(z)
                )
                dp=exact_separate(m,D,proof,max_factor_bits=8)
                exhaustive,mask=brute_separate(m,D,proof)
                self.assertEqual(dp.maximum,exhaustive)
                self.assertEqual(direct_slack(
                    m,D,proof,dp.maximizing_mask),exhaustive)
                reverse=exact_separate(
                    m,D,proof,order=tuple(reversed(range(m))),max_factor_bits=8
                )
                self.assertEqual(reverse.maximum,exhaustive)

    def test_bipartite_graph_exact_quarter_certificate_and_small_support(self):
        for m,edges in (
            (2,((0,1),)),
            (4,((0,1),(1,2),(2,3))),
            (8,tuple((i,i+1) for i in range(7))),
            (12,tuple((0,i) for i in range(1,12))),
        ):
            D,R,proof=bipartite_pair_support_certificate(m,edges)
            self.assertLessEqual(len(R),3)
            self.assertEqual(moment_fingerprint(m,D,R),
                             independent_fingerprint(m,D,R))
            self.assertEqual(moment_fingerprint(m,D,R)[0],1)
            self.assertTrue(all(moment_fingerprint(m,D,R)[j]==0
                                for j in range(1,1+len(D))))
            self.assertEqual(
                moment_fingerprint(m,D,R)[1+len(D):],
                (Fraction(1,4),)*m,
            )
            self.assertEqual(
                verify_postprocessor_primal(m,D,integer_witness(R)),
                Fraction(1,4),
            )
            self.assertEqual(verify_dual_fast(m,D,proof),Fraction(1,4))
            dp=exact_separate(m,D,proof)
            self.assertEqual(dp.maximum,0)
            self.assertLessEqual(dp.induced_width,1)
            if m<=8:
                self.assertEqual(brute_separate(m,D,proof)[0],0)

    def test_long_path_full_active_dual_uses_only_width_one_factors(self):
        m=128
        D=tuple((1<<i)|(1<<(i+1)) for i in range(m-1))
        z=(Fraction(-1,m),)*m
        weights={S:Fraction(1,200) for S in D}
        proof=PostprocessorDual(Fraction(0),weights,z)
        dp=exact_separate(
            m,D,proof,order=tuple(range(m)),max_factor_bits=3
        )
        self.assertEqual(dp.maximum,Fraction(m-1,200))
        self.assertEqual(dp.max_join_scope,2)
        self.assertEqual(dp.induced_width,1)
        self.assertEqual(dp.maximizing_mask,0)
        self.assertLess(dp.candidate_assignments,8*m)
        self.assertFalse(dp.feasible)
        self.assertEqual(direct_slack(m,D,proof,0),
                         Fraction(m-1,200))

    def test_frozen_chain_dual_with_256_readout_bits_needs_no_enumeration(self):
        m=256
        D=tuple((1<<i)|(1<<(i+1)) for i in range(m-1))
        z=[Fraction(0)]*m
        z[0]=z[1]=Fraction(-1,2)
        proof=PostprocessorDual(
            Fraction(1,4),{D[0]:Fraction(-1,4)},tuple(z)
        )
        receipt=exact_separate(
            m,D,proof,order=tuple(range(m)),max_factor_bits=3
        )
        self.assertEqual(receipt.maximum,0)
        self.assertEqual(receipt.induced_width,1)
        self.assertTrue(receipt.feasible)
        self.assertEqual(verify_dual_fast(
            m,D,proof,order=tuple(range(m)),max_factor_bits=3
        ),Fraction(1,4))
        self.assertLess(receipt.candidate_assignments,8*m)

    def test_affine_sparsifier_preserves_all_moments_with_fewer_atoms(self):
        m=4
        D=(3,12)
        first={0:Fraction(1,2),1:Fraction(1,4),2:Fraction(1,4)}
        second={0:Fraction(1,2),4:Fraction(1,4),8:Fraction(1,4)}
        dense={a|b:pa*pb for a,pa in first.items()
               for b,pb in second.items()}
        self.assertEqual(len(dense),9)
        reduced=sparsify_mask_law(m,D,dense)
        self.assertLessEqual(len(reduced),1+len(D)+m)
        self.assertLess(len(reduced),len(dense))
        self.assertEqual(independent_fingerprint(m,D,dense),
                         independent_fingerprint(m,D,reduced))
        self.assertEqual(moment_fingerprint(m,D,reduced),
                         independent_fingerprint(m,D,dense))
        self.assertEqual(
            verify_postprocessor_primal(m,D,integer_witness(reduced)),
            Fraction(1,4)
        )

    def test_affine_sparsifier_works_for_dense_64_atom_rational_law(self):
        m=6
        D=(3,12,48)
        dense={mask:Fraction(1,64) for mask in range(1<<m)}
        before=independent_fingerprint(m,D,dense)
        reduced=sparsify_mask_law(m,D,dense)
        self.assertLessEqual(len(reduced),1+len(D)+m)
        self.assertEqual(independent_fingerprint(m,D,reduced),before)
        self.assertEqual(moment_fingerprint(m,D,reduced),before)
        self.assertEqual(sum(reduced.values()),1)
        self.assertEqual(
            verify_postprocessor_primal(m,D,integer_witness(reduced)),
            Fraction(1,2)
        )

    def test_min_fill_width_and_empty_factor_controls(self):
        m=8
        path=tuple((i,i+1) for i in range(m-1))
        scopes=tuple((u,v) for u,v in path)
        order=min_fill_order(m,scopes)
        self.assertEqual(len(order),m)
        self.assertEqual(set(order),set(range(m)))
        support=tuple((1<<u)|(1<<v) for u,v in path)
        z=[Fraction(0)]*m
        z[0]=z[1]=Fraction(-1,2)
        proof=PostprocessorDual(Fraction(1,4),{support[0]:Fraction(-1,4)},tuple(z))
        self.assertEqual(exact_separate(m,support,proof).maximum,0)
        empty=PostprocessorDual(Fraction(0),{},(Fraction(-1),)+(0,)*(m-1))
        self.assertEqual(exact_separate(m,(),empty).maximum,0)
        self.assertEqual(exact_separate(m,(),empty).max_join_scope,1)

    def test_reject_hyperedge_too_wide_and_invalid_certificates(self):
        m=8
        high=(1<<m)-1
        proof=PostprocessorDual(Fraction(0),{high:Fraction(1,2)},
                                (Fraction(-1),)+(0,)*(m-1))
        with self.assertRaises(ValueError):
            exact_separate(m,(high,),proof,max_factor_bits=5)
        with self.assertRaises(ValueError):
            exact_separate(m,(high,),proof,order=(0,1))
        with self.assertRaises(ValueError):
            exact_separate(m,(high,),proof,order=tuple(range(7))+(0,))
        with self.assertRaises(ValueError):
            exact_separate(m,(high,),proof,order=tuple(range(8)),
                           max_factor_bits=6)
        with self.assertRaises(ValueError):
            exact_separate(m,(3,),proof)
        with self.assertRaises(ValueError):
            exact_separate(m,(3,3),proof)
        with self.assertRaises(ValueError):
            bipartite_pair_support_certificate(3,((0,1),(1,2),(2,0)))
        with self.assertRaises(ValueError):
            bipartite_pair_support_certificate(2,((0,0),))
        with self.assertRaises(ValueError):
            sparsify_mask_law(4,(3,),{0:Fraction(2)})
        with self.assertRaises(ValueError):
            min_fill_order(4,((1,5),))


if __name__=="__main__":
    unittest.main()
