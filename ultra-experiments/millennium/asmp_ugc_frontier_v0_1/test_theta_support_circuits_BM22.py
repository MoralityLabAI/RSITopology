"""BM-22: independent theta Fourier support circuits and exact q4 erasure.

All small Fourier coefficients are compared with complete uniform vertex
label enumeration. The full mask equalization is also checked through
independent Boolean-XOR convolutions, rather than just the BM-22 character
identities. A 360-edge biconnected treewidth-two theta serves as the
symbolic exponential-support counterexample with short optimal mask proof.
"""
from fractions import Fraction
from itertools import product
from math import comb, prod
from random import Random
import unittest

from theta_support_circuits_BM22 import ThetaSupportCircuit
from theta_fourier_transfer_BM12 import theta_path_game,theta_walsh_transfer
from theta_orbit_lp_BM14 import (
    OrbitModel,mask_mass_orbits,orbit_signatures,
)
from generic_fourier_erasure_BM17 import (
    census,signed_walsh,mask_walsh
)
from fourier_completion_BM18 import convolve_clean,mask_marginals
from sparse_fourier_degree_BM13 import primal_for_fourier_degree
from theta_shared_cycle_erasure import (
    THETA_SHIFTS, Q8_FLAT,Q8_FRUSTRATED,
)
from sharp_erasure_optimality import critical_erasure_cap
from support_aware_fixtures_BM19 import FIXTURES


def circuit(q,lengths,gains):
    return ThetaSupportCircuit(q,lengths,(0,)*len(lengths),gains)


def direct_clean_counts(instance):
    g0=theta_path_game(instance.q,instance.lengths,instance.gains0)
    g1=theta_path_game(instance.q,instance.lengths,instance.gains1)
    return census(g0),census(g1)


def complete_output_walsh_error(instance,law):
    p0,p1=direct_clean_counts(instance)
    return convolve_clean(instance.edge_count,p0,law)==convolve_clean(
        instance.edge_count,p1,law
    )


class ThetaSupportCircuitsTests(unittest.TestCase):
    def test_every_small_coefficient_matches_independent_uniform_labels(self):
        examples=(
            circuit(2,(2,2,2),(0,1,0)),
            circuit(4,(1,2,2),(0,1,2)),
            circuit(4,(2,2,2),(0,1,2)),
            circuit(4,(2,3,3),(0,1,2)),
            circuit(4,(2,2,3),(0,1,2)),
            circuit(4,(1,3,3),(0,1,2)),
            circuit(4,(2,2,2),(0,1,0)),
            circuit(8,(2,2,2),(0,1,2)),
        )
        for c in examples:
            p0,p1=direct_clean_counts(c)
            for S in range(1<<c.edge_count):
                self.assertEqual(c.clean_walsh(S,0),signed_walsh(p0,S))
                self.assertEqual(c.clean_walsh(S,1),signed_walsh(p1,S))
                self.assertEqual(c.discrepancy(S),
                                 signed_walsh(p0,S)-signed_walsh(p1,S))
                self.assertEqual(c.contains_discrepancy(S),
                                 signed_walsh(p0,S)!=signed_walsh(p1,S))
                self.assertEqual(c.clean_walsh(S,1),
                                 theta_walsh_transfer(
                                     c.q,c.lengths,c.gains1,S))
            self.assertEqual(c.support_count(),sum(
                p0h!=p1h for p0h,p1h in (
                    (signed_walsh(p0,S),signed_walsh(p1,S))
                    for S in range(1<<c.edge_count))
            ))

    def test_q4_distinct_path_type_closed_cardinality_and_full_cancellation(self):
        examples={
            (2,2,2):(10,True),
            (1,2,2):(8,True),
            (2,2,3):(1+3+7+1,True),
            (2,3,3):(3+7+7,False),
            (1,3,3):(1+7+7+1,True),
            (3,3,3):(7+7+7+1,True),
            (1,2,3):(1+3+7,False),
        }
        for lengths,(count,full_nonzero) in examples.items():
            c=circuit(4,lengths,(0,1,2))
            self.assertEqual(c.q4_distinct_three_path_support_count(),count)
            self.assertEqual(c.support_count(),count)
            full=(1<<c.edge_count)-1
            self.assertEqual(bool(c.discrepancy(full)),full_nonzero)
            for J in range(8):
                if J.bit_count()==2:
                    self.assertNotEqual(c.full_delta(J),0)
                elif J.bit_count()<2:
                    self.assertEqual(c.full_delta(J),0)

    def test_exact_q4_three_even_path_theorem_rational_lower_and_upper(self):
        lengths_cases={
            (2,2,2):Fraction(1,6),
            (2,2,4):Fraction(1,8),
            (2,2,6):Fraction(1,8),
            (2,4,4):Fraction(1,10),
            (2,4,6):Fraction(1,12),
            (2,4,8):Fraction(1,12),
            (4,6,8):Fraction(1,18),
            (2,2,20):Fraction(1,8),
        }
        for lengths,eta in lengths_cases.items():
            c=circuit(4,lengths,(0,1,2))
            self.assertEqual(c.q4_even_erasure_cap(),eta)
            proof=c.q4_even_lower_proof()
            self.assertEqual(proof["combined_lower_bound"],eta)
            self.assertEqual(proof["parity_lower_bound"],
                             Fraction(1,sum(lengths)))
            self.assertEqual(proof["projected_cycle_lower_bound"],
                             Fraction(1,2*(sum(lengths)-max(lengths))))
            self.assertEqual(c.q4_even_verify_upper_algebraic(),eta)
            self.assertEqual(c.q4_even_verify_upper_symbolic(),eta)
            law=c.q4_even_explicit_mask_law()
            self.assertEqual(sum(law.values()),1)
            self.assertEqual(max(mask_marginals(c.edge_count,law)),eta)
            activation=c.q4_even_activation_law()
            self.assertEqual(sum(activation.values()),1)
            for J in (3,5,6,7):
                self.assertEqual(sum((
                    w*(-1 if (T&J).bit_count()%2 else 1)
                    for T,w in activation.items()
                ),Fraction(0)),0)

    def test_q4_even_theta_full_output_equality_against_label_census(self):
        for lengths in ((2,2,2),(2,2,4),(2,4,4),(2,2,6)):
            c=circuit(4,lengths,(0,1,2))
            mask=c.q4_even_explicit_mask_law()
            self.assertTrue(complete_output_walsh_error(c,mask))
            p0,p1=direct_clean_counts(c)
            self.assertNotEqual(p0,p1)
            self.assertEqual(max(mask_marginals(c.edge_count,mask)),
                             c.q4_even_erasure_cap())

    def test_BM09_six_edge_mask_optimum_recovered_and_gain_independence(self):
        c=circuit(4,(2,2,2),(0,1,2))
        self.assertEqual(c.q4_even_erasure_cap(),Fraction(1,6))
        q=c.q4_even_explicit_mask_law()
        self.assertEqual(q[0],Fraction(1,4))
        self.assertEqual(sum(1 for v in q.values() if v),10)
        self.assertEqual(set(q),{0,1,2,4,8,16,32,10,17,36})
        self.assertEqual(q[1],Fraction(1,12))
        self.assertEqual(q[10],Fraction(1,12))
        self.assertEqual(c.q4_even_receipt()[
            "exact_hypothesis_aware_erasure"],"1/6")
        other=circuit(4,(2,2,2),(0,2,3))
        self.assertEqual(other.support_count(),c.support_count())
        self.assertEqual(other.q4_even_erasure_cap(),Fraction(1,6))
        self.assertEqual(other.q4_even_explicit_mask_law(),q)

    def test_sparse_frozen_masks_support_membership_without_full_census(self):
        cases=(
            ("diamond",3,circuit(4,(1,2,2),(0,1,2))),
            ("theta",4,circuit(4,(2,2,2),(0,1,2))),
        )
        for name,degree,c in cases:
            mask,D=primal_for_fourier_degree(name,degree)
            p0,p1=direct_clean_counts(c)
            expected=FIXTURES[(name,degree)][0]
            actual=tuple(S for S in range(1<<c.edge_count)
                         if c.masked_discrepancy(S,mask,mask,D))
            self.assertEqual(actual,expected)
            for S in range(1<<c.edge_count):
                reference=(signed_walsh(p0,S)-signed_walsh(p1,S))*mask_walsh(
                    mask,D,S
                )
                self.assertEqual(c.masked_discrepancy(S,mask,mask,D),
                                 reference)

    def test_orbit_masked_support_count_matches_partial_and_full_BM14_masks(self):
        for name,degree,c in (
            ("diamond",3,circuit(4,(1,2,2),(0,1,2))),
            ("theta",4,circuit(4,(2,2,2),(0,1,2))),
        ):
            mask,D=primal_for_fourier_degree(name,degree)
            orbits=mask_mass_orbits(c.lengths,mask,D)
            self.assertEqual(c.symmetric_masked_support_count(orbits,orbits),
                             len(FIXTURES[(name,degree)][0]))
        c=circuit(8,(2,2,2),(0,1,2))
        a=mask_mass_orbits(c.lengths,{
            x:v for x,v in enumerate(Q8_FLAT) if v},10080)
        b=mask_mass_orbits(c.lengths,{
            x:v for x,v in enumerate(Q8_FRUSTRATED) if v},10080)
        self.assertEqual(c.symmetric_masked_support_count(a,b),0)
        self.assertGreater(c.support_count(),0)

    def test_360_edge_biconnected_theta_exponential_support_constant_formula(self):
        L=(120,120,120)
        c=circuit(4,L,(0,1,2))
        m=sum(L)
        self.assertEqual(m,360)
        self.assertEqual(c.support_count(),3*((1<<120)-1)+1)
        self.assertEqual(c.q4_distinct_three_path_support_count(),
                         3*((1<<120)-1)+1)
        self.assertEqual(c.q4_even_erasure_cap(),Fraction(1,360))
        receipt=c.q4_even_receipt()
        self.assertEqual(receipt["edges"],360)
        self.assertEqual(receipt["exact_hypothesis_aware_erasure"],"1/360")
        self.assertFalse(receipt["clean_support_table_materialized"])
        self.assertEqual(c.q4_even_verify_upper_algebraic(),
                         Fraction(1,360))
        self.assertEqual(c.discrepancy((1<<360)-1),
                         Fraction(1,2**(360-4)))
        self.assertTrue(c.contains_discrepancy((1<<360)-1))
        for i in (0,119,120,239,240,359):
            # Exactly two whole paths and a proper 119-edge selection on
            # the third path remains a Fourier discrepancy.
            self.assertTrue(c.contains_discrepancy((1<<360)-1 ^ (1<<i)))
        rng=Random(20261110)
        for _ in range(200):
            mask=c.q4_even_sampler(rng)
            self.assertLessEqual(mask.bit_count(),3)
            self.assertEqual(mask.bit_count(),len(set(
                i for i,path in enumerate(c.path_masks) if mask&path
            )))

    def test_one_even_two_odd_cancellation_even_when_D_hypergraph_full_clique(self):
        lengths=(2,131,133)
        c=circuit(4,lengths,(0,1,2))
        self.assertEqual(c.discrepancy((1<<c.edge_count)-1),0)
        self.assertEqual(c.support_count(),
                         sum((1<<L)-1 for L in lengths))
        self.assertEqual(c.q4_distinct_three_path_support_count(),
                         c.support_count())
        # For every pair of edges a,b, some 2-full-path support contains
        # them, even though all three paths together cancel. The
        # interaction graph of D is therefore the full clique on m bits.
        for i,j in ((0,1),(0,2),(1,133),(20,255),(132,265)):
            path_pair=(next(k for k,M in enumerate(c.path_masks)
                            if M&(1<<i)),
                       next(k for k,M in enumerate(c.path_masks)
                            if M&(1<<j)))
            J=tuple(sorted(set(path_pair)))
            if len(J)==1:
                J=J+(next(k for k in range(3) if k not in J),)
            full_pair=c.path_masks[J[0]]|c.path_masks[J[1]]
            self.assertTrue(c.contains_discrepancy(full_pair))
            self.assertEqual(full_pair&(1<<i),1<<i)
            self.assertEqual(full_pair&(1<<j),1<<j)

    def test_two_path_q2_vanishing_proper_subset_character(self):
        c=circuit(2,(3,4),(0,1))
        self.assertEqual(c.alpha,0)
        self.assertEqual(c.support_count(),1)
        full=(1<<7)-1
        self.assertTrue(c.contains_discrepancy(full))
        for i in range(7):
            self.assertFalse(c.contains_discrepancy(full^(1<<i)))
        self.assertEqual(c.support_path_types(),(3,))

    def test_ambiguous_constraints_and_out_of_budget_requests_rejected(self):
        with self.assertRaises(ValueError):
            ThetaSupportCircuit(3,(2,2,2),(0,0,0),(0,1,2))
        with self.assertRaises(ValueError):
            ThetaSupportCircuit(4,(2,2,0),(0,0,0),(0,1,2))
        with self.assertRaises(ValueError):
            circuit(4,(1,2,2),(0,1,2)).q4_even_erasure_cap()
        with self.assertRaises(ValueError):
            circuit(8,(2,2,2),(0,1,2)).q4_even_erasure_cap()
        with self.assertRaises(ValueError):
            circuit(4,(2,2,2),(0,1,0)).q4_distinct_three_path_support_count()
        with self.assertRaises(ValueError):
            circuit(4,(2,2,2),(0,1,2)).signature(64)
        with self.assertRaises(ValueError):
            circuit(4,(2,2,2),(0,1,2)).masked_discrepancy(
                3,{0:3},{0:2},4
            )
        with self.assertRaises(ValueError):
            circuit(4,(120,120,120),(0,1,2)).q4_even_explicit_mask_law(
                max_states=10000
            )
        with self.assertRaises(ValueError):
            circuit(4,(2,2,2),(0,1,2)).symmetric_masked_support_count(
                {(0,0,0):Fraction(2)},
                {(0,0,0):Fraction(1)}
            )


if __name__=="__main__":
    unittest.main()
