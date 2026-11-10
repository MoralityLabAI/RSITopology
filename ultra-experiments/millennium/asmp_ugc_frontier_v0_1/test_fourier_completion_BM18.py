"""BM-18 exact rational universal completion and optimal noise LP tests."""
from fractions import Fraction
from itertools import product
from math import comb
import unittest

from fourier_completion_BM18 import (
    radial_lp,krawtchouk_ratio,check_radial_primal,check_radial_dual,
    fair_hitting_noise,sharp_radial_fixture,verify_sharp_radial,
    radial_mask_law,mask_marginals,xor_convolve_masks,
    convolve_clean,postprocess_primal,completion_bound,manifest,
)
from generic_fourier_erasure_BM17 import (
    Pair,Primal,census,check_primal,signed_walsh,
)
from k4_high_degree_BM17 import k4_pair, DEGREE_PRIMALS
from finite_seed import Game
from diamond_weighted_fourier_BM10 import EDGES as D_EDGES,SHIFT as D_SHIFT
from theta_shared_cycle_erasure import THETA_EDGES,THETA_SHIFTS
from sparse_fourier_degree_BM13 import primal_for_fourier_degree
from sharp_erasure_optimality import critical_erasure_cap


def _registered_pair(kind):
    if kind=="diamond":
        edges,shifts,vertices=D_EDGES,D_SHIFT,4
    elif kind=="theta":
        edges,shifts,vertices=THETA_EDGES,THETA_SHIFTS,5
    else:
        raise ValueError("unknown finite graph")
    return Pair(
        Game(vertices,2,tuple((u,v,0) for u,v in edges)),
        Game(vertices,2,tuple((u,v,s) for (u,v),s in zip(edges,shifts))),
    )


def _degree_witness(kind,degree):
    masks,den=primal_for_fourier_degree(kind,degree)
    p=_registered_pair(kind)
    eta=max(
        Fraction(sum(w for x,w in masks.items() if x&(1<<i)),den)
        for i in range(p.m)
    )
    return p,Primal(den,masks,masks,eta)


def _cycle_pair(m):
    edges=tuple((i,(i+1)%m) for i in range(m))
    return Pair(
        Game(m,2,tuple((u,v,0) for u,v in edges)),
        Game(m,2,tuple((u,v,1 if i==m-1 else 0)
                       for i,(u,v) in enumerate(edges))),
    )


class FourierCompletionTests(unittest.TestCase):
    def test_all_hitting_masks_erase_all_high_degree_characters(self):
        for m in range(1,9):
            for d in range(m+1):
                weights=fair_hitting_noise(m,d)
                r=check_radial_primal(m,d,weights)
                self.assertEqual(r,Fraction(m-d,2*m))
                law=radial_mask_law(m,weights)
                self.assertEqual(sum(law.values()),1)
                self.assertEqual(mask_marginals(m,law),(r,)*m)
                for s in range(d+1,m+1):
                    self.assertEqual(
                        sum((p*((-1)**(mask&((1<<s)-1)).bit_count())
                             for mask,p in law.items()),Fraction(0)),0)

    def test_normalized_Krawtchouk_matches_independent_weight_orbits(self):
        for m in range(1,9):
            for s,t in product(range(m+1),repeat=2):
                direct=Fraction(
                    sum((-1 if (mask&((1<<s)-1)).bit_count()%2 else 1)
                        for mask in range(1<<m) if mask.bit_count()==t),
                    comb(m,t),
                )
                self.assertEqual(krawtchouk_ratio(m,s,t),direct)

    def test_universal_sharp_near_top_duals_for_all_m_up_to_20(self):
        for m in range(1,21):
            self.assertEqual(verify_sharp_radial(m,m-1),Fraction(1,2*m))
            self.assertEqual(verify_sharp_radial(m,m),0)
            self.assertEqual(verify_sharp_radial(m,0),Fraction(1,2))
            if m>=2:
                self.assertEqual(verify_sharp_radial(m,m-2),Fraction(1,m))

    def test_improved_radial_LP_fixtures_with_exact_primal_dual(self):
        expected={
            (5,2):Fraction(1,4),
            (6,3):Fraction(5,24),
            (7,4):Fraction(1,6),
            (8,4):Fraction(5,26),
        }
        for (m,d),optimum in expected.items():
            p,y=sharp_radial_fixture(m,d)
            lp=radial_lp(m,d)
            self.assertEqual(lp.variables,m+1)
            self.assertEqual(lp.rows,m-d+1)
            self.assertEqual(len(lp.equalities),m-d+1)
            self.assertEqual(check_radial_primal(m,d,p),optimum)
            self.assertEqual(check_radial_dual(m,d,y),optimum)
            self.assertLess(optimum,check_radial_primal(
                m,d,fair_hitting_noise(m,d)))
        self.assertEqual(manifest()["improved_fixtures"][0]["optimum"],"1/4")

    def test_postprocess_K4_degree_five_masks_to_full_erasure(self):
        pair=k4_pair()
        witness=DEGREE_PRIMALS[5]
        self.assertEqual(witness.eta,Fraction(4,19))
        self.assertTrue(check_primal(pair,5,witness))
        actual,bound=postprocess_primal(pair,5,witness,fair_hitting_noise(6,5))
        self.assertEqual(bound,Fraction(59,228))
        self.assertLessEqual(actual,bound)
        self.assertGreaterEqual(actual,DEGREE_PRIMALS[6].eta)
        self.assertEqual(completion_bound(6,5,Fraction(4,19)),bound)

    def test_improved_K4_completion_at_degree_three(self):
        pair=k4_pair()
        witness=DEGREE_PRIMALS[3]
        improved,_=sharp_radial_fixture(6,3)
        actual,bound=postprocess_primal(pair,3,witness,improved)
        self.assertEqual(bound,Fraction(11,36))
        self.assertLessEqual(actual,bound)
        self.assertLess(bound,completion_bound(6,3,Fraction(1,6)))
        self.assertGreaterEqual(actual,DEGREE_PRIMALS[6].eta)

    def test_postprocess_diamond_theta_truncated_fourier_witnesses(self):
        for kind,degree in (("diamond",3),("theta",4)):
            pair,witness=_degree_witness(kind,degree)
            self.assertTrue(check_primal(pair,degree,witness))
            actual,bound=postprocess_primal(
                pair,degree,witness,fair_hitting_noise(pair.m,degree)
            )
            want=(Fraction(3,10) if kind=="diamond"
                  else Fraction(1,4))
            self.assertEqual(bound,want)
            self.assertLessEqual(actual,bound)
            self.assertGreaterEqual(actual,(
                Fraction(1,5) if kind=="diamond" else Fraction(1,6)
            ))

    def test_isolated_q4_cycle_sharpness_of_final_degree_universal_bound(self):
        for m in range(2,7):
            pair=_cycle_pair(m)
            initial=Primal(1,{0:1},{0:1},Fraction(0))
            self.assertTrue(check_primal(pair,m-1,initial))
            actual,bound=postprocess_primal(
                pair,m-1,initial,fair_hitting_noise(m,m-1)
            )
            self.assertEqual(actual,Fraction(1,2*m))
            self.assertEqual(bound,critical_erasure_cap(4,m))
            self.assertEqual(actual,bound)

    def test_postprocess_convolution_and_character_independence(self):
        m=5
        source={0:Fraction(1,2),3:Fraction(1,2)}
        fair=radial_mask_law(m,fair_hitting_noise(m,3))
        out=xor_convolve_masks(m,source,fair)
        self.assertEqual(sum(out.values()),1)
        r=Fraction(1,5)
        original=mask_marginals(m,source)
        expected=tuple(p+r*(1-2*p) for p in original)
        self.assertEqual(mask_marginals(m,out),expected)
        for S in range(1<<m):
            if S.bit_count()>3:
                self.assertEqual(sum(
                    (v*(-1)**((mask&S).bit_count()) for mask,v in out.items()),
                    Fraction(0)
                ),0)

    def test_additive_epsilon_bound_is_explicit_and_matched_in_cycle(self):
        m=12
        d=9
        epsilon=Fraction(m-d,2*m)
        self.assertEqual(epsilon,Fraction(1,8))
        self.assertEqual(completion_bound(m,d,Fraction(0)),epsilon)
        self.assertEqual(completion_bound(m,d,Fraction(1,4)),
                         Fraction(1,4)+epsilon/2)
        self.assertEqual(completion_bound(m,m,Fraction(1,4)),Fraction(1,4))
        self.assertLessEqual(completion_bound(m,d,Fraction(1,4))
                             -Fraction(1,4),epsilon)

    def test_invalid_LP_mask_and_certificate_contracts(self):
        with self.assertRaises(ValueError):
            radial_lp(0,0)
        with self.assertRaises(ValueError):
            radial_lp(5,6)
        with self.assertRaises(ValueError):
            krawtchouk_ratio(3,4,1)
        with self.assertRaises(ValueError):
            check_radial_primal(5,2,(Fraction(1),))
        with self.assertRaises(AssertionError):
            check_radial_primal(5,2,fair_hitting_noise(5,3))
        with self.assertRaises(ValueError):
            check_radial_dual(5,2,(Fraction(0),))
        with self.assertRaises(AssertionError):
            check_radial_dual(5,2,(Fraction(1),0,0,0))
        with self.assertRaises(KeyError):
            sharp_radial_fixture(9,3)
        with self.assertRaises(ValueError):
            completion_bound(5,3,Fraction(3,4))
        with self.assertRaises(ValueError):
            radial_mask_law(13,fair_hitting_noise(13,12))
        with self.assertRaises(ValueError):
            mask_marginals(2,{0:Fraction(2)})
        with self.assertRaises(ValueError):
            xor_convolve_masks(2,{0:Fraction(1)},{4:Fraction(1)})


if __name__ == "__main__":
    unittest.main()
