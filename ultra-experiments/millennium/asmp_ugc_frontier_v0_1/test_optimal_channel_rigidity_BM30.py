"""BM-30 independent exact tests for asymptotic channel rigidity and stability.

Checks rational 1-parameter equality family on actual complete finite
output laws, unique minimax intersection, conditional special masks,
signed de Finetti parity flow, exact local gap/stability algebra, and
perturbation rejection. The general infinite measure proof is in the
Markdown note; this is finite symbolic verification, not Lean.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import product
from random import Random
import unittest

from optimal_channel_rigidity_BM30 import (
    LIMIT,SPECIAL_CONDITIONAL,DirectingAtom,
    canonical_equality_atoms,conditional_special_from_moments,
    frontier_costs,frontier_components,
    explicit_frontier_mask,verify_exact_frontier,optimized_frontier,
    local_overlap_gap_lower,stability_bounds,proof_receipt,
)
from infinite_replication_rigidity_BM29 import (
    pair_walsh,WEIGHTED_BOUND,bm27_directing_atoms,
    verify_bm27_equality_case,
)
from replication_uniform_upper_BM27 import (
    PAIR_I,PAIR_A,PAIR_B,PAIR_E,PAIRS,COMPONENTS,
    xor_convolve,exact_clean_law,
    explicit_mask_law as bm27_mask_law,
)
from fourier_completion_BM18 import mask_marginals
from repeated_gain_erasure_BM24 import gain_family
from generic_fourier_erasure_BM17 import census


def independent_flow(atoms):
    lhs=defaultdict(lambda:Fraction(0))
    rhs=defaultdict(lambda:Fraction(0))
    for a in atoms:
        if not a.mu:
            continue
        where=(a.u,a.w)
        down=(a.u,a.w/2)
        lhs[where]+=2*a.nu0
        lhs[down]+=7*a.nu0
        rhs[where]+=a.nu1
        rhs[down]+=8*a.nu1
    return {key:lhs[key]-rhs[key] for key in lhs.keys()|rhs.keys()}


def independent_cost_accounting(atoms):
    self_mu=sum((a.mu for a in atoms),Fraction(0))
    if self_mu!=1:
        raise AssertionError("directing measure unnormalized")
    J=sum(((1-a.u)*a.mu for a in atoms),Fraction(0))
    H=sum((min(a.nu0,a.nu1) for a in atoms),Fraction(0))
    overlap_gap=Fraction(16,5)*J-H
    T=sum((((a.mu+min(a.nu0,a.nu1))/2-a.v)
           for a in atoms),Fraction(0))
    ordinary=J/2
    exceptional=(1-sum((a.v for a in atoms),Fraction(0)))/2
    weighted_excess=8*ordinary+5*exceptional-Fraction(5,4)
    expanded=Fraction(5,4)*overlap_gap+Fraction(5,2)*T
    return ordinary,exceptional,overlap_gap,T,weighted_excess,expanded


class BM30ChannelRigidityTests(unittest.TestCase):
    def test_all_conditional_special_two_bit_noise_laws_are_exact(self):
        atoms=canonical_equality_atoms(Fraction(1,13))
        self.assertEqual(tuple(a.name for a in atoms),("I","A","B"))
        self.assertEqual(tuple(a.mu for a in atoms),
                         (Fraction(3,13),Fraction(2,13),Fraction(8,13)))
        self.assertEqual(tuple((a.nu0,a.nu1) for a in atoms),(
            (Fraction(0),Fraction(0)),
            (Fraction(1,13),Fraction(2,13)),
            (Fraction(8,13),Fraction(7,13)),
        ))
        for a in atoms:
            for h in (0,1):
                predicted=conditional_special_from_moments(a,h)
                self.assertEqual(predicted,SPECIAL_CONDITIONAL[a.name][h])
                self.assertEqual(sum(predicted),1)
                self.assertEqual(pair_walsh(predicted)[3],
                                 (a.nu0 if h==0 else a.nu1)/a.mu)
                self.assertEqual(pair_walsh(predicted)[1],a.v/a.mu)
        self.assertEqual(SPECIAL_CONDITIONAL["I"],(PAIR_E,PAIR_E))
        self.assertEqual(SPECIAL_CONDITIONAL["A"][1],PAIR_A)
        self.assertEqual(SPECIAL_CONDITIONAL["B"][0],
            tuple((3*x+y)/4 for x,y in zip(PAIR_I,PAIR_A)))
        self.assertEqual(SPECIAL_CONDITIONAL["B"][1],
            tuple((3*x+y)/4 for x,y in zip(PAIR_I,PAIR_B)))

    def test_one_parameter_weighted_equality_flow_for_all_rational_c(self):
        for c in (Fraction(0),Fraction(1,100),Fraction(1,52),
                  Fraction(1,26),Fraction(1,13),Fraction(9,100),
                  Fraction(1,10)):
            atoms=canonical_equality_atoms(c)
            self.assertEqual(tuple(a.mu for a in atoms),
                             (1-10*c,2*c,8*c))
            self.assertTrue(all(v==0 for v in independent_flow(atoms).values()))
            ordinary,special,G,T,weighted,expanded=independent_cost_accounting(
                atoms)
            self.assertEqual((G,T,weighted,expanded),(0,0,0,0))
            self.assertEqual((ordinary,special),
                             (Fraction(5,4)*c,Fraction(1,4)-2*c))
            self.assertEqual(frontier_costs(c),(
                ordinary,special,max(ordinary,special)
            ))

    def test_complete_Boolean_output_equality_for_multiple_c_and_n(self):
        for c in (Fraction(0),Fraction(1,20),Fraction(1,13),
                  Fraction(1,10)):
            result=verify_exact_frontier(c,n_values=(1,2,3))
            for n in (1,2,3):
                q0=explicit_frontier_mask(n,c,0)
                q1=explicit_frontier_mask(n,c,1)
                p0,p1=exact_clean_law(n,0),exact_clean_law(n,1)
                self.assertEqual(xor_convolve(p0,q0),xor_convolve(p1,q1))
                self.assertEqual(sum(q0.values()),1)
                self.assertEqual(sum(q1.values()),1)
                costs=frontier_costs(c)
                self.assertEqual(
                    mask_marginals(2*n+2,q0)[:2*n],(costs[0],)*(2*n))
                self.assertEqual(
                    mask_marginals(2*n+2,q1)[-2:],(costs[1],)*2)
                if c==Fraction(1,13):
                    self.assertEqual(q0,bm27_mask_law(n,0))
                    self.assertEqual(q1,bm27_mask_law(n,1))

    def test_minimax_balance_is_uniquely_5_over_52(self):
        receipt=optimized_frontier()
        self.assertEqual(receipt["optimal_directing_parameter"],"1/13")
        self.assertEqual(receipt["minimax_cap"],"5/52")
        self.assertEqual(LIMIT,Fraction(5,52))
        for c in (Fraction(0),Fraction(1,100),Fraction(1,20),
                  Fraction(1,12),Fraction(1,10)):
            self.assertGreater(frontier_costs(c)[2],LIMIT)
        for c in (Fraction(1,40),Fraction(1,13),Fraction(1,11)):
            # Sign of the crossing at c=1/13.
            o,s,_=frontier_costs(c)
            self.assertEqual((o>s)-(o<s),
                             (c>Fraction(1,13))-(c<Fraction(1,13)))

    def test_local_dyadic_deficit_improved_to_five_eighths(self):
        for u in (Fraction(-1),Fraction(0),Fraction(1,2),
                  Fraction(5,8),Fraction(11,16),Fraction(3,4),
                  Fraction(4,5),Fraction(15,16),Fraction(1)):
            got=local_overlap_gap_lower(u)
            if u<=Fraction(5,8):
                expected=Fraction(16,5)*(1-u)-1
            elif u<=Fraction(3,4):
                expected=Fraction(16,5)*(Fraction(3,4)-u)
            else:
                expected=Fraction(16,5)*(1-u)
            self.assertEqual(got,expected)
            self.assertGreaterEqual(got,0)
        self.assertEqual(local_overlap_gap_lower(Fraction(5,8)),
                         Fraction(1,5))
        self.assertEqual(local_overlap_gap_lower(Fraction(3,4)),0)
        self.assertEqual(local_overlap_gap_lower(Fraction(1)),0)
        for bad in (Fraction(2),Fraction(-3)):
            with self.assertRaises(ValueError):
                local_overlap_gap_lower(bad)

    def test_quantitative_near_optimal_directing_measure_bounds(self):
        for delta in (Fraction(0),Fraction(1,100000),
                      Fraction(1,1000),Fraction(1,100)):
            for eps in (Fraction(1,100),Fraction(1,16),
                        Fraction(1,8),Fraction(1,2)):
                b=stability_bounds(delta,eps)
                self.assertEqual(b["overlap_deficit_upper"],
                                 Fraction(52,5)*delta)
                self.assertEqual(b["special_nonnegativity_slack_upper"],
                                 Fraction(26,5)*delta)
                self.assertEqual(b["weighted_cost_gap"],13*delta)
                self.assertEqual(b["mass_far_from_optimal_u_upper"],
                    min(Fraction(1),Fraction(52)*delta/
                        min(Fraction(1),16*eps)))
        self.assertEqual(
            stability_bounds(Fraction(1,1000),Fraction(1,32))[
                "mass_far_from_optimal_u_upper"
            ],Fraction(13,125))
        with self.assertRaises(ValueError):
            stability_bounds(-1,Fraction(1,10))
        with self.assertRaises(ValueError):
            stability_bounds(0,0)

    def test_fair_noise_and_zero_ordinary_mask_have_exact_slack_decomposition(self):
        # Fully independent fair noise on all bits is always a legal
        # full eraser with cost 1/2; its signed exceptional parity is 0.
        fair=(DirectingAtom("F",Fraction(1),Fraction(0),
                            Fraction(0),Fraction(0),Fraction(0),Fraction(0)),)
        vals=independent_cost_accounting(fair)
        self.assertEqual(vals[0:2],(Fraction(1,2),Fraction(1,2)))
        self.assertEqual(vals[2],Fraction(16,5))
        self.assertEqual(vals[3],Fraction(1,2))
        self.assertEqual(vals[4],vals[5])
        self.assertEqual(vals[4],Fraction(21,4))
        # Ordinary identity + special E costs (0,1/4), and is an
        # equalizer in its own right.
        only_identity=canonical_equality_atoms(Fraction(0))
        vals=independent_cost_accounting(only_identity)
        self.assertEqual(vals,(0,Fraction(1,4),0,0,0,0))

    def test_exact_BM29_equality_case_and_proof_receipt(self):
        old=verify_bm27_equality_case()
        self.assertEqual(old["limit"],"5/52")
        current=proof_receipt()
        self.assertTrue(current["unique_symmetric_infinite_mask_channel"])
        self.assertEqual(current["BM29_limit"],"5/52")
        self.assertEqual(current["ordinary_cost"],"5/52")
        self.assertEqual(current["exceptional_cost"],"5/52")
        self.assertFalse(current["measure_theory_machine_formalized"])
        self.assertFalse(current["quantitative_finite_n_rate_claimed"])

    def test_invalid_directing_family_parameters_and_mask_contracts(self):
        for c in (-1,Fraction(11,100)):
            with self.assertRaises(ValueError):
                canonical_equality_atoms(c)
            with self.assertRaises(ValueError):
                frontier_components(c,0)
        with self.assertRaises(ValueError):
            frontier_components(Fraction(1,13),2)
        with self.assertRaises(ValueError):
            explicit_frontier_mask(6,Fraction(1,13),0)
        with self.assertRaises(ValueError):
            explicit_frontier_mask(0,Fraction(1,13),0)
        with self.assertRaises(ValueError):
            conditional_special_from_moments(
                DirectingAtom("X",0,0,0,0,0,0),0
            )


if __name__=="__main__":
    unittest.main()
