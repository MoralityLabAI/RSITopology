from __future__ import annotations

import copy
import itertools
import json
import tempfile
import unittest
from pathlib import Path

from chain_identifiability import (
    canonical_model,
    compose,
    enumerate_configuration,
    explicit_cut_counterexample,
    observation_signature,
    predicted_orbit_count,
    relabel_hidden,
    restricted_bell,
    singleton_do_design,
    singleton_do_star_counterexample,
    stirling_second,
    matrix_rank_exact,
    main,
    protocol_fixture_checks,
)


class ChainIdentifiabilityTests(unittest.TestCase):
    def test_stirling_and_restricted_bell(self) -> None:
        self.assertEqual(stirling_second(3, 2), 3)
        self.assertEqual(stirling_second(4, 2), 7)
        self.assertEqual(restricted_bell(3, 2), 4)
        self.assertEqual(restricted_bell(0, 0), 1)

    def test_hidden_relabeling_is_gauge(self) -> None:
        h_map = (0, 0, 1, 2)
        g_map = (0, 0, 1)
        base_signature = observation_signature(h_map, g_map, 2)
        base_output = compose(h_map, g_map)
        base_canonical = canonical_model(h_map, g_map)
        for permutation in itertools.permutations(range(3)):
            g_new, h_new = relabel_hidden(h_map, g_map, permutation)
            self.assertEqual(compose(h_new, g_new), base_output)
            self.assertEqual(observation_signature(h_new, g_new, 2), base_signature)
            self.assertEqual(canonical_model(h_new, g_new), base_canonical)

    def test_registered_counterexample(self) -> None:
        receipt = explicit_cut_counterexample()
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(receipt["compatible_surjective_orbit_count"], 3)

    def test_partition_formula_on_small_exhaustive_grid(self) -> None:
        for input_size in range(1, 4):
            for hidden_size in range(1, 4):
                for output_size in range(1, 3):
                    result = enumerate_configuration(input_size, hidden_size, output_size)
                    self.assertEqual(result["formula_mismatches"], [])

    def test_exact_universe_and_gauge_census(self) -> None:
        result = enumerate_configuration(3, 3, 2)
        self.assertEqual(result["model_count"], 216)
        self.assertEqual(result["expected_model_count"], 216)
        self.assertEqual(result["surjective_hidden_model_count"], 48)
        self.assertEqual(result["expected_surjective_hidden_model_count"], 48)
        self.assertEqual(result["gauge_transform_checks"], 1296)
        self.assertEqual(result["expected_gauge_transform_checks"], 1296)
        self.assertTrue(result["universe_complete"])
        self.assertTrue(result["gauge_universe_complete"])

    def test_identifiability_criterion_examples(self) -> None:
        # k=(2,1), n=(3,1): S(3,2)*S(1,1)=3 under hidden surjectivity.
        signature = ((2, 1), (0, 0, 0, 1))
        self.assertEqual(predicted_orbit_count(signature, surjective_hidden=True), 3)
        # Unrestricted hidden use allows 1- or 2-block partitions: 1+3=4.
        self.assertEqual(predicted_orbit_count(signature, surjective_hidden=False), 4)

    def test_singleton_do_star_blind_pair(self) -> None:
        receipt = singleton_do_star_counterexample()
        self.assertTrue(all(receipt["checks"].values()))
        self.assertEqual(receipt["design_rank"], 4)
        self.assertEqual(receipt["design_nullity"], 4)
        self.assertEqual(receipt["f_coordinate_influences"], (1, 3, 3))
        self.assertEqual(receipt["g_coordinate_influences"], (3, 3, 3))
        self.assertEqual(matrix_rank_exact(singleton_do_design(3)), 4)

    def test_runner_rejects_unregistered_grid(self) -> None:
        protocol = Path(__file__).with_name("protocol_v0_1.json")
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "result.json"
            with self.assertRaisesRegex(ValueError, "differs from registered"):
                main(
                    [
                        "--protocol",
                        str(protocol),
                        "--output",
                        str(output),
                        "--max-input-size",
                        "3",
                        "--max-hidden-size",
                        "3",
                        "--max-output-size",
                        "2",
                    ]
                )

    def test_protocol_fixture_binding_detects_mutation(self) -> None:
        protocol_path = Path(__file__).with_name("protocol_v0_1.json")
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        result = {
            "counterexample": explicit_cut_counterexample(),
            "singleton_do_star_counterexample": singleton_do_star_counterexample(),
        }
        self.assertTrue(all(protocol_fixture_checks(protocol, result).values()))
        mutated = copy.deepcopy(protocol)
        mutated["registered_counterexample"]["h_left"][0] = 2
        self.assertFalse(all(protocol_fixture_checks(mutated, result).values()))

    def test_runner_rejects_output_alias_before_enumeration(self) -> None:
        protocol = Path(__file__).with_name("protocol_v0_1.json")
        with self.assertRaisesRegex(ValueError, "aliases"):
            main(["--protocol", str(protocol), "--output", str(protocol)])


if __name__ == "__main__":
    unittest.main()
