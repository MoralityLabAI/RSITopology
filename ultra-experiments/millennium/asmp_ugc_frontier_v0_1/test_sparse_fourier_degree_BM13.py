"""BM-13: exact sparse Fourier certificates and locality-degree hierarchy."""
from fractions import Fraction
from itertools import product
import unittest

from sparse_fourier_degree_BM13 import (
    DIAMOND_DUAL_WALSH,THETA_DUAL_WALSH,
    dual_certificate,sparse_dual_slacks,verify_sparse_dual,
    primal_for_fourier_degree,verify_truncated_primal,
    truncated_degree_profile,sparse_manifest,
)
from diamond_weighted_fourier_BM10 import (
    verify_full_primal as diamond_full_primal,
    verify_full_dual as diamond_old_dual,
    DUAL_WALSH as old_diamond_walsh,
)
from theta_shared_cycle_erasure import verify_q4_primal,verify_q4_lower_lemma
from sharp_erasure_optimality import critical_erasure_cap


class SparseFourierDegreeTests(unittest.TestCase):
    def test_small_five_term_theta_dual_proves_sixth_and_fifth_degree(self):
        self.assertTrue(verify_q4_primal() and verify_q4_lower_lemma())
        self.assertEqual(set(THETA_DUAL_WALSH),{15,51,60,31,47})
        self.assertEqual(len(THETA_DUAL_WALSH),5)
        self.assertEqual(max(s.bit_count() for s in THETA_DUAL_WALSH),5)
        self.assertEqual(verify_sparse_dual("theta"),Fraction(1,6))
        slacks=sparse_dual_slacks("theta")
        self.assertEqual(tuple(map(len,slacks)),(64,64))
        self.assertEqual(max(max(row) for row in slacks),0)
        self.assertTrue(any(v<0 for row in slacks for v in row))

    def test_diamond_8_term_dual_replaces_prior_17_term_certificate(self):
        self.assertTrue(diamond_full_primal() and diamond_old_dual())
        self.assertEqual(len(old_diamond_walsh),17)
        self.assertEqual(len(DIAMOND_DUAL_WALSH),8)
        self.assertEqual(verify_sparse_dual("diamond"),Fraction(1,5))
        self.assertEqual(max(s.bit_count() for s in DIAMOND_DUAL_WALSH),4)
        slacks=sparse_dual_slacks("diamond")
        self.assertEqual(tuple(map(len,slacks)),(32,32))
        self.assertEqual(max(max(row) for row in slacks),0)

    def test_exact_fourier_degree_profiles_all_cutoffs(self):
        self.assertEqual(truncated_degree_profile("diamond"),(
            0,0,0,Fraction(1,6),Fraction(1,5),Fraction(1,5)))
        self.assertEqual(truncated_degree_profile("theta"),(
            0,0,0,0,Fraction(1,8),Fraction(1,6),Fraction(1,6)))
        self.assertEqual(critical_erasure_cap(4,3),Fraction(1,6))
        self.assertEqual(critical_erasure_cap(4,4),Fraction(1,8))
        self.assertEqual(max(s.bit_count() for s in dual_certificate("diamond")[1]),4)
        self.assertEqual(max(s.bit_count() for s in dual_certificate("theta")[1]),5)

    def test_low_degree_witness_fails_at_the_next_required_degree(self):
        from sparse_fourier_degree_BM13 import _hats
        for graph,degree,new_degree in (("diamond",3,4),("theta",4,5)):
            m=5 if graph=="diamond" else 6
            masks,D=primal_for_fourier_degree(graph,degree)
            self.assertEqual(verify_truncated_primal(graph,degree),
                             critical_erasure_cap(4,3 if graph=="diamond" else 4))
            p0,p1=_hats(graph)
            offending=[
                S for S in range(1,1<<m) if S.bit_count()==new_degree
                and (p0[S]-p1[S])*sum(
                    (-1 if (mask&S).bit_count()%2 else 1)*v
                    for mask,v in masks.items()
                )!=0
            ]
            self.assertTrue(offending)

    def test_sparse_dual_inequalities_directly_by_independent_integer_fourier(self):
        from diamond_weighted_fourier_BM10 import clean_counts as diamond_counts
        from theta_shared_cycle_erasure import theta_laws
        for graph,counts in (
            ("diamond",diamond_counts()),("theta",theta_laws(4))
        ):
            norm,y,z=dual_certificate(graph)
            m=5 if graph=="diamond" else 6
            expected=[]
            for h in range(2):
                p=counts[h]
                n=sum(p)
                row=[]
                for mask in range(1<<m):
                    value=norm[h]
                    for subset,c in y.items():
                        hat=sum(
                            k * (1 if ((out&subset).bit_count()%2==0) else -1)
                            for out,k in enumerate(p)
                        )
                        value += (
                            (1 if h==0 else -1)*c*Fraction(hat,n)
                            *(1 if ((mask&subset).bit_count()%2==0) else -1)
                        )
                    value += sum(
                        (coef for edge,coef in z[h].items() if mask&(1<<edge)),
                        Fraction(0)
                    )
                    row.append(value)
                expected.append(tuple(row))
            self.assertEqual(tuple(expected),sparse_dual_slacks(graph))

    def test_manifest_and_invalid_contracts(self):
        manifest=sparse_manifest()
        self.assertEqual(manifest["diamond"]["dual_walsh_terms"],8)
        self.assertEqual(manifest["theta"]["dual_walsh_terms"],5)
        self.assertEqual(manifest["diamond"]["max_dual_degree"],4)
        self.assertEqual(manifest["theta"]["max_dual_degree"],5)
        self.assertEqual(manifest["theta"]["full_optimum"],"1/6")
        for bad in ("other","",None):
            with self.assertRaises(ValueError):
                verify_sparse_dual(bad)
        with self.assertRaises(ValueError):
            primal_for_fourier_degree("theta",7)
        with self.assertRaises(ValueError):
            primal_for_fourier_degree("diamond",-1)


if __name__=="__main__":
    unittest.main()
