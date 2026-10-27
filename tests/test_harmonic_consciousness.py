"""Mechanical invariants and preregistered controls for HarmonicConsciousness."""
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

from HarmonicConsciousness.benchmark import (  # noqa: E402
    KINDS, ToySystem, binary_transition_matrix, channel_roll_surrogate, effective_dimension,
    gf2_rank, partition_cross_rank,
    mean_squared_correlation, probe_budget_to_find_failure, run_benchmark,
    simulate, spectral_peak_fraction,
)


class HarmonicToyTests(unittest.TestCase):
    def test_fixed_cue_register_exact_delay(self):
        rng = np.random.default_rng(23)
        cues = rng.integers(0, 2, 80, dtype=np.uint8)
        trace = simulate("delay_register", cues, 22, 12)
        np.testing.assert_array_equal(trace["predictions"][12:], cues[:-12])
        cut = simulate("delay_register_cut", cues, 22, 12)
        self.assertTrue(np.all(cut["predictions"][12:] == 0))

    def test_xor_two_shears_invertible_given_cue(self):
        """Every shear is reversible by repeating it in reverse order."""
        system = ToySystem("xor_grid", seed=9)
        system.bits = np.random.default_rng(4).integers(0, 2, system.nodes, dtype=np.uint8)
        before = system.bits.copy()
        system.step(1)
        system.bits[0] ^= 1  # remove input bit
        side = 4
        for parity in (1, 0):
            for v in range(system.nodes):
                if ((v // side) + v % side) % 2 == parity:
                    system.bits[v] ^= np.bitwise_xor.reduce(system.bits[list(system.neighbors[v])])
        np.testing.assert_array_equal(system.bits, before)

    def test_exact_gf2_partition_integration_control(self):
        self.assertEqual(gf2_rank(np.eye(16, dtype=np.uint8)), 16)
        self.assertEqual(gf2_rank(np.zeros((3, 4), dtype=np.uint8)), 0)
        self.assertEqual(gf2_rank(binary_transition_matrix("xor_grid")), 16)
        self.assertGreater(partition_cross_rank("xor_grid"), 0)
        self.assertEqual(partition_cross_rank("xor_grid_cut"), 0)
        self.assertEqual(partition_cross_rank("delay_register"), 1)
        self.assertEqual(partition_cross_rank("delay_register_cut"), 0)
        self.assertIsNone(partition_cross_rank("phase_locked"))

    def test_phase_order_high_is_not_recall_evidence(self):
        result = run_benchmark(seed=53, trials=3, length=128, delay=12)
        self.assertGreater(result["summary"]["phase_locked"]["mean_phase_order"], .9)
        self.assertEqual(result["summary"]["delay_register"]["mean_accuracy"], 1.)
        self.assertLess(result["summary"]["delay_register_cut"]["mean_accuracy"], .65)

    def test_circular_surrogate_preserves_power_changes_cross_channel_relation(self):
        t = np.arange(256)
        signals = np.column_stack([np.sin(2 * np.pi * 7 * t / 256)] * 16)
        surrogate = channel_roll_surrogate(signals, 20261027)
        for i in range(16):
            np.testing.assert_allclose(
                abs(np.fft.rfft(signals[:, i])), abs(np.fft.rfft(surrogate[:, i])),
                atol=1.e-10)
        self.assertAlmostEqual(spectral_peak_fraction(signals),
                               spectral_peak_fraction(surrogate), places=12)
        self.assertGreater(mean_squared_correlation(signals) -
                           mean_squared_correlation(surrogate), .2)

    def test_relabel_and_constant_channel_controls(self):
        s = np.random.default_rng(5).normal(size=(70, 16))
        perm = np.random.default_rng(6).permutation(16)
        for metric in (spectral_peak_fraction, mean_squared_correlation,
                       effective_dimension):
            self.assertAlmostEqual(metric(s), metric(s[:, perm]), places=12)
            self.assertEqual(metric(np.zeros((70, 16))), 0.)

    def test_probe_budget_exact_hypergeometric_boundary(self):
        self.assertEqual(probe_budget_to_find_failure([10], 10, delta=.05), 1)
        self.assertIsNone(probe_budget_to_find_failure([0], 10))
        self.assertEqual(probe_budget_to_find_failure([1], 10, delta=.1), 9)
        with self.assertRaises(ValueError):
            probe_budget_to_find_failure([11], 10)

    def test_deterministic_seed_matrix_and_metric_contract(self):
        a = run_benchmark(seed=7, trials=2, length=80, delay=12)
        b = run_benchmark(seed=7, trials=2, length=80, delay=12)
        self.assertEqual(a, b)
        self.assertEqual(len(a["trials"]), 2 * len(KINDS))
        self.assertEqual(a["status"], "synthetic_toy_no_consciousness_claim")
        self.assertNotIn("phi_value", a)
        self.assertEqual(a["summary"]["delay_register"]["q95_falsification_probes"], None)
        self.assertTrue(all(np.isfinite(r["spectral_peak_fraction"]) for r in a["trials"]))

    def test_protocol_matches_declared_defaults(self):
        manifest = json.loads((ROOT / "HarmonicConsciousness" /
                               "protocol_v0_1.json").read_text())
        self.assertEqual(manifest["schema"], "harmonic_consciousness_adversarial_v0.1")
        self.assertEqual(manifest["families"], list(KINDS))
        self.assertEqual(manifest["delay"], 12)
        self.assertEqual(manifest["num_trials_per_seed"], 24)
        self.assertEqual(manifest["interpretation"]["IIT_Phi"], "not_computed")
        self.assertEqual(manifest["interpretation"]["FRC_lim_inf"], "not_estimated")

    def test_runner_json_parseable(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "receipt.json"
            subprocess.run([sys.executable, str(ROOT / "scripts/run_harmonic_consciousness.py"),
                            "--trials", "2", "--length", "80", "--out", str(out)],
                           capture_output=True, text=True, check=True)
            receipt = json.loads(out.read_text())
            self.assertEqual(receipt["parameters"]["trials"], 2)
            self.assertEqual(len(receipt["summary"]), len(KINDS))


if __name__ == "__main__":
    unittest.main()
