"""Exact, seed-invariant finite-state causal-identification assertions."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from HarmonicConsciousness.dormant_gate import (  # noqa: E402
    GateRegister, cross_partition_rank, input_controllability_rank,
    linear_map, run_adversary, run_trace,
)


class DormantGateTests(unittest.TestCase):
    def test_all_input_streams_up_to_length_eight_have_same_full_trace(self):
        # 2^8 = 256 exhaustive binary sequences, independent of RNG.
        for code in range(256):
            cues = np.array([(code >> k) & 1 for k in range(8)], dtype=np.uint8)
            a, ap = run_trace("plain", cues)
            b, bp = run_trace("dormant_gate", cues)
            np.testing.assert_array_equal(a, b)
            np.testing.assert_array_equal(ap, bp)
            self.assertTrue((a[:, 15] == 0).all())

    def test_exact_transition_differs_by_one_entry(self):
        a, ba = linear_map("plain")
        b, bb = linear_map("dormant_gate")
        expected = np.zeros((16, 16), dtype=np.uint8)
        expected[7, 15] = 1
        np.testing.assert_array_equal(a ^ b, expected)
        np.testing.assert_array_equal(ba, bb)
        self.assertEqual(cross_partition_rank("plain"), 1)
        self.assertEqual(cross_partition_rank("dormant_gate"), 2)
        self.assertEqual(input_controllability_rank("plain"), 15)
        self.assertEqual(input_controllability_rank("dormant_gate"), 15)

    def test_same_lesion_diverges_at_fixed_lags(self):
        cues = np.random.default_rng(5).integers(0, 2, 80, dtype=np.uint8)
        a, ap = run_trace("plain", cues, intervene_at=32)
        b, bp = run_trace("dormant_gate", cues, intervene_at=32)
        self.assertEqual(int(np.count_nonzero(a[32] ^ b[32])), 0)
        self.assertEqual(int(np.count_nonzero(a[33] ^ b[33])), 1)
        self.assertEqual(int(np.count_nonzero(a[38] ^ b[38])), 1)
        self.assertNotEqual(int(ap[38]), int(bp[38]))
        self.assertTrue(np.array_equal(a[:32], b[:32]))

    def test_expected_delayed_recall_and_prohibitions(self):
        cues = np.random.default_rng(10).integers(0, 2, 64, dtype=np.uint8)
        obs, pred = run_trace("dormant_gate", cues, delay=12)
        np.testing.assert_array_equal(pred[12:], cues[:-12])
        with self.assertRaises(ValueError):
            run_trace("dormant_gate", np.array([1, 2]))
        with self.assertRaises(ValueError):
            GateRegister("other")
        with self.assertRaises(ValueError):
            GateRegister("plain").intervene(site=16)
        with self.assertRaises(ValueError):
            run_adversary(length=20)

    def test_seeds_reproduce_and_all_registered_predictions_hold(self):
        first = run_adversary(seed=110, trials=3, length=96)
        again = run_adversary(seed=110, trials=3, length=96)
        self.assertEqual(first, again)
        self.assertTrue(all(first["diagnostics"].values()))
        self.assertEqual(first["metric_scope"]["FRC"].split(";")[0], "not estimated")

    def test_protocol_and_output(self):
        protocol = json.loads((ROOT / "HarmonicConsciousness/protocol_v0_2.json").read_text())
        self.assertEqual(protocol["state_dimension"], 16)
        self.assertEqual(protocol["replication_seed"], 44178013)
        self.assertEqual(protocol["scope"]["IIT_Phi"], "not_computed")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "receipt.json"
            subprocess.run([sys.executable, str(ROOT / "scripts/run_harmonic_dormant_gate.py"),
                            "--trials", "2", "--length", "80", "--out", str(path)],
                           check=True, capture_output=True, text=True)
            receipt = json.loads(path.read_text())
            self.assertTrue(all(receipt["diagnostics"].values()))
            self.assertEqual(len(receipt["trials"]), 2)


if __name__ == "__main__":
    unittest.main()
