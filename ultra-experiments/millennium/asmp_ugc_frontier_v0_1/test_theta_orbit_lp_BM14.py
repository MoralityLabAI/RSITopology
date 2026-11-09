"""BM-14: independent exact path-orbit LP and dual-symmetry checks."""
from fractions import Fraction
from itertools import product
from math import comb
import unittest

from theta_orbit_lp_BM14 import (
    OrbitModel,orbit_signatures,mask_signature,canonical_subset,
    walsh_kernel_one,walsh_kernel,mask_mass_orbits,expand_orbit_masses,
    mask_orbit_walsh,orbit_marginals,verify_orbit_primal,
    aggregate_dual_to_orbits,verify_orbit_dual,clean_orbit_law,
    masked_count_law,build_orbit_lp,check_orbit_lp_primal,orbit_manifest,
)
from theta_fourier_transfer_BM12 import theta_path_game,theta_observation_counts
from sparse_fourier_degree_BM13 import (
    dual_certificate as full_dual,verify_sparse_dual,
)
from diamond_weighted_fourier_BM10 import (
    PRIMAL_MASK_COUNTS as DIAMOND_MASKS,PRIMAL_DENOMINATOR as DIAMOND_DENOM,
    verify_full_primal as diamond_full,
)
from theta_shared_cycle_erasure import (
    q4_common_mask, Q8_FLAT,Q8_FRUSTRATED,verify_q8_primal,verify_q8_dual,
)
from correlated_minimax import apply_correlated_mask
from frontier_bounds import tv_distance


def models():
    return (
        ("diamond",OrbitModel(4,(1,2,2),(0,0,0),(0,1,2))),
        ("theta",OrbitModel(4,(2,2,2),(0,0,0),(0,1,2))),
    )


def original_masks(kind):
    if kind=="diamond":
        return DIAMOND_MASKS,DIAMOND_MASKS,DIAMOND_DENOM
    q4={i:v for i,v in enumerate(q4_common_mask()) if v}
    return q4,q4,12


def bit_law_from_counts(game):
    counts=theta_observation_counts(game)
    return {
        tuple(bool(mask & (1<<i)) for i in range(len(game.edges))):
        Fraction(n,game.q**game.vertices)
        for mask,n in enumerate(counts) if n
    }


def mask_boolean_law(lengths,full_probs):
    return {
        tuple(bool(mask&(1<<i)) for i in range(sum(lengths))):prob
        for mask,prob in full_probs.items() if prob
    }


class ThetaOrbitLPTests(unittest.TestCase):
    def test_orbit_reduction_sizes_and_full_model_dimensions(self):
        expected={"diamond":(32,18),"theta":(64,27)}
        for name,model in models():
            manifest=orbit_manifest(model)
            full,orbits=expected[name]
            self.assertEqual(manifest["full_mask_states_per_world"],full)
            self.assertEqual(manifest["orbit_mask_states_per_world"],orbits)
            self.assertEqual(manifest["orbit_lp_variables"],2*orbits+1)
            self.assertEqual(manifest["orbit_lp_equalities"],orbits+1)
            self.assertEqual(manifest["orbit_lp_marginal_inequalities"],6)
            lp=build_orbit_lp(model)
            self.assertEqual(len(lp.equality_rows),orbits+1)
            self.assertEqual(len(lp.inequality_rows),6)
            self.assertTrue(all(len(row)==2*orbits+1
                                for row in lp.equality_rows+lp.inequality_rows))

    def test_binary_Krawtchouk_kernel_matches_independent_uniform_masks(self):
        for n in range(1,7):
            for s,t in product(range(n+1),repeat=2):
                expected=Fraction(sum(
                    (-1 if (mask&((1<<s)-1)).bit_count()%2 else 1)
                    for mask in range(1<<n) if mask.bit_count()==t
                ),comb(n,t))
                self.assertEqual(walsh_kernel_one(n,s,t),expected)
        for lengths in ((1,2,2),(2,2,2),(1,3,2)):
            for s,t in product(orbit_signatures(lengths),repeat=2):
                self.assertEqual(walsh_kernel(lengths,s,t),
                                 Fraction(1)*__import__("math").prod(
                                     walsh_kernel_one(n,a,b)
                                     for n,a,b in zip(lengths,s,t)
                                 ))

    def test_independent_residual_orbit_probability_matches_all_vertex_labels(self):
        for q,lengths,g0,g1 in (
            (4,(1,2,2),(0,0,0),(0,1,2)),
            (4,(2,2,2),(0,0,0),(0,1,2)),
            (8,(2,2,2),(0,0,0),(0,1,2)),
            (4,(1,2,3),(0,0,0),(0,1,2)),
        ):
            model=OrbitModel(q,lengths,g0,g1)
            for h,gains in ((0,g0),(1,g1)):
                direct_counts=theta_observation_counts(
                    theta_path_game(q,lengths,gains)
                )
                direct={}
                for mask,value in enumerate(direct_counts):
                    signature=mask_signature(lengths,mask)
                    direct[signature]=direct.get(signature,Fraction(0))+Fraction(
                        value,q**(2+sum(n-1 for n in lengths))
                    )
                self.assertEqual(clean_orbit_law(model,h),direct)
                self.assertEqual(sum(direct.values()),1)

    def test_previous_full_mask_upper_witnesses_project_to_exact_orbit_primal(self):
        self.assertTrue(diamond_full())
        for name,model in models():
            a,b,d=original_masks(name)
            p0=mask_mass_orbits(model.lengths,a,d)
            p1=mask_mass_orbits(model.lengths,b,d)
            expected=Fraction(1,5) if name=="diamond" else Fraction(1,6)
            self.assertEqual(verify_orbit_primal(model,p0,p1,cap=expected),expected)
            lp=build_orbit_lp(model)
            self.assertTrue(check_orbit_lp_primal(lp,p0,p1,expected))
            self.assertEqual(sum(expand_orbit_masses(model.lengths,p0).values()),1)

    def test_q8_theta_asymmetric_64_mask_witness_survives_orbit_averaging(self):
        self.assertTrue(verify_q8_primal() and verify_q8_dual())
        model=OrbitModel(8,(2,2,2),(0,0,0),(0,1,2))
        q0=mask_mass_orbits(model.lengths,{
            i:v for i,v in enumerate(Q8_FLAT) if v},10080)
        q1=mask_mass_orbits(model.lengths,{
            i:v for i,v in enumerate(Q8_FRUSTRATED) if v},10080)
        self.assertEqual(verify_orbit_primal(model,q0,q1),Fraction(29,630))
        self.assertTrue(check_orbit_lp_primal(
            build_orbit_lp(model),q0,q1,Fraction(29,630)))

    def test_independent_full_output_convolution_agrees_with_reduced_count_channel(self):
        for name,model in models():
            a,b,den=original_masks(name)
            q0=mask_mass_orbits(model.lengths,a,den)
            q1=mask_mass_orbits(model.lengths,b,den)
            out=[]
            for h,q in ((0,q0),(1,q1)):
                expanded=expand_orbit_masses(model.lengths,q)
                clean=bit_law_from_counts(theta_path_game(
                    model.q,model.lengths,model.gains0 if h==0 else model.gains1
                ))
                masked=apply_correlated_mask(clean,
                    mask_boolean_law(model.lengths,expanded))
                summary={}
                for bits,p in masked.items():
                    sig=tuple(sum(bits[sum(model.lengths[:i]):
                                       sum(model.lengths[:i+1])])
                              for i in range(len(model.lengths)))
                    summary[sig]=summary.get(sig,Fraction(0))+p
                count_oracle=masked_count_law(model,h,q)
                self.assertEqual(count_oracle,summary)
                out.append(masked)
            self.assertEqual(out[0],out[1])
            self.assertEqual(tv_distance(out[0],out[1]),0)

    def test_BM13_full_duals_compress_to_six_and_four_orbit_signatures(self):
        for kind,model in models():
            self.assertEqual(verify_sparse_dual(kind),
                             Fraction(1,5) if kind=="diamond" else Fraction(1,6))
            norm,y,z=full_dual(kind)
            agg=aggregate_dual_to_orbits(model.lengths,norm,y,z)
            self.assertEqual(verify_orbit_dual(model,*agg),
                             Fraction(1,5) if kind=="diamond" else Fraction(1,6))
            self.assertEqual(len(agg[1]),6 if kind=="diamond" else 4)
            self.assertEqual(len(agg[2]),2)
            self.assertEqual(tuple(map(len,agg[2])),(3,3))
            self.assertTrue(all(v<=0 for row in agg[2] for v in row))

    def test_large_31_edge_4096_label_case_is_lazy_and_symmetry_compressed(self):
        model=OrbitModel(4096,(12,10,9),(0,0,0),(0,1,2))
        manifest=orbit_manifest(model)
        self.assertEqual(manifest["full_mask_states_per_world"],2**31)
        self.assertEqual(manifest["orbit_mask_states_per_world"],13*11*10)
        self.assertEqual(manifest["orbit_lp_variables"],2*1430+1)
        self.assertEqual(manifest["orbit_lp_equalities"],1431)
        self.assertEqual(manifest["orbit_lp_marginal_inequalities"],6)
        self.assertEqual(model.clean_walsh(0,(0,0,0)),1)
        for subset in ((12,10,9),(1,2,3),(0,10,0)):
            self.assertTrue(-1<=model.clean_walsh(1,subset)<=1)
        self.assertEqual(walsh_kernel(model.lengths,(0,0,0),(12,10,9)),1)
        with self.assertRaises(ValueError):
            build_orbit_lp(model,max_classes=100)

    def test_malformed_probabilities_and_dual_budgets_rejected(self):
        model=models()[0][1]
        a,b,den=original_masks("diamond")
        x=mask_mass_orbits(model.lengths,a,den)
        with self.assertRaises(ValueError):
            verify_orbit_primal(model,{(0,0,0):Fraction(2)},x)
        with self.assertRaises(ValueError):
            mask_mass_orbits(model.lengths,{33:1},1)
        with self.assertRaises(ValueError):
            canonical_subset(model.lengths,(2,0,0))
        with self.assertRaises(ValueError):
            walsh_kernel_one(2,3,1)
        with self.assertRaises(ValueError):
            aggregate_dual_to_orbits(
                model.lengths,(Fraction(0),Fraction(0)),{35:Fraction(1)},({},{}))
        with self.assertRaises(ValueError):
            verify_orbit_dual(model,(Fraction(0),Fraction(0)),{},((0,0,0),(0,0,0)))
        lp=build_orbit_lp(model)
        self.assertFalse(check_orbit_lp_primal(lp,x,x,Fraction(0)))


if __name__=="__main__":
    unittest.main()
