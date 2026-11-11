"""BM-40 exact Hellinger brackets, histogram combinatorics, iid risks."""
import unittest
from fractions import Fraction
from math import comb

from robust_sequential_visibility_BM40 import (
    exact_histogram_laws,exact_histogram_tv,
    certified_finite_affinity,certified_asymptotic_affinity,
    episodes_for_risk_upper,iid_bayes_error_upper,
    theorem_receipt,_sqrt_interval,
)
from replication_uniform_upper_BM27 import (
    exact_clean_law,explicit_mask_law,xor_convolve,
)
from exact_graded_visibility_BM39 import graded_total_variation


def explicit_hist(n,law):
    out={}
    for report,p in law.items():
        c=[0,0,0,0]
        for j in range(n):
            c[(report>>(2*j))&3]+=1
        key=(tuple(c),(report>>(2*n))&3)
        out[key]=out.get(key,Fraction())+p
    return out


class BM40SequentialTests(unittest.TestCase):
    def test_histogram_law_equals_independent_full_census(self):
        for n in (1,2,3):
            for lam in (Fraction(0),Fraction(1,2),Fraction(1)):
                p0,p1=exact_histogram_laws(n,lam)
                for h,derived in ((0,p0),(1,p1)):
                    mask=explicit_mask_law(n,h)
                    q={k:(1-lam)*mask.get(k,0)+(lam if k==0 else 0)
                       for k in mask.keys()|{0}}
                    direct=xor_convolve(exact_clean_law(n,h),q)
                    self.assertEqual(derived,explicit_hist(n,direct))
                self.assertEqual(exact_histogram_tv(n,lam),
                                 graded_total_variation(n,lam))

    def test_integer_sqrt_bound_is_exact_with_monotone_envelope(self):
        scale=10**12
        self.assertEqual(_sqrt_interval(Fraction(1,4),scale),
                         (scale//2,scale//2))
        lo,hi=_sqrt_interval(Fraction(1,3),scale)
        self.assertLessEqual(Fraction(lo,scale)**2,Fraction(1,3))
        self.assertGreaterEqual(Fraction(hi,scale)**2,Fraction(1,3))
        self.assertLessEqual(hi-lo,1)
        with self.assertRaises(ValueError):
            _sqrt_interval(Fraction(-1,3),scale)

    def test_eraser_exact_affinity_one_and_no_finite_episode_bound(self):
        for n in (1,2,17):
            r=certified_finite_affinity(n,Fraction(0))
            self.assertEqual(r.affinity_lower,1)
            self.assertEqual(r.affinity_upper,1)
            self.assertEqual(r.exact_tv,0)
        self.assertIsNone(episodes_for_risk_upper(Fraction(1)))
        self.assertEqual(iid_bayes_error_upper(Fraction(1),100),Fraction(1,2))

    def test_positive_finite_BC_and_monotonicity(self):
        rs=[certified_finite_affinity(n,Fraction(1,2),digits=20)
            for n in (1,4,8,17,25)]
        for a,b in zip(rs,rs[1:]):
            self.assertGreater(a.affinity_lower,b.affinity_upper)
        lo,hi=certified_asymptotic_affinity(Fraction(1,2),digits=20)
        self.assertGreater(rs[-1].affinity_lower,hi)
        self.assertLess(rs[-1].affinity_upper,1)
        self.assertEqual(rs[-1].histogram_states,comb(28,3)*4)
        self.assertEqual(rs[-1].exact_tv,
                         graded_total_variation(25,Fraction(1,2)))

    def test_bound_on_fresh_episode_count_and_risk(self):
        r=certified_finite_affinity(25,Fraction(1,2),digits=22)
        self.assertEqual(episodes_for_risk_upper(r.affinity_upper,Fraction(1,3)),90)
        m=episodes_for_risk_upper(r.affinity_upper,Fraction(1,20))
        self.assertEqual(m,511)
        self.assertGreaterEqual(m,500)
        self.assertLessEqual(m,520)
        self.assertLessEqual(iid_bayes_error_upper(r.affinity_upper,m),
                             Fraction(1,20))
        self.assertGreater(iid_bayes_error_upper(r.affinity_upper,m-1),
                           Fraction(1,20))
        self.assertGreater(
            episodes_for_risk_upper(r.affinity_upper,Fraction(1,20)),
            episodes_for_risk_upper(r.affinity_upper,Fraction(1,3)),
        )

    def test_asymptotic_affinity_and_receipt(self):
        lo,hi=certified_asymptotic_affinity(Fraction(1,2))
        self.assertLess(hi-lo,Fraction(1,10**17))
        self.assertGreater(lo,Fraction(99,100))
        full=certified_finite_affinity(25,Fraction(1),digits=22)
        self.assertEqual(episodes_for_risk_upper(full.affinity_upper,Fraction(1,3)),13)
        self.assertEqual(episodes_for_risk_upper(full.affinity_upper,Fraction(1,20)),72)
        r=theorem_receipt(25,Fraction(1,2),digits=20)
        self.assertEqual(r["n"],25)
        self.assertEqual(r["lambda"],"1/2")
        self.assertTrue(r["fresh_iid_episode_requirement"])
        self.assertFalse(r["history_adaptive_attacker_guarantee"])
        for n,lam in ((33,Fraction(1,2)),(1,Fraction(-1,2))):
            with self.assertRaises(ValueError):
                certified_finite_affinity(n,lam)


if __name__=="__main__":
    unittest.main()
