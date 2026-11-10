"""BM-19: independent exact residual Fourier, primal, dual and output checks."""
from fractions import Fraction
import unittest

from generic_fourier_erasure_BM17 import (
    Primal,census,output_counts,signed_walsh,mask_walsh,
)
from fourier_completion_BM18 import (
    check_radial_primal,fair_hitting_noise,
)
from support_aware_completion_BM19 import (
    PostprocessorPrimal,PostprocessorDual,
    remaining_fourier_support,verify_postprocessor_primal,
    verify_postprocessor_dual,certify_support_optimum,
    postprocess_partial_pair,singleton_union_bound,support_lp_metadata,
)
from support_aware_fixtures_BM19 import (
    FIXTURES,frozen_partial,fixture_receipt,certificate_manifest,
)


def independent_hadamard_residual(pair,partial):
    """Compare two complete partially masked output laws directly."""
    a=output_counts(census(pair.flat),partial.q0)
    b=output_counts(census(pair.other),partial.q1)
    return tuple(S for S in range(1,1<<pair.m)
                 if signed_walsh(a,S)!=signed_walsh(b,S))


def independent_mask_walsh(witness,subset):
    return Fraction(
        sum(((-1 if (mask & subset).bit_count()%2 else 1)*mass
             for mask,mass in witness.weights.items())),
        witness.denominator,
    )


class SupportAwareCompletionTests(unittest.TestCase):
    def test_all_five_exact_postprocessing_primal_and_dual_witnesses(self):
        expected={
            ("k4",3):(Fraction(7,38),Fraction(11,38),17),
            ("k4",4):(Fraction(1,10),Fraction(13,50),3),
            ("k4",5):(Fraction(1,12),Fraction(59,228),1),
            ("diamond",3):(Fraction(1,5),Fraction(3,10),6),
            ("theta",4):(Fraction(1,6),Fraction(1,4),7),
        }
        self.assertEqual(set(FIXTURES),set(expected))
        for key,(optimal,final,number) in expected.items():
            receipt=fixture_receipt(*key)
            self.assertEqual(receipt.optimal_extra_flip,optimal)
            self.assertEqual(receipt.completed_max_flip,final)
            self.assertEqual(receipt.uniform_completion_upper,final)
            self.assertEqual(len(receipt.discrepancy_support),number)
            self.assertTrue(receipt.complete_laws_equal)
            self.assertEqual(receipt.checked_dual_inequalities,
                             1<<frozen_partial(*key)[0].m)

    def test_residual_support_matches_independent_complete_output_convolution(self):
        for (name,degree),(expected,optimal,primal,dual) in FIXTURES.items():
            pair,partial=frozen_partial(name,degree)
            self.assertEqual(
                remaining_fourier_support(pair,degree,partial),
                independent_hadamard_residual(pair,partial)
            )
            self.assertEqual(
                independent_hadamard_residual(pair,partial),expected
            )
            for S in expected:
                self.assertEqual(independent_mask_walsh(primal,S),0)
            self.assertEqual(
                certify_support_optimum(pair.m,expected,primal,dual),optimal
            )

    def test_k4_partial_degree_four_has_exact_short_combinatorial_lower(self):
        support,optimum,upper,dual=FIXTURES[("k4",4)]
        self.assertEqual(support,(47,61,63))
        self.assertEqual(tuple(s.bit_count() for s in support),(5,5,6))
        self.assertEqual(singleton_union_bound(support),Fraction(1,10))
        self.assertEqual(verify_postprocessor_primal(6,support,upper),
                         Fraction(1,10))
        self.assertEqual(verify_postprocessor_dual(6,support,dual),
                         Fraction(1,10))
        self.assertEqual(upper.weights,{
            0:9,1:2,2:1,4:2,8:2,16:1,18:1,32:2
        })
        self.assertEqual(dual.characters,{61:Fraction(-1,10)})
        self.assertEqual(sum(upper.weights.values()),20)

    def test_strict_improvement_over_BM18_universal_higher_degree_eraser(self):
        for graph,degree in (("k4",3),("k4",4),("k4",5),
                             ("diamond",3),("theta",4)):
            pair,partial=frozen_partial(graph,degree)
            optimal=FIXTURES[(graph,degree)][1]
            generic=check_radial_primal(
                pair.m,degree,fair_hitting_noise(pair.m,degree))
            if graph=="k4" and degree==3:
                generic=Fraction(5,24)  # BM-18 exact radial optimum
            self.assertLessEqual(optimal,generic)
            if (graph,degree) in (("k4",3),("k4",4)):
                self.assertLess(optimal,generic)
            else:
                self.assertEqual(optimal,generic)
        self.assertEqual(Fraction(5,24)-Fraction(7,38),
                         Fraction(11,456))
        self.assertEqual(Fraction(1,6)-Fraction(1,10),Fraction(1,15))

    def test_certified_completed_K4_cap_is_above_its_reoptimized_full_LP(self):
        full=Fraction(3,14)
        for degree in (3,4,5):
            completed=fixture_receipt("k4",degree).completed_max_flip
            self.assertGreater(completed,full)
        self.assertEqual(
            fixture_receipt("k4",4).completed_max_flip-Fraction(3,14),
            Fraction(8,175)
        )

    def test_perturbing_primal_or_dual_is_detected(self):
        support,optimum,upper,dual=FIXTURES[("k4",4)]
        altered=dict(upper.weights)
        altered[0]-=1
        altered[1]+=1
        with self.assertRaises(AssertionError):
            verify_postprocessor_primal(
                6,support,PostprocessorPrimal(upper.denominator,altered)
            )
        false_dual=PostprocessorDual(
            dual.normalization+Fraction(1,100),
            dual.characters,dual.marginal_multipliers
        )
        with self.assertRaises(AssertionError):
            verify_postprocessor_dual(6,support,false_dual)
        with self.assertRaises(AssertionError):
            verify_postprocessor_dual(
                6,support,PostprocessorDual(
                    dual.normalization,dual.characters,
                    (Fraction(0),)*6
                )
            )

    def test_empty_residual_support_requires_zero_additional_noise(self):
        pair,partial=frozen_partial("k4",5)
        identical=type(pair)(pair.flat,pair.flat)
        zero=Primal(1,{0:1},{0:1},Fraction(0))
        self.assertEqual(remaining_fourier_support(identical,0,zero),())
        witness=PostprocessorPrimal(1,{0:1})
        dual=PostprocessorDual(Fraction(0),{},(Fraction(-1),)+(Fraction(0),)*5)
        self.assertEqual(certify_support_optimum(6,(),witness,dual),0)
        self.assertEqual(postprocess_partial_pair(
            identical,0,zero,witness,dual
        ).completed_max_flip,0)

    def test_graph_support_LP_dimensions_and_bad_inputs(self):
        for key,(supports,optimum,primal,dual) in FIXTURES.items():
            m=frozen_partial(*key)[0].m
            report=support_lp_metadata(m,supports)
            self.assertEqual(report["variables"],(1<<m)+1)
            self.assertEqual(report["normalization_and_fourier_rows"],
                             len(supports)+1)
            self.assertEqual(report["marginal_inequality_rows"],m)
            self.assertEqual(report["dual_mask_inequalities"],1<<m)
        with self.assertRaises(ValueError):
            support_lp_metadata(6,(47,47))
        with self.assertRaises(ValueError):
            support_lp_metadata(0,(1,))
        with self.assertRaises(ValueError):
            support_lp_metadata(6,(64,))
        with self.assertRaises(ValueError):
            verify_postprocessor_primal(6,(63,),PostprocessorPrimal(0,{0:1}))
        with self.assertRaises(ValueError):
            verify_postprocessor_dual(
                6,(63,),PostprocessorDual(
                    Fraction(0),{31:Fraction(1)},(Fraction(-1),)+(0,)*5
                )
            )

    def test_receipts_manifest_is_consistent_with_registered_witnesses(self):
        manifest=certificate_manifest()
        self.assertEqual(len(manifest),5)
        self.assertEqual(manifest["k4-d4"]["residual_support_count"],3)
        self.assertEqual(manifest["k4-d4"]["optimal_postprocessing_rate"],"1/10")
        self.assertEqual(manifest["k4-d3"]["optimal_postprocessing_rate"],"7/38")
        self.assertEqual(manifest["diamond-d3"]["optimal_postprocessing_rate"],"1/5")
        self.assertEqual(manifest["theta-d4"]["optimal_postprocessing_rate"],"1/6")


if __name__=="__main__":
    unittest.main()
