import copy
import unittest

from collatz_core import analyze, modular_labels
from reachability import certificate, forward_orbit, verify_certificate


class ReachabilityTest(unittest.TestCase):
    def test_exact_closed_certificates_on_all_small_pairs(self):
        for d in (1, 5, 13, 29, 49, 73):
            core = analyze(d)
            for source in core.states:
                targets = set(forward_orbit(source, d))
                for target in core.states:
                    self.assertEqual(verify_certificate(certificate(source, target, d)),
                                     target not in targets)

    def test_alias_and_edit_require_rechecking(self):
        q = modular_labels(13)
        self.assertEqual(q[1], q[5])
        proof = certificate(1, 5, 13)
        self.assertTrue(verify_certificate(proof))
        self.assertFalse(verify_certificate(proof, ((1, 5),)))
        self.assertTrue(verify_certificate(proof, ((5, 7),)))

    def test_malformed_certificates_are_rejected(self):
        valid = certificate(5, 1, 13)
        for change in ({"closed_set": [5]}, {"closed_set": [5, 7, 7]},
                       {"source": 3}, {"target": 5}, {"d": 12},
                       {"closed_set": [5, 7, 14]}, {"schema": "forged"},
                       {"closed_set": None}, {"target": True}):
            forged = copy.deepcopy(valid)
            forged.update(change)
            self.assertFalse(verify_certificate(forged), change)


if __name__ == "__main__":
    unittest.main()
