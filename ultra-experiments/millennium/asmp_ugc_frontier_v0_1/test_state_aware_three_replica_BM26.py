"""BM-26: independent exact full readout proof and 502-edge dual lift."""
from fractions import Fraction
from math import lcm
import unittest

from state_aware_three_replica_BM26 import (
    EXACT_CAP,MASK_DENOMINATOR,DUAL_DENOMINATOR,
    DUAL_MARGINAL_DENOMINATOR,
    FLAT_ORBIT_NUMERATORS,FRUSTRATED_ORBIT_NUMERATORS,
    ORBIT_DUAL_WALSH_NUMERATORS,DUAL_NORMALIZATION_NUMERATORS,
    DUAL_MARGINAL_NUMERATORS,
    model,orbit_masks,orbit_dual,verify_exact_orbit_certificate,
    full_mask_law,full_dual,verify_exact_full_certificate,
    lifted_full_dual,verify_symbolic_lift,projection_bounds,
    theorem_receipt,
)
from state_aware_replication_BM25 import (
    EXACT_ETA as PREVIOUS_N2_ETA,verify_exact_full_certificate as previous_n2,
)
from repeated_gain_erasure_BM24 import (
    gain_family,common_mask_orbits,verify_common_symbolic,
)
from repeated_theta_orbits_BM24 import (
    build_repeated_lp,check_repeated_lp_matrix,
)
from generic_fourier_erasure_BM17 import (
    census,signed_walsh,
)
from fourier_completion_BM18 import convolve_clean,mask_marginals


class BM26Q8ThreeOrdinaryPathTests(unittest.TestCase):
    def test_sharp_30_class_orbit_upper_and_lower_are_exact(self):
        net=model()
        self.assertEqual((net.q,net.m,net.vertices),(8,8,6))
        self.assertEqual((net.path_count,net.orbit_size),(4,30))
        self.assertEqual(EXACT_CAP,Fraction(751225,13956626))
        self.assertEqual(sum(FLAT_ORBIT_NUMERATORS),MASK_DENOMINATOR)
        self.assertEqual(sum(FRUSTRATED_ORBIT_NUMERATORS),MASK_DENOMINATOR)
        a,b=orbit_masks()
        self.assertEqual((len(a),len(b)),(16,16))
        self.assertEqual(sum(a.values()),1)
        self.assertEqual(sum(b.values()),1)
        self.assertEqual(net.max_bit_marginal(a,b),EXACT_CAP)
        self.assertEqual(verify_exact_orbit_certificate(),EXACT_CAP)

    def test_every_mask_class_exactly_satisfies_four_cap_inequalities(self):
        net=model()
        a,b=orbit_masks()
        eta=EXACT_CAP
        for law in (a,b):
            for ty,t in enumerate(net.types):
                cap=sum((
                    mass*Fraction(
                        sum(j*sig[ty][j] for j in range(t.length+1)),
                        t.length*t.count,
                    ) for sig,mass in law.items()
                ),Fraction(0))
                self.assertEqual(cap,eta)
        lp=build_repeated_lp(net,max_orbits=64)
        self.assertEqual(lp.variables,61)
        self.assertEqual(len(lp.equalities),31)
        self.assertEqual(len(lp.inequalities),4)
        self.assertTrue(check_repeated_lp_matrix(lp,a,b,eta))
        self.assertFalse(check_repeated_lp_matrix(
            lp,a,b,eta-Fraction(1,10**10)
        ))

    def test_rational_dual_has_29_histogram_characters_and_valid_objective(self):
        norm,coeff,z=orbit_dual()
        self.assertEqual((len(coeff),sum(bool(v) for v in
                          ORBIT_DUAL_WALSH_NUMERATORS)),(29,29))
        self.assertEqual(
            sum(norm),EXACT_CAP
        )
        self.assertEqual(
            -sum((v for side in z for v in side),Fraction(0)),1
        )
        self.assertEqual(
            DUAL_NORMALIZATION_NUMERATORS,
            (-117251951355,331441223355)
        )
        self.assertEqual(DUAL_MARGINAL_NUMERATORS,
                         (-2972592,0,0,-4005721))
        self.assertEqual(
            model().verify_dual(norm,coeff,z,max_orbits=64),EXACT_CAP
        )
        self.assertTrue(all(v<=0 for side in z for v in side))

    def test_all_256_outputs_and_512_full_mask_inequalities_checked(self):
        receipt=verify_exact_full_certificate()
        self.assertEqual(receipt.optimum,EXACT_CAP)
        self.assertTrue(receipt.full_output_equal)
        self.assertEqual(receipt.checked_mask_inequalities,512)
        self.assertEqual(receipt.walsh_terms,255)
        a,b=full_mask_law(0),full_mask_law(1)
        self.assertEqual(sum(a.values()),1)
        self.assertEqual(sum(b.values()),1)
        self.assertEqual(mask_marginals(8,a),(EXACT_CAP,)*8)
        self.assertEqual(mask_marginals(8,b),(EXACT_CAP,)*8)
        p0,p1=census(model().game(0)),census(model().game(1))
        self.assertNotEqual(p0,p1)
        self.assertEqual(convolve_clean(8,p0,a),
                         convolve_clean(8,p1,b))

    def test_full_dual_coefficients_recover_orbit_dual_exactly(self):
        net=model()
        dual=full_dual()
        norm,coeff,z=orbit_dual()
        self.assertEqual(len(dual.walsh_numerators),255)
        self.assertEqual(len(dual.marginal_numerators),16)
        self.assertEqual(
            Fraction(sum(dual.normalization_numerators),
                     dual.walsh_denominator),EXACT_CAP
        )
        self.assertEqual(-sum(dual.marginal_numerators),
                         dual.marginal_denominator)
        aggregated={}
        for S,n in dual.walsh_numerators.items():
            sig=net.signature(S)
            aggregated[sig]=aggregated.get(sig,Fraction(0))+Fraction(
                n,dual.walsh_denominator
            )
        self.assertEqual(aggregated,coeff)
        self.assertEqual(
            len({net.signature(S) for S in dual.walsh_numerators}),29
        )

    def test_strict_growth_of_first_three_replication_thresholds(self):
        self.assertEqual(PREVIOUS_N2_ETA,Fraction(5,118))
        self.assertGreater(EXACT_CAP,PREVIOUS_N2_ETA)
        self.assertLess(EXACT_CAP,Fraction(1,8))
        self.assertEqual(
            EXACT_CAP-PREVIOUS_N2_ETA,
            Fraction(751225,13956626)-Fraction(5,118)
        )
        self.assertEqual(previous_n2().optimum,PREVIOUS_N2_ETA)

    def test_nonzero_exceptional_gain_is_immaterial(self):
        for gain in (1,2,3,4,5,6,7):
            self.assertEqual(
                verify_exact_orbit_certificate(gain),EXACT_CAP
            )
            self.assertEqual(
                model(gain).clean_support_count(max_orbits=64),
                4**3-3**3
            )
        self.assertEqual(verify_exact_full_certificate(2).optimum,
                         EXACT_CAP)

    def test_projection_dual_lifts_without_new_Fourier_terms(self):
        for n in (3,4,5,10,250):
            self.assertEqual(verify_symbolic_lift(n),EXACT_CAP)
            dual=lifted_full_dual(n)
            self.assertEqual(len(dual.walsh_numerators),255)
            self.assertEqual(len(dual.marginal_numerators),2*(2*n+2))
            self.assertEqual(
                Fraction(sum(dual.normalization_numerators),
                         dual.walsh_denominator),EXACT_CAP
            )
            self.assertEqual(-sum(dual.marginal_numerators),
                             dual.marginal_denominator)
            self.assertEqual(projection_bounds(n),
                             (EXACT_CAP,Fraction(1,8)))

    def test_502_edge_large_repeated_path_lower_and_common_upper(self):
        net=gain_family(250,2,q=8)
        self.assertEqual(net.m,502)
        self.assertEqual(net.path_count,251)
        self.assertEqual(net.orbit_size,94878)
        self.assertEqual(net.BM14_pathwise_orbit_size,3**251)
        self.assertEqual(verify_common_symbolic(250,2,q=8),
                         Fraction(1,8))
        self.assertEqual(verify_symbolic_lift(250),EXACT_CAP)
        self.assertEqual(projection_bounds(250),
                         (EXACT_CAP,Fraction(1,8)))
        self.assertFalse(theorem_receipt()["asymptotic_limit_claimed"])

    def test_mutated_upper_or_lower_certificate_is_rejected(self):
        net=model()
        a,b=orbit_masks()
        source=next(k for k,v in a.items() if v>Fraction(1,100))
        target=next(k for k in net.all_signatures(max_orbits=64)
                    if k not in a)
        altered=dict(a)
        altered[source]-=Fraction(1,MASK_DENOMINATOR)
        altered[target]=Fraction(1,MASK_DENOMINATOR)
        self.assertEqual(sum(altered.values()),1)
        with self.assertRaises(AssertionError):
            net.verify_primal(altered,b,max_orbits=64)
        norm,coeff,z=orbit_dual()
        corrupted=(norm[0],norm[1]+Fraction(1,10**8))
        with self.assertRaises(AssertionError):
            net.verify_dual(corrupted,coeff,z,max_orbits=64)

    def test_receipt_and_invalid_projection_dimensions(self):
        receipt=theorem_receipt()
        self.assertEqual(receipt["exact_hypothesis_aware_cap"],
                         "751225/13956626")
        self.assertEqual(receipt["nonzero_primal_orbit_masses"],(16,16))
        self.assertEqual(receipt["nonzero_orbit_dual_characters"],29)
        self.assertEqual(receipt["nonzero_full_dual_characters"],255)
        self.assertEqual(receipt["full_output_patterns_verified"],256)
        self.assertEqual(receipt["full_dual_mask_inequalities_verified"],512)
        self.assertFalse(receipt["n_ge4_sharp_claimed"])
        with self.assertRaises(ValueError):
            projection_bounds(2)
        with self.assertRaises(ValueError):
            lifted_full_dual(2)
        with self.assertRaises(ValueError):
            full_mask_law(2)


if __name__=="__main__":
    unittest.main()
