"""BM-29 exact finite algebra controls for the asymptotic 5/52 theorem.

The proof's infinite exchangeability, compactness and measure
disintegration are written in the associated mathematical note.
These tests check every algebraic identity and sharp equality case
using exact rational arithmetic, plus independent finite-world mask
rigidity and full output compatibility from BM-25/BM-26/BM-27.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from infinite_replication_rigidity_BM29 import (
    LIMIT,ORD_COEFFICIENT,SPECIAL_COEFFICIENT,
    WEIGHTED_BOUND,U_THRESHOLD,
    pair_walsh,shared_clean_marginal_walsh,
    ordinary_pair_mask_coordinates,TwoLevelChain,
    low_u_overlap_certificate,isolated_high_u_certificate,
    weighted_limit_inequality,bm27_directing_atoms,
    verify_bm27_equality_case,theorem_receipt,
)
from replication_uniform_upper_BM27 import (
    PAIR_I,PAIR_A,PAIR_B,PAIR_E,
    explicit_mask_law,verify_convolution_identity,theorem_upper,
)
from state_aware_replication_BM25 import (
    expanded_full_mask_law as bm25_full_mask_law,
)
from state_aware_three_replica_BM26 import (
    full_mask_law as bm26_full_mask_law,
)
from repeated_gain_erasure_BM24 import gain_family
from fourier_completion_BM18 import convolve_clean
from generic_fourier_erasure_BM17 import census


def marginal(full_mask_law,ordinary_bits,exception_index=None):
    """Independent exact mask projection without any Fourier transforms."""
    ordinary_limit=(1<<ordinary_bits)-1
    result=defaultdict(lambda:Fraction(0))
    for mask,weight in full_mask_law.items():
        key=(mask&ordinary_limit,)
        if exception_index is not None:
            key+=(int(bool(mask&(1<<(ordinary_bits+exception_index)))),)
        result[key]+=weight
    return dict(result)


def signed_parity_measure_equation(atoms):
    """Independent finite atomic test of the infinite parity-flow equation."""
    def push(field,scale):
        out=defaultdict(lambda:Fraction(0))
        for a in atoms.values():
            out[(a["u"],a["w"]*scale)]+=a[field]
        return dict(out)
    lhs=defaultdict(lambda:Fraction(0))
    rhs=defaultdict(lambda:Fraction(0))
    for key,val in push("nu0",1).items():
        lhs[key]+=2*val
    for key,val in push("nu0",Fraction(1,2)).items():
        lhs[key]+=7*val
    for key,val in push("nu1",1).items():
        rhs[key]+=val
    for key,val in push("nu1",Fraction(1,2)).items():
        rhs[key]+=8*val
    return {key:lhs[key]-rhs[key] for key in lhs.keys()|rhs.keys()}


class InfiniteReplicationRigidityTests(unittest.TestCase):
    def test_pair_ordinary_and_special_Fourier_transform_exact(self):
        self.assertEqual(pair_walsh(PAIR_A),(1,Fraction(3,4),
                                            Fraction(3,4),1))
        self.assertEqual(pair_walsh(PAIR_B),(1,Fraction(3,4),
                                            Fraction(3,4),Fraction(1,2)))
        self.assertEqual(pair_walsh(PAIR_I),(1,1,1,1))
        self.assertEqual(pair_walsh(PAIR_E),(1,Fraction(1,2),
                                            Fraction(1,2),0))
        for pair in (PAIR_I,PAIR_A,PAIR_B,PAIR_E):
            u,w=ordinary_pair_mask_coordinates(pair)
            self.assertGreaterEqual(w,2*u-1)
            self.assertLessEqual(w,1)
        with self.assertRaises(ValueError):
            ordinary_pair_mask_coordinates((1,0,0,Fraction(-1)))
        with self.assertRaises(ValueError):
            ordinary_pair_mask_coordinates(
                (Fraction(1,2),Fraction(1,2),0,0)
            )
        with self.assertRaises(ValueError):
            pair_walsh((1,0,0))

    def test_shared_clean_ordinary_and_single_special_signals_positive(self):
        for n in (1,2,3,4):
            model=gain_family(n,2,q=8)
            for b in range(n+1):
                for r in range(n-b+1):
                    ordinary_hist=(n-b-r,b,r)
                    for special in (0,1):
                        exc=tuple(int(t==special) for t in range(3))
                        sig=(ordinary_hist,exc)
                        expected=shared_clean_marginal_walsh(
                            b,r,special
                        )
                        self.assertGreater(expected,0)
                        self.assertEqual(
                            model.clean_walsh_signature(0,sig),expected
                        )
                        self.assertEqual(
                            model.clean_walsh_signature(1,sig),expected
                        )
        with self.assertRaises(ValueError):
            shared_clean_marginal_walsh(1,1,2)

    def test_complete_equalizers_have_identical_ordinary_mask_marginals(self):
        examples=(
            (2,bm25_full_mask_law(0),bm25_full_mask_law(1)),
            (3,bm26_full_mask_law(0),bm26_full_mask_law(1)),
        )+tuple(
            (n,explicit_mask_law(n,0),explicit_mask_law(n,1))
            for n in (1,2,3)
        )
        for n,a,b in examples:
            self.assertEqual(marginal(a,2*n),marginal(b,2*n))
            for special_bit in (0,1):
                self.assertEqual(
                    marginal(a,2*n,special_bit),
                    marginal(b,2*n,special_bit)
                )
            self.assertNotEqual(a,b)

    def test_BM27_directing_measure_is_shared_and_has_exact_1_2_8_7_flow(self):
        atoms=bm27_directing_atoms()
        self.assertEqual(tuple(atoms),("I","A","B"))
        self.assertEqual(atoms["I"]["mu"],Fraction(3,13))
        self.assertEqual(atoms["A"]["mu"],Fraction(2,13))
        self.assertEqual(atoms["B"]["mu"],Fraction(8,13))
        self.assertEqual(atoms["A"]["w"],1)
        self.assertEqual(atoms["B"]["w"],Fraction(1,2))
        self.assertEqual(atoms["A"]["u"],Fraction(3,4))
        self.assertEqual(atoms["B"]["u"],Fraction(3,4))
        self.assertEqual(
            tuple(atoms["A"][k] for k in ("nu0","nu1")),
            (Fraction(1,13),Fraction(2,13)),
        )
        self.assertEqual(
            tuple(atoms["B"][k] for k in ("nu0","nu1")),
            (Fraction(8,13),Fraction(7,13)),
        )
        self.assertTrue(all(v==0 for v in
                            signed_parity_measure_equation(atoms).values()))

    def test_two_level_overlap_certificate_at_sharp_BM27_atom(self):
        a=bm27_directing_atoms()
        chain=TwoLevelChain(
            Fraction(3,4),Fraction(1),
            a["A"]["mu"],a["B"]["mu"],Fraction(1,13)
        )
        self.assertTrue(chain.check())
        self.assertEqual(chain.signed_nu,(
            Fraction(1,13),Fraction(2,13),
            Fraction(8,13),Fraction(7,13)
        ))
        self.assertEqual(chain.overlap,Fraction(8,13))
        self.assertEqual(
            chain.overlap,Fraction(4,5)*(chain.mu_high+chain.mu_low)
        )
        self.assertEqual(
            chain.overlap,
            Fraction(16,5)*(1-chain.u)*(chain.mu_high+chain.mu_low)
        )

    def test_high_u_two_level_random_rational_signed_atoms_satisfy_dual(self):
        rng=Random(20261110)
        for _ in range(120):
            u=Fraction(rng.randint(89,96),128) # >11/16, <=3/4
            minimum=2*u-1
            # w_H must satisfy w_H/2>=minimum, so choose w_H=1.
            c=Fraction(rng.choice((-1,1))*rng.randint(1,5),100)
            mu_high=2*abs(c)+Fraction(rng.randint(0,10),100)
            mu_low=8*abs(c)+Fraction(rng.randint(0,10),100)
            witness=TwoLevelChain(u,Fraction(1),mu_high,mu_low,c)
            self.assertTrue(witness.check())
            self.assertLessEqual(witness.overlap,
                                 Fraction(16,5)*(1-u)*
                                 (mu_high+mu_low))
        with self.assertRaises(ValueError):
            TwoLevelChain(Fraction(3,4),1,
                          Fraction(1,100),Fraction(1,10),
                          Fraction(1,50)).check()
        with self.assertRaises(ValueError):
            TwoLevelChain(Fraction(7,8),1,
                          Fraction(1,5),Fraction(1,5),
                          Fraction(0)).check()

    def test_low_u_or_isolated_high_u_measures_require_no_dyadic_pairing(self):
        for u in (Fraction(-1),Fraction(0),
                  Fraction(1,2),Fraction(11,16)):
            for mass in (Fraction(0),Fraction(1,5),Fraction(1)):
                self.assertTrue(low_u_overlap_certificate(
                    u,mass,mass
                ))
        for u in (Fraction(4,5),Fraction(1)):
            self.assertTrue(isolated_high_u_certificate(u,0,0))
        with self.assertRaises(ValueError):
            low_u_overlap_certificate(Fraction(3,4),1,1)
        with self.assertRaises(ValueError):
            isolated_high_u_certificate(Fraction(4,5),1,0)

    def test_weighted_cost_inequality_saturates_the_BM27_exact_mask(self):
        receipt=verify_bm27_equality_case()
        self.assertEqual(receipt["limit"],"5/52")
        self.assertEqual(receipt["dyadic_signed_parity_ratio"],
                         (1,2,8,7))
        self.assertEqual(receipt["ordinary_per_bit"],"5/52")
        self.assertEqual(receipt["special_per_bit"],"5/52")
        self.assertEqual(
            weighted_limit_inequality(Fraction(5,52),
                                      Fraction(5,52)),
            Fraction(5,4)
        )
        self.assertEqual(
            WEIGHTED_BOUND/Fraction(
                ORD_COEFFICIENT+SPECIAL_COEFFICIENT
            ),LIMIT
        )
        self.assertEqual(
            theorem_upper(250),LIMIT
        )
        self.assertEqual(
            theorem_receipt()["analytic_lower"],"5/52"
        )

    def test_BM27_joint_probability_and_special_bit_marginal_controls(self):
        self.assertTrue(verify_convolution_identity())
        for n in (1,2,3):
            net=gain_family(n,2,q=8)
            clean0,clean1=census(net.game(0)),census(net.game(1))
            from replication_uniform_upper_BM27 import (
                xor_convolve,exact_clean_law
            )
            for h,counts in ((0,clean0),(1,clean1)):
                expected=exact_clean_law(n,h)
                self.assertEqual(
                    tuple(expected.get(j,Fraction(0))
                          for j in range(1<<net.m)),
                    tuple(Fraction(w,sum(counts)) for w in counts)
                )
            self.assertEqual(
                marginal(explicit_mask_law(n,0),2*n),
                marginal(explicit_mask_law(n,1),2*n)
            )


if __name__=="__main__":
    unittest.main()
