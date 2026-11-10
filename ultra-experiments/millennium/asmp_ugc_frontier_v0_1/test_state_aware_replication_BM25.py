"""BM-25 exact q8 replication: seven-character full dual and symbolic lift.

Regressions cross-check the BM-24 18-orbit model, its independently
constructed rational LP matrix, the BM-17 FULL 64-output/128-atom
rational primal/dual checker and the n>=2 projection theorem.
"""
from fractions import Fraction
import unittest

from state_aware_replication_BM25 import (
    EXACT_ETA, ORBIT_DENOMINATOR,
    FLAT_MASK_NUMERATORS,FRUSTRATED_MASK_NUMERATORS,
    ORBIT_DUAL_WALSH,ORBIT_DUAL_NORMALIZATION,ORBIT_DUAL_MARGINALS,
    model,sharp_orbit_masks,verify_exact_orbit_certificate,
    expanded_full_mask_law,sparse_full_dual,verify_exact_full_certificate,
    projection_bounds,lifted_full_dual,verify_symbolic_lift,theorem_receipt,
)
from repeated_gain_erasure_BM24 import (
    gain_family,common_mask_orbits,verify_common_symbolic,exact_common_cap,
)
from repeated_theta_orbits_BM24 import (
    build_repeated_lp,check_repeated_lp_matrix,
)
from generic_fourier_erasure_BM17 import (
    census,signed_walsh,
)
from fourier_completion_BM18 import (
    mask_marginals,convolve_clean,
)
from sharp_erasure_optimality import (
    critical_erasure_cap,verify_sharp_witness,
)
from theta_shared_cycle_erasure import (
    verify_q8_primal,verify_q8_dual,
)


class StateAwareReplicationTests(unittest.TestCase):
    def test_exact_18_orbit_matching_primal_dual_and_independent_matrix(self):
        self.assertEqual(EXACT_ETA,Fraction(5,118))
        self.assertEqual(sum(FLAT_MASK_NUMERATORS.values()),13216)
        self.assertEqual(sum(FRUSTRATED_MASK_NUMERATORS.values()),13216)
        net=model()
        self.assertEqual((net.path_count,net.m,net.vertices),(3,6,5))
        self.assertEqual(net.orbit_size,18)
        self.assertEqual(verify_exact_orbit_certificate(),EXACT_ETA)
        a,b=sharp_orbit_masks()
        self.assertEqual(len(a),9)
        self.assertEqual(len(b),11)
        self.assertEqual(net.max_bit_marginal(a,b),EXACT_ETA)
        lp=build_repeated_lp(net)
        self.assertEqual((lp.variables,len(lp.equalities),len(lp.inequalities)),
                         (37,19,4))
        self.assertTrue(check_repeated_lp_matrix(lp,a,b,EXACT_ETA))
        self.assertFalse(check_repeated_lp_matrix(
            lp,a,b,EXACT_ETA-Fraction(1,10000)
        ))

    def test_exact_128_full_cube_dual_and_64_output_laws(self):
        report=verify_exact_full_certificate()
        self.assertEqual(report.optimum,EXACT_ETA)
        self.assertEqual(report.checked_mask_inequalities,128)
        self.assertEqual(report.walsh_terms,7)
        self.assertTrue(report.full_output_equal)
        net=model()
        clean0,clean1=census(net.game(0)),census(net.game(1))
        self.assertNotEqual(clean0,clean1)
        a,b=expanded_full_mask_law(0),expanded_full_mask_law(1)
        self.assertEqual((len(a),len(b)),(33,36))
        self.assertEqual(mask_marginals(net.m,a),(EXACT_ETA,)*6)
        self.assertEqual(mask_marginals(net.m,b),(EXACT_ETA,)*6)
        self.assertEqual(
            convolve_clean(net.m,clean0,a),
            convolve_clean(net.m,clean1,b)
        )

    def test_full_dual_has_only_seven_Fourier_signatures(self):
        dual=sparse_full_dual()
        self.assertEqual(set(dual.walsh_numerators),
                         {31,47,55,59,61,62,63})
        self.assertEqual(Fraction(sum(dual.normalization_numerators),
                                  dual.walsh_denominator),EXACT_ETA)
        self.assertEqual(-sum(dual.marginal_numerators),
                         dual.marginal_denominator)
        self.assertEqual(len(dual.marginal_numerators),12)
        self.assertTrue(all(v<=0 for v in dual.marginal_numerators))
        self.assertEqual(len(ORBIT_DUAL_WALSH),3)
        self.assertEqual(ORBIT_DUAL_NORMALIZATION,
                         (Fraction(0),EXACT_ETA))
        self.assertEqual(ORBIT_DUAL_MARGINALS[0],
                         (-Fraction(11,59),-Fraction(19,59)))
        self.assertEqual(ORBIT_DUAL_MARGINALS[1],
                         (-Fraction(10,59),-Fraction(19,59)))

    def test_clean_discrepancy_support_seven_exact_full_characters(self):
        net=model()
        c0,c1=census(net.game(0)),census(net.game(1))
        D={S for S in range(1<<net.m)
           if signed_walsh(c0,S)!=signed_walsh(c1,S)}
        self.assertEqual(D,{31,47,55,59,61,62,63})
        self.assertEqual(net.clean_support_count(),7)
        self.assertEqual(net.clean_support_count(),4**2-3**2)
        self.assertEqual(D,set(sparse_full_dual().walsh_numerators))

    def test_replication_increases_optimal_q8_mask_budget(self):
        self.assertTrue(verify_sharp_witness(8,4))
        single=critical_erasure_cap(8,4)
        self.assertEqual(single,Fraction(1,44))
        self.assertGreater(EXACT_ETA,single)
        self.assertEqual(EXACT_ETA/single,Fraction(110,59))
        self.assertEqual(EXACT_ETA-single,Fraction(51,2596))
        self.assertLess(EXACT_ETA,exact_common_cap(2))
        # Same K_2,3 topology, but BM-09 has three distinct path
        # gains, so all three four-cycles are frustrated.
        self.assertTrue(verify_q8_primal() and verify_q8_dual())
        self.assertLess(EXACT_ETA,Fraction(29,630))

    def test_nonzero_exceptional_gain_is_a_statistical_automorphism(self):
        for gain in (1,2,3,4,5,6,7):
            self.assertEqual(verify_exact_orbit_certificate(gain),EXACT_ETA)
            net=model(gain)
            self.assertEqual(net.clean_support_count(),7)
        for gain in (1,2,7):
            self.assertEqual(verify_exact_full_certificate(gain).optimum,
                             EXACT_ETA)

    def test_exact_seven_term_lower_lifts_to_more_ordinary_paths(self):
        for n in (2,3,5,10,250):
            self.assertEqual(verify_symbolic_lift(n),EXACT_ETA)
            extended=lifted_full_dual(n)
            self.assertEqual(len(extended.walsh_numerators),7)
            self.assertEqual(len(extended.marginal_numerators),
                             2*(2*n+2))
            self.assertEqual(
                Fraction(sum(extended.normalization_numerators),
                         extended.walsh_denominator),EXACT_ETA
            )
            self.assertEqual(-sum(extended.marginal_numerators),
                             extended.marginal_denominator)
            self.assertEqual(
                projection_bounds(n),
                (EXACT_ETA,Fraction(1,8))
            )

    def test_250_ordinary_paths_projected_lower_and_common_upper(self):
        n=250
        net=gain_family(n,2,q=8)
        self.assertEqual(net.m,502)
        self.assertEqual(net.path_count,251)
        self.assertEqual(net.orbit_size,94878)
        self.assertEqual(net.BM14_pathwise_orbit_size,3**251)
        self.assertEqual(4**n-3**n,4**250-3**250)
        self.assertEqual(verify_common_symbolic(n,2,q=8),
                         Fraction(1,8))
        self.assertEqual(verify_symbolic_lift(n),EXACT_ETA)
        self.assertEqual(projection_bounds(n),
                         (Fraction(5,118),Fraction(1,8)))
        self.assertGreater(4**250-3**250,1<<499)

    def test_mutated_orbit_channel_and_dual_are_detected(self):
        net=model()
        a,b=sharp_orbit_masks()
        altered=dict(a)
        src=next(k for k,v in altered.items() if v>Fraction(1,100))
        target=next(k for k in net.all_signatures() if k not in altered)
        altered[src]-=Fraction(1,ORBIT_DENOMINATOR)
        altered[target]=Fraction(1,ORBIT_DENOMINATOR)
        self.assertEqual(sum(altered.values()),1)
        with self.assertRaises(AssertionError):
            net.verify_primal(altered,b)
        norm=(ORBIT_DUAL_NORMALIZATION[0],
              ORBIT_DUAL_NORMALIZATION[1]+Fraction(1,10000))
        with self.assertRaises(AssertionError):
            net.verify_dual(norm,ORBIT_DUAL_WALSH,ORBIT_DUAL_MARGINALS)

    def test_receipt_and_invalid_input_contracts(self):
        r=theorem_receipt()
        self.assertEqual(r["hypothesis_aware_exact_erasure"],"5/118")
        self.assertEqual(r["single_ordinary_cycle_exact"],"1/44")
        self.assertEqual(r["strict_replication_cost_ratio"],"110/59")
        self.assertEqual(r["nonzero_full_dual_Fourier_subsets"],7)
        self.assertTrue(r["complete_output_laws_equal"])
        self.assertFalse(r["higher_n_exact_optimum_claimed"])
        with self.assertRaises(ValueError):
            projection_bounds(1)
        with self.assertRaises(ValueError):
            projection_bounds(2,gain=0)
        with self.assertRaises(ValueError):
            lifted_full_dual(1)
        with self.assertRaises(ValueError):
            expanded_full_mask_law(2)


if __name__=="__main__":
    unittest.main()
