"""BM-05 exact conditional false-authorization/competence gate controls."""
from fractions import Fraction
import unittest

from correlated_minimax import conditional_minimax_error
from robust_certification_gate import robust_monitor_certificate


class RobustCertificationGateTests(unittest.TestCase):
    def test_positive_three_probe_two_sided_certificate(self):
        c=robust_monitor_certificate(
            4,Fraction(1,16),3,
            false_restoration_accept_caps=(Fraction(1,1000),)*3,
            genuine_restoration_reject_caps=(Fraction(1,100),)*3,
            max_path_units=9,
            maximum_false_authorization=Fraction(1,5),
            minimum_correct_authorization=Fraction(4,5),
        )
        self.assertEqual(c.parity_error_bound,Fraction(5,32))
        self.assertEqual(c.authorized_wrong_bound,
                         Fraction(5,32)+Fraction(3,1000))
        self.assertEqual(c.correct_authorization_lower_bound,
                         1-Fraction(5,32)-Fraction(3,100))
        self.assertEqual(c.worst_case_resource_units,9)
        self.assertTrue(c.passes)

    def test_correlated_mask_kills_non_inert_certification_at_one_eighth(self):
        c=robust_monitor_certificate(4,Fraction(1,8),3,
                                     maximum_false_authorization=Fraction(1,5),
                                     minimum_correct_authorization=Fraction(4,5))
        self.assertEqual(c.parity_error_bound,Fraction(1,2))
        self.assertFalse(c.passes)

    def test_cost_gate_fails_even_with_sufficient_statistics(self):
        c=robust_monitor_certificate(
            4,Fraction(1,16),3,
            false_restoration_accept_caps=(Fraction(1,1000),)*3,
            genuine_restoration_reject_caps=(Fraction(1,100),)*3,
            max_path_units=8,
        )
        self.assertEqual(c.worst_case_resource_units,9)
        self.assertFalse(c.passes)

    def test_weak_attestation_fails_separate_soundness_and_liveness_gates(self):
        fa=robust_monitor_certificate(
            4,Fraction(1,16),3,
            false_restoration_accept_caps=(Fraction(1,20),)*3,
            genuine_restoration_reject_caps=(Fraction(0),)*3,
        )
        self.assertGreater(fa.authorized_wrong_bound,Fraction(1,5))
        self.assertFalse(fa.passes)
        fr=robust_monitor_certificate(
            4,Fraction(1,16),3,
            false_restoration_accept_caps=(Fraction(0),)*3,
            genuine_restoration_reject_caps=(Fraction(1,10),)*3,
        )
        self.assertLess(fr.correct_authorization_lower_bound,Fraction(4,5))
        self.assertFalse(fr.passes)

    def test_no_intervention_audits_still_support_passive_binary_certificate(self):
        c=robust_monitor_certificate(
            4,Fraction(1,16),3, max_path_units=3
        )
        self.assertEqual(c.worst_case_resource_units,3)
        self.assertEqual(c.authorized_wrong_bound,conditional_minimax_error(
            4,Fraction(1,16),3))
        self.assertTrue(c.passes)

    def test_reject_mismatched_restoration_receipts(self):
        with self.assertRaises(ValueError):
            robust_monitor_certificate(4,Fraction(1,16),3,
                false_restoration_accept_caps=(Fraction(1,10),),
                genuine_restoration_reject_caps=())
        with self.assertRaises(ValueError):
            robust_monitor_certificate(4,Fraction(1,16),1,
                false_restoration_accept_caps=(Fraction(0),Fraction(0)),
                genuine_restoration_reject_caps=(Fraction(0),Fraction(0)))
        with self.assertRaises(ValueError):
            robust_monitor_certificate(4,Fraction(1,16),2,
                false_restoration_accept_caps=(Fraction(-1),),
                genuine_restoration_reject_caps=(Fraction(0),))
        with self.assertRaises(ValueError):
            robust_monitor_certificate(4,Fraction(1,16),3,
                restoration_audit_units=0)
        with self.assertRaises(ValueError):
            robust_monitor_certificate(4,Fraction(1,16),3,
                maximum_false_authorization=Fraction(6,5))
        with self.assertRaises(ValueError):
            robust_monitor_certificate(4,Fraction(1,16),3,
                minimum_correct_authorization=Fraction(-1,5))


if __name__=="__main__":
    unittest.main()
